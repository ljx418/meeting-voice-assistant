"""Governed V4.6 Agent workflow builder helpers."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


FORBIDDEN_TERMS = (
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
    "/v1/rpc",
    "/v1/events/subscribe",
    "Agent executor ready",
    "controlled executor ready",
    "production-ready external app support",
    "full multi-Agent orchestration ready",
)


def create_builder_session(*, user_request: str, scope: dict[str, Any] | None = None) -> dict[str, Any]:
    session = {
        "agent_builder_session_id": f"v46_builder_session_{uuid4().hex[:12]}",
        "status": "drafting",
        "scope": scope or {},
        "user_request_summary": _summary(user_request),
        "clarifying_questions": [
            "是否只处理 Markdown 文件？",
            "是否需要为每个子文件夹生成独立总结？",
            "是否在用户确认后再应用、发布和运行？",
        ],
        "selected_workflow_template": "v41_local_folder_summary",
        "agent_capabilities": ["propose", "explain", "handoff", "navigate"],
        "agent_mutation_allowed": False,
        "created_at": _now_iso(),
        "redaction_status": "redacted",
    }
    assert_no_forbidden_text(session)
    return session


def generate_workflow_draft(session: dict[str, Any]) -> dict[str, Any]:
    draft = {
        "proposal_id": f"v46_workflow_proposal_{uuid4().hex[:12]}",
        "agent_builder_session_id": session["agent_builder_session_id"],
        "proposal_type": "workflow_spec_draft",
        "status": "proposed",
        "workflow_spec_ref": "v41_local_recursive_markdown_summary",
        "patch_operations": [
            {"operation": "create_workflow_draft", "target": "local_folder_summary", "requires_user_confirmed_apply": True},
            {"operation": "configure_folder_input", "target": "Desktop/技术分享", "requires_user_confirmed_apply": True},
        ],
        "preview_nodes": [
            "folder_input",
            "folder_scan",
            "markdown_filter",
            "markdown_parse",
            "folder_group",
            "per_folder_summary",
            "overview_summary",
            "quality_check",
            "artifact_publish",
        ],
        "agent_mutation_allowed": False,
        "redaction_status": "redacted",
    }
    assert_no_forbidden_text(draft)
    return draft


def explain_workflow_plan(session: dict[str, Any], proposal: dict[str, Any]) -> dict[str, Any]:
    explanation = {
        "explanation_id": f"v46_explanation_{uuid4().hex[:12]}",
        "agent_builder_session_id": session["agent_builder_session_id"],
        "proposal_id": proposal["proposal_id"],
        "read_only": True,
        "summary": "该计划会先生成工作流草案，再等待用户确认应用、发布和运行。",
        "steps": proposal["preview_nodes"],
        "agent_mutation_allowed": False,
        "redaction_status": "redacted",
    }
    assert_no_forbidden_text(explanation)
    return explanation


def propose_debug_repair(session: dict[str, Any], *, failed_station_id: str = "markdown_parse") -> dict[str, Any]:
    repair = {
        "repair_proposal_id": f"v46_repair_proposal_{uuid4().hex[:12]}",
        "agent_builder_session_id": session["agent_builder_session_id"],
        "failed_station_id": failed_station_id,
        "read_only_diagnosis": "Markdown parse failure can be repaired by adding stricter Markdown-only filtering and unsupported file recording.",
        "patch_operations": [
            {"operation": "update_quality_rule", "target": "unsupported_file_recorded", "requires_user_confirmed_apply": True}
        ],
        "status": "proposed",
        "agent_mutation_allowed": False,
        "redaction_status": "redacted",
    }
    assert_no_forbidden_text(repair)
    return repair


def build_handoff(session: dict[str, Any], proposal_id: str, target_panel: str = "editing_panel") -> dict[str, Any]:
    handoff = {
        "handoff_id": f"v46_handoff_{uuid4().hex[:12]}",
        "agent_builder_session_id": session["agent_builder_session_id"],
        "proposal_id": proposal_id,
        "target_panel": target_panel,
        "operation_executed": False,
        "requires_user_confirmation": True,
        "agent_mutation_allowed": False,
        "redaction_status": "redacted",
    }
    assert_no_forbidden_text(handoff)
    return handoff


def assert_no_forbidden_text(value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(value, str) else value
    for term in FORBIDDEN_TERMS:
        if term in text:
            raise AssertionError(f"Forbidden term leaked: {term}")


def _summary(text: str) -> str:
    cleaned = " ".join(text.split())[:160]
    replacements = {
        "自动应用": "自动执行应用",
        "自动发布": "自动执行发布",
        "Agent 已执行": "Agent 执行完成声明",
        "Agent 已发布": "Agent 发布完成声明",
    }
    for source, target in replacements.items():
        cleaned = cleaned.replace(source, target)
    return cleaned


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()
