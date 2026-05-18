import type { AgentTalkContextSummary } from "../api/agentTalkTypes.js";
import { safeText } from "../api/redaction.js";

export interface AgentContextSummaryProps {
  context: AgentTalkContextSummary;
}

export function AgentContextSummary({ context }: AgentContextSummaryProps) {
  return (
    <section className="agent-section">
      <h3>上下文摘要</h3>
      <p className="muted">仅展示 context.business 的脱敏摘要。</p>
      <pre>{safeText(context.business)}</pre>
    </section>
  );
}
