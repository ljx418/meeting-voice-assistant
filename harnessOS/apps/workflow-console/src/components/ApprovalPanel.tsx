import type { AgentActionHandoff, ApprovalSummary } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface ApprovalPanelProps {
  approvals: ApprovalSummary[];
  handoff?: AgentActionHandoff | null;
  onRespond?: (approvalId: string, decision: "approve" | "reject", reason?: string, handoff?: AgentActionHandoff | null) => void;
}

export function ApprovalPanel({ approvals, handoff, onRespond }: ApprovalPanelProps) {
  return (
    <section className="operation-panel" aria-label="审批面板" data-testid="approval-panel">
      <div className="panel-heading">
        <span className="eyebrow">Approval</span>
        <h3>审批面板</h3>
        <small>仅用户显式确认后响应 workflow-bound approval</small>
      </div>
      {approvals.length === 0 ? <p className="muted">暂无待处理审批</p> : null}
      {handoff ? <p className="handoff-banner" data-testid="agent-handoff-banner">{handoffMessage(handoff)}</p> : null}
      {approvals.map((approval) => {
        const inactive = approval.active === false || approval.status !== "pending";
        const disabled = inactive || !isHandoffActionable(handoff);
        return (
          <article className="operation-card" key={approval.approval_id}>
            <div>
              <strong>{approval.request_summary || approval.approval_id}</strong>
              <span className="status">{approval.status}</span>
            </div>
            {approval.inactive_reason ? <small>{safeText(approval.inactive_reason)}</small> : null}
            <div className="button-row">
              <button
                data-testid="approval-approve-button"
                disabled={disabled}
                type="button"
                onClick={() => onRespond?.(approval.approval_id, "approve", undefined, handoff)}
              >
                用户确认通过
              </button>
              <button disabled={disabled} type="button" onClick={() => onRespond?.(approval.approval_id, "reject", undefined, handoff)}>
                用户确认拒绝
              </button>
            </div>
          </article>
        );
      })}
    </section>
  );
}

function isHandoffActionable(handoff?: AgentActionHandoff | null): boolean {
  return !handoff || handoff.status === "active" || handoff.status === "opened";
}

function handoffMessage(handoff: AgentActionHandoff): string {
  if (handoff.status === "expired") return "来自 Agent 建议，已过期 / 需要重新生成建议。";
  if (handoff.status === "stale") return "来自 Agent 建议，已失效 / 需要重新生成建议。";
  if (handoff.status === "blocked") return "来自 Agent 建议，已阻断 / 需要重新生成建议。";
  if (handoff.status === "used_for_user_confirmed_action") return "来自 Agent 建议，已使用。";
  if (handoff.status === "dismissed") return "来自 Agent 建议，已忽略。";
  if (handoff.status === "opened") return "来自 Agent 建议，已打开，等待用户确认后响应审批。";
  return "来自 Agent 建议，等待用户确认后响应审批。";
}
