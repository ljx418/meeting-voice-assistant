import assert from "node:assert/strict";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ConsoleShell } from "../components/ConsoleShell.js";
import type { WorkflowBoard } from "../api/types.js";

const realBoard: WorkflowBoard = {
  workflow_instance: {
    workflow_instance_id: "wfi_real",
    workflow_template_id: "wf_real",
    workflow_version_id: "wfv_real",
    status: "running",
  },
  stations: [
    {
      station: { station_id: "station_storyboard", name: "分镜生成 Agent", role: "storyboard_agent" },
      runs: [
        {
          station_run_id: "sr_real",
          station_id: "station_storyboard",
          status: "completed",
          output_artifacts: [
            {
              artifact_id: "art_real",
              name: "storyboard_v1.json",
              metadata: {
                raw_artifact_content: "raw-bytes",
                capability_token: "cap-token",
              },
            },
          ],
          trace_summary: { summary: "Authorization: Bearer secret" },
        },
      ],
      status: "completed",
      output_artifacts: [{ artifact_id: "art_real", name: "storyboard_v1.json" }],
      trace_summary: { summary: "raw_trace_payload" },
    },
  ],
  current_station_ids: ["station_storyboard"],
  artifacts: [
    {
      artifact_id: "art_real",
      name: "storyboard_v1.json",
      metadata: {
        subscription_token: "sub-token",
        raw_connector_payload: "raw-connector",
      },
    },
  ],
  trace_summary: { summary: "raw_trace_payload" },
};

test("ConsoleShell renders BFF-style real board DTO without leaking secrets", () => {
  const html = renderToStaticMarkup(
    <ConsoleShell
      workflows={[{ workflow_template_id: "wf_real", name: "真实工作流", latest_version_id: "wfv_real" }]}
      versions={[{ workflow_template_id: "wf_real", workflow_version_id: "wfv_real", version: "1.0.0" }]}
      instances={[{ workflow_template_id: "wf_real", workflow_version_id: "wfv_real", workflow_instance_id: "wfi_real", status: "running" }]}
      selectedWorkflowId="wf_real"
      selectedVersionId="wfv_real"
      selectedInstanceId="wfi_real"
      board={realBoard}
      status={{ workflow_instance_id: "wfi_real", status: "running", current_station_ids: ["station_storyboard"] }}
      events={[{ type: "artifact.registered", source: "live", data: { Authorization: "Bearer secret" } }]}
      eventState="connected"
      onWorkflowChange={() => undefined}
      onVersionChange={() => undefined}
      onInstanceChange={() => undefined}
    />,
  );
  assert.match(html, /真实工作流/);
  assert.match(html, /技术分享资料递归总结工作流/);
  assert.match(html, /文件夹输入/);
  assert.match(html, /事件连接：connected/);
  for (const forbidden of ["cap-token", "sub-token", "Bearer secret", "raw_trace_payload", "raw_artifact_content", "raw_connector_payload"]) {
    assert(!html.includes(forbidden), `${forbidden} leaked in real bridge render`);
  }
});
