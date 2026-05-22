import assert from "node:assert/strict";
import test from "node:test";
import { renderToStaticMarkup } from "react-dom/server";
import type { AgentActionHandoff } from "../api/types.js";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";
import { ApprovalPanel } from "../components/ApprovalPanel.js";
import { ContextPanel } from "../components/ContextPanel.js";
import { WorkflowEditingPanel } from "../components/WorkflowEditingPanel.js";
import { demoPatchDiff, demoPatchProposal } from "../api/demoData.js";

function handoff(status: AgentActionHandoff["status"], inactiveReason?: string): AgentActionHandoff {
  return {
    handoff_id: `aah_${status}`,
    proposal_id: "aap_1",
    workflow_instance_id: "wfi_1",
    workflow_template_id: "wf_1",
    target_panel: "editing_panel",
    target_resource: { workflow_patch_id: "wfp_1" },
    suggested_form_prefill: { value: "建议文本" },
    expires_at: "2099-01-01T00:00:00Z",
    status,
    inactive_reason: inactiveReason,
    created_at: "2026-05-21T00:00:00Z",
    created_by: "agent",
    redaction_status: "redacted",
  };
}

test("operation panels show terminal handoff status and disable confirmation", () => {
  const expired = handoff("expired", "handoff_expired");
  const editing = renderToStaticMarkup(<WorkflowEditingPanel proposal={demoPatchProposal} diff={demoPatchDiff} handoff={expired} />);
  const approval = renderToStaticMarkup(
    <ApprovalPanel approvals={[{ approval_id: "ap_1", status: "pending", active: true }]} handoff={{ ...expired, target_panel: "approval_panel" }} />,
  );
  const context = renderToStaticMarkup(
    <ContextPanel context={{ workflow_instance_id: "wfi_1", revision: 1, business: {} }} handoff={{ ...expired, target_panel: "context_panel" }} />,
  );
  assert(editing.includes("已过期"));
  assert(approval.includes("已过期"));
  assert(context.includes("已过期"));
  assert(editing.includes("disabled"));
  assert(approval.includes("disabled"));
  assert(context.includes("disabled"));
});

test("Agent handoff client exposes lifecycle and audit routes", async () => {
  const calls: Array<{ url: string; method: string }> = [];
  const client = new WorkflowConsoleClient("/bff");
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ url: String(input).replace("/bff", ""), method: init?.method || "GET" });
    return new Response(JSON.stringify([]), { status: 200, headers: { "content-type": "application/json" } });
  }) as typeof fetch;
  try {
    await client.listAgentActionHandoffs("wfi_1");
    await client.listAgentActionHandoffAudit("wfi_1", "aah_1");
    await client.dismissAgentActionHandoff("wfi_1", "aah_1");
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.deepEqual(calls, [
    { method: "GET", url: "/instances/wfi_1/agent/action-handoffs" },
    { method: "GET", url: "/instances/wfi_1/agent/action-handoffs/aah_1/audit" },
    { method: "POST", url: "/instances/wfi_1/agent/action-handoffs/aah_1/dismiss" },
  ]);
});

