import type {
  DialogueTurnRequest,
  DialogueTurnResponse,
  ScoreSessionRequest,
  ScoreSessionResponse,
  SessionCreateRequest,
  SessionCreateResponse,
} from "../types/session";

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

export async function transcribeAudio(audioBlob: Blob): Promise<string> {
  const form = new FormData();
  form.append("audio", audioBlob, "turn.wav");

  const resp = await fetch(`${API_BASE}/stt/transcribe`, {
    method: "POST",
    body: form,
  });

  if (!resp.ok) {
    throw new Error(`Failed transcribing audio: ${resp.status}`);
  }

  const body = (await resp.json()) as { text: string };
  return body.text;
}

export async function generateDialogueTurn(
  payload: DialogueTurnRequest,
): Promise<DialogueTurnResponse> {
  const resp = await fetch(`${API_BASE}/dialogue/turn`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      trust: payload.trust,
      resistance: payload.resistance,
      trainee_text: payload.traineeText,
      primary_objection: payload.primaryObjection,
    }),
  });

  if (!resp.ok) {
    throw new Error(`Failed dialogue turn: ${resp.status}`);
  }

  return (await resp.json()) as DialogueTurnResponse;
}

export async function synthesizeSpeech(text: string): Promise<ArrayBuffer> {
  const resp = await fetch(`${API_BASE}/tts/synthesize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  if (!resp.ok) {
    throw new Error(`Failed speech synthesis: ${resp.status}`);
  }

  return await resp.arrayBuffer();
}

export async function scoreSession(
  payload: ScoreSessionRequest,
): Promise<ScoreSessionResponse> {
  const resp = await fetch(`${API_BASE}/sessions/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    throw new Error(`Failed session scoring: ${resp.status}`);
  }

  return (await resp.json()) as ScoreSessionResponse;
}
