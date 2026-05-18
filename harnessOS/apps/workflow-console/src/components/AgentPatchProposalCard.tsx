import type { WorkflowPatchDiff, WorkflowPatchProposal } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface AgentPatchProposalCardProps {
  proposal: WorkflowPatchProposal;
  diff: WorkflowPatchDiff;
}

export function AgentPatchProposalCard({ proposal, diff }: AgentPatchProposalCardProps) {
  return (
    <section className="agent-section">
      <h3>Patch 建议</h3>
      <p className="muted">Agent 只能生成建议和展示 Diff，不能直接应用或发布。</p>
      <div className="diff-card">
        <div>
          <strong>{proposal.operation}</strong>
          <span className="status">{proposal.status}</span>
        </div>
        <dl>
          <dt>修改前</dt>
          <dd>{safeText(diff.before_summary)}</dd>
          <dt>修改后</dt>
          <dd>{safeText(diff.after_summary)}</dd>
          <dt>风险</dt>
          <dd>{diff.risk_flags.length ? diff.risk_flags.join(", ") : "无"}</dd>
        </dl>
        <div className="button-row">
          <button type="button">生成建议</button>
          <button type="button">查看 Diff</button>
          <button type="button">前往编辑面板</button>
        </div>
      </div>
    </section>
  );
}
