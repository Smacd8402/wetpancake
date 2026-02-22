import React from "react";

type ScorecardProps = {
  total: number;
  dimensions: Record<string, number>;
};

export function Scorecard({ total, dimensions }: ScorecardProps): JSX.Element {
  return (
    <section>
      <h2>Post-Call Scorecard</h2>
      <p>Total: {total}</p>
      <ul>
        {Object.entries(dimensions).map(([name, score]) => (
          <li key={name}>
            {name}: {score}
          </li>
        ))}
      </ul>
    </section>
  );
}
