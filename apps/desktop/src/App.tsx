import React, { useMemo, useState } from "react";

import { CallScreen } from "./components/CallScreen";
import { Scorecard } from "./components/Scorecard";
import {
  createSession,
  generateDialogueTurn,
  scoreSession,
  synthesizeSpeech,
  transcribeAudio,
} from "./lib/api";
import { createPressToTalkRecorder, playWavBytes } from "./lib/audio";
import type { ScoreSessionResponse, TranscriptTurn } from "./types/session";

type AppState = "idle" | "in_call" | "post_call";

const EMPTY_SCORE: ScoreSessionResponse = {
  total_score: 0,
  dimensions: {},
  misses: [],
  replacement_phrasing: { actual: "", stronger: "" },
};

export function App(): JSX.Element {
  const [state, setState] = useState<AppState>("idle");
  const [sessionId, setSessionId] = useState<string>("");
  const [transcript, setTranscript] = useState<TranscriptTurn[]>([]);
  const [trust, setTrust] = useState<number>(0.4);
  const [resistance, setResistance] = useState<number>(0.6);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [isProcessingTurn, setIsProcessingTurn] = useState<boolean>(false);
  const [closeAttempt, setCloseAttempt] = useState<boolean>(false);
  const [valueStatement, setValueStatement] = useState<boolean>(false);
  const [objectionResolved, setObjectionResolved] = useState<boolean>(false);
  const [score, setScore] = useState<ScoreSessionResponse>(EMPTY_SCORE);

  const recorder = useMemo(() => createPressToTalkRecorder(), []);

  async function startCall(): Promise<void> {
    const created = await createSession({ durationMinutes: 8 });
    setSessionId(created.session_id);
    setTranscript([]);
    setTrust(0.4);
    setResistance(0.6);
    setCloseAttempt(false);
    setValueStatement(false);
    setObjectionResolved(false);
    setState("in_call");
  }

  async function onPressStart(): Promise<void> {
    if (isProcessingTurn || isRecording) return;
    setIsRecording(true);
    await recorder.start();
  }

  async function onPressEnd(): Promise<void> {
    if (!isRecording) return;
    setIsRecording(false);
    setIsProcessingTurn(true);

    try {
      const audioBlob = await recorder.stop();
      const traineeText = await transcribeAudio(audioBlob);
      const traineeTurn: TranscriptTurn = {
        speaker: "trainee",
        text: traineeText,
        ts: new Date().toISOString(),
      };
      setTranscript((prev) => [...prev, traineeTurn]);

      const dialogue = await generateDialogueTurn({
        trust,
        resistance,
        traineeText,
        primaryObjection: "busy",
      });

      setTrust(dialogue.trust);
      setResistance(dialogue.resistance);

      const prospectTurn: TranscriptTurn = {
        speaker: "prospect",
        text: dialogue.text,
        ts: new Date().toISOString(),
      };
      setTranscript((prev) => [...prev, prospectTurn]);

      const wav = await synthesizeSpeech(dialogue.text);
      await playWavBytes(wav);
    } finally {
      setIsProcessingTurn(false);
    }
  }

  async function endCall(): Promise<void> {
    if (!sessionId) return;
    const scored = await scoreSession({
      transcript,
      outcomes: {
        close_attempt: closeAttempt,
        value_statement: valueStatement,
        objection_resolved: objectionResolved,
      },
    });
    setScore(scored);
    setState("post_call");
  }

  if (state === "in_call") {
    return (
      <CallScreen
        transcript={transcript}
        isRecording={isRecording}
        isProcessingTurn={isProcessingTurn}
        closeAttempt={closeAttempt}
        valueStatement={valueStatement}
        objectionResolved={objectionResolved}
        onCloseAttemptChange={setCloseAttempt}
        onValueStatementChange={setValueStatement}
        onObjectionResolvedChange={setObjectionResolved}
        onPressStart={onPressStart}
        onPressEnd={onPressEnd}
        onEndCall={endCall}
      />
    );
  }

  if (state === "post_call") {
    return (
      <Scorecard
        total={score.total_score}
        dimensions={score.dimensions}
        misses={score.misses}
        replacement={score.replacement_phrasing}
      />
    );
  }

  return (
    <main>
      <h1>Wetpancake B2B Call Trainer</h1>
      <button onClick={() => void startCall()} type="button">
        Start Call
      </button>
    </main>
  );
}
