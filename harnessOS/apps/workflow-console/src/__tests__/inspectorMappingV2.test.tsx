import assert from "node:assert/strict";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { buildInspectorPromptIntent } from "../api/canvasPatchIntents.js";
import { ConsoleShell } from "../components/ConsoleShell.js";
import type { WorkflowBoard, WorkflowStatus } from "../api/types.js";

const board: WorkflowBoard = {
  workflow_instance: { workflow_instance_id: "wfi_1", workflow_template_id: "wf_1", workflow_version_id: "wfv_1", status: "running" },
  current_station_ids: ["station_b"],
  stations: [
    {
      station: { station_id: "station_b", name: "分镜生成", role: "storyboard" },
      status: "running",
      runs: [{ station_run_id: "sr_b", station_id: "station_b", status: "running", output_artifacts: [] }],
    },
  ],
};

const status: WorkflowStatus = { workflow_instance_id: "wfi_1", status: "running", current_station_ids: ["station_b"] };

test("console render exposes no inspector automation claims", () => {
  const html = renderToStaticMarkup(
    <ConsoleShell
      workflows={[{ workflow_template_id: "wf_1", name: "Workflow" }]}
      versions={[{ workflow_template_id: "wf_1", workflow_version_id: "wfv_1", version: "1.0.0" }]}
      instances={[{ workflow_template_id: "wf_1", workflow_version_id: "wfv_1", workflow_instance_id: "wfi_1", status: "running" }]}
      selectedWorkflowId="wf_1"
      selectedVersionId="wfv_1"
      selectedInstanceId="wfi_1"
      board={board}
      status={status}
      events={[]}
      onWorkflowChange={() => undefined}
      onVersionChange={() => undefined}
      onInstanceChange={() => undefined}
    />,
  );

  assert.match(html, /Agent 只负责建议/);
  for (const forbidden of ["自动应用", "自动发布", "已帮你修改并发布"]) {
    assert(!html.includes(forbidden));
  }
});

test("inspector prompt intent only contains allowlisted fields", () => {
  const intent = buildInspectorPromptIntent("station_b", "增强角色一致性", "wfi_1");
  assert.deepEqual(Object.keys(intent.payload).sort(), ["prompt_patch", "station_id"]);
});
