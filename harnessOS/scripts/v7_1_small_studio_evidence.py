from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.auth.tenant_boundary import IdentityContext
from core.product_console.v7_1_small_studio import build_small_studio_projection, read_json, render_small_studio_html, scan_small_studio_html


OUT_DIR = Path("docs/design/V7.x/evidence/v7-1-small-studio")
V6_FINAL = Path("docs/design/V6.x/evidence/v6-9-final-acceptance/final-acceptance-data.json")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "raw").mkdir(parents=True, exist_ok=True)
    v6_final_data = read_json(V6_FINAL)
    context = IdentityContext(
        tenant_id="tenant_v7_1",
        workspace_id="workspace_v7_1",
        project_id="project_v7_1",
        app_id="app_v7_1",
        actor_type="human_user",
        actor_id="user_v7_1_admin",
        user_id="user_v7_1_admin",
        service_account_id="service_account_v7_1",
        request_id="request_v7_1_evidence",
        correlation_id="correlation_v7_1_evidence",
    )
    source_refs = {
        "v6_final_acceptance": str(V6_FINAL),
        "v6_2_credential_provider": "docs/design/V6.x/evidence/v6-2-credential-provider/acceptance-data.json",
        "v6_3_observability_audit": "docs/design/V6.x/evidence/v6-3-observability-audit/acceptance-data.json",
        "v6_6_external_app_onboarding": "docs/design/V6.x/evidence/v6-6-external-app-onboarding/acceptance-data.json",
    }
    projection = build_small_studio_projection(context, source_refs=source_refs, v6_final_data=v6_final_data)
    html = render_small_studio_html(projection)
    scan = scan_small_studio_html(html)
    data = {
        "stage_id": "V7-1",
        "status": "PASS" if scan["status"] == "PASS" and all(projection.global_assertions.values()) else "FAIL",
        "allowed_claim": "V7-1 complete: small studio production pilot control plane ready for review.",
        "evidence_scope": "repo_backed_fixture",
        "runtime_backed": False,
        "provider_backed": False,
        "real_data_used": True,
        "scenario_count": 11,
        "scenarios": [
            _scenario("studio_context_contains_tenant_workspace_project_app_refs", bool(projection.studio_context["project_ids"]) and bool(projection.studio_context["app_ids"])),
            _scenario("studio_inventory_contains_counts", projection.studio_inventory["workspace_count"] == 1),
            _scenario("workspace_project_app_inventory_refs_exist", projection.app_inventory["app_id"] == context.app_id),
            _scenario("provider_profile_projection_redacts_secret", projection.provider_profiles[0]["redaction_status"] == "redacted_refs_only"),
            _scenario("credential_ref_projection_no_raw_secret", projection.credential_refs[0]["redaction_status"] == "no_raw_secret_material"),
            _scenario("role_binding_projection_auditable", all(item["audit_ref"] for item in projection.role_bindings)),
            _scenario("quota_denial_explainable", any(item["policy_decision"] == "deny" for item in projection.quota_decisions)),
            _scenario("cross_workspace_access_denied", projection.cross_workspace_denial["policy_decision"] == "deny"),
            _scenario("studio_control_plane_does_not_construct_runtime_truth", projection.global_assertions["does_not_write_runtime_truth"]),
            _scenario("no_false_green_claim_scan_passes", not scan["forbidden_claim_hits"]),
            _scenario("redaction_scan_passes", not scan["sensitive_hits"]),
        ],
        "claim_violations": scan["forbidden_claim_hits"],
        "redaction_status": "PASS" if not scan["sensitive_hits"] else "FAIL",
        "runtime_truth_hits": scan["runtime_truth_hits"],
        "source_refs": source_refs,
        "next_stage_audit": "V7-2 pre-implementation review must close before Mission TUI coding.",
        "proceed_decision": "proceed_to_v7_2_pre_implementation_review",
    }
    _write_json("acceptance-data.json", data)
    _write_json("raw/studio-context.json", projection.studio_context)
    _write_json("raw/studio-inventory.json", projection.studio_inventory)
    _write_json("raw/workspace-inventory.json", projection.workspace_inventory)
    _write_json("raw/project-inventory.json", projection.project_inventory)
    _write_json("raw/app-inventory.json", projection.app_inventory)
    _write_json("raw/provider-profiles.json", projection.provider_profiles)
    _write_json("raw/credential-refs.json", projection.credential_refs)
    _write_json("raw/role-bindings.json", projection.role_bindings)
    _write_json("raw/quota-decisions.json", projection.quota_decisions)
    _write_json("raw/audit-source-refs.json", projection.audit_source_refs)
    _write_json("raw/cross-workspace-denial.json", projection.cross_workspace_denial)
    _write_claim_scan(scan)
    _write_redaction_scan(scan)
    _write_summary(data)
    (OUT_DIR / "index.html").write_text(html, encoding="utf-8")


def _scenario(scenario_id: str, passed: bool) -> dict[str, str]:
    return {"scenario_id": scenario_id, "status": "PASS" if passed else "FAIL", "evidence_scope": "repo_backed_fixture"}


def _write_json(name: str, data: Any) -> None:
    path = OUT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_claim_scan(scan: dict[str, Any]) -> None:
    lines = ["# V7-1 Claims Scan", "", f"status: {'PASS' if not scan['forbidden_claim_hits'] else 'FAIL'}", f"violations: {len(scan['forbidden_claim_hits'])}", ""]
    for hit in scan["forbidden_claim_hits"]:
        lines.append(f"- {hit}")
    (OUT_DIR / "claims-scan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_redaction_scan(scan: dict[str, Any]) -> None:
    lines = ["# V7-1 Redaction Scan", "", f"status: {'PASS' if not scan['sensitive_hits'] else 'FAIL'}", f"sensitive_hits: {scan['sensitive_hits']}", f"runtime_truth_hits: {scan['runtime_truth_hits']}"]
    (OUT_DIR / "redaction-scan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summary(data: dict[str, Any]) -> None:
    lines = [
        "# V7-1 Small Studio Acceptance Result",
        "",
        f"status: {data['status']}",
        f"allowed_claim: {data['allowed_claim']}",
        f"evidence_scope: {data['evidence_scope']}",
        f"scenario_count: {data['scenario_count']}",
        f"redaction_status: {data['redaction_status']}",
        "",
        "## No False Green Statement",
        "",
        "V7-1 proves only a repo-backed Small Studio product aggregation pilot slice ready for review. It does not prove full production GA, enterprise auth ready, production-ready external app support, complete Workflow Studio, Agent executor, or production controlled executor.",
        "",
        "## Scenario Results",
        "",
    ]
    for scenario in data["scenarios"]:
        lines.append(f"- {scenario['scenario_id']}: {scenario['status']}")
    (OUT_DIR / "result-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
