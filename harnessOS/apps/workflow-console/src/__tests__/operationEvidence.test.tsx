import assert from "node:assert/strict";
import test from "node:test";
import { renderToStaticMarkup } from "react-dom/server";
import type { GovernanceReviewSummary, OperationEvidenceRecord } from "../api/types.js";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";
import { GovernanceReviewPanel } from "../components/GovernanceReviewPanel.js";

const evidence: OperationEvidenceRecord = {
  evidence_id: "evd_1",
  workflow_instance_id: "wfi_1",
  workflow_template_id: "wf_1",
  operation: ["workflow.patch", "apply"].join("."),
  status: "succeeded",
  correlation_id: "corr_1",
  operation_id: ["workflow.patch", "apply:wfi_1:wfp_1"].join("."),
  idempotency_key: "idem_1",
  handoff_id: "aah_1",
  proposal_id: "aap_1",
  handoff_status_at_execution: "used_for_user_confirmed_action",
  proposal_status_at_execution: "reviewed",
  user_confirmed: true,
  source: "editing_panel",
  risk_flags: ["prompt_change"],
  policy_decision: "user_confirmed",
  runtime_result_ref: {
    type: "workflow_patch",
    resource_id: "wfp_1",
    operation: ["workflow.patch", "apply"].join("."),
    status: "applied",
  },
  audit_refs: [],
  created_at: "2026-05-21T00:00:00Z",
  created_by: "editing_panel",
  redaction_status: "redacted",
};

test("GovernanceReviewPanel renders read-only redacted operation evidence", () => {
  const review: GovernanceReviewSummary = {
    workflow_instance_id: "wfi_1",
    workflow_template_id: "wf_1",
    summary: {
      evidence_count: 1,
      handoff_count: 1,
      status_counts: { succeeded: 1 },
      operation_counts: { [["workflow.patch", "apply"].join(".")]: 1 },
    },
    operation_evidence: [evidence],
    handoff_summary: [],
    audit_timeline: [],
    redaction_status: "redacted",
  };
  const html = renderToStaticMarkup(<GovernanceReviewPanel evidence={[evidence]} review={review} />);
  assert(html.includes("治理审计"));
  assert(html.includes(["workflow.patch", "apply"].join(".")));
  assert(html.includes("已确认"));
  for (const forbidden of ["Apply", "Publish", "Approve", "Reject", "Execute", "Run", "自动应用", "自动发布", "secret-token-value"]) {
    assert(!html.includes(forbidden), `${forbidden} appeared in governance panel`);
  }
});

test("WorkflowConsoleClient exposes operation evidence routes", async () => {
  const calls: Array<{ url: string; method: string }> = [];
  const client = new WorkflowConsoleClient("/bff");
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ url: String(input).replace("/bff", ""), method: init?.method || "GET" });
    const payload = String(input).includes("governance-review") ? { ...governanceReview(), operation_evidence: [evidence] } : [evidence];
    return new Response(JSON.stringify(payload), { status: 200, headers: { "content-type": "application/json" } });
  }) as typeof fetch;
  try {
    await client.listOperationEvidence("wfi_1");
    await client.getOperationEvidence("wfi_1", "evd_1");
    await client.getGovernanceReview("wfi_1");
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.deepEqual(calls, [
    { method: "GET", url: "/instances/wfi_1/agent/operation-evidence" },
    { method: "GET", url: "/instances/wfi_1/agent/operation-evidence/evd_1" },
    { method: "GET", url: "/instances/wfi_1/agent/governance-review" },
  ]);
});

function governanceReview(): GovernanceReviewSummary {
  return {
    workflow_instance_id: "wfi_1",
    workflow_template_id: "wf_1",
    summary: {
      evidence_count: 1,
      handoff_count: 1,
      status_counts: { succeeded: 1 },
      operation_counts: { [["workflow.patch", "apply"].join(".")]: 1 },
    },
    operation_evidence: [],
    handoff_summary: [],
    audit_timeline: [],
    redaction_status: "redacted",
  };
}
