"use client";

import { useCall } from "@stream-io/video-react-sdk";
import React, { useEffect, useRef, useState } from "react";
import { useChatContext } from "stream-chat-react";

const TranscriptPanel = () => {
  const { client } = useChatContext();
  const [transcripts, setTranscripts] = useState([]);
  const transcriptEndRef = useRef(null);
  const call = useCall();

    useEffect(() => {
      transcriptEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [transcripts]);

  useEffect(() => {
    if (!call) {
      console.log("⚠️ Call not ready");
      return;
    }

    const callId = process.env.NEXT_PUBLIC_CALL_ID;
    const channel = client.channel("messaging", callId);
    channel.watch();

    const handleClosedCaption = (event) => {
      if (event.closed_caption) {
        const newTranscript = {
          text: event.closed_caption.text,
          speaker:
            event.closed_caption.user?.name ||
            event.closed_caption.user?.id ||
            "Unknown",
          timestamp: new Date(
            event.closed_caption.start_time,
          ).toLocaleTimeString(),
        };

        setTranscripts((prev) => [...prev, newTranscript]);
      }
    };

    call.on("call.closed_caption", handleClosedCaption);

    return () => {
      console.log("🧹 Cleaning up caption listeners");
      call.off("call.closed_caption", handleClosedCaption);
    };
  }, [call]);

  return (
    <div className="h-full flex flex-col">
      <div className="px-6 py-5 border-b border-gray-700 bg-linear-to-r from-gray-800 to-gray-750 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/10 rounded-lg text-2xl">📝</div>

          <div>
            <h3 className="text-lg font-bold text-white">Live Transcript</h3>
            <p className="text-xs text-gray-400 mt-0.5">
              {transcripts.length}{""}
              {transcripts.length === 1 ? "message" : "messages"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-xs text-green-500 font-medium">Live</span>
        </div>
      </div>

      {/* Transcript List */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3 bg-gray-850 custom-scroller">
        {transcripts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-4">
            <p className="text-gray-300 text-lg font-semibold mb-2">
              Waiting for transcripts                 
            </p>

            <p className="text-gray-500 text-sm max-w-xs">
              Start speaking to see live transcription appear here
            </p>
          </div>
        ) : (
          <>
          {transcripts.map((transcript, idx) => (
              <div
                  key={idx}
                  className="bg-gray-700/50 rounded-lg p-4 hover:bg-gray-700 transition"
              >
                  
                  <div className="flex items-center gap-2 mb-2">
                      <span className="font-medium text-blue-400 text-sm">
                        {transcript.speaker}
                      </span>
                      <span className="text-xs text-gray-500">
                          {transcript.timestamp}
                      </span>
                  </div>
                  <p className="text-gray-200 text-sm">{transcript.text}</p>
              </div>
          ))}
              <div ref={transcriptEndRef}></div>
          </>
        )}
      </div>
    </div>
  );
};

export default TranscriptPanel;
