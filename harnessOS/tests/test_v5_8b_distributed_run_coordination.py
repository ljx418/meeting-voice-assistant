from __future__ import annotations

from core.policies.production_controlled_executor_runtime import ExecutionScope
from core.workflows.v5_8_distributed_runtime import (
    AgentWorkerRegistry,
    DistributedRunCoordinator,
    DistributedRunRequest,
    DistributedWorkerDescriptor,
    read_v4_multi_agent_evidence_summary,
    seed_workers_for_stations,
)
from tests.v5_3_observability_support import make_context
from tests.v5_7b_runtime_support import make_human_authorization


def make_request_for_summary(context, summary, *, source: str = "product_console", user_confirmed: bool = True) -> DistributedRunRequest:
    return DistributedRunRequest(
        workflow_instance_id=summary["workflow_instance_id"],
        source=source,
        actor_type=context.actor_type,
        target_scope=ExecutionScope.from_context(context),
        user_confirmed=user_confirmed,
        human_authorization=make_human_authorization(context, operations=("workflow.instance.start",)),
        station_ids=summary["station_ids"][:3],
        evidence_source_refs=(summary["result_path"], summary["summary_path"]),
        idempotency_key="v5-8b-start",
        correlation_id=context.correlation_id,
        request_id=context.request_id,
    )


def test_v5_8b_reads_existing_real_multi_agent_evidence_as_input() -> None:
    summary = read_v4_multi_agent_evidence_summary("UX-08-serial-video")

    assert summary["runtime_backed"] is True
    assert summary["real_provider_backed"] is True
    assert summary["provider"] == "minimax"
    assert summary["provider_invocation_count"] >= len(summary["station_ids"])
    assert "writer_agent" in summary["station_ids"]


def test_v5_8b_coordinates_worker_assignment_from_real_evidence() -> None:
    context = make_context()
    summary = read_v4_multi_agent_evidence_summary("UX-08-serial-video")
    registry = AgentWorkerRegistry()
    seed_workers_for_stations(context, registry, summary["station_ids"][:3])
    coordinator = DistributedRunCoordinator(registry=registry)

    result = coordinator.start_run(context, make_request_for_summary(context, summary))

    assert result.status == "coordinated"
    assert result.run_state is not None
    assert result.evidence is not None
    assert result.run_state["status"] == "running"
    assert result.run_state["staging_only"] is True
    assert result.run_state["production_ready"] is False
    assert set(result.run_state["assignments"]) == set(summary["station_ids"][:3])
    assert result.evidence["policy_decision"] == "allow_minimal_coordination_slice"
    assert result.evidence["credential_boundary_decision"] == "worker_credential_decision_refs_required"


def test_v5_8b_coordinator_restart_recovers_persisted_run_state() -> None:
    context = make_context()
    summary = read_v4_multi_agent_evidence_summary("UX-09-parallel-deliberation")
    registry = AgentWorkerRegistry()
    seed_workers_for_stations(context, registry, summary["station_ids"][:3])
    coordinator = DistributedRunCoordinator(registry=registry)
    started = coordinator.start_run(context, make_request_for_summary(context, summary))

    recovered = coordinator.recover_after_restart(started.distributed_run_id or "")

    assert recovered.status == "recovered"
    assert recovered.run_state is not None
    assert recovered.run_state["status"] == "running_recovered"
    assert recovered.run_state["recovered_after_restart"] is True
    assert any(event["event_type"] == "coordinator.restart.recovered" for event in recovered.run_state["incident_timeline"])


def test_v5_8b_lost_worker_recovery_retains_old_attempt_and_lineage() -> None:
    context = make_context()
    summary = read_v4_multi_agent_evidence_summary("UX-10-engineering-workflow")
    station_ids = summary["station_ids"][:3]
    registry = AgentWorkerRegistry()
    seed_workers_for_stations(context, registry, station_ids)
    replacement_station = station_ids[1]
    registry.register(
        DistributedWorkerDescriptor.from_context(
            context,
            worker_id=f"worker_{replacement_station}_replacement",
            station_id=replacement_station,
            credential_decision_ref=f"credential-decision://v5-8b/{replacement_station}/replacement",
        )
    )
    coordinator = DistributedRunCoordinator(registry=registry)
    started = coordinator.start_run(context, make_request_for_summary(context, summary))

    recovered = coordinator.recover_lost_worker(
        started.distributed_run_id or "",
        station_id=replacement_station,
        replacement_worker_id=f"worker_{replacement_station}_replacement",
    )

    attempts = recovered.run_state["station_attempts"][replacement_station]
    assert recovered.status == "worker_recovered"
    assert len(attempts) == 2
    assert attempts[0]["attempt_number"] == 1
    assert attempts[1]["attempt_number"] == 2
    assert recovered.run_state["downstream_stale"] == [f"downstream-of:{replacement_station}"]
    assert any(lineage["producer_attempt_id"] == attempts[1]["attempt_id"] for lineage in recovered.run_state["artifact_lineage"].values())


def test_v5_8b_source_agent_and_missing_confirmation_are_denied() -> None:
    context = make_context()
    summary = read_v4_multi_agent_evidence_summary("UX-08-serial-video")
    registry = AgentWorkerRegistry()
    seed_workers_for_stations(context, registry, summary["station_ids"][:3])
    coordinator = DistributedRunCoordinator(registry=registry)

    agent_result = coordinator.start_run(context, make_request_for_summary(context, summary, source="agent"))
    unconfirmed = coordinator.start_run(context, make_request_for_summary(context, summary, user_confirmed=False))

    assert agent_result.status == "blocked"
    assert agent_result.blocked_reason == "source_agent_durable_mutation_denied"
    assert unconfirmed.status == "blocked"
    assert unconfirmed.blocked_reason == "missing_user_confirmation"


def test_v5_8b_cross_tenant_worker_assignment_is_denied() -> None:
    context = make_context()
    summary = read_v4_multi_agent_evidence_summary("UX-08-serial-video")
    registry = AgentWorkerRegistry()
    for station_id in summary["station_ids"][:3]:
        registry.register(
            DistributedWorkerDescriptor(
                worker_id=f"wrong_tenant_worker_{station_id}",
                tenant_id="tenant_other",
                workspace_id=context.workspace_id,
                project_id=context.project_id,
                app_id=context.app_id,
                station_id=station_id,
                credential_decision_ref=f"credential-decision://v5-8b/{station_id}",
            )
        )
    coordinator = DistributedRunCoordinator(registry=registry)

    result = coordinator.start_run(context, make_request_for_summary(context, summary))

    assert result.status == "blocked"
    assert result.blocked_reason == "worker_not_available_or_scope_denied"
