"""V5.2 credential and provider lifecycle core tests."""

from __future__ import annotations

import json

import pytest

from core.auth.credential_provider import (
    CredentialProviderError,
    CredentialProviderRegistry,
    ProviderProfile,
    resolve_provider_profile_from_env,
)
from core.auth.tenant_boundary import IdentityContext


def _context(*, actor_type: str = "human_user", actor_id: str = "user_001") -> IdentityContext:
    kwargs = {"user_id": "user_001"} if actor_type == "human_user" else {}
    if actor_type == "agent":
        kwargs = {"agent_id": "agent_001", "session_id": "agent_session_001"}
    return IdentityContext(
        tenant_id="tenant_001",
        workspace_id="workspace_001",
        project_id="project_001",
        app_id="app_001",
        actor_type=actor_type,
        actor_id=actor_id,
        request_id="req_001",
        correlation_id="corr_001",
        **kwargs,
    )


def _profile_data(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "provider_profile_id": "provider_profile_001",
        "tenant_id": "tenant_001",
        "workspace_id": "workspace_001",
        "project_id": "project_001",
        "app_id": "app_001",
        "provider": "minimax",
        "provider_kind": "llm",
        "base_url_ref": "env://MINIMAX_BASE_URL",
        "model_refs": ["MiniMax-M2.1"],
        "credential_ref_id": "credential_ref_001",
        "capability_refs": ["llm.chat", "llm.summarize"],
        "status": "active",
        "created_by": "user_001",
    }
    data.update(overrides)
    return data


def _registry_with_profile() -> tuple[CredentialProviderRegistry, IdentityContext, ProviderProfile]:
    context = _context()
    registry = CredentialProviderRegistry()
    profile = registry.create_provider_profile(context, _profile_data(), source="user", user_confirmed=True)
    return registry, context, profile


def test_provider_profile_strict_schema_rejects_unknown_fields() -> None:
    data = _profile_data(layout={"x": 10})
    with pytest.raises(CredentialProviderError) as exc:
        ProviderProfile.from_mapping(data)
    assert exc.value.code == "PROVIDER_PROFILE_INVALID"
    assert exc.value.reason == "unknown_field"


def test_provider_profile_rejects_sensitive_fields() -> None:
    data = _profile_data()
    data["Authorization"] = "Bearer secret-token-value"
    with pytest.raises(CredentialProviderError) as exc:
        ProviderProfile.from_mapping(data)
    assert exc.value.reason == "sensitive_field"
    assert "secret-token-value" not in json.dumps(exc.value.to_error())


def test_provider_profile_requires_tenant_workspace_project_app_binding() -> None:
    registry = CredentialProviderRegistry()
    context = _context()
    data = _profile_data(workspace_id="workspace_other")
    with pytest.raises(CredentialProviderError) as exc:
        registry.create_provider_profile(context, data, source="user", user_confirmed=True)
    assert exc.value.code == "CREDENTIAL_SCOPE_DENIED"
    assert exc.value.reason == "workspace_mismatch"


def test_credential_issue_requires_user_confirmation() -> None:
    registry, context, profile = _registry_with_profile()
    with pytest.raises(CredentialProviderError) as exc:
        registry.issue_credential(
            context,
            provider_profile_id=profile.provider_profile_id,
            credential_ref_id="credential_ref_001",
            secret_ref="env://MINIMAX_API_KEY",
            source="user",
            user_confirmed=False,
        )
    assert exc.value.code == "CREDENTIAL_USER_CONFIRMATION_REQUIRED"


def test_source_agent_cannot_issue_rotate_or_revoke_credentials() -> None:
    registry, context, profile = _registry_with_profile()
    registry.issue_credential(
        context,
        provider_profile_id=profile.provider_profile_id,
        credential_ref_id="credential_ref_001",
        secret_ref="env://MINIMAX_API_KEY",
        source="user",
        user_confirmed=True,
    )
    agent_context = _context(actor_type="agent", actor_id="agent_001")
    for operation in ("issue", "rotate", "revoke"):
        with pytest.raises(CredentialProviderError) as exc:
            if operation == "issue":
                registry.issue_credential(
                    agent_context,
                    provider_profile_id=profile.provider_profile_id,
                    credential_ref_id=f"credential_ref_agent_{operation}",
                    secret_ref="env://MINIMAX_API_KEY",
                    source="agent",
                    user_confirmed=True,
                )
            elif operation == "rotate":
                registry.rotate_credential(
                    agent_context,
                    credential_ref_id="credential_ref_001",
                    new_secret_ref="env://MINIMAX_API_KEY",
                    source="agent",
                    user_confirmed=True,
                )
            else:
                registry.revoke_credential(
                    agent_context,
                    credential_ref_id="credential_ref_001",
                    source="agent",
                    user_confirmed=True,
                )
        assert exc.value.code == "CREDENTIAL_AGENT_MUTATION_DENIED"


def test_credential_reference_never_exposes_raw_secret() -> None:
    registry, context, profile = _registry_with_profile()
    credential, event = registry.issue_credential(
        context,
        provider_profile_id=profile.provider_profile_id,
        credential_ref_id="credential_ref_001",
        secret_ref="secret://provider/minimax/key",
        source="user",
        user_confirmed=True,
    )
    raw = json.dumps({"credential": credential.to_dict(), "event": event.to_dict()})
    assert "provider/minimax/key" not in raw
    assert "secret://[REDACTED]" in raw
    assert event.operation == "credential.issue"
    assert event.user_confirmed is True


def test_rotate_and_revoke_produce_lifecycle_events() -> None:
    registry, context, profile = _registry_with_profile()
    registry.issue_credential(
        context,
        provider_profile_id=profile.provider_profile_id,
        credential_ref_id="credential_ref_001",
        secret_ref="env://MINIMAX_API_KEY",
        source="user",
        user_confirmed=True,
    )
    rotated, rotate_event = registry.rotate_credential(
        context,
        credential_ref_id="credential_ref_001",
        new_secret_ref="env://MINIMAX_API_KEY",
        source="user",
        user_confirmed=True,
    )
    revoked, revoke_event = registry.revoke_credential(
        context,
        credential_ref_id="credential_ref_001",
        source="user",
        user_confirmed=True,
    )
    assert rotated.status == "active"
    assert rotate_event.operation == "credential.rotate.complete"
    assert rotate_event.previous_status == "active"
    assert revoked.status == "revoked"
    assert revoke_event.operation == "credential.revoke"
    assert len(registry.lifecycle_events) == 3


def test_raw_secret_ref_is_rejected() -> None:
    registry, context, profile = _registry_with_profile()
    with pytest.raises(CredentialProviderError) as exc:
        registry.issue_credential(
            context,
            provider_profile_id=profile.provider_profile_id,
            credential_ref_id="credential_ref_001",
            secret_ref="sk-real-looking-secret",
            source="user",
            user_confirmed=True,
        )
    assert exc.value.code == "CREDENTIAL_SECRET_REDACTED"


def test_provider_smoke_records_redacted_invocation_evidence() -> None:
    registry, context, profile = _registry_with_profile()
    registry.issue_credential(
        context,
        provider_profile_id=profile.provider_profile_id,
        credential_ref_id="credential_ref_001",
        secret_ref="env://MINIMAX_API_KEY",
        source="user",
        user_confirmed=True,
    )
    evidence = registry.validate_provider_smoke(
        context,
        provider_profile_id=profile.provider_profile_id,
        capability_ref="llm.summarize",
        model_ref="MiniMax-M2.1",
        input_artifact_refs=["artifact_input_001"],
        output_artifact_refs=["artifact_output_001"],
        prompt_template_ref="prompt_template_v5_2_smoke",
        redacted_input_summary_ref="summary://input/redacted",
        redacted_output_summary_ref="summary://output/redacted",
        runtime_result_ref="runtime_result_001",
        source="user",
        user_confirmed=True,
    )
    data = evidence.to_dict()
    raw = json.dumps(data)
    assert data["provider"] == "minimax"
    assert data["model_ref"] == "MiniMax-M2.1"
    assert data["redaction_status"] == "redacted"
    assert "raw prompt" not in raw
    assert "MINIMAX_API_KEY" not in raw
    assert "Bearer" not in raw


def test_provider_smoke_rejects_raw_summary_refs() -> None:
    registry, context, profile = _registry_with_profile()
    registry.issue_credential(
        context,
        provider_profile_id=profile.provider_profile_id,
        credential_ref_id="credential_ref_001",
        secret_ref="env://MINIMAX_API_KEY",
        source="user",
        user_confirmed=True,
    )
    with pytest.raises(CredentialProviderError) as exc:
        registry.validate_provider_smoke(
            context,
            provider_profile_id=profile.provider_profile_id,
            capability_ref="llm.summarize",
            model_ref="MiniMax-M2.1",
            input_artifact_refs=["artifact_input_001"],
            output_artifact_refs=["artifact_output_001"],
            prompt_template_ref="prompt_template_v5_2_smoke",
            redacted_input_summary_ref="raw prompt leaked",
            redacted_output_summary_ref="summary://output/redacted",
            runtime_result_ref="runtime_result_001",
            source="user",
            user_confirmed=True,
        )
    assert exc.value.reason == "raw_summary_ref_denied"


def test_env_provider_profile_resolution_uses_real_config_without_exposing_key(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env.local"
    env_file.write_text(
        "\n".join(
            [
                "V5_LLM_PROVIDER=minimax",
                "V5_LLM_MODEL=MiniMax-M2.1",
                "MINIMAX_API_KEY=sk-test-realistic-secret",
                "MINIMAX_BASE_URL=https://api.minimax.chat/v1",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    profile_data, secret_ref, secret_configured, source = resolve_provider_profile_from_env(_context(), env_files=(str(env_file),))
    raw = json.dumps({"profile": profile_data, "secret_ref": secret_ref, "secret_configured": secret_configured, "source": source})
    assert profile_data["provider"] == "minimax"
    assert profile_data["model_refs"] == ["MiniMax-M2.1"]
    assert secret_ref == "env://MINIMAX_API_KEY"
    assert secret_configured is True
    assert source.endswith(".env.local")
    assert "sk-test-realistic-secret" not in raw

