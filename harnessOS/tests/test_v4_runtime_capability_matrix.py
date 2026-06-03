import json
from pathlib import Path


def test_runtime_capability_matrix_schema_exists_and_tracks_false_green_fields():
    schema = json.loads(Path("docs/design/V4.x/schemas/runtime_capability_matrix.schema.json").read_text())
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]["status"]["enum"]) == {
        "supported",
        "partial",
        "planned",
        "unsupported",
    }
    for field in [
        "runtime_backed",
        "deterministic_only",
        "false_green_risk",
        "agent_executable",
        "requires_user_confirmation",
    ]:
        assert field in schema["required"]


def test_runtime_capability_matrix_doc_marks_future_claims_unsupported():
    text = Path("docs/design/V4.x/v4_x_runtime_capability_matrix.md").read_text()
    assert "| agent_executor | unsupported |" in text
    assert "| controlled_executor_production | unsupported |" in text
    assert "| full_multi_agent_orchestration | unsupported |" in text
    assert "deterministic dev/local evidence" in text
