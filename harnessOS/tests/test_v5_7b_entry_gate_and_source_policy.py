from __future__ import annotations

from core.policies.production_controlled_executor_runtime import ExecutionScope
from tests.v5_3_observability_support import make_context
from tests.v5_7b_runtime_support import make_approved_api_client, make_human_authorization, make_request, make_runtime, make_service_account_context


def test_product_console_workflow_start_requires_human_confirmation_and_authorization() -> None:
    context = make_context()
    runtime = make_runtime()

    missing_confirmation = runtime.execute(context, make_request(context, user_confirmed=False)).to_dict()
    missing_authorization = runtime.execute(context, make_request(context, human_authorization=None)).to_dict()

    assert missing_confirmation["status"] == "blocked"
    assert missing_confirmation["blocked_reason"] == "missing_user_confirmation"
    assert missing_authorization["status"] == "blocked"
    assert missing_authorization["blocked_reason"] == "missing_human_authorization"


def test_source_agent_and_agent_actor_are_denied_before_runtime_state_changes() -> None:
    agent_context = make_context(actor_type="agent", actor_id="agent_v5_7b")
    runtime = make_runtime()

    result = runtime.execute(
        agent_context,
        make_request(agent_context, source="agent", idempotency_key="agent-denied"),
    ).to_dict()

    assert result["status"] == "blocked"
    assert result["blocked_reason"] == "source_agent_durable_mutation_denied"
    assert runtime.evidence == []


def test_wrong_tenant_and_workspace_are_denied() -> None:
    context = make_context()
    runtime = make_runtime()
    wrong_tenant = ExecutionScope(
        tenant_id="tenant_other",
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
    )
    wrong_workspace = ExecutionScope(
        tenant_id=context.tenant_id,
        workspace_id="workspace_other",
        project_id=context.project_id,
        app_id=context.app_id,
    )

    tenant_result = runtime.execute(context, make_request(context, target_scope=wrong_tenant, idempotency_key="wrong-tenant")).to_dict()
    workspace_result = runtime.execute(context, make_request(context, target_scope=wrong_workspace, idempotency_key="wrong-workspace")).to_dict()

    assert tenant_result["blocked_reason"] == "tenant_mismatch"
    assert workspace_result["blocked_reason"] == "workspace_mismatch"


def test_approved_api_requires_service_account_and_matching_human_authorization() -> None:
    context = make_service_account_context()
    authorization = make_human_authorization(context, operations=("workflow.instance.start",))
    client = make_approved_api_client(context, authorization)
    runtime = make_runtime()

    allowed = runtime.execute(
        context,
        make_request(
            context,
            source="approved_api",
            human_authorization=authorization,
            approved_api_client=client,
            idempotency_key="approved-api-start",
        ),
    ).to_dict()
    missing_auth = runtime.execute(
        context,
        make_request(
            context,
            source="approved_api",
            human_authorization=None,
            approved_api_client=client,
            idempotency_key="approved-api-missing-auth",
        ),
    ).to_dict()

    assert allowed["status"] == "applied_limited_runtime_slice"
    assert allowed["evidence"]["source"] == "approved_api"
    assert allowed["evidence"]["human_authorization_ref"] == authorization.human_authorization_ref
    assert missing_auth["status"] == "blocked"
    assert missing_auth["blocked_reason"] == "missing_human_authorization"


def test_approved_api_wrong_workspace_and_source_agent_are_denied() -> None:
    context = make_service_account_context()
    authorization = make_human_authorization(context, operations=("workflow.instance.start",))
    wrong_client = make_approved_api_client(context, authorization)
    wrong_client = type(wrong_client)(**{**wrong_client.to_dict(), "workspace_id": "workspace_other"})
    runtime = make_runtime()

    wrong_workspace = runtime.execute(
        context,
        make_request(
            context,
            source="approved_api",
            human_authorization=authorization,
            approved_api_client=wrong_client,
            idempotency_key="approved-api-wrong-workspace",
        ),
    ).to_dict()
    agent_context = make_context(actor_type="agent", actor_id="agent_v5_7b")
    agent_source = runtime.execute(agent_context, make_request(agent_context, source="agent", idempotency_key="approved-api-agent")).to_dict()

    assert wrong_workspace["blocked_reason"] == "approved_api_wrong_workspace"
    assert agent_source["blocked_reason"] == "source_agent_durable_mutation_denied"


def test_service_account_with_human_authorization_is_not_agent_executor_or_admin_override() -> None:
    context = make_service_account_context()
    authorization = make_human_authorization(context, operations=("workflow.instance.start",))
    runtime = make_runtime()

    allowed = runtime.execute(context, make_request(context, human_authorization=authorization, idempotency_key="svc-start")).to_dict()
    expired = runtime.execute(
        context,
        make_request(
            context,
            human_authorization=make_human_authorization(context, operations=("workflow.instance.start",), expires_at="2020-01-01T00:00:00+00:00"),
            idempotency_key="svc-expired",
        ),
    ).to_dict()
    wrong_operation = runtime.execute(
        context,
        make_request(
            context,
            operation="station.rerun",
            target_refs={"workflow_instance_id": "workflow-instance-v5-7b", "station_id": "markdown_parse", "station_run_id": "station-run-v5-7b-1"},
            human_authorization=authorization,
            idempotency_key="svc-wrong-op",
        ),
    ).to_dict()

    assert allowed["status"] == "applied_limited_runtime_slice"
    assert allowed["evidence"]["actor_type"] == "service_account"
    assert expired["blocked_reason"] == "human_authorization_invalid"
    assert wrong_operation["blocked_reason"] == "human_authorization_invalid"
