"use client";

import { useBackend } from "./BackendProvider";

// The live list of incidents: time and what the violation was. Newest first.
export default function AlertList() {
  const { state } = useBackend();
  const alerts = state?.alerts ?? [];

  return (
    <section className="flex h-full flex-col rounded border border-line bg-panel">
      <h3 className="border-b border-line px-4 py-3 text-xs font-bold uppercase tracking-wider text-steel-light">
        Live alerts
      </h3>
      {alerts.length === 0 ? (
        <p className="px-4 py-6 text-sm text-steel">No alerts, everything is fine</p>
      ) : (
        <ul className="max-h-[32rem] flex-1 overflow-y-auto">
          {alerts.map((alert) => {
            const danger = alert.type === "zone_entry";
            return (
              <li
                key={alert.id}
                className={`flex items-center gap-3 border-b border-line border-l-4 px-4 py-2.5 text-sm ${
                  danger ? "border-l-danger" : "border-l-warn"
                }`}
              >
                <span className="font-mono text-xs text-steel">{alert.time}</span>
                <span className="flex-1 font-medium text-white">{alert.label}</span>
                <span className="font-mono text-xs text-steel-light">
                  Worker {alert.person_id}
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
