import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { renderToStaticMarkup } from "react-dom/server";
import { test } from "node:test";
import { AgentTalkShell } from "../components/AgentTalkShell.js";
import type { AgentActionProposal, AgentTalkSession } from "../api/types.js";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";

const session: AgentTalkSession = {
  agent_session_id: "ats_1",
  workflow_instance_id: "wfi_1",
  workflow_template_id: "wf_1",
  redaction_status: "redacted",
  messages: [],
  suggestions: [],
};

const proposals: AgentActionProposal[] = [
  {
    proposal_id: "aap_1",
    agent_session_id: "ats_1",
    workflow_instance_id: "wfi_1",
    workflow_template_id: "wf_1",
    intent_type: "open_editing_panel",
    policy_class: "navigation",
    lifecycle: "proposed",
    status: "proposed",
    title: "前往编辑面板",
    summary: "用户进入编辑面板后再确认修改。",
    target_panel: "editing",
    risk_level: "low",
    risk_flags: [],
    requires_approval: false,
    policy_decision: "proposal_only",
    redaction_status: "redacted",
  },
  {
    proposal_id: "aap_2",
    agent_session_id: "ats_1",
    workflow_instance_id: "wfi_1",
    workflow_template_id: "wf_1",
    intent_type: "show_patch_diff",
    policy_class: "display_only",
    lifecycle: "proposed",
    status: "proposed",
    title: "查看 Diff",
    summary: "只展示差异，不应用。",
    target_panel: "editing",
    workflow_patch_id: "wfp_1",
    risk_level: "medium",
    risk_flags: ["prompt_change"],
    requires_approval: false,
    policy_decision: "proposal_only",
    redaction_status: "redacted",
  },
];

test("Agent action proposal queue exposes non-executable controls only", () => {
  const html = renderToStaticMarkup(<AgentTalkShell session={session} actionProposals={proposals} events={[]} />);
  assert(html.includes("agent-action-proposal-queue"));
  assert(html.includes("查看详情"));
  assert(html.includes("查看 Diff"));
  assert(html.includes("前往编辑面板"));
  assert(!html.includes("Apply"));
  assert(!html.includes("Publish"));
  assert(!html.includes("Approve"));
  assert(!html.includes("Reject"));
  for (const forbidden of ["自动应用", "自动发布", "已帮你修改并发布"]) {
    assert(!html.includes(forbidden), `${forbidden} appeared in Agent action proposal queue`);
  }
});

test("AgentTalk visible controls have local feedback or navigation handlers", () => {
  const source = readFileSync("src/components/AgentTalkShell.tsx", "utf8");

  assert(source.includes("function applyQuickPrompt"));
  assert(source.includes("function requestSuggestion"));
  assert(source.includes("data-testid=\"agent-action-proposal-detail\""));
  assert(!source.includes('<button type="button">生成建议</button>'));
  assert(!source.includes('<button type="button">查看详情</button>'));
  assert(!source.includes('<button type="button" key={item}>{item}</button>'));
});

test("Agent action proposal client uses structured BFF routes", async () => {
  const calls: Array<{ url: string; method: string }> = [];
  const client = new WorkflowConsoleClient("/bff");
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === "string" ? input : input instanceof URL ? input.pathname : input.url;
    calls.push({ url: url.replace(/^\/bff/, ""), method: init?.method || "GET" });
    return new Response(JSON.stringify(proposals[0]), { status: 200, headers: { "content-type": "application/json" } });
  }) as typeof fetch;
  try {
    await client.listAgentActionProposals("wfi_1");
    await client.createAgentActionProposal("wfi_1", { intent_type: "open_editing_panel" });
    await client.dismissAgentActionProposal("wfi_1", "aap_1");
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.deepEqual(calls, [
    { method: "GET", url: "/instances/wfi_1/agent/action-proposals" },
    { method: "POST", url: "/instances/wfi_1/agent/action-proposals" },
    { method: "POST", url: "/instances/wfi_1/agent/action-proposals/aap_1/dismiss" },
  ]);
});
