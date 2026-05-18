import type { WorkflowPatchDiff, WorkflowPatchProposal } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface WorkflowEditingPanelProps {
  proposal: WorkflowPatchProposal;
  diff: WorkflowPatchDiff;
  highRiskDiff?: WorkflowPatchDiff;
}

export function WorkflowEditingPanel(props: WorkflowEditingPanelProps) {
  const risks = props.diff.risk_flags.length ? props.diff.risk_flags.join(", ") : "无";

  return (
    <section className="panel editing-panel">
      <h2>工作流编辑</h2>
      <p className="muted">编辑只通过 BFF patch 路径写入 draft，不直接修改已发布版本。</p>
      <div className="diff-card">
        <div>
          <strong>Patch</strong>
          <span className="status">{props.proposal.status}</span>
        </div>
        <p>{props.proposal.operation}</p>
        <dl>
          <dt>修改前</dt>
          <dd>{safeText(props.diff.before_summary)}</dd>
          <dt>修改后</dt>
          <dd>{safeText(props.diff.after_summary)}</dd>
          <dt>风险</dt>
          <dd>{risks}</dd>
        </dl>
        <div className="button-row">
          <button type="button">查看 Diff</button>
          <button type="button">等待用户确认</button>
          <button type="button">前往编辑面板</button>
        </div>
      </div>
      {props.highRiskDiff ? (
        <div className="risk-card">
          <h3>高风险变更</h3>
          <p>{safeText(props.highRiskDiff.after_summary)}</p>
          <p>风险：{props.highRiskDiff.risk_flags.join(", ")}</p>
          <p className="muted">需要治理审批，当前控制台不会直接应用此类变更。</p>
          <button type="button" disabled>
            等待治理确认
          </button>
        </div>
      ) : null}
    </section>
  );
}
