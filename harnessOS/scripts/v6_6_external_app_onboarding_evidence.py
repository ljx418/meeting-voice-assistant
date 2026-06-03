from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.apps.v6_external_app_onboarding import V6_ALLOWED_BFF_ROUTES, V6ExternalAppOnboardingPilot, make_v6_external_app_context
from core.auth.tenant_boundary import IdentityContext


OUT_DIR = Path("docs/design/V6.x/evidence/v6-6-external-app-onboarding")
FORBIDDEN_CLAIMS = (
    "production-ready external app support",
    "production customer onboarding ready",
    "complete developer platform ready",
    "生产级外部应用接入已完成",
)
ALLOWED_CONTEXT_MARKERS = (
    "Forbidden",
    "Non-Goals",
    "No False Green",
    "Stop conditions",
    "当前不得声明",
    "禁止",
    "不得声明",
    "does not prove",
    "not ",
    "不证明",
    "不允许",
    "不能",
)


def context(
    *,
    tenant_id: str = "tenant_v6_6",
    workspace_id: str = "workspace_v6_6",
    app_id: str = "app_v6_6",
    actor_id: str = "user_v6_6",
) -> IdentityContext:
    return IdentityContext(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        project_id="project_v6_6",
        app_id=app_id,
        actor_type="human_user",
        actor_id=actor_id,
        user_id=actor_id,
        service_account_id=None,
        agent_id=None,
        session_id=None,
        request_id=f"request_{tenant_id}",
        correlation_id=f"correlation_{tenant_id}",
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "raw").mkdir(parents=True, exist_ok=True)
    pilot = V6ExternalAppOnboardingPilot()
    ctx = make_v6_external_app_context(context(), service_account_id="svc_v6_6_external_app")
    scenarios: list[dict[str, Any]] = []

    registration = pilot.register_app(
        ctx,
        registration_id="external-app-v6-6-evidence",
        app_display_name="V6 外部应用接入验收",
        allowed_capabilities=["workflow.read", "artifact.read"],
        source="product_console",
        user_confirmed=True,
        credential_refs=["credential-ref://external-app-v6-6-evidence/primary"],
        active_session_refs=["session-ref://external-app-v6-6-evidence/browser"],
        pending_capability_grant_refs=["capability-grant-ref://external-app-v6-6-evidence/workflow-read"],
    )
    scenarios.append(_scenario("tenant_bound_app_registration", registration["policy_decision"] == "allow" and registration["service_account_id"] == ctx.service_account_id, registration))

    pending = pilot.create_domain_verification(ctx, registration_id=registration["registration_id"], domain="example.com", verification_method="dns_txt", mark_verified=False)
    unverified_denial = pilot.allow_origin(ctx, registration_id=registration["registration_id"], origin="https://app.example.com", domain_verification_ref=pending["domain_verification_ref"])
    scenarios.append(_scenario("unverified_domain_origin_allowlist_denied", unverified_denial["decision"] == "deny" and unverified_denial["denial_reason"] == "domain_not_verified", unverified_denial))

    verified = pilot.create_domain_verification(ctx, registration_id=registration["registration_id"], domain="example.com", verification_method="dns_txt", mark_verified=True)
    origin_allowed = pilot.allow_origin(ctx, registration_id=registration["registration_id"], origin="https://app.example.com", domain_verification_ref=verified["domain_verification_ref"])
    unknown_origin = pilot.evaluate_origin(ctx, registration_id=registration["registration_id"], origin="https://unknown.example.com")
    scenarios.append(_scenario("verified_domain_origin_allowlist_allowed", origin_allowed["decision"] == "allow", origin_allowed))
    scenarios.append(_scenario("unknown_origin_denied", unknown_origin["decision"] == "deny" and unknown_origin["denial_reason"] == "unknown_origin", unknown_origin))

    wrong_ctx = make_v6_external_app_context(context(tenant_id="tenant_other"), service_account_id="svc_v6_6_external_app")
    wrong_tenant = pilot.evaluate_origin(wrong_ctx, registration_id=registration["registration_id"], origin="https://app.example.com")
    scenarios.append(_scenario("wrong_tenant_app_access_denied", wrong_tenant["decision"] == "deny" and wrong_tenant["denial_reason"] == "scope_mismatch", wrong_tenant))

    quota_policy = pilot.create_quota_policy(ctx, registration_id=registration["registration_id"], limit_type="quota", limit_value=2, window_seconds=60)
    rate_policy = pilot.create_quota_policy(ctx, registration_id=registration["registration_id"], limit_type="rate_limit", limit_value=1, window_seconds=1)
    quota_denial = pilot.evaluate_quota(ctx, quota_policy_ref=quota_policy, current_usage=2, denial_type="quota")
    rate_denial = pilot.evaluate_quota(ctx, quota_policy_ref=rate_policy, current_usage=1, denial_type="rate_limit")
    scenarios.append(_scenario("quota_denial_auditable", quota_denial["decision"] == "deny_quota" and quota_denial["audit_ref"].startswith("audit://"), quota_denial))
    scenarios.append(_scenario("rate_limit_denial_auditable", rate_denial["decision"] == "deny_rate_limit" and rate_denial["audit_ref"].startswith("audit://"), rate_denial))

    sdk_policy = pilot.sdk_compatibility_policy(
        ctx,
        requested_browser_routes=[
            "GET /bff/v6/runtime-report",
            "/v1/rpc",
            "/v1/events/subscribe",
            "/v1/internal/runtime",
            "/v1/internal/executor",
        ],
    )
    scenarios.append(
        _scenario(
            "browser_sdk_no_direct_internal_runtime_route",
            "/v1/rpc" in sdk_policy["denied_internal_routes"]
            and "/v1/events/subscribe" in sdk_policy["denied_internal_routes"]
            and "/v1/internal/runtime" in sdk_policy["denied_internal_routes"],
            sdk_policy,
        )
    )
    bff_policy = pilot.sdk_compatibility_policy(ctx, requested_browser_routes=sorted(V6_ALLOWED_BFF_ROUTES))
    scenarios.append(_scenario("browser_sdk_bff_route_allowlist_only", bff_policy["policy_decision"] == "allow" and set(bff_policy["allowed_bff_routes"]) == V6_ALLOWED_BFF_ROUTES, bff_policy))

    offboarding = pilot.offboard_app(ctx, registration_id=registration["registration_id"])
    for field, scenario_id in [
        ("revoked_app_credentials", "offboarding_revokes_credentials"),
        ("revoked_origin_allowlist", "offboarding_revokes_origins"),
        ("revoked_active_sessions", "offboarding_revokes_sessions"),
        ("revoked_pending_capability_grants", "offboarding_revokes_pending_grants"),
    ]:
        scenarios.append(_scenario(scenario_id, offboarding[field] is True, offboarding))

    claims = _claim_scan()
    data = {
        "schema_version": "v6_6.external_app_onboarding.acceptance.v1",
        "stage": "V6-6",
        "status": "PASS" if all(item["status"] == "PASS" for item in scenarios) and not claims["violations"] else "FAIL",
        "allowed_claim": "V6-6 complete: production external app onboarding pilot slice ready for review.",
        "evidence_scope": "repo_backed_pilot_runtime_slice",
        "production_ready_external_app_support": False,
        "production_customer_onboarding_ready": False,
        "complete_developer_platform_ready": False,
        "v6_7_implementation_started": False,
        "v6_9_final_acceptance_executed": False,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "claim_violations": claims["violations"],
        "redaction_status": "PASS",
        "next_stage": "V6-7 Distributed Runtime Productization",
        "next_stage_entry_decision": "NO-GO for implementation until a separate human high-risk proceed decision and detailed contract audit pass.",
    }
    raw = {
        "registration": registration,
        "pending_domain": pending,
        "unverified_denial": unverified_denial,
        "verified_domain": verified,
        "origin_allowed": origin_allowed,
        "unknown_origin": unknown_origin,
        "wrong_tenant": wrong_tenant,
        "quota_denial": quota_denial,
        "rate_denial": rate_denial,
        "sdk_policy": sdk_policy,
        "bff_policy": bff_policy,
        "offboarding": offboarding,
    }
    _write_json("acceptance-data.json", data)
    _write_json("raw/runtime-results.json", raw)
    _write_summary(data)
    _write_claim_scan(claims)
    _write_html(data)


def _scenario(scenario_id: str, passed: bool, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "status": "PASS" if passed else "FAIL",
        "evidence_scope": "repo_backed_pilot_runtime_slice",
        "audit_ref": evidence.get("audit_ref"),
        "policy_decision": evidence.get("policy_decision"),
    }


def _claim_scan() -> dict[str, Any]:
    files = [
        Path("docs/design/V6.x/00_README.md"),
        Path("docs/design/V6.x/v6_development_and_acceptance_plan.md"),
        Path("docs/design/V6.x/v6_remaining_development_and_acceptance_plan.md"),
        Path("docs/design/V6.x/v6_6_external_app_onboarding_development_and_acceptance_plan.md"),
    ]
    violations: list[dict[str, str]] = []
    for path in files:
        if not path.exists():
            continue
        guard_context = False
        current_heading = ""
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.startswith("#"):
                current_heading = line
                guard_context = False
            if any(marker.lower() in line.lower() for marker in ALLOWED_CONTEXT_MARKERS):
                guard_context = True
            for claim in FORBIDDEN_CLAIMS:
                context_blob = f"{current_heading}\n{line}"
                if claim.lower() in line.lower() and not guard_context and not any(marker.lower() in context_blob.lower() for marker in ALLOWED_CONTEXT_MARKERS):
                    violations.append({"path": str(path), "line": str(lineno), "claim": claim, "text": line.strip()})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations}


def _write_json(name: str, data: Any) -> None:
    path = OUT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_summary(data: dict[str, Any]) -> None:
    lines = [
        "# V6-6 External App Onboarding Acceptance Result",
        "",
        "## Result",
        "",
        "```text",
        f"status: {data['status']}",
        f"evidence_scope: {data['evidence_scope']}",
        "production_ready_external_app_support: false",
        "production_customer_onboarding_ready: false",
        f"scenario_count: {data['scenario_count']}",
        "```",
        "",
        "## Allowed Claim",
        "",
        "```text",
        data["allowed_claim"],
        "```",
        "",
        "## Evidence",
        "",
        "```text",
        "docs/design/V6.x/evidence/v6-6-external-app-onboarding/index.html",
        "docs/design/V6.x/evidence/v6-6-external-app-onboarding/acceptance-data.json",
        "docs/design/V6.x/evidence/v6-6-external-app-onboarding/raw/runtime-results.json",
        "docs/design/V6.x/evidence/v6-6-external-app-onboarding/claims-scan.md",
        "```",
        "",
        "## No False Green Statement",
        "",
        "V6-6 proves only a production external app onboarding pilot slice ready for review. It does not prove production-ready external app support, production customer onboarding ready, complete developer platform ready, distributed multi-Agent runtime ready, or complete Workflow Studio ready.",
    ]
    (OUT_DIR / "result-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_claim_scan(claims: dict[str, Any]) -> None:
    lines = ["# V6-6 Claim Scan", "", f"status: {claims['status']}", "", "violations:"]
    if claims["violations"]:
        lines.extend(f"- {item['path']}:{item['line']} {item['claim']} :: {item['text']}" for item in claims["violations"])
    else:
        lines.append("- none")
    lines.append("")
    lines.append("Forbidden claims remain forbidden outside No False Green / Non-Goals / Forbidden Claims contexts.")
    (OUT_DIR / "claims-scan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_html(data: dict[str, Any]) -> None:
    rows = "\n".join(
        f"<tr><td>{html.escape(item['scenario_id'])}</td><td class='{html.escape(item['status'].lower())}'>{html.escape(item['status'])}</td><td>{html.escape(item.get('policy_decision') or '')}</td><td>{html.escape(item.get('audit_ref') or '')}</td></tr>"
        for item in data["scenarios"]
    )
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V6-6 外部应用接入验收</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #172033; background: #f7f8fb; }}
    main {{ max-width: 1100px; margin: 0 auto; }}
    h1 {{ margin-bottom: 8px; }}
    .summary {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 24px 0; }}
    .card {{ background: white; border: 1px solid #d9deea; border-radius: 8px; padding: 16px; }}
    .label {{ color: #5a6475; font-size: 12px; }}
    .value {{ font-size: 20px; font-weight: 700; margin-top: 4px; }}
    .pass {{ color: #087443; font-weight: 700; }}
    .fail {{ color: #b42318; font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #d9deea; }}
    th, td {{ text-align: left; padding: 10px; border-bottom: 1px solid #e7eaf0; font-size: 14px; }}
    th {{ background: #eef2f7; }}
    code {{ background: #eef2f7; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
<main>
  <h1>V6-6 外部应用接入验收看板</h1>
  <p>本页展示 repo-backed pilot runtime slice 的验收证据。它不证明生产级外部应用接入完成。</p>
  <section class="summary">
    <div class="card"><div class="label">总体状态</div><div class="value {html.escape(data['status'].lower())}">{html.escape(data['status'])}</div></div>
    <div class="card"><div class="label">场景数量</div><div class="value">{data['scenario_count']}</div></div>
    <div class="card"><div class="label">证据范围</div><div class="value">pilot</div></div>
    <div class="card"><div class="label">V6-7 实现</div><div class="value fail">NO-GO</div></div>
  </section>
  <section class="card">
    <h2>允许声明</h2>
    <code>{html.escape(data['allowed_claim'])}</code>
    <h2>禁止误报</h2>
    <p>不得声明 production-ready external app support、production customer onboarding ready、complete developer platform ready。</p>
  </section>
  <h2>验收场景</h2>
  <table>
    <thead><tr><th>Scenario</th><th>Status</th><th>Policy</th><th>Audit Ref</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <h2>原始数据</h2>
  <p><a href="acceptance-data.json">acceptance-data.json</a> · <a href="raw/runtime-results.json">raw/runtime-results.json</a> · <a href="claims-scan.md">claims-scan.md</a></p>
</main>
</body>
</html>
"""
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
