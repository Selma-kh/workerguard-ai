"use client";

import { useBackend } from "./BackendProvider";

function Card({
  label,
  value,
  accent,
  caption,
}: {
  label: string;
  value: string;
  accent: string;
  caption?: string;
}) {
  return (
    <div className={`rounded border border-line border-t-4 bg-panel px-4 py-3 ${accent}`}>
      <div className="text-xs font-semibold uppercase tracking-wider text-steel">
        {label}
      </div>
      <div className="mt-1 font-mono text-4xl font-bold text-white">{value}</div>
      {caption && <div className="mt-1 text-xs text-steel">{caption}</div>}
    </div>
  );
}

// Real counts straight from the video. Shows "–" when nothing is being measured.
export default function KpiCards() {
  const { state } = useBackend();
  const live = state?.status === "running";
  const show = (n?: number) => (live && n !== undefined ? String(n) : "–");

  return (
    <div className="grid grid-cols-3 gap-4">
      <Card label="Workers" value={show(state?.workers)} accent="border-t-brand" />
      <Card
        label="Violations"
        value={show(state?.workers_with_violation)}
        accent="border-t-warn"
        caption="workers with at least one"
      />
      <Card
        label="In danger zone"
        value={show(state?.in_zone)}
        accent="border-t-danger"
      />
    </div>
  );
}
