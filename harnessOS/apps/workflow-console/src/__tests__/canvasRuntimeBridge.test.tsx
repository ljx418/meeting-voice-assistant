import assert from "node:assert/strict";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { buildEdgeAddIntent, buildInspectorPromptIntent, buildNodeAddIntent } from "../api/canvasPatchIntents.js";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";
import { ConsoleShell } from "../components/ConsoleShell.js";
import type { NodeCatalogItem, WorkflowBoard, WorkflowStatus } from "../api/types.js";

const board: WorkflowBoard = {
  workflow_instance: {
    workflow_instance_id: "wfi_1",
    workflow_template_id: "wf_1",
    workflow_version_id: "wfv_1",
    status: "running",
  },
  current_station_ids: ["station_a"],
  stations: [
    {
      station: { station_id: "station_a", name: "用户输入", role: "input" },
      status: "completed",
      runs: [{ station_run_id: "sr_a", station_id: "station_a", status: "completed", output_artifacts: [] }],
    },
    {
      station: { station_id: "station_b", name: "分镜生成", role: "storyboard" },
      status: "running",
      runs: [{ station_run_id: "sr_b", station_id: "station_b", status: "running", output_artifacts: [] }],
    },
  ],
};

const status: WorkflowStatus = {
  workflow_instance_id: "wfi_1",
  status: "running",
  current_station_ids: ["station_b"],
};

const catalog: NodeCatalogItem[] = [
  {
    id: "character_consistency",
    label: "角色一致性检查",
    catalog_id: "video.station.character_consistency",
    catalog_version: "2026-05-21",
    node_template_id: "character_consistency",
    station_kind: "reviewer",
    schema_version: "v4.0-n",
    allowed_skill_refs: ["video.character_consistency"],
    allowed_connector_refs: [],
    allowed_artifact_kinds: ["dummy.beta", "dummy.final", "storyboard"],
    allowed_quality_rules: ["visual_consistency"],
    allowed_approval_policies: [],
  },
];

test("canvas bridge intent builders create patch proposal payloads without layout fields", () => {
  const item = catalog.find((candidate) => candidate.id === "character_consistency");
  assert(item);
  const nodeIntent = buildNodeAddIntent(item, board.stations, "wfi_1");
  const edgeIntent = buildEdgeAddIntent("station_a", "station_b", "wfi_1");
  const inspectorIntent = buildInspectorPromptIntent("station_b", "增强角色一致性", "wfi_1");

  assert.equal(nodeIntent.operation, "add_station");
  assert.equal(nodeIntent.payload.station.metadata.node_catalog_id, "character_consistency");
  assert.equal(edgeIntent.operation, "update_edge");
  assert.equal(edgeIntent.payload.edge_patch.action, "add");
  assert.equal(inspectorIntent.operation, "update_station_prompt");
  const serialized = JSON.stringify({ nodeIntent, edgeIntent, inspectorIntent });
  for (const forbidden of ["position", "zoom", "selection", "viewport", "capability_token", "raw_trace_payload"]) {
    assert(!serialized.includes(forbidden), `${forbidden} leaked into intent payload`);
  }
});

test("canvas bridge client posts proposal through unified BFF route", async () => {
  const calls: Array<{ url: string; body?: string }> = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ url: String(input), body: typeof init?.body === "string" ? init.body : undefined });
    return new Response(JSON.stringify({ workflow_patch_id: "wfp_1", workflow_template_id: "wf_1", workflow_draft_id: "wfd_1", operation: "add_station", status: "proposed" }), { status: 200 });
  }) as typeof fetch;
  try {
    const client = new WorkflowConsoleClient("/bff");
    const item = catalog[0];
    await client.proposePatch("wf_1", buildNodeAddIntent(item, board.stations, "wfi_1"));
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.equal(calls[0].url, "/bff/workflows/wf_1/patches");
  assert(calls[0].body?.includes('"intent_type":"node_add"'));
  assert(!calls[0].body?.includes('"user_confirmed"'));
});

test("console renders canvas bridge controls without apply or publish automation copy", () => {
  const html = renderToStaticMarkup(
    <ConsoleShell
      workflows={[{ workflow_template_id: "wf_1", name: "Workflow" }]}
      versions={[{ workflow_template_id: "wf_1", workflow_version_id: "wfv_1", version: "1.0.0" }]}
      instances={[{ workflow_template_id: "wf_1", workflow_version_id: "wfv_1", workflow_instance_id: "wfi_1", status: "running" }]}
      selectedWorkflowId="wf_1"
      selectedVersionId="wfv_1"
      selectedInstanceId="wfi_1"
      board={board}
      nodeCatalog={catalog}
      status={status}
      events={[]}
      onWorkflowChange={() => undefined}
      onVersionChange={() => undefined}
      onInstanceChange={() => undefined}
    />,
  );
  assert.match(html, /生成连线 Patch/);
  assert.match(html, /拖拽节点到画布/);
  for (const forbidden of ["自动应用", "自动发布", "已帮你修改并发布", "capability_token", "raw_artifact_content"]) {
    assert(!html.includes(forbidden), `${forbidden} leaked in canvas bridge shell`);
  }
});
