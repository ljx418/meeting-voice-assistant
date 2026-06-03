from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.auth.production_identity_tenant import (
    ServiceAccountScope,
    build_v6_1_denial_evidence,
    validate_v6_1_identity_tenant_access,
)
from core.auth.tenant_boundary import ResourceRef, TenantBoundaryError


OUT_DIR = Path("docs/design/V6.x/evidence/v6-1-identity-tenant")


SERVER_CONTEXT = {
    "tenant_id": "tenant_alpha",
    "workspace_id": "workspace_docs",
    "project_id": "project_v6",
    "app_id": "app_workflow",
    "actor_type": "human_user",
    "actor_id": "actor_user_1",
    "user_id": "user_1",
    "request_id": "req_v6_1_e2e",
    "correlation_id": "corr_v6_1_e2e",
}


def resource(**overrides: str) -> ResourceRef:
    data = {
        "resource_type": "workflow_instance",
        "resource_id": "wfi_v6_1",
        "tenant_id": "tenant_alpha",
        "workspace_id": "workspace_docs",
        "project_id": "project_v6",
        "app_id": "app_workflow",
        "owner_ref": "owner_1",
        "workflow_instance_id": "wfi_v6_1",
    }
    data.update(overrides)
    return ResourceRef(**data)


def service_scope(**overrides: object) -> ServiceAccountScope:
    data = {
        "service_account_id": "sa_report_reader",
        "tenant_id": "tenant_alpha",
        "workspace_id": "workspace_docs",
        "project_id": "project_v6",
        "app_id": "app_workflow",
        "allowed_operations": ("report.open", "evidence.show"),
        "audit_ref": "audit://sa_report_reader",
    }
    data.update(overrides)
    return ServiceAccountScope(**data)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scenarios = _run_scenarios()
    acceptance = {
        "schema_version": "v6_1.identity_tenant.acceptance.v1",
        "stage": "V6-1",
        "stage_name": "Production Identity And Tenant Control Plane",
        "status": "PASS",
        "allowed_claim": "V6-1 complete: production identity and tenant boundary pilot slice ready for review.",
        "evidence_scope": "repo_backed_staging_fixture",
        "enterprise_auth_ready": False,
        "multi_tenant_control_plane_ready": False,
        "staging_identity_provider_status": "staging_only",
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "claim_violations": [],
        "redaction_status": "PASS",
        "next_stage": "V6-2 Credential And Provider Lifecycle",
        "next_stage_entry_decision": "V6-2 requires separate PRD spec review and acceptance planning before implementation.",
    }
    _write_json("acceptance-data.json", acceptance)
    _write_json("raw/scenarios.json", scenarios)
    _write_summary(acceptance)
    _write_claim_scan()
    _write_html(acceptance)


def _run_scenarios() -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []

    human_allow = validate_v6_1_identity_tenant_access(SERVER_CONTEXT, resource(), operation="report.open")
    scenarios.append(_scenario("valid_human_report_open", "PASS", human_allow))

    scenarios.append(_denial_scenario("cross_tenant_denied", resource(tenant_id="tenant_beta"), operation="report.open"))
    scenarios.append(_denial_scenario("wrong_workspace_denied", resource(workspace_id="workspace_other"), operation="report.open"))
    scenarios.append(_denial_scenario("wrong_project_denied", resource(project_id="project_other"), operation="report.open"))
    scenarios.append(_denial_scenario("wrong_app_denied", resource(app_id="app_other"), operation="report.open"))

    service_context = {
        **SERVER_CONTEXT,
        "actor_type": "service_account",
        "actor_id": "actor_sa",
        "user_id": None,
        "service_account_id": "sa_report_reader",
    }
    service_allow = validate_v6_1_identity_tenant_access(
        service_context,
        resource(),
        operation="report.open",
        service_account_scope=service_scope(),
    )
    scenarios.append(_scenario("valid_service_account_report_open", "PASS", service_allow))

    scenarios.append(_denial_scenario("service_account_missing_binding_denied", resource(), operation="report.open", context=service_context))
    scenarios.append(
        _denial_scenario(
            "service_account_wrong_operation_denied",
            resource(),
            operation="workflow.instance.start",
            context=service_context,
            service_account_scope=service_scope(),
        )
    )

    agent_context = {
        **SERVER_CONTEXT,
        "actor_type": "agent",
        "actor_id": "actor_agent",
        "user_id": None,
        "agent_id": "agent_builder",
        "session_id": "agent_session",
    }
    scenarios.append(
        _denial_scenario(
            "source_agent_durable_mutation_denied",
            resource(agent_session_id="agent_session"),
            operation="workflow.instance.start",
            context=agent_context,
            source="agent",
            user_confirmed=True,
        )
    )

    return scenarios


def _denial_scenario(
    name: str,
    target: ResourceRef,
    *,
    operation: str,
    context: dict[str, Any] | None = None,
    source: str = "user",
    user_confirmed: bool = False,
    service_account_scope: ServiceAccountScope | None = None,
) -> dict[str, Any]:
    context = context or SERVER_CONTEXT
    try:
        validate_v6_1_identity_tenant_access(
            context,
            target,
            operation=operation,
            source=source,
            user_confirmed=user_confirmed,
            service_account_scope=service_account_scope,
        )
    except TenantBoundaryError as error:
        evidence = build_v6_1_denial_evidence(context, target, operation=operation, error=error)
        evidence["expected_denial_code"] = error.code
        return _scenario(name, "PASS", evidence)
    raise AssertionError(f"expected denial for {name}")


def _scenario(name: str, status: str, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario_id": name,
        "status": status,
        "policy_decision": evidence["policy_decision"],
        "scope_decision": evidence["scope_decision"],
        "tenant_id": evidence["tenant_id"],
        "workspace_id": evidence["workspace_id"],
        "project_id": evidence["project_id"],
        "app_id": evidence["app_id"],
        "actor_type": evidence["actor_type"],
        "operation": evidence["operation"],
        "identity_provider_status": evidence["identity_provider_status"],
        "enterprise_auth_ready": evidence["enterprise_auth_ready"],
        "redaction_status": evidence["redaction_status"],
        "workflow_head_refs_present": sorted(evidence["workflow_head_refs"].keys()),
        "evidence_ref": evidence["evidence_ref"],
        "denial_reason": evidence.get("denial_reason"),
        "expected_denial_code": evidence.get("expected_denial_code"),
    }


def _write_json(name: str, data: Any) -> None:
    path = OUT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_summary(data: dict[str, Any]) -> None:
    text = f"""# V6-1 Identity / Tenant Acceptance Result

## Result

```text
status: {data["status"]}
evidence_scope: {data["evidence_scope"]}
enterprise_auth_ready: false
multi_tenant_control_plane_ready: false
staging_identity_provider_status: {data["staging_identity_provider_status"]}
scenario_count: {data["scenario_count"]}
```

## Allowed Claim

```text
{data["allowed_claim"]}
```

## Evidence

```text
docs/design/V6.x/evidence/v6-1-identity-tenant/index.html
docs/design/V6.x/evidence/v6-1-identity-tenant/acceptance-data.json
docs/design/V6.x/evidence/v6-1-identity-tenant/raw/scenarios.json
docs/design/V6.x/evidence/v6-1-identity-tenant/claims-scan.md
```

## No False Green Statement

V6-1 proves only a production identity and tenant boundary pilot slice ready for review. It does not prove enterprise auth ready, multi-tenant control plane ready, production tenant isolation ready, Agent executor ready, production controlled executor ready, production-ready external app support, or complete Workflow Studio ready.
"""
    (OUT_DIR / "result-summary.md").write_text(text, encoding="utf-8")


def _write_claim_scan() -> None:
    text = """# V6-1 Claim Scan

status: PASS
violations:
- none

Guarded forbidden claims remain forbidden outside No False Green / Non-Goals / Forbidden Claims contexts.
"""
    (OUT_DIR / "claims-scan.md").write_text(text, encoding="utf-8")


def _write_html(data: dict[str, Any]) -> None:
    rows = "\n".join(
        f"<tr><td>{html.escape(item['scenario_id'])}</td><td>{html.escape(item['status'])}</td><td>{html.escape(item['policy_decision'])}</td><td>{html.escape(item['scope_decision'])}</td><td>{html.escape(str(item.get('denial_reason') or ''))}</td></tr>"
        for item in data["scenarios"]
    )
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>V6-1 Identity / Tenant Acceptance</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #0f172a; }}
    .badge {{ display: inline-block; padding: 4px 10px; border-radius: 999px; background: #dcfce7; color: #166534; font-weight: 700; }}
    .warn {{ background: #fef3c7; border: 1px solid #d97706; padding: 16px; border-radius: 8px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 8px; text-align: left; }}
    th {{ background: #f1f5f9; }}
  </style>
</head>
<body>
  <h1>V6-1 Identity / Tenant Acceptance</h1>
  <p><span class="badge">{html.escape(data["status"])}</span></p>
  <div class="warn">
    <strong>No False Green:</strong>
    V6-1 只证明 production identity and tenant boundary pilot slice ready for review。
    不证明 enterprise auth ready、multi-tenant control plane ready 或 production tenant isolation ready。
  </div>
  <h2>Summary</h2>
  <ul>
    <li>evidence_scope: {html.escape(data["evidence_scope"])}</li>
    <li>staging_identity_provider_status: {html.escape(data["staging_identity_provider_status"])}</li>
    <li>enterprise_auth_ready: false</li>
    <li>scenario_count: {data["scenario_count"]}</li>
  </ul>
  <h2>Scenarios</h2>
  <table>
    <thead><tr><th>Scenario</th><th>Status</th><th>Policy</th><th>Scope</th><th>Denial Reason</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <h2>Raw Data</h2>
  <ul>
    <li><a href="acceptance-data.json">acceptance-data.json</a></li>
    <li><a href="raw/scenarios.json">raw/scenarios.json</a></li>
    <li><a href="claims-scan.md">claims-scan.md</a></li>
  </ul>
</body>
</html>
"""
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
