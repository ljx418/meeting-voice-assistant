import assert from "node:assert/strict";
import test from "node:test";
import { isDemoMode, loadWorkflowConsoleData, shouldRefreshForEvent } from "../hooks/useWorkflowConsoleData.js";
import type { WorkflowBoard, WorkflowStatus } from "../api/types.js";

const status: WorkflowStatus = {
  workflow_instance_id: "wfi_real",
  status: "running",
  current_station_ids: ["station_a"],
  station_counts: { completed: 1 },
};

const board: WorkflowBoard = {
  workflow_instance: {
    workflow_instance_id: "wfi_real",
    workflow_template_id: "wf_real",
    workflow_version_id: "wfv_real",
    status: "running",
  },
  stations: [
    {
      station: { station_id: "station_a", name: "真实节点" },
      runs: [{ station_run_id: "sr_real", station_id: "station_a", status: "completed", output_artifacts: [] }],
      status: "completed",
      output_artifacts: [],
    },
  ],
  current_station_ids: ["station_a"],
};

test("demo mode is explicit only", () => {
  assert.equal(isDemoMode({ VITE_HARNESSOS_DEMO_MODE: "true" }), true);
  assert.equal(isDemoMode({ VITE_HARNESSOS_DEMO_MODE: "false" }), false);
  assert.equal(isDemoMode({}), false);
});

test("loadWorkflowConsoleData hydrates from BFF-style real DTOs", async () => {
  const calls: string[] = [];
  const client = {
    listWorkflows: async () => {
      calls.push("workflows");
      return [{ workflow_template_id: "wf_real", name: "真实工作流", latest_version_id: "wfv_real" }];
    },
    listWorkflowVersions: async () => {
      calls.push("versions");
      return [{ workflow_template_id: "wf_real", workflow_version_id: "wfv_real", version: "1.0.0" }];
    },
    listInstances: async () => {
      calls.push("instances");
      return [{ workflow_template_id: "wf_real", workflow_version_id: "wfv_real", workflow_instance_id: "wfi_real", status: "running" }];
    },
    getInstanceStatus: async () => {
      calls.push("status");
      return status;
    },
    getBoard: async () => {
      calls.push("board");
      return board;
    },
    listStationOutputs: async () => {
      calls.push("outputs");
      return [{ artifact_id: "art_real", name: "storyboard.json" }];
    },
    listApprovals: async () => {
      calls.push("approvals");
      return [{ approval_id: "appr_real", status: "pending" }];
    },
    listQuality: async () => {
      calls.push("quality");
      return [{ evaluation_id: "qe_real", status: "passed", score: 0.9 }];
    },
    getContext: async () => {
      calls.push("context");
      return { workflow_instance_id: "wfi_real", revision: 1, business: { node: "station_a" } };
    },
  };

  const loaded = await loadWorkflowConsoleData(client as never);
  assert.deepEqual(calls, ["workflows", "versions", "instances", "status", "board", "outputs", "approvals", "quality", "context"]);
  assert.equal(loaded.selectedWorkflowId, "wf_real");
  assert.equal(loaded.selectedInstanceId, "wfi_real");
  assert.equal(loaded.board?.stations[0].station.name, "真实节点");
  assert.equal(loaded.stationOutputs[0].artifact_id, "art_real");
  assert.equal(loaded.approvals[0].approval_id, "appr_real");
  assert.equal(loaded.quality[0].evaluation_id, "qe_real");
  assert.equal(loaded.context?.business.node, "station_a");
});

test("event refresh is driven by allowlisted live events", () => {
  assert.equal(shouldRefreshForEvent({ type: "artifact.registered" }), true);
  assert.equal(shouldRefreshForEvent({ type: "workflow.patch.applied" }), true);
  assert.equal(shouldRefreshForEvent({ type: "quality.evaluated" }), false);
});
