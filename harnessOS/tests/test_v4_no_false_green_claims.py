"""V4.x unified no-false-green claim guard tests."""

from __future__ import annotations

from pathlib import Path


DOC_PATHS = [
    Path("docs/design/V4.x/00_README.md"),
    Path("docs/design/V4.x/v4_x_headless_current_gap_analysis.md"),
    Path("docs/design/V4.x/v4_x_headless_first_roadmap.md"),
    Path("docs/design/V4.x/v4_x_headless_api_surface_map.md"),
    Path("docs/design/V4.x/v4_x_tui_drawio_html_report_plan.md"),
    Path("docs/design/V4.x/v4_x_unified_experience_prd.md"),
    Path("docs/design/V4.x/v4_x_unified_development_plan.md"),
    Path("docs/design/V4.x/v4_x_unified_experience_completion_note.md"),
    Path("docs/design/V4.x/evidence/unified-experience/result-summary.md"),
]

FORBIDDEN_CLAIMS = [
    "complete Workflow Studio ready",
    "complete AgentTalkWindow ready",
    "Agent executor ready",
    "controlled executor ready",
    "production-ready external app support",
    "full multi-Agent orchestration ready",
    "autonomous workflow editing ready",
]

FORBIDDEN_COPY = [
    "自动应用",
    "自动发布",
    "Agent 已执行",
    "Agent 已发布",
]


def _allowed_forbidden_context(text: str, claim: str) -> bool:
    start = 0
    indexes = []
    while True:
        index = text.find(claim, start)
        if index < 0:
            break
        indexes.append(index)
        start = index + len(claim)
    for index in indexes:
        context = text[max(0, index - 320) : index + len(claim) + 160].lower()
        if not (
            "forbidden" in context
            or "still forbidden" in context
            or "禁止" in context
            or "不能声明" in context
            or "仍不能声明" in context
            or "does not prove" in context
            or "does not claim" in context
            or "not claim" in context
            or "不实现" in context
            or "非目标" in context
        ):
            return False
    return True


def test_forbidden_claims_only_appear_in_guard_context() -> None:
    for path in DOC_PATHS:
        text = path.read_text(encoding="utf-8")
        for claim in FORBIDDEN_CLAIMS:
            assert _allowed_forbidden_context(text, claim), f"{claim} appears as a positive claim in {path}"


def test_forbidden_ui_copy_is_absent_from_unified_docs() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in DOC_PATHS)
    for copy in FORBIDDEN_COPY:
        assert copy not in combined


def test_gap_drawio_reflects_unified_experience_rebaseline() -> None:
    text = Path("docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio").read_text(encoding="utf-8")

    for expected in [
        "Unified Headless Experience",
        "V4-U5C / U5D / U5E / U5 / U6",
        "Mission Console / TUI",
        "Workflow Blueprint",
        "Runtime Report / Evidence Chain",
        "Interaction Orchestrator",
        "ExperienceStateProjection",
        "Runtime Capability Matrix",
    ]:
        assert expected in text
