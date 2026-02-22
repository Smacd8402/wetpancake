export type SessionCreateRequest = {
  durationMinutes: number;
};

export type SessionCreateResponse = {
  session_id: string;
  seed: number;
};
