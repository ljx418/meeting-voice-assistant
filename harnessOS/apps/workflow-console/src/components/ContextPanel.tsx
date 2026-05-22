import type { AgentActionHandoff, WorkflowContextSummary } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface ContextPanelProps {
  context?: WorkflowContextSummary;
  handoff?: AgentActionHandoff | null;
  onSetBusinessValue?: (path: `business.${string}`, value: string, expectedRevision: number, handoff?: AgentActionHandoff | null) => void;
  onEmitBusinessEvent?: (eventType: `business.${string}`, payload: Record<string, unknown>, binding?: undefined, handoff?: AgentActionHandoff | null) => void;
}

export function ContextPanel({ context, handoff, onSetBusinessValue, onEmitBusinessEvent }: ContextPanelProps) {
  const revision = context?.revision || 1;
  const prefill = handoff?.suggested_form_prefill?.value;
  const note = typeof prefill === "string" ? prefill : "用户确认的业务备注";
  const disabled = !isHandoffActionable(handoff);
  return (
    <section className="operation-panel" aria-label="上下文面板" data-testid="context-panel">
      <div className="panel-heading">
        <span className="eyebrow">Context</span>
        <h3>业务上下文</h3>
        <small>只允许写入 context.business</small>
      </div>
      {handoff ? <p className="handoff-banner" data-testid="agent-handoff-banner">{handoffMessage(handoff)}</p> : null}
      <pre>{safeText(context?.business || {})}</pre>
      <div className="button-row">
        <button
          data-testid="context-update-button"
          disabled={disabled}
          type="button"
          onClick={() => onSetBusinessValue?.("business.operator_note", note, revision, handoff)}
        >
          写入 business.operator_note
        </button>
        <button disabled={disabled} type="button" onClick={() => onEmitBusinessEvent?.("business.workflow.note_submitted", { note }, undefined, handoff)}>
          发送业务事件
        </button>
      </div>
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
  if (handoff.status === "opened") return "来自 Agent 建议，已打开，等待用户确认后写入业务上下文。";
  return "来自 Agent 建议，等待用户确认后写入业务上下文。";
}
