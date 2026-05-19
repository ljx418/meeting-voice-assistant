import assert from "node:assert/strict";
import test from "node:test";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { ApprovalPanel } from "../components/ApprovalPanel.js";

test("ApprovalPanel renders explicit user decision controls and disables inactive approvals", () => {
  const html = renderToStaticMarkup(
    <ApprovalPanel
      approvals={[
        { approval_id: "appr_pending", status: "pending", request_summary: "发布前确认", active: true },
        { approval_id: "appr_inactive", status: "pending", request_summary: "已取消", active: false, inactive_reason: "workflow_cancelled" },
      ]}
    />,
  );
  assert.match(html, /审批面板/);
  assert.match(html, /用户确认通过/);
  assert.match(html, /用户确认拒绝/);
  assert.match(html, /workflow_cancelled/);
  assert.match(html, /disabled=""/);
  assert(!html.includes("approval.approve"));
  assert(!html.includes("approval.reject"));
  assert(!html.includes("自动"));
});
