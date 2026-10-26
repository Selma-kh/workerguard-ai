"use client";

import { BACKEND_URL } from "@/lib/api";
import { useBackend } from "./BackendProvider";

// The video area: the live stream when running, a black panel with a message otherwise.
export default function VideoPanel({ streamKey }: { streamKey: number }) {
  const { state } = useBackend();
  const running = state?.status === "running";

  let message = "Press Start to begin";
  if (state === null) message = "Camera unavailable, check the connection";
  else if (state.status === "unavailable")
    message = "Camera unavailable, check the connection";

  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-lg bg-black">
      {running ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          key={streamKey}
          src={`${BACKEND_URL}/video?k=${streamKey}`}
          alt="Live camera with detected workers"
          className="h-full w-full object-contain"
        />
      ) : (
        <div className="flex h-full items-center justify-center px-6 text-center text-sm text-steel-light">
          {message}
        </div>
      )}
      {running && (
        <span className="absolute right-3 top-3 flex items-center gap-2 rounded bg-black/60 px-2 py-1 text-xs font-semibold text-white">
          <span className="h-2 w-2 animate-pulse rounded-full bg-danger" />
          LIVE
        </span>
      )}
    </div>
  );
}
