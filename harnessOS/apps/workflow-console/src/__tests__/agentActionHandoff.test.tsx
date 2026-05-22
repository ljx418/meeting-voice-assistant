import assert from "node:assert/strict";
import test from "node:test";
import { renderToStaticMarkup } from "react-dom/server";
import type { AgentActionHandoff, AgentActionProposal } from "../api/types.js";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";
import { AgentTalkShell } from "../components/AgentTalkShell.js";
import { WorkflowEditingPanel } from "../components/WorkflowEditingPanel.js";
import { ApprovalPanel } from "../components/ApprovalPanel.js";
import { ContextPanel } from "../components/ContextPanel.js";
import { demoPatchDiff, demoPatchProposal } from "../api/demoData.js";

const handoff: AgentActionHandoff = {
  handoff_id: "aah_1",
  proposal_id: "aap_1",
  workflow_instance_id: "wfi_1",
  workflow_template_id: "wf_1",
  target_panel: "editing_panel",
  target_resource: { workflow_patch_id: "wp_1" },
  suggested_form_prefill: { value: "请用户确认" },
  expires_at: "2099-01-01T00:00:00Z",
  status: "active",
  created_at: "2026-05-20T00:00:00Z",
  created_by: "agent",
  redaction_status: "redacted",
};

const proposal: AgentActionProposal = {
  proposal_id: "aap_1",
  agent_session_id: "ats_1",
  workflow_instance_id: "wfi_1",
  workflow_template_id: "wf_1",
  intent_type: "open_editing_panel",
  policy_class: "navigation",
  lifecycle: "proposed",
  status: "proposed",
  title: "前往编辑面板",
  summary: "把建议交给编辑面板，由用户确认。",
  target_panel: "editing",
  workflow_patch_id: "wp_1",
  risk_level: "low",
  risk_flags: [],
  requires_approval: false,
  policy_decision: "proposal_only",
  redaction_status: "redacted",
};

test("Agent handoff UI exposes panel navigation without execution buttons", () => {
  const html = renderToStaticMarkup(<AgentTalkShell actionProposals={[proposal]} events={[]} />);
  assert(html.includes("前往编辑面板"));
  for (const forbidden of ["Apply", "Publish", "Approve", "Reject", "Execute", "Run"]) {
    assert(!html.includes(forbidden), `${forbidden} appeared in Agent handoff UI`);
  }
});

test("operation panels render Agent handoff banner and still require user confirmation controls", () => {
  const editing = renderToStaticMarkup(<WorkflowEditingPanel proposal={demoPatchProposal} diff={demoPatchDiff} handoff={handoff} />);
  const approval = renderToStaticMarkup(
    <ApprovalPanel
      approvals={[{ approval_id: "ap_1", status: "pending", active: true, request_summary: "确认继续" }]}
      handoff={{ ...handoff, target_panel: "approval_panel" }}
    />,
  );
  const context = renderToStaticMarkup(
    <ContextPanel
      context={{ workflow_instance_id: "wfi_1", revision: 1, business: {} }}
      handoff={{ ...handoff, target_panel: "context_panel" }}
    />,
  );
  assert(editing.includes("来自 Agent 建议"));
  assert(approval.includes("来自 Agent 建议"));
  assert(context.includes("来自 Agent 建议"));
  assert(approval.includes("用户确认通过"));
  assert(context.includes("写入 business.operator_note"));
});

test("Agent handoff client uses structured BFF routes", async () => {
  const calls: Array<{ url: string; method: string; body?: string }> = [];
  const client = new WorkflowConsoleClient("/bff");
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ url: String(input).replace("/bff", ""), method: init?.method || "GET", body: String(init?.body || "") });
    return new Response(JSON.stringify(handoff), { status: 200, headers: { "content-type": "application/json" } });
  }) as typeof fetch;
  try {
    await client.createAgentActionHandoff("wfi_1", "aap_1", { target_panel: "editing_panel", workflow_patch_id: "wp_1" });
    await client.getAgentActionHandoff("wfi_1", "aah_1");
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.deepEqual(calls.map((call) => ({ method: call.method, url: call.url })), [
    { method: "POST", url: "/instances/wfi_1/agent/action-proposals/aap_1/handoff" },
    { method: "GET", url: "/instances/wfi_1/agent/action-handoffs/aah_1" },
  ]);
});
