from __future__ import annotations

import json
from pathlib import Path


DOCS = Path("docs/design/V5.x")


def test_v5_7a_allowlist_defines_candidate_actions_with_required_controls() -> None:
    allowlist = json.loads((DOCS / "v5_7a_runtime_action_allowlist.json").read_text(encoding="utf-8"))
    actions = {item["operation"]: item for item in allowlist["candidate_actions"]}
    assert set(actions) == {
        "workflow.instance.start",
        "station.rerun",
        "artifact.write",
        "quality.evaluation.create",
    }
    for action in actions.values():
        assert action["requires_user_confirmation"] is True
        assert action["idempotency_required"] is True
        assert action["audit_required"] is True
        assert action["incident_timeline_required"] is True
        assert action["rollback_strategy"]
    assert actions["artifact.write"]["risk_level"] in {"medium", "high", "critical"}
    assert actions["artifact.write"]["requires_approval_gate"] is True
    assert actions["quality.evaluation.create"]["risk_level"] in {"medium", "high", "critical"}
    assert actions["quality.evaluation.create"]["requires_approval_gate"] is True


def test_v5_7a_excluded_actions_are_not_candidate_actions() -> None:
    allowlist = json.loads((DOCS / "v5_7a_runtime_action_allowlist.json").read_text(encoding="utf-8"))
    candidates = {item["operation"] for item in allowlist["candidate_actions"]}
    excluded = {item["operation"] for item in allowlist["excluded_actions"]}
    assert {"connector.call", "external_llm.call", "business.event.emit", "context.update", "workflow.template.publish", "approval.respond"}.issubset(excluded)
    assert candidates.isdisjoint(excluded)
    assert "agent" in allowlist["forbidden_sources"]
    assert allowlist["runtime_execution_enabled"] is False


def test_v5_7a_schemas_are_strict_design_contracts() -> None:
    schema_files = [
        "v5_7a_execution_envelope.schema.json",
        "v5_7a_sandbox_input_descriptor.schema.json",
        "v5_7a_rollback_descriptor.schema.json",
        "v5_7a_kill_switch_decision.schema.json",
        "v5_7a_execution_evidence.schema.json",
    ]
    for file_name in schema_files:
        schema = json.loads((DOCS / file_name).read_text(encoding="utf-8"))
        assert schema["additionalProperties"] is False
        assert schema["required"]


def test_v5_7a_execution_evidence_matches_v5_7b_preimplementation_requirements() -> None:
    schema = json.loads((DOCS / "v5_7a_execution_evidence.schema.json").read_text(encoding="utf-8"))
    required = set(schema["required"])
    assert {"project_id", "human_authorization_ref", "capability_decision", "timeout_policy_ref", "target_refs"}.issubset(required)
    target_refs = schema["properties"]["target_refs"]
    assert target_refs["additionalProperties"] is False
    for definition in target_refs["properties"].values():
        assert definition["minLength"] == 1
    conditions = json.dumps(schema["allOf"])
    assert "workflow.instance.start" in conditions
    assert "workflow_instance_id" in conditions
    assert "station.rerun" in conditions
    assert "station_run_id" in conditions
    assert "artifact.write" in conditions
    assert "output_artifact_target_id" in conditions
    assert "quality.evaluation.create" in conditions
    assert "quality_evaluation_id" in conditions


def test_v5_7a_execution_envelope_has_operation_specific_target_refs() -> None:
    schema = json.loads((DOCS / "v5_7a_execution_envelope.schema.json").read_text(encoding="utf-8"))
    target_refs = schema["properties"]["target_refs"]
    assert target_refs["additionalProperties"] is False
    for definition in target_refs["properties"].values():
        assert definition["minLength"] == 1
    conditions = json.dumps(schema["allOf"])
    assert "workflow.instance.start" in conditions
    assert "workflow_instance_id" in conditions
    assert "station.rerun" in conditions
    assert "station_run_id" in conditions
    assert "artifact.write" in conditions
    assert "output_artifact_target_id" in conditions
    assert "quality.evaluation.create" in conditions
    assert "quality_evaluation_id" in conditions


def test_v5_7a_kill_switch_decision_records_policy_and_correlation() -> None:
    schema = json.loads((DOCS / "v5_7a_kill_switch_decision.schema.json").read_text(encoding="utf-8"))
    required = set(schema["required"])
    assert {"checked_at", "checked_by", "policy_ref", "correlation_id"}.issubset(required)
