"""V4.0-Q executor sandbox boundary contract tests."""

from __future__ import annotations

import json
from pathlib import Path


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_q_controlled_executor_design_gate_contract.json")


def test_sandbox_boundary_requires_redacted_bff_dto_and_forbids_raw_access() -> None:
    sandbox = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))["sandbox_boundary"]
    assert sandbox["future_executor_input"] == "redacted BFF DTO only"
    assert set(sandbox["forbidden_fields_and_access"]) >= {
        "capability_token",
        "subscription_token",
        "Authorization",
        "Bearer",
        "secret",
        "raw_trace_payload",
        "raw_artifact_content",
        "raw_connector_payload",
        "raw prompt",
        "upstream signed URL",
        "direct WorkflowStore write",
        "direct WorkflowDraft write",
        "direct WorkflowVersion write",
        "direct StationRun write",
    }


def test_q_executor_design_does_not_add_raw_payload_source_paths() -> None:
    q_sources = [
        Path("docs/design/V4.0/v4_0_q_controlled_executor_design_gate_plan.md"),
        Path("docs/design/V4.0/v4_0_q_controlled_executor_design_gate_completion_note.md"),
        Path("apps/workflow-console/src/api/workflowConsoleClient.ts"),
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in q_sources)
    for forbidden_phrase in ("read raw_trace_payload", "read raw_artifact_content", "read raw_connector_payload", "WorkflowStore.write", "WorkflowDraft.write", "WorkflowVersion.write", "StationRun.write"):
        assert forbidden_phrase not in combined
