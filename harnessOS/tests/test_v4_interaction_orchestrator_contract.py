"""V4.x interaction orchestrator contract tests."""

from __future__ import annotations

import json
from pathlib import Path


DOC = Path("docs/design/V4.x/v4_x_interaction_orchestrator_contract.md")
SCHEMAS = [
    Path("docs/design/V4.x/schemas/interaction_intent.schema.json"),
    Path("docs/design/V4.x/schemas/interaction_state_projection.schema.json"),
    Path("docs/design/V4.x/schemas/handoff_request.schema.json"),
]


def test_interaction_orchestrator_doc_keeps_runtime_boundary() -> None:
    text = DOC.read_text(encoding="utf-8")

    assert "它不直接写 runtime" in text
    assert "source=agent cannot execute mutation" in text
    assert "Durable mutation requires `user_confirmed=true`" in text
    assert "HTML Report and Drawio can only request read-only views or handoff" in text


def test_interaction_schemas_are_strict() -> None:
    for path in SCHEMAS:
        schema = json.loads(path.read_text(encoding="utf-8"))
        assert schema["additionalProperties"] is False, path
        assert schema["required"], path


def test_agent_source_is_supported_only_for_non_mutating_policy() -> None:
    intent_schema = json.loads(SCHEMAS[0].read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")

    assert "agent" in intent_schema["properties"]["source"]["enum"]
    assert "| workflow.patch.apply | no | user_confirmed_only |" in doc
    assert "| workflow.instance.start | no | user_confirmed_only |" in doc
    assert "| station.rerun | no | user_confirmed_only |" in doc

