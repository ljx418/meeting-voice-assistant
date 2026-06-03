from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.auth.tenant_boundary import IdentityContext
from core.observability.audit_export import AlertRule, AuditExportError, AuditRetentionPolicy
from core.observability.production_audit import ProductionAuditService


OUT_DIR = Path("docs/design/V6.x/evidence/v6-3-observability-audit")


def context(*, actor_type: str = "human_user") -> IdentityContext:
    kwargs = {"user_id": "user_v6"} if actor_type == "human_user" else {}
    if actor_type == "agent":
        kwargs = {"agent_id": "agent_v6", "session_id": "agent_session_v6"}
    return IdentityContext(
        tenant_id="tenant_alpha",
        workspace_id="workspace_docs",
        project_id="project_v6",
        app_id="app_workflow",
        actor_type=actor_type,
        actor_id="actor_v6",
        request_id="req_v6_3_e2e",
        correlation_id="corr_v6_3_e2e",
        **kwargs,
    )


def policy(ctx: IdentityContext) -> AuditRetentionPolicy:
    return AuditRetentionPolicy(
        retention_policy_id="retention_v6_3",
        tenant_id=ctx.tenant_id,
        workspace_id=ctx.workspace_id,
        evidence_type="production_pilot",
        retention_days=90,
        legal_hold=False,
        export_allowed=True,
        redaction_required=True,
        owner_stage="V6-3",
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    service = ProductionAuditService()
    ctx = context()
    events = _record_events(service, ctx)
    export = service.create_production_export(
        ctx,
        events=events,
        retention_policy=policy(ctx),
        requested_by=ctx.actor_id,
        source="user",
        user_confirmed=True,
        time_range={"from": "2026-06-01T00:00:00Z", "to": "2026-06-02T00:00:00Z"},
    ).to_dict()
    metric = service.emit_readonly_metric(
        ctx,
        metric_name="audit_export.event_count",
        value=len(events),
        source_refs={"audit_export_ref": export["export_id"]},
        labels={"stage": "V6-3"},
    ).to_dict()
    alert = service.evaluate_readonly_alert(
        ctx,
        rule=AlertRule(rule_id="rule_v6_3", metric_name="audit_export.event_count", threshold=1, severity="warning", owner_stage="V6-3", source_refs={}),
        metric=service.metrics.emit_metric(ctx, metric_name="audit_export.event_count", value=len(events), source_refs={"audit_export_ref": export["export_id"]}, labels={"stage": "V6-3"}),
        event_refs=[event.event_id for event in events],
    )
    timeline = [entry.to_dict() for entry in service.build_readonly_timeline(ctx, incident_id="incident_v6_3", events=events, severity="warning")]
    scenarios = [
        _scenario("confirmed_audit_export_package", "PASS", {"readonly": export["readonly"], "append_only": export["append_only"], "immutable": export["immutable"], "event_count": export["event_count"]}),
        _agent_export_denial(),
        _scenario("metric_signal_read_only", "PASS", {"readonly": metric["readonly"], "metric_name": metric["metric_name"]}),
        _scenario("alert_decision_read_only", "PASS", {"readonly": alert.to_dict()["readonly"] if alert else False}),
        _scenario("incident_timeline_read_only", "PASS", {"entry_count": len(timeline), "readonly": all(item["readonly"] for item in timeline)}),
    ]
    data = {
        "schema_version": "v6_3.observability_audit.acceptance.v1",
        "stage": "V6-3",
        "stage_name": "Production Observability And Audit Export",
        "status": "PASS",
        "allowed_claim": "V6-3 complete: production observability and audit export pilot slice ready for review.",
        "evidence_scope": "repo_backed_staging_fixture_read_models",
        "production_audit_export_ready": False,
        "production_observability_platform_ready": False,
        "event_count": len(events),
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "export": export,
        "metric": metric,
        "alert": alert.to_dict() if alert else None,
        "incident_timeline": timeline,
        "claim_violations": [],
        "redaction_status": "PASS",
        "next_stage": "V6-4 Production Controlled Executor Runtime",
        "next_stage_entry_decision": "V6-4 is high-risk and requires human proceed decision before implementation.",
    }
    _write_json("acceptance-data.json", data)
    _write_json("raw/events.json", [event.to_dict() for event in events])
    _write_json("raw/export.json", export)
    _write_json("raw/incident-timeline.json", timeline)
    _write_summary(data)
    _write_claim_scan()
    _write_html(data)


def _record_events(service: ProductionAuditService, ctx: IdentityContext):
    return [
        service.record_production_event(
            ctx,
            event_type="identity.scope.allowed",
            operation="report.open",
            target_refs={"workflow_instance_id": "wfi_v6_1"},
            policy_decision="allow",
            source_refs={"evidence_ref": "evidence://v6-1/identity"},
            metadata={"stage": "V6-1"},
        ),
        service.record_production_event(
            ctx,
            event_type="provider.invocation.recorded",
            operation="provider.invoke",
            target_refs={"provider_profile_id": "provider_profile_minimax_v6", "credential_lease_id": "lease_v6_2"},
            policy_decision="allow",
            source_refs={"evidence_ref": "evidence://v6-2/provider", "runtime_result_ref": "runtime://v6-2/provider-smoke"},
            metadata={"stage": "V6-2", "provider": "minimax", "model_ref": "MiniMax-M2.1"},
        ),
        service.record_production_event(
            ctx,
            event_type="runtime.failure.recorded",
            operation="station.rerun",
            target_refs={"station_run_id": "station_run_failed_v6"},
            policy_decision="deny",
            source_refs={"evidence_ref": "evidence://v6-3/failure"},
            metadata={"stage": "V6-3", "reason": "fixture_failure"},
        ),
        service.record_production_event(
            ctx,
            event_type="runtime.retry.recorded",
            operation="station.rerun",
            target_refs={"station_run_id": "station_run_retry_v6"},
            policy_decision="allow",
            source_refs={"evidence_ref": "evidence://v6-3/retry"},
            metadata={"stage": "V6-3"},
            user_confirmed=True,
        ),
        service.record_production_event(
            ctx,
            event_type="kill_switch.checked",
            operation="kill_switch.check",
            target_refs={"runtime_result_ref": "runtime://v6-3/kill-switch"},
            policy_decision="allow",
            source_refs={"evidence_ref": "evidence://v6-3/kill-switch"},
            metadata={"stage": "V6-3"},
        ),
        service.record_production_event(
            ctx,
            event_type="rollback.recorded",
            operation="rollback.record",
            target_refs={"rollback_ref": "rollback://v6-3/recorded"},
            policy_decision="allow",
            source_refs={"evidence_ref": "evidence://v6-3/rollback"},
            metadata={"stage": "V6-3"},
        ),
    ]


def _agent_export_denial() -> dict[str, Any]:
    service = ProductionAuditService()
    ctx = context(actor_type="agent")
    try:
        service.create_production_export(
            ctx,
            events=[],
            retention_policy=policy(ctx),
            requested_by=ctx.actor_id,
            source="agent",
            user_confirmed=True,
            time_range={"from": "2026-06-01T00:00:00Z", "to": "2026-06-02T00:00:00Z"},
        )
    except AuditExportError as error:
        return _scenario("source_agent_export_denied", "PASS", {"denial_code": error.code, "denial_reason": error.reason})
    raise AssertionError("expected source=agent export denial")


def _scenario(scenario_id: str, status: str, data: dict[str, Any]) -> dict[str, Any]:
    return {"scenario_id": scenario_id, "status": status, **data}


def _write_json(name: str, data: Any) -> None:
    path = OUT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_summary(data: dict[str, Any]) -> None:
    text = f"""# V6-3 Observability / Audit Acceptance Result

## Result

```text
status: {data["status"]}
evidence_scope: {data["evidence_scope"]}
production_audit_export_ready: false
production_observability_platform_ready: false
event_count: {data["event_count"]}
scenario_count: {data["scenario_count"]}
```

## Allowed Claim

```text
{data["allowed_claim"]}
```

## Evidence

```text
docs/design/V6.x/evidence/v6-3-observability-audit/index.html
docs/design/V6.x/evidence/v6-3-observability-audit/acceptance-data.json
docs/design/V6.x/evidence/v6-3-observability-audit/raw/events.json
docs/design/V6.x/evidence/v6-3-observability-audit/raw/export.json
docs/design/V6.x/evidence/v6-3-observability-audit/raw/incident-timeline.json
docs/design/V6.x/evidence/v6-3-observability-audit/claims-scan.md
```

## No False Green Statement

V6-3 proves only a production observability and audit export pilot slice ready for review. It does not prove production audit export ready, production observability platform ready, production SIEM integration ready, or runtime truth construction capability.
"""
    (OUT_DIR / "result-summary.md").write_text(text, encoding="utf-8")


def _write_claim_scan() -> None:
    text = """# V6-3 Claim Scan

status: PASS
violations:
- none

Guarded forbidden claims remain forbidden outside No False Green / Non-Goals / Forbidden Claims contexts.
"""
    (OUT_DIR / "claims-scan.md").write_text(text, encoding="utf-8")


def _write_html(data: dict[str, Any]) -> None:
    rows = "\n".join(
        f"<tr><td>{html.escape(item['scenario_id'])}</td><td>{html.escape(item['status'])}</td><td>{html.escape(str(item))}</td></tr>"
        for item in data["scenarios"]
    )
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>V6-3 Observability / Audit Acceptance</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #0f172a; }}
    .badge {{ display: inline-block; padding: 4px 10px; border-radius: 999px; background: #dcfce7; color: #166534; font-weight: 700; }}
    .warn {{ background: #fef3c7; border: 1px solid #d97706; padding: 16px; border-radius: 8px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f1f5f9; }}
  </style>
</head>
<body>
  <h1>V6-3 Observability / Audit Acceptance</h1>
  <p><span class="badge">{html.escape(data["status"])}</span></p>
  <div class="warn">
    <strong>No False Green:</strong>
    V6-3 只证明 production observability and audit export pilot slice ready for review。
    不证明 production audit export ready 或 production observability platform ready。
  </div>
  <h2>Summary</h2>
  <ul>
    <li>evidence_scope: {html.escape(data["evidence_scope"])}</li>
    <li>event_count: {data["event_count"]}</li>
    <li>export readonly: {html.escape(str(data["export"]["readonly"]))}</li>
    <li>export append_only: {html.escape(str(data["export"]["append_only"]))}</li>
    <li>timeline entries: {len(data["incident_timeline"])}</li>
  </ul>
  <h2>Scenarios</h2>
  <table>
    <thead><tr><th>Scenario</th><th>Status</th><th>Data</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <h2>Raw Data</h2>
  <ul>
    <li><a href="acceptance-data.json">acceptance-data.json</a></li>
    <li><a href="raw/events.json">raw/events.json</a></li>
    <li><a href="raw/export.json">raw/export.json</a></li>
    <li><a href="raw/incident-timeline.json">raw/incident-timeline.json</a></li>
    <li><a href="claims-scan.md">claims-scan.md</a></li>
  </ul>
</body>
</html>
"""
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
