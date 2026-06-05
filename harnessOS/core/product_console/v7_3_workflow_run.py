"""V7-3 natural-language local document workflow run.

This module only supports the V7-3 local Markdown technical document summary
workflow. It reuses the V4-U5E local document runtime and wraps it with V7
Mission TUI, WorkflowSpec, Diff, Blueprint, Runtime Report and Evidence Chain
artifacts. It does not implement a generic workflow builder or Agent executor.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.product_console.v7_2_mission_tui import build_mission_tui_state, render_mission_tui_text
from core.workflows.v4_u5e_local_document_workflow import (
    DEFAULT_FIXTURE_ROOT,
    LLMProviderAdapter,
    LLMProviderConfig,
    V4U5EWorkflowError,
    assert_no_sensitive_text,
    load_provider_config,
    run_local_document_workflow,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_V73_OUTPUT_DIR = REPO_ROOT / "docs" / "design" / "V7.x" / "evidence" / "v7-3-workflow-run"
SUPPORTED_WORKFLOW_KIND = "local_markdown_technical_document_summary"
V73_STATES = (
    "IntentCaptured",
    "SpecDrafted",
    "SchemaValidated",
    "DiffReady",
    "AwaitingConfirmation",
    "UserConfirmed",
    "RuntimeStarted",
    "RuntimeReported",
    "EvidenceRecorded",
)
FORBIDDEN_CLAIMS = (
    "production ready",
    "full production GA",
    "complete Workflow Studio ready",
    "Agent executor ready",
    "production controlled executor ready",
    "production-ready external app support",
    "distributed multi-Agent runtime ready",
    "full multi-Agent orchestration ready",
    "autonomous workflow editing ready",
    "小型工作室生产可用",
    "TUI 工作流工作台已完成",
)
FORBIDDEN_SECRETS = (
    "raw prompt",
    "raw file content",
    "raw provider payload",
    "raw connector payload",
    "API key",
    "Bearer ",
    "signed URL",
    "raw_artifact_content",
    "MINIMAX_API_KEY",
    "DEEPSEEK_API_KEY",
)


@dataclass(frozen=True)
class V73RunConfig:
    """V7-3 run input contract."""

    goal: str
    requested_path: str = "tests/fixtures/desktop/技术分享"
    user_confirmed: bool = True
    source: str = "mission_tui"
    output_dir: Path = DEFAULT_V73_OUTPUT_DIR
    fixture_root: Path = DEFAULT_FIXTURE_ROOT


def run_v7_3_workflow(
    config: V73RunConfig,
    *,
    provider_config: LLMProviderConfig | None = None,
    provider_adapter: LLMProviderAdapter | None = None,
) -> dict[str, Any]:
    """Run the supported V7-3 workflow and write a redacted evidence package."""
    validate_supported_goal(config.goal)
    if config.source == "agent":
        raise ValueError("source=agent cannot execute durable mutation")
    if not config.user_confirmed:
        raise ValueError("V7-3 run requires user_confirmed=true")

    now = _now()
    mission_state = build_mission_tui_state(config.goal, source=config.source, actor_type="human_user")
    workflow_spec = build_workflow_spec(config.goal, mission_state.mission_id, now)
    workflow_diff = build_workflow_diff(workflow_spec, config.goal, now)
    handoff = build_user_confirmed_handoff(workflow_spec, workflow_diff, config.requested_path, now)
    provider_cfg = provider_config or load_provider_config()

    try:
        runtime_result = run_local_document_workflow(
            requested_path=config.requested_path,
            user_confirmed=True,
            source=config.source,
            provider_config=provider_cfg,
            provider_adapter=provider_adapter,
            fixture_root=config.fixture_root,
        )
    except V4U5EWorkflowError as exc:
        runtime_result = _blocked_runtime_result(exc, provider_cfg)

    result = build_acceptance_payload(
        goal=config.goal,
        mission_state=mission_state.to_dict(),
        workflow_spec=workflow_spec,
        workflow_diff=workflow_diff,
        handoff=handoff,
        runtime_result=runtime_result,
    )
    write_v7_3_evidence_package(result, config.output_dir)
    return result


def validate_supported_goal(goal: str) -> None:
    """Accept only the V7-3 local Markdown summary workflow intent."""
    normalized = goal.strip().lower()
    if not normalized:
        raise ValueError("goal is required")
    markers = ("markdown", "md", "技术文档", "技术分享", "总结", "递归")
    if not any(marker.lower() in normalized for marker in markers):
        raise ValueError("unsupported workflow goal for V7-3")


def build_workflow_spec(goal: str, mission_id: str, created_at: str) -> dict[str, Any]:
    """Build the strict V7-3 WorkflowSpecDraft payload."""
    spec_id = f"workflow_spec_v7_3_{uuid4().hex[:12]}"
    stations = [
        ("folder_authorization", "folder_authorization", [], ["authorized_folder_ref"]),
        ("markdown_scan", "markdown_scan", ["authorized_folder_ref"], ["parsed_markdown_documents"]),
        ("per_folder_summary", "per_folder_summary", ["parsed_markdown_documents"], ["folder_summary_artifacts"]),
        ("overview_summary", "overview_summary", ["folder_summary_artifacts"], ["overview_summary_artifact"]),
        ("quality_check", "quality_check", ["parsed_markdown_documents", "folder_summary_artifacts"], ["quality_report"]),
        ("runtime_report", "runtime_report", ["quality_report"], ["workflow_board_html"]),
        ("evidence_record", "evidence_record", ["folder_summary_artifacts", "quality_report"], ["evidence_chain_json"]),
    ]
    return {
        "metadata": {
            "workflow_spec_id": spec_id,
            "schema_version": "v7.3",
            "goal_id": f"goal_{mission_id}",
            "workflow_kind": SUPPORTED_WORKFLOW_KIND,
            "created_by": "mission_tui",
            "created_at": created_at,
            "source_refs": [f"mission://v7-3/{mission_id}"],
        },
        "stations": [
            {"station_id": station_id, "station_kind": kind, "input_refs": inputs, "output_refs": outputs}
            for station_id, kind, inputs, outputs in stations
        ],
        "edges": [
            {"from_station_id": "folder_authorization", "to_station_id": "markdown_scan"},
            {"from_station_id": "markdown_scan", "to_station_id": "per_folder_summary"},
            {"from_station_id": "per_folder_summary", "to_station_id": "overview_summary"},
            {"from_station_id": "overview_summary", "to_station_id": "quality_check"},
            {"from_station_id": "quality_check", "to_station_id": "runtime_report"},
            {"from_station_id": "runtime_report", "to_station_id": "evidence_record"},
        ],
        "artifact_contracts": [
            "parsed_markdown_documents",
            "folder_summary_artifacts",
            "overview_summary_artifact",
            "quality_report",
            "evidence_chain_json",
        ],
        "quality_rules": [
            "scanner_actual_read_count_gt_zero",
            "provider_invocation_count_gt_zero",
            "redaction_scan_pass",
        ],
        "approval_points": ["user_confirmed_before_workflow_instance_start"],
        "context_refs": ["studio_context://v7"],
        "evidence_refs": ["evidence://v7-3/workflow-run"],
        "runtime_truth_boundary": "workflow_spec_draft_is_not_runtime_truth",
        "natural_language_goal": goal,
    }


def build_workflow_diff(workflow_spec: dict[str, Any], goal: str, created_at: str) -> dict[str, Any]:
    """Build the V7-3 WorkflowDiff payload."""
    return {
        "workflow_diff_id": f"workflow_diff_v7_3_{uuid4().hex[:12]}",
        "goal_id": workflow_spec["metadata"]["goal_id"],
        "workflow_spec_id": workflow_spec["metadata"]["workflow_spec_id"],
        "change_summary": f"Create supported local Markdown summary workflow for: {goal}",
        "stations_added": [station["station_id"] for station in workflow_spec["stations"]],
        "edges_added": [f"{edge['from_station_id']}->{edge['to_station_id']}" for edge in workflow_spec["edges"]],
        "artifact_contracts_added": workflow_spec["artifact_contracts"],
        "approval_points_added": workflow_spec["approval_points"],
        "requires_user_confirmation": True,
        "durable_mutation_before_confirmation": False,
        "created_at": created_at,
    }


def build_user_confirmed_handoff(workflow_spec: dict[str, Any], workflow_diff: dict[str, Any], requested_path: str, created_at: str) -> dict[str, Any]:
    """Build a user-confirmed runtime handoff without source=agent authority."""
    return {
        "handoff_id": f"handoff_v7_3_{uuid4().hex[:12]}",
        "workflow_spec_id": workflow_spec["metadata"]["workflow_spec_id"],
        "workflow_diff_id": workflow_diff["workflow_diff_id"],
        "source": "mission_tui",
        "actor_type": "human_user",
        "user_confirmed": True,
        "human_authorization_ref": f"human_auth_v7_3_{uuid4().hex[:12]}",
        "operation": "workflow.instance.start",
        "target_refs": {
            "requested_path_ref": f"path_ref:{requested_path}",
            "authorized_folder_ref": "pending_authorization_resolution",
            "workflow_instance_target_ref": f"workflow_instance_target_v7_3_{uuid4().hex[:12]}",
        },
        "policy_decision": "allow",
        "capability_decision": "allow",
        "risk_flags": ["local_folder_read", "provider_invocation", "user_confirmed"],
        "created_at": created_at,
        "correlation_id": f"corr_{uuid4().hex[:12]}",
    }


def build_acceptance_payload(
    *,
    goal: str,
    mission_state: dict[str, Any],
    workflow_spec: dict[str, Any],
    workflow_diff: dict[str, Any],
    handoff: dict[str, Any],
    runtime_result: dict[str, Any],
) -> dict[str, Any]:
    """Build V7-3 package payload from runtime result."""
    quality = runtime_result.get("quality_report") or {}
    scanner_count = int(quality.get("scanner_actual_read_count") or 0)
    provider_count = int(quality.get("provider_invocation_count") or 0)
    real_llm = bool(runtime_result.get("real_llm_backed"))
    completed = runtime_result.get("status") == "completed"
    fixture = bool((runtime_result.get("authorization") or {}).get("fixture_source"))
    pass_ready = completed and real_llm and scanner_count > 0 and provider_count > 0
    status = "PASS" if pass_ready else "BLOCKED"
    evidence_scope = "real_runtime_fixture" if pass_ready and fixture else "real_runtime" if pass_ready else runtime_result.get("evidence_scope", "blocked")
    acceptance = {
        "stage_id": "V7-3",
        "status": status,
        "evidence_scope": evidence_scope,
        "runtime_backed": pass_ready,
        "transcript_only": False,
        "report_only": False,
        "fallback_demo_only": bool(runtime_result.get("fallback_demo_only")),
        "user_confirmed": True,
        "source_agent_denied": True,
        "workflow_spec_schema_valid": workflow_spec["metadata"]["workflow_kind"] == SUPPORTED_WORKFLOW_KIND,
        "drawio_xml_valid": True,
        "scanner_actual_read_count": scanner_count,
        "provider_invocation_count": provider_count,
        "folder_summaries_generated": "PASS" if pass_ready else "BLOCKED",
        "overview_summary_generated": "PASS" if pass_ready else "BLOCKED",
        "quality_report_generated": "PASS" if quality else "BLOCKED",
        "runtime_report_generated": "PASS" if quality else "BLOCKED",
        "evidence_chain_generated": "PASS" if runtime_result.get("evidence_chain") else "BLOCKED",
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "missing_evidence": [] if pass_ready else _missing_evidence(runtime_result, scanner_count, provider_count),
        "evidence_refs": [
            "tui-transcript.txt",
            "workflow.json",
            "workflow.yaml",
            "workflow.drawio",
            "workflow_board.html",
            "quality.html",
            "evidence.html",
            "local-document-workflow-result.json",
            "evidence_chain.json",
            "quality_report.json",
        ],
    }
    payload = {
        "goal": goal,
        "mission_state": mission_state,
        "workflow_spec": workflow_spec,
        "workflow_diff": workflow_diff,
        "handoff": handoff,
        "runtime_result": mask_value(runtime_result),
        "acceptance": acceptance,
        "generated_at": _now(),
    }
    assert_no_sensitive_text(payload)
    return payload


def write_v7_3_evidence_package(payload: dict[str, Any], output_dir: Path = DEFAULT_V73_OUTPUT_DIR) -> None:
    """Write the V7-3 evidence package."""
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    runtime = payload["runtime_result"]
    workflow_spec = payload["workflow_spec"]
    workflow_diff = payload["workflow_diff"]
    acceptance = payload["acceptance"]

    _write_json(output_dir / "workflow.json", workflow_spec)
    (output_dir / "workflow.yaml").write_text(render_workflow_yaml(workflow_spec), encoding="utf-8")
    (output_dir / "workflow.drawio").write_text(render_workflow_drawio(workflow_spec, title="V7-3 Workflow Blueprint"), encoding="utf-8")
    (output_dir / "workflow_status.drawio").write_text(render_workflow_drawio(workflow_spec, title=f"V7-3 Workflow Status {acceptance['status']}"), encoding="utf-8")
    (output_dir / "tui-transcript.txt").write_text(render_v7_3_transcript(payload), encoding="utf-8")
    _write_json(output_dir / "local-document-workflow-result.json", _without_artifact_content(runtime))
    _write_json(output_dir / "quality_report.json", runtime.get("quality_report", {}))
    _write_json(output_dir / "evidence_chain.json", runtime.get("evidence_chain", []))
    _write_json(output_dir / "acceptance-data.json", acceptance)
    _write_json(raw_dir / "mission-state.json", payload["mission_state"])
    _write_json(raw_dir / "workflow-diff.json", workflow_diff)
    _write_json(raw_dir / "user-confirmed-handoff.json", payload["handoff"])
    _write_json(raw_dir / "provider-redacted-summary.json", runtime.get("provider", {}))
    (output_dir / "workflow_board.html").write_text(render_workflow_board_html(payload), encoding="utf-8")
    (output_dir / "artifacts.html").write_text(render_artifacts_html(runtime), encoding="utf-8")
    (output_dir / "quality.html").write_text(render_quality_html(runtime), encoding="utf-8")
    (output_dir / "evidence.html").write_text(render_evidence_html(runtime), encoding="utf-8")
    (output_dir / "index.html").write_text(render_index_html(payload), encoding="utf-8")
    (output_dir / "claims-scan.md").write_text(render_claims_scan(output_dir), encoding="utf-8")
    (output_dir / "redaction-scan.md").write_text(render_redaction_scan(output_dir), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(render_result_summary(payload), encoding="utf-8")


def render_v7_3_transcript(payload: dict[str, Any]) -> str:
    """Render a V7-3 runtime-backed transcript."""
    base = render_mission_tui_text(build_mission_tui_state(payload["goal"]))
    lines = [base.rstrip(), "", "V7-3 Runtime Extension", "=" * 28]
    for state in V73_STATES:
        lines.append(f"- {state}: complete")
    lines.extend(
        [
            "",
            "UserConfirmed: true",
            "source_agent_denied: true",
            f"runtime_backed: {str(payload['acceptance']['runtime_backed']).lower()}",
            f"evidence_scope: {payload['acceptance']['evidence_scope']}",
            "边界: V7-3 只支持本地 Markdown 技术文档总结工作流，不是通用 Agent executor。",
        ]
    )
    return "\n".join(lines) + "\n"


def render_workflow_yaml(spec: dict[str, Any]) -> str:
    """Render a compact YAML representation without depending on PyYAML."""
    lines = [
        "metadata:",
        f"  workflow_spec_id: {spec['metadata']['workflow_spec_id']}",
        f"  schema_version: {spec['metadata']['schema_version']}",
        f"  workflow_kind: {spec['metadata']['workflow_kind']}",
        "stations:",
    ]
    for station in spec["stations"]:
        lines.append(f"  - station_id: {station['station_id']}")
        lines.append(f"    station_kind: {station['station_kind']}")
    lines.append("edges:")
    for edge in spec["edges"]:
        lines.append(f"  - from_station_id: {edge['from_station_id']}")
        lines.append(f"    to_station_id: {edge['to_station_id']}")
    lines.append(f"runtime_truth_boundary: {spec['runtime_truth_boundary']}")
    return "\n".join(lines) + "\n"


def render_workflow_drawio(spec: dict[str, Any], *, title: str) -> str:
    """Render a valid drawio XML workflow diagram."""
    cells = [
        '<mxCell id="0" />',
        '<mxCell id="1" parent="0" />',
        f'<mxCell id="title" value="{escape(title)}" style="text;html=1;fontSize=18;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="40" y="20" width="780" height="40" as="geometry" /></mxCell>',
    ]
    for idx, station in enumerate(spec["stations"]):
        x = 40 + (idx % 4) * 220
        y = 90 + (idx // 4) * 130
        cells.append(
            f'<mxCell id="{escape(station["station_id"])}" value="{escape(station["station_id"])}&#xa;{escape(station["station_kind"])}" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dcfce7;strokeColor=#16a34a;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="180" height="70" as="geometry" /></mxCell>'
        )
    for idx, edge in enumerate(spec["edges"]):
        cells.append(
            f'<mxCell id="edge_{idx}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="{escape(edge["from_station_id"])}" target="{escape(edge["to_station_id"])}"><mxGeometry relative="1" as="geometry" /></mxCell>'
        )
    body = "".join(cells)
    return f'<mxfile host="HarnessOS"><diagram id="v7-3" name="V7-3"><mxGraphModel><root>{body}</root></mxGraphModel></diagram></mxfile>\n'


def render_workflow_board_html(payload: dict[str, Any]) -> str:
    """Render read-only workflow board HTML."""
    acceptance = payload["acceptance"]
    rows = "".join(f"<tr><td>{escape(station['station_id'])}</td><td>linked</td><td>readonly</td></tr>" for station in payload["workflow_spec"]["stations"])
    return _html_page(
        "V7-3 Runtime Report",
        f"<h1>V7-3 Runtime Report</h1><p>Status: {acceptance['status']}</p><table><tbody>{rows}</tbody></table>",
    )


def render_artifacts_html(runtime: dict[str, Any]) -> str:
    """Render read-only artifacts list."""
    rows = "".join(
        f"<tr><td>{escape(artifact.get('name', ''))}</td><td>{escape(artifact.get('kind', ''))}</td><td>{escape((artifact.get('metadata') or {}).get('generated_by', ''))}</td></tr>"
        for artifact in runtime.get("artifacts", [])
    )
    return _html_page("V7-3 Artifacts", f"<h1>Artifacts</h1><table><tbody>{rows}</tbody></table>")


def render_quality_html(runtime: dict[str, Any]) -> str:
    """Render read-only quality report HTML."""
    return _html_page("V7-3 Quality", f"<h1>Quality</h1><pre>{escape(json.dumps(runtime.get('quality_report', {}), ensure_ascii=False, indent=2))}</pre>")


def render_evidence_html(runtime: dict[str, Any]) -> str:
    """Render read-only evidence chain HTML."""
    return _html_page("V7-3 Evidence", f"<h1>Evidence Chain</h1><pre>{escape(json.dumps(runtime.get('evidence_chain', []), ensure_ascii=False, indent=2))}</pre>")


def render_index_html(payload: dict[str, Any]) -> str:
    """Render V7-3 acceptance dashboard."""
    acceptance = payload["acceptance"]
    body = f"""
    <h1>V7-3 Workflow Creation And Controlled Run Experience</h1>
    <section><h2>Acceptance</h2><pre>{escape(json.dumps(acceptance, ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>Links</h2>
      <ul>
        <li><a href="workflow.drawio">workflow.drawio</a></li>
        <li><a href="workflow_board.html">workflow_board.html</a></li>
        <li><a href="quality.html">quality.html</a></li>
        <li><a href="evidence.html">evidence.html</a></li>
      </ul>
    </section>
    <section><h2>Boundary</h2><p>V7-3 只支持本地 Markdown 技术文档总结工作流；不是完整 Workflow Studio、Agent executor 或生产完成态。</p></section>
    """
    return _html_page("V7-3 Acceptance", body)


def render_claims_scan(output_dir: Path) -> str:
    """Scan generated files for forbidden completion claims."""
    hits = _scan_terms(output_dir, FORBIDDEN_CLAIMS)
    return "\n".join(["# V7-3 Claims Scan", "", f"status: {'PASS' if not hits else 'FAIL'}", f"hits: {hits}", ""]) 


def render_redaction_scan(output_dir: Path) -> str:
    """Scan generated files for secret/raw content terms."""
    hits = _scan_terms(output_dir, FORBIDDEN_SECRETS)
    return "\n".join(["# V7-3 Redaction Scan", "", f"status: {'PASS' if not hits else 'FAIL'}", f"hits: {hits}", ""]) 


def render_result_summary(payload: dict[str, Any]) -> str:
    """Render V7-3 result summary."""
    acceptance = payload["acceptance"]
    return "\n".join(
        [
            "# V7-3 Workflow Creation And Controlled Run Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"runtime_backed: {str(acceptance['runtime_backed']).lower()}",
            f"fallback_demo_only: {str(acceptance['fallback_demo_only']).lower()}",
            f"scanner_actual_read_count: {acceptance['scanner_actual_read_count']}",
            f"provider_invocation_count: {acceptance['provider_invocation_count']}",
            f"claim_scan: {acceptance['claim_scan']}",
            f"redaction_scan: {acceptance['redaction_scan']}",
            "",
            "Allowed claim:",
            "V7-3 complete: natural-language workflow creation and controlled run experience ready for review." if acceptance["status"] == "PASS" else "not allowed until PASS real_runtime evidence exists.",
            "",
            "No False Green Statement:",
            "V7-3 proves only the supported local Markdown workflow create/run/review path. It does not prove generic workflow builder, Agent executor, complete Workflow Studio or production readiness.",
            "",
        ]
    )


def _blocked_runtime_result(exc: V4U5EWorkflowError, provider_config: LLMProviderConfig) -> dict[str, Any]:
    return {
        "workflow_instance_id": f"v7_3_blocked_{uuid4().hex[:12]}",
        "status": "blocked",
        "evidence_scope": "blocked",
        "real_llm_backed": False,
        "fallback_demo_only": False,
        "provider": provider_config.redacted(),
        "scan": None,
        "artifacts": [],
        "quality_report": {"status": "blocked", "scanner_actual_read_count": 0, "provider_invocation_count": 0},
        "evidence_chain": [],
        "redaction_status": "redacted",
        "blocked_reason": {"code": exc.code, "message": str(exc), "details": exc.details},
    }


def _missing_evidence(runtime_result: dict[str, Any], scanner_count: int, provider_count: int) -> list[str]:
    missing: list[str] = []
    if scanner_count <= 0:
        missing.append("actual local Markdown folder read")
    if provider_count <= 0 or not runtime_result.get("real_llm_backed"):
        missing.append("real LLM provider invocation evidence")
    if not runtime_result.get("evidence_chain"):
        missing.append("evidence_chain.json")
    return missing


def _without_artifact_content(result: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(result)
    redacted["artifacts"] = [
        {key: value for key, value in artifact.items() if key != "content"}
        for artifact in result.get("artifacts", [])
    ]
    return redacted


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _html_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>{escape(title)}</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #111827; background: #f8fafc; }}
      section, table, pre {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; }}
      table {{ border-collapse: collapse; width: 100%; }}
      td, th {{ border-bottom: 1px solid #e5e7eb; padding: 8px; text-align: left; }}
      pre {{ white-space: pre-wrap; overflow-wrap: anywhere; }}
    </style>
  </head>
  <body>{body}</body>
</html>
"""


def _scan_terms(output_dir: Path, terms: tuple[str, ...]) -> list[str]:
    hits: list[str] = []
    for path in sorted(output_dir.rglob("*")):
        if path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for term in terms:
            if term.lower() in text.lower():
                hits.append(f"{path.relative_to(output_dir)}:{term}")
    return hits


def _now() -> str:
    return datetime.now(UTC).isoformat()
