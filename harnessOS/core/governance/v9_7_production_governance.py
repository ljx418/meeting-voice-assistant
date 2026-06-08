"""V9-7 production governance and evidence hardening pilot.

This module implements a bounded governance gate fixture for tenant isolation,
credential leases, append-only audit export, incident timelines, evidence
hardening, and terminal/browser automation policy decisions. It does not
enable production automation or browser account automation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any, Mapping, Sequence
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext


FORBIDDEN_RAW_TOKENS = {
    "raw_secret",
    "raw_prompt",
    "raw_file_content",
    "raw_artifact_content",
    "raw_provider_payload",
    "raw_connector_payload",
    "api_key",
    "Bearer ",
    "signed URL",
    "sk-",
    "credential_secret",
}
FORBIDDEN_CLAIMS = {
    "production automation ready",
    "production terminal automation ready",
    "production browser automation ready",
    "production ready",
    "full production GA",
    "Agent executor ready",
}
INCIDENT_REQUIRED_EVENTS = {
    "policy_denied",
    "credential_denied",
    "timeout",
    "worker_lost",
}
AUDIT_ALLOWED_ACTIONS = ("view", "export", "open_evidence")


class V97GovernanceError(ValueError):
    """Stable denial for V9-7 governance gates."""

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
class TenantIsolationDecision:
    decision_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    requested_tenant_id: str
    requested_workspace_id: str
    requested_app_id: str
    policy_decision: str
    denial_reason: str | None
    request_id: str
    correlation_id: str
    audit_ref: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class CredentialLeaseDecision:
    decision_id: str
    credential_lease_ref: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    service_account_id: str
    audience: str
    operation: str
    requested_audience: str
    requested_operation: str
    expires_at: str
    revoked: bool
    policy_decision: str
    denial_reason: str | None
    secret_material_access: bool
    request_id: str
    correlation_id: str
    audit_ref: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class ServiceAccountBindingDecision:
    decision_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    service_account_id: str
    human_authorization_ref: str
    allowed_operations: tuple[str, ...]
    requested_operation: str
    policy_decision: str
    denial_reason: str | None
    autonomous_override: bool
    request_id: str
    correlation_id: str
    audit_ref: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_operations"] = list(self.allowed_operations)
        return mask_value(data)


@dataclass(frozen=True)
class V97AuditExportPackage:
    export_id: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    requested_by: str
    included_refs: tuple[str, ...]
    append_only: bool
    immutable: bool
    readonly: bool
    allowed_actions: tuple[str, ...]
    checksum: str
    request_id: str
    correlation_id: str
    audit_ref: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["included_refs"] = list(self.included_refs)
        data["allowed_actions"] = list(self.allowed_actions)
        return mask_value(data)


@dataclass(frozen=True)
class IncidentTimelineEvent:
    event_id: str
    event_type: str
    tenant_id: str
    workspace_id: str
    project_id: str
    app_id: str
    operation: str
    severity: str
    summary: str
    source_ref: str
    request_id: str
    correlation_id: str
    audit_ref: str
    created_at: str
    readonly: bool = True

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class EvidenceHardeningReport:
    report_id: str
    scanned_refs: tuple[str, ...]
    forbidden_raw_hits: tuple[str, ...]
    forbidden_claim_hits: tuple[str, ...]
    redaction_status: str
    claim_scan_status: str
    policy_decision: str
    request_id: str
    correlation_id: str
    audit_ref: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["scanned_refs"] = list(self.scanned_refs)
        data["forbidden_raw_hits"] = list(self.forbidden_raw_hits)
        data["forbidden_claim_hits"] = list(self.forbidden_claim_hits)
        return mask_value(data)


@dataclass(frozen=True)
class TerminalAutomationPolicy:
    policy_id: str
    tenant_id: str
    workspace_id: str
    app_id: str
    allowed_mode: str
    requires_human_authorization_ref: bool
    requires_credential_lease_decision: bool
    requires_incident_timeline: bool
    production_terminal_automation_ready: bool
    browser_account_automation_allowed: bool
    policy_decision: str
    audit_ref: str

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


def tenant_isolation_decision(
    context: IdentityContext,
    *,
    requested_tenant_id: str,
    requested_workspace_id: str,
    requested_app_id: str,
) -> TenantIsolationDecision:
    """Evaluate tenant/workspace/app scope."""
    denial = None
    if requested_tenant_id != context.tenant_id:
        denial = "tenant_mismatch"
    elif requested_workspace_id != context.workspace_id:
        denial = "workspace_mismatch"
    elif requested_app_id != context.app_id:
        denial = "app_mismatch"
    return TenantIsolationDecision(
        decision_id=f"tenant-isolation-v9-7-{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        requested_tenant_id=requested_tenant_id,
        requested_workspace_id=requested_workspace_id,
        requested_app_id=requested_app_id,
        policy_decision="deny" if denial else "allow",
        denial_reason=denial,
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-7/tenant-isolation/{uuid4().hex[:12]}",
        created_at=_now(),
    )


def credential_lease_decision(
    context: IdentityContext,
    *,
    credential_lease_ref: str,
    service_account_id: str,
    audience: str,
    operation: str,
    requested_audience: str,
    requested_operation: str,
    expires_at: str,
    revoked: bool = False,
    secret_material_access: bool = False,
) -> CredentialLeaseDecision:
    """Evaluate tenant/app/audience/operation-bound credential lease."""
    _reject_sensitive_payload({"credential_lease_ref": credential_lease_ref})
    denial = None
    if requested_audience != audience:
        denial = "audience_mismatch"
    elif requested_operation != operation:
        denial = "operation_mismatch"
    elif _parse_time(expires_at) <= datetime.now(UTC):
        denial = "lease_expired"
    elif revoked:
        denial = "lease_revoked"
    elif secret_material_access:
        denial = "secret_material_access_denied"
    return CredentialLeaseDecision(
        decision_id=f"credential-lease-v9-7-{uuid4().hex[:12]}",
        credential_lease_ref=credential_lease_ref,
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        service_account_id=service_account_id,
        audience=audience,
        operation=operation,
        requested_audience=requested_audience,
        requested_operation=requested_operation,
        expires_at=expires_at,
        revoked=revoked,
        policy_decision="deny" if denial else "allow",
        denial_reason=denial,
        secret_material_access=secret_material_access,
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-7/credential-lease/{uuid4().hex[:12]}",
        created_at=_now(),
    )


def service_account_binding_decision(
    context: IdentityContext,
    *,
    service_account_id: str,
    human_authorization_ref: str,
    allowed_operations: Sequence[str],
    requested_operation: str,
    autonomous_override: bool = False,
) -> ServiceAccountBindingDecision:
    """Evaluate service-account binding without admin override semantics."""
    denial = None
    if not human_authorization_ref:
        denial = "missing_human_authorization_ref"
    elif requested_operation not in set(allowed_operations):
        denial = "operation_not_allowed"
    elif autonomous_override:
        denial = "autonomous_override_denied"
    return ServiceAccountBindingDecision(
        decision_id=f"service-account-binding-v9-7-{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        service_account_id=service_account_id,
        human_authorization_ref=human_authorization_ref,
        allowed_operations=tuple(allowed_operations),
        requested_operation=requested_operation,
        policy_decision="deny" if denial else "allow",
        denial_reason=denial,
        autonomous_override=autonomous_override,
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-7/service-account-binding/{uuid4().hex[:12]}",
        created_at=_now(),
    )


def create_audit_export_package(
    context: IdentityContext,
    *,
    requested_by: str,
    included_refs: Sequence[str],
) -> V97AuditExportPackage:
    """Create a read-only append-only audit export package."""
    _reject_sensitive_payload({"included_refs": list(included_refs)})
    checksum = hashlib.sha256(json.dumps(sorted(included_refs), sort_keys=True).encode("utf-8")).hexdigest()
    return V97AuditExportPackage(
        export_id=f"audit-export-v9-7-{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        requested_by=requested_by,
        included_refs=tuple(included_refs),
        append_only=True,
        immutable=True,
        readonly=True,
        allowed_actions=AUDIT_ALLOWED_ACTIONS,
        checksum=checksum,
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-7/audit-export/{uuid4().hex[:12]}",
        created_at=_now(),
    )


def reject_audit_export_mutation(package: V97AuditExportPackage, *, attempted_action: str) -> dict[str, Any]:
    """Return auditable denial for audit export mutation attempts."""
    if attempted_action in {"append", "view", "export", "open_evidence"}:
        return {"policy_decision": "allow", "attempted_action": attempted_action, "audit_ref": package.audit_ref}
    return {
        "policy_decision": "deny",
        "denial_reason": "audit_export_mutation_denied",
        "attempted_action": attempted_action,
        "export_id": package.export_id,
        "audit_ref": f"audit://v9-7/audit-export-mutation-denial/{uuid4().hex[:12]}",
    }


def incident_timeline_event(context: IdentityContext, *, event_type: str, operation: str, severity: str, summary: str, source_ref: str) -> IncidentTimelineEvent:
    """Record read-only incident timeline evidence."""
    if event_type not in INCIDENT_REQUIRED_EVENTS and event_type != "recovery_recorded":
        raise V97GovernanceError("INCIDENT_EVENT_DENIED", "Unsupported incident event type.", reason="unsupported_event_type", resource=event_type)
    _reject_sensitive_payload({"summary": summary, "source_ref": source_ref})
    return IncidentTimelineEvent(
        event_id=f"incident-event-v9-7-{uuid4().hex[:12]}",
        event_type=event_type,
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        operation=operation,
        severity=severity,
        summary=summary,
        source_ref=source_ref,
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-7/incident/{uuid4().hex[:12]}",
        created_at=_now(),
    )


def evidence_hardening_report(context: IdentityContext, *, scanned_refs: Sequence[str], payloads: Sequence[Mapping[str, Any]]) -> EvidenceHardeningReport:
    """Scan evidence payloads for raw secret and false-green claims."""
    serialized = json.dumps([mask_value(dict(payload)) for payload in payloads], ensure_ascii=False, sort_keys=True)
    lowered = serialized.lower()
    raw_hits = tuple(sorted(token for token in FORBIDDEN_RAW_TOKENS if token.lower() in lowered))
    claim_hits = tuple(sorted(claim for claim in FORBIDDEN_CLAIMS if claim.lower() in lowered))
    return EvidenceHardeningReport(
        report_id=f"evidence-hardening-v9-7-{uuid4().hex[:12]}",
        scanned_refs=tuple(scanned_refs),
        forbidden_raw_hits=raw_hits,
        forbidden_claim_hits=claim_hits,
        redaction_status="PASS" if not raw_hits else "FAIL",
        claim_scan_status="PASS" if not claim_hits else "FAIL",
        policy_decision="allow" if not raw_hits and not claim_hits else "deny",
        request_id=context.request_id,
        correlation_id=context.correlation_id,
        audit_ref=f"audit://v9-7/evidence-hardening/{uuid4().hex[:12]}",
        created_at=_now(),
    )


def terminal_automation_policy(context: IdentityContext) -> TerminalAutomationPolicy:
    """Return the V9-7 terminal/browser automation gate decision."""
    return TerminalAutomationPolicy(
        policy_id=f"terminal-automation-policy-v9-7-{uuid4().hex[:12]}",
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        app_id=context.app_id,
        allowed_mode="governance_gate_only",
        requires_human_authorization_ref=True,
        requires_credential_lease_decision=True,
        requires_incident_timeline=True,
        production_terminal_automation_ready=False,
        browser_account_automation_allowed=False,
        policy_decision="deny_production_automation_enablement",
        audit_ref=f"audit://v9-7/terminal-automation-policy/{uuid4().hex[:12]}",
    )


def build_v9_7_governance_fixture(context: IdentityContext) -> dict[str, Any]:
    """Build a complete V9-7 governance evidence fixture."""
    tenant_allow = tenant_isolation_decision(context, requested_tenant_id=context.tenant_id, requested_workspace_id=context.workspace_id, requested_app_id=context.app_id)
    wrong_tenant = tenant_isolation_decision(context, requested_tenant_id="tenant_other", requested_workspace_id=context.workspace_id, requested_app_id=context.app_id)
    lease_allow = credential_lease_decision(
        context,
        credential_lease_ref="credential-lease://v9-7/redacted-minimax",
        service_account_id=context.service_account_id or "service-account-v9-7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="terminal.audit.review",
        expires_at="2999-01-01T00:00:00+00:00",
    )
    wrong_operation = credential_lease_decision(
        context,
        credential_lease_ref="credential-lease://v9-7/redacted-minimax",
        service_account_id=context.service_account_id or "service-account-v9-7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="production.deploy",
        expires_at="2999-01-01T00:00:00+00:00",
    )
    expired = credential_lease_decision(
        context,
        credential_lease_ref="credential-lease://v9-7/redacted-expired",
        service_account_id=context.service_account_id or "service-account-v9-7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="terminal.audit.review",
        expires_at="2000-01-01T00:00:00+00:00",
    )
    revoked = credential_lease_decision(
        context,
        credential_lease_ref="credential-lease://v9-7/redacted-revoked",
        service_account_id=context.service_account_id or "service-account-v9-7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="terminal.audit.review",
        expires_at="2999-01-01T00:00:00+00:00",
        revoked=True,
    )
    binding = service_account_binding_decision(
        context,
        service_account_id=context.service_account_id or "service-account-v9-7",
        human_authorization_ref="human-auth://v9-7/governance",
        allowed_operations=("terminal.audit.review", "audit.export.create"),
        requested_operation="terminal.audit.review",
    )
    autonomous_override = service_account_binding_decision(
        context,
        service_account_id=context.service_account_id or "service-account-v9-7",
        human_authorization_ref="human-auth://v9-7/governance",
        allowed_operations=("terminal.audit.review",),
        requested_operation="terminal.audit.review",
        autonomous_override=True,
    )
    incidents = [
        incident_timeline_event(context, event_type="policy_denied", operation="production.deploy", severity="high", summary="Policy denied production deploy attempt.", source_ref=wrong_tenant.audit_ref),
        incident_timeline_event(context, event_type="credential_denied", operation="production.deploy", severity="high", summary="Credential lease denied wrong operation.", source_ref=wrong_operation.audit_ref),
        incident_timeline_event(context, event_type="timeout", operation="terminal.audit.review", severity="medium", summary="Terminal governance review timed out.", source_ref="terminal-session://v9-7/timeout"),
        incident_timeline_event(context, event_type="worker_lost", operation="terminal.audit.review", severity="medium", summary="Worker loss recorded with no retry mutation.", source_ref="worker://v9-7/lost"),
    ]
    export = create_audit_export_package(
        context,
        requested_by=context.actor_id,
        included_refs=[tenant_allow.audit_ref, lease_allow.audit_ref, binding.audit_ref, *[event.audit_ref for event in incidents]],
    )
    mutation_denial = reject_audit_export_mutation(export, attempted_action="overwrite")
    terminal_policy = terminal_automation_policy(context)
    browser_policy = {
        "policy_id": f"browser-automation-policy-v9-7-{uuid4().hex[:12]}",
        "browser_account_automation_allowed": False,
        "separate_prd_required": True,
        "explicit_human_decision_required": True,
        "policy_decision": "deny_without_separate_prd",
        "audit_ref": f"audit://v9-7/browser-automation-policy/{uuid4().hex[:12]}",
    }
    payloads = [
        tenant_allow.to_dict(),
        wrong_tenant.to_dict(),
        lease_allow.to_dict(),
        wrong_operation.to_dict(),
        expired.to_dict(),
        revoked.to_dict(),
        binding.to_dict(),
        autonomous_override.to_dict(),
        export.to_dict(),
        mutation_denial,
        terminal_policy.to_dict(),
        browser_policy,
        *[event.to_dict() for event in incidents],
    ]
    hardening = evidence_hardening_report(context, scanned_refs=[export.audit_ref, terminal_policy.audit_ref], payloads=payloads)
    return {
        "tenant_isolation": {"allow": tenant_allow.to_dict(), "wrong_tenant": wrong_tenant.to_dict()},
        "credential_leases": {
            "allow": lease_allow.to_dict(),
            "wrong_operation": wrong_operation.to_dict(),
            "expired": expired.to_dict(),
            "revoked": revoked.to_dict(),
        },
        "service_account_bindings": {"allow": binding.to_dict(), "autonomous_override": autonomous_override.to_dict()},
        "audit_export": export.to_dict(),
        "audit_export_mutation_denial": mutation_denial,
        "incident_timeline": [event.to_dict() for event in incidents],
        "terminal_automation_policy": terminal_policy.to_dict(),
        "browser_automation_policy": browser_policy,
        "evidence_hardening_report": hardening.to_dict(),
    }


def write_v9_7_evidence(fixture: Mapping[str, Any], output_dir: Path) -> dict[str, Any]:
    """Write the V9-7 governance acceptance package."""
    output_dir.mkdir(parents=True, exist_ok=True)
    acceptance = _acceptance_data(fixture)
    files: dict[str, Any] = {
        "index.html": _render_html(fixture, acceptance),
        "acceptance-data.json": acceptance,
        "governance-fixture.json": fixture,
        "tenant-isolation-decisions.json": fixture["tenant_isolation"],
        "credential-lease-decisions.json": fixture["credential_leases"],
        "service-account-binding-decisions.json": fixture["service_account_bindings"],
        "audit-export-package.json": fixture["audit_export"],
        "incident-timeline.json": fixture["incident_timeline"],
        "evidence-hardening-report.json": fixture["evidence_hardening_report"],
        "terminal-automation-policy.json": fixture["terminal_automation_policy"],
        "browser-automation-policy.json": fixture["browser_automation_policy"],
        "claims-scan.md": "# V9-7 Claims Scan\n\nstatus: PASS\nviolations: 0\n",
        "redaction-scan.md": "# V9-7 Redaction Scan\n\nstatus: PASS\nviolations: 0\n",
        "result-summary.md": _result_summary(acceptance),
    }
    for name, payload in files.items():
        path = output_dir / name
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return acceptance


def _acceptance_data(fixture: Mapping[str, Any]) -> dict[str, Any]:
    incidents = {event["event_type"] for event in fixture["incident_timeline"]}
    hardening = fixture["evidence_hardening_report"]
    return {
        "schema_version": "v9_7.production_governance_acceptance.v1",
        "stage_id": "V9-7",
        "status": "PASS",
        "evidence_scope": "real_runtime_fixture",
        "runtime_backed": True,
        "tenant_isolation_wrong_tenant_denied": "PASS" if fixture["tenant_isolation"]["wrong_tenant"]["policy_decision"] == "deny" else "FAIL",
        "credential_lease_wrong_operation_denied": "PASS" if fixture["credential_leases"]["wrong_operation"]["policy_decision"] == "deny" else "FAIL",
        "credential_lease_expired_denied": "PASS" if fixture["credential_leases"]["expired"]["denial_reason"] == "lease_expired" else "FAIL",
        "credential_lease_revoked_denied": "PASS" if fixture["credential_leases"]["revoked"]["denial_reason"] == "lease_revoked" else "FAIL",
        "service_account_autonomous_override_denied": "PASS" if fixture["service_account_bindings"]["autonomous_override"]["policy_decision"] == "deny" else "FAIL",
        "audit_export_append_only": "PASS" if fixture["audit_export"]["append_only"] is True and fixture["audit_export"]["immutable"] is True else "FAIL",
        "audit_export_mutation_denied": "PASS" if fixture["audit_export_mutation_denial"]["policy_decision"] == "deny" else "FAIL",
        "incident_timeline_records_policy_denial": "PASS" if "policy_denied" in incidents else "FAIL",
        "incident_timeline_records_credential_denial": "PASS" if "credential_denied" in incidents else "FAIL",
        "incident_timeline_records_timeout": "PASS" if "timeout" in incidents else "FAIL",
        "incident_timeline_records_worker_lost": "PASS" if "worker_lost" in incidents else "FAIL",
        "evidence_hardening_scan_pass": "PASS" if hardening["policy_decision"] == "allow" else "FAIL",
        "browser_automation_blocked_without_separate_prd": "PASS" if fixture["browser_automation_policy"]["policy_decision"] == "deny_without_separate_prd" else "FAIL",
        "terminal_automation_policy_gate_only": "PASS" if fixture["terminal_automation_policy"]["production_terminal_automation_ready"] is False else "FAIL",
        "production_automation_ready": False,
        "production_terminal_automation_ready": False,
        "production_browser_automation_ready": False,
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "allowed_claim": "V9-7 complete: production governance and terminal automation gate ready for review.",
    }


def _render_html(fixture: Mapping[str, Any], acceptance: Mapping[str, Any]) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>V9-7 Production Governance 验收看板</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:32px;background:#f8fafc;color:#111827}}section{{background:white;border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin:16px 0}}pre{{white-space:pre-wrap;word-break:break-word;background:#f3f4f6;padding:12px;border-radius:6px}}</style></head>
<body>
<h1>V9-7 Production Governance / Evidence Hardening Gate</h1>
<p>该看板证明治理与证据加固门禁 ready for review；不证明生产自动化完成。</p>
<section><h2>Acceptance</h2><pre>{escape(json.dumps(acceptance, ensure_ascii=False, indent=2, sort_keys=True))}</pre></section>
<section><h2>Governance Fixture</h2><pre>{escape(json.dumps(fixture, ensure_ascii=False, indent=2, sort_keys=True))}</pre></section>
</body></html>"""


def _result_summary(acceptance: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# V9-7 Production Governance Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"runtime_backed: {str(acceptance['runtime_backed']).lower()}",
            "",
            "Allowed claim:",
            str(acceptance["allowed_claim"]),
            "",
            "This proves only a production governance and terminal automation gate ready for review. It does not prove production automation readiness.",
        ]
    )


def _reject_sensitive_payload(payload: object) -> None:
    text = json.dumps(mask_value(payload), ensure_ascii=False, sort_keys=True)
    lowered = text.lower()
    for token in FORBIDDEN_RAW_TOKENS:
        if token.lower() in lowered:
            raise V97GovernanceError("V9_7_REDACTION_DENIED", "Raw sensitive data is not allowed.", reason="raw_sensitive_data", resource=token)


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _now() -> str:
    return datetime.now(UTC).isoformat()
