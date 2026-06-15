"""Persistence helpers for V2.35 coding-agent handoff artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from .persistence import task_navigation_dir


def handoff_dir(workspace: Path, codebase_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id) / "handoff"


def handoff_path(workspace: Path, codebase_id: str, handoff_id: str) -> Path:
    return handoff_dir(workspace, codebase_id) / f"{handoff_id}.json"


def handoff_artifact_ref(codebase_id: str, handoff_id: str) -> dict[str, str]:
    return {"type": "agent_handoff", "artifact_ref": f"coding-agent://{codebase_id}/task_navigation/handoff/{handoff_id}.json"}


def write_handoff(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(handoff_path(workspace, codebase_id, str(payload["handoff_id"])), payload)


def read_handoff(workspace: Path, codebase_id: str, handoff_id: str) -> dict[str, Any]:
    payload = read_json(handoff_path(workspace, codebase_id, handoff_id), None)
    if not payload:
        raise FileNotFoundError("COPILOT_HANDOFF_NOT_FOUND")
    return payload
