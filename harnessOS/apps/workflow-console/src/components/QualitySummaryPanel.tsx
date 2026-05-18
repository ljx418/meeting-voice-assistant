import type { QualitySummary } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface QualitySummaryPanelProps {
  evaluations: QualitySummary[];
}

export function QualitySummaryPanel({ evaluations }: QualitySummaryPanelProps) {
  return (
    <section className="panel">
      <h3>质量摘要</h3>
      {evaluations.length === 0 ? <p className="muted">暂无质量评估</p> : null}
      {evaluations.map((evaluation) => (
        <div key={evaluation.evaluation_id}>
          <strong>{evaluation.evaluation_id}</strong> <span className="status">{evaluation.status}</span>
          {evaluation.score !== undefined ? <div>分数：{evaluation.score}</div> : null}
          {evaluation.issues ? <small>{safeText(evaluation.issues)}</small> : null}
        </div>
      ))}
    </section>
  );
}
