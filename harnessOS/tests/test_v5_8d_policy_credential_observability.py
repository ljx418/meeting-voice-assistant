from __future__ import annotations

from core.policies.production_controlled_executor_runtime import ExecutionScope
from core.workflows.v5_8_distributed_runtime import (
    AgentWorkerRegistry,
    ArtifactLineageService,
    AttemptHistoryStore,
    DistributedRunCoordinator,
    DistributedRunRequest,
    DistributedRuntimeCoordinationError,
    build_distributed_observability_package,
    build_policy_credential_decision,
    build_runtime_report_projection,
    read_v4_multi_agent_evidence_summary,
    seed_workers_for_stations,
)
from tests.v5_3_observability_support import make_context
from tests.v5_7b_runtime_support import make_human_authorization


def _state_registry_report():
    context = make_context()
    summary = read_v4_multi_agent_evidence_summary("UX-09-parallel-deliberation")
    station_ids = summary["station_ids"][:3]
    registry = AgentWorkerRegistry()
    seed_workers_for_stations(context, registry, station_ids)
    coordinator = DistributedRunCoordinator(registry=registry)
    request = DistributedRunRequest(
        workflow_instance_id=summary["workflow_instance_id"],
        source="product_console",
        actor_type=context.actor_type,
        target_scope=ExecutionScope.from_context(context),
        user_confirmed=True,
        human_authorization=make_human_authorization(context, operations=("workflow.instance.start",)),
        station_ids=station_ids,
        evidence_source_refs=(summary["result_path"], summary["summary_path"]),
        idempotency_key="v5-8d-start",
        correlation_id=context.correlation_id,
        request_id=context.request_id,
    )
    started = coordinator.start_run(context, request)
    state = coordinator.store.load(started.distributed_run_id or "")
    attempts = AttemptHistoryStore()
    lineage = ArtifactLineageService()
    attempts.ingest_state(state)
    lineage.ingest_state(state)
    report = build_runtime_report_projection(state, attempts, lineage)
    return state, registry, report


def test_v5_8d_policy_credential_decision_requires_worker_credential_refs() -> None:
    state, registry, _report = _state_registry_report()

    decision = build_policy_credential_decision(state, registry).to_dict()

    assert decision["policy_decision"] == "allow_distributed_projection_only"
    assert decision["credential_boundary_decision"] == "all_assigned_workers_have_credential_decision_refs"
    assert decision["worker_credential_refs"]
    assert decision["source_agent_can_mutate"] is False
    assert decision["unrestricted_connector_call_allowed"] is False
    assert decision["unrestricted_external_llm_call_allowed"] is False


def test_v5_8d_policy_credential_decision_denies_missing_worker_credential_ref() -> None:
    state, registry, _report = _state_registry_report()
    first_worker_id = next(iter(registry.workers))
    worker = registry.workers[first_worker_id]
    registry.workers[first_worker_id] = type(worker)(
        worker_id=worker.worker_id,
        tenant_id=worker.tenant_id,
        workspace_id=worker.workspace_id,
        project_id=worker.project_id,
        app_id=worker.app_id,
        station_id=worker.station_id,
        credential_decision_ref="",
    )

    try:
        build_policy_credential_decision(state, registry)
    except DistributedRuntimeCoordinationError as exc:
        assert exc.reason == "missing_worker_credential_decision"
    else:
        raise AssertionError("missing worker credential decision should be denied")


def test_v5_8d_observability_package_is_read_only_and_records_audit_refs() -> None:
    state, registry, report = _state_registry_report()
    decision = build_policy_credential_decision(state, registry)

    package = build_distributed_observability_package(state, report, decision)

    assert package["readonly"] is True
    assert package["report_actions"] == ["view", "export"]
    assert package["production_ready"] is False
    assert package["policy_credential_decision"]["decision_id"] == decision.decision_id
    assert len(package["audit_events"]) >= 2
    assert package["metrics"]["assigned_worker_count"] == len(state.assignments)
    assert package["redaction_status"] == "redacted"


def test_v5_8d_observability_package_redacts_sensitive_terms() -> None:
    state, registry, report = _state_registry_report()
    decision = build_policy_credential_decision(state, registry)
    package = build_distributed_observability_package(state, report, decision)
    combined = str(package)

    for forbidden in [
        "capability_token",
        "subscription_token",
        "Authorization",
        "Bearer",
        "raw_trace_payload",
        "raw_artifact_content",
        "raw_connector_payload",
        "raw prompt",
        "upstream signed URL",
    ]:
        assert forbidden not in combined
