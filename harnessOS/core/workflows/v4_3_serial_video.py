"""Deterministic V4.3 serial video workflow helpers.

The helpers model a dev/local serial multi-Agent workflow slice. They generate
text artifacts only and do not call external model, connector, or video tools.
"""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
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
    "complete Workflow Studio ready",
    "complete AgentTalkWindow ready",
    "Agent executor ready",
    "controlled executor ready",
    "production-ready external app support",
    "full multi-Agent orchestration ready",
)

TOP_LEVEL_SPEC_KEYS = {
    "metadata",
    "stations",
    "edges",
    "artifact_contracts",
    "quality_rules",
    "approval_points",
    "context_refs",
    "evidence_refs",
}

AGENT_DESCRIPTOR_KEYS = {
    "role",
    "goal",
    "model_ref",
    "tool_refs",
    "skill_refs",
    "input_artifact_contract",
    "output_artifact_contract",
}

VIDEO_STATIONS: list[dict[str, Any]] = [
    {
        "station_id": "writer_agent",
        "name": "编剧 Agent",
        "station_kind": "agent_station",
        "role": "Writer Agent",
        "goal": "把创作 brief 转成视频脚本大纲。",
        "model_ref": "dev_local_text_model",
        "tool_refs": ["brief_reader"],
        "skill_refs": ["script_outline"],
        "input": "video_brief",
        "output": "script_outline",
        "artifact_name": "script_outline.md",
    },
    {
        "station_id": "storyboard_agent",
        "name": "分镜 Agent",
        "station_kind": "agent_station",
        "role": "Storyboard Agent",
        "goal": "把脚本大纲转成镜头分镜。",
        "model_ref": "dev_local_text_model",
        "tool_refs": ["scene_planner"],
        "skill_refs": ["storyboard_planning"],
        "input": "script_outline",
        "output": "storyboard",
        "artifact_name": "storyboard.md",
    },
    {
        "station_id": "copywriting_agent",
        "name": "文案 Agent",
        "station_kind": "agent_station",
        "role": "Copywriting Agent",
        "goal": "生成口播文案、标题和短文案。",
        "model_ref": "dev_local_text_model",
        "tool_refs": ["copy_template"],
        "skill_refs": ["short_copy"],
        "input": "storyboard",
        "output": "short_copy",
        "artifact_name": "short_copy.md",
    },
    {
        "station_id": "editing_plan_agent",
        "name": "剪辑计划 Agent",
        "station_kind": "agent_station",
        "role": "Editing Plan Agent",
        "goal": "输出剪辑节奏、素材需求和转场计划。",
        "model_ref": "dev_local_text_model",
        "tool_refs": ["timeline_planner"],
        "skill_refs": ["editing_plan"],
        "input": "short_copy",
        "output": "editing_plan",
        "artifact_name": "editing_plan.md",
    },
    {
        "station_id": "quality_review_agent",
        "name": "质量审查 Agent",
        "station_kind": "quality_station",
        "role": "Quality Review Agent",
        "goal": "检查脚本、分镜、文案和剪辑计划是否覆盖 brief。",
        "model_ref": "dev_local_rule_model",
        "tool_refs": ["quality_rules"],
        "skill_refs": ["video_quality_review"],
        "input": "editing_plan",
        "output": "quality_review",
        "artifact_name": "quality_review.json",
    },
    {
        "station_id": "publish_preparation_agent",
        "name": "发布准备 Agent",
        "station_kind": "agent_station",
        "role": "Publish Preparation Agent",
        "goal": "生成发布清单、封面建议和上线前检查表。",
        "model_ref": "dev_local_text_model",
        "tool_refs": ["publish_checklist"],
        "skill_refs": ["publish_package"],
        "input": "quality_review",
        "output": "publish_package",
        "artifact_name": "publish_package.md",
    },
]


def build_video_workflow_spec(brief_path: str = "tests/fixtures/v4_3/video_brief/launch_brief.md") -> dict[str, Any]:
    """Build the strict V4.3 serial video WorkflowSpec."""
    return {
        "metadata": {
            "workflow_spec_id": "v43_serial_video_creation",
            "schema_version": "v4.3",
            "name": "串行多 Agent 视频创作流水线",
            "stage": "V4.3 Serial Multi-Agent Video Workflow MVP",
            "source_baseline": "V4.2-C controlled runtime MVP",
            "runtime_truth_boundary": "WorkflowSpec is a review artifact and does not replace WorkflowDraft or WorkflowVersion runtime truth.",
            "generated_from": "v4_3_dev_local_video_fixture",
        },
        "stations": [_station_spec(station) for station in VIDEO_STATIONS],
        "edges": [
            {
                "edge_id": f"edge_{VIDEO_STATIONS[index]['station_id']}_{VIDEO_STATIONS[index + 1]['station_id']}",
                "from_station_id": VIDEO_STATIONS[index]["station_id"],
                "to_station_id": VIDEO_STATIONS[index + 1]["station_id"],
                "artifact_contract_id": VIDEO_STATIONS[index]["output"],
            }
            for index in range(len(VIDEO_STATIONS) - 1)
        ],
        "artifact_contracts": [
            {"artifact_contract_id": "video_brief", "kind": "brief_markdown", "description": "视频创作 brief 引用。"},
            {"artifact_contract_id": "script_outline", "kind": "markdown", "description": "脚本大纲。"},
            {"artifact_contract_id": "storyboard", "kind": "markdown", "description": "分镜文档。"},
            {"artifact_contract_id": "short_copy", "kind": "markdown", "description": "口播与短文案。"},
            {"artifact_contract_id": "editing_plan", "kind": "markdown", "description": "剪辑计划。"},
            {"artifact_contract_id": "quality_review", "kind": "quality_report", "description": "质量审查报告。"},
            {"artifact_contract_id": "publish_package", "kind": "markdown", "description": "发布准备包。"},
        ],
        "quality_rules": [
            {"rule_id": "brief_coverage", "description": "每个工位产物都必须引用输入 brief 的主题。"},
            {"rule_id": "station_output_present", "description": "每个串行工位都必须有可查看产物。"},
            {"rule_id": "quality_review_passed", "description": "质量审查必须记录覆盖率和风险。"},
        ],
        "approval_points": [
            {"approval_point_id": "start_video_workflow", "operation": "workflow.instance.start", "policy": "user_confirmed_only"},
            {"approval_point_id": "rerun_video_station", "operation": "station.rerun", "policy": "user_confirmed_only"},
            {"approval_point_id": "continue_video_downstream", "operation": "workflow.instance.continue_downstream", "policy": "user_confirmed_only"},
        ],
        "context_refs": [
            {"context_ref_id": "video_brief_path", "value_label": brief_path},
            {"context_ref_id": "runtime_mode", "value_label": "dev_local_deterministic_runner"},
        ],
        "evidence_refs": [
            {"evidence_ref_id": "v4_3_runtime", "kind": "runtime_result", "resource_id": "runtime-result.json"},
            {"evidence_ref_id": "v4_3_attempt_history", "kind": "attempt_history", "resource_id": "attempt-history.json"},
            {"evidence_ref_id": "v4_3_operation_evidence", "kind": "operation_evidence", "resource_id": "operation-evidence.json"},
        ],
    }


def build_video_workflow_schema() -> dict[str, Any]:
    """Return a strict JSON schema for the V4.3 WorkflowSpec evidence."""
    station_schema = {
        "type": "object",
        "required": ["station_id", "name", "station_kind", "agent_descriptor", "input_artifacts", "output_artifacts"],
        "additionalProperties": False,
        "properties": {
            "station_id": {"type": "string"},
            "name": {"type": "string"},
            "station_kind": {"type": "string"},
            "agent_descriptor": {
                "type": "object",
                "required": sorted(AGENT_DESCRIPTOR_KEYS),
                "additionalProperties": False,
                "properties": {
                    "role": {"type": "string"},
                    "goal": {"type": "string"},
                    "model_ref": {"type": "string"},
                    "tool_refs": {"type": "array", "items": {"type": "string"}},
                    "skill_refs": {"type": "array", "items": {"type": "string"}},
                    "input_artifact_contract": {"type": "string"},
                    "output_artifact_contract": {"type": "string"},
                },
            },
            "input_artifacts": {"type": "array", "items": {"type": "string"}},
            "output_artifacts": {"type": "array", "items": {"type": "string"}},
        },
    }
    ref_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"context_ref_id": {"type": "string"}, "value_label": {"type": "string"}},
        "required": ["context_ref_id", "value_label"],
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "V4.3 Serial Video WorkflowSpec",
        "type": "object",
        "required": sorted(TOP_LEVEL_SPEC_KEYS),
        "additionalProperties": False,
        "properties": {
            "metadata": {"type": "object", "additionalProperties": {"type": "string"}},
            "stations": {"type": "array", "items": station_schema},
            "edges": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["edge_id", "from_station_id", "to_station_id", "artifact_contract_id"],
                    "additionalProperties": False,
                    "properties": {
                        "edge_id": {"type": "string"},
                        "from_station_id": {"type": "string"},
                        "to_station_id": {"type": "string"},
                        "artifact_contract_id": {"type": "string"},
                    },
                },
            },
            "artifact_contracts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["artifact_contract_id", "kind", "description"],
                    "additionalProperties": False,
                    "properties": {"artifact_contract_id": {"type": "string"}, "kind": {"type": "string"}, "description": {"type": "string"}},
                },
            },
            "quality_rules": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["rule_id", "description"],
                    "additionalProperties": False,
                    "properties": {"rule_id": {"type": "string"}, "description": {"type": "string"}},
                },
            },
            "approval_points": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["approval_point_id", "operation", "policy"],
                    "additionalProperties": False,
                    "properties": {"approval_point_id": {"type": "string"}, "operation": {"type": "string"}, "policy": {"type": "string"}},
                },
            },
            "context_refs": {"type": "array", "items": ref_schema},
            "evidence_refs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["evidence_ref_id", "kind", "resource_id"],
                    "additionalProperties": False,
                    "properties": {"evidence_ref_id": {"type": "string"}, "kind": {"type": "string"}, "resource_id": {"type": "string"}},
                },
            },
        },
    }


def validate_video_workflow_spec(spec: dict[str, Any]) -> None:
    """Validate the strict V4.3 WorkflowSpec without adding a schema dependency."""
    if set(spec) != TOP_LEVEL_SPEC_KEYS:
        raise ValueError("V4.3 WorkflowSpec has unknown or missing top-level fields.")
    assert_no_forbidden_text(spec)
    station_ids = [station["station_id"] for station in spec["stations"]]
    expected = [station["station_id"] for station in VIDEO_STATIONS]
    if station_ids != expected:
        raise ValueError("V4.3 video workflow stations must match the serial video order.")
    for station in spec["stations"]:
        if set(station) != {"station_id", "name", "station_kind", "agent_descriptor", "input_artifacts", "output_artifacts"}:
            raise ValueError("V4.3 station spec contains unknown fields.")
        descriptor = station["agent_descriptor"]
        if set(descriptor) != AGENT_DESCRIPTOR_KEYS:
            raise ValueError("V4.3 AgentDescriptor contains unknown or missing fields.")
        if not descriptor["tool_refs"] or not descriptor["skill_refs"]:
            raise ValueError("V4.3 AgentDescriptor must include tool_refs and skill_refs.")
    expected_edges = [(expected[index], expected[index + 1]) for index in range(len(expected) - 1)]
    actual_edges = [(edge["from_station_id"], edge["to_station_id"]) for edge in spec["edges"]]
    if actual_edges != expected_edges:
        raise ValueError("V4.3 video workflow edges must be serial.")


def run_serial_video_workflow(
    *,
    brief_text: str,
    brief_path: str,
    scope: dict[str, Any] | None = None,
    simulate_failure_station: str | None = None,
) -> dict[str, Any]:
    """Run the deterministic serial video workflow."""
    now = _now_iso()
    workflow_instance_id = f"v43_video_instance_{uuid4().hex[:12]}"
    nodes: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    failed = False
    simulate_failure_station = _station_id_alias(simulate_failure_station)
    for index, station in enumerate(VIDEO_STATIONS):
        attempts: list[dict[str, Any]] = []
        if failed:
            status = "pending"
            error = None
        elif simulate_failure_station == station["station_id"]:
            status = "failed"
            error = f"Deterministic video station failed: {station['station_id']}"
            failed = True
            attempts.append(_attempt(station["station_id"], 1, status="failed", error=error, created_at=now))
        else:
            status = "completed"
            error = None
            attempts.append(_attempt(station["station_id"], 1, status="completed", error=None, created_at=now))
            artifacts.append(_artifact_for_station(station, brief_text, workflow_instance_id, index))
        nodes.append(
            {
                "station_id": station["station_id"],
                "name": station["name"],
                "status": status,
                "agent_descriptor": _agent_descriptor(station),
                "input_artifact": station["input"],
                "output_artifact": station["output"],
                "attempts": attempts,
                "error": error,
                "updated_at": now,
            }
        )
    status = "failed" if failed else "completed"
    quality_report = _quality_report(brief_text, status=status, artifacts=artifacts)
    return {
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": "v43_serial_video_template",
        "workflow_version_id": "v43_serial_video_version_1",
        "status": status,
        "backed_by": "v4_3_serial_video_runtime",
        "runtime_mode": "dev_local_deterministic_runner",
        "scope": scope or {},
        "brief_path": brief_path,
        "nodes": nodes,
        "artifacts": artifacts,
        "quality_report": quality_report,
        "downstream_stale": [],
        "user_confirmed_required": True,
        "agent_mutation_allowed": False,
        "redaction_status": "redacted",
        "created_at": now,
        "updated_at": now,
    }


def rerun_video_station(run: dict[str, Any], station_id: str) -> dict[str, Any]:
    """Rerun a station, preserve attempt history, and mark downstream stale."""
    station_id = _station_id_alias(station_id) or station_id
    station_ids = [station["station_id"] for station in VIDEO_STATIONS]
    if station_id not in station_ids:
        raise ValueError(f"Unknown V4.3 station: {station_id}")
    now = _now_iso()
    rerun = deepcopy(run)
    stale: list[dict[str, Any]] = []
    downstream = False
    for node in rerun["nodes"]:
        attempts = list(node.get("attempts") or [])
        if node["station_id"] == station_id:
            attempts.append(_attempt(station_id, len(attempts) + 1, status="completed", error=None, created_at=now))
            node["status"] = "completed"
            node["attempts"] = attempts
            node["error"] = None
            node["updated_at"] = now
            station = next(item for item in VIDEO_STATIONS if item["station_id"] == station_id)
            artifact_names = {artifact["name"] for artifact in rerun.get("artifacts", [])}
            if station["artifact_name"] not in artifact_names:
                rerun.setdefault("artifacts", []).append(_artifact_for_station(station, "重跑后的 brief 上下文", rerun["workflow_instance_id"], station_ids.index(station_id)))
            downstream = True
            continue
        if downstream:
            node["status"] = "stale"
            node["updated_at"] = now
            stale.append({"station_id": node["station_id"], "reason": f"upstream_rerun:{station_id}", "requires_user_confirmed_continue": True})
    rerun["status"] = "waiting_user_confirmation"
    rerun["downstream_stale"] = stale
    rerun["updated_at"] = now
    return rerun


def continue_video_downstream(run: dict[str, Any]) -> dict[str, Any]:
    """Complete stale downstream stations after user confirmation."""
    now = _now_iso()
    continued = deepcopy(run)
    station_by_id = {station["station_id"]: station for station in VIDEO_STATIONS}
    existing_artifact_names = {artifact["name"] for artifact in continued.get("artifacts", [])}
    for index, node in enumerate(continued["nodes"]):
        if node["status"] != "stale":
            continue
        attempts = list(node.get("attempts") or [])
        attempts.append(_attempt(node["station_id"], len(attempts) + 1, status="completed", error=None, created_at=now))
        node["status"] = "completed"
        node["attempts"] = attempts
        node["updated_at"] = now
        station = station_by_id[node["station_id"]]
        if station["artifact_name"] not in existing_artifact_names:
            continued.setdefault("artifacts", []).append(_artifact_for_station(station, "续跑后的 brief 上下文", continued["workflow_instance_id"], index))
    continued["status"] = "completed"
    continued["downstream_stale"] = []
    continued["quality_report"] = _quality_report("续跑后的 brief 上下文", status="completed", artifacts=continued.get("artifacts", []))
    continued["updated_at"] = now
    return continued


def attempt_history(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": run["workflow_instance_id"],
        "stations": [
            {"station_id": node["station_id"], "status": node["status"], "attempts": node.get("attempts") or []}
            for node in run["nodes"]
        ],
        "redaction_status": "redacted",
    }


def assert_no_forbidden_text(value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(value, str) else value
    for term in FORBIDDEN_TERMS:
        if term in text:
            raise AssertionError(f"Forbidden term leaked: {term}")


def _station_spec(station: dict[str, Any]) -> dict[str, Any]:
    return {
        "station_id": station["station_id"],
        "name": station["name"],
        "station_kind": station["station_kind"],
        "agent_descriptor": _agent_descriptor(station),
        "input_artifacts": [station["input"]],
        "output_artifacts": [station["output"]],
    }


def _agent_descriptor(station: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": station["role"],
        "goal": station["goal"],
        "model_ref": station["model_ref"],
        "tool_refs": station["tool_refs"],
        "skill_refs": station["skill_refs"],
        "input_artifact_contract": station["input"],
        "output_artifact_contract": station["output"],
    }


def _artifact_for_station(station: dict[str, Any], brief_text: str, workflow_instance_id: str, index: int) -> dict[str, Any]:
    name = station["artifact_name"]
    if name.endswith(".json"):
        content = json.dumps(
            {
                "status": "passed",
                "coverage": "complete",
                "checked_artifacts": ["script_outline.md", "storyboard.md", "short_copy.md", "editing_plan.md"],
                "risks": ["dev_local_text_only", "no_real_video_rendering"],
                "redaction_status": "redacted",
            },
            ensure_ascii=False,
            indent=2,
        )
        kind = "quality_report"
    else:
        brief_title = _brief_title(brief_text)
        content = (
            f"# {station['name']}产物\n\n"
            f"## 角色\n{station['role']}\n\n"
            f"## 目标\n{station['goal']}\n\n"
            f"## 输入引用\n{station['input']}，主题：{brief_title}\n\n"
            f"## 输出内容\n- 工位序号：{index + 1}\n- 产物契约：{station['output']}\n- 使用工具：{', '.join(station['tool_refs'])}\n- 使用技能：{', '.join(station['skill_refs'])}\n\n"
            "## 说明\n这是 dev/local 确定性文本产物，用于验证串行多 Agent 工作流语义，不代表真实视频渲染。\n"
        )
        kind = "markdown"
    return {
        "artifact_id": f"v43_artifact_{uuid4().hex[:12]}",
        "workflow_instance_id": workflow_instance_id,
        "station_id": station["station_id"],
        "name": name,
        "kind": kind,
        "content": content,
        "metadata": {"redaction_status": "redacted", "agent_role": station["role"]},
        "redaction_status": "redacted",
    }


def _quality_report(brief_text: str, *, status: str, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    expected = {station["artifact_name"] for station in VIDEO_STATIONS}
    actual = {artifact["name"] for artifact in artifacts}
    return {
        "status": "passed" if status == "completed" and expected.issubset(actual) else "failed",
        "brief_title": _brief_title(brief_text),
        "artifact_coverage": {"expected": sorted(expected), "generated": sorted(actual), "missing": sorted(expected - actual)},
        "risk_flags": ["dev_local_text_only", "no_external_model_call", "no_real_video_rendering"],
        "redaction_status": "redacted",
    }


def _attempt(station_id: str, attempt: int, *, status: str, error: str | None, created_at: str) -> dict[str, Any]:
    return {
        "attempt_id": f"attempt_{station_id}_{attempt}",
        "attempt": attempt,
        "status": status,
        "error": error,
        "created_at": created_at,
    }


def _brief_title(brief_text: str) -> str:
    for line in brief_text.splitlines():
        stripped = line.strip("# ").strip()
        if stripped:
            return stripped[:80]
    return "未命名视频创作 brief"


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _station_id_alias(station_id: str | None) -> str | None:
    aliases = {
        "writer": "writer_agent",
        "storyboard": "storyboard_agent",
        "copywriting": "copywriting_agent",
        "editing_plan": "editing_plan_agent",
        "quality_review": "quality_review_agent",
        "publish_preparation": "publish_preparation_agent",
    }
    if station_id is None:
        return None
    return aliases.get(station_id, station_id)
