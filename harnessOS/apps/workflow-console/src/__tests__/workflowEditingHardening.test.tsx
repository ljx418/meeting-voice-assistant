import assert from "node:assert/strict";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";
import { WorkflowEditingPanel } from "../components/WorkflowEditingPanel.js";
import type { WorkflowPatchDiff, WorkflowPatchProposal } from "../api/types.js";

const proposal: WorkflowPatchProposal = {
  workflow_patch_id: "wfp_editing",
  workflow_template_id: "wf_editing",
  workflow_draft_id: "wfd_editing",
  operation: "update_station_prompt",
  status: "proposed",
  requires_approval: false,
  risk_flags: [],
};

const diff: WorkflowPatchDiff = {
  workflow_patch_id: "wfp_editing",
  workflow_draft_id: "wfd_editing",
  base_revision: 2,
  operation: "update_station_prompt",
  target: { type: "station", station_id: "station_b" },
  before_summary: "旧提示词",
  after_summary: "新提示词",
  risk_flags: [],
  requires_approval: false,
  redacted: true,
};

test("editing client uses structured BFF routes for governed writes", async () => {
  const calls: Array<{ url: string; body?: string }> = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ url: String(input), body: typeof init?.body === "string" ? init.body : undefined });
    return new Response(JSON.stringify({ operation: "ok", status: "ok", resource: {} }), { status: 200 });
  }) as typeof fetch;
  try {
    const client = new WorkflowConsoleClient("/bff");
    await client.listInstancePatches("wfi_1");
    await client.applyPatch("wf_1", "wfp_1", { workflow_instance_id: "wfi_1", user_confirmed: true, source: "editing_panel" });
    await client.rejectPatch("wf_1", "wfp_1", { workflow_instance_id: "wfi_1", user_confirmed: true, source: "editing_panel" });
    await client.publishWorkflow("wf_1", { version: "2.0.0", expected_draft_revision: 3, user_confirmed: true, source: "editing_panel" });
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.deepEqual(calls.map((call) => call.url), [
    "/bff/instances/wfi_1/patches",
    "/bff/workflows/wf_1/patches/wfp_1/apply",
    "/bff/workflows/wf_1/patches/wfp_1/reject",
    "/bff/workflows/wf_1/publish",
  ]);
  assert(calls.slice(1).every((call) => call.body?.includes('"user_confirmed":true')));
  assert(calls.slice(1).every((call) => call.body?.includes('"source":"editing_panel"')));
  assert(calls.every((call) => !call.url.includes("/v1/rpc")));
  assert(calls.every((call) => !call.url.includes("/v1/events/subscribe")));
});

test("editing panel exposes apply reject publish only as user-confirmed actions", () => {
  const html = renderToStaticMarkup(
    <WorkflowEditingPanel
      proposal={proposal}
      diff={diff}
      onApplyPatch={() => undefined}
      onRejectPatch={() => undefined}
      onPublishVersion={() => undefined}
    />,
  );
  assert.match(html, /应用到草稿/);
  assert.match(html, /拒绝变更/);
  assert.match(html, /发布新版本/);
  assert.match(html, /无需治理审批/);
  for (const forbidden of ["自动应用", "自动发布", "已帮你修改并发布", "capability_token", "raw_trace_payload"]) {
    assert(!html.includes(forbidden), `${forbidden} leaked in editing panel`);
  }
});

test("high risk patch renders disabled apply state", () => {
  const risky = { ...diff, requires_approval: true, risk_flags: ["connector_change"] };
  const html = renderToStaticMarkup(<WorkflowEditingPanel proposal={{ ...proposal, requires_approval: true }} diff={risky} />);
  assert.match(html, /需要治理审批/);
  assert.match(html, /当前不能直接应用/);
  assert.match(html, /disabled=""/);
});
