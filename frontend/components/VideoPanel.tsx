"use client";

import { useEffect, useState } from "react";
import { BACKEND_URL } from "@/lib/api";
import { useBackend } from "./BackendProvider";

function Clock() {
  const [now, setNow] = useState<string>("");
  useEffect(() => {
    const tick = () => setNow(new Date().toLocaleTimeString("en-GB"));
    tick();
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, []);
  return <>{now}</>;
}

// The red/amber alert bar laid over the top edge of the video.
function AlertBanner() {
  const { state } = useBackend();
  if (!state || state.status !== "running") return null;

  if (state.in_zone > 0) {
    return (
      <div className="alarm-flash absolute inset-x-0 top-0 z-10 bg-danger px-4 py-2 text-center text-sm font-bold uppercase tracking-wider text-white">
        Danger zone: {state.in_zone} worker{state.in_zone > 1 ? "s" : ""} inside
      </div>
    );
  }
  const parts: string[] = [];
  if (state.missing_helmet > 0)
    parts.push(`${state.missing_helmet} without a helmet`);
  if (state.missing_vest > 0) parts.push(`${state.missing_vest} without a vest`);
  if (parts.length === 0) return null;
  return (
    <div className="absolute inset-x-0 top-0 z-10 bg-warn px-4 py-2 text-center text-sm font-bold uppercase tracking-wider text-background">
      PPE missing: {parts.join(", ")}
    </div>
  );
}

// The video area: the live stream when running, a black panel with a message otherwise.
export default function VideoPanel({ streamKey }: { streamKey: number }) {
  const { state } = useBackend();
  const running = state?.status === "running";

  let message = "Press Start to begin";
  if (state === null || state.status === "unavailable")
    message = "Camera unavailable, check the connection";

  return (
    <div className="relative aspect-video w-full overflow-hidden rounded border border-line bg-black">
      {running ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          key={streamKey}
          src={`${BACKEND_URL}/video?k=${streamKey}`}
          alt="Live camera with detected workers"
          className="h-full w-full object-contain"
        />
      ) : (
        <div className="flex h-full items-center justify-center px-6 text-center font-mono text-sm text-steel">
          {message}
        </div>
      )}

      <AlertBanner />

      {/* Camera-frame marks, label and clock */}
      <span className="frame-corner tl" />
      <span className="frame-corner tr" />
      <span className="frame-corner bl" />
      <span className="frame-corner br" />
      <span className="absolute bottom-3 left-12 font-mono text-xs font-semibold tracking-wider text-white/90 drop-shadow">
        CAM-01 · ZONE A
      </span>
      <span className="absolute bottom-3 right-12 font-mono text-xs font-semibold tracking-wider text-white/90 drop-shadow">
        <Clock />
      </span>
      {running && (
        <span className="absolute left-12 top-12 z-0 flex items-center gap-2 rounded bg-black/60 px-2 py-1 font-mono text-xs font-semibold text-white">
          <span className="h-2 w-2 animate-pulse rounded-full bg-danger" />
          REC
        </span>
      )}
    </div>
  );
}
