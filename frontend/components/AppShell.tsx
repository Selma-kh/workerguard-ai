"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { BackendProvider, useBackend } from "./BackendProvider";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: "▦" },
  { href: "/events", label: "Event Log", icon: "☰" },
];

function StatusBadge() {
  const { state } = useBackend();
  let label = "Backend not reachable";
  let color = "bg-danger";
  if (state?.status === "running") {
    label = "System online";
    color = "bg-ok";
  } else if (state?.status === "stopped") {
    label = "System idle";
    color = "bg-steel";
  } else if (state?.status === "unavailable") {
    label = "Camera unavailable";
    color = "bg-warn";
  }
  return (
    <span className="flex items-center gap-2 text-sm font-medium text-charcoal">
      <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
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
        <header className="flex h-14 items-center justify-between border-b border-steel-light bg-white px-5">
          <h1 className="text-lg font-semibold text-brand">Worker Safety AI</h1>
          <StatusBadge />
        </header>

        <div className="flex flex-1">
          <nav
            className={`flex flex-col bg-brand text-white transition-all ${
              collapsed ? "w-16" : "w-52"
            }`}
          >
            <button
              onClick={() => setCollapsed(!collapsed)}
              aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
              className="h-12 px-5 text-left text-lg hover:bg-brand-dark"
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
                  className={`flex h-12 items-center gap-3 px-5 text-sm font-medium hover:bg-brand-dark ${
                    active ? "bg-brand-dark" : ""
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
