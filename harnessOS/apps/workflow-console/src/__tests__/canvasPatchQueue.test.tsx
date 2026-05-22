import assert from "node:assert/strict";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { WorkflowEditingPanel } from "../components/WorkflowEditingPanel.js";
import type { WorkflowPatchDiff, WorkflowPatchProposal } from "../api/types.js";

const diff: WorkflowPatchDiff = {
  workflow_patch_id: "patch_1",
  workflow_draft_id: "draft_1",
  base_revision: 1,
  operation: "add_station",
  target: {},
  before_summary: "before",
  after_summary: "after",
  risk_flags: [],
  requires_approval: false,
  redacted: true,
};

test("stale patch disables apply and shows blocking warning", () => {
  const proposal: WorkflowPatchProposal = {
    workflow_patch_id: "patch_1",
    patch_id: "patch_1",
    workflow_template_id: "template_1",
    workflow_draft_id: "draft_1",
    base_revision: 1,
    current_draft_revision: 2,
    operation: "add_station",
    status: "stale",
    selected: true,
    stale_reason: "base_revision_mismatch",
    conflict_reason: "base_revision 1 does not match current draft revision 2",
  };

  const html = renderToStaticMarkup(<WorkflowEditingPanel proposal={proposal} diff={diff} onApplyPatch={() => undefined} />);

  assert.match(html, /base_revision 1 does not match current draft revision 2/);
  assert.match(html, /disabled=""/);
});

test("high risk patch remains blocked from direct apply", () => {
  const proposal: WorkflowPatchProposal = {
    workflow_patch_id: "patch_2",
    workflow_template_id: "template_1",
    workflow_draft_id: "draft_1",
    operation: "update_connector",
    status: "blocked",
    requires_approval: true,
    risk_flags: ["requires_approval"],
    conflict_reason: "requires_approval",
  };
  const highRiskDiff = { ...diff, workflow_patch_id: "patch_2", requires_approval: true, risk_flags: ["requires_approval"] };

  const html = renderToStaticMarkup(<WorkflowEditingPanel proposal={proposal} diff={highRiskDiff} onApplyPatch={() => undefined} />);

  assert.match(html, /requires_approval/);
  assert.match(html, /需要治理审批/);
});
