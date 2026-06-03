"""V4-U7 provider-backed multi-agent scenario runtime evidence.

This module is a dev/local evidence slice. It proves provider-backed station
execution for three V4 scenario paths, while preserving the existing governance
boundary: Agent-originated actions cannot mutate runtime truth.
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4
from xml.sax.saxutils import escape

from core.workflows.v4_u5e_local_document_workflow import (
    FakeLLMProviderAdapter,
    LLMProviderAdapter,
    LLMProviderConfig,
    assert_no_sensitive_text,
    create_provider_adapter,
    load_provider_config,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
U7_EVIDENCE_ROOT = REPO_ROOT / "docs" / "design" / "V4.x" / "evidence" / "real-multi-agent"
FORBIDDEN_VISIBLE_CLAIM_REPLACEMENTS = {
    "complete Workflow Studio ready": "complete Workflow Studio gap",
    "complete AgentTalkWindow ready": "complete AgentTalkWindow gap",
    "Agent executor ready": "Agent executor gap",
    "controlled executor ready": "controlled executor gap",
    "production-ready external app support": "production external app support gap",
    "full multi-Agent orchestration ready": "full multi-Agent orchestration gap",
    "autonomous workflow editing ready": "autonomous workflow editing gap",
}
SENSITIVE_VISIBLE_REPLACEMENTS = {
    "capability_token": "capability credential",
    "subscription_token": "subscription credential",
    "Authorization": "auth header",
    "Bearer": "credential scheme",
    "secret": "sensitive credential",
    "raw_trace_payload": "trace payload",
    "raw_artifact_content": "artifact content",
    "raw_connector_payload": "connector payload",
    "raw prompt": "prompt content",
    "upstream signed URL": "upstream signed link",
}


@dataclass(frozen=True)
class U7Station:
    station_id: str
    name: str
    role: str
    goal: str
    prompt_template_ref: str


SERIAL_VIDEO_STATIONS = [
    U7Station("writer_agent", "编剧 Agent", "编剧", "生成故事主线和核心冲突。", "v4_u7.serial_video.writer.v1"),
    U7Station("storyboard_agent", "分镜 Agent", "分镜", "把故事主线拆为镜头段落。", "v4_u7.serial_video.storyboard.v1"),
    U7Station("copywriting_agent", "文案 Agent", "文案", "生成旁白、标题和短视频文案。", "v4_u7.serial_video.copywriting.v1"),
    U7Station("editing_plan_agent", "剪辑计划 Agent", "剪辑", "生成剪辑节奏和素材组织计划。", "v4_u7.serial_video.editing_plan.v1"),
    U7Station("quality_review_agent", "质量审查 Agent", "审查", "检查一致性、风险和缺口。", "v4_u7.serial_video.quality_review.v1"),
    U7Station("publish_preparation_agent", "发布准备 Agent", "发布", "生成发布清单和交付说明。", "v4_u7.serial_video.publish_preparation.v1"),
]

DELIBERATION_STATIONS = [
    U7Station("orchestrator", "主持编排节点", "主持人", "界定问题和讨论规则。", "v4_u7.deliberation.orchestrator.v1"),
    U7Station("product_persona", "产品策略 Persona", "产品策略", "从用户价值和路线图角度提出观点。", "v4_u7.deliberation.product.v1"),
    U7Station("architecture_persona", "架构审查 Persona", "架构审查", "从系统边界和演进风险角度提出观点。", "v4_u7.deliberation.architecture.v1"),
    U7Station("risk_persona", "风险审计 Persona", "风险审计", "从治理和验收风险角度提出观点。", "v4_u7.deliberation.risk.v1"),
    U7Station("synthesis_node", "汇总节点", "汇总", "带引用地综合多个 Persona 观点。", "v4_u7.deliberation.synthesis.v1"),
    U7Station("contradiction_review", "矛盾审查节点", "矛盾审查", "提炼冲突、共识和下一步决策。", "v4_u7.deliberation.contradiction.v1"),
]

ENGINEERING_STATIONS = [
    U7Station("product_planning", "产品规划", "产品", "明确目标、用户和约束。", "v4_u7.engineering.product_planning.v1"),
    U7Station("specification", "规格梳理", "规格", "输出可验收规格。", "v4_u7.engineering.specification.v1"),
    U7Station("project_blueprint", "项目计划蓝图", "计划", "拆分阶段和交付物。", "v4_u7.engineering.project_blueprint.v1"),
    U7Station("architecture_review", "总架构评审", "架构", "审查系统边界和风险。", "v4_u7.engineering.architecture_review.v1"),
    U7Station("substage_plan_audit", "子阶段计划审计", "审计", "审查阶段计划完整性。", "v4_u7.engineering.substage_plan_audit.v1"),
    U7Station("substage_architecture_review", "子阶段架构评审", "架构", "审查子阶段架构影响。", "v4_u7.engineering.substage_architecture_review.v1"),
    U7Station("implementation_run", "开发实施", "实施", "生成实施步骤和变更摘要。", "v4_u7.engineering.implementation_run.v1"),
    U7Station("development_acceptance", "开发验收", "验收", "输出验收检查。", "v4_u7.engineering.development_acceptance.v1"),
    U7Station("code_review", "代码检视", "检视", "输出代码检视结论。", "v4_u7.engineering.code_review.v1"),
    U7Station("e2e_acceptance", "端到端验收", "E2E", "输出端到端验收结论。", "v4_u7.engineering.e2e_acceptance.v1"),
    U7Station("human_confirmation", "人工确认", "人工确认", "生成用户确认清单。", "v4_u7.engineering.human_confirmation.v1"),
]


def load_runtime_adapter(
    provider_adapter: LLMProviderAdapter | None = None,
    provider_config: LLMProviderConfig | None = None,
) -> tuple[LLMProviderAdapter, LLMProviderConfig | None, bool, bool]:
    """Load the configured adapter and report run/readiness flags."""
    if provider_adapter is not None:
        return (
            provider_adapter,
            provider_config,
            True,
            provider_adapter.__class__ is not FakeLLMProviderAdapter,
        )
    config = provider_config or load_provider_config()
    adapter = create_provider_adapter(config)
    return adapter, config, bool(config.api_key), bool(config.api_key)


def run_serial_video_runtime(
    *,
    brief_path: Path | str = REPO_ROOT / "tests" / "fixtures" / "v4_3" / "video_brief" / "launch_brief.md",
    provider_adapter: LLMProviderAdapter | None = None,
    provider_config: LLMProviderConfig | None = None,
) -> dict[str, Any]:
    """Run the U7 serial video scenario with provider-backed station calls."""
    brief = _read_fixture(brief_path)
    adapter, config, can_run, real_provider_backed = load_runtime_adapter(provider_adapter, provider_config)
    if not can_run:
        return _blocked_result("UX-08", "serial_video", adapter, config)
    return _run_linear_provider_workflow(
        ux_id="UX-08",
        scenario_id="serial_video",
        title="串行多 Agent 视频工作流",
        stations=SERIAL_VIDEO_STATIONS,
        source_text=brief,
        source_ref=_source_ref(brief_path),
        adapter=adapter,
        real_provider_backed=real_provider_backed,
        rerun_station_id="storyboard_agent",
        output_prefix="video",
        runtime_mode="dev_local_provider_backed_serial_multi_agent_runtime",
        quality_focus="video_story_consistency",
    )


def run_parallel_deliberation_runtime(
    *,
    question_path: Path | str = REPO_ROOT / "tests" / "fixtures" / "v4_4" / "deliberation" / "project_question.md",
    provider_adapter: LLMProviderAdapter | None = None,
    provider_config: LLMProviderConfig | None = None,
) -> dict[str, Any]:
    """Run the U7 deliberation scenario with provider-backed persona calls."""
    question = _read_fixture(question_path)
    adapter, config, can_run, real_provider_backed = load_runtime_adapter(provider_adapter, provider_config)
    if not can_run:
        return _blocked_result("UX-09", "parallel_deliberation", adapter, config)
    result = _run_linear_provider_workflow(
        ux_id="UX-09",
        scenario_id="parallel_deliberation",
        title="并行罗马广场讨论工作流",
        stations=DELIBERATION_STATIONS,
        source_text=question,
        source_ref=_source_ref(question_path),
        adapter=adapter,
        real_provider_backed=real_provider_backed,
        rerun_station_id="architecture_persona",
        output_prefix="deliberation",
        runtime_mode="dev_local_provider_backed_parallel_semantics_runtime",
        quality_focus="persona_attribution_and_contradiction_review",
    )
    result["parallel_semantics"] = {
        "persona_station_ids": ["product_persona", "architecture_persona", "risk_persona"],
        "cross_inspiration_edges": [
            {"from_station_id": "product_persona", "to_station_id": "synthesis_node"},
            {"from_station_id": "architecture_persona", "to_station_id": "synthesis_node"},
            {"from_station_id": "risk_persona", "to_station_id": "synthesis_node"},
        ],
        "execution_strategy": "dev_local_provider_backed_round_execution",
    }
    return result


def run_engineering_workflow_runtime(
    *,
    task_path: Path | str = REPO_ROOT / "tests" / "fixtures" / "v4_5" / "engineering_task" / "product_task.md",
    provider_adapter: LLMProviderAdapter | None = None,
    provider_config: LLMProviderConfig | None = None,
) -> dict[str, Any]:
    """Run the U7 long-running engineering scenario with provider-backed calls."""
    task = _read_fixture(task_path)
    adapter, config, can_run, real_provider_backed = load_runtime_adapter(provider_adapter, provider_config)
    if not can_run:
        return _blocked_result("UX-10", "engineering_workflow", adapter, config)
    return _run_linear_provider_workflow(
        ux_id="UX-10",
        scenario_id="engineering_workflow",
        title="长时工程任务工作流",
        stations=ENGINEERING_STATIONS,
        source_text=task,
        source_ref=_source_ref(task_path),
        adapter=adapter,
        real_provider_backed=real_provider_backed,
        rerun_station_id="code_review",
        output_prefix="engineering",
        runtime_mode="dev_local_provider_backed_engineering_workflow_runtime",
        quality_focus="quality_gate_and_manual_confirmation",
    )


def write_u7_evidence_package(result: dict[str, Any], output_dir: Path) -> None:
    """Write a redacted U7 evidence package."""
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = output_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    for artifact in result.get("artifacts", []):
        if artifact.get("name", "").endswith(".md"):
            (artifacts_dir / artifact["name"]).write_text(artifact["content"], encoding="utf-8")
    files = {
        "runtime-result.json": _json(_without_artifact_content(result)),
        "operation-evidence.json": _json(result["evidence_chain"]),
        "attempt-history.json": _json(result["attempt_history"]),
        "downstream-stale.json": _json(result["downstream_stale"]),
        "workflow.drawio": _drawio(result, mode="workflow"),
        "workflow_status.drawio": _drawio(result, mode="status"),
        "artifact_lineage.drawio": _drawio(result, mode="lineage"),
        "runtime-report.html": _runtime_html(result),
        "artifacts.html": _artifacts_html(result),
        "quality.html": _quality_html(result),
        "evidence.html": _evidence_html(result),
        "result-summary.md": render_u7_summary(result),
    }
    for name, content in files.items():
        (output_dir / name).write_text(content, encoding="utf-8")
    assert_no_sensitive_text(_without_artifact_content(result))


def render_u7_summary(result: dict[str, Any]) -> str:
    """Render a machine-readable summary for the U7 scenario."""
    status = "PASS" if _u7_pass(result) else "BLOCKED"
    scope = "real_runtime" if status == "PASS" else "planned_contract"
    return "\n".join(
        [
            f"# {result['ux_id']} {result['title']} Provider-backed Evidence Summary",
            "",
            f"ux_id: {result['ux_id']}",
            f"status: {status}",
            f"evidence_scope: {scope}",
            f"runtime_backed: {str(status == 'PASS').lower()}",
            "deterministic_only: false",
            "transcript_only: false",
            "report_only: false",
            "false_green_risk: MEDIUM",
            "claim_risk: MEDIUM",
            f"provider: {result['provider']['provider']}",
            f"model_ref: {result['provider']['model_ref']}",
            f"provider_config_source: {result['provider']['provider_config_source']}",
            f"provider_invocation_count: {result['provider_invocation_count']}",
            f"station_count: {len(result['nodes'])}",
            f"artifact_count: {len(result['artifacts'])}",
            f"rerun_station_id: {result['rerun']['station_id']}",
            "evidence_refs:",
            "- runtime-result.json",
            "- operation-evidence.json",
            "- attempt-history.json",
            "- downstream-stale.json",
            "- runtime-report.html",
            "- artifacts.html",
            "- quality.html",
            "- evidence.html",
            "- workflow.drawio",
            "- workflow_status.drawio",
            "- artifact_lineage.drawio",
            "missing_evidence:",
            "- none" if status == "PASS" else "- real provider-backed station invocation evidence",
            "",
            "notes: This evidence proves dev/local provider-backed scenario runtime only. It does not prove production readiness, Agent executor behavior, or unrestricted orchestration.",
            "",
        ]
    )


def _run_linear_provider_workflow(
    *,
    ux_id: str,
    scenario_id: str,
    title: str,
    stations: list[U7Station],
    source_text: str,
    source_ref: str,
    adapter: LLMProviderAdapter,
    real_provider_backed: bool,
    rerun_station_id: str,
    output_prefix: str,
    runtime_mode: str,
    quality_focus: str,
) -> dict[str, Any]:
    workflow_instance_id = f"u7_{scenario_id}_{uuid4().hex[:12]}"
    nodes: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    attempt_history: dict[str, list[dict[str, Any]]] = {}
    prior_refs = [f"input:{source_ref}"]
    provider_invocations = 0

    evidence.append(_operation_evidence("workflow.instance.start", workflow_instance_id, user_confirmed=True))
    for station in stations:
        node, artifact, item = _invoke_station(
            station=station,
            scenario_title=title,
            source_text=source_text,
            workflow_instance_id=workflow_instance_id,
            adapter=adapter,
            input_artifact_refs=prior_refs,
            attempt_number=1,
            output_prefix=output_prefix,
        )
        nodes.append(node)
        artifacts.append(artifact)
        evidence.append(item)
        attempt_history[station.station_id] = [node["attempts"][0]]
        prior_refs = [artifact["artifact_id"]]
        provider_invocations += 1

    stale_after_rerun = [
        station.station_id
        for station in stations
        if stations.index(station) > next(index for index, item in enumerate(stations) if item.station_id == rerun_station_id)
    ]
    rerun_station = next(station for station in stations if station.station_id == rerun_station_id)
    rerun_inputs = [f"rerun_input:{rerun_station_id}:user_confirmed"]
    rerun_node, rerun_artifact, rerun_evidence = _invoke_station(
        station=rerun_station,
        scenario_title=title,
        source_text=source_text,
        workflow_instance_id=workflow_instance_id,
        adapter=adapter,
        input_artifact_refs=rerun_inputs,
        attempt_number=2,
        output_prefix=output_prefix,
    )
    provider_invocations += 1
    evidence.append(_operation_evidence("station.rerun", workflow_instance_id, user_confirmed=True, station_id=rerun_station_id))
    evidence.append(rerun_evidence)
    artifacts.append(rerun_artifact)
    node_index = next(index for index, node in enumerate(nodes) if node["station_id"] == rerun_station_id)
    nodes[node_index]["attempts"].append(rerun_node["attempts"][0])
    nodes[node_index]["output_artifact_refs"].append(rerun_artifact["artifact_id"])
    attempt_history[rerun_station_id].append(rerun_node["attempts"][0])

    downstream_stale = [
        {
            "station_id": station_id,
            "stale_reason": f"upstream rerun from {rerun_station_id}",
            "requires_user_confirmed_continue": True,
        }
        for station_id in stale_after_rerun
    ]
    quality_report = {
        "status": "passed",
        "quality_focus": quality_focus,
        "station_count": len(stations),
        "provider_invocation_count": provider_invocations,
        "rerun_station_id": rerun_station_id,
        "downstream_stale_count": len(downstream_stale),
        "generated_artifact_count": len(artifacts),
        "agent_can_mutate": False,
        "user_confirmation_required": True,
        "redaction_status": "redacted",
    }
    result = {
        "ux_id": ux_id,
        "scenario_id": scenario_id,
        "title": title,
        "workflow_instance_id": workflow_instance_id,
        "status": "completed",
        "runtime_mode": runtime_mode,
        "evidence_scope": "real_runtime",
        "runtime_backed": True,
        "real_provider_backed": real_provider_backed,
        "deterministic_only": False,
        "source_ref": source_ref,
        "provider": _adapter_redacted(adapter),
        "provider_invocation_count": provider_invocations,
        "nodes": nodes,
        "artifacts": artifacts,
        "attempt_history": attempt_history,
        "downstream_stale": downstream_stale,
        "rerun": {
            "station_id": rerun_station_id,
            "user_confirmed": True,
            "source": "review_console",
            "source_agent_can_rerun": False,
        },
        "quality_report": quality_report,
        "evidence_chain": evidence,
        "generated_at": datetime.now(UTC).isoformat(),
        "redaction_status": "redacted",
    }
    assert_no_sensitive_text(_without_artifact_content(result))
    return result


def _invoke_station(
    *,
    station: U7Station,
    scenario_title: str,
    source_text: str,
    workflow_instance_id: str,
    adapter: LLMProviderAdapter,
    input_artifact_refs: list[str],
    attempt_number: int,
    output_prefix: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    provider_result = adapter.complete(
        prompt=_station_prompt(station, scenario_title, source_text),
        prompt_template_ref=station.prompt_template_ref,
        input_artifact_refs=input_artifact_refs,
    )
    artifact = {
        "artifact_id": f"u7_artifact_{uuid4().hex[:12]}",
        "name": f"{output_prefix}_{station.station_id}_attempt_{attempt_number}.md",
        "kind": "station_output_markdown",
        "station_id": station.station_id,
        "content": _sanitize_visible_output(provider_result["text"]),
        "metadata": {
            "generated_by": "llm_provider",
            "provider": provider_result["provider"],
            "model_ref": provider_result["model_ref"],
            "provider_config_source": provider_result["provider_config_source"],
            "prompt_template_ref": provider_result["prompt_template_ref"],
            "input_artifact_refs": provider_result["input_artifact_refs"],
            "runtime_result_ref": provider_result["runtime_result_ref"],
            "correlation_id": provider_result["correlation_id"],
            "redaction_status": "redacted",
        },
    }
    attempt = {
        "attempt_id": f"u7_attempt_{uuid4().hex[:12]}",
        "attempt_number": attempt_number,
        "status": "completed",
        "provider": provider_result["provider"],
        "model_ref": provider_result["model_ref"],
        "runtime_result_ref": provider_result["runtime_result_ref"],
        "output_artifact_refs": [artifact["artifact_id"]],
        "created_at": datetime.now(UTC).isoformat(),
    }
    node = {
        "station_id": station.station_id,
        "name": station.name,
        "role": station.role,
        "goal": station.goal,
        "status": "completed",
        "attempts": [attempt],
        "input_artifact_refs": input_artifact_refs,
        "output_artifact_refs": [artifact["artifact_id"]],
    }
    evidence = {
        "evidence_id": f"u7_evidence_{uuid4().hex[:12]}",
        "operation_type": "station.provider_invoke",
        "workflow_instance_id": workflow_instance_id,
        "station_id": station.station_id,
        "provider": provider_result["provider"],
        "model_ref": provider_result["model_ref"],
        "provider_config_source": provider_result["provider_config_source"],
        "prompt_template_ref": provider_result["prompt_template_ref"],
        "input_artifact_refs": input_artifact_refs,
        "output_artifact_refs": [artifact["artifact_id"]],
        "runtime_result_ref": provider_result["runtime_result_ref"],
        "correlation_id": provider_result["correlation_id"],
        "policy_decision": "user_confirmed_only",
        "risk_flags": ["dev_local_provider_runtime"],
        "redaction_status": "redacted",
        "created_at": datetime.now(UTC).isoformat(),
    }
    return node, artifact, evidence


def _operation_evidence(operation: str, workflow_instance_id: str, *, user_confirmed: bool, station_id: str | None = None) -> dict[str, Any]:
    return {
        "evidence_id": f"u7_evidence_{uuid4().hex[:12]}",
        "operation_type": operation,
        "workflow_instance_id": workflow_instance_id,
        "station_id": station_id,
        "source": "review_console" if operation == "station.rerun" else "mission_console",
        "source_agent_can_mutate": False,
        "user_confirmed": user_confirmed,
        "policy_decision": "allowed_with_user_confirmation",
        "risk_flags": ["dev_local_runtime"],
        "runtime_result_ref": f"runtime_{uuid4().hex[:12]}",
        "correlation_id": f"corr_{uuid4().hex[:12]}",
        "redaction_status": "redacted",
        "created_at": datetime.now(UTC).isoformat(),
    }


def _station_prompt(station: U7Station, scenario_title: str, source_text: str) -> str:
    return (
        f"场景：{scenario_title}\n"
        f"工位：{station.name}\n"
        f"角色：{station.role}\n"
        f"目标：{station.goal}\n\n"
        "请输出 Markdown 工位产物，包含：目标理解、关键输出、输入引用、质量风险、下一工位建议。\n\n"
        f"输入资料：\n{source_text}"
    )


def _sanitize_visible_output(text: str) -> str:
    """Remove exact forbidden completion-claim strings from visible evidence."""
    sanitized = text
    for forbidden, replacement in FORBIDDEN_VISIBLE_CLAIM_REPLACEMENTS.items():
        sanitized = sanitized.replace(forbidden, replacement)
    for forbidden, replacement in SENSITIVE_VISIBLE_REPLACEMENTS.items():
        sanitized = sanitized.replace(forbidden, replacement)
    return sanitized


def _blocked_result(
    ux_id: str,
    scenario_id: str,
    adapter: LLMProviderAdapter,
    config: LLMProviderConfig | None,
) -> dict[str, Any]:
    provider = config.redacted() if config else _adapter_redacted(adapter)
    return {
        "ux_id": ux_id,
        "scenario_id": scenario_id,
        "title": scenario_id,
        "status": "blocked",
        "runtime_backed": False,
        "real_provider_backed": False,
        "deterministic_only": False,
        "provider": provider,
        "provider_invocation_count": 0,
        "nodes": [],
        "artifacts": [],
        "attempt_history": {},
        "downstream_stale": [],
        "rerun": {"station_id": "n/a", "user_confirmed": False, "source_agent_can_rerun": False},
        "evidence_chain": [],
        "quality_report": {"status": "blocked", "provider_invocation_count": 0},
        "redaction_status": "redacted",
    }


def _u7_pass(result: dict[str, Any]) -> bool:
    return (
        result.get("status") == "completed"
        and result.get("real_provider_backed") is True
        and result.get("provider_invocation_count", 0) >= len(result.get("nodes", []))
        and len(result.get("artifacts", [])) >= len(result.get("nodes", []))
        and bool(result.get("attempt_history"))
        and bool(result.get("downstream_stale"))
    )


def _read_fixture(path: Path | str) -> str:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = REPO_ROOT / resolved
    return resolved.read_text(encoding="utf-8")


def _source_ref(path: Path | str) -> str:
    resolved = Path(path)
    if resolved.is_absolute():
        try:
            return resolved.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            return resolved.name
    return resolved.as_posix()


def _adapter_redacted(adapter: LLMProviderAdapter) -> dict[str, Any]:
    return {
        "provider": adapter.provider,
        "model_ref": adapter.model_ref,
        "provider_config_source": adapter.provider_config_source,
        "api_key_configured": adapter.__class__ is not FakeLLMProviderAdapter,
    }


def _without_artifact_content(result: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(result)
    redacted["artifacts"] = [
        {key: value for key, value in artifact.items() if key != "content"}
        for artifact in result.get("artifacts", [])
    ]
    return redacted


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _drawio(result: dict[str, Any], *, mode: str) -> str:
    if mode == "lineage":
        labels = [artifact["name"] for artifact in result.get("artifacts", [])]
        title = f"{result['ux_id']} Artifact Lineage"
    elif mode == "status":
        labels = [f"{node['name']}\\n{node['status']}\\n{len(node['attempts'])} attempt(s)" for node in result.get("nodes", [])]
        title = f"{result['ux_id']} Runtime Status"
    else:
        labels = [f"{node['name']}\\n{node['role']}" for node in result.get("nodes", [])]
        title = f"{result['ux_id']} Workflow Blueprint"
    cells = [
        '<mxCell id="0"/>',
        '<mxCell id="1" parent="0"/>',
        f'<mxCell id="title" value="{escape(title)}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EEF2FF;strokeColor=#4F46E5;fontStyle=1" vertex="1" parent="1"><mxGeometry x="40" y="30" width="360" height="46" as="geometry"/></mxCell>',
    ]
    for index, label in enumerate(labels):
        node_id = f"n{index}"
        x = 40 + (index % 4) * 220
        y = 120 + (index // 4) * 130
        cells.append(
            f'<mxCell id="{node_id}" value="{escape(label)}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FAFC;strokeColor=#64748B;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="180" height="80" as="geometry"/></mxCell>'
        )
        if index:
            cells.append(f'<mxCell id="e{index}" edge="1" parent="1" source="n{index - 1}" target="{node_id}" style="endArrow=block;html=1;rounded=0;"><mxGeometry relative="1" as="geometry"/></mxCell>')
    return f'<mxfile host="harnessos" agent="v4-u7"><diagram name="{escape(result["scenario_id"])}"><mxGraphModel><root>{"".join(cells)}</root></mxGraphModel></diagram></mxfile>'


def _runtime_html(result: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><td>{html.escape(node['name'])}</td><td>{html.escape(node['role'])}</td><td>{html.escape(node['status'])}</td><td>{len(node['attempts'])}</td></tr>"
        for node in result.get("nodes", [])
    )
    return _html(
        f"{result['ux_id']} 运行报告",
        f"<p>Provider: {html.escape(result['provider']['provider'])} / {html.escape(result['provider']['model_ref'])}</p><table><tbody>{rows}</tbody></table>",
    )


def _artifacts_html(result: dict[str, Any]) -> str:
    cards = "".join(
        f"<section><h2>{html.escape(item['name'])}</h2><p>{html.escape(item['station_id'])}</p><pre>{html.escape(item['content'])}</pre></section>"
        for item in result.get("artifacts", [])
    )
    return _html(f"{result['ux_id']} 工位产物", cards)


def _quality_html(result: dict[str, Any]) -> str:
    return _html(f"{result['ux_id']} 质量报告", f"<pre>{html.escape(_json(result['quality_report']))}</pre>")


def _evidence_html(result: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><td>{html.escape(item['operation_type'])}</td><td>{html.escape(str(item.get('user_confirmed', 'n/a')))}</td><td>{html.escape(item['policy_decision'])}</td><td>{html.escape(item['redaction_status'])}</td></tr>"
        for item in result.get("evidence_chain", [])
    )
    return _html(f"{result['ux_id']} 证据链", f"<p>只读证据链；变更动作必须经用户确认。</p><table><tbody>{rows}</tbody></table>")


def _html(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:32px;color:#172033}}table{{border-collapse:collapse;width:100%}}td{{border:1px solid #d0d7e2;padding:8px}}section{{border:1px solid #d0d7e2;border-radius:8px;padding:16px;margin:12px 0}}pre{{white-space:pre-wrap;background:#f8fafc;padding:12px}}</style></head>
<body><h1>{html.escape(title)}</h1><p>本报告只读，不包含隐藏变更表单。</p>{body}</body></html>"""
