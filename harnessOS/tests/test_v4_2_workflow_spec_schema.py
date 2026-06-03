"""V4.2-A WorkflowSpec contract tests."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.v4_2_headless_evidence import TOP_LEVEL_SPEC_KEYS, validate_workflow_spec


EVIDENCE_DIR = Path("docs/design/V4.2/evidence/headless-interaction")


def _spec() -> dict:
    return json.loads((EVIDENCE_DIR / "workflow.json").read_text(encoding="utf-8"))


def _schema() -> dict:
    return json.loads((EVIDENCE_DIR / "workflow.schema.json").read_text(encoding="utf-8"))


def _walk_objects(schema: dict):
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            yield schema
        for value in schema.values():
            yield from _walk_objects(value)
    elif isinstance(schema, list):
        for value in schema:
            yield from _walk_objects(value)


def test_workflow_spec_has_required_strict_sections() -> None:
    spec = _spec()
    schema = _schema()

    assert set(spec) == TOP_LEVEL_SPEC_KEYS
    assert set(schema["required"]) == TOP_LEVEL_SPEC_KEYS
    assert all(item.get("additionalProperties") is False for item in _walk_objects(schema))
    validate_workflow_spec(spec)


def test_workflow_spec_rejects_unknown_top_level_field() -> None:
    spec = _spec()
    spec["layout"] = {"x": 1}

    with pytest.raises(ValueError):
        validate_workflow_spec(spec)


def test_workflow_spec_rejects_token_and_raw_payload_fields() -> None:
    spec = deepcopy(_spec())
    spec["metadata"]["capability_token"] = "not-allowed"

    with pytest.raises(AssertionError):
        validate_workflow_spec(spec)


def test_workflow_spec_is_not_runtime_truth() -> None:
    metadata = _spec()["metadata"]

    assert metadata["generated_from"] == "v4_1_local_workflow_path"
    assert "not WorkflowDraft or WorkflowVersion runtime truth" in metadata["runtime_truth_boundary"]
