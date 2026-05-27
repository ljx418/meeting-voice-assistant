import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ConsoleShell } from "../components/ConsoleShell.js";
import { loadWorkflowConsoleData, refreshWorkflowConsoleRuntimeState, shouldRefreshForEvent } from "../hooks/useWorkflowConsoleData.js";
import type { WorkflowBoard, WorkflowPatchDiff, WorkflowStatus } from "../api/types.js";

const board: WorkflowBoard = {
  workflow_instance: {
    workflow_instance_id: "wfi_reference",
    workflow_template_id: "wf_reference",
    workflow_version_id: "wfv_reference",
    status: "waiting_approval",
  },
  stations: [
    {
      station: { station_id: "station_a", name: "Collect Input" },
      runs: [{ station_run_id: "sr_a", station_id: "station_a", status: "completed", output_artifacts: [{ artifact_id: "art_a", name: "a.json" }] }],
      status: "completed",
      output_artifacts: [{ artifact_id: "art_a", name: "a.json" }],
    },
    {
      station: { station_id: "station_b", name: "Transform Input" },
      runs: [{ station_run_id: "sr_b", station_id: "station_b", status: "completed", output_artifacts: [{ artifact_id: "art_b", name: "b.json" }] }],
      status: "completed",
      output_artifacts: [{ artifact_id: "art_b", name: "b.json" }],
    },
    {
      station: { station_id: "station_c", name: "Human Gate" },
      runs: [{ station_run_id: "sr_c", station_id: "station_c", status: "waiting_approval", output_artifacts: [] }],
      status: "waiting_approval",
      approvals: [{ approval_id: "appr_reference", status: "pending", active: true }],
    },
  ],
  current_station_ids: ["station_c"],
  artifacts: [{ artifact_id: "art_b", name: "b.json" }],
  approvals: [{ approval_id: "appr_reference", status: "pending", active: true }],
  quality_evaluations: [{ evaluation_id: "qe_reference", status: "passed", score: 0.91 }],
  trace_summary: { summary: "redacted trace summary" },
};

const status: WorkflowStatus = {
  workflow_instance_id: "wfi_reference",
  status: "waiting_approval",
  current_station_ids: ["station_c"],
};

const completedStatus: WorkflowStatus = {
  workflow_instance_id: "wfi_reference",
  status: "completed",
  current_station_ids: [],
};

const patchDiff: WorkflowPatchDiff = {
  workflow_patch_id: "wfp_reference",
  workflow_draft_id: "wfd_reference",
  base_revision: 2,
  operation: "update_station_prompt",
  target: { type: "station", station_id: "station_b" },
  before_summary: "old prompt",
  after_summary: "new prompt",
  risk_flags: ["prompt_change"],
  requires_approval: true,
  redacted: true,
};

test("reference console E2E test source does not import demo fixture data", () => {
  const source = readFileSync(new URL("./referenceConsoleE2E.test.js", import.meta.url), "utf8");
  assert(!source.includes(`demo${"Data"}`));
});

test("reference console renders real BFF DTOs and seeded PatchDiffDTO", async () => {
  const client = {
    listWorkflows: async () => [{ workflow_template_id: "wf_reference", name: "Reference Workflow", latest_version_id: "wfv_reference" }],
    listWorkflowVersions: async () => [{ workflow_template_id: "wf_reference", workflow_version_id: "wfv_reference", version: "1.0.0" }],
    listInstances: async () => [{ workflow_template_id: "wf_reference", workflow_version_id: "wfv_reference", workflow_instance_id: "wfi_reference", status: "waiting_approval" }],
    getInstanceStatus: async () => status,
    getBoard: async () => board,
    listStationOutputs: async () => [{ artifact_id: "art_a", name: "a.json" }],
    listApprovals: async () => [{ approval_id: "appr_reference", status: "pending", active: true }],
    listQuality: async () => [{ evaluation_id: "qe_reference", status: "passed", score: 0.91 }],
    getContext: async () => ({ workflow_instance_id: "wfi_reference", revision: 3, business: { selected_scene: "scene_001" } }),
    getInstancePatchDiff: async () => patchDiff,
  };
  const loaded = await loadWorkflowConsoleData(client as never);
  const diff = await client.getInstancePatchDiff();
  const html = renderToStaticMarkup(
    <ConsoleShell
      workflows={loaded.workflows}
      versions={loaded.versions}
      instances={loaded.instances}
      selectedWorkflowId={loaded.selectedWorkflowId}
      selectedVersionId={loaded.selectedVersionId}
      selectedInstanceId={loaded.selectedInstanceId}
      board={loaded.board as WorkflowBoard}
      status={loaded.status as WorkflowStatus}
      approvals={loaded.approvals}
      quality={loaded.quality}
      context={loaded.context}
      events={[{ type: "business.event.received", source: "live", data: { status: "failed", raw_trace_payload: "secret" } }]}
      patchProposal={{
        workflow_patch_id: diff.workflow_patch_id,
        workflow_template_id: "wf_reference",
        workflow_draft_id: "wfd_reference",
        operation: diff.operation,
        status: "proposed",
        proposed_by: "agent_reference",
        requires_approval: diff.requires_approval,
        risk_flags: diff.risk_flags,
      }}
      patchDiff={diff}
      eventState="connected"
      onWorkflowChange={() => undefined}
      onVersionChange={() => undefined}
      onInstanceChange={() => undefined}
    />,
  );
  assert.match(html, /Reference Workflow/);
  assert.match(html, /技术分享资料递归总结工作流/);
  assert.match(html, /Markdown 文件过滤/);
  assert.equal(diff.operation, "update_station_prompt");
  assert.equal(diff.redacted, true);
  assert.equal(loaded.approvals[0].approval_id, "appr_reference");
  assert.equal(loaded.quality[0].evaluation_id, "qe_reference");
  assert.equal(loaded.context?.business.selected_scene, "scene_001");
  for (const forbidden of ["raw_trace_payload", "capability_token", "subscription_token", "Authorization", "raw_artifact_content"]) {
    assert(!html.includes(forbidden), `${forbidden} leaked in render`);
  }
});

test("event refresh ignores fake event status and reloads runtime truth", async () => {
  assert.equal(shouldRefreshForEvent({ type: "business.event.received", data: { status: "failed" } }), true);
  const calls: string[] = [];
  const client = {
    getInstanceStatus: async () => {
      calls.push("status");
      return completedStatus;
    },
    getBoard: async () => {
      calls.push("board");
      return { ...board, workflow_instance: { ...board.workflow_instance, status: "completed" }, current_station_ids: [] };
    },
    listApprovals: async () => {
      calls.push("approvals");
      return [{ approval_id: "appr_reference", status: "approved", active: true }];
    },
    listQuality: async () => {
      calls.push("quality");
      return [{ evaluation_id: "qe_reference", status: "passed", score: 0.91 }];
    },
    getContext: async () => {
      calls.push("context");
      return { workflow_instance_id: "wfi_reference", revision: 4, business: { selected_scene: "scene_002" } };
    },
  };
  const refreshed = await refreshWorkflowConsoleRuntimeState(client as never, {
    workflows: [],
    versions: [],
    instances: [],
    selectedWorkflowId: "wf_reference",
    selectedVersionId: "wfv_reference",
    selectedInstanceId: "wfi_reference",
    board,
    status,
    stationOutputs: [],
    approvals: [],
    quality: [],
    context: { workflow_instance_id: "wfi_reference", revision: 3, business: { selected_scene: "scene_001" } },
  });
  assert.deepEqual(calls, ["status", "board", "approvals", "quality", "context"]);
  assert.equal(refreshed.status?.status, "completed");
  assert.equal(refreshed.context?.business.selected_scene, "scene_002");
});
