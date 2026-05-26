import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import type { AgentActionProposal, AgentTalkInteractionState, AgentTalkSession } from "../api/types.js";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";
import { AgentTalkShell } from "../components/AgentTalkShell.js";

const session: AgentTalkSession = {
  agent_session_id: "ats_1",
  workflow_instance_id: "wfi_1",
  workflow_template_id: "wf_1",
  redaction_status: "redacted",
  messages: [],
  suggestions: [],
};

const interactionState: AgentTalkInteractionState = {
  workflow_instance_id: "wfi_1",
  workflow_template_id: "wf_1",
  agent_session_id: "ats_1",
  selected_suggestion_id: "ags_1",
  selected_proposal_id: "aap_1",
  selected_handoff_id: "aah_1",
  selected_patch_id: "wfp_1",
  selected_evidence_id: "evd_1",
  stale_reasons: ["selected_patch_stale"],
  refresh_generation: "agent_interaction:test",
  redaction_status: "redacted",
};

const proposal: AgentActionProposal = {
  proposal_id: "aap_1",
  agent_session_id: "ats_1",
  workflow_instance_id: "wfi_1",
  workflow_template_id: "wf_1",
  intent_type: "suggest_patch",
  policy_class: "proposal_only",
  lifecycle: "proposed",
  status: "proposed",
  title: "生成 Patch 建议",
  summary: "只创建 proposal，等待用户确认。",
  target_panel: "editing",
  workflow_patch_id: "wfp_1",
  risk_level: "low",
  risk_flags: [],
  requires_approval: false,
  policy_decision: "proposal_only",
  redaction_status: "redacted",
};

test("AgentTalk shell renders interaction state stale guard and evidence navigation", () => {
  const html = renderToStaticMarkup(
    <AgentTalkShell session={session} interactionState={interactionState} actionProposals={[proposal]} events={[]} />,
  );

  assert(html.includes("存在失效选择"));
  assert(html.includes("agent_interaction:test"));
  assert(html.includes("查看治理审计"));
  for (const forbidden of ["自动应用", "自动发布", "已帮你修改并发布", "Agent 已执行", "Agent 已发布"]) {
    assert(!html.includes(forbidden), `${forbidden} appeared in AgentTalk interaction UI`);
  }
});

test("Canvas Copilot renders proposal results inline and keeps terminal-style input behavior", () => {
  const html = renderToStaticMarkup(
    <AgentTalkShell session={session} interactionState={interactionState} actionProposals={[proposal]} events={[]} />,
  );
  const source = readFileSync("src/components/AgentTalkShell.tsx", "utf8");

  assert(html.includes("Canvas Copilot"));
  assert(html.includes("agent-proposal-result-message"));
  assert(html.includes("Proposal Result"));
  assert(html.includes("workflow.patch.propose"));
  assert(source.includes("function handleInputKeyDown"));
  assert(source.includes("event.key !== \"Enter\" || event.shiftKey"));
  assert(source.includes("event.preventDefault()"));
});

test("AgentTalk client exposes interaction state route without direct core calls", async () => {
  const calls: string[] = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL) => {
    calls.push(String(input));
    return new Response(JSON.stringify(interactionState), { status: 200, headers: { "content-type": "application/json" } });
  }) as typeof fetch;
  try {
    const client = new WorkflowConsoleClient("/bff");
    await client.getAgentInteractionState("wfi_1");
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.deepEqual(calls, ["/bff/instances/wfi_1/agent/interaction-state"]);
  assert(calls.every((call) => !call.includes("/v1/rpc")));
  assert(calls.every((call) => !call.includes("/v1/events/subscribe")));
});
