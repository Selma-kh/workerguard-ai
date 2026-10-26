"use client";

import { useCallback, useEffect, useRef } from "react";

// Plays the siren in a loop while `active` is true and `muted` is false.
// Browsers only allow sound after the person has clicked on the page, so `unlock`
// must be called from a click (the Start button).
export function useSiren(active: boolean, muted: boolean) {
  const audio = useRef<HTMLAudioElement | null>(null);

  const unlock = useCallback(() => {
    if (!audio.current) {
      audio.current = new Audio("/siren.wav");
      audio.current.loop = true;
    }
    // Play and immediately pause once, inside the click, to be allowed to play later.
    audio.current
      .play()
      .then(() => audio.current?.pause())
      .catch(() => {});
  }, []);

  useEffect(() => {
    const element = audio.current;
    if (!element) return;
    if (active && !muted) {
      element.play().catch(() => {});
    } else {
      element.pause();
      element.currentTime = 0;
    }
  }, [active, muted]);

  return { unlock };
}
