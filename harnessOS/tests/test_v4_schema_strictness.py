import json
from pathlib import Path


SCHEMA_DIR = Path("docs/design/V4.x/schemas")


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text())


def test_target_refs_is_not_arbitrary_object():
    schema = load_schema("target_refs.schema.json")
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == {
        "workflow_spec_id",
        "workflow_instance_id",
        "station_id",
        "station_run_id",
        "artifact_id",
        "evidence_id",
        "handoff_id",
        "report_id",
    }


def test_operation_is_enum_with_required_actions():
    schema = load_schema("operation.schema.json")
    assert schema["type"] == "string"
    assert {
        "workflow.spec.generate",
        "workflow.patch.propose",
        "workflow.patch.apply",
        "workflow.template.publish",
        "workflow.instance.start",
        "station.rerun",
        "approval.respond",
        "context.update",
        "evidence.show",
        "report.open",
        "drawio.open",
        "handoff.open",
    }.issubset(set(schema["enum"]))


def test_projection_station_states_are_ref_not_object():
    schema = load_schema("interaction_state_projection.schema.json")
    assert schema["properties"]["station_states"]["items"] == {"$ref": "station_state.schema.json"}
    assert "refresh_generation" in schema["required"]
    assert "stale_reasons" in schema["required"]
    assert schema["properties"]["read_model_only"]["const"] is True


def test_available_actions_guard_agent_mutation():
    schema = load_schema("available_actions.schema.json")
    assert schema["properties"]["operation"] == {"$ref": "operation.schema.json"}
    guard = schema["properties"]["source_agent_mutation_guard"]["const"]
    assert "source=agent cannot execute" in guard
    assert "approval.respond" in guard


def test_evidence_report_is_readonly_and_action_limited():
    schema = load_schema("evidence_report.schema.json")
    for field in ["created_at", "created_by", "source_refs", "readonly", "report_actions"]:
        assert field in schema["required"]
    assert schema["properties"]["readonly"]["const"] is True
    assert set(schema["properties"]["report_actions"]["items"]["enum"]) == {
        "view",
        "export",
        "open_handoff",
    }
