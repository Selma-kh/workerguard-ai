"use client";

import { useState } from "react";
import { useBackend } from "@/components/BackendProvider";
import VideoPanel from "@/components/VideoPanel";
import { startCamera, stopCamera } from "@/lib/api";

export default function Dashboard() {
  const { state, refresh } = useBackend();
  const [streamKey, setStreamKey] = useState(0);
  const running = state?.status === "running";

  async function toggle() {
    try {
      if (running) await stopCamera();
      else {
        await startCamera();
        setStreamKey((k) => k + 1); // new key = a fresh video connection
      }
    } catch {
      // the status badge and video panel already show when the backend is down
    }
    refresh();
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-semibold text-charcoal">Dashboard</h2>
        <button
          onClick={toggle}
          disabled={state === null}
          className="rounded bg-brand px-5 py-2 text-sm font-semibold text-white hover:bg-brand-dark disabled:opacity-50"
        >
          {running ? "Stop" : "Start"}
        </button>
      </div>

      <VideoPanel streamKey={streamKey} />

      <p className="mt-3 text-sm text-steel">
        People in view: {running ? state?.workers ?? 0 : "–"}
      </p>
    </div>
  );
}
