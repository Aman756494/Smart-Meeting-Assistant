import { StreamVideoClient } from "@stream-io/node-sdk";
import { useEffect, useState } from "react";
import { StreamChat } from "stream-chat";

export function userStreamClients({ apiKey, user, token }) {
  const [videoClient, setVideoClient] = useState(null);
  const [chatClient, setChatClient] = useState(null);

  useEffect(() => {
    if (!user || !token || !apiKey) return;

    let isMounted = true;

    const initClients = async () => {
      try {
        const tokenProvider = () => Promise.resolve(token);

        const myVideoClient = new StreamVideoClient({
          apiKey,
          user,
          tokenProvider,
        });

        const myChatClient = StreamChat.getInstance(apiKey);
        await myChatClient.connectUser(user, token);

        if (isMounted) {
          setVideoClient(myVideoClient);
          setChatClient(myChatClient);
        }
      } catch (error) {
        console.error("Client initialization error:", error);
      }
    };
    initClients();

    return () => {
      isMounted = false;
      if (videoClient) {
        videoClient.disconnectUser().catch(console.error);
      }
      if (chatClient) {
        chatClient.disconnectUser().catch(console.error);
      }
    };
  }, [apiKey, user, token]);
  return { videoClient, chatClient };
}
