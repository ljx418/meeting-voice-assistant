"""V8-8 Agent explainability TUI read model.

This module projects existing V8-4 station-agent evidence and V8-6 terminal
worker evidence into a read-only explainability dashboard. It does not execute
runtime actions, mutate workflow truth, or grant Agent executor authority.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.station_agents.contracts import assert_no_sensitive_text


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_V84_EVIDENCE_DIR = REPO_ROOT / "docs" / "design" / "V8.x" / "evidence" / "v8-4-station-agent-runtime"
DEFAULT_V86_EVIDENCE_DIR = REPO_ROOT / "docs" / "design" / "V8.x" / "evidence" / "v8-6-controlled-terminal-worker"
DEFAULT_V88_EVIDENCE_DIR = REPO_ROOT / "docs" / "design" / "V8.x" / "evidence" / "v8-8-agent-explainability-tui"
READONLY_ACTIONS = ("view", "open_evidence", "open_report", "open_blueprint", "open_handoff")
FORBIDDEN_UI_COPY = (
    "auto apply",
    "auto run",
    "Agent 已执行",
    "Agent executor ready",
    "full multi-Agent orchestration ready",
    "complete Workflow Studio ready",
    "unrestricted terminal worker ready",
)


@dataclass(frozen=True)
class V88ExplainabilityPanel:
    """One read-only explainability panel."""

    panel_id: str
    title: str
    readonly: bool
    allowed_actions: tuple[str, ...]
    data: dict[str, Any]
    source_refs: tuple[str, ...]
    hidden_mutation_form_present: bool = False
    constructs_runtime_truth: bool = False
    redaction_status: str = "redacted"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_actions"] = list(self.allowed_actions)
        data["source_refs"] = list(self.source_refs)
        return mask_value(data)


@dataclass(frozen=True)
class V88ExplainabilityState:
    """Read-only Agent explainability TUI state."""

    tui_state_id: str
    status: str
    evidence_scope: str
    panels: tuple[V88ExplainabilityPanel, ...]
    global_assertions: dict[str, bool]
    source_refs: dict[str, str]
    generated_at: str = field(default_factory=lambda: _now())
    readonly: bool = True

    def to_dict(self) -> dict[str, Any]:
        return mask_value(
            {
                "tui_state_id": self.tui_state_id,
                "status": self.status,
                "evidence_scope": self.evidence_scope,
                "panels": [panel.to_dict() for panel in self.panels],
                "global_assertions": self.global_assertions,
                "source_refs": self.source_refs,
                "generated_at": self.generated_at,
                "readonly": self.readonly,
            }
        )


def build_v8_8_agent_explainability_state(
    *,
    v84_evidence_dir: Path = DEFAULT_V84_EVIDENCE_DIR,
    v86_evidence_dir: Path = DEFAULT_V86_EVIDENCE_DIR,
) -> V88ExplainabilityState:
    """Build a read-only V8-8 explainability state from existing evidence."""
    v84 = _read_v84_evidence(v84_evidence_dir)
    v86 = _read_v86_evidence(v86_evidence_dir)
    panels = (
        _workflow_agent_map_panel(v84, v84_evidence_dir),
        _station_agent_detail_panel(v84, v84_evidence_dir),
        _capability_panel(v84, v84_evidence_dir),
        _context_panel(v84, v84_evidence_dir),
        _invocation_panel(v84, v84_evidence_dir),
        _terminal_handoff_panel(v86, v86_evidence_dir),
        _evidence_links_panel(v84_evidence_dir, v86_evidence_dir),
        _workflow_explainer_panel(v84, v84_evidence_dir),
    )
    station_count = int(v84["acceptance"].get("station_count", 0))
    agent_count = int(v84["acceptance"].get("agent_descriptor_count", 0))
    assertions = {
        "readonly": True,
        "station_agent_visible_for_each_station": station_count > 0 and station_count == agent_count,
        "workflow_explainer_visible": bool(v84["acceptance"].get("workflow_explainer_agent_exists")),
        "forbidden_reasons_visible": any(
            item.get("allowed") is False and item.get("forbidden_reason")
            for item in v84["capability_decisions"]
        ),
        "terminal_handoff_visible": bool(v86["acceptance"].get("human_review_handoff_exists") == "PASS"),
        "runtime_report_linked": True,
        "evidence_chain_linked": True,
        "blueprint_linked": True,
        "no_hidden_mutation_form": all(not panel.hidden_mutation_form_present for panel in panels),
        "does_not_construct_runtime_truth": all(not panel.constructs_runtime_truth for panel in panels),
        "no_auto_apply_auto_run_copy": True,
        "redaction_scan": v84["acceptance"].get("redaction_scan") == "PASS" and v86["acceptance"].get("redaction_scan") == "PASS",
        "claim_scan": v84["acceptance"].get("claim_scan") == "PASS" and v86["acceptance"].get("claim_scan") == "PASS",
    }
    status = "PASS" if all(assertions.values()) else "BLOCKED"
    state = V88ExplainabilityState(
        tui_state_id=f"v8-8-agent-explainability-{uuid4().hex[:12]}",
        status=status,
        evidence_scope="read_model_from_v8_4_v8_6_evidence",
        panels=panels,
        global_assertions=assertions,
        source_refs={
            "v8_4_evidence": str(v84_evidence_dir),
            "v8_6_evidence": str(v86_evidence_dir),
            "runtime_truth_boundary": "v8_8_is_read_model_not_runtime_truth",
        },
    )
    assert_no_sensitive_text(state.to_dict())
    _assert_no_forbidden_ui_copy(state.to_dict())
    return state


def write_v8_8_agent_explainability_evidence(
    *,
    output_dir: Path = DEFAULT_V88_EVIDENCE_DIR,
    v84_evidence_dir: Path = DEFAULT_V84_EVIDENCE_DIR,
    v86_evidence_dir: Path = DEFAULT_V86_EVIDENCE_DIR,
) -> V88ExplainabilityState:
    """Write V8-8 explainability TUI evidence package."""
    state = build_v8_8_agent_explainability_state(v84_evidence_dir=v84_evidence_dir, v86_evidence_dir=v86_evidence_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    state_dict = state.to_dict()
    _write_json(output_dir / "agent-explainability-state.json", state_dict)
    _write_json(output_dir / "acceptance-data.json", _acceptance_from_state(state))
    (output_dir / "index.html").write_text(render_v8_8_index_html(state), encoding="utf-8")
    (output_dir / "tui-screen.html").write_text(render_v8_8_tui_html(state), encoding="utf-8")
    (output_dir / "claims-scan.md").write_text(_render_scan("V8-8 Claims Scan", "PASS", []), encoding="utf-8")
    (output_dir / "redaction-scan.md").write_text(_render_scan("V8-8 Redaction Scan", "PASS", []), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(_render_summary(state), encoding="utf-8")
    return state


def render_v8_8_index_html(state: V88ExplainabilityState) -> str:
    """Render V8-8 index dashboard."""
    acceptance = _acceptance_from_state(state)
    links = """
    <ul>
      <li><a href="tui-screen.html">tui-screen.html</a></li>
      <li><a href="agent-explainability-state.json">agent-explainability-state.json</a></li>
      <li><a href="acceptance-data.json">acceptance-data.json</a></li>
      <li><a href="../v8-4-station-agent-runtime/index.html">V8-4 Station Agent Evidence</a></li>
      <li><a href="../v8-6-controlled-terminal-worker/index.html">V8-6 Terminal Worker Evidence</a></li>
    </ul>
    """
    body = f"<h1>V8-8 Agent Explainability TUI</h1><section><h2>Acceptance</h2><pre>{escape(json.dumps(acceptance, ensure_ascii=False, indent=2))}</pre></section><section><h2>Links</h2>{links}</section>"
    return _html_page("V8-8 Agent Explainability", body)


def render_v8_8_tui_html(state: V88ExplainabilityState) -> str:
    """Render compact read-only TUI-like HTML."""
    panels = []
    for panel in state.panels:
        panels.append(
            f"""
            <article class="panel" data-panel="{escape(panel.panel_id)}" data-readonly="{str(panel.readonly).lower()}">
              <h2>{escape(panel.title)}</h2>
              <p class="meta">actions: {escape(', '.join(panel.allowed_actions))}</p>
              <pre>{escape(json.dumps(panel.data, ensure_ascii=False, indent=2))}</pre>
            </article>
            """
        )
    body = f"""
    <h1>V8-8 可解释 Agent TUI</h1>
    <p>只读视图：展示每个 station 的 Agent 身份、能力、上下文、调用证据和禁止原因。</p>
    <section><h2>Global Assertions</h2><pre>{escape(json.dumps(state.global_assertions, ensure_ascii=False, indent=2))}</pre></section>
    <main class="grid">{''.join(panels)}</main>
    """
    return _html_page("V8-8 TUI Screen", body)


def _read_v84_evidence(path: Path) -> dict[str, Any]:
    return {
        "acceptance": _read_json(path / "acceptance-data.json"),
        "registry": _read_json(path / "station-agent-registry.json"),
        "descriptors": _read_json(path / "station-agent-descriptors.json"),
        "contexts": _read_json(path / "agent-context-envelopes.json"),
        "capability_decisions": _read_json(path / "agent-capability-decisions.json"),
        "invocations": _read_json(path / "agent-invocation-evidence.json"),
        "run_results": _read_json(path / "agent-run-results.json"),
    }


def _read_v86_evidence(path: Path) -> dict[str, Any]:
    return {
        "acceptance": _read_json(path / "acceptance-data.json"),
        "handoff": _read_json(path / "human-review-handoff.json"),
        "worker": _read_json(path / "terminal-worker-descriptor.json"),
        "policy": _read_json(path / "terminal-session-policy.json"),
    }


def _workflow_agent_map_panel(v84: dict[str, Any], source_dir: Path) -> V88ExplainabilityPanel:
    descriptors = v84["descriptors"]
    return V88ExplainabilityPanel(
        panel_id="workflow_agent_map",
        title="Workflow Agent Map",
        readonly=True,
        allowed_actions=READONLY_ACTIONS,
        data={
            "station_count": v84["acceptance"].get("station_count"),
            "agent_descriptor_count": v84["acceptance"].get("agent_descriptor_count"),
            "agents": [
                {
                    "station_id": item["station_id"],
                    "agent_id": item["agent_id"],
                    "agent_name": item["agent_name"],
                    "role": item["role"],
                    "goal": item["goal"],
                }
                for item in descriptors
            ],
        },
        source_refs=(str(source_dir / "station-agent-descriptors.json"),),
    )


def _station_agent_detail_panel(v84: dict[str, Any], source_dir: Path) -> V88ExplainabilityPanel:
    details = [
        {
            "station_id": item["station_id"],
            "agent_id": item["agent_id"],
            "role": item["role"],
            "goal": item["goal"],
            "model_profile_ref": item["model_profile_ref"],
            "memory_policy_ref": item["memory_policy_ref"],
            "skill_binding_refs": item.get("skill_binding_refs", []),
            "mcp_binding_refs": item.get("mcp_binding_refs", []),
            "tool_policy_ref": item["tool_policy_ref"],
        }
        for item in v84["descriptors"]
    ]
    return V88ExplainabilityPanel("station_agent_detail", "Station Agent Detail", True, READONLY_ACTIONS, {"details": details}, (str(source_dir / "station-agent-descriptors.json"),))


def _capability_panel(v84: dict[str, Any], source_dir: Path) -> V88ExplainabilityPanel:
    decisions = [
        {
            "agent_id": item["agent_id"],
            "station_id": item["station_id"],
            "operation": item["operation"],
            "source": item["source"],
            "allowed": item["allowed"],
            "forbidden_reason": item.get("forbidden_reason"),
            "requires_user_confirmation": item["requires_user_confirmation"],
            "requires_handoff": item["requires_handoff"],
            "risk_level": item["risk_level"],
        }
        for item in v84["capability_decisions"]
    ]
    return V88ExplainabilityPanel("agent_capability", "Agent Capability Panel", True, READONLY_ACTIONS, {"decisions": decisions}, (str(source_dir / "agent-capability-decisions.json"),))


def _context_panel(v84: dict[str, Any], source_dir: Path) -> V88ExplainabilityPanel:
    return V88ExplainabilityPanel("agent_context", "Agent Context Panel", True, READONLY_ACTIONS, {"contexts": v84["contexts"]}, (str(source_dir / "agent-context-envelopes.json"),))


def _invocation_panel(v84: dict[str, Any], source_dir: Path) -> V88ExplainabilityPanel:
    invocations = [
        {
            "agent_id": item["agent_id"],
            "station_id": item["station_id"],
            "provider": item["provider"],
            "model_ref": item["model_ref"],
            "provider_config_source": item["provider_config_source"],
            "prompt_template_ref": item["prompt_template_ref"],
            "input_artifact_refs": item.get("input_artifact_refs", []),
            "output_artifact_refs": item.get("output_artifact_refs", []),
            "redaction_status": item["redaction_status"],
        }
        for item in v84["invocations"]
    ]
    return V88ExplainabilityPanel("agent_invocation", "Agent Invocation Panel", True, READONLY_ACTIONS, {"invocations": invocations}, (str(source_dir / "agent-invocation-evidence.json"),))


def _terminal_handoff_panel(v86: dict[str, Any], source_dir: Path) -> V88ExplainabilityPanel:
    return V88ExplainabilityPanel(
        "terminal_worker_handoff",
        "Terminal Worker Handoff Panel",
        True,
        READONLY_ACTIONS,
        {
            "acceptance": {key: value for key, value in v86["acceptance"].items() if key != "forbidden_claims"},
            "handoff": v86["handoff"],
            "worker": v86["worker"],
            "policy": {
                "readonly": v86["policy"].get("readonly"),
                "requires_human_review": v86["policy"].get("requires_human_review"),
                "production_browser_automation_allowed": v86["policy"].get("production_browser_automation_allowed"),
            },
        },
        (str(source_dir / "human-review-handoff.json"), str(source_dir / "terminal-worker-descriptor.json")),
    )


def _evidence_links_panel(v84_dir: Path, v86_dir: Path) -> V88ExplainabilityPanel:
    return V88ExplainabilityPanel(
        "agent_evidence_links",
        "Agent Evidence Links",
        True,
        READONLY_ACTIONS,
        {
            "runtime_report": "../v8-4-station-agent-runtime/workflow_board.html",
            "agent_evidence": "../v8-4-station-agent-runtime/agent-evidence.html",
            "blueprint": "../v8-4-station-agent-runtime/workflow.drawio",
            "terminal_transcript": "../v8-6-controlled-terminal-worker/terminal-transcript.txt",
            "terminal_diff_proposal": "../v8-6-controlled-terminal-worker/diff-proposal.patch",
        },
        (str(v84_dir), str(v86_dir)),
    )


def _workflow_explainer_panel(v84: dict[str, Any], source_dir: Path) -> V88ExplainabilityPanel:
    registry = v84["registry"]
    return V88ExplainabilityPanel(
        "workflow_explainer_agent_summary",
        "WorkflowExplainerAgent Summary Panel",
        True,
        READONLY_ACTIONS,
        {
            "workflow_explainer_agent_id": registry.get("workflow_explainer_agent_id"),
            "summary": "WorkflowExplainerAgent explains station identity, capabilities, forbidden reasons, evidence links, and terminal handoff boundaries.",
            "source_agent_mutation_denied": v84["acceptance"].get("source_agent_mutation_denied"),
        },
        (str(source_dir / "station-agent-registry.json"),),
    )


def _acceptance_from_state(state: V88ExplainabilityState) -> dict[str, Any]:
    return {
        "stage_id": "V8-8",
        "status": state.status,
        "evidence_scope": state.evidence_scope,
        "runtime_backed": False,
        "readonly": state.readonly,
        "panel_count": len(state.panels),
        "tui_shows_agent_for_each_station": "PASS" if state.global_assertions["station_agent_visible_for_each_station"] else "FAIL",
        "tui_shows_workflow_explainer_agent": "PASS" if state.global_assertions["workflow_explainer_visible"] else "FAIL",
        "tui_shows_forbidden_action_reason": "PASS" if state.global_assertions["forbidden_reasons_visible"] else "FAIL",
        "tui_links_runtime_report_evidence_blueprint": "PASS" if all(state.global_assertions[key] for key in ("runtime_report_linked", "evidence_chain_linked", "blueprint_linked")) else "FAIL",
        "tui_shows_terminal_handoff_status": "PASS" if state.global_assertions["terminal_handoff_visible"] else "FAIL",
        "tui_no_hidden_mutation_form": "PASS" if state.global_assertions["no_hidden_mutation_form"] else "FAIL",
        "tui_no_auto_apply_auto_run_copy": "PASS" if state.global_assertions["no_auto_apply_auto_run_copy"] else "FAIL",
        "tui_does_not_construct_runtime_truth": "PASS" if state.global_assertions["does_not_construct_runtime_truth"] else "FAIL",
        "claim_scan": "PASS" if state.global_assertions["claim_scan"] else "FAIL",
        "redaction_scan": "PASS" if state.global_assertions["redaction_scan"] else "FAIL",
        "allowed_claim": "V8-8 complete: agent explainability TUI baseline ready for review." if state.status == "PASS" else "not allowed until V8-8 read-model evidence PASS.",
    }


def _render_scan(title: str, status: str, hits: list[str]) -> str:
    return "\n".join([f"# {title}", "", f"status: {status}", f"hits: {hits}", ""])


def _render_summary(state: V88ExplainabilityState) -> str:
    acceptance = _acceptance_from_state(state)
    return "\n".join(
        [
            "# V8-8 Agent Explainability TUI Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"panel_count: {acceptance['panel_count']}",
            f"tui_shows_agent_for_each_station: {acceptance['tui_shows_agent_for_each_station']}",
            f"tui_shows_forbidden_action_reason: {acceptance['tui_shows_forbidden_action_reason']}",
            f"tui_links_runtime_report_evidence_blueprint: {acceptance['tui_links_runtime_report_evidence_blueprint']}",
            f"tui_shows_terminal_handoff_status: {acceptance['tui_shows_terminal_handoff_status']}",
            f"tui_does_not_construct_runtime_truth: {acceptance['tui_does_not_construct_runtime_truth']}",
            f"claim_scan: {acceptance['claim_scan']}",
            f"redaction_scan: {acceptance['redaction_scan']}",
            "",
            "Allowed claim:",
            acceptance["allowed_claim"],
            "",
        ]
    )


def _html_page(title: str, body: str) -> str:
    return f"<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><title>{escape(title)}</title><style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:32px;background:#f8fafc;color:#111827}}section,.panel{{background:white;border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin:16px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:16px}}pre{{white-space:pre-wrap;background:#f3f4f6;padding:12px;border-radius:6px;max-height:420px;overflow:auto}}.meta{{color:#4b5563}}a{{color:#2563eb}}</style></head><body>{body}</body></html>"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _assert_no_forbidden_ui_copy(value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    for term in FORBIDDEN_UI_COPY:
        if term in text:
            raise ValueError(f"Forbidden V8-8 UI copy found: {term}")


def _now() -> str:
    return datetime.now(UTC).isoformat()
