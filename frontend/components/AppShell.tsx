"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { BackendProvider, useBackend } from "./BackendProvider";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: "▦" },
  { href: "/events", label: "Event Log", icon: "☰" },
];

// An LED-style status light plus a label.
function StatusBadge() {
  const { state } = useBackend();
  let label = "Backend not reachable";
  let led = "bg-danger shadow-[0_0_8px_2px_rgba(239,59,59,0.7)]";
  if (state?.status === "running") {
    label = "System online";
    led = "bg-ok shadow-[0_0_8px_2px_rgba(34,197,94,0.7)]";
  } else if (state?.status === "stopped") {
    label = "System idle";
    led = "bg-steel";
  } else if (state?.status === "unavailable") {
    label = "Camera unavailable";
    led = "bg-warn shadow-[0_0_8px_2px_rgba(245,158,11,0.7)]";
  }
  return (
    <span className="flex items-center gap-2 font-mono text-xs uppercase tracking-wider text-steel-light">
      <span className={`h-3 w-3 rounded-full ${led}`} />
      {label}
    </span>
  );
}

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <BackendProvider>
      <div className="flex min-h-screen flex-col">
        <header className="flex h-14 items-center justify-between border-b border-line bg-panel px-5">
          <div className="flex items-center gap-3">
            <span className="flex h-8 w-8 items-center justify-center rounded bg-warn text-lg font-black text-background">
              ⚠
            </span>
            <h1 className="text-lg font-bold tracking-wide text-white">
              WORKER SAFETY <span className="text-warn">AI</span>
            </h1>
          </div>
          <StatusBadge />
        </header>
        <div className="hazard-stripe h-1.5" />

        <div className="flex flex-1">
          <nav
            className={`flex flex-col border-r border-line bg-brand-dark text-white transition-all ${
              collapsed ? "w-16" : "w-52"
            }`}
          >
            <button
              onClick={() => setCollapsed(!collapsed)}
              aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
              className="h-12 px-5 text-left text-lg text-steel-light hover:bg-brand-mid"
            >
              {collapsed ? "»" : "«"}
            </button>
            {NAV_ITEMS.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  title={item.label}
                  className={`flex h-12 items-center gap-3 border-l-4 px-4 text-sm font-semibold uppercase tracking-wider hover:bg-brand-mid ${
                    active ? "border-warn bg-brand-mid" : "border-transparent"
                  }`}
                >
                  <span className="w-4 text-center">{item.icon}</span>
                  {!collapsed && item.label}
                </Link>
              );
            })}
          </nav>

          <main className="flex-1 p-6">{children}</main>
        </div>
      </div>
    </BackendProvider>
  );
}
