import { safeText } from "../api/redaction.js";

export interface AgentApprovalNoticeProps {
  approval: {
    approval_id: string;
    status: "pending" | "inactive";
    message: string;
  };
}

export function AgentApprovalNotice({ approval }: AgentApprovalNoticeProps) {
  return (
    <section className="agent-section">
      <h3>审批提醒</h3>
      <p>{safeText(approval.message)}</p>
      <div>
        <strong>{approval.approval_id}</strong> <span className="status">{approval.status}</span>
      </div>
      <p className="muted">等待用户确认。请前往审批面板处理。</p>
    </section>
  );
}
