import assert from "node:assert/strict";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { buildNodeAddIntent } from "../api/canvasPatchIntents.js";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";
import { ConsoleShell } from "../components/ConsoleShell.js";
import type { NodeCatalogItem, WorkflowBoard, WorkflowStatus } from "../api/types.js";

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

const board: WorkflowBoard = {
  workflow_instance: { workflow_instance_id: "wfi_1", workflow_template_id: "wf_1", workflow_version_id: "wfv_1", status: "running" },
  current_station_ids: ["station_a"],
  stations: [{ station: { station_id: "station_a", name: "A" }, status: "completed", runs: [] }],
};

const status: WorkflowStatus = { workflow_instance_id: "wfi_1", status: "running", current_station_ids: ["station_a"] };

test("node library renders BFF supplied catalog labels", () => {
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

  assert.match(html, /角色一致性检查/);
});

test("node add intent carries catalog version from BFF DTO", () => {
  const intent = buildNodeAddIntent(catalog[0], board.stations, "wfi_1");
  assert.equal(intent.payload.station.metadata.catalog_version, "2026-05-21");
  assert.equal(intent.payload.station.metadata.station_kind, "reviewer");
});

test("client fetches node catalog through BFF route", async () => {
  const calls: string[] = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL) => {
    calls.push(String(input));
    return new Response(JSON.stringify(catalog), { status: 200 });
  }) as typeof fetch;
  try {
    await new WorkflowConsoleClient("/bff").listNodeCatalog("wf_1");
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.equal(calls[0], "/bff/workflows/wf_1/node-catalog");
});
