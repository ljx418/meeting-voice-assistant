from __future__ import annotations

from core.policies.production_controlled_executor_runtime import ExecutionScope
from core.workflows.v5_8_distributed_runtime import (
    AgentWorkerRegistry,
    ArtifactLineageService,
    AttemptHistoryStore,
    DistributedRunCoordinator,
    DistributedRunRequest,
    DistributedWorkerDescriptor,
    build_runtime_report_projection,
    read_v4_multi_agent_evidence_summary,
    seed_workers_for_stations,
)
from tests.v5_3_observability_support import make_context
from tests.v5_7b_runtime_support import make_human_authorization


def _coordinated_recovery_state():
    context = make_context()
    summary = read_v4_multi_agent_evidence_summary("UX-08-serial-video")
    station_ids = summary["station_ids"][:3]
    registry = AgentWorkerRegistry()
    seed_workers_for_stations(context, registry, station_ids)
    recovery_station = station_ids[1]
    registry.register(
        DistributedWorkerDescriptor.from_context(
            context,
            worker_id=f"worker_{recovery_station}_replacement",
            station_id=recovery_station,
            credential_decision_ref=f"credential-decision://v5-8c/{recovery_station}/replacement",
        )
    )
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
        idempotency_key="v5-8c-start",
        correlation_id=context.correlation_id,
        request_id=context.request_id,
    )
    started = coordinator.start_run(context, request)
    recovered = coordinator.recover_lost_worker(
        started.distributed_run_id or "",
        station_id=recovery_station,
        replacement_worker_id=f"worker_{recovery_station}_replacement",
    )
    return coordinator.store.load(recovered.distributed_run_id or ""), recovery_station


def test_v5_8c_attempt_history_is_append_only_after_worker_recovery() -> None:
    state, recovery_station = _coordinated_recovery_state()
    store = AttemptHistoryStore()

    store.ingest_state(state)
    store.ingest_state(state)

    history = store.to_dict()
    assert len(history[recovery_station]) == 2
    assert history[recovery_station][0]["attempt_number"] == 1
    assert history[recovery_station][1]["attempt_number"] == 2
    assert history[recovery_station][1]["previous_attempt_id"] == history[recovery_station][0]["attempt_id"]
    assert history[recovery_station][1]["recovery_reason"] == "worker_recovery"


def test_v5_8c_artifact_lineage_preserves_producer_attempt_after_recovery() -> None:
    state, recovery_station = _coordinated_recovery_state()
    lineage = ArtifactLineageService()

    lineage.ingest_state(state)
    records = lineage.to_dict()

    station_records = [record for record in records.values() if record["station_id"] == recovery_station]
    assert len(station_records) == 2
    assert any(record["lineage_status"] == "recovered" for record in station_records)
    recovered = next(record for record in station_records if record["lineage_status"] == "recovered")
    assert recovered["previous_attempt_id"]
    assert recovered["producer_worker_id"].endswith("_replacement")


def test_v5_8c_runtime_report_projection_is_read_only_and_links_attempt_lineage() -> None:
    state, recovery_station = _coordinated_recovery_state()
    attempts = AttemptHistoryStore()
    lineage = ArtifactLineageService()
    attempts.ingest_state(state)
    lineage.ingest_state(state)

    report = build_runtime_report_projection(state, attempts, lineage)

    assert report["readonly"] is True
    assert report["report_actions"] == ["view", "export"]
    assert report["production_ready"] is False
    assert report["attempt_history"][recovery_station][1]["recovery_reason"] == "worker_recovery"
    assert report["artifact_lineage"]
    assert report["source_refs"]
    assert report["redaction_status"] == "redacted"


def test_v5_8c_projection_does_not_expose_mutation_actions_or_sensitive_payloads() -> None:
    state, _recovery_station = _coordinated_recovery_state()
    attempts = AttemptHistoryStore()
    lineage = ArtifactLineageService()
    attempts.ingest_state(state)
    lineage.ingest_state(state)

    report = build_runtime_report_projection(state, attempts, lineage)
    combined = str(report)

    for forbidden_action in ["Apply", "Publish", "Approve", "Reject", "Execute", "Run"]:
        assert forbidden_action not in report["report_actions"]
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
