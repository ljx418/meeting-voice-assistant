"""Persistence helpers for V2.1 code quality governance."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import (
    code_quality_feedback_path,
    code_quality_plan_path,
    code_quality_reviews_path,
    code_quality_rules_path,
    code_quality_summary_path,
    read_jsonl,
    write_jsonl,
)


def quality_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "code_quality_feedback", "artifact_ref": f"code-quality://{codebase_id}/feedback.jsonl"},
        {"type": "code_quality_rules", "artifact_ref": f"code-quality://{codebase_id}/rules.jsonl"},
        {"type": "code_quality_reviews", "artifact_ref": f"code-quality://{codebase_id}/reviews.jsonl"},
        {"type": "code_quality_plan", "artifact_ref": f"code-quality://{codebase_id}/plan.json"},
        {"type": "code_quality_summary", "artifact_ref": f"code-quality://{codebase_id}/summary.json"},
    ]


def feedback_artifact_ref(feedback_id: str) -> str:
    return f"code-quality-feedback://{feedback_id}"


def rule_artifact_ref(rule_id: str) -> str:
    return f"code-quality-rule://{rule_id}"


def plan_artifact_ref(plan_id: str) -> str:
    return f"code-quality-plan://{plan_id}"


def read_feedback(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    return read_jsonl(code_quality_feedback_path(workspace, codebase_id))


def write_feedback(workspace: Path, codebase_id: str, rows: list[dict[str, Any]]) -> None:
    write_jsonl(code_quality_feedback_path(workspace, codebase_id), rows)


def read_rules(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    return read_jsonl(code_quality_rules_path(workspace, codebase_id))


def write_rules(workspace: Path, codebase_id: str, rows: list[dict[str, Any]]) -> None:
    write_jsonl(code_quality_rules_path(workspace, codebase_id), rows)


def read_reviews(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    return read_jsonl(code_quality_reviews_path(workspace, codebase_id))


def write_reviews(workspace: Path, codebase_id: str, rows: list[dict[str, Any]]) -> None:
    write_jsonl(code_quality_reviews_path(workspace, codebase_id), rows)


def read_plan(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return read_json(code_quality_plan_path(workspace, codebase_id), {})


def write_plan(workspace: Path, codebase_id: str, plan: dict[str, Any]) -> None:
    write_json(code_quality_plan_path(workspace, codebase_id), plan)


def read_summary(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return read_json(code_quality_summary_path(workspace, codebase_id), {})


def write_summary(workspace: Path, codebase_id: str, summary: dict[str, Any]) -> None:
    write_json(code_quality_summary_path(workspace, codebase_id), summary)
