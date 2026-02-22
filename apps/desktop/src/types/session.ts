export type SessionCreateRequest = {
  durationMinutes: number;
};

export type SessionCreateResponse = {
  session_id: string;
  seed: number;
};

export type DialogueTurnRequest = {
  trust: number;
  resistance: number;
  traineeText: string;
  primaryObjection: string;
};

export type DialogueTurnResponse = {
  text: string;
  trust: number;
  resistance: number;
};

export type TranscriptTurn = {
  speaker: "trainee" | "prospect";
  text: string;
  ts: string;
};

export type ScoreSessionRequest = {
  transcript: TranscriptTurn[];
  outcomes: {
    close_attempt: boolean;
    value_statement: boolean;
    objection_resolved: boolean;
  };
};

export type ScoreSessionResponse = {
  total_score: number;
  dimensions: Record<string, number>;
  misses: string[];
  replacement_phrasing: {
    actual: string;
    stronger: string;
  };
};
