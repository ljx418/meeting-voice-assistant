"""V4.0-Q executor claim guard tests."""

from __future__ import annotations

from pathlib import Path

from tests.v4_0_guard_utils import (
    SAFE_FORBIDDEN_CLAIM_CONTEXT_MARKERS,
    SAFE_FORBIDDEN_COPY_CONTEXT_MARKERS,
    assert_phrases_only_in_safe_context,
    v4_0_doc_and_frontend_files,
)


ALLOWED_Q_CLAIM = "V4.0-Q complete: controlled executor design gate ready for review."
FORBIDDEN_Q_CLAIMS = {
    "controlled executor ready",
    "Agent executor ready",
    "autonomous workflow editing ready",
    "complete AgentTalkWindow ready",
    "complete Workflow Studio ready",
    "production-ready external app support",
    "full low-code canvas editing ready",
}
FORBIDDEN_UI_COPY = {
    "自动应用",
    "自动发布",
    "Agent 已执行",
    "Agent 已发布",
}


def test_v4_0_q_allowed_claim_is_documented() -> None:
    completion = Path("docs/design/V4.0/v4_0_q_controlled_executor_design_gate_completion_note.md").read_text(encoding="utf-8")
    assert ALLOWED_Q_CLAIM in completion


def test_executor_forbidden_claims_and_misleading_copy_are_guarded() -> None:
    files = v4_0_doc_and_frontend_files()
    assert_phrases_only_in_safe_context(
        files=files,
        phrases=FORBIDDEN_Q_CLAIMS,
        safe_markers=SAFE_FORBIDDEN_CLAIM_CONTEXT_MARKERS,
    )
    assert_phrases_only_in_safe_context(
        files=files,
        phrases=FORBIDDEN_UI_COPY,
        safe_markers=SAFE_FORBIDDEN_COPY_CONTEXT_MARKERS,
    )
