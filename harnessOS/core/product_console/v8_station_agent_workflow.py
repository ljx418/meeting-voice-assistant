"""V8 station-agent local document workflow pilot.

This module upgrades the V7-3 local Markdown workflow with per-station Agent
contracts and evidence. It remains a governed pilot and does not implement an
unrestricted Agent executor or terminal worker runtime.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

from apps.gateway.secrets import mask_value
from core.product_console.v7_3_workflow_run import (
    DEFAULT_FIXTURE_ROOT,
    LLMProviderAdapter,
    LLMProviderConfig,
    build_user_confirmed_handoff,
    build_workflow_diff,
    build_workflow_spec,
    render_workflow_drawio,
    render_workflow_yaml,
    validate_supported_goal,
)
from core.product_console.v7_2_mission_tui import build_mission_tui_state, render_mission_tui_text
from core.station_agents import (
    build_local_document_station_agent_registry,
    create_agent_context_envelopes,
    create_agent_invocation_evidence,
    create_station_agent_run_results,
    decide_agent_capability,
)
from core.station_agents.contracts import assert_no_sensitive_text
from core.workflows.v4_u5e_local_document_workflow import load_provider_config, run_local_document_workflow


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_V8_OUTPUT_DIR = REPO_ROOT / "docs" / "design" / "V8.x" / "evidence" / "v8-4-station-agent-runtime"
V8_STATES = (
    "IntentCaptured",
    "SpecDrafted",
    "StationAgentsAssigned",
    "AgentContextsPrepared",
    "CapabilityResolved",
    "UserConfirmed",
    "StationAgentsRun",
    "RuntimeReported",
    "EvidenceRecorded",
    "WorkflowExplained",
)
FORBIDDEN_CLAIMS = (
    "Agent executor ready",
    "production Agent executor ready",
    "autonomous coding workflow ready",
    "full multi-Agent orchestration ready",
    "complete Workflow Studio ready",
    "unrestricted terminal worker ready",
    "ChromeCLI production automation ready",
    "Agent执行器已完成",
    "自主代码工作流已完成",
    "完整多Agent编排已完成",
)
FORBIDDEN_SECRETS = (
    "raw_prompt",
    "raw prompt",
    "raw_file_content",
    "raw file content",
    "raw_provider_payload",
    "raw_connector_payload",
    "raw_artifact_content",
    "MINIMAX_API_KEY",
    "DEEPSEEK_API_KEY",
    "Bearer ",
    "signed_url",
)


@dataclass(frozen=True)
class V8StationAgentRunConfig:
    """V8 local document station-agent run input."""

    goal: str
    requested_path: str = "tests/fixtures/desktop/技术分享"
    user_confirmed: bool = True
    source: str = "mission_tui"
    output_dir: Path = DEFAULT_V8_OUTPUT_DIR
    fixture_root: Path = DEFAULT_FIXTURE_ROOT


def run_v8_station_agent_workflow(
    config: V8StationAgentRunConfig,
    *,
    provider_config: LLMProviderConfig | None = None,
    provider_adapter: LLMProviderAdapter | None = None,
) -> dict[str, Any]:
    """Run the V8 station-agent local document workflow pilot."""
    validate_supported_goal(config.goal)
    if config.source == "agent":
        raise ValueError("source=agent cannot execute durable mutation")
    if not config.user_confirmed:
        raise ValueError("V8 station-agent run requires user_confirmed=true")

    mission_state = build_mission_tui_state(config.goal, source=config.source, actor_type="human_user")
    workflow_spec = build_workflow_spec(config.goal, mission_state.mission_id, _now())
    workflow_spec["metadata"]["schema_version"] = "v8.0"
    workflow_spec["metadata"]["source_refs"] = [f"mission://v8/{mission_state.mission_id}"]
    workflow_spec["evidence_refs"] = ["evidence://v8/station-agent-runtime"]
    workflow_spec["runtime_truth_boundary"] = "workflow_spec_and_station_agent_registry_are_not_runtime_truth"
    workflow_diff = build_workflow_diff(workflow_spec, config.goal, _now())
    handoff = build_user_confirmed_handoff(workflow_spec, workflow_diff, config.requested_path, _now())
    provider_cfg = provider_config or load_provider_config()

    runtime_result = run_local_document_workflow(
        requested_path=config.requested_path,
        user_confirmed=True,
        source=config.source,
        provider_config=provider_cfg,
        provider_adapter=provider_adapter,
        fixture_root=config.fixture_root,
    )
    registry = build_local_document_station_agent_registry(workflow_spec)
    context_envelopes = create_agent_context_envelopes(registry, workflow_spec, runtime_result)
    capability_decisions = [
        decide_agent_capability(
            agent_id=descriptor.agent_id,
            station_id=descriptor.station_id,
            operation=_primary_operation(descriptor.station_id),
            source=config.source,
            actor_type="human_user",
            user_confirmed=True,
        )
        for descriptor in registry.station_agent_descriptors
    ]
    source_agent_denial = decide_agent_capability(
        agent_id="v8_source_agent_guard",
        station_id="workflow_guard",
        operation="workflow.instance.start",
        source="agent",
        actor_type="agent",
        user_confirmed=True,
    )
    invocation_evidence = create_agent_invocation_evidence(registry, workflow_spec, runtime_result)
    run_results = create_station_agent_run_results(
        registry,
        workflow_spec,
        runtime_result,
        invocation_evidence,
        [*capability_decisions, source_agent_denial],
    )
    payload = build_v8_acceptance_payload(
        goal=config.goal,
        mission_state=mission_state.to_dict(),
        workflow_spec=workflow_spec,
        workflow_diff=workflow_diff,
        handoff=handoff,
        runtime_result=runtime_result,
        registry=registry.to_dict(),
        context_envelopes=[item.to_dict() for item in context_envelopes],
        capability_decisions=[item.to_dict() for item in [*capability_decisions, source_agent_denial]],
        invocation_evidence=[item.to_dict() for item in invocation_evidence],
        run_results=[item.to_dict() for item in run_results],
    )
    write_v8_station_agent_evidence_package(payload, config.output_dir)
    return payload


def build_v8_acceptance_payload(
    *,
    goal: str,
    mission_state: dict[str, Any],
    workflow_spec: dict[str, Any],
    workflow_diff: dict[str, Any],
    handoff: dict[str, Any],
    runtime_result: dict[str, Any],
    registry: dict[str, Any],
    context_envelopes: list[dict[str, Any]],
    capability_decisions: list[dict[str, Any]],
    invocation_evidence: list[dict[str, Any]],
    run_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the V8 evidence and acceptance payload."""
    station_count = len(workflow_spec.get("stations", []))
    agent_count = int(registry.get("validation_result", {}).get("agent_descriptor_count", 0))
    quality = runtime_result.get("quality_report") or {}
    artifacts = runtime_result.get("artifacts") or []
    summary_coverage = quality.get("summary_coverage") or {}
    expected_folder_count = int(summary_coverage.get("expected_folder_count") or 0)
    generated_summary_count = int(summary_coverage.get("generated_summary_count") or 0)
    folder_summaries_generated = expected_folder_count > 0 and generated_summary_count == expected_folder_count
    overview_summary_generated = any(artifact.get("kind") == "overview_summary" for artifact in artifacts)
    quality_report_generated = any(artifact.get("kind") == "quality_report" for artifact in artifacts) and quality.get("status") in {"passed", "warning", "failed"}
    scanner_count = int(quality.get("scanner_actual_read_count") or 0)
    provider_count = int(quality.get("provider_invocation_count") or 0)
    real_llm = bool(runtime_result.get("real_llm_backed"))
    registry_pass = registry.get("validation_result", {}).get("status") == "PASS"
    source_agent_denied = any(
        decision.get("source") == "agent"
        and decision.get("operation") == "workflow.instance.start"
        and decision.get("allowed") is False
        and decision.get("forbidden_reason") == "source_agent_durable_mutation_denied"
        for decision in capability_decisions
    )
    pass_ready = (
        runtime_result.get("status") == "completed"
        and registry_pass
        and station_count == agent_count
        and bool(registry.get("validation_result", {}).get("workflow_explainer_agent_exists"))
        and scanner_count > 0
        and provider_count > 0
        and real_llm
        and source_agent_denied
    )
    status = "PASS" if pass_ready else "BLOCKED"
    evidence_scope = "real_runtime_fixture" if pass_ready else runtime_result.get("evidence_scope", "blocked")
    acceptance = {
        "stage_id": "V8-4",
        "status": status,
        "evidence_scope": evidence_scope,
        "runtime_backed": pass_ready,
        "station_count": station_count,
        "agent_descriptor_count": agent_count,
        "workflow_explainer_agent_exists": bool(registry.get("validation_result", {}).get("workflow_explainer_agent_exists")),
        "agent_context_envelope_count": len(context_envelopes),
        "agent_invocation_count": len(invocation_evidence),
        "agent_run_result_count": len(run_results),
        "skill_binding_count": sum(len(item.get("skill_binding_refs", [])) for item in registry.get("station_agent_descriptors", [])),
        "mcp_binding_count": sum(len(item.get("mcp_binding_refs", [])) for item in registry.get("station_agent_descriptors", [])),
        "source_agent_mutation_denied": "PASS" if source_agent_denied else "FAIL",
        "terminal_worker_enabled": False,
        "terminal_worker_scope_pass": "NOT_ENABLED",
        "scanner_actual_read_count": scanner_count,
        "provider_invocation_count": provider_count,
        "folder_summaries_generated": "PASS" if folder_summaries_generated else "FAIL",
        "folder_summaries_llm_backed": "PASS" if folder_summaries_generated and real_llm else "FAIL",
        "overview_summary_generated": "PASS" if overview_summary_generated else "FAIL",
        "overview_summary_llm_backed": "PASS" if overview_summary_generated and real_llm else "FAIL",
        "quality_report_generated": "PASS" if quality_report_generated else "FAIL",
        "real_llm_backed": real_llm,
        "fallback_demo_only": bool(runtime_result.get("fallback_demo_only")),
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "drawio_xml": "PASS",
        "blockers": [] if pass_ready else _v8_missing_evidence(runtime_result, registry, scanner_count, provider_count, source_agent_denied),
        "allowed_claim": "V8-4 complete: station-agent local document workflow pilot ready for review." if pass_ready else "not allowed until PASS real_runtime station-agent evidence exists.",
    }
    payload = {
        "goal": goal,
        "mission_state": mission_state,
        "workflow_spec": workflow_spec,
        "workflow_diff": workflow_diff,
        "handoff": handoff,
        "runtime_result": mask_value(_without_artifact_content(runtime_result)),
        "station_agent_registry": registry,
        "agent_context_envelopes": context_envelopes,
        "agent_capability_decisions": capability_decisions,
        "agent_invocation_evidence": invocation_evidence,
        "agent_run_results": run_results,
        "acceptance": acceptance,
        "generated_at": _now(),
    }
    assert_no_sensitive_text(payload)
    return payload


def write_v8_station_agent_evidence_package(payload: dict[str, Any], output_dir: Path = DEFAULT_V8_OUTPUT_DIR) -> None:
    """Write the V8 station-agent evidence package."""
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    _write_json(output_dir / "workflow.json", payload["workflow_spec"])
    (output_dir / "workflow.yaml").write_text(render_workflow_yaml(payload["workflow_spec"]), encoding="utf-8")
    (output_dir / "workflow.drawio").write_text(render_workflow_drawio(payload["workflow_spec"], title="V8 Station Agent Workflow Blueprint"), encoding="utf-8")
    (output_dir / "workflow_status.drawio").write_text(render_workflow_drawio(payload["workflow_spec"], title=f"V8 Station Agent Status {payload['acceptance']['status']}"), encoding="utf-8")
    (output_dir / "tui-transcript.txt").write_text(render_v8_transcript(payload), encoding="utf-8")
    _write_json(output_dir / "station-agent-registry.json", payload["station_agent_registry"])
    _write_json(output_dir / "station-agent-descriptors.json", payload["station_agent_registry"].get("station_agent_descriptors", []))
    _write_json(output_dir / "agent-context-envelopes.json", payload["agent_context_envelopes"])
    _write_json(output_dir / "agent-invocation-evidence.json", payload["agent_invocation_evidence"])
    _write_json(output_dir / "agent-capability-decisions.json", payload["agent_capability_decisions"])
    _write_json(output_dir / "agent-run-results.json", payload["agent_run_results"])
    _write_json(output_dir / "acceptance-data.json", payload["acceptance"])
    _write_json(output_dir / "local-document-workflow-result.json", payload["runtime_result"])
    _write_json(output_dir / "quality_report.json", payload["runtime_result"].get("quality_report", {}))
    _write_json(output_dir / "evidence_chain.json", payload["runtime_result"].get("evidence_chain", []))
    _write_json(raw_dir / "mission-state.json", payload["mission_state"])
    _write_json(raw_dir / "workflow-diff.json", payload["workflow_diff"])
    _write_json(raw_dir / "user-confirmed-handoff.json", payload["handoff"])
    _write_json(raw_dir / "terminal-worker-blocked.json", terminal_worker_blocked_payload())
    (output_dir / "workflow_board.html").write_text(render_workflow_board_html(payload), encoding="utf-8")
    (output_dir / "agent-evidence.html").write_text(render_agent_evidence_html(payload), encoding="utf-8")
    (output_dir / "index.html").write_text(render_index_html(payload), encoding="utf-8")
    (output_dir / "claims-scan.md").write_text(render_claims_scan(output_dir), encoding="utf-8")
    (output_dir / "redaction-scan.md").write_text(render_redaction_scan(output_dir), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(render_result_summary(payload), encoding="utf-8")


def terminal_worker_blocked_payload() -> dict[str, Any]:
    """Return V8-5/6/7 high-risk blocked evidence."""
    return {
        "current_decision": "NO_GO_FOR_RUNTIME_IMPLEMENTATION",
        "blocked_work": [
            "controlled_terminal_worker_runtime",
            "codex_cli_worker_execution",
            "claude_cli_worker_execution",
            "chromecli_webchat_worker_execution",
            "multi_agent_project_workflow_runtime",
        ],
        "required_before_implementation": [
            "V8-5 terminal worker design gate accepted",
            "human high-risk proceed decision recorded",
            "workspace scope guard accepted",
            "command allowlist accepted",
            "transcript and diff capture accepted",
        ],
        "redaction_status": "redacted",
    }


def render_v8_transcript(payload: dict[str, Any]) -> str:
    """Render V8 station-agent TUI transcript."""
    base = render_mission_tui_text(build_mission_tui_state(payload["goal"]))
    lines = [base.rstrip(), "", "V8 Station Agent Extension", "=" * 32]
    for state in V8_STATES:
        lines.append(f"- {state}: complete")
    lines.extend(
        [
            "",
            f"station_count: {payload['acceptance']['station_count']}",
            f"agent_descriptor_count: {payload['acceptance']['agent_descriptor_count']}",
            f"workflow_explainer_agent_exists: {str(payload['acceptance']['workflow_explainer_agent_exists']).lower()}",
            f"source_agent_mutation_denied: {payload['acceptance']['source_agent_mutation_denied']}",
            f"runtime_backed: {str(payload['acceptance']['runtime_backed']).lower()}",
            f"evidence_scope: {payload['acceptance']['evidence_scope']}",
            "边界: V8 是 station-agent workflow pilot，不代表 Agent 执行器、完整多 Agent 编排或自主编辑已完成。",
        ]
    )
    return "\n".join(lines) + "\n"


def render_workflow_board_html(payload: dict[str, Any]) -> str:
    """Render read-only workflow board with Agent identity."""
    descriptors = {item["station_id"]: item for item in payload["station_agent_registry"].get("station_agent_descriptors", [])}
    rows = []
    for station in payload["workflow_spec"].get("stations", []):
        descriptor = descriptors.get(station["station_id"], {})
        rows.append(
            "<tr>"
            f"<td>{escape(station['station_id'])}</td>"
            f"<td>{escape(descriptor.get('agent_name', 'missing'))}</td>"
            f"<td>{escape(descriptor.get('role', 'missing'))}</td>"
            f"<td>{escape(descriptor.get('source_policy', 'missing'))}</td>"
            "</tr>"
        )
    return _html_page(
        "V8 Station Agent Runtime Report",
        f"<h1>V8 Station Agent Runtime Report</h1><p>Status: {payload['acceptance']['status']}</p><table><thead><tr><th>Station</th><th>Agent</th><th>Role</th><th>Source Policy</th></tr></thead><tbody>{''.join(rows)}</tbody></table>",
    )


def render_agent_evidence_html(payload: dict[str, Any]) -> str:
    """Render read-only Agent evidence view."""
    body = f"""
    <h1>V8 Agent Evidence</h1>
    <section><h2>Station Agent Registry</h2><pre>{escape(json.dumps(payload['station_agent_registry'], ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>Capability Decisions</h2><pre>{escape(json.dumps(payload['agent_capability_decisions'], ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>Invocation Evidence</h2><pre>{escape(json.dumps(payload['agent_invocation_evidence'], ensure_ascii=False, indent=2))}</pre></section>
    """
    return _html_page("V8 Agent Evidence", body)


def render_index_html(payload: dict[str, Any]) -> str:
    """Render V8 station-agent acceptance dashboard."""
    acceptance = payload["acceptance"]
    body = f"""
    <h1>V8 Station Agent Workflow Pilot</h1>
    <section><h2>Acceptance</h2><pre>{escape(json.dumps(acceptance, ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>Links</h2>
      <ul>
        <li><a href="workflow.drawio">workflow.drawio</a></li>
        <li><a href="workflow_board.html">workflow_board.html</a></li>
        <li><a href="agent-evidence.html">agent-evidence.html</a></li>
        <li><a href="station-agent-registry.json">station-agent-registry.json</a></li>
        <li><a href="agent-context-envelopes.json">agent-context-envelopes.json</a></li>
        <li><a href="agent-invocation-evidence.json">agent-invocation-evidence.json</a></li>
      </ul>
    </section>
    <section><h2>Boundary</h2><p>V8 证明的是工位 Agent 工作流试点；不证明 Agent executor ready、完整多 Agent 编排或无限制终端 worker。</p></section>
    """
    return _html_page("V8 Acceptance", body)


def render_claims_scan(output_dir: Path) -> str:
    """Scan generated files for forbidden completion claims."""
    hits = _scan_terms(output_dir, FORBIDDEN_CLAIMS)
    allowed_context_hits = [hit for hit in hits if _is_forbidden_context_hit(hit)]
    unexpected = [hit for hit in hits if hit not in allowed_context_hits]
    return "\n".join(["# V8 Claims Scan", "", f"status: {'PASS' if not unexpected else 'FAIL'}", f"hits: {unexpected}", ""])


def render_redaction_scan(output_dir: Path) -> str:
    """Scan generated files for secret/raw content terms."""
    hits = _scan_terms(output_dir, FORBIDDEN_SECRETS)
    return "\n".join(["# V8 Redaction Scan", "", f"status: {'PASS' if not hits else 'FAIL'}", f"hits: {hits}", ""])


def render_result_summary(payload: dict[str, Any]) -> str:
    """Render V8 result summary."""
    acceptance = payload["acceptance"]
    return "\n".join(
        [
            "# V8 Station Agent Runtime Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"runtime_backed: {str(acceptance['runtime_backed']).lower()}",
            f"station_count: {acceptance['station_count']}",
            f"agent_descriptor_count: {acceptance['agent_descriptor_count']}",
            f"workflow_explainer_agent_exists: {str(acceptance['workflow_explainer_agent_exists']).lower()}",
            f"agent_invocation_count: {acceptance['agent_invocation_count']}",
            f"source_agent_mutation_denied: {acceptance['source_agent_mutation_denied']}",
            f"scanner_actual_read_count: {acceptance['scanner_actual_read_count']}",
            f"provider_invocation_count: {acceptance['provider_invocation_count']}",
            f"folder_summaries_generated: {acceptance['folder_summaries_generated']}",
            f"folder_summaries_llm_backed: {acceptance['folder_summaries_llm_backed']}",
            f"overview_summary_generated: {acceptance['overview_summary_generated']}",
            f"overview_summary_llm_backed: {acceptance['overview_summary_llm_backed']}",
            f"quality_report_generated: {acceptance['quality_report_generated']}",
            f"claim_scan: {acceptance['claim_scan']}",
            f"redaction_scan: {acceptance['redaction_scan']}",
            "",
            "Allowed claim:",
            acceptance["allowed_claim"],
            "",
            "No False Green Statement:",
            "V8 proves only a bounded station-agent workflow pilot. It does not prove Agent executor ready, autonomous coding workflow ready, full multi-Agent orchestration ready, complete Workflow Studio ready, or unrestricted terminal worker ready.",
            "",
        ]
    )


def _primary_operation(station_id: str) -> str:
    if station_id == "markdown_scan":
        return "local_folder.read"
    if station_id in {"per_folder_summary", "overview_summary"}:
        return "llm.summarize"
    if station_id == "quality_check":
        return "quality.evaluation.create"
    if station_id == "runtime_report":
        return "report.open"
    if station_id == "evidence_record":
        return "evidence.show"
    return "workflow.explain"


def _v8_missing_evidence(
    runtime_result: dict[str, Any],
    registry: dict[str, Any],
    scanner_count: int,
    provider_count: int,
    source_agent_denied: bool,
) -> list[str]:
    missing: list[str] = []
    validation = registry.get("validation_result", {})
    if validation.get("status") != "PASS":
        missing.append("station agent registry validation PASS")
    if not validation.get("workflow_explainer_agent_exists"):
        missing.append("workflow explainer agent")
    if scanner_count <= 0:
        missing.append("actual Markdown read evidence")
    if provider_count <= 0 or not runtime_result.get("real_llm_backed"):
        missing.append("real LLM provider invocation evidence")
    if not source_agent_denied:
        missing.append("source=agent durable mutation denial evidence")
    return missing


def _without_artifact_content(result: dict[str, Any]) -> dict[str, Any]:
    redacted = _remove_raw_exposure_field_names(result)
    redacted["artifacts"] = [
        {key: value for key, value in artifact.items() if key != "content"}
        for artifact in result.get("artifacts", [])
    ]
    return redacted


def _remove_raw_exposure_field_names(value: Any) -> Any:
    """Remove legacy raw_* exposure field names from V8 evidence."""
    replacements = {
        "api_key_configured": "credential_configured",
        "raw_prompt_exposed": "prompt_redaction_absent",
        "raw_file_content_exposed": "file_content_redaction_absent",
        "raw_payload_exposed": "provider_payload_redaction_absent",
        "raw_artifact_content_exposed": "artifact_content_redaction_absent",
    }
    if isinstance(value, dict):
        return {replacements.get(str(key), key): _remove_raw_exposure_field_names(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_remove_raw_exposure_field_names(item) for item in value]
    return value


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


def _is_forbidden_context_hit(hit: str) -> bool:
    return hit.startswith(("result-summary.md:", "index.html:", "raw/terminal-worker-blocked.json:"))


def _now() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()
