import React from "react";

type ScorecardProps = {
  total: number;
  dimensions: Record<string, number>;
  misses: string[];
  replacement: {
    actual: string;
    stronger: string;
  };
};

export function Scorecard({ total, dimensions, misses, replacement }: ScorecardProps): JSX.Element {
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

      <h3>Top Misses</h3>
      <ul>
        {misses.map((m) => (
          <li key={m}>{m}</li>
        ))}
      </ul>

      <h3>Replacement Phrasing</h3>
      <p>
        <strong>Actual:</strong> {replacement.actual}
      </p>
      <p>
        <strong>Stronger:</strong> {replacement.stronger}
      </p>
    </section>
  );
}
