import type { TraceSummary } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface TraceSummaryPanelProps {
  traceSummary?: TraceSummary;
}

export function TraceSummaryPanel({ traceSummary }: TraceSummaryPanelProps) {
  return (
    <section className="panel">
      <h3>Trace 摘要</h3>
      {traceSummary ? (
        <div>
          <strong>{traceSummary.trace_id || "trace"}</strong>
          <p>{safeText(traceSummary.summary || traceSummary)}</p>
        </div>
      ) : (
        <p className="muted">暂无 Trace 摘要</p>
      )}
    </section>
  );
}
