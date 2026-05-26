"""V4.0-O forbidden completion claim guard."""

from __future__ import annotations

from pathlib import Path

from tests.v4_0_guard_utils import (
    SAFE_FORBIDDEN_CLAIM_CONTEXT_MARKERS,
    assert_phrases_only_in_safe_context,
    v4_0_doc_and_frontend_files,
)


ALLOWED_O_CLAIM = "V4.0-O complete: governed canvas proposal workflow ready for expanded dev/local Workflow Console validation."
FORBIDDEN_CLAIMS = {
    "complete Workflow Studio ready",
    "full low-code canvas editing ready",
    "complete AgentTalkWindow ready",
    "controlled executor ready",
    "Agent executor ready",
    "autonomous workflow editing ready",
    "direct canvas-to-runtime mutation ready",
    "production-ready external app support",
}
ALLOWED_FORBIDDEN_CLAIM_FILES = {
    "docs/design/V4.0/00_README.md",
    "docs/design/V4.0/v4_0_current_gap_analysis.md",
    "docs/design/V4.0/v4_0_completion_audit_report.md",
    "docs/design/V4.0/v4_0_event_contract_map.md",
    "docs/design/V4.0/v4_0_ui_contract_map.md",
    "docs/design/V4.0/v4_0_workflow_studio_low_code_baseline.md",
    "docs/design/V4.0/v4_0_o_governed_canvas_proposal_workflow_plan.md",
    "docs/design/V4.0/v4_0_o_governed_canvas_proposal_workflow_completion_note.md",
}


def test_v4_0_o_allowed_claim_is_documented() -> None:
    plan = Path("docs/design/V4.0/v4_0_o_governed_canvas_proposal_workflow_plan.md").read_text(encoding="utf-8")
    assert ALLOWED_O_CLAIM in plan


def test_forbidden_claims_only_appear_as_forbidden_or_non_goals() -> None:
    files = [
        path
        for path in v4_0_doc_and_frontend_files()
        if path.as_posix() not in ALLOWED_FORBIDDEN_CLAIM_FILES
    ]
    assert_phrases_only_in_safe_context(
        files=files,
        phrases=FORBIDDEN_CLAIMS,
        safe_markers=SAFE_FORBIDDEN_CLAIM_CONTEXT_MARKERS,
    )
