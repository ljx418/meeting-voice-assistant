"""Persistence helpers for V2.32 lightweight relationship artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import read_jsonl, write_jsonl
from .persistence import task_navigation_dir


def relationship_graph_path(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "relationship_graph.json"


def relationships_path(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "relationships.jsonl"


def relationship_blockers_path(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "relationship_blockers.jsonl"


def relationship_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "relationship_graph", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/relationship_graph.json"},
        {"type": "relationships", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/relationships.jsonl"},
        {"type": "relationship_blockers", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/relationship_blockers.jsonl"},
    ]


def write_relationship_bundle(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(relationship_graph_path(workspace, codebase_id), payload)
    write_jsonl(relationships_path(workspace, codebase_id), list(payload.get("relationships") or []))
    write_jsonl(relationship_blockers_path(workspace, codebase_id), list(payload.get("relationship_blockers") or []))


def read_relationship_bundle(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(relationship_graph_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("TASK_RELATIONSHIPS_NOT_BUILT")
    return payload


def read_relationship_rows(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    return read_jsonl(relationships_path(workspace, codebase_id))
