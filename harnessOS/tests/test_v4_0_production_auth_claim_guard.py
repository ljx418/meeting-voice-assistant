"""V4.0-S production auth claim guard tests."""

from __future__ import annotations

from pathlib import Path

from tests.v4_0_guard_utils import (
    SAFE_FORBIDDEN_CLAIM_CONTEXT_MARKERS,
    SAFE_FORBIDDEN_COPY_CONTEXT_MARKERS,
    assert_phrases_only_in_safe_context,
    v4_0_doc_and_frontend_files,
)


ALLOWED_S_CLAIM = "V4.0-S complete: production auth and tenant boundary follow-up design ready for review."
FORBIDDEN_S_CLAIMS = {
    "production-ready external app support",
    "enterprise auth ready",
    "multi-tenant control plane ready",
    "OAuth ready",
    "SSO ready",
    "controlled executor ready",
    "Agent executor ready",
    "complete Workflow Studio ready",
    "complete AgentTalkWindow ready",
}
FORBIDDEN_AUTH_COPY = {
    "生产可用",
    "生产认证已完成",
    "企业认证可用",
    "企业级认证已完成",
    "多租户控制台已完成",
    "OAuth 已接入",
    "SSO 已接入",
    "生产接入已完成",
    "生产客户可接入",
    "production ready",
}


def test_v4_0_s_allowed_claim_is_documented() -> None:
    completion = Path("docs/design/V4.0/v4_0_s_production_auth_tenant_boundary_design_completion_note.md").read_text(encoding="utf-8")
    assert ALLOWED_S_CLAIM in completion


def test_production_auth_forbidden_claims_and_copy_are_guarded() -> None:
    files = v4_0_doc_and_frontend_files()
    assert_phrases_only_in_safe_context(
        files=files,
        phrases=FORBIDDEN_S_CLAIMS,
        safe_markers=SAFE_FORBIDDEN_CLAIM_CONTEXT_MARKERS,
    )
    assert_phrases_only_in_safe_context(
        files=files,
        phrases=FORBIDDEN_AUTH_COPY,
        safe_markers=SAFE_FORBIDDEN_COPY_CONTEXT_MARKERS,
    )
