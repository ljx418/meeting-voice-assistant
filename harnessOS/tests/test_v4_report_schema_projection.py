"""V4.x report schema projection tests."""

from __future__ import annotations

import json
from pathlib import Path


DOC = Path("docs/design/V4.x/v4_x_report_schema.md")
SCHEMA_DIR = Path("docs/design/V4.x/schemas")


def test_report_schema_doc_is_read_only_projection() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "报告是 read model，不是 runtime truth" in text
    assert "HTML Report must not include hidden mutation forms" in text
    assert "Drawio must not include mutation instructions" in text
    assert "Runtime status must come from BFF / runtime DTO" in text


def test_report_schemas_are_strict_and_redacted() -> None:
    for name in [
        "workflow_report.schema.json",
        "station_report.schema.json",
        "artifact_report.schema.json",
        "quality_report.schema.json",
        "evidence_report.schema.json",
    ]:
        schema = json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
        assert schema["additionalProperties"] is False, name

    workflow_schema = json.loads((SCHEMA_DIR / "workflow_report.schema.json").read_text(encoding="utf-8"))
    assert "redaction_status" in workflow_schema["required"]
    assert workflow_schema["properties"]["redaction_status"]["enum"] == ["redacted"]


def test_evidence_report_contains_governance_chain_fields() -> None:
    schema = json.loads((SCHEMA_DIR / "evidence_report.schema.json").read_text(encoding="utf-8"))
    required = set(schema["required"])

    assert {
        "proposal_id",
        "handoff_id",
        "user_confirmed",
        "operation_type",
        "runtime_result_ref",
        "risk_flags",
        "policy_decision",
        "correlation_id",
        "redaction_status",
        "review_status",
    }.issubset(required)

