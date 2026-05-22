import type { AgentActionHandoff, WorkflowPatchDiff, WorkflowPatchProposal } from "../api/types.js";
import { safeText } from "../api/redaction.js";
import { useState } from "react";

export interface WorkflowEditingPanelProps {
  proposal: WorkflowPatchProposal;
  diff: WorkflowPatchDiff;
  highRiskDiff?: WorkflowPatchDiff;
  onApplyPatch?: (patchId: string, handoff?: AgentActionHandoff | null) => Promise<void> | void;
  onRejectPatch?: (patchId: string, reason?: string, handoff?: AgentActionHandoff | null) => Promise<void> | void;
  onPublishVersion?: (version: string, expectedDraftRevision: number, handoff?: AgentActionHandoff | null) => Promise<void> | void;
  handoff?: AgentActionHandoff | null;
}

export function WorkflowEditingPanel(props: WorkflowEditingPanelProps) {
  const risks = props.diff.risk_flags.length ? props.diff.risk_flags.join(", ") : "无";
  const [version, setVersion] = useState("2.0.0");
  const [busy, setBusy] = useState<"apply" | "reject" | "publish" | null>(null);
  const [message, setMessage] = useState("");
  const isApplied = props.proposal.status === "applied";
  const isRejected = props.proposal.status === "rejected";
  const isStale = props.proposal.status === "stale" || Boolean(props.proposal.stale_reason);
  const isBlocked = props.proposal.status === "blocked" || props.proposal.status === "conflicted";
  const handoffActionable = isHandoffActionable(props.handoff);
  const canApply = Boolean(props.onApplyPatch) && !props.diff.requires_approval && !isRejected && !isStale && !isBlocked && handoffActionable;
  const canReject = Boolean(props.onRejectPatch) && !isApplied && handoffActionable;
  const publishRevision = props.proposal.status === "applied"
    ? props.proposal.risk_flags?.length
      ? undefined
      : props.diff.base_revision + 1
    : undefined;

  async function runAction(kind: "apply" | "reject" | "publish") {
    setBusy(kind);
    setMessage("");
    try {
      if (kind === "apply") {
        await props.onApplyPatch?.(props.proposal.workflow_patch_id, props.handoff);
        setMessage("Patch 已应用到草稿，正在刷新版本和看板。");
      }
      if (kind === "reject") {
        await props.onRejectPatch?.(props.proposal.workflow_patch_id, "user rejected from editing panel", props.handoff);
        setMessage("Patch 已拒绝，正在刷新状态。");
      }
      if (kind === "publish" && publishRevision) {
        await props.onPublishVersion?.(version, publishRevision, props.handoff);
        setMessage("新版本已发布，正在刷新版本列表。");
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "编辑操作失败");
    } finally {
      setBusy(null);
    }
  }

  return (
    <section className="panel editing-panel" data-testid="editing-panel">
      <h2>工作流编辑</h2>
      <p className="muted">编辑只通过 BFF patch 路径写入 draft，不直接修改已发布版本。</p>
      {props.handoff ? <p className="handoff-banner" data-testid="agent-handoff-banner">{handoffMessage(props.handoff)}</p> : null}
      <div className="diff-card">
        <div>
          <strong>Patch</strong>
          <span className="status" data-testid="patch-status">{props.proposal.status}</span>
        </div>
        {isStale || isBlocked ? (
          <p className="operation-message" data-testid="patch-stale-warning">
            {props.proposal.conflict_reason || props.proposal.stale_reason || "该 Patch 已失效，需要刷新后重新生成。"}
          </p>
        ) : null}
        <p>{props.proposal.operation}</p>
        <dl>
          <dt>修改前</dt>
          <dd>{safeText(props.diff.before_summary)}</dd>
          <dt>修改后</dt>
          <dd>{safeText(props.diff.after_summary)}</dd>
          <dt>风险</dt>
          <dd>{risks}</dd>
          <dt>审批建议</dt>
          <dd>{props.diff.requires_approval ? "需要治理审批，当前不能直接应用" : "无需治理审批，可由用户确认后应用到草稿"}</dd>
        </dl>
        <div className="button-row">
          <button type="button">查看 Diff</button>
          <button
            data-testid="patch-apply-button"
            disabled={!canApply || busy !== null}
            type="button"
            onClick={() => {
              if (window.confirm("确认将该 Patch 应用到草稿？")) {
                void runAction("apply");
              }
            }}
          >
            {busy === "apply" ? "应用中…" : "应用到草稿"}
          </button>
          <button
            data-testid="patch-reject-button"
            disabled={!canReject || busy !== null}
            type="button"
            onClick={() => {
              if (window.confirm("确认拒绝该 Patch？")) {
                void runAction("reject");
              }
            }}
          >
            {busy === "reject" ? "拒绝中…" : "拒绝变更"}
          </button>
        </div>
        <div className="publish-row">
          <label>
            发布版本
            <input
              data-testid="publish-version-input"
              value={version}
              onChange={(event) => setVersion(event.currentTarget.value)}
              placeholder="2.0.0"
            />
          </label>
          <button
            data-testid="publish-version-button"
            disabled={!props.onPublishVersion || !isApplied || !publishRevision || busy !== null}
            type="button"
            onClick={() => {
              if (window.confirm("确认基于当前草稿发布新版本？")) {
                void runAction("publish");
              }
            }}
          >
            {busy === "publish" ? "发布中…" : "发布新版本"}
          </button>
        </div>
        {message ? <p className="operation-message" data-testid="editing-operation-message">{safeText(message)}</p> : null}
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

function isHandoffActionable(handoff?: AgentActionHandoff | null): boolean {
  return !handoff || handoff.status === "active" || handoff.status === "opened";
}

function handoffMessage(handoff: AgentActionHandoff): string {
  if (handoff.status === "expired") return "来自 Agent 建议，已过期 / 需要重新生成建议。";
  if (handoff.status === "stale") return "来自 Agent 建议，已失效 / 需要重新生成建议。";
  if (handoff.status === "blocked") return "来自 Agent 建议，已阻断 / 需要重新生成建议。";
  if (handoff.status === "used_for_user_confirmed_action") return "来自 Agent 建议，已使用。";
  if (handoff.status === "dismissed") return "来自 Agent 建议，已忽略。";
  if (handoff.status === "opened") return "来自 Agent 建议，已打开，等待用户确认后执行。";
  return "来自 Agent 建议，等待用户确认后执行。";
}
