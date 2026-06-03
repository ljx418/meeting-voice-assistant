from __future__ import annotations

import pytest

from core.auth.tenant_boundary import (
    ResourceRef,
    TenantBoundaryError,
    build_denial_audit_event,
    resolve_identity_context,
    validate_resource_access,
)


SERVER_CONTEXT = {
    "tenant_id": "tenant_alpha",
    "workspace_id": "workspace_docs",
    "project_id": "project_v5",
    "app_id": "app_workflow",
    "actor_type": "human_user",
    "actor_id": "actor_user_1",
    "user_id": "user_1",
    "request_id": "req_v5_1",
    "correlation_id": "corr_v5_1",
}


def resource(**overrides: str) -> ResourceRef:
    data = {
        "resource_type": "workflow_instance",
        "resource_id": "wfi_1",
        "tenant_id": "tenant_alpha",
        "workspace_id": "workspace_docs",
        "project_id": "project_v5",
        "app_id": "app_workflow",
        "owner_ref": "owner_1",
        "workflow_instance_id": "wfi_1",
    }
    data.update(overrides)
    return ResourceRef(**data)


def test_client_supplied_tenant_cannot_override_server_bound_identity() -> None:
    with pytest.raises(TenantBoundaryError) as exc:
        resolve_identity_context(SERVER_CONTEXT, {"tenant_id": "tenant_beta"})

    assert exc.value.code == "TENANT_SCOPE_DENIED"
    assert exc.value.to_error()["data"]["reason"] == "tenant_id_mismatch"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("tenant_id", "tenant_beta", "TENANT_SCOPE_DENIED"),
        ("workspace_id", "workspace_other", "WORKSPACE_SCOPE_DENIED"),
        ("project_id", "project_other", "PROJECT_SCOPE_DENIED"),
        ("app_id", "app_other", "APP_SCOPE_DENIED"),
    ],
)
def test_scope_mismatches_are_denied_with_stable_errors(field: str, value: str, code: str) -> None:
    context = resolve_identity_context(SERVER_CONTEXT)

    with pytest.raises(TenantBoundaryError) as exc:
        validate_resource_access(context, resource(**{field: value}), operation="evidence.show")

    assert exc.value.code == code


def test_service_account_outside_bound_scope_is_denied() -> None:
    context = resolve_identity_context(
        {
            **SERVER_CONTEXT,
            "actor_type": "service_account",
            "actor_id": "actor_sa_1",
            "user_id": None,
            "service_account_id": "sa_1",
        }
    )

    with pytest.raises(TenantBoundaryError) as exc:
        validate_resource_access(context, resource(workspace_id="workspace_other"), operation="report.open")

    assert exc.value.code == "WORKSPACE_SCOPE_DENIED"


def test_agent_identity_is_not_executor_identity_for_durable_mutation() -> None:
    context = resolve_identity_context(
        {
            **SERVER_CONTEXT,
            "actor_type": "agent",
            "actor_id": "actor_agent_1",
            "user_id": None,
            "agent_id": "agent_builder",
            "session_id": "agent_session_1",
        }
    )

    with pytest.raises(TenantBoundaryError) as exc:
        validate_resource_access(
            context,
            resource(agent_session_id="agent_session_1"),
            operation="workflow.instance.start",
            source="agent",
            user_confirmed=True,
        )

    assert exc.value.code == "AGENT_EXECUTION_DENIED"


def test_durable_mutation_requires_user_confirmation() -> None:
    context = resolve_identity_context(SERVER_CONTEXT)

    with pytest.raises(TenantBoundaryError) as exc:
        validate_resource_access(context, resource(), operation="workflow.instance.start", source="user")

    assert exc.value.code == "USER_CONFIRMATION_REQUIRED"


def test_valid_scoped_access_returns_audit_event_with_required_refs() -> None:
    context = resolve_identity_context(SERVER_CONTEXT)

    audit = validate_resource_access(context, resource(), operation="workflow.instance.start", source="user", user_confirmed=True)

    assert audit["policy_decision"] == "allow"
    assert audit["scope_decision"] == "allow"
    assert audit["tenant_id"] == "tenant_alpha"
    assert audit["workspace_id"] == "workspace_docs"
    assert audit["project_id"] == "project_v5"
    assert audit["app_id"] == "app_workflow"
    assert audit["actor_type"] == "human_user"
    assert audit["actor_id"] == "actor_user_1"
    assert audit["target_resource_type"] == "workflow_instance"
    assert audit["target_resource_id"] == "wfi_1"
    assert audit["request_id"] == "req_v5_1"
    assert audit["correlation_id"] == "corr_v5_1"
    assert audit["redaction_status"] == "redacted"


def test_denial_audit_event_redacts_sensitive_metadata() -> None:
    context = resolve_identity_context(SERVER_CONTEXT)
    target = resource(tenant_id="tenant_beta")
    try:
        validate_resource_access(context, target, operation="evidence.show")
    except TenantBoundaryError as error:
        audit = build_denial_audit_event(context, operation="evidence.show", target=target, error=error)
    else:
        raise AssertionError("expected denial")

    assert audit["policy_decision"] == "deny"
    assert audit["scope_decision"] == "deny"
    assert audit["denial_reason"] == "tenant_mismatch"
    assert audit["risk_flags"] == ["tenant_mismatch"]
    assert "capability_token" not in str(audit)
    assert "Authorization" not in str(audit)
