import React from "react";

export interface TraceSummary {
  trace_id?: string;
  trace_count: number;
  redacted_summary: string;
}

export function TracePanel({ summary }: { summary: TraceSummary }): JSX.Element {
  return (
    <section>
      <h2>Trace Summary</h2>
      <pre>{JSON.stringify(summary, null, 2)}</pre>
    </section>
  );
}
