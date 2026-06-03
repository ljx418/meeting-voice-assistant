from __future__ import annotations

from core.policies.controlled_executor_trial import ControlledExecutorTrialRunner
from tests.v5_3_observability_support import make_context


def test_synthetic_workflow_start_records_redacted_runtime_evidence() -> None:
    context = make_context()
    runner = ControlledExecutorTrialRunner()
    runner.seed_workflow(workflow_instance_id="synthetic_instance_v5_4b", station_ids=["scan", "summary"])

    result = runner.start_workflow(
        context,
        workflow_instance_id="synthetic_instance_v5_4b",
        source="user",
        actor_type="human_user",
        user_confirmed=True,
    )
    data = result.to_dict()

    assert data["status"] == "applied_synthetic"
    assert data["runtime_evidence"]["synthetic_only"] is True
    assert data["runtime_evidence"]["runtime_backed"] is False
    assert data["runtime_evidence"]["user_confirmed"] is True
    assert data["workflow_state"]["status"] == "running"
    assert data["workflow_state"]["synthetic_only"] is True
    assert data["decision"]["runtime_execution_allowed"] is False


def test_synthetic_station_rerun_retains_attempt_history_and_marks_stale() -> None:
    context = make_context()
    runner = ControlledExecutorTrialRunner()
    runner.seed_workflow(workflow_instance_id="synthetic_instance_v5_4b", station_ids=["scan", "summary"])
    runner.start_workflow(
        context,
        workflow_instance_id="synthetic_instance_v5_4b",
        source="user",
        actor_type="human_user",
        user_confirmed=True,
    )

    first = runner.rerun_station(
        context,
        workflow_instance_id="synthetic_instance_v5_4b",
        station_id="scan",
        source="user",
        actor_type="human_user",
        user_confirmed=True,
        input_refs=["artifact://input/scan"],
        output_refs=["artifact://output/scan-v1"],
    )
    second = runner.rerun_station(
        context,
        workflow_instance_id="synthetic_instance_v5_4b",
        station_id="scan",
        source="user",
        actor_type="human_user",
        user_confirmed=True,
        input_refs=["artifact://input/scan"],
        output_refs=["artifact://output/scan-v2"],
    )

    scan_state = second.to_dict()["workflow_state"]["station_states"]["scan"]
    summary_state = second.to_dict()["workflow_state"]["station_states"]["summary"]

    assert first.status == "applied_synthetic"
    assert scan_state["attempt_count"] == 2
    assert [attempt["attempt_number"] for attempt in scan_state["attempts"]] == [1, 2]
    assert summary_state["downstream_stale"] is True
