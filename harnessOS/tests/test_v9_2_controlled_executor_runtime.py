from __future__ import annotations

import pytest

from core.policies.v9_agent_executor_safety import (
    build_approval_gate_decision,
    build_human_authorization_ref,
    build_kill_switch_decision,
    build_rollback_descriptor,
    build_timeout_policy,
)
from core.policies.v9_controlled_executor_runtime import V9LimitedControlledExecutorRuntime


def make_envelope(
    *,
    operation: str = "workflow.instance.start",
    source: str = "product_console",
    actor_type: str = "human_user",
    user_confirmed: bool = True,
    human_authorization_ref: str | None = None,
    target_refs: dict[str, str] | None = None,
    payload_refs: list[str] | None = None,
    idempotency_key: str = "idem-v9-2",
) -> dict[str, object]:
    refs = target_refs or _target_refs_for(operation)
    return {
        "schema_version": "v9.0",
        "execution_envelope_id": f"env-v9-2-{operation}-{idempotency_key}",
        "operation": operation,
        "source": source,
        "actor_type": actor_type,
        "actor_id": "user-v9-2",
        "agent_id": "agent-v9-2",
        "station_id": refs.get("station_id", "station-v9-2"),
        "tenant_id": "tenant-v9",
        "workspace_id": "workspace-v9",
        "project_id": "project-v9",
        "app_id": "app-v9",
        "workflow_instance_id": refs.get("workflow_instance_id", "workflow-v9-2"),
        "station_run_id": refs.get("station_run_id", "station-run-v9-2"),
        "target_refs": refs,
        "payload_refs": payload_refs or ["context_ref:v9-2"],
        "user_confirmed": user_confirmed,
        "human_authorization_ref": human_authorization_ref,
        "capability_decision_ref": "capability-ref-pending",
        "approval_gate_ref": "approval://v9-2/default" if operation in {"artifact.write", "quality.evaluation.create"} else None,
        "idempotency_key": idempotency_key,
        "timeout_policy_ref": "timeout://v9-2/default",
        "kill_switch_policy_ref": "kill-switch://v9-2/default",
        "rollback_descriptor_ref": "rollback://v9-2/default",
        "correlation_id": "corr-v9-2",
        "request_id": "req-v9-2",
        "audit_ref": "audit://v9-2/envelope",
        "created_at": "2026-06-05T00:00:00Z",
    }


def test_workflow_instance_start_with_human_authorization_ref_executes_limited_slice() -> None:
    runtime = V9LimitedControlledExecutorRuntime()
    envelope = make_envelope(user_confirmed=False, human_authorization_ref="har-v9-2-start")
    authorization = build_human_authorization_ref(ref="har-v9-2-start", envelope=envelope)

    result = runtime.execute(
        envelope=envelope,
        human_authorization=authorization,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    assert result["status"] == "applied_v9_2_limited_runtime_slice"
    assert result["runtime_result_ref"] == "runtime-result://v9-2/workflow-v9-2/start"
    assert result["workflow_state"]["status"] == "running"
    assert result["execution_evidence"]["human_authorization_ref"] == "har-v9-2-start"
    assert result["execution_evidence"]["redaction_status"] == "PASS"
    assert result["agent_executor_ready"] is False
    assert result["controlled_executor_ready"] is False


def test_station_rerun_retains_old_attempt_and_marks_downstream_stale() -> None:
    runtime = V9LimitedControlledExecutorRuntime()
    runtime.seed_workflow(workflow_instance_id="workflow-v9-2", station_id="station-v9-2", station_run_id="station-run-v9-2-old", failed=True)
    envelope = make_envelope(
        operation="station.rerun",
        target_refs={"workflow_instance_id": "workflow-v9-2", "station_id": "station-v9-2", "station_run_id": "station-run-v9-2-old"},
    )

    result = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    attempts = result["workflow_state"]["station_attempts"]["station-v9-2"]
    assert result["status"] == "applied_v9_2_limited_runtime_slice"
    assert len(attempts) == 2
    assert attempts[0]["status"] == "failed"
    assert attempts[1]["previous_attempt_id"] == attempts[0]["attempt_id"]
    assert "downstream-of:station-v9-2" in result["workflow_state"]["downstream_stale"]


def test_artifact_write_and_quality_evaluation_are_append_only_and_approval_gated() -> None:
    runtime = V9LimitedControlledExecutorRuntime()
    artifact = make_envelope(operation="artifact.write", target_refs={"artifact_id": "artifact-v9-2"}, idempotency_key="idem-artifact-1")
    quality = make_envelope(operation="quality.evaluation.create", target_refs={"quality_evaluation_id": "quality-v9-2"}, idempotency_key="idem-quality-1")

    missing_approval = runtime.execute(
        envelope=artifact,
        kill_switch=build_kill_switch_decision(artifact),
        timeout_policy=build_timeout_policy(artifact),
        rollback_descriptor=build_rollback_descriptor(artifact),
    ).to_dict()
    artifact_result = runtime.execute(
        envelope=artifact | {"idempotency_key": "idem-artifact-2"},
        approval_gate=build_approval_gate_decision(artifact),
        kill_switch=build_kill_switch_decision(artifact),
        timeout_policy=build_timeout_policy(artifact),
        rollback_descriptor=build_rollback_descriptor(artifact),
    ).to_dict()
    quality_result = runtime.execute(
        envelope=quality,
        approval_gate=build_approval_gate_decision(quality),
        kill_switch=build_kill_switch_decision(quality),
        timeout_policy=build_timeout_policy(quality),
        rollback_descriptor=build_rollback_descriptor(quality),
    ).to_dict()

    assert missing_approval["status"] == "blocked"
    assert missing_approval["blocked_reason"] == "approval_gate_required"
    assert artifact_result["workflow_state"]["artifact_versions"]["artifact-v9-2"][0]["operation"] == "append_version"
    assert quality_result["workflow_state"]["quality_evaluations"]["quality-v9-2"][0]["operation"] == "append_evaluation"


def test_source_agent_and_excluded_actions_are_denied() -> None:
    runtime = V9LimitedControlledExecutorRuntime()
    source_agent = make_envelope(source="agent", actor_type="agent")
    excluded = make_envelope(operation="workflow.instance.start") | {"operation": "connector.call"}

    source_agent_result = runtime.execute(
        envelope=source_agent,
        kill_switch=build_kill_switch_decision(source_agent),
        timeout_policy=build_timeout_policy(source_agent),
        rollback_descriptor=build_rollback_descriptor(source_agent),
    ).to_dict()
    excluded_result = runtime.execute(envelope=excluded).to_dict()

    assert source_agent_result["status"] == "blocked"
    assert source_agent_result["blocked_reason"] == "source_agent_durable_mutation_denied"
    assert excluded_result["status"] == "blocked"
    assert excluded_result["blocked_reason"] == "operation_not_allowed"


def test_idempotency_duplicate_returns_prior_runtime_result_ref_and_conflict_denied() -> None:
    runtime = V9LimitedControlledExecutorRuntime()
    envelope = make_envelope(idempotency_key="idem-dup")
    first = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    second = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    conflict = runtime.execute(
        envelope=make_envelope(idempotency_key="idem-dup", target_refs={"workflow_instance_id": "workflow-other"}),
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    assert first["status"] == "applied_v9_2_limited_runtime_slice"
    assert second["status"] == "idempotent_replay"
    assert second["runtime_result_ref"] == first["runtime_result_ref"]
    assert conflict["status"] == "blocked"
    assert conflict["blocked_reason"] == "idempotency_key_conflict"


def test_kill_switch_and_raw_content_are_denied() -> None:
    runtime = V9LimitedControlledExecutorRuntime()
    envelope = make_envelope()
    runtime.disable_workspace("workspace-v9")
    kill_result = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    raw_result = V9LimitedControlledExecutorRuntime().execute(
        envelope=make_envelope(payload_refs=["raw_prompt:blocked"]),
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    assert kill_result["status"] == "blocked"
    assert kill_result["blocked_reason"] == "kill_switch_denied"
    assert raw_result["status"] == "blocked"
    assert raw_result["blocked_reason"] == "forbidden_raw_content"


def _target_refs_for(operation: str) -> dict[str, str]:
    if operation == "workflow.instance.start":
        return {"workflow_instance_id": "workflow-v9-2"}
    if operation == "station.rerun":
        return {"workflow_instance_id": "workflow-v9-2", "station_id": "station-v9-2", "station_run_id": "station-run-v9-2"}
    if operation == "artifact.write":
        return {"artifact_id": "artifact-v9-2"}
    if operation == "quality.evaluation.create":
        return {"quality_evaluation_id": "quality-v9-2"}
    raise AssertionError(f"unexpected operation: {operation}")
