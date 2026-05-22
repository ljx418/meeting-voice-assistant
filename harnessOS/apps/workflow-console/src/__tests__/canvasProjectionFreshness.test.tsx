import assert from "node:assert/strict";
import test from "node:test";
import { projectBoardForCanvas, shouldRefreshForEvent } from "../hooks/useWorkflowConsoleData.js";
import type { CanvasDraftProjection, WorkflowBoard } from "../api/types.js";

const board: WorkflowBoard = {
  workflow_instance: { workflow_instance_id: "wfi_1", workflow_template_id: "wf_1", workflow_version_id: "wfv_1", status: "running" },
  current_station_ids: ["station_a"],
  stations: [{ station: { station_id: "station_a", name: "A" }, status: "completed", runs: [] }],
};

test("projection freshness fields are carried without replacing runtime status", () => {
  const projection: CanvasDraftProjection = {
    projection_id: "projection_1",
    workflow_instance_id: "wfi_1",
    workflow_template_id: "wf_1",
    workflow_draft_id: "draft_1",
    draft_revision: 2,
    generated_at: "2026-05-22T00:00:00Z",
    board_status_timestamp: "2026-05-22T00:00:00Z",
    patch_queue_revision: "patch_queue:empty",
    freshness_state: "fresh",
    stale_reasons: [],
    source_refs: { design_structure: { draft_revision: 2 } },
    nodes: [
      { station_id: "station_a", name: "A", skill_refs: [], connector_refs: [], run_count: 0 },
      { station_id: "station_b", name: "Draft B", skill_refs: [], connector_refs: [], run_count: 0 },
    ],
    edges: [],
    runtime_summary: {},
    redaction_status: "redacted",
  };

  const projected = projectBoardForCanvas(board, projection);

  assert.equal(projection.freshness_state, "fresh");
  assert.equal(projected.stations[0].status, "completed");
  assert.equal(projected.stations[1].status, "draft_only");
});

test("workflow patch proposed event only triggers refresh path", () => {
  assert.equal(shouldRefreshForEvent({ type: "workflow.patch.proposed", data: { draft_revision: 999, patch_status: "applied" } }), true);
});
