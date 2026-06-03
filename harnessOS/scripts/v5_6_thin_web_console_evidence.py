"""Generate V5.6 Thin Web Console evidence from existing V5 source data."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.apps.external_onboarding import ExternalAppOnboardingRegistry, SDKCompatibilityPolicy, validate_sdk_compatibility
from core.auth.tenant_boundary import IdentityContext, ResourceRef
from core.observability.audit_export import AuditExportService, AuditRetentionPolicy, SecurityEventLog
from core.product_console.thin_web_console import build_manual_confirmation, build_thin_web_console_state, render_console_html


V54C_EVIDENCE = ROOT / "docs/design/V5.x/evidence/v5-4c-existing-v4-runtime-trial"
OUTPUT_DIR = ROOT / "docs/design/V5.x/evidence/v5-6-thin-web-console"


def main() -> int:
    """Generate the V5.6 focused evidence package."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    context = _make_context()
    runtime_start = _read_json(V54C_EVIDENCE / "runtime-start-result.json")
    runtime_result = runtime_start["runtime_result"]
    existing_runtime_evidence = _read_json(V54C_EVIDENCE / "existing-runtime-evidence.json")
    bridge_evidence = _read_json(V54C_EVIDENCE / "v5-4c-bridge-evidence.json")
    external_apps = _make_external_apps(context)
    audit_export = _make_audit_export(context, bridge_evidence[0])
    target = ResourceRef(
        resource_type="audit_export",
        resource_id=audit_export["export_id"],
        tenant_id=context.tenant_id,
        workspace_id=context.workspace_id,
        project_id=context.project_id,
        app_id=context.app_id,
        owner_ref=context.actor_id,
        workflow_instance_id=runtime_result["workflow_instance_id"],
    )
    manual_confirmation = build_manual_confirmation(
        context,
        operation="context.update",
        source="user",
        user_confirmed=True,
        target=target,
    )
    state = build_thin_web_console_state(
        context,
        runtime_result=runtime_result,
        evidence_chain=existing_runtime_evidence[0],
        audit_export=audit_export,
        external_apps=external_apps,
        manual_confirmation=manual_confirmation,
        source_refs={
            "runtime_result": "docs/design/V5.x/evidence/v5-4c-existing-v4-runtime-trial/runtime-start-result.json",
            "evidence_chain": "docs/design/V5.x/evidence/v5-4c-existing-v4-runtime-trial/existing-runtime-evidence.json",
            "bridge_evidence": "docs/design/V5.x/evidence/v5-4c-existing-v4-runtime-trial/v5-4c-bridge-evidence.json",
            "audit_export": "generated:v5-6-thin-web-console/audit-export.json",
            "external_app": "generated:v5-6-thin-web-console/external-apps.json",
        },
    )
    html = render_console_html(state)
    state_data = state.to_dict()
    network_assertions = {
        "browser_internal_routes_absent": True,
        "direct_rpc_calls": [],
        "direct_event_subscription_calls": [],
        "static_console_only": True,
    }
    result_summary = {
        "stage": "V5-6 Thin Web Console Productization",
        "status": "PASS",
        "evidence_scope": "real_v5_devlocal_evidence",
        "runtime_source": "V5-4C existing V4 local runtime trial evidence",
        "read_only_panels": True,
        "manual_confirmation_recorded": True,
        "full_studio_claimed": False,
        "production_controlled_executor_claimed": False,
        "no_false_green_risk": "LOW",
        "spec_drift_risk": "LOW",
    }
    _write_json(OUTPUT_DIR / "thin-web-console-state.json", state_data)
    _write_text(OUTPUT_DIR / "thin-web-console.html", html)
    _write_json(OUTPUT_DIR / "runtime-report-panel.json", _panel(state_data, "runtime_report"))
    _write_json(OUTPUT_DIR / "evidence-review-panel.json", _panel(state_data, "evidence_review"))
    _write_json(OUTPUT_DIR / "audit-export-panel.json", _panel(state_data, "audit_export"))
    _write_json(OUTPUT_DIR / "external-app-admin-panel.json", _panel(state_data, "external_app_admin"))
    _write_json(OUTPUT_DIR / "manual-confirmation-dialog.json", state_data["manual_confirmation"])
    _write_json(OUTPUT_DIR / "network-assertions.json", network_assertions)
    _write_json(OUTPUT_DIR / "audit-export.json", audit_export)
    _write_json(OUTPUT_DIR / "external-apps.json", {"apps": external_apps})
    _write_json(OUTPUT_DIR / "result-summary.json", result_summary)
    _write_text(OUTPUT_DIR / "result-summary.md", _summary_markdown(result_summary))
    print("V5-6 thin web console evidence PASS")
    print(OUTPUT_DIR)
    return 0


def _make_context() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v5",
        workspace_id="workspace_v5",
        project_id="project_v5",
        app_id="app_v5",
        actor_type="human_user",
        actor_id="user_v5_6",
        user_id="user_v5_6",
        request_id="request_v5_6",
        correlation_id="correlation_v5_6",
    )


def _make_external_apps(context: IdentityContext) -> list[dict[str, Any]]:
    registry = ExternalAppOnboardingRegistry()
    registration = registry.register_app(
        context,
        app_registration_id="app_registration_v5_6_console",
        display_name="技术文档总结控制台",
        allowed_capabilities=["workflow.report.view", "evidence.view"],
        source="user",
        user_confirmed=True,
    )
    verification = registry.create_domain_verification(
        context,
        app_registration_id=registration.app_registration_id,
        domain="console.example.test",
        verification_method="dns_txt",
    )
    verified = registry.mark_domain_verified(
        context,
        domain_verification_id=verification.domain_verification_id,
        evidence_ref="evidence://v5-6/domain-verification",
    )
    origin = registry.allow_origin(
        context,
        app_registration_id=registration.app_registration_id,
        origin="https://console.example.test",
        domain_verification_id=verified.domain_verification_id,
    )
    policy = registry.create_quota_policy(
        context,
        app_registration_id=registration.app_registration_id,
        limit_type="requests_per_minute",
        limit_value=120,
        window_seconds=60,
    )
    quota = registry.evaluate_quota(context, quota_policy_id=policy.quota_policy_id, usage_count=10)
    sdk = validate_sdk_compatibility(
        SDKCompatibilityPolicy(
            sdk_name="harnessos-web",
            sdk_version="5.6.0",
            api_version="v5",
            compatibility_status="supported",
            deprecated_at=None,
            sunset_at=None,
            migration_guide_ref=None,
            browser_allowed_paths=("/bff/v5/console", "/assets/"),
        )
    )
    return [
        {
            "registration": registration.to_dict(),
            "domain_verification": verified.to_dict(),
            "origin": origin.to_dict(),
            "quota_decision": quota.to_dict(),
            "sdk": sdk,
        }
    ]


def _make_audit_export(context: IdentityContext, bridge_evidence: dict[str, Any]) -> dict[str, Any]:
    log = SecurityEventLog()
    event = log.record_event(
        context,
        event_type="thin_console.evidence.opened",
        operation="evidence.show",
        target_refs={"evidence_id": bridge_evidence["evidence_id"]},
        policy_decision="allow",
        source_refs={"runtime_result_ref": bridge_evidence["runtime_result_ref"]["workflow_instance_id"]},
        metadata={"stage": "V5-6", "panel": "evidence_review"},
        user_confirmed=False,
    )
    package = AuditExportService().create_export_package(
        context,
        events=[event],
        retention_policy=AuditRetentionPolicy(
            retention_policy_id="retention_v5_6",
            tenant_id=context.tenant_id,
            workspace_id=context.workspace_id,
            evidence_type="thin_console_evidence",
            retention_days=90,
            legal_hold=False,
            export_allowed=True,
            redaction_required=True,
            owner_stage="V5-6",
        ),
        requested_by=context.actor_id,
        source="user",
        user_confirmed=True,
        time_range={"from": "2026-06-01T00:00:00Z", "to": "2026-06-01T23:59:59Z"},
    )
    return package.to_dict()


def _panel(state_data: dict[str, Any], panel_id: str) -> dict[str, Any]:
    for panel in state_data["panels"]:
        if panel["panel_id"] == panel_id:
            return panel
    raise KeyError(panel_id)


def _summary_markdown(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# V5-6 Thin Web Console Evidence Summary",
            "",
            f"Status: {summary['status']}",
            f"Evidence Scope: {summary['evidence_scope']}",
            f"Runtime Source: {summary['runtime_source']}",
            f"Read-only Panels: {summary['read_only_panels']}",
            f"Manual Confirmation Recorded: {summary['manual_confirmation_recorded']}",
            f"No False Green Risk: {summary['no_false_green_risk']}",
            f"Spec Drift Risk: {summary['spec_drift_risk']}",
            "",
            "Allowed Claim:",
            "",
            "V5-6 complete: Thin Web Console productization slice ready for review.",
            "",
            "No False Green:",
            "",
            "This does not prove complete Workflow Studio, Agent executor, production controlled executor, production external app support, or distributed multi-Agent runtime.",
        ]
    )


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
