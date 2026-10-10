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
        instructions="You're a helpful AI assistant",
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

    # ---- Everything below is at the same level as "agent = ..." ----

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

    logger.info("✅ Agent finished")


# ============================================
# ENTRY POINT
# ============================================

def print_meeting_summary():
    """
    Print the meeting summary
    """
    logger.info("📝 Meeting Summary:")
    full_transcript = " ".join(meeting_data["transcript"])
    logger.info(full_transcript)


if __name__ == "__main__":
    call_id = os.getenv("CALL_ID", f"meeting-{uuid4().hex[:8]}")  # Default call ID for testing

    try:
        asyncio.run(start_agent(call_id))
    except KeyboardInterrupt:
        logger.info("🤖 Meeting Assistant stopped by user")
    finally:
        if meeting_data["transcript"]:
            print_meeting_summary()