import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";
import { shouldRefreshForEvent } from "../hooks/useWorkflowConsoleData.js";

interface ExecutorDesignGateContract {
  runtime_enabled: boolean;
  callable_executor_routes_enabled: boolean;
  policy_matrix: Array<{
    action: string;
    classification: string;
    q_stage_callable_by_executor: boolean;
    future_executor_eligible: boolean;
  }>;
  capability_profile: Array<{ capability: string; active_in_q: boolean; can_mutate_runtime: boolean }>;
  event_truth: { eventbridge_payload_can_construct_truth: boolean };
}

function loadContract(): ExecutorDesignGateContract {
  return JSON.parse(readFileSync("../../docs/design/V4.0/v4_0_q_controlled_executor_design_gate_contract.json", "utf8")) as ExecutorDesignGateContract;
}

test("executor design gate contract keeps executor inactive", () => {
  const contract = loadContract();
  assert.equal(contract.runtime_enabled, false);
  assert.equal(contract.callable_executor_routes_enabled, false);

  const executorCapabilities = contract.capability_profile.filter((item) => item.capability.startsWith("executor."));
  assert(executorCapabilities.length >= 4);
  for (const capability of executorCapabilities) {
    assert.equal(capability.active_in_q, false, capability.capability);
    assert.equal(capability.can_mutate_runtime, false, capability.capability);
  }
});

test("executor policy matrix blocks Q-stage executor calls", () => {
  const contract = loadContract();
  const byAction = new Map(contract.policy_matrix.map((item) => [item.action, item]));
  assert.equal(byAction.get("connector.call")?.classification, "never_executor");
  assert.equal(byAction.get("external_llm.call")?.classification, "never_executor");
  for (const item of contract.policy_matrix) {
    assert.equal(item.q_stage_callable_by_executor, false, item.action);
    if (item.classification === "never_executor") {
      assert.equal(item.future_executor_eligible, false, item.action);
    }
  }
});

test("frontend client exposes no executor route or direct v1 executor path", async () => {
  const calls: string[] = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL) => {
    calls.push(String(input));
    return new Response(JSON.stringify([]), { status: 200, headers: { "content-type": "application/json" } });
  }) as typeof fetch;
  try {
    const client = new WorkflowConsoleClient("/bff");
    await client.listWorkflows();
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.deepEqual(calls, ["/bff/workflows"]);
  for (const call of calls) {
    assert(!call.includes("/execute"));
    assert(!call.includes("/agent/execute"));
    assert(!call.includes("/v1/rpc"));
    assert(!call.includes("/v1/events/subscribe"));
  }
});

test("fake executor event payload does not become refresh truth", () => {
  assert.equal(
    shouldRefreshForEvent({
      type: "executor.completed",
      data: { executor_truth: { status: "published" }, patch_status: "applied" },
    }),
    false,
  );
  assert.equal(loadContract().event_truth.eventbridge_payload_can_construct_truth, false);
});
