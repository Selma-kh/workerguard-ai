"use client";

import { useEffect, useState } from "react";
import { Alert, BACKEND_URL, EventLogData, getEvents } from "@/lib/api";

function Stat({ label, value, accent }: { label: string; value: string; accent: string }) {
  return (
    <div className={`rounded border border-line border-t-4 bg-panel px-4 py-3 ${accent}`}>
      <div className="text-xs font-semibold uppercase tracking-wider text-steel">{label}</div>
      <div className="mt-1 font-mono text-3xl font-bold text-white">{value}</div>
    </div>
  );
}

export default function EventLog() {
  const [data, setData] = useState<EventLogData | null>(null);
  const [failed, setFailed] = useState(false);
  const [open, setOpen] = useState<Alert | null>(null);

  // Ask the backend for this session's incidents once a second.
  useEffect(() => {
    const load = () =>
      getEvents()
        .then((d) => {
          setData(d);
          setFailed(false);
        })
        .catch(() => setFailed(true));
    load();
    const timer = setInterval(load, 1000);
    return () => clearInterval(timer);
  }, []);

  const summary = data?.summary;
  const events = data?.events ?? [];

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-bold uppercase tracking-wider text-white">Event Log</h2>
        <a
          href={`${BACKEND_URL}/api/export.csv`}
          download
          className="rounded bg-brand px-5 py-2 text-sm font-bold uppercase tracking-wider text-white hover:bg-brand-mid"
        >
          Download CSV
        </a>
      </div>

      {failed && (
        <p className="mb-4 rounded border border-danger bg-danger/10 px-4 py-3 text-sm text-danger">
          Backend not reachable. Start it, then reload this page.
        </p>
      )}

      <p className="mb-2 text-xs uppercase tracking-wider text-steel">This session</p>
      <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-5">
        <Stat label="Incidents" value={String(summary?.total ?? 0)} accent="border-t-brand" />
        <Stat label="Missing helmet" value={String(summary?.no_helmet ?? 0)} accent="border-t-warn" />
        <Stat label="Missing vest" value={String(summary?.no_vest ?? 0)} accent="border-t-warn" />
        <Stat label="Zone entries" value={String(summary?.zone_entry ?? 0)} accent="border-t-danger" />
        <Stat
          label="Workers with no violation"
          value={
            summary?.compliance_percent == null ? "–" : `${summary.compliance_percent}%`
          }
          accent="border-t-ok"
        />
      </div>

      <div className="rounded border border-line bg-panel">
        {events.length === 0 ? (
          <p className="px-4 py-8 text-sm text-steel">
            No incidents in this session yet. They appear here as soon as an alert fires.
          </p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-line text-left text-xs uppercase tracking-wider text-steel">
                <th className="px-4 py-3">Time</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Worker</th>
                <th className="px-4 py-3">Snapshot</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event) => (
                <tr key={event.id} className="border-b border-line last:border-0">
                  <td className="px-4 py-2 font-mono text-xs text-steel-light">{event.time}</td>
                  <td className="px-4 py-2">
                    <span
                      className={`rounded px-2 py-0.5 text-xs font-bold uppercase ${
                        event.type === "zone_entry"
                          ? "bg-danger/20 text-danger"
                          : "bg-warn/20 text-warn"
                      }`}
                    >
                      {event.label}
                    </span>
                  </td>
                  <td className="px-4 py-2 font-mono text-xs text-steel-light">
                    Worker {event.person_id}
                  </td>
                  <td className="px-4 py-2">
                    {event.snapshot_file && (
                      <button onClick={() => setOpen(event)} title="Click to enlarge">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={`${BACKEND_URL}/snapshots/${event.snapshot_file}`}
                          alt={`Snapshot: ${event.label}`}
                          className="h-14 w-24 rounded border border-line object-cover"
                        />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {open && open.snapshot_file && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-6"
          onClick={() => setOpen(null)}
        >
          <div className="max-h-full max-w-4xl" onClick={(e) => e.stopPropagation()}>
            <div className="mb-2 flex items-center justify-between text-sm text-white">
              <span>
                {open.time} · {open.label} · Worker {open.person_id}
              </span>
              <button onClick={() => setOpen(null)} className="rounded bg-panel-2 px-3 py-1">
                Close
              </button>
            </div>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`${BACKEND_URL}/snapshots/${open.snapshot_file}`}
              alt={`Snapshot: ${open.label}`}
              className="max-h-[80vh] rounded border border-line"
            />
          </div>
        </div>
      )}
    </div>
  );
}
