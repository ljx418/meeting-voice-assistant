"""V4.0-R production readiness claim guard tests."""

from __future__ import annotations

from pathlib import Path

from tests.v4_0_guard_utils import (
    SAFE_FORBIDDEN_CLAIM_CONTEXT_MARKERS,
    SAFE_FORBIDDEN_COPY_CONTEXT_MARKERS,
    assert_phrases_only_in_safe_context,
    v4_0_doc_and_frontend_files,
)


ALLOWED_R_CLAIM = "V4.0-R complete: production readiness preflight ready for review."
FORBIDDEN_R_CLAIMS = {
    "production-ready external app support",
    "enterprise auth ready",
    "multi-tenant control plane ready",
    "controlled executor ready",
    "Agent executor ready",
    "complete Workflow Studio ready",
    "complete AgentTalkWindow ready",
}
FORBIDDEN_PRODUCTION_COPY = {
    "企业级认证已完成",
    "多租户控制台已完成",
    "生产接入已完成",
    "已支持生产客户接入",
    "production ready",
}


def test_v4_0_r_allowed_claim_is_documented() -> None:
    completion = Path("docs/design/V4.0/v4_0_r_production_readiness_preflight_completion_note.md").read_text(encoding="utf-8")
    assert ALLOWED_R_CLAIM in completion


def test_production_forbidden_claims_and_misleading_copy_are_guarded() -> None:
    files = v4_0_doc_and_frontend_files()
    assert_phrases_only_in_safe_context(
        files=files,
        phrases=FORBIDDEN_R_CLAIMS,
        safe_markers=SAFE_FORBIDDEN_CLAIM_CONTEXT_MARKERS,
    )
    assert_phrases_only_in_safe_context(
        files=files,
        phrases=FORBIDDEN_PRODUCTION_COPY,
        safe_markers=SAFE_FORBIDDEN_COPY_CONTEXT_MARKERS,
    )
