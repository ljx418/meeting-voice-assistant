"""V7-2 explainable Mission TUI projection.

The module builds a transcript-only workflow-head state for the CLI. It does
not execute durable mutations or construct runtime truth.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from html import escape
from typing import Any
from uuid import uuid4

from apps.gateway.secrets import mask_value


STATE_LINE = (
    "IntentCaptured",
    "SpecDrafted",
    "SchemaValidated",
    "DiffReady",
    "AwaitingConfirmation",
)
FORBIDDEN_COPY = {
    "自动应用",
    "自动发布",
    "Agent 已执行",
    "Agent 已发布",
    "complete Workflow Studio ready",
    "Agent executor ready",
    "production controlled executor ready",
    "production ready",
    "TUI 工作流工作台已完成",
}
SENSITIVE_TOKENS = {
    "capability_token",
    "subscription_token",
    "Authorization:",
    "Bearer ",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw prompt",
    "raw_secret",
    "api_key",
    "sk-",
}


@dataclass(frozen=True)
class V72MissionTuiState:
    """Transcript-only Mission TUI state."""

    mission_id: str
    natural_language_goal: str
    current_state: str
    timeline: list[dict[str, str]]
    available_actions: list[dict[str, Any]]
    forbidden_reasons: list[dict[str, Any]]
    links: dict[str, str]
    transcript_only: bool
    runtime_backed: bool
    runtime_truth_boundary: str
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted state DTO."""
        return mask_value(asdict(self))


def build_mission_tui_state(goal: str, *, source: str = "mission_tui", actor_type: str = "human_user") -> V72MissionTuiState:
    """Build an explainable Mission TUI state without executing runtime actions."""
    normalized_goal = goal.strip()
    if not normalized_goal:
        raise ValueError("goal is required")
    mission_id = f"mission_v7_2_{uuid4().hex[:12]}"
    now = _now()
    timeline = [
        {"state": state, "status": "complete" if state != "AwaitingConfirmation" else "active", "occurred_at": now, "source_ref": f"mission://v7-2/{mission_id}/{state}"}
        for state in STATE_LINE
    ]
    available_actions = [
        {
            "action_id": f"action_{uuid4().hex[:10]}",
            "mission_id": mission_id,
            "operation": "workflow.patch.propose",
            "source": source,
            "actor_type": actor_type,
            "requires_user_confirmation": False,
            "agent_executable": False,
            "policy_decision": "allow",
            "capability_decision": "allow",
            "risk_flags": ["proposal_only", "transcript_only"],
            "target_refs": {"workflow_spec_id": f"workflow-spec://v7-2/{mission_id}"},
        },
        {
            "action_id": f"action_{uuid4().hex[:10]}",
            "mission_id": mission_id,
            "operation": "workflow.instance.start",
            "source": source,
            "actor_type": actor_type,
            "requires_user_confirmation": True,
            "agent_executable": False,
            "policy_decision": "needs_review",
            "capability_decision": "needs_user_confirmation",
            "risk_flags": ["durable_mutation", "user_confirmation_required"],
            "target_refs": {"workflow_spec_id": f"workflow-spec://v7-2/{mission_id}"},
        },
    ]
    forbidden_reasons = [
        {
            "reason_id": f"reason_{uuid4().hex[:10]}",
            "mission_id": mission_id,
            "operation": "workflow.instance.start",
            "source": "agent",
            "reason_code": "source_agent_denied",
            "human_readable_summary": "Agent 来源不能直接执行持久化运行，必须等待人工确认。",
            "policy_ref": "policy://v7-2/source-agent-denied",
        },
        {
            "reason_id": f"reason_{uuid4().hex[:10]}",
            "mission_id": mission_id,
            "operation": "workflow.instance.start",
            "source": source,
            "reason_code": "requires_user_confirmation",
            "human_readable_summary": "运行工作流属于持久化动作，必须先获得 user_confirmed=true。",
            "policy_ref": "policy://v7-2/user-confirmation-required",
        },
    ]
    links = {
        "workflow_spec": f"workflow-spec://v7-2/{mission_id}",
        "workflow_diff": f"workflow-diff://v7-2/{mission_id}",
        "blueprint": f"drawio://v7-2/{mission_id}/workflow.drawio",
        "runtime_report": "runtime-report://not-started/transcript-only",
        "evidence_chain": f"evidence://v7-2/{mission_id}/transcript",
    }
    state = V72MissionTuiState(
        mission_id=mission_id,
        natural_language_goal=normalized_goal,
        current_state="AwaitingConfirmation",
        timeline=timeline,
        available_actions=available_actions,
        forbidden_reasons=forbidden_reasons,
        links=links,
        transcript_only=True,
        runtime_backed=False,
        runtime_truth_boundary="tui_is_workflow_head_not_runtime_truth",
        generated_at=now,
    )
    validate_mission_tui_state(state)
    return state


def render_mission_tui_text(state: V72MissionTuiState) -> str:
    """Render a terminal-friendly transcript in Simplified Chinese."""
    data = state.to_dict()
    lines = [
        "HarnessOS Mission TUI",
        "=" * 28,
        f"任务: {data['natural_language_goal']}",
        f"当前状态: {data['current_state']}",
        f"证据范围: transcript_only={data['transcript_only']} runtime_backed={data['runtime_backed']}",
        "",
        "状态线:",
    ]
    for item in data["timeline"]:
        lines.append(f"- {item['state']}: {item['status']}")
    lines.extend(["", "可用动作:"])
    for action in data["available_actions"]:
        lines.append(
            f"- {action['operation']} | confirmation={action['requires_user_confirmation']} | policy={action['policy_decision']} | capability={action['capability_decision']}"
        )
    lines.extend(["", "禁止原因:"])
    for reason in data["forbidden_reasons"]:
        lines.append(f"- {reason['operation']} / {reason['reason_code']}: {reason['human_readable_summary']}")
    lines.extend(["", "证据链接:"])
    for key, value in data["links"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "边界: TUI 是 workflow head，不是 runtime truth；用户确认前不会执行持久化动作。"])
    transcript = "\n".join(lines) + "\n"
    validate_rendered_text(transcript)
    return transcript


def render_mission_tui_html(state: V72MissionTuiState) -> str:
    """Render read-only Mission TUI evidence HTML."""
    transcript = render_mission_tui_text(state)
    data = state.to_dict()
    return f"""<!doctype html>
<html lang=\"zh-CN\">
  <head>
    <meta charset=\"utf-8\" />
    <title>V7-2 Explainable Mission TUI</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; margin: 32px; background: #f8fafc; color: #111827; }}
      section {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin: 16px 0; }}
      pre {{ white-space: pre-wrap; background: #f1f5f9; padding: 12px; border-radius: 6px; }}
    </style>
  </head>
  <body>
    <h1>V7-2 Explainable Mission TUI</h1>
    <section><h2>Transcript</h2><pre>{escape(transcript)}</pre></section>
    <section><h2>State DTO</h2><pre>{escape(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True))}</pre></section>
  </body>
</html>
"""


def validate_mission_tui_state(state: V72MissionTuiState) -> None:
    """Validate no-false-green and runtime truth boundaries."""
    data = state.to_dict()
    serialized = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if data["runtime_backed"] is not False or data["transcript_only"] is not True:
        raise ValueError("V7-2 must remain transcript-only")
    if data["runtime_truth_boundary"] != "tui_is_workflow_head_not_runtime_truth":
        raise ValueError("runtime truth boundary missing")
    for action in data["available_actions"]:
        if action["operation"] == "workflow.instance.start":
            if action["requires_user_confirmation"] is not True:
                raise ValueError("workflow start must require confirmation")
            if action["agent_executable"] is not False:
                raise ValueError("agent must not execute durable action")
    for token in SENSITIVE_TOKENS:
        if token.lower() in serialized.lower():
            raise ValueError(f"sensitive token leaked: {token}")


def validate_rendered_text(text: str) -> None:
    """Validate rendered text does not overclaim."""
    for copy in FORBIDDEN_COPY:
        if copy.lower() in text.lower():
            raise ValueError(f"forbidden copy leaked: {copy}")


def scan_mission_tui_output(text: str) -> dict[str, Any]:
    """Scan rendered transcript or HTML."""
    return {
        "status": "PASS" if not [copy for copy in FORBIDDEN_COPY if copy.lower() in text.lower()] and not [token for token in SENSITIVE_TOKENS if token.lower() in text.lower()] else "FAIL",
        "forbidden_copy_hits": [copy for copy in FORBIDDEN_COPY if copy.lower() in text.lower()],
        "sensitive_hits": [token for token in SENSITIVE_TOKENS if token.lower() in text.lower()],
    }


def _now() -> str:
    return datetime.now(UTC).isoformat()
