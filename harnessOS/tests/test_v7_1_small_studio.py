from __future__ import annotations

import json
import subprocess
from pathlib import Path

from core.auth.tenant_boundary import IdentityContext
from core.product_console.v7_1_small_studio import build_small_studio_projection, render_small_studio_html, scan_small_studio_html


OUT_DIR = Path("docs/design/V7.x/evidence/v7-1-small-studio")


def make_context() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v7_1",
        workspace_id="workspace_v7_1",
        project_id="project_v7_1",
        app_id="app_v7_1",
        actor_type="human_user",
        actor_id="user_v7_1_admin",
        user_id="user_v7_1_admin",
        service_account_id="service_account_v7_1",
        request_id="request_v7_1",
        correlation_id="correlation_v7_1",
    )


def make_projection():
    return build_small_studio_projection(
        make_context(),
        source_refs={"v6_final_acceptance": "docs/design/V6.x/evidence/v6-9-final-acceptance/final-acceptance-data.json"},
        v6_final_data={"production_ready": False},
    )


def test_studio_context_contains_tenant_workspace_project_app_refs() -> None:
    projection = make_projection()

    assert projection.studio_context["tenant_id"] == "tenant_v7_1"
    assert projection.studio_context["workspace_id"] == "workspace_v7_1"
    assert projection.studio_context["project_ids"] == ["project_v7_1"]
    assert projection.studio_context["app_ids"] == ["app_v7_1"]
    assert projection.studio_context["runtime_truth_boundary"] == "product_aggregation_only_no_runtime_truth_write"


def test_provider_profile_projection_redacts_secret() -> None:
    profile = make_projection().provider_profiles[0]
    serialized = json.dumps(profile, ensure_ascii=False)

    assert profile["redaction_status"] == "redacted_refs_only"
    assert "api_key" not in serialized
    assert "Bearer " not in serialized
    assert "sk-" not in serialized


def test_credential_ref_projection_no_raw_secret() -> None:
    credential_ref = make_projection().credential_refs[0]
    serialized = json.dumps(credential_ref, ensure_ascii=False)

    assert credential_ref["redaction_status"] == "no_raw_credential_material"
    assert "raw_secret" not in serialized
    assert "api_key" not in serialized
    assert "Bearer " not in serialized


def test_role_binding_projection_auditable() -> None:
    bindings = make_projection().role_bindings

    assert {binding["role"] for binding in bindings} == {"studio_admin", "workflow_operator", "reviewer"}
    assert all(binding["audit_ref"].startswith("audit://v7-1/") for binding in bindings)


def test_quota_denial_explainable() -> None:
    decisions = make_projection().quota_decisions
    denial = next(item for item in decisions if item["policy_decision"] == "deny")

    assert denial["remaining"] == 0
    assert denial["limit_ref"] == "quota-policy://v7-1/monthly-provider-calls"
    assert denial["audit_ref"] == "audit://v7-1/quota-denial"


def test_cross_workspace_access_denied() -> None:
    denial = make_projection().cross_workspace_denial

    assert denial["policy_decision"] == "deny"
    assert denial["denial_reason"] == "workspace_mismatch"
    assert denial["target_workspace_id"] == "other-workspace"


def test_studio_control_plane_does_not_construct_runtime_truth() -> None:
    projection = make_projection()
    serialized = json.dumps(projection.to_dict(), ensure_ascii=False)

    assert projection.global_assertions["does_not_write_runtime_truth"] is True
    for forbidden in ("WorkflowDraft", "WorkflowVersion", "WorkflowInstance", "StationRun", "raw_artifact_content"):
        assert forbidden not in serialized


def test_small_studio_html_redaction_and_claim_scan_passes() -> None:
    html = render_small_studio_html(make_projection())
    scan = scan_small_studio_html(html)

    assert scan["status"] == "PASS"
    assert scan["sensitive_hits"] == []
    assert scan["forbidden_claim_hits"] == []
    assert scan["runtime_truth_hits"] == []


def test_v7_1_evidence_script_generates_package() -> None:
    subprocess.run(["./.venv/bin/python", "scripts/v7_1_small_studio_evidence.py"], check=True)

    required = [
        "index.html",
        "acceptance-data.json",
        "result-summary.md",
        "claims-scan.md",
        "redaction-scan.md",
        "raw/studio-context.json",
        "raw/studio-inventory.json",
        "raw/workspace-inventory.json",
        "raw/project-inventory.json",
        "raw/app-inventory.json",
        "raw/provider-profiles.json",
        "raw/credential-refs.json",
        "raw/role-bindings.json",
        "raw/quota-decisions.json",
        "raw/audit-source-refs.json",
        "raw/cross-workspace-denial.json",
    ]
    missing = [name for name in required if not (OUT_DIR / name).exists()]
    assert missing == []

    data = json.loads((OUT_DIR / "acceptance-data.json").read_text(encoding="utf-8"))
    assert data["stage_id"] == "V7-1"
    assert data["status"] == "PASS"
    assert data["evidence_scope"] == "repo_backed_fixture"
    assert data["redaction_status"] == "PASS"
    assert data["claim_violations"] == []
