import assert from "node:assert/strict";
import test from "node:test";
import { shouldRefreshForEvent } from "../hooks/useWorkflowConsoleData.js";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";

test("Agent event payloads trigger refresh but are not trusted as UI truth", () => {
  assert.equal(
    shouldRefreshForEvent({
      type: "agent.action_proposal.created",
      data: {
        selected_proposal_id: "fake_proposal",
        selected_patch_id: "fake_patch",
        evidence_id: "fake_evidence",
        raw_trace_payload: "secret-token-value",
      },
    }),
    true,
  );
  assert.equal(shouldRefreshForEvent({ type: "agent.fake.payload_only" }), false);
});

test("Agent refresh path pulls BFF DTOs after fake event instead of reading event payload", async () => {
  const calls: string[] = [];
  const client = new WorkflowConsoleClient("/bff");
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL) => {
    calls.push(String(input));
    return new Response(JSON.stringify([]), { status: 200, headers: { "content-type": "application/json" } });
  }) as typeof fetch;
  try {
    await client.getAgentInteractionState("wfi_1");
    await client.listAgentSuggestions("wfi_1");
    await client.listAgentActionProposals("wfi_1");
    await client.listAgentActionHandoffs("wfi_1");
    await client.listOperationEvidence("wfi_1");
    await client.getGovernanceReview("wfi_1");
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert(calls.includes("/bff/instances/wfi_1/agent/interaction-state"));
  assert(calls.includes("/bff/instances/wfi_1/agent/suggestions"));
  assert(calls.includes("/bff/instances/wfi_1/agent/action-proposals"));
  assert(calls.includes("/bff/instances/wfi_1/agent/action-handoffs"));
  assert(calls.includes("/bff/instances/wfi_1/agent/operation-evidence"));
  assert(calls.includes("/bff/instances/wfi_1/agent/governance-review"));
  assert(calls.every((call) => !call.includes("/v1/rpc")));
  assert(calls.every((call) => !call.includes("/v1/events/subscribe")));
});
