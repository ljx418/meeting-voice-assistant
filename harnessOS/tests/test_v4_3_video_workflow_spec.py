"""V4.3 serial video WorkflowSpec tests."""

from __future__ import annotations

from copy import deepcopy

import pytest

from core.workflows.v4_3_serial_video import (
    AGENT_DESCRIPTOR_KEYS,
    TOP_LEVEL_SPEC_KEYS,
    VIDEO_STATIONS,
    build_video_workflow_schema,
    build_video_workflow_spec,
    validate_video_workflow_spec,
)


def test_video_workflow_spec_has_strict_serial_agent_descriptors() -> None:
    spec = build_video_workflow_spec()
    schema = build_video_workflow_schema()

    assert set(spec) == TOP_LEVEL_SPEC_KEYS
    assert set(schema["required"]) == TOP_LEVEL_SPEC_KEYS
    assert [station["station_id"] for station in spec["stations"]] == [station["station_id"] for station in VIDEO_STATIONS]
    for station in spec["stations"]:
        assert set(station["agent_descriptor"]) == AGENT_DESCRIPTOR_KEYS
        assert station["agent_descriptor"]["model_ref"]
        assert station["agent_descriptor"]["tool_refs"]
        assert station["agent_descriptor"]["skill_refs"]
    validate_video_workflow_spec(spec)


def test_video_workflow_spec_rejects_unknown_field() -> None:
    spec = build_video_workflow_spec()
    spec["layout"] = {"x": 1}

    with pytest.raises(ValueError):
        validate_video_workflow_spec(spec)


def test_video_workflow_spec_rejects_token_and_raw_payload() -> None:
    spec = deepcopy(build_video_workflow_spec())
    spec["stations"][0]["agent_descriptor"]["capability_token"] = "not-allowed"

    with pytest.raises(AssertionError):
        validate_video_workflow_spec(spec)


def test_video_workflow_spec_is_not_runtime_truth() -> None:
    metadata = build_video_workflow_spec()["metadata"]

    assert "does not replace WorkflowDraft or WorkflowVersion runtime truth" in metadata["runtime_truth_boundary"]
    assert metadata["generated_from"] == "v4_3_dev_local_video_fixture"

