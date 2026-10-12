#===================================
# STEP 1: BASIC SETUP AND IMPORTS
#===================================

import asyncio  # For async/await (like in JavaScript)
import os  # To read environment variables
import logging  # Better than print() for debugging
from uuid import uuid4  # Generate unique IDs
from dotenv import load_dotenv  # Load .env files

# Vision Agents - Core Library
from vision_agents.core import agents  # Main Agent class
from vision_agents.plugins import getstream, gemini  # Stream and Gemini integrations
from vision_agents.core.edge.types import User  # User type for agent

from vision_agents.core.events import (
    CallSessionParticipantJoinedEvent,
    CallSessionParticipantLeftEvent,
    CallSessionStartedEvent,
    CallSessionEndedEvent,
    PluginErrorEvent,
)

from vision_agents.core.llm.events import (
    RealtimeUserSpeechTranscriptionEvent,  # When speech is transcribed
    LLMResponseChunkEvent,  # When agent responds
)

# =================================
# STEP 2: Add Event Handlers - Session and Participants
# =================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file

meeting_data = {
    "transcript": [],
    "is_active": False,
}


async def start_agent(call_id: str):
    """
    Start the meeting assistant agent

    Args:
        call_id: The meeting ID (must match frontend!)
    """

    logger.info("🤖 Starting Meeting Assistant...")
    logger.info(f"📞 Call ID: {call_id}")

    agent = agents.Agent(
        edge=getstream.Edge(),
        agent_user=User(
            id="meeting-assistant-bot",
            name="Meeting Assistant",
            # role="assistant",
        ),

        instructions="""
        You are a meeting transcription bot.
        
        CRITICAL RULES - FOLLOW EXACTLY:
        1. YOU MUST NEVER SPEAK unless someone says "Hey Assistant"
        2. DO NOT respond to conversations between users
        3. DO NOT acknowledge anything users say to each other
        4. DO NOT explain that you're staying silent
        5. DO NOT say "I should remain silent" or any variation
        6. ONLY RESPOND when you explicitly hear "Hey Assistant" followed by a question
        7. If unsure whether to speak: DON'T SPEAK
        
        Your ONLY job:
        - Listen silently
        - Transcribe everything
        - Wait for "Hey Assistant"
        
        When you DO hear "Hey Assistant":
        - Answer the question using meeting transcript and notes
        - Keep answer short and factual
        - Use only information from this meeting
        
        Example:
        ❌ User: "Let's discuss the budget" → You: STAY COMPLETELY SILENT
        ❌ User: "What do you think?" → You: STAY COMPLETELY SILENT
        
        ✅ User: "Hey Assistant, what are the action items?" → You: Answer with action items
        ✅ User: "Hey Assistant, summarize the meeting" → You: Provide summary
        """,
        
        # Gemini Realtime handles STT, LLM and TTS
        # fps=0 means no video frames sent (audio only, saves costs)
        llm=gemini.Realtime(fps=0),
    )

    # Store agent reference for later use
    meeting_data["agent"] = agent
    meeting_data["call_id"] = call_id

    @agent.events.subscribe  # Register event listener
    async def handle_session_started(event: CallSessionStartedEvent):
        logger.info("📞 call started")
        meeting_data["is_active"] = True
        logger.info("🎙️ Meeting started")

        try:
            channel = agent.edge.client.channel("messaging", call_id)
            await channel.watch()
            meeting_data["channel"]=channel
            logger.info("✅ Chat channel initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize chat channel: {e}")   

    @agent.events.subscribe
    async def handle_participant_joined(event: CallSessionParticipantJoinedEvent):

        if event.participant.user.id == "meeting-assistant-bot":
            return

        participant_name = event.participant.user.name
        logger.info(f"👤 Participant joined: {participant_name}")

    @agent.events.subscribe
    async def handle_participant_left(event: CallSessionParticipantLeftEvent):

        if event.participant.user.id == "meeting-assistant-bot":
            return

        participant_name = event.participant.user.name
        logger.info(f"👋 Participant left: {participant_name}")

    # =========================================
    # STEP 3: Add Transcription Handler
    # =========================================

    @agent.events.subscribe
    async def handle_transcription(event: RealtimeUserSpeechTranscriptionEvent):
        """
        Called when Gemini transcribes speech to text
        Handles:
        1. Auto-transcription (stores all speech)
        2. Q&A trigger detection ("Hey Assistant")
        """
        #Ignore empty transcripts
        if not event.text or len(event.text.strip()) == 0:
            return

        # Get speakere ID (or "Unknown" if not available)
        speaker = getattr(event, 'participant_id', 'Unknown')
        transcript_text = event.text

        meeting_data["transcript"].append({
            "speaker":speaker,
            "text": transcript_text,
            "timestamp": getattr(event, 'timestamp', None)
        })

        logger.info(f"📝 [{speaker}]: {transcript_text}")

        # =====================================
        # STEP 4: Add Q&A Feature
        # =====================================

        if transcript_text.lower().startswith("hey assistant"):
            #Extract question (remove "hey assistant" prefix - 13 chars)
            question = transcript_text[13:].strip()

            if question:
                logger.info(f"❓ Q&A triggered: {question}")

                #Build context from all transcripts
                context = "MEETING TRANSCRIPT:\n\n"
                for entry in meeting_data["transcript"]:
                    context += f"[{entry['speaker']}]: {entry['text']}\n"

                    # Create prompt with full meeting context
                    prompt = f"""
                    {context}

                   USER QUESTION: {question}

                   Answer based ONLY on the meeting transcript above.
                   Be concise and helpful.
                    """

                    try:
                        # Send to Gemini (responds with voice)
                        await agent.simple_response(prompt)
                        logger.info(f"🤖 Responding to question")
                    except Exception as e:
                        logger.error(f"❌ Q&A error: {e}")

    @agent.events.subscribe
    async def handle_llm_respose(event: LLMResponseChunkEvent):
        """Log agent's response (What AI is typing)"""
        if hasattr(event, 'delta') and event.delta:
            logger.info(f"🤖 Agent: {event.delta}")

    @agent.events.subscribe
    async def handle_session_ended(event: CallSessionEndedEvent):
        """Called when call ends"""
        meeting_data["is_active"] = False
        logger.info("🛑 Meeting ended")
        logger.info(f"📊 Final status:")
        logger.info(f"   -Transcript entries: {len(meeting_data['transcript'])}")


    # =========================================
    # STEP 5: Add Error Handling and Cleanup
    # =========================================

    @agent.events.subscribe
    async def handle_errors(event: PluginErrorEvent):
        """Called when plugin errors occur"""
        logger.error(f"❌ Plugin error: {event.error_message}")
        if event.is_fatal:
            logger.error("🚨 Fatal error")

    # Create agent user in Stream
    await agent.create_user()

    call = agent.edge.client.video.call("default", call_id)

    logger.info("✅ Joining call...")

    with await agent.join(call):
        logger.info("✅ Joined call successfully")
        logger.info("\n📋 Features:")
        logger.info("   1. ✅ Auto-transcription")
        logger.info("   2. ✅ Q&A (say `Hey Assistant` + question)")

        # Wait until call ends
        await agent.finish()

    logger.info("✅ Agent finished.")


# ============================================
# ENTRY POINT
# ============================================

def print_meeting_summary():
    """
    Print the meeting summary
    """
    logger.info("📝 Meeting Summary:")
    for entry in meeting_data['transcript']:
        print(f"[{entry['speaker']}]: {entry['text']}")


if __name__ == "__main__":
    call_id = os.getenv("CALL_ID", f"meeting-{uuid4().hex[:8]}")  # Default call ID for testing

    try:
        asyncio.run(start_agent(call_id))
    except KeyboardInterrupt:
        logger.info("🤖 Meeting Assistant stopped by user")
    finally:
        if meeting_data["transcript"]:
            print_meeting_summary()