from __future__ import annotations

from core.auth.tenant_boundary import IdentityContext
from core.policies.production_controlled_executor_runtime import (
    ApprovedApiClient,
    ExecutionScope,
    HumanAuthorization,
    LimitedProductionControlledExecutorRuntime,
    ProductionExecutionRequest,
)
from tests.v5_3_observability_support import make_context

_DEFAULT_AUTHORIZATION = object()


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
) -> HumanAuthorization:
    return HumanAuthorization(
        human_authorization_ref="human-auth://v5-7b/authorization",
        authorization_subject_actor_id=context.actor_id,
        authorization_created_at="2026-01-01T00:00:00+00:00",
        authorization_expires_at=expires_at,
        allowed_operations=operations,
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        audit_ref="audit://v5-7b/human-authorization",
    )


def make_approved_api_client(context: IdentityContext, authorization: HumanAuthorization) -> ApprovedApiClient:
    return ApprovedApiClient(
        api_client_id="api-client-v5-7b",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        service_account_id=context.service_account_id or "svc_v5_3",
        human_authorization_ref=authorization.human_authorization_ref,
        allowed_operations=("workflow.instance.start", "station.rerun"),
        rate_limit_policy_ref="rate-limit://v5-7b/default",
        quota_policy_ref="quota://v5-7b/default",
    )


def make_runtime() -> LimitedProductionControlledExecutorRuntime:
    runtime = LimitedProductionControlledExecutorRuntime()
    runtime.seed_workflow(
        workflow_instance_id="workflow-instance-v5-7b",
        station_id="markdown_parse",
        station_run_id="station-run-v5-7b-1",
        failed=True,
    )
    return runtime


def make_request(
    context: IdentityContext | None = None,
    *,
    operation: str = "workflow.instance.start",
    source: str = "product_console",
    user_confirmed: bool = True,
    human_authorization: HumanAuthorization | None | object = _DEFAULT_AUTHORIZATION,
    approved_api_client: ApprovedApiClient | None = None,
    approval_gate_decision_ref: str | None = None,
    target_scope: ExecutionScope | None = None,
    target_refs: dict[str, str] | None = None,
    payload_refs: dict[str, str] | None = None,
    idempotency_key: str = "idempotency-v5-7b-1",
) -> ProductionExecutionRequest:
    context = context or make_context()
    authorization = make_human_authorization(context, operations=(operation,)) if human_authorization is _DEFAULT_AUTHORIZATION else human_authorization
    refs = target_refs or {"workflow_instance_id": "workflow-instance-v5-7b"}
    return ProductionExecutionRequest(
        operation=operation,
        source=source,
        actor_type=context.actor_type,
        target_refs=refs,
        user_confirmed=user_confirmed,
        human_authorization=authorization,
        target_scope=target_scope or ExecutionScope.from_context(context),
        idempotency_key=idempotency_key,
        correlation_id=context.correlation_id,
        request_id=context.request_id,
        approved_api_client=approved_api_client,
        approval_gate_decision_ref=approval_gate_decision_ref,
        payload_refs=payload_refs or {},
    )


def make_service_account_context() -> IdentityContext:
    return make_context(actor_type="service_account", actor_id="svc_v5_3")
