"""V4.2-A no-false-green tests."""

from __future__ import annotations

from pathlib import Path


DOC_PATHS = [
    Path("docs/design/V4.2/v4_2_headless_interaction_pivot_plan.md"),
    Path("docs/design/V4.2/v4_2_headless_interaction_pivot_completion_note.md"),
    Path("docs/design/V4.2/evidence/headless-interaction/result-summary.md"),
    Path("docs/design/V4.x/v4_x_headless_current_gap_analysis.md"),
]

FORBIDDEN_COMPLETION_CLAIMS = [
    "complete Workflow Studio ready",
    "Agent executor ready",
    "controlled executor ready",
    "production-ready external app support",
    "full multi-Agent orchestration ready",
]


def _allowed_forbidden_claim_context(text: str, claim: str) -> bool:
    start = 0
    indexes = []
    while True:
        index = text.find(claim, start)
        if index < 0:
            break
        indexes.append(index)
        start = index + len(claim)
    for index in indexes:
        context = text[max(0, index - 300) : index + len(claim) + 80].lower()
        if not (
            "forbidden" in context
            or "must not claim" in context
            or "must not implement" in context
            or "不得声明" in context
            or "不能声明" in context
            or "禁止" in context
            or "not prove" in context
        ):
            return False
    return True


def test_forbidden_claims_only_appear_as_forbidden_context() -> None:
    for path in DOC_PATHS:
        text = path.read_text(encoding="utf-8")
        for claim in FORBIDDEN_COMPLETION_CLAIMS:
            assert _allowed_forbidden_claim_context(text, claim), f"{claim} appears as an allowed claim in {path}"


def test_result_summary_keeps_v42a_scope_narrow() -> None:
    text = Path("docs/design/V4.2/evidence/headless-interaction/result-summary.md").read_text(encoding="utf-8")

    assert "V4.2-A complete: headless interaction baseline ready for local workflow validation." in text
    assert "Generic controlled execution runtime is deferred to V4.2-B/C: PASS" in text
    assert "No false-green claims: PASS" in text
