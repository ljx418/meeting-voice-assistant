"""V5.6 Thin Web Console productization primitives.

This module builds a read-only console state from existing V5 evidence. It does
not add BFF routes, runtime behavior, Agent executor authority, or full Studio
editing capability.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html import escape
from typing import Any, Mapping, Sequence
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext, ResourceRef, TenantBoundaryError, validate_resource_access


READ_ONLY_PANEL_ACTIONS = ("view", "open_report", "open_evidence", "export_request_handoff")
BROWSER_FORBIDDEN_PATHS = ("/v1/rpc", "/v1/events/subscribe")
READ_ONLY_PANEL_IDS = {"runtime_report", "evidence_review", "audit_export", "external_app_admin"}
FORBIDDEN_BUTTON_LABELS = {"Apply", "Publish", "Approve", "Reject", "Execute", "Run", "自动应用", "自动发布", "Agent 已执行", "Agent 已发布"}
SENSITIVE_OUTPUT_TOKENS = (
    "capability_token",
    "subscription_token",
    "Authorization",
    "Bearer",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw prompt",
    "upstream signed URL",
    "api_key",
    "secret",
    "sk-",
)


class ThinWebConsoleError(ValueError):
    """Stable V5.6 thin console denial."""

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
class ConsolePanel:
    """One product-console panel projection."""

    panel_id: str
    title: str
    readonly: bool
    allowed_actions: tuple[str, ...]
    source_refs: dict[str, str]
    data: dict[str, Any]
    redaction_status: str = "redacted"

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted panel DTO."""
        data = asdict(self)
        data["allowed_actions"] = list(self.allowed_actions)
        return mask_value(data)


@dataclass(frozen=True)
class ManualConfirmationRecord:
    """User-confirmed product-console operation handoff."""

    confirmation_id: str
    operation: str
    source: str
    actor_type: str
    actor_id: str
    user_confirmed: bool
    policy_decision: str
    target_refs: dict[str, str]
    evidence_ref: str
    created_at: str
    redaction_status: str = "redacted"

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted confirmation DTO."""
        return mask_value(asdict(self))


@dataclass(frozen=True)
class ThinWebConsoleState:
    """Read-only V5.6 product console state."""

    console_id: str
    tenant_context: dict[str, str]
    navigation_items: tuple[str, ...]
    panels: tuple[ConsolePanel, ...]
    manual_confirmation: ManualConfirmationRecord
    global_assertions: dict[str, bool]
    source_refs: dict[str, str]
    generated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    readonly: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted console DTO."""
        data = asdict(self)
        data["navigation_items"] = list(self.navigation_items)
        data["panels"] = [panel.to_dict() for panel in self.panels]
        data["manual_confirmation"] = self.manual_confirmation.to_dict()
        return mask_value(data)


def build_manual_confirmation(
    context: IdentityContext,
    *,
    operation: str,
    source: str,
    user_confirmed: bool,
    target: ResourceRef,
) -> ManualConfirmationRecord:
    """Record a user-confirmed console handoff without executing runtime work."""
    try:
        audit = validate_resource_access(context, target, operation=operation, source=source, user_confirmed=user_confirmed)
    except TenantBoundaryError as exc:
        raise ThinWebConsoleError(exc.code, str(exc), reason=exc.reason, resource=exc.resource) from exc
    return ManualConfirmationRecord(
        confirmation_id=f"console_confirmation_{uuid4().hex}",
        operation=operation,
        source=source,
        actor_type=context.actor_type,
        actor_id=context.actor_id,
        user_confirmed=True,
        policy_decision=audit["policy_decision"],
        target_refs={
            "tenant_id": target.tenant_id,
            "workspace_id": target.workspace_id,
            "project_id": target.project_id,
            "app_id": target.app_id,
            "resource_type": target.resource_type,
            "resource_id": target.resource_id,
            "workflow_instance_id": target.workflow_instance_id or "",
        },
        evidence_ref=audit["evidence_ref"],
        created_at=datetime.now(UTC).isoformat(),
    )


def build_thin_web_console_state(
    context: IdentityContext,
    *,
    runtime_result: Mapping[str, Any],
    evidence_chain: Mapping[str, Any],
    audit_export: Mapping[str, Any],
    external_apps: Sequence[Mapping[str, Any]],
    manual_confirmation: ManualConfirmationRecord,
    source_refs: Mapping[str, str],
) -> ThinWebConsoleState:
    """Build a read-only product-console state from redacted source DTOs."""
    panels = (
        ConsolePanel(
            panel_id="runtime_report",
            title="运行报告",
            readonly=True,
            allowed_actions=("view", "open_report"),
            source_refs={"runtime_result_ref": source_refs.get("runtime_result", "")},
            data=_runtime_report_data(runtime_result),
        ),
        ConsolePanel(
            panel_id="evidence_review",
            title="证据链审查",
            readonly=True,
            allowed_actions=("view", "open_evidence"),
            source_refs={"evidence_ref": source_refs.get("evidence_chain", "")},
            data=_evidence_review_data(evidence_chain),
        ),
        ConsolePanel(
            panel_id="audit_export",
            title="审计导出",
            readonly=True,
            allowed_actions=("view", "export_request_handoff"),
            source_refs={"audit_export_ref": source_refs.get("audit_export", "")},
            data=dict(mask_value(audit_export)),
        ),
        ConsolePanel(
            panel_id="external_app_admin",
            title="外部应用",
            readonly=True,
            allowed_actions=("view", "open_evidence"),
            source_refs={"external_app_ref": source_refs.get("external_app", "")},
            data={"apps": [dict(mask_value(app)) for app in external_apps]},
        ),
    )
    state = ThinWebConsoleState(
        console_id=f"thin_console_{uuid4().hex}",
        tenant_context={
            "tenant_id": context.tenant_id,
            "workspace_id": context.workspace_id,
            "project_id": context.project_id,
            "app_id": context.app_id,
            "actor_type": context.actor_type,
            "actor_id": context.actor_id,
        },
        navigation_items=("Mission Console", "Runtime Report", "Evidence Chain", "Audit Export", "External Apps"),
        panels=panels,
        manual_confirmation=manual_confirmation,
        global_assertions={
            "browser_internal_routes_absent": True,
            "read_only_panels": True,
            "manual_confirmation_required": manual_confirmation.user_confirmed,
            "redaction_passed": True,
            "full_studio_not_claimed": True,
        },
        source_refs=dict(source_refs),
    )
    validate_thin_web_console_state(state)
    return state


def validate_thin_web_console_state(state: ThinWebConsoleState) -> None:
    """Validate read-only and browser-safety invariants for the console state."""
    for panel in state.panels:
        if panel.panel_id in READ_ONLY_PANEL_IDS and not panel.readonly:
            raise ThinWebConsoleError("THIN_CONSOLE_READONLY_REQUIRED", "Panel must be read-only.", reason="readonly_required", resource=panel.panel_id)
        if panel.panel_id in READ_ONLY_PANEL_IDS and not set(panel.allowed_actions).issubset(set(READ_ONLY_PANEL_ACTIONS)):
            raise ThinWebConsoleError("THIN_CONSOLE_ACTION_DENIED", "Read-only panel has a disallowed action.", reason="execution_action", resource=panel.panel_id)
    serialized = repr(state.to_dict())
    if any(path in serialized for path in BROWSER_FORBIDDEN_PATHS):
        raise ThinWebConsoleError("THIN_CONSOLE_BROWSER_ROUTE_DENIED", "Console state cannot expose direct internal browser routes.", reason="browser_route")
    if any(token in serialized for token in SENSITIVE_OUTPUT_TOKENS):
        raise ThinWebConsoleError("THIN_CONSOLE_REDACTION_DENIED", "Console state cannot expose sensitive fields.", reason="sensitive_output")


def render_console_html(state: ThinWebConsoleState) -> str:
    """Render a static, dependency-free HTML report for human review."""
    validate_thin_web_console_state(state)
    rows = "\n".join(_render_panel(panel) for panel in state.panels)
    context = state.tenant_context
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <title>V5-6 Thin Web Console 验收看板</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc; color: #0f172a; }}
    header {{ padding: 24px 32px; background: #e0f2fe; border-bottom: 1px solid #bae6fd; }}
    main {{ padding: 24px 32px; display: grid; gap: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
    .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06); }}
    .muted {{ color: #64748b; font-size: 13px; }}
    .pill {{ display: inline-block; padding: 3px 8px; border-radius: 999px; background: #dcfce7; color: #166534; font-size: 12px; font-weight: 700; }}
    pre {{ white-space: pre-wrap; word-break: break-word; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; font-size: 12px; }}
  </style>
</head>
<body>
  <header>
    <h1>V5-6 Thin Web Console 验收看板</h1>
    <p>范围：只读运行报告、只读证据链、审计导出申请入口、外部应用观察入口、人工确认记录。</p>
    <p class=\"muted\">租户：{escape(context['tenant_id'])} / 工作区：{escape(context['workspace_id'])} / 应用：{escape(context['app_id'])}</p>
  </header>
  <main>
    <section class=\"card\">
      <h2>全局断言 <span class=\"pill\">PASS</span></h2>
      <p>浏览器只使用产品控制台静态证据；只读面板不提供执行按钮；人工确认记录已生成；敏感内容已脱敏。</p>
    </section>
    <section class=\"grid\">{rows}</section>
    <section class=\"card\">
      <h2>人工确认记录</h2>
      <pre>{escape(_safe_repr(state.manual_confirmation.to_dict()))}</pre>
    </section>
  </main>
</body>
</html>
"""


def _render_panel(panel: ConsolePanel) -> str:
    return f"""<article class=\"card\">
  <h2>{escape(panel.title)} <span class=\"pill\">只读</span></h2>
  <p class=\"muted\">Panel: {escape(panel.panel_id)} / Actions: {escape(', '.join(panel.allowed_actions))}</p>
  <pre>{escape(_safe_repr(panel.to_dict()))}</pre>
</article>"""


def _runtime_report_data(runtime_result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "workflow_instance_id": runtime_result.get("workflow_instance_id"),
        "status": runtime_result.get("status"),
        "station_count": len(runtime_result.get("station_states", [])) if isinstance(runtime_result.get("station_states"), list) else runtime_result.get("station_count"),
        "artifact_count": len(runtime_result.get("artifacts", [])) if isinstance(runtime_result.get("artifacts"), list) else runtime_result.get("artifact_count"),
        "source": "v5_4c_existing_v4_runtime_trial",
    }


def _evidence_review_data(evidence_chain: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "proposal_id": evidence_chain.get("proposal_id"),
        "handoff_id": evidence_chain.get("handoff_id"),
        "operation_type": evidence_chain.get("operation_type"),
        "policy_decision": evidence_chain.get("policy_decision"),
        "runtime_result_ref": evidence_chain.get("runtime_result_ref"),
        "redaction_status": evidence_chain.get("redaction_status", "redacted"),
        "readonly": True,
    }


def _safe_repr(data: Mapping[str, Any]) -> str:
    text = repr(mask_value(data))
    for token in SENSITIVE_OUTPUT_TOKENS:
        text = text.replace(token, "[REDACTED]")
    return text
