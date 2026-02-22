import React from "react";

type CallScreenProps = {
  onEndCall: () => void;
};

export function CallScreen({ onEndCall }: CallScreenProps): JSX.Element {
  return (
    <section>
      <h2>Call in progress</h2>
      <p>Live prospect simulation is active.</p>
      <button onClick={onEndCall} type="button">
        End Call
      </button>
    </section>
  );
}
