from __future__ import annotations

import pytest

from core.auth.production_identity_tenant import (
    ServiceAccountScope,
    resolve_staging_identity_provider_status,
    validate_v6_1_identity_tenant_access,
)
from core.auth.tenant_boundary import ResourceRef, TenantBoundaryError


SERVER_CONTEXT = {
    "tenant_id": "tenant_alpha",
    "workspace_id": "workspace_docs",
    "project_id": "project_v6",
    "app_id": "app_workflow",
    "actor_type": "human_user",
    "actor_id": "actor_user_1",
    "user_id": "user_1",
    "request_id": "req_v6_1",
    "correlation_id": "corr_v6_1",
}


def resource(**overrides: str) -> ResourceRef:
    data = {
        "resource_type": "workflow_instance",
        "resource_id": "wfi_v6_1",
        "tenant_id": "tenant_alpha",
        "workspace_id": "workspace_docs",
        "project_id": "project_v6",
        "app_id": "app_workflow",
        "owner_ref": "owner_1",
        "workflow_instance_id": "wfi_v6_1",
    }
    data.update(overrides)
    return ResourceRef(**data)


def service_scope(**overrides: object) -> ServiceAccountScope:
    data = {
        "service_account_id": "sa_report_reader",
        "tenant_id": "tenant_alpha",
        "workspace_id": "workspace_docs",
        "project_id": "project_v6",
        "app_id": "app_workflow",
        "allowed_operations": ("report.open", "evidence.show"),
        "audit_ref": "audit://sa_report_reader",
    }
    data.update(overrides)
    return ServiceAccountScope(**data)


def test_v6_1_staging_identity_provider_status_defaults_to_staging_only() -> None:
    status = resolve_staging_identity_provider_status({})

    assert status.status == "staging_only"
    assert status.evidence_scope == "staging_fixture"
    assert status.enterprise_auth_ready is False


def test_v6_1_valid_human_access_projects_identity_to_all_heads() -> None:
    audit = validate_v6_1_identity_tenant_access(
        SERVER_CONTEXT,
        resource(),
        operation="report.open",
        metadata={"Authorization": "Bearer secret", "safe": "ok"},
    )

    assert audit["policy_decision"] == "allow"
    assert audit["tenant_id"] == "tenant_alpha"
    assert audit["identity_provider_status"] == "staging_only"
    assert audit["enterprise_auth_ready"] is False
    assert set(audit["workflow_head_refs"]) == {
        "mission_console",
        "workflow_blueprint",
        "runtime_report",
        "review_console",
        "evidence_chain",
        "workflow_spec_registry",
    }
    assert audit["workflow_head_refs"]["runtime_report"]["tenant_id"] == "tenant_alpha"
    assert "Bearer secret" not in str(audit)


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("tenant_id", "tenant_beta", "TENANT_SCOPE_DENIED"),
        ("workspace_id", "workspace_other", "WORKSPACE_SCOPE_DENIED"),
        ("project_id", "project_other", "PROJECT_SCOPE_DENIED"),
        ("app_id", "app_other", "APP_SCOPE_DENIED"),
    ],
)
def test_v6_1_scope_mismatch_denied(field: str, value: str, code: str) -> None:
    with pytest.raises(TenantBoundaryError) as exc:
        validate_v6_1_identity_tenant_access(SERVER_CONTEXT, resource(**{field: value}), operation="report.open")

    assert exc.value.code == code


def test_v6_1_service_account_missing_binding_denied() -> None:
    context = {
        **SERVER_CONTEXT,
        "actor_type": "service_account",
        "actor_id": "actor_sa",
        "user_id": None,
        "service_account_id": "sa_report_reader",
    }

    with pytest.raises(TenantBoundaryError) as exc:
        validate_v6_1_identity_tenant_access(context, resource(), operation="report.open")

    assert exc.value.code == "SERVICE_ACCOUNT_SCOPE_DENIED"
    assert exc.value.reason == "missing_service_account_scope"


def test_v6_1_service_account_wrong_operation_denied() -> None:
    context = {
        **SERVER_CONTEXT,
        "actor_type": "service_account",
        "actor_id": "actor_sa",
        "user_id": None,
        "service_account_id": "sa_report_reader",
    }

    with pytest.raises(TenantBoundaryError) as exc:
        validate_v6_1_identity_tenant_access(context, resource(), operation="workflow.instance.start", service_account_scope=service_scope())

    assert exc.value.code == "SERVICE_ACCOUNT_OPERATION_DENIED"


def test_v6_1_service_account_valid_operation_allowed() -> None:
    context = {
        **SERVER_CONTEXT,
        "actor_type": "service_account",
        "actor_id": "actor_sa",
        "user_id": None,
        "service_account_id": "sa_report_reader",
    }

    audit = validate_v6_1_identity_tenant_access(context, resource(), operation="report.open", service_account_scope=service_scope())

    assert audit["service_account_scope_decision"] == "allow"
    assert audit["service_account_id"] == "sa_report_reader"
    assert audit["service_account_audit_ref"] == "audit://sa_report_reader"


def test_v6_1_source_agent_durable_mutation_denied() -> None:
    context = {
        **SERVER_CONTEXT,
        "actor_type": "agent",
        "actor_id": "actor_agent",
        "user_id": None,
        "agent_id": "agent_builder",
        "session_id": "agent_session",
    }

    with pytest.raises(TenantBoundaryError) as exc:
        validate_v6_1_identity_tenant_access(
            context,
            resource(agent_session_id="agent_session"),
            operation="workflow.instance.start",
            source="agent",
            user_confirmed=True,
        )

    assert exc.value.code == "AGENT_EXECUTION_DENIED"


def test_v6_1_configured_oidc_records_redacted_refs_not_enterprise_ready() -> None:
    status = resolve_staging_identity_provider_status(
        {
            "V6_1_IDENTITY_PROVIDER": "oidc_fixture",
            "V6_1_OIDC_ISSUER": "https://idp.example.test/tenant_alpha",
            "V6_1_OIDC_CLIENT_ID": "client-v6-1-alpha",
        }
    )

    assert status.status == "staging_real"
    assert status.enterprise_auth_ready is False
    assert "idp.example.test" not in str(status.to_audit_fields())
