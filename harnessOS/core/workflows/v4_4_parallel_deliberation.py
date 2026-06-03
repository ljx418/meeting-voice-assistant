"""Deterministic V4.4 parallel deliberation workflow helpers."""

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

PERSONAS = [
    {
        "station_id": "product_strategist_agent",
        "name": "产品策略 Persona",
        "persona": "product_strategist",
        "viewpoint": "优先验证用户可用的 Headless workflow core，降低完整 Web Studio 投入。",
        "artifact_name": "product_strategy_opinion.md",
    },
    {
        "station_id": "architecture_agent",
        "name": "架构 Persona",
        "persona": "architecture_reviewer",
        "viewpoint": "保留七平面事实源，用多 Head 输出替代重前端耦合。",
        "artifact_name": "architecture_opinion.md",
    },
    {
        "station_id": "risk_reviewer_agent",
        "name": "风险 Persona",
        "persona": "risk_reviewer",
        "viewpoint": "继续强化 No False Green、用户确认和证据链，避免 Agent executor 误报。",
        "artifact_name": "risk_review_opinion.md",
    },
]

STATIONS = [
    {"station_id": "orchestrator", "name": "Orchestrator", "kind": "orchestrator", "artifact_name": "deliberation_plan.md"},
    *[
        {"station_id": persona["station_id"], "name": persona["name"], "kind": "persona_agent", "artifact_name": persona["artifact_name"]}
        for persona in PERSONAS
    ],
    {"station_id": "synthesis", "name": "观点汇总节点", "kind": "synthesis", "artifact_name": "synthesis_with_attribution.md"},
    {"station_id": "contradiction_review", "name": "矛盾审查节点", "kind": "quality_station", "artifact_name": "contradiction_review.json"},
]


def build_deliberation_spec(question_path: str = "tests/fixtures/v4_4/deliberation/project_question.md") -> dict[str, Any]:
    return {
        "metadata": {
            "workflow_spec_id": "v44_parallel_deliberation",
            "schema_version": "v4.4",
            "name": "罗马广场并行多 Agent 讨论工作流",
            "stage": "V4.4 Parallel Multi-Agent Deliberation Workflow MVP",
            "runtime_truth_boundary": "WorkflowSpec is a review artifact and does not replace WorkflowDraft or WorkflowVersion runtime truth.",
            "generated_from": "v4_4_dev_local_deliberation_fixture",
        },
        "stations": [_station_spec(station) for station in STATIONS],
        "edges": [
            {"edge_id": "edge_orchestrator_product", "from_station_id": "orchestrator", "to_station_id": "product_strategist_agent", "artifact_contract_id": "deliberation_plan"},
            {"edge_id": "edge_orchestrator_architecture", "from_station_id": "orchestrator", "to_station_id": "architecture_agent", "artifact_contract_id": "deliberation_plan"},
            {"edge_id": "edge_orchestrator_risk", "from_station_id": "orchestrator", "to_station_id": "risk_reviewer_agent", "artifact_contract_id": "deliberation_plan"},
            {"edge_id": "edge_product_architecture_inspiration", "from_station_id": "product_strategist_agent", "to_station_id": "architecture_agent", "artifact_contract_id": "opinion_artifact"},
            {"edge_id": "edge_architecture_risk_inspiration", "from_station_id": "architecture_agent", "to_station_id": "risk_reviewer_agent", "artifact_contract_id": "opinion_artifact"},
            *[
                {"edge_id": f"edge_{persona['station_id']}_synthesis", "from_station_id": persona["station_id"], "to_station_id": "synthesis", "artifact_contract_id": "opinion_artifact"}
                for persona in PERSONAS
            ],
            {"edge_id": "edge_synthesis_contradiction_review", "from_station_id": "synthesis", "to_station_id": "contradiction_review", "artifact_contract_id": "synthesis_artifact"},
        ],
        "artifact_contracts": [
            {"artifact_contract_id": "project_question", "kind": "markdown", "description": "真实 dev/local 讨论问题。"},
            {"artifact_contract_id": "deliberation_plan", "kind": "markdown", "description": "Orchestrator 讨论计划。"},
            {"artifact_contract_id": "opinion_artifact", "kind": "markdown", "description": "persona 独立观点。"},
            {"artifact_contract_id": "synthesis_artifact", "kind": "markdown", "description": "带归因的汇总观点。"},
            {"artifact_contract_id": "contradiction_report", "kind": "quality_report", "description": "矛盾和未决风险审查。"},
        ],
        "quality_rules": [
            {"rule_id": "all_personas_present", "description": "所有 persona 必须产出观点。"},
            {"rule_id": "attribution_required", "description": "汇总必须标注观点来源。"},
            {"rule_id": "contradictions_recorded", "description": "矛盾和风险必须记录。"},
        ],
        "approval_points": [
            {"approval_point_id": "start_deliberation", "operation": "workflow.instance.start", "policy": "user_confirmed_only"},
            {"approval_point_id": "rerun_persona", "operation": "station.rerun", "policy": "user_confirmed_only"},
            {"approval_point_id": "continue_synthesis", "operation": "workflow.instance.continue_downstream", "policy": "user_confirmed_only"},
        ],
        "context_refs": [{"context_ref_id": "project_question_path", "value_label": question_path}],
        "evidence_refs": [
            {"evidence_ref_id": "runtime_result", "kind": "runtime_result", "resource_id": "runtime-result.json"},
            {"evidence_ref_id": "operation_evidence", "kind": "operation_evidence", "resource_id": "operation-evidence.json"},
        ],
    }


def validate_deliberation_spec(spec: dict[str, Any]) -> None:
    if set(spec) != TOP_LEVEL_SPEC_KEYS:
        raise ValueError("V4.4 deliberation spec has unknown or missing top-level fields.")
    assert_no_forbidden_text(spec)
    expected = [station["station_id"] for station in STATIONS]
    if [station["station_id"] for station in spec["stations"]] != expected:
        raise ValueError("V4.4 deliberation stations do not match expected order.")
    if not any("inspiration" in edge["edge_id"] for edge in spec["edges"]):
        raise ValueError("V4.4 deliberation spec must include cross-inspiration edges.")


def run_deliberation_workflow(*, question_text: str, question_path: str, scope: dict[str, Any] | None = None) -> dict[str, Any]:
    now = _now_iso()
    workflow_instance_id = f"v44_deliberation_instance_{uuid4().hex[:12]}"
    artifacts = [_artifact(station, question_text, workflow_instance_id, index) for index, station in enumerate(STATIONS)]
    nodes = [
        {
            "station_id": station["station_id"],
            "name": station["name"],
            "kind": station["kind"],
            "status": "completed",
            "attempts": [{"attempt_id": f"attempt_{station['station_id']}_1", "attempt": 1, "status": "completed", "created_at": now, "error": None}],
            "updated_at": now,
        }
        for station in STATIONS
    ]
    return {
        "workflow_instance_id": workflow_instance_id,
        "workflow_template_id": "v44_parallel_deliberation_template",
        "workflow_version_id": "v44_parallel_deliberation_version_1",
        "status": "completed",
        "backed_by": "v4_4_parallel_deliberation_runtime",
        "runtime_mode": "dev_local_deterministic_persona_runner",
        "scope": scope or {},
        "question_path": question_path,
        "nodes": nodes,
        "artifacts": artifacts,
        "quality_report": _quality_report(artifacts),
        "downstream_stale": [],
        "agent_mutation_allowed": False,
        "user_confirmed_required": True,
        "redaction_status": "redacted",
    }


def rerun_persona_station(run: dict[str, Any], station_id: str) -> dict[str, Any]:
    persona_ids = {persona["station_id"] for persona in PERSONAS}
    if station_id not in persona_ids:
        raise ValueError("V4.4 MVP only supports persona station rerun.")
    rerun = deepcopy(run)
    now = _now_iso()
    stale = []
    for node in rerun["nodes"]:
        attempts = list(node.get("attempts") or [])
        if node["station_id"] == station_id:
            attempts.append({"attempt_id": f"attempt_{station_id}_{len(attempts) + 1}", "attempt": len(attempts) + 1, "status": "completed", "created_at": now, "error": None})
            node["attempts"] = attempts
            node["status"] = "completed"
        if node["station_id"] in {"synthesis", "contradiction_review"}:
            node["status"] = "stale"
            stale.append({"station_id": node["station_id"], "reason": f"persona_rerun:{station_id}", "requires_user_confirmed_continue": True})
    rerun["status"] = "waiting_user_confirmation"
    rerun["downstream_stale"] = stale
    return rerun


def continue_deliberation_downstream(run: dict[str, Any]) -> dict[str, Any]:
    continued = deepcopy(run)
    now = _now_iso()
    for node in continued["nodes"]:
        if node["status"] == "stale":
            attempts = list(node.get("attempts") or [])
            attempts.append({"attempt_id": f"attempt_{node['station_id']}_{len(attempts) + 1}", "attempt": len(attempts) + 1, "status": "completed", "created_at": now, "error": None})
            node["attempts"] = attempts
            node["status"] = "completed"
    continued["status"] = "completed"
    continued["downstream_stale"] = []
    continued["quality_report"] = _quality_report(continued.get("artifacts") or [])
    return continued


def attempt_history(run: dict[str, Any]) -> dict[str, Any]:
    return {"workflow_instance_id": run["workflow_instance_id"], "stations": [{"station_id": node["station_id"], "status": node["status"], "attempts": node.get("attempts") or []} for node in run["nodes"]], "redaction_status": "redacted"}


def assert_no_forbidden_text(value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(value, str) else value
    for term in FORBIDDEN_TERMS:
        if term in text:
            raise AssertionError(f"Forbidden term leaked: {term}")


def _station_spec(station: dict[str, Any]) -> dict[str, Any]:
    descriptor = {
        "persona": station.get("persona") or station["kind"],
        "goal": "从指定视角讨论项目问题并输出可归因观点。",
        "model_ref": "dev_local_persona_model",
        "tool_refs": ["question_reader", "opinion_template"],
        "skill_refs": ["deliberation_opinion"],
    }
    return {"station_id": station["station_id"], "name": station["name"], "station_kind": station["kind"], "persona_descriptor": descriptor}


def _artifact(station: dict[str, Any], question_text: str, workflow_instance_id: str, index: int) -> dict[str, Any]:
    if station["station_id"] == "synthesis":
        content = "# 带归因的观点汇总\n\n- 产品策略：优先 Headless-first。\n- 架构视角：保留七平面事实源。\n- 风险视角：继续 No False Green 门禁。\n\n## Attribution\nproduct_strategist_agent, architecture_agent, risk_reviewer_agent\n"
        kind = "markdown"
    elif station["station_id"] == "contradiction_review":
        content = json.dumps({"status": "passed", "contradictions": ["Web Studio 体验投入 vs Headless-first 落地速度"], "unresolved_risks": ["future production auth", "future real model invocation"], "redaction_status": "redacted"}, ensure_ascii=False, indent=2)
        kind = "quality_report"
    else:
        persona = next((item for item in PERSONAS if item["station_id"] == station["station_id"]), None)
        viewpoint = persona["viewpoint"] if persona else "组织讨论轮次并分配 persona 视角。"
        content = f"# {station['name']}产物\n\n## 输入问题\n{_question_title(question_text)}\n\n## 观点\n{viewpoint}\n\n## 引用\n{station['station_id']}\n"
        kind = "markdown"
    return {"artifact_id": f"v44_artifact_{uuid4().hex[:12]}", "workflow_instance_id": workflow_instance_id, "station_id": station["station_id"], "name": station["artifact_name"], "kind": kind, "content": content, "metadata": {"redaction_status": "redacted"}, "redaction_status": "redacted"}


def _quality_report(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    names = {artifact["name"] for artifact in artifacts}
    expected = {station["artifact_name"] for station in STATIONS}
    return {"status": "passed" if expected.issubset(names) else "failed", "persona_count": len(PERSONAS), "artifact_coverage": {"expected": sorted(expected), "generated": sorted(names), "missing": sorted(expected - names)}, "redaction_status": "redacted"}


def _question_title(question_text: str) -> str:
    for line in question_text.splitlines():
        stripped = line.strip("# ").strip()
        if stripped:
            return stripped[:100]
    return "未命名讨论问题"


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()

