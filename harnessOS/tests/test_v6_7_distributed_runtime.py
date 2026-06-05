from __future__ import annotations

import json
from pathlib import Path

from core.auth.tenant_boundary import IdentityContext
from core.policies.v6_controlled_executor_runtime import V6ExecutionScope, V6HumanAuthorization
from core.workflows.v6_7_distributed_runtime import (
    V67AgentWorkerRegistry,
    V67DistributedRunCoordinator,
    V67DistributedRunRequest,
    V67WorkerDescriptor,
    build_v67_observability_package,
    build_v67_runtime_report,
    seed_v67_workers,
)


SCHEMA_DIR = Path("docs/design/V6.x/schemas")


def make_context(*, actor_type: str = "human_user", tenant_id: str = "tenant_v6_7", actor_id: str = "user_v6_7") -> IdentityContext:
    return IdentityContext(
        tenant_id=tenant_id,
        workspace_id="workspace_v6_7",
        project_id="project_v6_7",
        app_id="app_v6_7",
        actor_type=actor_type,
        actor_id=actor_id,
        user_id=actor_id if actor_type == "human_user" else None,
        service_account_id=actor_id if actor_type == "service_account" else None,
        agent_id=actor_id if actor_type == "agent" else None,
        session_id="session_v6_7" if actor_type == "agent" else None,
        request_id=f"request_{actor_id}",
        correlation_id=f"correlation_{actor_id}",
    )


def make_authorization(context: IdentityContext, *, operations: tuple[str, ...] = ("workflow.instance.start",)) -> V6HumanAuthorization:
    return V6HumanAuthorization(
        human_authorization_ref="human-auth://v6-7/authorization",
        authorization_subject_actor_id=context.actor_id,
        authorization_created_at="2026-06-03T00:00:00+00:00",
        authorization_expires_at="2999-01-01T00:00:00+00:00",
        allowed_operations=operations,
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        authorizing_human_user_id=context.user_id or "user_v6_7",
        audit_ref="audit://v6-7/human-authorization",
    )


def make_request(
    context: IdentityContext,
    *,
    source: str = "product_console",
    branch_station_ids: dict[str, tuple[str, ...]] | None = None,
    completed_station_ids: tuple[str, ...] = (),
    station_dependencies: dict[str, tuple[str, ...]] | None = None,
    user_confirmed: bool = True,
    idempotency_key: str = "v6-7-start",
) -> V67DistributedRunRequest:
    return V67DistributedRunRequest(
        workflow_instance_id="workflow-instance-v6-7",
        source=source,
        actor_type=context.actor_type,
        target_scope=V6ExecutionScope.from_context(context),
        user_confirmed=user_confirmed,
        human_authorization=make_authorization(context),
        branch_station_ids=branch_station_ids or {"branch-script": ("writer_agent",), "branch-review": ("review_agent",)},
        evidence_source_refs=("docs/design/V6.x/evidence/v6-6-external-app-onboarding/acceptance-data.json",),
        idempotency_key=idempotency_key,
        correlation_id=context.correlation_id,
        request_id=context.request_id,
        completed_station_ids=completed_station_ids,
        station_dependencies=station_dependencies or {},
    )


def registry_with_workers(context: IdentityContext, count: int = 6) -> V67AgentWorkerRegistry:
    registry = V67AgentWorkerRegistry()
    seed_v67_workers(context, registry, count)
    return registry


def test_v6_7_schemas_parse_and_required_contract_fields_exist() -> None:
    schema_names = [
        "v6_7_agent_worker_registry_schema.json",
        "v6_7_worker_assignment_schema.json",
        "v6_7_distributed_state_checkpoint_schema.json",
        "v6_7_attempt_history_store_schema.json",
        "v6_7_artifact_lineage_service_schema.json",
        "v6_7_worker_recovery_decision_schema.json",
        "v6_7_incident_timeline_event_schema.json",
    ]
    for name in schema_names:
        schema = json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
        assert schema["additionalProperties"] is False

    worker_schema = json.loads((SCHEMA_DIR / "v6_7_agent_worker_registry_schema.json").read_text(encoding="utf-8"))
    assert {"project_id", "app_id"}.issubset(worker_schema["required"])
    assignment_schema = json.loads((SCHEMA_DIR / "v6_7_worker_assignment_schema.json").read_text(encoding="utf-8"))
    assert assignment_schema["properties"]["source"]["enum"] == ["product_console", "approved_api"]


def test_v6_7_worker_assignment_denies_source_agent_and_missing_confirmation() -> None:
    context = make_context()
    coordinator = V67DistributedRunCoordinator(registry=registry_with_workers(context))

    source_agent = coordinator.start_run(context, make_request(context, source="agent", idempotency_key="source-agent"))
    unconfirmed = coordinator.start_run(context, make_request(context, user_confirmed=False, idempotency_key="unconfirmed"))

    assert source_agent.status == "blocked"
    assert source_agent.blocked_reason == "source_agent_durable_mutation_denied"
    assert unconfirmed.status == "blocked"
    assert unconfirmed.blocked_reason == "missing_user_confirmation"


def test_v6_7_worker_wrong_tenant_and_missing_decisions_are_denied() -> None:
    context = make_context()
    wrong_registry = V67AgentWorkerRegistry()
    wrong_registry.register(
        V67WorkerDescriptor(
            worker_id="wrong-tenant-worker",
            tenant_id="tenant_other",
            workspace_id=context.workspace_id,
            project_id=context.project_id,
            app_id=context.app_id,
            worker_type="station_worker",
            explicit_tenant_binding=True,
            credential_decision_ref="credential-decision://v6-7/wrong",
            policy_decision_ref="policy-decision://v6-7/wrong",
        )
    )
    wrong_result = V67DistributedRunCoordinator(registry=wrong_registry).start_run(context, make_request(context))

    assert wrong_result.status == "blocked"
    assert wrong_result.blocked_reason == "worker_not_available_or_scope_denied"

    missing_decision_registry = V67AgentWorkerRegistry()
    try:
        missing_decision_registry.register(
            V67WorkerDescriptor(
                worker_id="missing-policy",
                tenant_id=context.tenant_id,
                workspace_id=context.workspace_id,
                project_id=context.project_id,
                app_id=context.app_id,
                worker_type="station_worker",
                explicit_tenant_binding=True,
                credential_decision_ref="credential-decision://v6-7/missing-policy",
                policy_decision_ref="",
            )
        )
    except ValueError as exc:
        assert getattr(exc, "reason") == "missing_worker_policy_decision"
    else:
        raise AssertionError("missing policy decision must be denied")


def test_v6_7_parallel_branch_states_are_independent_and_checkpointed() -> None:
    context = make_context()
    coordinator = V67DistributedRunCoordinator(registry=registry_with_workers(context))

    result = coordinator.start_run(context, make_request(context, branch_station_ids={"branch-a": ("a1", "a2"), "branch-b": ("b1", "b2")}))

    assert result.status == "started"
    assert result.run_state is not None
    assert result.run_state["branch_states"] == {"branch-a": "running", "branch-b": "running"}
    assert {checkpoint["branch_id"] for checkpoint in result.run_state["checkpoints"]} == {"branch-a", "branch-b"}
    assert {checkpoint["branch_state"] for checkpoint in result.run_state["checkpoints"]} == {"running"}


def test_v6_7_serial_station_dependency_blocks_downstream() -> None:
    context = make_context()
    coordinator = V67DistributedRunCoordinator(registry=registry_with_workers(context))

    result = coordinator.start_run(
        context,
        make_request(
            context,
            branch_station_ids={"serial": ("upstream", "downstream")},
            station_dependencies={"downstream": ("upstream",)},
            completed_station_ids=(),
        ),
    )

    assert result.status == "started"
    assert result.run_state is not None
    assert result.run_state["branch_states"]["serial"] == "waiting_dependency"
    assert "upstream" in result.run_state["assignments"]
    assert "downstream" not in result.run_state["assignments"]
    assert any(checkpoint["station_id"] == "downstream" and checkpoint["branch_state"] == "waiting_dependency" for checkpoint in result.run_state["checkpoints"])


def test_v6_7_lost_worker_recovery_retains_attempt_error_lineage_and_timeline() -> None:
    context = make_context()
    registry = registry_with_workers(context)
    coordinator = V67DistributedRunCoordinator(registry=registry)
    started = coordinator.start_run(context, make_request(context, branch_station_ids={"parallel": ("writer", "reviewer")}))
    assert started.distributed_run_id is not None

    recovered = coordinator.recover_worker(
        context,
        started.distributed_run_id,
        station_id="writer",
        failure_type="worker_lost",
        replacement_worker_id="worker_v6_7_3",
        recovery_strategy="retry_replacement_worker",
        idempotency_key="recover-writer",
    )

    assert recovered.status == "worker_recovered"
    assert recovered.run_state is not None
    attempts = recovered.run_state["station_attempts"]["writer"]
    assert len(attempts) == 2
    assert attempts[0]["status"] == "failed"
    assert attempts[0]["error_ref"].startswith("error-ref://v6-7/worker_lost/")
    assert attempts[1]["previous_attempt_id"] == attempts[0]["attempt_id"]
    assert attempts[1]["old_attempt_retained"] is True
    assert recovered.run_state["downstream_stale"] == ["downstream-of:writer"]
    assert any(lineage["producer_attempt_id"] == attempts[1]["attempt_id"] and lineage["previous_attempt_id"] == attempts[0]["attempt_id"] for lineage in recovered.run_state["artifact_lineage"].values())
    event_types = {event["event_type"] for event in recovered.run_state["incident_timeline"]}
    assert {"worker_lost", "retry_scheduled", "attempt_recovered", "artifact_lineage_recorded"}.issubset(event_types)

    replay = coordinator.recover_worker(
        context,
        started.distributed_run_id,
        station_id="writer",
        failure_type="worker_lost",
        replacement_worker_id="worker_v6_7_3",
        recovery_strategy="retry_replacement_worker",
        idempotency_key="recover-writer",
    )
    assert replay.status == "idempotent_recovery_replay"
    assert replay.evidence == recovered.evidence


def test_v6_7_report_and_observability_are_read_only_and_no_false_green() -> None:
    context = make_context()
    coordinator = V67DistributedRunCoordinator(registry=registry_with_workers(context))
    result = coordinator.start_run(context, make_request(context, branch_station_ids={"branch": ("writer", "reviewer")}))
    assert result.distributed_run_id is not None
    state = coordinator.store.load(result.distributed_run_id)

    report = build_v67_runtime_report(state)
    package = build_v67_observability_package(state)

    assert report["readonly"] is True
    assert report["report_actions"] == ["view", "export"]
    assert report["distributed_multi_agent_runtime_ready"] is False
    assert report["full_multi_agent_orchestration_ready"] is False
    assert report["agent_executor_ready"] is False
    assert package["readonly"] is True
    combined = json.dumps(package, ensure_ascii=False)
    for forbidden in ("raw_artifact_content", "raw prompt", "Authorization", "Bearer", "secret"):
        assert forbidden.lower() not in combined.lower()
