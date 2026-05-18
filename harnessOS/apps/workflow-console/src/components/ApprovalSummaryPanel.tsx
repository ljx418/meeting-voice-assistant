import type { ApprovalSummary } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface ApprovalSummaryPanelProps {
  approvals: ApprovalSummary[];
}

export function ApprovalSummaryPanel({ approvals }: ApprovalSummaryPanelProps) {
  return (
    <section className="panel">
      <h3>审批摘要</h3>
      {approvals.length === 0 ? <p className="muted">暂无审批</p> : null}
      {approvals.map((approval) => (
        <div key={approval.approval_id}>
          <strong>{approval.approval_id}</strong> <span className="status">{approval.status}</span>
          {approval.reason ? <div>{safeText(approval.reason)}</div> : null}
        </div>
      ))}
    </section>
  );
}
