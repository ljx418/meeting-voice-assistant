"""Persistence helpers for V2.31 task navigation artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir


def task_navigation_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "coding_agent" / "task_navigation"


def navigation_index_path(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "navigation_index.json"


def task_queries_dir(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "task_queries"


def task_query_path(workspace: Path, codebase_id: str, task_id: str) -> Path:
    safe = str(task_id or "task").strip().replace("/", "_")
    return task_queries_dir(workspace, codebase_id) / f"{safe}.json"


def task_navigation_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "task_navigation_index", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/navigation_index.json"},
    ]


def task_query_artifact_ref(codebase_id: str, task_id: str) -> dict[str, str]:
    return {"type": "task_navigation_query", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/task_queries/{task_id}.json"}


def write_navigation_index(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(navigation_index_path(workspace, codebase_id), payload)


def read_navigation_index(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(navigation_index_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("TASK_NAVIGATION_NOT_BUILT")
    return payload


def write_task_query(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(task_query_path(workspace, codebase_id, str(payload["task_id"])), payload)


def read_task_query(workspace: Path, codebase_id: str, task_id: str) -> dict[str, Any]:
    payload = read_json(task_query_path(workspace, codebase_id, task_id), None)
    if not payload:
        raise FileNotFoundError("TASK_QUERY_NOT_FOUND")
    return payload
