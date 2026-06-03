import json
from pathlib import Path


def test_workflow_spec_registry_schema_declares_runtime_boundary():
    schema = json.loads(Path("docs/design/V4.x/schemas/workflow_spec_registry.schema.json").read_text())
    assert schema["additionalProperties"] is False
    for field in [
        "spec_id",
        "spec_hash",
        "schema_version",
        "source",
        "created_by",
        "validated_at",
        "linked_workflow_draft_id",
        "linked_workflow_version_id",
        "linked_workflow_instance_id",
        "runtime_truth_boundary",
    ]:
        assert field in schema["required"]
    assert "does not replace WorkflowDraft" in schema["properties"]["runtime_truth_boundary"]["const"]


def test_workflow_spec_registry_doc_blocks_report_or_event_truth():
    text = Path("docs/design/V4.x/v4_x_workflow_spec_registry.md").read_text()
    assert "WorkflowSpec Registry 不能替代 WorkflowDraft / WorkflowVersion" in text
    assert "Drawio 不能构造 runtime truth" in text
    assert "HTML Report 不能构造 runtime truth" in text
    assert "EventBridge payload 不能构造 runtime truth" in text
