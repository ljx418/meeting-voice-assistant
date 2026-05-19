import type { ApprovalSummary } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface ApprovalPanelProps {
  approvals: ApprovalSummary[];
  onRespond?: (approvalId: string, decision: "approve" | "reject") => void;
}

export function ApprovalPanel({ approvals, onRespond }: ApprovalPanelProps) {
  return (
    <section className="operation-panel" aria-label="审批面板">
      <div className="panel-heading">
        <span className="eyebrow">Approval</span>
        <h3>审批面板</h3>
        <small>仅用户显式确认后响应 workflow-bound approval</small>
      </div>
      {approvals.length === 0 ? <p className="muted">暂无待处理审批</p> : null}
      {approvals.map((approval) => {
        const inactive = approval.active === false || approval.status !== "pending";
        return (
          <article className="operation-card" key={approval.approval_id}>
            <div>
              <strong>{approval.request_summary || approval.approval_id}</strong>
              <span className="status">{approval.status}</span>
            </div>
            {approval.inactive_reason ? <small>{safeText(approval.inactive_reason)}</small> : null}
            <div className="button-row">
              <button disabled={inactive} type="button" onClick={() => onRespond?.(approval.approval_id, "approve")}>
                用户确认通过
              </button>
              <button disabled={inactive} type="button" onClick={() => onRespond?.(approval.approval_id, "reject")}>
                用户确认拒绝
              </button>
            </div>
          </article>
        );
      })}
    </section>
  );
}
