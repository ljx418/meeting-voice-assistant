import type { AgentTalkFixture } from "../api/agentTalkTypes.js";
import { AgentApprovalNotice } from "./AgentApprovalNotice.js";
import { AgentContextSummary } from "./AgentContextSummary.js";
import { AgentEventTimeline } from "./AgentEventTimeline.js";
import { AgentPatchProposalCard } from "./AgentPatchProposalCard.js";

export interface AgentTalkShellProps {
  fixture: AgentTalkFixture;
}

export function AgentTalkShell({ fixture }: AgentTalkShellProps) {
  return (
    <section className="panel agent-talk-shell">
      <div>
        <h2>{fixture.title}</h2>
        <p className="muted">Preparation shell · demo fixture · not runtime E2E</p>
      </div>
      <div className="allowed-actions">
        {fixture.allowed_actions.map((action) => (
          <span className="status" key={action}>
            {action}
          </span>
        ))}
      </div>
      <AgentEventTimeline events={fixture.events} />
      <AgentPatchProposalCard proposal={fixture.patch_proposal} diff={fixture.patch_diff} />
      <AgentApprovalNotice approval={fixture.approval_notice} />
      <AgentContextSummary context={fixture.context_summary} />
    </section>
  );
}
