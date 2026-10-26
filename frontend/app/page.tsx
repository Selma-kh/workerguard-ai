"use client";

import { useState } from "react";
import AlertList from "@/components/AlertList";
import { useBackend } from "@/components/BackendProvider";
import KpiCards from "@/components/KpiCards";
import VideoPanel from "@/components/VideoPanel";
import { startCamera, stopCamera } from "@/lib/api";
import { useSiren } from "@/lib/useSiren";

export default function Dashboard() {
  const { state, refresh } = useBackend();
  const [streamKey, setStreamKey] = useState(0);
  const [muted, setMuted] = useState(false);
  const running = state?.status === "running";
  const { unlock } = useSiren(running && (state?.in_zone ?? 0) > 0, muted);

  async function toggle() {
    try {
      if (running) await stopCamera();
      else {
        unlock(); // this click is what lets the browser play the siren later
        await startCamera();
        setStreamKey((k) => k + 1); // new key = a fresh video connection
      }
    } catch {
      // the status light and video panel already show when the backend is down
    }
    refresh();
  }

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-bold uppercase tracking-wider text-white">
          Dashboard
        </h2>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setMuted((m) => !m)}
            className={`rounded border px-4 py-2 text-sm font-semibold ${
              muted
                ? "border-warn bg-warn/15 text-warn"
                : "border-line bg-panel-2 text-steel-light hover:bg-panel"
            }`}
          >
            {muted ? "🔇 Siren muted" : "🔊 Siren on"}
          </button>
          <button
            onClick={toggle}
            disabled={state === null}
            className="rounded bg-brand px-6 py-2 text-sm font-bold uppercase tracking-wider text-white hover:bg-brand-mid disabled:opacity-50"
          >
            {running ? "Stop" : "Start"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1fr_20rem]">
        <div className="space-y-4">
          <VideoPanel streamKey={streamKey} />
          <KpiCards />
        </div>
        <AlertList />
      </div>
    </div>
  );
}
