from __future__ import annotations

import pytest

from core.policies.v9_agent_executor_safety import (
    V9AgentExecutorSafetyGate,
    V9SafetyGateError,
    build_approval_gate_decision,
    build_human_authorization_ref,
    build_kill_switch_decision,
    build_rollback_descriptor,
    build_timeout_policy,
)


def make_envelope(
    *,
    operation: str = "workflow.instance.start",
    source: str = "product_console",
    actor_type: str = "human_user",
    user_confirmed: bool = True,
    human_authorization_ref: str | None = None,
    target_refs: dict[str, str] | None = None,
    payload_refs: list[str] | None = None,
) -> dict[str, object]:
    refs = target_refs or _target_refs_for(operation)
    return {
        "schema_version": "v9.0",
        "execution_envelope_id": f"env-{operation}",
        "operation": operation,
        "source": source,
        "actor_type": actor_type,
        "actor_id": "user-v9-1",
        "agent_id": "agent-v9-1",
        "station_id": refs.get("station_id", "station-v9-1"),
        "tenant_id": "tenant-v9",
        "workspace_id": "workspace-v9",
        "project_id": "project-v9",
        "app_id": "app-v9",
        "workflow_instance_id": refs.get("workflow_instance_id", "workflow-v9"),
        "station_run_id": refs.get("station_run_id", "station-run-v9"),
        "target_refs": refs,
        "payload_refs": payload_refs or ["context_ref:v9-1"],
        "user_confirmed": user_confirmed,
        "human_authorization_ref": human_authorization_ref,
        "capability_decision_ref": "capability-ref-pending",
        "approval_gate_ref": "approval://v9-1/default" if operation in {"artifact.write", "quality.evaluation.create"} else None,
        "idempotency_key": "idem-v9-1",
        "timeout_policy_ref": "timeout://v9-1/default",
        "kill_switch_policy_ref": "kill-switch://v9-1/default",
        "rollback_descriptor_ref": "rollback://v9-1/default",
        "correlation_id": "corr-v9-1",
        "request_id": "req-v9-1",
        "audit_ref": "audit://v9-1/envelope",
        "created_at": "2026-06-05T00:00:00Z",
    }


def test_workflow_start_allows_safety_gate_handoff_but_not_runtime_execution() -> None:
    envelope = make_envelope()
    gate = V9AgentExecutorSafetyGate()

    decision = gate.evaluate(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    assert decision["decision"] == "allow"
    assert decision["runtime_execution_allowed"] is False
    assert decision["evidence"]["runtime_execution_allowed"] is False
    assert decision["requires_user_confirmation"] is True


def test_source_agent_durable_mutation_is_denied_even_with_user_confirmation() -> None:
    envelope = make_envelope(source="agent", actor_type="agent", user_confirmed=True)
    gate = V9AgentExecutorSafetyGate()

    decision = gate.evaluate(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    assert decision["decision"] == "deny"
    assert decision["denial_reason"] == "source_agent_durable_mutation_denied"
    assert decision["runtime_execution_allowed"] is False


def test_missing_user_confirmation_and_human_authorization_is_denied() -> None:
    envelope = make_envelope(user_confirmed=False, human_authorization_ref=None)
    gate = V9AgentExecutorSafetyGate()

    decision = gate.evaluate(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    assert decision["decision"] == "deny"
    assert decision["denial_reason"] == "missing_user_confirmation_or_valid_human_authorization_ref"


def test_valid_human_authorization_ref_can_replace_user_confirmation_for_safety_gate() -> None:
    envelope = make_envelope(user_confirmed=False, human_authorization_ref="har-v9-1")
    authorization = build_human_authorization_ref(ref="har-v9-1", envelope=envelope)
    gate = V9AgentExecutorSafetyGate()

    decision = gate.evaluate(
        envelope=envelope,
        human_authorization=authorization,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    assert decision["decision"] == "allow"
    assert decision["requires_human_authorization_ref"] is True
    assert decision["runtime_execution_allowed"] is False


@pytest.mark.parametrize(
    "mutate",
    [
        lambda auth: auth | {"expires_at": "2020-01-01T00:00:00Z"},
        lambda auth: auth | {"tenant_id": "wrong-tenant"},
        lambda auth: auth | {"operation_hash": "wrong-operation-hash"},
        lambda auth: auth | {"revoked": True, "revoked_at": "2026-06-05T00:00:00Z", "revocation_reason": "test"},
    ],
)
def test_invalid_human_authorization_ref_is_denied(mutate) -> None:
    envelope = make_envelope(user_confirmed=False, human_authorization_ref="har-v9-1")
    authorization = mutate(build_human_authorization_ref(ref="har-v9-1", envelope=envelope))
    gate = V9AgentExecutorSafetyGate()

    decision = gate.evaluate(
        envelope=envelope,
        human_authorization=authorization,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    assert decision["decision"] == "deny"
    assert decision["denial_reason"] == "missing_user_confirmation_or_valid_human_authorization_ref"


def test_artifact_write_requires_approval_gate_and_is_redacted() -> None:
    envelope = make_envelope(operation="artifact.write", target_refs={"artifact_id": "artifact-v9-1"}, payload_refs=["artifact_ref:content-v9-1"])
    gate = V9AgentExecutorSafetyGate()

    missing_approval = gate.evaluate(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    allowed = gate.evaluate(
        envelope=envelope,
        approval_gate=build_approval_gate_decision(envelope),
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()

    assert missing_approval["denial_reason"] == "approval_gate_required"
    assert allowed["decision"] == "allow"
    assert allowed["requires_approval_gate"] is True
    assert "raw" not in str(allowed["evidence"]).lower()


def test_kill_switch_timeout_and_rollback_contracts_are_required() -> None:
    envelope = make_envelope()
    gate = V9AgentExecutorSafetyGate()

    kill_denied = gate.evaluate(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope, allowed=False),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    missing_timeout = gate.evaluate(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    missing_rollback = gate.evaluate(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
    ).to_dict()

    assert kill_denied["denial_reason"] == "kill_switch_denied"
    assert missing_timeout["denial_reason"] == "missing_timeout_policy"
    assert missing_rollback["denial_reason"] == "missing_rollback_descriptor"


def test_raw_content_is_rejected_before_decision() -> None:
    envelope = make_envelope(payload_refs=["raw_prompt:do-not-allow"])

    with pytest.raises(V9SafetyGateError) as excinfo:
        V9AgentExecutorSafetyGate().evaluate(
            envelope=envelope,
            kill_switch=build_kill_switch_decision(envelope),
            timeout_policy=build_timeout_policy(envelope),
            rollback_descriptor=build_rollback_descriptor(envelope),
        )

    assert excinfo.value.reason == "forbidden_raw_content"


def _target_refs_for(operation: str) -> dict[str, str]:
    if operation == "workflow.instance.start":
        return {"workflow_instance_id": "workflow-v9"}
    if operation == "station.rerun":
        return {"station_id": "station-v9-1", "station_run_id": "station-run-v9"}
    if operation == "artifact.write":
        return {"artifact_id": "artifact-v9"}
    if operation == "quality.evaluation.create":
        return {"quality_evaluation_id": "quality-v9"}
    raise AssertionError(f"unexpected operation: {operation}")
