"""Persistence helpers for V2.33 impact and test selection artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from .persistence import task_navigation_dir


def impacts_dir(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "impacts"


def test_selection_dir(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "test_selection"


def impact_path(workspace: Path, codebase_id: str, task_id: str) -> Path:
    return impacts_dir(workspace, codebase_id) / f"{task_id}.json"


def test_selection_path(workspace: Path, codebase_id: str, task_id: str) -> Path:
    return test_selection_dir(workspace, codebase_id) / f"{task_id}.json"


def impact_artifact_refs(codebase_id: str, task_id: str) -> list[dict[str, str]]:
    return [
        {"type": "impact_analysis", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/impacts/{task_id}.json"},
        {"type": "test_selection", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/test_selection/{task_id}.json"},
    ]


def write_impact_bundle(workspace: Path, codebase_id: str, impact: dict[str, Any], test_selection: dict[str, Any]) -> None:
    task_id = str(impact["task_id"])
    write_json(impact_path(workspace, codebase_id, task_id), impact)
    write_json(test_selection_path(workspace, codebase_id, task_id), test_selection)


def read_impact_bundle(workspace: Path, codebase_id: str, task_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    impact = read_json(impact_path(workspace, codebase_id, task_id), None)
    selection = read_json(test_selection_path(workspace, codebase_id, task_id), None)
    if not impact or not selection:
        raise FileNotFoundError("IMPACT_ANALYSIS_NOT_BUILT")
    return impact, selection
