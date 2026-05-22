import assert from "node:assert/strict";
import test from "node:test";
import { renderToStaticMarkup } from "react-dom/server";
import type { GovernanceReviewSummary } from "../api/types.js";
import { GovernanceReviewPanel } from "../components/GovernanceReviewPanel.js";

const review: GovernanceReviewSummary = {
  workflow_instance_id: "wfi_1",
  workflow_template_id: "wf_1",
  summary: {
    evidence_count: 0,
    handoff_count: 1,
    status_counts: {},
    operation_counts: {},
  },
  operation_evidence: [],
  handoff_summary: [{ handoff_id: "aah_1", status: "active", target_panel: "editing_panel" }],
  audit_timeline: [{ type: "agent_handoff", resource_id: "aah_1", status: "active" }],
  redaction_status: "redacted",
};

test("Agent evidence review remains read-only and redacted", () => {
  const html = renderToStaticMarkup(<GovernanceReviewPanel review={review} />);
  assert(html.includes("只读证据链"));
  assert(!html.includes("capability_token"));
  assert(!html.includes("raw_trace_payload"));
  for (const forbidden of ["Apply", "Publish", "Approve", "Reject", "Execute", "Run", "自动应用", "自动发布"]) {
    assert(!html.includes(forbidden), `${forbidden} appeared in evidence review`);
  }
});
