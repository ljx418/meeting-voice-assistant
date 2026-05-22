import type { QualitySummary } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface QualityPanelProps {
  evaluations: QualitySummary[];
}

export function QualityPanel({ evaluations }: QualityPanelProps) {
  return (
    <section className="operation-panel" aria-label="质量面板" data-testid="quality-panel">
      <div className="panel-heading">
        <span className="eyebrow">Quality</span>
        <h3>质量面板</h3>
        <small>只读刷新，不创建或绑定评估</small>
      </div>
      {evaluations.length === 0 ? <p className="muted">暂无质量评估</p> : null}
      {evaluations.map((evaluation) => (
        <article className="operation-card" key={evaluation.evaluation_id}>
          <div>
            <strong>{evaluation.rubric_id || evaluation.evaluation_id}</strong>
            <span className="status">{evaluation.status}</span>
          </div>
          <p>Score {evaluation.score ?? "manual_required"}</p>
          {evaluation.issues?.length ? <small>Issues {safeText(evaluation.issues)}</small> : null}
          {evaluation.suggestions?.length ? <small>Suggestions {safeText(evaluation.suggestions)}</small> : null}
        </article>
      ))}
    </section>
  );
}
