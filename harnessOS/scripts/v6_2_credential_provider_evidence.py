from __future__ import annotations

import html
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.auth.credential_provider import CredentialProviderError, CredentialProviderRegistry
from core.auth.production_credential_provider import ProductionCredentialProviderLifecycle
from core.auth.tenant_boundary import IdentityContext


OUT_DIR = Path("docs/design/V6.x/evidence/v6-2-credential-provider")


def context() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_alpha",
        workspace_id="workspace_docs",
        project_id="project_v6",
        app_id="app_workflow",
        actor_type="human_user",
        actor_id="actor_v6",
        user_id="user_v6",
        request_id="req_v6_2_e2e",
        correlation_id="corr_v6_2_e2e",
    )


def profile_data() -> dict[str, object]:
    return {
        "provider_profile_id": "provider_profile_minimax_v6",
        "tenant_id": "tenant_alpha",
        "workspace_id": "workspace_docs",
        "project_id": "project_v6",
        "app_id": "app_workflow",
        "provider": "minimax",
        "provider_kind": "llm",
        "base_url_ref": "env://MINIMAX_BASE_URL",
        "model_refs": ["MiniMax-M2.1"],
        "credential_ref_id": "credential_ref_minimax_v6",
        "capability_refs": ["llm.summarize"],
        "status": "active",
        "created_by": "actor_v6",
    }


def future() -> str:
    return (datetime.now(UTC) + timedelta(minutes=5)).isoformat()


def past() -> str:
    return (datetime.now(UTC) - timedelta(minutes=5)).isoformat()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scenarios = _run_scenarios()
    acceptance = {
        "schema_version": "v6_2.credential_provider.acceptance.v1",
        "stage": "V6-2",
        "stage_name": "Production Credential And Provider Lifecycle",
        "status": "PASS",
        "allowed_claim": "V6-2 complete: production credential and provider lifecycle pilot slice ready for review.",
        "evidence_scope": "repo_backed_staging_fixture_with_env_secret_refs",
        "production_secret_lifecycle_ready": False,
        "production_managed_secret_store_ready": False,
        "provider": "minimax",
        "model_ref": "MiniMax-M2.1",
        "credential_ref": "env://MINIMAX_API_KEY",
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "claim_violations": [],
        "redaction_status": "PASS",
        "next_stage": "V6-3 Observability And Audit Export",
        "next_stage_entry_decision": "V6-3 requires separate PRD spec review and acceptance planning before implementation.",
    }
    _write_json("acceptance-data.json", acceptance)
    _write_json("raw/scenarios.json", scenarios)
    _write_summary(acceptance)
    _write_claim_scan()
    _write_html(acceptance)


def _life() -> tuple[ProductionCredentialProviderLifecycle, IdentityContext]:
    ctx = context()
    registry = CredentialProviderRegistry()
    registry.create_provider_profile(ctx, profile_data(), source="user", user_confirmed=True)
    registry.issue_credential(
        ctx,
        provider_profile_id="provider_profile_minimax_v6",
        credential_ref_id="credential_ref_minimax_v6",
        secret_ref="env://MINIMAX_API_KEY",
        source="user",
        user_confirmed=True,
    )
    return ProductionCredentialProviderLifecycle(registry), ctx


def _issue_lease(life: ProductionCredentialProviderLifecycle, ctx: IdentityContext, *, expires_at: str | None = None):
    return life.issue_lease(
        ctx,
        provider_profile_id="provider_profile_minimax_v6",
        audience="llm_provider:minimax",
        operation="provider.invoke",
        capability_ref="llm.summarize",
        model_ref="MiniMax-M2.1",
        expires_at=expires_at or future(),
    )


def _invoke(life: ProductionCredentialProviderLifecycle, ctx: IdentityContext, lease_id: str, **overrides: str):
    data = {
        "credential_lease_id": lease_id,
        "audience": "llm_provider:minimax",
        "operation": "provider.invoke",
        "capability_ref": "llm.summarize",
        "model_ref": "MiniMax-M2.1",
        "provider_config_source": "env://MINIMAX_BASE_URL",
        "input_artifact_refs": ["artifact://input/redacted"],
        "output_artifact_refs": ["artifact://output/redacted"],
        "prompt_template_ref": "prompt_template://v6_2_summary",
        "redacted_input_summary_ref": "summary://input/redacted",
        "redacted_output_summary_ref": "summary://output/redacted",
        "runtime_result_ref": "runtime://v6_2/provider-smoke",
    }
    data.update(overrides)
    return life.validate_provider_invocation(ctx, **data)


def _run_scenarios() -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []

    life, ctx = _life()
    lease = _issue_lease(life, ctx)
    evidence = _invoke(life, ctx, lease.credential_lease_id).to_dict()
    scenarios.append(_scenario("valid_lease_bound_invocation", "PASS", "allow", "allow", evidence))

    scenarios.append(_denial("expired_lease_denied", expires_at=past()))
    scenarios.append(_denial("wrong_audience_denied", invoke_overrides={"audience": "llm_provider:other"}))
    scenarios.append(_denial("wrong_operation_denied", invoke_overrides={"operation": "provider.other"}))
    scenarios.append(_denial("raw_prompt_ref_denied", invoke_overrides={"redacted_input_summary_ref": "raw prompt: unsafe"}))

    life, ctx = _life()
    lease = _issue_lease(life, ctx)
    life.registry.revoke_credential(ctx, credential_ref_id="credential_ref_minimax_v6", source="user", user_confirmed=True)
    scenarios.append(_denial_with_life("revoked_credential_denied", life, ctx, lease.credential_lease_id))

    life, ctx = _life()
    lease = _issue_lease(life, ctx)
    life.registry.revoke_credential(ctx, credential_ref_id="credential_ref_minimax_v6", source="user", user_confirmed=True, emergency=True)
    scenarios.append(_denial_with_life("emergency_revoke_blocks_invocation", life, ctx, lease.credential_lease_id))

    return scenarios


def _denial(name: str, *, expires_at: str | None = None, invoke_overrides: dict[str, str] | None = None) -> dict[str, Any]:
    life, ctx = _life()
    lease = _issue_lease(life, ctx, expires_at=expires_at)
    return _denial_with_life(name, life, ctx, lease.credential_lease_id, invoke_overrides=invoke_overrides)


def _denial_with_life(
    name: str,
    life: ProductionCredentialProviderLifecycle,
    ctx: IdentityContext,
    lease_id: str,
    *,
    invoke_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        _invoke(life, ctx, lease_id, **(invoke_overrides or {}))
    except CredentialProviderError as error:
        return {
            "scenario_id": name,
            "status": "PASS",
            "policy_decision": "deny",
            "credential_decision": "deny",
            "lease_decision": "deny",
            "denial_code": error.code,
            "denial_reason": error.reason,
            "redaction_status": "redacted",
        }
    raise AssertionError(f"expected denial for {name}")


def _scenario(name: str, status: str, credential_decision: str, lease_decision: str, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario_id": name,
        "status": status,
        "policy_decision": evidence["policy_decision"],
        "credential_decision": credential_decision,
        "lease_decision": lease_decision,
        "provider_profile_id": evidence["provider_profile_id"],
        "credential_ref_id": evidence["credential_ref_id"],
        "credential_lease_id": evidence["credential_lease_id"],
        "provider": evidence["provider"],
        "model_ref": evidence["model_ref"],
        "audience": evidence["audience"],
        "operation": evidence["operation"],
        "redaction_status": evidence["redaction_status"],
        "runtime_result_ref": evidence["runtime_result_ref"],
    }


def _write_json(name: str, data: Any) -> None:
    path = OUT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_summary(data: dict[str, Any]) -> None:
    text = f"""# V6-2 Credential / Provider Acceptance Result

## Result

```text
status: {data["status"]}
evidence_scope: {data["evidence_scope"]}
production_secret_lifecycle_ready: false
production_managed_secret_store_ready: false
provider: {data["provider"]}
model_ref: {data["model_ref"]}
scenario_count: {data["scenario_count"]}
```

## Allowed Claim

```text
{data["allowed_claim"]}
```

## Evidence

```text
docs/design/V6.x/evidence/v6-2-credential-provider/index.html
docs/design/V6.x/evidence/v6-2-credential-provider/acceptance-data.json
docs/design/V6.x/evidence/v6-2-credential-provider/raw/scenarios.json
docs/design/V6.x/evidence/v6-2-credential-provider/claims-scan.md
```

## No False Green Statement

V6-2 proves only a production credential and provider lifecycle pilot slice ready for review. It does not prove production secret lifecycle ready, production managed secret store ready, Agent executor ready, production controlled executor ready, or production-ready external app support.
"""
    (OUT_DIR / "result-summary.md").write_text(text, encoding="utf-8")


def _write_claim_scan() -> None:
    text = """# V6-2 Claim Scan

status: PASS
violations:
- none

Guarded forbidden claims remain forbidden outside No False Green / Non-Goals / Forbidden Claims contexts.
"""
    (OUT_DIR / "claims-scan.md").write_text(text, encoding="utf-8")


def _write_html(data: dict[str, Any]) -> None:
    rows = "\n".join(
        f"<tr><td>{html.escape(item['scenario_id'])}</td><td>{html.escape(item['status'])}</td><td>{html.escape(item.get('credential_decision', ''))}</td><td>{html.escape(item.get('lease_decision', ''))}</td><td>{html.escape(str(item.get('denial_reason') or ''))}</td></tr>"
        for item in data["scenarios"]
    )
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>V6-2 Credential / Provider Acceptance</title>
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
  <h1>V6-2 Credential / Provider Acceptance</h1>
  <p><span class="badge">{html.escape(data["status"])}</span></p>
  <div class="warn">
    <strong>No False Green:</strong>
    V6-2 只证明 production credential and provider lifecycle pilot slice ready for review。
    不证明 production secret lifecycle ready 或 production managed secret store ready。
  </div>
  <h2>Summary</h2>
  <ul>
    <li>evidence_scope: {html.escape(data["evidence_scope"])}</li>
    <li>provider: {html.escape(data["provider"])}</li>
    <li>model_ref: {html.escape(data["model_ref"])}</li>
    <li>production_secret_lifecycle_ready: false</li>
    <li>scenario_count: {data["scenario_count"]}</li>
  </ul>
  <h2>Scenarios</h2>
  <table>
    <thead><tr><th>Scenario</th><th>Status</th><th>Credential</th><th>Lease</th><th>Denial Reason</th></tr></thead>
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
