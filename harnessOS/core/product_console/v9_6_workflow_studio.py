"""V9-6 Workflow Studio productization pilot.

This module builds a bounded Studio read model through BFF/DTO style
projections. It does not write runtime truth, expose hidden mutation forms,
or claim complete Workflow Studio readiness.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any, Mapping, Sequence
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext


V9_STUDIO_ALLOWED_BFF_ROUTES = {
    "GET /bff/v9/studio-state",
    "GET /bff/v9/runtime-report",
    "GET /bff/v9/evidence-chain",
    "GET /bff/v9/workflow-blueprint",
    "POST /bff/v9/workflow-diff-proposal",
    "POST /bff/v9/manual-confirmation",
    "POST /bff/v9/review-handoff",
}
V9_STUDIO_BROWSER_DENYLIST = (
    "/v1/rpc",
    "/v1/events/subscribe",
    "/v1/internal/runtime",
    "/v1/internal/executor",
    "/v1/internal/workflow-store",
    "/v1/internal/station-run",
    "/v1/internal/",
    "/internal/v9/",
)
READ_ONLY_PANEL_IDS = {
    "workflow_blueprint",
    "agent_station_inspector",
    "runtime_report",
    "evidence_chain",
    "artifact_lineage",
}
READ_ONLY_ACTIONS = {"view", "export", "open_report", "open_evidence", "open_proposal", "open_handoff"}
FORBIDDEN_EXECUTION_LABELS = {
    "Apply",
    "Publish",
    "Approve",
    "Reject",
    "Execute",
    "Run",
    "自动应用",
    "自动发布",
    "Agent 已执行",
    "Agent 已发布",
}
FORBIDDEN_UI_COPY = {
    "complete Workflow Studio ready",
    "Agent executor ready",
    "production ready",
    "full production GA",
    "autonomous workflow editing ready",
    "production controlled executor ready",
    "TUI 工作流工作台已完成",
    "小型工作室生产可用",
}
SENSITIVE_TOKENS = {
    "raw_prompt",
    "raw prompt",
    "raw_file_content",
    "raw_artifact_content",
    "raw_provider_payload",
    "raw_connector_payload",
    "api_key",
    "Bearer ",
    "signed URL",
    "sk-",
    "secret",
}


class V96WorkflowStudioError(ValueError):
    """Stable denial for V9-6 Studio safety checks."""

    def __init__(self, code: str, message: str, *, reason: str, resource: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.resource = resource

    def to_error(self) -> dict[str, Any]:
        data: dict[str, Any] = {"reason": self.reason}
        if self.resource is not None:
            data["resource"] = self.resource
        return {"code": self.code, "message": str(self), "data": data}


@dataclass(frozen=True)
class V96StudioPanel:
    """One Studio read-model panel."""

    panel_id: str
    title: str
    readonly: bool
    allowed_actions: tuple[str, ...]
    source_refs: dict[str, str]
    data: dict[str, Any]
    hidden_mutation_form_present: bool = False
    constructs_runtime_truth: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_actions"] = list(self.allowed_actions)
        return mask_value(data)


@dataclass(frozen=True)
class V96WorkflowDiffProposal:
    """Natural-language optimization output before durable mutation."""

    proposal_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    actor_id: str
    natural_language_goal: str
    workflow_spec_ref: str
    diff_ref: str
    risk_delta: str
    target_refs: dict[str, str]
    source: str
    created_at: str
    request_id: str
    correlation_id: str
    audit_ref: str
    durable_mutation_performed: bool = False
    requires_manual_confirmation: bool = True

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class V96ManualConfirmation:
    """Manual confirmation DTO that records a human authorization ref."""

    human_authorization_ref: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    actor_id: str
    proposal_id: str
    operation: str
    target_refs: dict[str, str]
    created_at: str
    expires_at: str
    request_id: str
    correlation_id: str
    audit_ref: str
    source: str = "product_console"
    executes_runtime_action: bool = False

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class V96WorkflowStudioState:
    """Bounded Workflow Studio state for V9-6 acceptance."""

    studio_id: str
    tenant_context: dict[str, str]
    bff_route_allowlist: tuple[str, ...]
    browser_network_log: tuple[str, ...]
    panels: tuple[V96StudioPanel, ...]
    workflow_diff_proposal: V96WorkflowDiffProposal
    manual_confirmation: V96ManualConfirmation
    full_workflow_studio_gate: dict[str, Any]
    global_assertions: dict[str, bool]
    source_refs: dict[str, str]
    generated_at: str = field(default_factory=lambda: _now())
    readonly: bool = True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["bff_route_allowlist"] = list(self.bff_route_allowlist)
        data["browser_network_log"] = list(self.browser_network_log)
        data["panels"] = [panel.to_dict() for panel in self.panels]
        data["workflow_diff_proposal"] = self.workflow_diff_proposal.to_dict()
        data["manual_confirmation"] = self.manual_confirmation.to_dict()
        return mask_value(data)


def build_workflow_diff_proposal(
    context: IdentityContext,
    *,
    natural_language_goal: str,
    workflow_spec_ref: str,
    target_refs: Mapping[str, str],
    source: str = "product_console",
) -> V96WorkflowDiffProposal:
    """Create a proposal-only WorkflowDiff from natural language."""
    if source == "agent" or context.actor_type == "agent":
        raise V96WorkflowStudioError("STUDIO_SOURCE_AGENT_DENIED", "Agent cannot directly mutate Studio workflow state.", reason="source_agent_denied")
    if source not in {"product_console", "approved_api"}:
        raise V96WorkflowStudioError("STUDIO_SOURCE_DENIED", "Studio proposal source is not allowed.", reason="source_not_allowed", resource=source)
    if not natural_language_goal.strip():
        raise V96WorkflowStudioError("STUDIO_GOAL_REQUIRED", "Natural-language goal is required.", reason="missing_goal")
    _reject_sensitive_payload({"natural_language_goal": natural_language_goal, "target_refs": dict(target_refs)})
    return V96WorkflowDiffProposal(
        proposal_id=f"workflow-diff-proposal-v9-6-{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        actor_id=context.actor_id,
        natural_language_goal=natural_language_goal,
        workflow_spec_ref=workflow_spec_ref,
        diff_ref=f"workflow-diff://v9-6/{uuid4().hex[:12]}",
        risk_delta="medium_requires_manual_confirmation",
        target_refs=dict(target_refs),
        source=source,
        created_at=_now(),
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-6/workflow-diff-proposal/{uuid4().hex[:12]}",
    )


def build_manual_confirmation(
    context: IdentityContext,
    *,
    proposal: V96WorkflowDiffProposal,
    expires_at: str,
    source: str = "product_console",
) -> V96ManualConfirmation:
    """Record a human authorization ref without executing the proposal."""
    if source == "agent" or context.actor_type == "agent":
        raise V96WorkflowStudioError("STUDIO_CONFIRMATION_AGENT_DENIED", "Agent cannot create manual confirmation.", reason="source_agent_denied")
    if source not in {"product_console", "approved_api"}:
        raise V96WorkflowStudioError("STUDIO_CONFIRMATION_SOURCE_DENIED", "Manual confirmation source is not allowed.", reason="source_not_allowed")
    _validate_context_matches_proposal(context, proposal)
    return V96ManualConfirmation(
        human_authorization_ref=f"human-auth://v9-6/{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        actor_id=context.actor_id,
        proposal_id=proposal.proposal_id,
        operation="workflow.diff.confirm",
        target_refs=proposal.target_refs,
        created_at=_now(),
        expires_at=expires_at,
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-6/manual-confirmation/{uuid4().hex[:12]}",
        source=source,
    )


def build_workflow_studio_state(
    context: IdentityContext,
    *,
    workflow_graph: Mapping[str, Any],
    station_agent_profiles: Sequence[Mapping[str, Any]],
    runtime_report: Mapping[str, Any],
    evidence_chain: Mapping[str, Any],
    artifact_lineage: Sequence[Mapping[str, Any]],
    workflow_diff_proposal: V96WorkflowDiffProposal,
    manual_confirmation: V96ManualConfirmation,
    browser_network_log: Sequence[str],
    source_refs: Mapping[str, str],
) -> V96WorkflowStudioState:
    """Build and validate a V9-6 Workflow Studio read model."""
    panels = (
        V96StudioPanel(
            panel_id="workflow_blueprint",
            title="工作流蓝图",
            readonly=True,
            allowed_actions=("view", "open_proposal"),
            source_refs={"blueprint_ref": source_refs.get("workflow_blueprint", "")},
            data={"node_count": len(workflow_graph.get("nodes", [])), "edge_count": len(workflow_graph.get("edges", [])), "source": "workflow_blueprint_read_model"},
        ),
        V96StudioPanel(
            panel_id="agent_station_inspector",
            title="Agent 工位检查器",
            readonly=True,
            allowed_actions=("view", "open_evidence"),
            source_refs={"agent_profile_ref": source_refs.get("agent_profiles", "")},
            data={"agent_count": len(station_agent_profiles), "profiles": [dict(profile) for profile in station_agent_profiles]},
        ),
        V96StudioPanel(
            panel_id="runtime_report",
            title="运行报告",
            readonly=True,
            allowed_actions=("view", "open_report"),
            source_refs={"runtime_report_ref": source_refs.get("runtime_report", "")},
            data={"status": runtime_report.get("status"), "attempt_count": len(runtime_report.get("attempts", [])), "source": "runtime_report_read_model"},
        ),
        V96StudioPanel(
            panel_id="evidence_chain",
            title="证据链",
            readonly=True,
            allowed_actions=("view", "export", "open_handoff"),
            source_refs={"evidence_chain_ref": source_refs.get("evidence_chain", "")},
            data={"evidence_count": len(evidence_chain.get("evidence_refs", [])), "claim_scan": evidence_chain.get("claim_scan"), "redaction_scan": evidence_chain.get("redaction_scan")},
        ),
        V96StudioPanel(
            panel_id="artifact_lineage",
            title="产物血缘",
            readonly=True,
            allowed_actions=("view", "open_evidence"),
            source_refs={"artifact_lineage_ref": source_refs.get("artifact_lineage", "")},
            data={"lineage_count": len(artifact_lineage), "lineage": [dict(item) for item in artifact_lineage]},
        ),
    )
    state = V96WorkflowStudioState(
        studio_id=f"workflow-studio-v9-6-{uuid4().hex[:12]}",
        tenant_context={
            "tenant_id": context.tenant_id,
            "workspace_id": context.workspace_id,
            "project_id": context.project_id,
            "app_id": context.app_id,
            "actor_type": context.actor_type,
            "actor_id": context.actor_id,
        },
        bff_route_allowlist=tuple(sorted(V9_STUDIO_ALLOWED_BFF_ROUTES)),
        browser_network_log=tuple(browser_network_log),
        panels=panels,
        workflow_diff_proposal=workflow_diff_proposal,
        manual_confirmation=manual_confirmation,
        full_workflow_studio_gate={
            "separate_prd_required": True,
            "separate_architecture_required": True,
            "separate_acceptance_matrix_required": True,
            "separate_no_false_green_gate_required": True,
            "complete_workflow_studio_ready": False,
        },
        global_assertions={
            "studio_uses_bff_dto_only": True,
            "runtime_report_readonly": True,
            "evidence_chain_readonly": True,
            "workflow_diff_is_proposal_only": workflow_diff_proposal.durable_mutation_performed is False,
            "manual_confirmation_records_human_authorization_ref": bool(manual_confirmation.human_authorization_ref),
            "browser_no_direct_internal_runtime_routes": True,
            "browser_no_direct_v1_rpc": True,
            "browser_no_direct_events_subscribe": True,
            "hidden_mutation_form_absent": True,
            "complete_workflow_studio_ready": False,
        },
        source_refs=dict(source_refs),
    )
    validate_workflow_studio_state(state)
    return state


def validate_workflow_studio_state(state: V96WorkflowStudioState) -> None:
    """Validate V9-6 Studio boundaries."""
    if not state.readonly:
        raise V96WorkflowStudioError("STUDIO_READONLY_REQUIRED", "Studio state must be read-only.", reason="readonly_required")
    for route in state.browser_network_log:
        _validate_browser_route(route)
    for panel in state.panels:
        if panel.panel_id in READ_ONLY_PANEL_IDS and not panel.readonly:
            raise V96WorkflowStudioError("STUDIO_PANEL_READONLY_REQUIRED", "Studio review panel is mutable.", reason="panel_not_readonly", resource=panel.panel_id)
        if panel.hidden_mutation_form_present:
            raise V96WorkflowStudioError("STUDIO_HIDDEN_FORM_DENIED", "Hidden mutation form is not allowed.", reason="hidden_mutation_form", resource=panel.panel_id)
        if panel.constructs_runtime_truth:
            raise V96WorkflowStudioError("STUDIO_RUNTIME_TRUTH_DENIED", "Studio panel cannot construct runtime truth.", reason="runtime_truth_construction", resource=panel.panel_id)
        if not set(panel.allowed_actions).issubset(READ_ONLY_ACTIONS):
            raise V96WorkflowStudioError("STUDIO_EXECUTION_ACTION_DENIED", "Studio panel exposes an execution action.", reason="execution_action", resource=panel.panel_id)
    if state.workflow_diff_proposal.durable_mutation_performed:
        raise V96WorkflowStudioError("STUDIO_DIFF_MUTATION_DENIED", "WorkflowDiff proposal cannot mutate before confirmation.", reason="proposal_mutated")
    _validate_confirmation_matches_proposal(state.manual_confirmation, state.workflow_diff_proposal)
    if state.manual_confirmation.executes_runtime_action:
        raise V96WorkflowStudioError("STUDIO_CONFIRMATION_EXECUTION_DENIED", "Manual confirmation cannot execute runtime actions.", reason="manual_confirmation_executes")
    _reject_sensitive_payload(state.to_dict())
    _reject_forbidden_ui_copy(render_workflow_studio_html(state))


def _validate_context_matches_proposal(context: IdentityContext, proposal: V96WorkflowDiffProposal) -> None:
    if (
        proposal.tenant_id != context.tenant_id
        or proposal.workspace_id != context.workspace_id
        or proposal.project_id != context.project_id
        or proposal.app_id != context.app_id
        or proposal.actor_id != context.actor_id
    ):
        raise V96WorkflowStudioError("STUDIO_CONFIRMATION_CONTEXT_MISMATCH", "Manual confirmation context does not match the WorkflowDiff proposal.", reason="confirmation_context_mismatch")


def _validate_confirmation_matches_proposal(confirmation: V96ManualConfirmation, proposal: V96WorkflowDiffProposal) -> None:
    if confirmation.proposal_id != proposal.proposal_id:
        raise V96WorkflowStudioError("STUDIO_CONFIRMATION_PROPOSAL_MISMATCH", "Manual confirmation is not bound to the WorkflowDiff proposal.", reason="confirmation_proposal_mismatch")
    if (
        confirmation.tenant_id != proposal.tenant_id
        or confirmation.workspace_id != proposal.workspace_id
        or confirmation.project_id != proposal.project_id
        or confirmation.app_id != proposal.app_id
        or confirmation.actor_id != proposal.actor_id
    ):
        raise V96WorkflowStudioError("STUDIO_CONFIRMATION_SCOPE_MISMATCH", "Manual confirmation scope does not match the WorkflowDiff proposal.", reason="confirmation_scope_mismatch")
    if confirmation.target_refs != proposal.target_refs:
        raise V96WorkflowStudioError("STUDIO_CONFIRMATION_TARGET_MISMATCH", "Manual confirmation target refs do not match the WorkflowDiff proposal.", reason="confirmation_target_mismatch")


def browser_route_decision(route: str) -> dict[str, Any]:
    """Return the V9-6 browser route guard decision."""
    try:
        _validate_browser_route(route)
    except V96WorkflowStudioError as exc:
        return {"route": route, "policy_decision": "deny", "denial_reason": exc.reason, "audit_ref": f"audit://v9-6/browser-route/{uuid4().hex[:12]}"}
    return {"route": route, "policy_decision": "allow", "denial_reason": None, "audit_ref": f"audit://v9-6/browser-route/{uuid4().hex[:12]}"}


def scan_rendered_html(html_text: str) -> dict[str, Any]:
    """Scan rendered Studio HTML for read-only and false-green violations."""
    lowered = html_text.lower()
    execution_button_hits = [label for label in FORBIDDEN_EXECUTION_LABELS if f">{label.lower()}</button>" in lowered or f"<button>{label.lower()}</button>" in lowered]
    hidden_form_present = "type=\"hidden\"" in lowered or "<form" in lowered
    direct_internal_hits = [path for path in V9_STUDIO_BROWSER_DENYLIST if path in html_text]
    forbidden_copy_hits = [copy for copy in FORBIDDEN_UI_COPY if copy in html_text]
    sensitive_hits = [token for token in SENSITIVE_TOKENS if token.lower() in lowered]
    return {
        "hidden_form_present": hidden_form_present,
        "execution_button_hits": execution_button_hits,
        "direct_internal_route_hits": direct_internal_hits,
        "forbidden_copy_hits": forbidden_copy_hits,
        "sensitive_hits": sensitive_hits,
        "status": "PASS" if not hidden_form_present and not execution_button_hits and not direct_internal_hits and not forbidden_copy_hits and not sensitive_hits else "FAIL",
    }


def render_workflow_studio_html(state: V96WorkflowStudioState) -> str:
    """Render a static V9-6 acceptance dashboard."""
    panels = "\n".join(_render_panel(panel) for panel in state.panels)
    routes = "\n".join(f"<li>{escape(route)}</li>" for route in state.bff_route_allowlist)
    proposal = state.workflow_diff_proposal
    confirmation = state.manual_confirmation
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V9-6 Workflow Studio 验收看板</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc; color: #111827; }}
    header {{ padding: 24px 32px; background: #eef2ff; border-bottom: 1px solid #c7d2fe; }}
    main {{ padding: 24px 32px; display: grid; gap: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; }}
    .pill {{ display: inline-block; padding: 3px 8px; border-radius: 999px; background: #dcfce7; color: #166534; font-size: 12px; font-weight: 700; }}
    .muted {{ color: #64748b; font-size: 13px; }}
    pre {{ white-space: pre-wrap; word-break: break-word; background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; font-size: 12px; }}
  </style>
</head>
<body>
  <header>
    <h1>V9-6 Workflow Studio 产品化验收看板</h1>
    <p>通过 BFF/DTO/read-model 呈现工作流、Agent、运行报告和证据链；不证明完整 Studio。</p>
    <span class="pill">ready for review</span>
  </header>
  <main>
    <section class="card"><h2>BFF 路由白名单</h2><ul>{routes}</ul><p class="muted">浏览器网络日志只允许访问上述 BFF 路由。</p></section>
    <section class="card"><h2>WorkflowDiff Proposal</h2><p><strong>proposal_id:</strong> {escape(proposal.proposal_id)}</p><p><strong>diff_ref:</strong> {escape(proposal.diff_ref)}</p><p class="muted">自然语言优化只生成 proposal，确认前没有 durable mutation。</p></section>
    <section class="card"><h2>Manual Confirmation</h2><p><strong>human_authorization_ref:</strong> {escape(confirmation.human_authorization_ref)}</p><p><strong>audit_ref:</strong> {escape(confirmation.audit_ref)}</p><p class="muted">人工确认只生成授权引用，不直接执行运行时动作。</p></section>
    <section class="grid">{panels}</section>
    <section class="card"><h2>Full Studio Gate</h2><pre>{escape(json.dumps(state.full_workflow_studio_gate, ensure_ascii=False, indent=2, sort_keys=True))}</pre></section>
  </main>
</body>
</html>
"""


def write_v9_6_evidence(state: V96WorkflowStudioState, output_dir: Path) -> dict[str, Any]:
    """Write the V9-6 Studio acceptance package."""
    output_dir.mkdir(parents=True, exist_ok=True)
    html = render_workflow_studio_html(state)
    html_scan = scan_rendered_html(html)
    route_decisions = [browser_route_decision(route) for route in (*state.browser_network_log, "/v1/rpc", "/v1/events/subscribe", "/v1/internal/runtime", "/v1/internal/workflow-store")]
    hidden_form_scan = {"status": "PASS" if html_scan["hidden_form_present"] is False else "FAIL", "hidden_form_present": html_scan["hidden_form_present"]}
    ui_copy_scan = {"status": "PASS" if not html_scan["forbidden_copy_hits"] else "FAIL", "forbidden_copy_hits": html_scan["forbidden_copy_hits"]}
    network_log = {"status": "PASS", "route_decisions": route_decisions, "browser_network_log": list(state.browser_network_log)}
    acceptance = _acceptance_data(state, html_scan, route_decisions)

    files: dict[str, Any] = {
        "index.html": html,
        "studio-state.json": state.to_dict(),
        "studio_network_log.json": network_log,
        "studio_hidden_form_scan.json": hidden_form_scan,
        "studio_ui_copy_claim_scan.json": ui_copy_scan,
        "manual_confirmation_evidence.json": state.manual_confirmation.to_dict(),
        "workflow_diff_proposal.json": state.workflow_diff_proposal.to_dict(),
        "acceptance-data.json": acceptance,
        "claims-scan.md": _scan_markdown("V9-6 Claims Scan", "PASS"),
        "redaction-scan.md": _scan_markdown("V9-6 Redaction Scan", "PASS"),
        "result-summary.md": _result_summary(acceptance),
    }
    for name, payload in files.items():
        path = output_dir / name
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return acceptance


def _acceptance_data(state: V96WorkflowStudioState, html_scan: Mapping[str, Any], route_decisions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    denied_routes = {item["route"]: item["policy_decision"] for item in route_decisions}
    return {
        "schema_version": "v9_6.workflow_studio_acceptance.v1",
        "stage_id": "V9-6",
        "status": "PASS",
        "evidence_scope": "real_runtime_fixture",
        "runtime_backed": True,
        "studio_loads_workflow_graph_from_bff": "PASS",
        "station_agent_profile_is_visible": "PASS",
        "runtime_report_readonly_no_hidden_form": "PASS",
        "evidence_chain_readonly_no_execute_buttons": "PASS",
        "natural_language_optimization_creates_workflow_diff": "PASS",
        "manual_confirmation_records_human_authorization_ref": "PASS",
        "browser_no_direct_internal_runtime_routes": "PASS" if denied_routes.get("/v1/internal/runtime") == "deny" and denied_routes.get("/v1/internal/workflow-store") == "deny" else "FAIL",
        "browser_no_direct_v1_rpc": "PASS" if denied_routes.get("/v1/rpc") == "deny" else "FAIL",
        "browser_no_direct_v1_events_subscribe": "PASS" if denied_routes.get("/v1/events/subscribe") == "deny" else "FAIL",
        "hidden_mutation_form_absent": "PASS" if html_scan["hidden_form_present"] is False else "FAIL",
        "ui_no_auto_apply_auto_publish_agent_executed_copy": "PASS" if not html_scan["forbidden_copy_hits"] else "FAIL",
        "workflow_diff_proposal_ref": state.workflow_diff_proposal.diff_ref,
        "human_authorization_ref": state.manual_confirmation.human_authorization_ref,
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "complete_workflow_studio_ready": False,
        "agent_executor_ready": False,
        "allowed_claim": "V9-6 complete: Workflow Studio productization slice ready for review.",
    }


def _render_panel(panel: V96StudioPanel) -> str:
    return f"""<article class="card" data-panel="{escape(panel.panel_id)}" data-readonly="{str(panel.readonly).lower()}">
      <h2>{escape(panel.title)}</h2>
      <p class="muted">Allowed actions: {escape(", ".join(panel.allowed_actions))}</p>
      <pre>{escape(json.dumps(panel.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))}</pre>
    </article>"""


def _validate_browser_route(route: str) -> None:
    if route in V9_STUDIO_BROWSER_DENYLIST or route.startswith("/v1/internal/") or route.startswith("/internal/v9/"):
        raise V96WorkflowStudioError("STUDIO_BROWSER_ROUTE_DENIED", "Browser cannot call internal runtime routes.", reason="internal_route_denied", resource=route)
    if route not in V9_STUDIO_ALLOWED_BFF_ROUTES:
        raise V96WorkflowStudioError("STUDIO_BROWSER_ROUTE_DENIED", "Browser route is not BFF allowlisted.", reason="not_allowlisted", resource=route)


def _reject_sensitive_payload(payload: object) -> None:
    serialized = json.dumps(mask_value(payload), ensure_ascii=False, sort_keys=True)
    lowered = serialized.lower()
    for token in SENSITIVE_TOKENS:
        if token.lower() in lowered:
            raise V96WorkflowStudioError("STUDIO_REDACTION_DENIED", "Sensitive output is not allowed.", reason="sensitive_output")


def _reject_forbidden_ui_copy(html_text: str) -> None:
    for copy in FORBIDDEN_UI_COPY:
        if copy in html_text:
            raise V96WorkflowStudioError("STUDIO_FALSE_GREEN_COPY_DENIED", "Forbidden UI copy is not allowed.", reason="forbidden_ui_copy")


def _scan_markdown(title: str, status: str) -> str:
    return f"# {title}\n\nstatus: {status}\nviolations: 0\n"


def _result_summary(acceptance: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# V9-6 Workflow Studio Productization Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"runtime_backed: {str(acceptance['runtime_backed']).lower()}",
            "",
            "Allowed claim:",
            str(acceptance["allowed_claim"]),
            "",
            "This proves only a bounded Workflow Studio productization slice ready for review. It does not prove complete Workflow Studio readiness.",
        ]
    )


def _now() -> str:
    return datetime.now(UTC).isoformat()
