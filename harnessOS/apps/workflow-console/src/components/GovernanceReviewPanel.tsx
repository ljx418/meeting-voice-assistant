import type { GovernanceReviewSummary, OperationEvidenceRecord } from "../api/types.js";

export interface GovernanceReviewPanelProps {
  evidence?: OperationEvidenceRecord[];
  review?: GovernanceReviewSummary | null;
}

export function GovernanceReviewPanel({ evidence = [], review }: GovernanceReviewPanelProps) {
  const records = review?.operation_evidence?.length ? review.operation_evidence : evidence;
  const statusCounts = review?.summary.status_counts || countBy(records, "status");
  return (
    <section className="panel governance-review" data-testid="governance-review-panel">
      <h3>治理审计</h3>
      <p className="muted">只读证据链：建议来源、交接状态、用户确认和运行结果。</p>
      <div className="governance-summary">
        <span>证据 {records.length}</span>
        <span>交接 {review?.summary.handoff_count || 0}</span>
        <span>成功 {statusCounts.succeeded || 0}</span>
        <span>阻断 {statusCounts.blocked || 0}</span>
      </div>
      <div className="evidence-list">
        {records.length ? (
          records.map((record) => (
            <article className="evidence-card" data-testid="operation-evidence-card" key={record.evidence_id}>
              <header>
                <strong>{record.operation}</strong>
                <span className={`status evidence-${record.status}`}>{labelStatus(record.status)}</span>
              </header>
              <dl>
                <dt>建议</dt>
                <dd>{record.proposal_id || "无"}</dd>
                <dt>交接</dt>
                <dd>{record.handoff_id || "无"} · {record.handoff_status_at_execution || "未绑定"}</dd>
                <dt>用户确认</dt>
                <dd>{record.user_confirmed ? "已确认" : "未确认"}</dd>
                <dt>策略</dt>
                <dd>{record.policy_decision || "user_confirmed"}</dd>
                <dt>运行结果</dt>
                <dd>{record.runtime_result_ref.type}:{record.runtime_result_ref.status}</dd>
              </dl>
            </article>
          ))
        ) : (
          <p className="muted">暂无用户确认操作证据。</p>
        )}
      </div>
    </section>
  );
}

function countBy(records: OperationEvidenceRecord[], key: keyof OperationEvidenceRecord): Record<string, number> {
  return records.reduce<Record<string, number>>((counts, record) => {
    const value = String(record[key] || "unknown");
    counts[value] = (counts[value] || 0) + 1;
    return counts;
  }, {});
}

function labelStatus(status: OperationEvidenceRecord["status"]): string {
  const labels: Record<OperationEvidenceRecord["status"], string> = {
    succeeded: "成功",
    failed: "失败",
    idempotent_replayed: "幂等重放",
    blocked: "已阻断",
    stale_rejected: "已失效",
    expired_rejected: "已过期",
  };
  return labels[status] || status;
}
