"""V4.0-O forbidden completion claim guard."""

from __future__ import annotations

from pathlib import Path


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
    for path in [*Path("docs/design/V4.0").glob("*.md"), *Path("apps/workflow-console/src").rglob("*.*")]:
        text = path.read_text(encoding="utf-8")
        relative = path.as_posix()
        for claim in FORBIDDEN_CLAIMS:
            if claim not in text:
                continue
            assert relative in ALLOWED_FORBIDDEN_CLAIM_FILES or "不能声明" in text or "禁止" in text or "Forbidden" in text, (
                f"{claim!r} appears outside explicit forbidden/non-goal context in {relative}"
            )
