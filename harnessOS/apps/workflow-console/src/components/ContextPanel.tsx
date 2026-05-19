import type { WorkflowContextSummary } from "../api/types.js";
import { safeText } from "../api/redaction.js";

export interface ContextPanelProps {
  context?: WorkflowContextSummary;
  onSetBusinessValue?: (path: `business.${string}`, value: string, expectedRevision: number) => void;
  onEmitBusinessEvent?: (eventType: `business.${string}`, payload: Record<string, unknown>) => void;
}

export function ContextPanel({ context, onSetBusinessValue, onEmitBusinessEvent }: ContextPanelProps) {
  const revision = context?.revision || 1;
  return (
    <section className="operation-panel" aria-label="上下文面板">
      <div className="panel-heading">
        <span className="eyebrow">Context</span>
        <h3>业务上下文</h3>
        <small>只允许写入 context.business</small>
      </div>
      <pre>{safeText(context?.business || {})}</pre>
      <div className="button-row">
        <button type="button" onClick={() => onSetBusinessValue?.("business.operator_note", "用户确认的业务备注", revision)}>
          写入 business.operator_note
        </button>
        <button type="button" onClick={() => onEmitBusinessEvent?.("business.workflow.note_submitted", { note: "用户提交上下文事件" })}>
          发送业务事件
        </button>
      </div>
    </section>
  );
}
