"""V1.3 restricted Agent Workflow draft contract."""

from __future__ import annotations

import hashlib
import re
from typing import Any


class AgentWorkflowValidationError(ValueError):
    """Raised when an Agent workflow draft request is outside V1.3-F scope."""


def _digest(prefix: str, *parts: object) -> str:
    value = "\n".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]}"


def _extract_folder_hint(goal: str) -> str:
    normalized = goal.strip()
    if not normalized:
        raise AgentWorkflowValidationError("VALIDATION_ERROR: user_goal is required.")
    match = re.search(r"(Desktop/技术分享|桌面/技术分享|技术分享)", normalized)
    if match:
        value = match.group(1)
        return "Desktop/技术分享" if value == "技术分享" else value
    raise AgentWorkflowValidationError("VALIDATION_ERROR: V1.3-F only supports the registered folder_summary_v1 template for Desktop/技术分享.")


def create_agent_workflow_draft(*, workspace_id: str, user_goal: str) -> dict[str, Any]:
    folder_hint = _extract_folder_hint(user_goal)
    task_id = _digest("task", workspace_id, user_goal)
    workflow_id = _digest("wf", workspace_id, task_id, "folder_summary_v1")
    steps = [
        "scan_folder",
        "extract_text",
        "group_by_subfolder",
        "create_sources",
        "summarize_folder",
        "generate_index_report",
        "write_artifacts",
    ]
    workflow = {
        "workflow_id": workflow_id,
        "name": "递归文件夹总结",
        "template_id": "folder_summary_v1",
        "status": "draft",
        "required_permissions": ["folder:scan", "folder:extract:md_txt"],
        "draft_parameters": {
            "authorized_root_hint": folder_hint,
            "include_extensions": [".md", ".txt"],
            "exclude_globs": ["**/*.tmp"],
            "follow_symlinks": False,
            "requires_user_confirmation": True,
        },
        "steps": [
            {
                "step_id": _digest("step", workflow_id, name),
                "name": name,
                "status": "pending",
                "logs": [],
                "retry_count": 0,
                "artifact_refs": [],
            }
            for name in steps
        ],
    }
    task = {
        "task_id": task_id,
        "workspace_id": workspace_id,
        "user_goal": user_goal,
        "status": "awaiting_approval",
        "workflow_id": workflow_id,
    }
    return {"task": task, "workflow": workflow}
