# 🎙️ Smart Meeting Assistant

A real-time video meeting app with live transcription and a voice AI assistant that sits in the call, listens silently, and answers questions about the meeting only when you say "Hey Assistant".

Built with Next.js and Stream (Video + Chat) on the frontend, and a Python bot powered by Vision Agents and Google Gemini Realtime on the backend.

🔗 Live demo  https://smart-meeting-assistant-seven.vercel.app/

✨ Features
📹 HD video meetings – join a call with just your name, no sign-up required
📝 Live transcript panel – real-time closed captions with speaker names and timestamps
🤖 AI meeting bot – a Python agent joins the same call as a participant
🗣️ Voice Q&A – say "Hey Assistant, what are the action items?" and the bot answers by voice using the meeting transcript
🤫 Silent by default – the bot never interrupts; it only speaks when addressed
🔐 Secure token generation – Stream user tokens are issued server-side through a Next.js API route
🌙 Responsive dark UI – built with Tailwind CSS

🧰 Tech Stack
Frontend (meeting-assistant/)
Technology	Purpose
Next.js (App Router)	React framework, routing and API routes
React 19	UI library
Tailwind CSS v4	Styling
@stream-io/video-react-sdk	Video calling UI, call controls, closed captions
stream-chat / stream-chat-react	Chat client and context
@stream-io/node-sdk	Server-side user upsert and token generation
ESLint	Linting
Vercel	Deployment
Backend (backend/)
Technology	Purpose
Python 3.13	Runtime
Vision Agents 0.2.2	Framework for building real-time AI agents in video calls
vision-agents-plugins-getstream	Stream Edge integration (agent joins the call)
vision-agents-plugins-gemini	Gemini Realtime (speech-to-text, LLM and text-to-speech in one)
getstream	Stream Python SDK (with WebRTC and telemetry)
python-dotenv	Environment variable loading
uv	Python package and project manager

┌──────────────────────┐        ┌────────────────────┐
│  Next.js Frontend    │        │   Stream Cloud     │
│  - Join page         │◄──────►│   Video + Chat     │
│  - Meeting room      │        │   (WebRTC, Captions)│
│  - Live transcript   │        └─────────▲──────────┘
└─────────▲────────────┘                  │
          │ /api/token                    │ joins same call
          │ (server-side token)           │
┌─────────┴────────────┐        ┌─────────┴──────────┐
│  Next.js API Route   │        │  Python AI Agent   │
│  Stream Node SDK     │        │  Vision Agents +   │
└──────────────────────┘        │  Gemini Realtime   │
                                └────────────────────┘

1. A user enters their name on the home page and is redirected to /meeting/<call-id>.

2. The page requests a signed user token from /api/token (generated with the Stream Node SDK).
3. The Stream Video and Chat clients connect, the user joins the call, and closed captions are started.
4. The transcript panel listens to call.closed_caption events and renders them live.
5. The Python agent joins the same call (matching call ID), transcribes speech through Gemini Realtime, stores it, and when it detects the phrase "Hey Assistant" it answers the question using the transcript as context.

🚀 Getting Started
Prerequisites
Node.js 18+ and npm
Python 3.13+ and uv
A Stream account (API key and secret, with Video and Chat enabled)
A Google AI Studio API key for Gemini

🤝 Contributing

# 🤝 Contributions, issues and feature requests are welcome. Fork the repo, create a feature branch, and open a pull request.

# 👤 Author ->Aman – @Aman756494