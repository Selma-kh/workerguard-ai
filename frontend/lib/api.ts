// Calls to the Python backend.

export const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export type BackendState = {
  status: "stopped" | "running" | "unavailable";
  workers: number;
};

export async function getState(): Promise<BackendState> {
  const response = await fetch(`${BACKEND_URL}/api/state`, { cache: "no-store" });
  if (!response.ok) throw new Error("Backend returned an error");
  return response.json();
}

export async function startCamera(): Promise<BackendState> {
  const response = await fetch(`${BACKEND_URL}/api/start`, { method: "POST" });
  if (!response.ok) throw new Error("Could not start the camera");
  return response.json();
}

export async function stopCamera(): Promise<BackendState> {
  const response = await fetch(`${BACKEND_URL}/api/stop`, { method: "POST" });
  if (!response.ok) throw new Error("Could not stop the camera");
  return response.json();
}
