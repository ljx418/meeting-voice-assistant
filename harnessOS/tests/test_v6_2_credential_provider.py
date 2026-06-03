from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from core.auth.credential_provider import CredentialProviderError, CredentialProviderRegistry
from core.auth.production_credential_provider import ProductionCredentialProviderLifecycle
from core.auth.tenant_boundary import IdentityContext


def context(*, actor_type: str = "human_user") -> IdentityContext:
    kwargs = {"user_id": "user_v6"} if actor_type == "human_user" else {}
    if actor_type == "agent":
        kwargs = {"agent_id": "agent_v6", "session_id": "agent_session_v6"}
    return IdentityContext(
        tenant_id="tenant_alpha",
        workspace_id="workspace_docs",
        project_id="project_v6",
        app_id="app_workflow",
        actor_type=actor_type,
        actor_id="actor_v6",
        request_id="req_v6_2",
        correlation_id="corr_v6_2",
        **kwargs,
    )


def profile_data() -> dict[str, object]:
    return {
        "provider_profile_id": "provider_profile_minimax_v6",
        "tenant_id": "tenant_alpha",
        "workspace_id": "workspace_docs",
        "project_id": "project_v6",
        "app_id": "app_workflow",
        "provider": "minimax",
        "provider_kind": "llm",
        "base_url_ref": "env://MINIMAX_BASE_URL",
        "model_refs": ["MiniMax-M2.1"],
        "credential_ref_id": "credential_ref_minimax_v6",
        "capability_refs": ["llm.summarize"],
        "status": "active",
        "created_by": "actor_v6",
    }


def lifecycle() -> tuple[ProductionCredentialProviderLifecycle, IdentityContext]:
    ctx = context()
    registry = CredentialProviderRegistry()
    registry.create_provider_profile(ctx, profile_data(), source="user", user_confirmed=True)
    registry.issue_credential(
        ctx,
        provider_profile_id="provider_profile_minimax_v6",
        credential_ref_id="credential_ref_minimax_v6",
        secret_ref="env://MINIMAX_API_KEY",
        source="user",
        user_confirmed=True,
    )
    return ProductionCredentialProviderLifecycle(registry), ctx


def future() -> str:
    return (datetime.now(UTC) + timedelta(minutes=5)).isoformat()


def past() -> str:
    return (datetime.now(UTC) - timedelta(minutes=5)).isoformat()


def issue_valid_lease(life: ProductionCredentialProviderLifecycle, ctx: IdentityContext):
    return life.issue_lease(
        ctx,
        provider_profile_id="provider_profile_minimax_v6",
        audience="llm_provider:minimax",
        operation="provider.invoke",
        capability_ref="llm.summarize",
        model_ref="MiniMax-M2.1",
        expires_at=future(),
    )


def invoke(life: ProductionCredentialProviderLifecycle, ctx: IdentityContext, lease_id: str, **overrides: str):
    data = {
        "credential_lease_id": lease_id,
        "audience": "llm_provider:minimax",
        "operation": "provider.invoke",
        "capability_ref": "llm.summarize",
        "model_ref": "MiniMax-M2.1",
        "provider_config_source": "env://MINIMAX_BASE_URL",
        "input_artifact_refs": ["artifact://input/redacted"],
        "output_artifact_refs": ["artifact://output/redacted"],
        "prompt_template_ref": "prompt_template://v6_2_summary",
        "redacted_input_summary_ref": "summary://input/redacted",
        "redacted_output_summary_ref": "summary://output/redacted",
        "runtime_result_ref": "runtime://v6_2/provider-smoke",
    }
    data.update(overrides)
    return life.validate_provider_invocation(ctx, **data)


def test_v6_2_lease_is_tenant_app_audience_operation_bound() -> None:
    life, ctx = lifecycle()
    lease = issue_valid_lease(life, ctx)

    assert lease.tenant_id == ctx.tenant_id
    assert lease.app_id == ctx.app_id
    assert lease.audience == "llm_provider:minimax"
    assert lease.operation == "provider.invoke"


def test_v6_2_valid_invocation_records_redacted_refs() -> None:
    life, ctx = lifecycle()
    lease = issue_valid_lease(life, ctx)
    evidence = invoke(life, ctx, lease.credential_lease_id).to_dict()
    raw = str(evidence)

    assert evidence["credential_lease_id"] == lease.credential_lease_id
    assert evidence["credential_ref_id"] == "credential_ref_minimax_v6"
    assert evidence["lease_decision"] == "allow"
    assert "MINIMAX_API_KEY" not in raw
    assert "raw prompt" not in raw
    assert "Bearer" not in raw


def test_v6_2_expired_lease_denied() -> None:
    life, ctx = lifecycle()
    lease = life.issue_lease(
        ctx,
        provider_profile_id="provider_profile_minimax_v6",
        audience="llm_provider:minimax",
        operation="provider.invoke",
        capability_ref="llm.summarize",
        model_ref="MiniMax-M2.1",
        expires_at=past(),
    )
    with pytest.raises(CredentialProviderError) as exc:
        invoke(life, ctx, lease.credential_lease_id)
    assert exc.value.code == "CREDENTIAL_LEASE_EXPIRED"


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("audience", "llm_provider:other", "audience_mismatch"),
        ("operation", "provider.other", "operation_mismatch"),
        ("capability_ref", "llm.chat", "capability_not_allowed"),
        ("model_ref", "OtherModel", "model_not_allowed"),
    ],
)
def test_v6_2_bound_invocation_mismatch_denied(field: str, value: str, reason: str) -> None:
    life, ctx = lifecycle()
    lease = issue_valid_lease(life, ctx)
    with pytest.raises(CredentialProviderError) as exc:
        invoke(life, ctx, lease.credential_lease_id, **{field: value})
    assert exc.value.reason == reason


def test_v6_2_revoked_credential_denied() -> None:
    life, ctx = lifecycle()
    lease = issue_valid_lease(life, ctx)
    life.registry.revoke_credential(ctx, credential_ref_id="credential_ref_minimax_v6", source="user", user_confirmed=True)
    with pytest.raises(CredentialProviderError) as exc:
        invoke(life, ctx, lease.credential_lease_id)
    assert exc.value.reason == "credential_not_active"


def test_v6_2_emergency_revoke_blocks_invocation() -> None:
    life, ctx = lifecycle()
    lease = issue_valid_lease(life, ctx)
    life.registry.revoke_credential(ctx, credential_ref_id="credential_ref_minimax_v6", source="user", user_confirmed=True, emergency=True)
    with pytest.raises(CredentialProviderError) as exc:
        invoke(life, ctx, lease.credential_lease_id)
    assert exc.value.reason == "credential_not_active"


def test_v6_2_raw_secret_and_raw_prompt_rejected() -> None:
    life, ctx = lifecycle()
    lease = issue_valid_lease(life, ctx)
    with pytest.raises(CredentialProviderError) as exc:
        invoke(life, ctx, lease.credential_lease_id, redacted_input_summary_ref="raw prompt: do not store")
    assert exc.value.code == "PROVIDER_EVIDENCE_REDACTION_DENIED"


def test_v6_2_source_agent_lifecycle_mutation_denied() -> None:
    life, _ctx = lifecycle()
    agent_ctx = context(actor_type="agent")
    with pytest.raises(CredentialProviderError) as exc:
        life.registry.issue_credential(
            agent_ctx,
            provider_profile_id="provider_profile_minimax_v6",
            credential_ref_id="credential_ref_agent",
            secret_ref="env://MINIMAX_API_KEY",
            source="agent",
            user_confirmed=True,
        )
    assert exc.value.code == "CREDENTIAL_AGENT_MUTATION_DENIED"
