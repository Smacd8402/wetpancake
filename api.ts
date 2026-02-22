import type { SessionCreateRequest, SessionCreateResponse } from "../types/session";

const API_BASE = "http://127.0.0.1:8000";

export async function createSession(
  payload: SessionCreateRequest,
): Promise<SessionCreateResponse> {
  const resp = await fetch(`${API_BASE}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ duration_minutes: payload.durationMinutes }),
  });

  if (!resp.ok) {
    throw new Error(`Failed creating session: ${resp.status}`);
  }

  return (await resp.json()) as SessionCreateResponse;
}
