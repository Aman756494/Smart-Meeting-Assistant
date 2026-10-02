import { StreamClient } from "@stream-io/node-sdk";

const apiKey = process.env.STREAM_API_KEY;
const apiSecret = process.env.STREAM_API_SECRET;

export async function POST(request) {
  try {
    const { userId } = await request.json();

    if (!apiKey || !apiSecret) {
      return Response.json(
        { error: "Missing API credentials" },
        { status: 500 },
      );
    }

    const serverClient = new StreamClient(apiKey, apiSecret);

    const newUser = {
      id: userId,
      role: "admin",
      name: userId,
    };

      await serverClient.upsertUsers([newUser]);
      
      const now = Math.floor(Date.now() / 1000); // current time in seconds

    const validity = 60 * 60 * 24;
    const token = serverClient.generateUserToken({
      user_id: userId,
        validity_in_seconds: validity,
      iat: now - 60, // Issue token 60 seconds in the past (fixes timing issues)
    });

    return Response.json({ token });
  } catch (error) {
    console.error("Token generation error:", error);
    return Response.json(
      { error: "Failed to generate token" },
      { status: 500 },
    );
  }
}
