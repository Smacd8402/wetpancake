import React, { useState } from "react";

import { CallScreen } from "./components/CallScreen";
import { Scorecard } from "./components/Scorecard";

type AppState = "idle" | "in_call" | "post_call";

const SAMPLE_SCORE = {
  total: 74,
  dimensions: {
    opener_clarity: 78,
    rapport_tone: 72,
    discovery_depth: 70,
    objection_handling: 76,
    value_articulation: 75,
    close_quality: 71,
    talk_listen_balance: 76,
  },
};

export function App(): JSX.Element {
  const [state, setState] = useState<AppState>("idle");

  if (state === "in_call") {
    return <CallScreen onEndCall={() => setState("post_call")} />;
  }

  if (state === "post_call") {
    return <Scorecard total={SAMPLE_SCORE.total} dimensions={SAMPLE_SCORE.dimensions} />;
  }

  return (
    <main>
      <h1>Wetpancake B2B Call Trainer</h1>
      <button onClick={() => setState("in_call")} type="button">
        Start Call
      </button>
    </main>
  );
}
