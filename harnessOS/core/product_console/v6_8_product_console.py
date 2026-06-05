"""V6-8 product console pilot slice.

This module builds a read-only Product Console projection from existing V6
runtime, evidence, audit, and external-app DTOs. It does not add production
routes, execute runtime actions, write runtime truth, or claim complete
Workflow Studio readiness.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html import escape
from typing import Any, Mapping, Sequence
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.apps.v6_external_app_onboarding import V6_ALLOWED_BFF_ROUTES, V6_INTERNAL_BROWSER_DENYLIST
from core.auth.tenant_boundary import IdentityContext


READ_ONLY_ACTIONS = {"view", "export", "open_handoff", "open_report", "open_evidence"}
READ_ONLY_PANEL_IDS = {"runtime_report", "evidence_review", "audit_export", "external_app_admin"}
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
    "生产可用",
    "完整工作流工作台已完成",
    "complete Workflow Studio ready",
    "production-ready external app support",
    "Agent executor ready",
    "full multi-Agent orchestration ready",
    "distributed multi-Agent runtime ready",
    "autonomous workflow editing ready",
}
SENSITIVE_OUTPUT_TOKENS = {
    "capability_token",
    "subscription_token",
    "Authorization:",
    "Bearer ",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw prompt",
    "upstream signed URL",
    "api_key",
    "secret",
    "sk-",
}


class V68ProductConsoleError(ValueError):
    """Stable denial for V6-8 product console safety checks."""

    def __init__(self, code: str, message: str, *, reason: str, resource: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.resource = resource

    def to_error(self) -> dict[str, Any]:
        """Return a redacted error DTO."""
        data: dict[str, Any] = {"reason": self.reason}
        if self.resource is not None:
            data["resource"] = self.resource
        return {"code": self.code, "message": str(self), "data": data}


@dataclass(frozen=True)
class V68Panel:
    """One read-only Product Console panel."""

    panel_id: str
    title: str
    readonly: bool
    allowed_actions: tuple[str, ...]
    source_refs: dict[str, str]
    data: dict[str, Any]
    hidden_mutation_form_present: bool = False
    constructs_runtime_truth: bool = False
    redaction_status: str = "redacted"

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted panel DTO."""
        data = asdict(self)
        data["allowed_actions"] = list(self.allowed_actions)
        return mask_value(data)


@dataclass(frozen=True)
class V68ManualConfirmation:
    """Auditable human authorization record created by the console UX."""

    human_authorization_ref: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    actor_id: str
    actor_type: str
    operation: str
    target_refs: dict[str, str]
    risk_flags: tuple[str, ...]
    policy_decision_ref: str
    policy_decision: str
    created_at: str
    expires_at: str
    correlation_id: str
    request_id: str
    audit_ref: str
    source: str = "product_console"
    executes_runtime_action: bool = False
    redaction_status: str = "redacted"

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted manual confirmation DTO."""
        data = asdict(self)
        data["risk_flags"] = list(self.risk_flags)
        return mask_value(data)


@dataclass(frozen=True)
class V68ProductConsoleState:
    """Read-only V6-8 Product Console state."""

    console_id: str
    tenant_context: dict[str, str]
    bff_route_allowlist: tuple[str, ...]
    browser_network_log: tuple[str, ...]
    panels: tuple[V68Panel, ...]
    manual_confirmation: V68ManualConfirmation
    full_workflow_studio_gate: dict[str, Any]
    global_assertions: dict[str, bool]
    source_refs: dict[str, str]
    generated_at: str = field(default_factory=lambda: _now())
    readonly: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted console DTO."""
        data = asdict(self)
        data["bff_route_allowlist"] = list(self.bff_route_allowlist)
        data["browser_network_log"] = list(self.browser_network_log)
        data["panels"] = [panel.to_dict() for panel in self.panels]
        data["manual_confirmation"] = self.manual_confirmation.to_dict()
        return mask_value(data)


def build_manual_confirmation(
    context: IdentityContext,
    *,
    operation: str,
    target_refs: Mapping[str, str],
    risk_flags: Sequence[str],
    policy_decision_ref: str,
    expires_at: str,
    source: str = "product_console",
) -> V68ManualConfirmation:
    """Create a human authorization ref without executing runtime actions."""
    if context.actor_type == "agent" or source == "agent":
        raise V68ProductConsoleError("MANUAL_CONFIRMATION_AGENT_DENIED", "Agent cannot create durable confirmation.", reason="source_agent_denied")
    if source not in {"product_console", "approved_api"}:
        raise V68ProductConsoleError("MANUAL_CONFIRMATION_SOURCE_DENIED", "Manual confirmation source is not allowed.", reason="source_not_allowed")
    _reject_sensitive_payload({"target_refs": dict(target_refs), "risk_flags": list(risk_flags)})
    return V68ManualConfirmation(
        human_authorization_ref=f"human-auth://v6-8/{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        actor_id=context.actor_id,
        actor_type=context.actor_type,
        operation=operation,
        target_refs=dict(target_refs),
        risk_flags=tuple(risk_flags),
        policy_decision_ref=policy_decision_ref,
        policy_decision="allow",
        created_at=_now(),
        expires_at=expires_at,
        correlation_id=context.correlation_id,
        request_id=context.request_id,
        audit_ref=f"audit://v6-8/manual-confirmation/{uuid4().hex[:12]}",
    )


def build_product_console_state(
    context: IdentityContext,
    *,
    runtime_report: Mapping[str, Any],
    evidence_review: Mapping[str, Any],
    audit_export: Mapping[str, Any],
    external_app_admin: Mapping[str, Any],
    manual_confirmation: V68ManualConfirmation,
    browser_network_log: Sequence[str],
    source_refs: Mapping[str, str],
) -> V68ProductConsoleState:
    """Build and validate a read-only Product Console state."""
    panels = (
        V68Panel(
            panel_id="runtime_report",
            title="运行报告",
            readonly=True,
            allowed_actions=("view", "open_report"),
            source_refs={"runtime_report_ref": source_refs.get("runtime_report", "")},
            data=_runtime_report_projection(runtime_report),
        ),
        V68Panel(
            panel_id="evidence_review",
            title="证据链审查",
            readonly=True,
            allowed_actions=("view", "export", "open_handoff"),
            source_refs={"evidence_ref": source_refs.get("evidence_review", "")},
            data=_evidence_review_projection(evidence_review),
        ),
        V68Panel(
            panel_id="audit_export",
            title="审计导出",
            readonly=True,
            allowed_actions=("view", "export"),
            source_refs={"audit_export_ref": source_refs.get("audit_export", "")},
            data=_audit_export_projection(audit_export),
        ),
        V68Panel(
            panel_id="external_app_admin",
            title="外部应用管理",
            readonly=True,
            allowed_actions=("view", "open_evidence"),
            source_refs={"external_app_ref": source_refs.get("external_app_admin", "")},
            data=_external_app_admin_projection(external_app_admin),
        ),
    )
    state = V68ProductConsoleState(
        console_id=f"product-console-v6-8-{uuid4().hex[:12]}",
        tenant_context={
            "tenant_id": context.tenant_id,
            "workspace_id": context.workspace_id,
            "project_id": context.project_id,
            "app_id": context.app_id,
            "actor_type": context.actor_type,
            "actor_id": context.actor_id,
        },
        bff_route_allowlist=tuple(sorted(V6_ALLOWED_BFF_ROUTES)),
        browser_network_log=tuple(browser_network_log),
        panels=panels,
        manual_confirmation=manual_confirmation,
        full_workflow_studio_gate={
            "separate_prd_required": True,
            "separate_architecture_required": True,
            "separate_acceptance_matrix_required": True,
            "separate_no_false_green_gate_required": True,
            "complete_workflow_studio_ready": False,
        },
        global_assertions={
            "runtime_report_readonly": True,
            "evidence_review_readonly": True,
            "audit_export_readonly": True,
            "external_app_admin_does_not_construct_runtime_truth": True,
            "manual_confirmation_records_human_authorization_ref": bool(manual_confirmation.human_authorization_ref),
            "browser_no_direct_internal_runtime_routes": True,
            "browser_no_direct_v1_rpc": True,
            "browser_no_direct_v1_events_subscribe": True,
            "full_workflow_studio_requires_separate_gate": True,
            "redaction_passed": True,
        },
        source_refs=dict(source_refs),
    )
    validate_product_console_state(state)
    return state


def validate_product_console_state(state: V68ProductConsoleState) -> None:
    """Validate read-only, browser-safety, and no-false-green invariants."""
    if not state.readonly:
        raise V68ProductConsoleError("PRODUCT_CONSOLE_READONLY_REQUIRED", "Product Console state must be read-only.", reason="readonly_required")
    for route in state.browser_network_log:
        _validate_browser_route(route)
    for panel in state.panels:
        if panel.panel_id in READ_ONLY_PANEL_IDS and not panel.readonly:
            raise V68ProductConsoleError("PRODUCT_CONSOLE_PANEL_READONLY_REQUIRED", "Read-only panel is mutable.", reason="panel_not_readonly", resource=panel.panel_id)
        if panel.hidden_mutation_form_present:
            raise V68ProductConsoleError("PRODUCT_CONSOLE_HIDDEN_FORM_DENIED", "Hidden mutation form is not allowed.", reason="hidden_mutation_form", resource=panel.panel_id)
        if panel.constructs_runtime_truth:
            raise V68ProductConsoleError("PRODUCT_CONSOLE_RUNTIME_TRUTH_DENIED", "Panel cannot construct runtime truth.", reason="runtime_truth_construction", resource=panel.panel_id)
        if not set(panel.allowed_actions).issubset(READ_ONLY_ACTIONS):
            raise V68ProductConsoleError("PRODUCT_CONSOLE_EXECUTION_ACTION_DENIED", "Panel exposes an execution action.", reason="execution_action", resource=panel.panel_id)
    if state.manual_confirmation.executes_runtime_action:
        raise V68ProductConsoleError("MANUAL_CONFIRMATION_EXECUTION_DENIED", "Manual confirmation cannot execute runtime actions.", reason="manual_confirmation_executes")
    _reject_sensitive_payload(state.to_dict())
    _reject_forbidden_ui_copy(render_product_console_html(state))


def browser_route_decision(route: str) -> dict[str, Any]:
    """Return the browser route guard decision for one requested path."""
    try:
        _validate_browser_route(route)
    except V68ProductConsoleError as exc:
        return {
            "route": route,
            "policy_decision": "deny",
            "denial_reason": exc.reason,
            "audit_ref": f"audit://v6-8/browser-route/{uuid4().hex[:12]}",
        }
    return {
        "route": route,
        "policy_decision": "allow",
        "denial_reason": None,
        "audit_ref": f"audit://v6-8/browser-route/{uuid4().hex[:12]}",
    }


def scan_rendered_html(html_text: str) -> dict[str, Any]:
    """Scan rendered HTML for V6-8 read-only browser safety evidence."""
    lowered = html_text.lower()
    execution_button_hits = []
    for label in FORBIDDEN_EXECUTION_LABELS:
        if f"<button>{label.lower()}</button>" in lowered or f">{label.lower()}</button>" in lowered:
            execution_button_hits.append(label)
    hidden_form_present = "type=\"hidden\"" in lowered or "<form" in lowered
    direct_internal_hits = [path for path in V6_INTERNAL_BROWSER_DENYLIST if path in html_text]
    forbidden_copy_hits = [copy for copy in FORBIDDEN_UI_COPY if copy in html_text]
    sensitive_hits = [token for token in SENSITIVE_OUTPUT_TOKENS if token.lower() in lowered]
    return {
        "hidden_form_present": hidden_form_present,
        "execution_button_hits": execution_button_hits,
        "direct_internal_route_hits": direct_internal_hits,
        "forbidden_copy_hits": forbidden_copy_hits,
        "sensitive_hits": sensitive_hits,
        "status": "PASS" if not hidden_form_present and not execution_button_hits and not direct_internal_hits and not forbidden_copy_hits and not sensitive_hits else "FAIL",
    }


def render_product_console_html(state: V68ProductConsoleState) -> str:
    """Render a static, dependency-free Product Console acceptance view."""
    panels = "\n".join(_render_panel(panel) for panel in state.panels)
    routes = "\n".join(f"<li>{escape(route)}</li>" for route in state.bff_route_allowlist)
    confirmation = state.manual_confirmation
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V6-8 Product Console 验收看板</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc; color: #111827; }}
    header {{ padding: 24px 32px; background: #ecfeff; border-bottom: 1px solid #a5f3fc; }}
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
    <h1>V6-8 Product Console 验收看板</h1>
    <p>只读产品控制台 pilot slice；不证明完整 Workflow Studio。</p>
    <span class="pill">ready for review</span>
  </header>
  <main>
    <section class="card">
      <h2>BFF 路由白名单</h2>
      <ul>{routes}</ul>
      <p class="muted">浏览器网络日志只允许访问上述 BFF 路由。</p>
    </section>
    <section class="card">
      <h2>人工确认记录</h2>
      <p><strong>human_authorization_ref:</strong> {escape(confirmation.human_authorization_ref)}</p>
      <p><strong>operation:</strong> {escape(confirmation.operation)}</p>
      <p><strong>audit_ref:</strong> {escape(confirmation.audit_ref)}</p>
      <p class="muted">人工确认只生成授权引用，不直接执行运行时动作。</p>
    </section>
    <section class="grid">{panels}</section>
    <section class="card">
      <h2>Full Workflow Studio Gate</h2>
      <pre>{escape(json.dumps(state.full_workflow_studio_gate, ensure_ascii=False, indent=2, sort_keys=True))}</pre>
    </section>
  </main>
</body>
</html>
"""


def _runtime_report_projection(runtime_report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": str(runtime_report.get("workflow_instance_id", "")),
        "status": str(runtime_report.get("status", "")),
        "attempt_count": len(runtime_report.get("attempts", [])),
        "lineage_count": len(runtime_report.get("artifact_lineage", [])),
        "incident_count": len(runtime_report.get("incident_timeline", [])),
        "source": "runtime_read_model",
    }


def _evidence_review_projection(evidence_review: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "evidence_scope": str(evidence_review.get("evidence_scope", "")),
        "scenario_count": evidence_review.get("scenario_count", 0),
        "claim_violations": list(evidence_review.get("claim_violations", [])),
        "redaction_status": str(evidence_review.get("redaction_status", "")),
        "allowed_actions": ["view", "export", "open_handoff"],
    }


def _audit_export_projection(audit_export: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "audit_export_ref": str(audit_export.get("audit_export_ref", "")),
        "authorized_view": bool(audit_export.get("authorized_view", False)),
        "immutable_or_append_only": bool(audit_export.get("immutable_or_append_only", True)),
        "source": "audit_export_read_model",
    }


def _external_app_admin_projection(external_app_admin: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "app_id": str(external_app_admin.get("app_id", "")),
        "registration_status": str(external_app_admin.get("registration_status", "")),
        "offboarding_revoked_credentials": bool(external_app_admin.get("offboarding_revoked_credentials", False)),
        "constructs_runtime_truth": False,
        "source": "external_app_admin_read_model",
    }


def _render_panel(panel: V68Panel) -> str:
    return f"""<article class="card" data-panel="{escape(panel.panel_id)}" data-readonly="{str(panel.readonly).lower()}">
      <h2>{escape(panel.title)}</h2>
      <p class="muted">Allowed actions: {escape(", ".join(panel.allowed_actions))}</p>
      <pre>{escape(json.dumps(panel.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))}</pre>
    </article>"""


def _validate_browser_route(route: str) -> None:
    if route in V6_INTERNAL_BROWSER_DENYLIST or route.startswith("/v1/internal/"):
        raise V68ProductConsoleError("PRODUCT_CONSOLE_BROWSER_ROUTE_DENIED", "Browser cannot call internal runtime routes.", reason="internal_route_denied", resource=route)
    if route not in V6_ALLOWED_BFF_ROUTES:
        raise V68ProductConsoleError("PRODUCT_CONSOLE_BROWSER_ROUTE_DENIED", "Browser route is not BFF allowlisted.", reason="not_allowlisted", resource=route)


def _reject_sensitive_payload(payload: object) -> None:
    serialized = json.dumps(mask_value(payload), ensure_ascii=False, sort_keys=True)
    lowered = serialized.lower()
    for token in SENSITIVE_OUTPUT_TOKENS:
        if token.lower() in lowered:
            raise V68ProductConsoleError("PRODUCT_CONSOLE_REDACTION_DENIED", "Sensitive output is not allowed.", reason="sensitive_output")


def _reject_forbidden_ui_copy(html_text: str) -> None:
    for copy in FORBIDDEN_UI_COPY:
        if copy in html_text:
            raise V68ProductConsoleError("PRODUCT_CONSOLE_FALSE_GREEN_COPY_DENIED", "Forbidden UI copy is not allowed.", reason="forbidden_ui_copy")


def _now() -> str:
    return datetime.now(UTC).isoformat()
