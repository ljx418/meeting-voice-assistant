from __future__ import annotations

from core.auth.tenant_boundary import IdentityContext
from core.policies.v6_controlled_executor_runtime import (
    V6ApprovedApiClient,
    V6ControlledExecutionRequest,
    V6ExecutionScope,
    V6HumanAuthorization,
    V6LimitedProductionControlledExecutorRuntime,
)


def make_context(*, actor_type: str = "human_user", actor_id: str = "user_v6_4") -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v6",
        workspace_id="workspace_v6",
        project_id="project_v6",
        app_id="app_v6",
        actor_type=actor_type,
        actor_id=actor_id,
        user_id="user_v6_4" if actor_type == "human_user" else None,
        service_account_id="svc_v6_4" if actor_type == "service_account" else None,
        agent_id="agent_v6_4" if actor_type == "agent" else None,
        session_id="session_v6_4" if actor_type == "agent" else None,
        request_id="request_v6_4",
        correlation_id="correlation_v6_4",
    )


def make_human_authorization(
    context: IdentityContext,
    *,
    operations: tuple[str, ...] = (
        "workflow.instance.start",
        "station.rerun",
        "artifact.write",
        "quality.evaluation.create",
    ),
    expires_at: str = "2999-01-01T00:00:00+00:00",
) -> V6HumanAuthorization:
    return V6HumanAuthorization(
        human_authorization_ref="human-auth://v6-4/authorization",
        authorization_subject_actor_id="user_v6_4",
        authorization_created_at="2026-01-01T00:00:00+00:00",
        authorization_expires_at=expires_at,
        allowed_operations=operations,
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        authorizing_human_user_id="user_v6_4",
        audit_ref="audit://v6-4/human-authorization",
    )


def make_approved_api_client(context: IdentityContext, authorization: V6HumanAuthorization) -> V6ApprovedApiClient:
    return V6ApprovedApiClient(
        api_client_id="api-client-v6-4",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        service_account_id=context.service_account_id or "svc_v6_4",
        human_authorization_ref=authorization.human_authorization_ref,
        allowed_operations=("workflow.instance.start", "station.rerun"),
        rate_limit_policy_ref="rate-limit://v6-4/default",
        quota_policy_ref="quota://v6-4/default",
    )


def make_runtime(context: IdentityContext | None = None) -> V6LimitedProductionControlledExecutorRuntime:
    context = context or make_context()
    runtime = V6LimitedProductionControlledExecutorRuntime()
    runtime.seed_workflow(
        context,
        workflow_instance_id="workflow-instance-v6-4",
        station_id="markdown_parse",
        station_run_id="station-run-v6-4-1",
        failed=True,
    )
    return runtime


def make_request(
    context: IdentityContext | None = None,
    *,
    operation: str = "workflow.instance.start",
    source: str = "product_console",
    actor_type: str | None = None,
    user_confirmed: bool = True,
    human_authorization: V6HumanAuthorization | None | object = object(),
    approved_api_client: V6ApprovedApiClient | None = None,
    approval_gate_decision_ref: str | None = None,
    target_refs: dict[str, str] | None = None,
    payload_refs: dict[str, str] | None = None,
    idempotency_key: str = "idempotency-v6-4-1",
) -> V6ControlledExecutionRequest:
    context = context or make_context()
    authorization = make_human_authorization(context, operations=(operation,)) if not isinstance(human_authorization, V6HumanAuthorization) and human_authorization is not None else human_authorization
    refs = target_refs or {"workflow_instance_id": "workflow-instance-v6-4"}
    return V6ControlledExecutionRequest(
        operation=operation,
        source=source,
        actor_type=actor_type or ("service_account_with_human_authorization" if context.actor_type == "service_account" else context.actor_type),
        target_refs=refs,
        user_confirmed=user_confirmed,
        human_authorization=authorization if isinstance(authorization, V6HumanAuthorization) else None,
        target_scope=V6ExecutionScope.from_context(context),
        idempotency_key=idempotency_key,
        correlation_id=context.correlation_id,
        request_id=context.request_id,
        approved_api_client=approved_api_client,
        approval_gate_decision_ref=approval_gate_decision_ref,
        payload_refs=payload_refs or {},
    )


def test_workflow_start_records_v6_4_evidence_and_audit_event() -> None:
    context = make_context()
    runtime = make_runtime(context)

    result = runtime.execute(context, make_request(context, idempotency_key="start-1")).to_dict()

    assert result["status"] == "applied_limited_runtime_slice"
    assert result["workflow_state"]["status"] == "running"
    assert result["evidence"]["operation"] == "workflow.instance.start"
    assert result["evidence"]["capability_decision"] == "allow_limited_production_pilot_slice"
    assert result["evidence"]["incident_timeline_ref"].startswith("incident-timeline://")
    assert result["audit_event_ref"].startswith("audit-event://")
    assert result["production_ready"] is False


def test_source_agent_is_denied_before_runtime_state_changes() -> None:
    context = make_context(actor_type="agent", actor_id="agent_v6_4")
    runtime = make_runtime(make_context())

    result = runtime.execute(
        context,
        make_request(context, source="agent", actor_type="agent", idempotency_key="agent-denied"),
    ).to_dict()

    assert result["status"] == "blocked"
    assert result["blocked_reason"] == "source_agent_durable_mutation_denied"
    assert runtime.evidence == []


def test_approved_api_requires_matching_human_authorization_and_service_account() -> None:
    context = make_context(actor_type="service_account", actor_id="svc_v6_4")
    authorization = make_human_authorization(context, operations=("workflow.instance.start",))
    client = make_approved_api_client(context, authorization)
    runtime = make_runtime(context)

    allowed = runtime.execute(
        context,
        make_request(
            context,
            source="approved_api",
            human_authorization=authorization,
            approved_api_client=client,
            idempotency_key="approved-api-allowed",
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
    assert allowed["evidence"]["actor_type"] == "service_account_with_human_authorization"
    assert missing_auth["blocked_reason"] == "missing_human_authorization"


def test_service_account_wrong_operation_and_expired_authorization_are_denied() -> None:
    context = make_context(actor_type="service_account", actor_id="svc_v6_4")
    runtime = make_runtime(context)
    wrong_operation_auth = make_human_authorization(context, operations=("workflow.instance.start",))
    expired_auth = make_human_authorization(context, operations=("station.rerun",), expires_at="2020-01-01T00:00:00+00:00")
    rerun_refs = {"workflow_instance_id": "workflow-instance-v6-4", "station_id": "markdown_parse", "station_run_id": "station-run-v6-4-1"}

    wrong_operation = runtime.execute(
        context,
        make_request(context, operation="station.rerun", target_refs=rerun_refs, human_authorization=wrong_operation_auth, idempotency_key="svc-wrong-op"),
    ).to_dict()
    expired = runtime.execute(
        context,
        make_request(context, operation="station.rerun", target_refs=rerun_refs, human_authorization=expired_auth, idempotency_key="svc-expired"),
    ).to_dict()

    assert wrong_operation["blocked_reason"] == "human_authorization_invalid"
    assert expired["blocked_reason"] == "human_authorization_invalid"


def test_station_rerun_retains_old_attempt_creates_new_attempt_and_marks_stale() -> None:
    context = make_context()
    runtime = make_runtime(context)
    refs = {"workflow_instance_id": "workflow-instance-v6-4", "station_id": "markdown_parse", "station_run_id": "station-run-v6-4-1"}

    result = runtime.execute(context, make_request(context, operation="station.rerun", target_refs=refs, idempotency_key="rerun-1")).to_dict()
    attempts = result["workflow_state"]["station_attempts"]["markdown_parse"]

    assert [attempt["status"] for attempt in attempts] == ["failed", "completed"]
    assert attempts[0]["station_run_id"] == "station-run-v6-4-1"
    assert attempts[1]["attempt_number"] == 2
    assert result["workflow_state"]["downstream_stale"] == ["downstream-of:markdown_parse"]


def test_artifact_write_and_quality_evaluation_are_approval_gated_and_append_only() -> None:
    context = make_context()
    runtime = make_runtime(context)
    artifact_refs = {"workflow_instance_id": "workflow-instance-v6-4", "artifact_id": "artifact-summary-v1", "station_id": "markdown_parse"}
    quality_refs = {"workflow_instance_id": "workflow-instance-v6-4", "quality_evaluation_id": "quality-eval-v1", "artifact_id": "artifact-summary-v1"}

    artifact_blocked = runtime.execute(context, make_request(context, operation="artifact.write", target_refs=artifact_refs, idempotency_key="artifact-blocked")).to_dict()
    artifact_allowed = runtime.execute(
        context,
        make_request(
            context,
            operation="artifact.write",
            target_refs=artifact_refs,
            payload_refs={"content_ref": "artifact-content-ref://summary/v2"},
            approval_gate_decision_ref="approval-gate://v6-4/artifact-write",
            idempotency_key="artifact-allowed",
        ),
    ).to_dict()
    quality_allowed = runtime.execute(
        context,
        make_request(
            context,
            operation="quality.evaluation.create",
            target_refs=quality_refs,
            payload_refs={"quality_rule_ref": "quality-rule://summary", "score_ref": "quality-score-ref://summary-v1"},
            approval_gate_decision_ref="approval-gate://v6-4/quality",
            idempotency_key="quality-allowed",
        ),
    ).to_dict()

    assert artifact_blocked["blocked_reason"] == "approval_gate_required"
    assert artifact_allowed["workflow_state"]["artifact_versions"]["artifact-summary-v1"][0]["operation"] == "append_version"
    assert quality_allowed["workflow_state"]["quality_evaluations"][0]["operation"] == "append_evaluation"


def test_kill_switch_and_idempotency_guards() -> None:
    context = make_context()
    runtime = make_runtime(context)
    request = make_request(context, idempotency_key="idempotent-start")

    first = runtime.execute(context, request).to_dict()
    second = runtime.execute(context, request).to_dict()
    runtime_with_kill_switch = make_runtime(context)
    runtime_with_kill_switch.disable_workspace(context.workspace_id)
    denied = runtime_with_kill_switch.execute(context, make_request(context, idempotency_key="kill-switch")).to_dict()

    assert second["status"] == "idempotent_replay"
    assert second["runtime_result_ref"] == first["runtime_result_ref"]
    assert denied["blocked_reason"] == "workspace_kill_switch_active"
    assert runtime_with_kill_switch.evidence == []


def test_excluded_actions_and_raw_payload_are_denied() -> None:
    context = make_context()
    runtime = make_runtime(context)

    for index, operation in enumerate(["business.event.emit", "context.update", "workflow.template.publish", "approval.respond", "connector.call", "external_llm.call"]):
        result = runtime.execute(
            context,
            make_request(
                context,
                operation=operation,
                human_authorization=make_human_authorization(context, operations=(operation,)),
                idempotency_key=f"excluded-{index}",
            ),
        ).to_dict()
        assert result["blocked_reason"] == "operation_not_allowed"

    raw = runtime.execute(
        context,
        make_request(
            context,
            operation="artifact.write",
            target_refs={"workflow_instance_id": "workflow-instance-v6-4", "artifact_id": "artifact-summary-v1"},
            payload_refs={"raw_artifact_content": "do not allow raw content"},
            approval_gate_decision_ref="approval-gate://v6-4/artifact-write",
            idempotency_key="raw-denied",
        ),
    ).to_dict()
    assert raw["blocked_reason"] == "redaction_failed"
