import { StreamClient } from "@stream-io/node-sdk";

export async function POST(request) {
  try {
    const apiKey = process.env.STREAM_API_KEY?.trim();
    const apiSecret = process.env.STREAM_API_SECRET?.trim();

    if (!apiKey) {
      return Response.json(
        { error: "STREAM_API_KEY missing" },
        { status: 500 },
      );
    }
    if (!apiSecret) {
      return Response.json(
        { error: "STREAM_API_SECRET missing" },
        { status: 500 },
      );
    }

    const { userId } = await request.json();
    if (!userId) {
      return Response.json(
        { error: "userId missing in request" },
        { status: 400 },
      );
    }

    const serverClient = new StreamClient(apiKey, apiSecret);

    await serverClient.upsertUsers([
      { id: userId, role: "admin", name: userId },
    ]);

    const now = Math.floor(Date.now() / 1000);
    const token = serverClient.generateUserToken({
      user_id: userId,
      validity_in_seconds: 60 * 60 * 24,
      iat: now - 60,
    });

    return Response.json({ token });
  } catch (error) {
    console.error("Token generation error:", error);
    return Response.json(
      {
        error: "Failed to generate token",
        detail: String(error?.message || error),
      },
      { status: 500 },
    );
  }
}
