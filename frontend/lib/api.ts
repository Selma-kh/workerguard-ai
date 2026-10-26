// Calls to the Python backend.

export const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export type Alert = {
  id: number;
  time: string;
  type: "zone_entry" | "no_helmet" | "no_vest";
  label: string;
  person_id: number;
  snapshot_file: string | null;
};

export type BackendState = {
  status: "stopped" | "running" | "unavailable";
  workers: number;
  in_zone: number;
  missing_helmet: number;
  missing_vest: number;
  violations: number;
  alerts: Alert[];
};

export async function getState(): Promise<BackendState> {
  const response = await fetch(`${BACKEND_URL}/api/state`, { cache: "no-store" });
  if (!response.ok) throw new Error("Backend returned an error");
  return response.json();
}

export async function startCamera(): Promise<void> {
  const response = await fetch(`${BACKEND_URL}/api/start`, { method: "POST" });
  if (!response.ok) throw new Error("Could not start the camera");
}

export async function stopCamera(): Promise<void> {
  const response = await fetch(`${BACKEND_URL}/api/stop`, { method: "POST" });
  if (!response.ok) throw new Error("Could not stop the camera");
}
