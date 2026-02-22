import React from "react";

import type { TranscriptTurn } from "../types/session";

type CallScreenProps = {
  transcript: TranscriptTurn[];
  isRecording: boolean;
  isProcessingTurn: boolean;
  closeAttempt: boolean;
  valueStatement: boolean;
  objectionResolved: boolean;
  onCloseAttemptChange: (next: boolean) => void;
  onValueStatementChange: (next: boolean) => void;
  onObjectionResolvedChange: (next: boolean) => void;
  onPressStart: () => Promise<void>;
  onPressEnd: () => Promise<void>;
  onEndCall: () => Promise<void>;
};

export function CallScreen({
  transcript,
  isRecording,
  isProcessingTurn,
  closeAttempt,
  valueStatement,
  objectionResolved,
  onCloseAttemptChange,
  onValueStatementChange,
  onObjectionResolvedChange,
  onPressStart,
  onPressEnd,
  onEndCall,
}: CallScreenProps): JSX.Element {
  return (
    <section>
      <h2>Call in progress</h2>
      <p>{isProcessingTurn ? "Processing turn..." : "Live prospect simulation is active."}</p>

      <button
        type="button"
        onMouseDown={() => void onPressStart()}
        onMouseUp={() => void onPressEnd()}
        onMouseLeave={() => {
          if (isRecording) {
            void onPressEnd();
          }
        }}
      >
        {isRecording ? "Release To Send" : "Hold To Talk"}
      </button>

      <div>
        <label>
          <input
            checked={closeAttempt}
            onChange={(e) => onCloseAttemptChange(e.target.checked)}
            type="checkbox"
          />
          Close attempt made
        </label>
        <label>
          <input
            checked={valueStatement}
            onChange={(e) => onValueStatementChange(e.target.checked)}
            type="checkbox"
          />
          Value statement delivered
        </label>
        <label>
          <input
            checked={objectionResolved}
            onChange={(e) => onObjectionResolvedChange(e.target.checked)}
            type="checkbox"
          />
          Objection resolved
        </label>
      </div>

      <h3>Transcript</h3>
      <ul>
        {transcript.map((turn, idx) => (
          <li key={`${turn.ts}-${idx}`}>
            <strong>{turn.speaker}:</strong> {turn.text}
          </li>
        ))}
      </ul>

      <button onClick={() => void onEndCall()} type="button">
        End Call
      </button>
    </section>
  );
}
