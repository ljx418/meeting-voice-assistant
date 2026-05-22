import assert from "node:assert/strict";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { AgentTalkShell } from "../components/AgentTalkShell.js";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";
import type { AgentTalkSession, AgentTalkSuggestion } from "../api/types.js";

const session: AgentTalkSession = {
  agent_session_id: "ats_1",
  workflow_instance_id: "wfi_1",
  workflow_template_id: "wf_1",
  redaction_status: "redacted",
  messages: [
    {
      message_id: "atm_1",
      agent_session_id: "ats_1",
      workflow_instance_id: "wfi_1",
      workflow_template_id: "wf_1",
      role: "user",
      source: "user",
      content: "帮我优化当前节点",
      redaction_status: "redacted",
    },
    {
      message_id: "atm_2",
      agent_session_id: "ats_1",
      workflow_instance_id: "wfi_1",
      workflow_template_id: "wf_1",
      role: "assistant",
      source: "assistant",
      content: "我只会生成建议和 Diff，等待用户确认。",
      redaction_status: "redacted",
    },
  ],
  suggestions: [],
};

const suggestions: AgentTalkSuggestion[] = [
  {
    suggestion_id: "ags_1",
    workflow_instance_id: "wfi_1",
    workflow_template_id: "wf_1",
    workflow_patch_id: "wfp_1",
    type: "show_diff",
    title: "查看 Diff",
    summary: "打开已有 Patch Diff；Agent 不会执行 Apply / Publish。",
    status: "active",
    action_intent: { action: "show_patch_diff", executable: false },
    risk_flags: [],
    requires_approval: false,
    redaction_status: "redacted",
  },
];

test("stateful AgentTalk shell renders non-executable suggestions only", () => {
  const html = renderToStaticMarkup(<AgentTalkShell session={session} suggestions={suggestions} events={[]} />);
  assert.match(html, /Agent 工作流助手/);
  assert.match(html, /帮我优化当前节点/);
  assert.match(html, /查看 Diff/);
  assert.match(html, /前往编辑面板/);
  assert(!html.includes("Apply Patch"));
  assert(!html.includes("Publish Version"));
  assert(!html.includes("Approve"));
  assert(!html.includes("Reject"));
  for (const forbidden of ["自动应用", "自动发布", "已帮你修改并发布", "capability_token", "raw_trace_payload"]) {
    assert(!html.includes(forbidden), `${forbidden} appeared in AgentTalk shell`);
  }
});

test("AgentTalk client uses structured BFF routes", async () => {
  const calls: Array<{ url: string; body?: string }> = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ url: String(input), body: typeof init?.body === "string" ? init.body : undefined });
    return new Response(JSON.stringify({ ...session, suggestions }), { status: 200, headers: { "content-type": "application/json" } });
  }) as typeof fetch;
  try {
    const client = new WorkflowConsoleClient("/bff");
    await client.getAgentSession("wfi_1");
    await client.sendAgentMessage("wfi_1", { content: "帮我优化当前节点" });
    await client.listAgentSuggestions("wfi_1");
    await client.dismissAgentSuggestion("wfi_1", "ags_1");
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.equal(calls[0].url, "/bff/instances/wfi_1/agent/session");
  assert.equal(calls[1].url, "/bff/instances/wfi_1/agent/messages");
  assert.equal(calls[2].url, "/bff/instances/wfi_1/agent/suggestions");
  assert.equal(calls[3].url, "/bff/instances/wfi_1/agent/suggestions/ags_1/dismiss");
  assert(!calls.some((call) => call.url.includes("/v1/rpc")));
});
