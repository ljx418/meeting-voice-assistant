from __future__ import annotations

from core.auth.credential_provider import CredentialProviderRegistry, resolve_provider_profile_from_env
from core.auth.tenant_boundary import IdentityContext
from core.observability.audit_export import AuditRetentionPolicy, ObservabilityEvent, SecurityEventLog


def make_context(*, actor_type: str = "human_user", actor_id: str = "user_v5_3") -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v5",
        workspace_id="workspace_v5",
        project_id="project_v5",
        app_id="app_v5",
        actor_type=actor_type,
        actor_id=actor_id,
        user_id="user_v5_3" if actor_type == "human_user" else None,
        service_account_id="svc_v5_3" if actor_type == "service_account" else None,
        agent_id="agent_v5_3" if actor_type == "agent" else None,
        session_id="session_v5_3" if actor_type == "agent" else None,
        request_id="request_v5_3",
        correlation_id="correlation_v5_3",
    )


def make_provider_invocation_event(context: IdentityContext | None = None) -> ObservabilityEvent:
    context = context or make_context()
    registry = CredentialProviderRegistry()
    profile_data, secret_ref, _secret_configured, _source = resolve_provider_profile_from_env(context, env_files=(".env.example",))
    registry.create_provider_profile(context, profile_data, source="user", user_confirmed=True)
    registry.issue_credential(
        context,
        provider_profile_id=profile_data["provider_profile_id"],
        credential_ref_id=profile_data["credential_ref_id"],
        secret_ref=secret_ref,
        source="user",
        user_confirmed=True,
    )
    provider_evidence = registry.validate_provider_smoke(
        context,
        provider_profile_id=profile_data["provider_profile_id"],
        capability_ref="llm.summarize",
        model_ref=profile_data["model_refs"][0],
        input_artifact_refs=["artifact://v4/ux12/input"],
        output_artifact_refs=["artifact://v4/ux12/summary"],
        prompt_template_ref="prompt-template://v5/provider-smoke",
        redacted_input_summary_ref="summary-ref://redacted/input",
        redacted_output_summary_ref="summary-ref://redacted/output",
        runtime_result_ref="runtime://v5/provider-smoke",
        source="user",
        user_confirmed=True,
    )
    log = SecurityEventLog()
    return log.record_event(
        context,
        event_type="provider.invocation.recorded",
        operation="provider.smoke.validate",
        target_refs={"provider_profile_id": profile_data["provider_profile_id"]},
        policy_decision="allow",
        source_refs={
            "evidence_ref": provider_evidence.provider_invocation_evidence_id,
            "runtime_result_ref": provider_evidence.runtime_result_ref,
        },
        metadata={
            "provider": provider_evidence.provider,
            "model_ref": provider_evidence.model_ref,
            "redacted_input_summary_ref": provider_evidence.redacted_input_summary_ref,
        },
        user_confirmed=True,
    )


def make_policy(context: IdentityContext | None = None) -> AuditRetentionPolicy:
    context = context or make_context()
    return AuditRetentionPolicy(
        retention_policy_id="retention_v5_3",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        evidence_type="provider_invocation",
        retention_days=90,
        legal_hold=False,
        export_allowed=True,
        redaction_required=True,
        owner_stage="V5-3",
    )
