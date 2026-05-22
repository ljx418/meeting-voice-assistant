import assert from "node:assert/strict";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { buildNodeAddIntent } from "../api/canvasPatchIntents.js";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";
import { ConsoleShell } from "../components/ConsoleShell.js";
import { projectBoardForCanvas } from "../hooks/useWorkflowConsoleData.js";
import type { CanvasDraftProjection, NodeCatalogItem, WorkflowBoard, WorkflowStatus } from "../api/types.js";

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
  ],
};

const status: WorkflowStatus = {
  workflow_instance_id: "wfi_1",
  status: "running",
  current_station_ids: ["station_a"],
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

test("controlled catalog renders node library and builds governed descriptor metadata", () => {
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
  assert.match(html, /节点库/);
  assert.match(html, /角色一致性检查/);

  const item = catalog.find((candidate) => candidate.id === "character_consistency");
  assert(item);
  const intent = buildNodeAddIntent(item, board.stations, "wfi_1");
  assert.equal(intent.payload.station.metadata.catalog_id, "video.station.character_consistency");
  assert.equal(intent.payload.station.metadata.station_kind, "reviewer");
  assert.deepEqual(intent.payload.station.skill_refs, ["video.character_consistency"]);
});

test("canvas proposal request omits layout fields and uses BFF route only", async () => {
  const calls: Array<{ url: string; body?: string }> = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ url: String(input), body: typeof init?.body === "string" ? init.body : undefined });
    return new Response(
      JSON.stringify({ workflow_patch_id: "wfp_1", workflow_template_id: "wf_1", workflow_draft_id: "wfd_1", operation: "add_station", status: "proposed" }),
      { status: 200 },
    );
  }) as typeof fetch;
  try {
    const item = catalog.find((candidate) => candidate.id === "character_consistency");
    assert(item);
    await new WorkflowConsoleClient("/bff").proposePatch("wf_1", buildNodeAddIntent(item, board.stations, "wfi_1"));
  } finally {
    globalThis.fetch = originalFetch;
  }

  assert.equal(calls[0].url, "/bff/workflows/wf_1/patches");
  assert(!calls[0].url.includes("/v1/rpc"));
  assert(!calls[0].url.includes("/v1/events/subscribe"));
  for (const forbidden of ["position", "viewport", "zoom", "selectedNode", "panelCollapsed", "activeTab", "Authorization", "raw_trace_payload"]) {
    assert(!calls[0].body?.includes(forbidden), `${forbidden} leaked into proposal payload`);
  }
});

test("projection adds draft-only nodes without replacing runtime status truth", () => {
  const projection: CanvasDraftProjection = {
    projection_id: "projection_1",
    workflow_instance_id: "wfi_1",
    workflow_template_id: "wf_1",
    workflow_draft_id: "wfd_1",
    draft_revision: 2,
    generated_at: "2026-05-21T00:00:00Z",
    source_refs: {},
    nodes: [
      { station_id: "station_a", name: "用户输入", role: "input", skill_refs: [], connector_refs: [], run_count: 1 },
      { station_id: "station_new", name: "待确认节点", role: "reviewer", skill_refs: [], connector_refs: [], run_count: 0 },
    ],
    edges: [],
    runtime_summary: {},
    freshness_state: "fresh",
    stale_reasons: [],
    redaction_status: "redacted",
  };
  const projected = projectBoardForCanvas(board, projection);
  assert.equal(projected.stations.length, 2);
  assert.equal(projected.stations[0].status, "completed");
  assert.equal(projected.stations[1].status, "draft_only");
});

test("inspector copy requires explicit patch generation and exposes no automation claims", () => {
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
  assert.match(html, /节点配置/);
  for (const forbidden of ["自动应用", "自动发布", "已帮你修改并发布"]) {
    assert(!html.includes(forbidden), `${forbidden} leaked in console copy`);
  }
});
