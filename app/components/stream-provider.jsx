import { StreamVideo } from "@stream-io/video-react-sdk";
import { useStreamClients } from "../hooks/use-stream-clients";
import { Chat } from "stream-chat-react";

const apiKey = process.env.NEXT_PUBLIC_STREAM_API_KEY;

export default function StreamProvider({ children, user, token }) {
  const { videoClient, chatClient } = useStreamClients({ apiKey, user, token });

  if (!videoClient || !chatClient) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-linear-to-br from-gray-900 via-gray-800 to-gray-900">
        <p className="text-white text-xl font-semibold mt-6">Connecting...</p>
      </div>
    );
  }

  return (
    <StreamVideo client={videoClient}>
      <Chat client={chatClient}>{children}</Chat>
    </StreamVideo>
  );
}
