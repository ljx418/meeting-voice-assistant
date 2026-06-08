from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from core.auth.tenant_boundary import IdentityContext
from core.governance.v9_7_production_governance import (
    V97GovernanceError,
    build_v9_7_governance_fixture,
    create_audit_export_package,
    credential_lease_decision,
    evidence_hardening_report,
    reject_audit_export_mutation,
    tenant_isolation_decision,
)


OUT_DIR = Path("docs/design/V9.x/evidence/v9-7-production-governance")


def make_context() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v9_7",
        workspace_id="workspace_v9_7",
        project_id="project_v9_7",
        app_id="app_v9_7",
        actor_type="human_user",
        actor_id="user_v9_7_reviewer",
        user_id="user_v9_7_reviewer",
        service_account_id="service_account_v9_7",
        request_id="request_v9_7",
        correlation_id="correlation_v9_7",
    )


def test_v9_7_tenant_isolation_wrong_tenant_denied() -> None:
    decision = tenant_isolation_decision(make_context(), requested_tenant_id="tenant_other", requested_workspace_id="workspace_v9_7", requested_app_id="app_v9_7")

    assert decision.policy_decision == "deny"
    assert decision.denial_reason == "tenant_mismatch"
    assert decision.audit_ref.startswith("audit://v9-7/tenant-isolation/")


def test_v9_7_credential_lease_wrong_operation_expired_revoked_denied() -> None:
    ctx = make_context()
    wrong_operation = credential_lease_decision(
        ctx,
        credential_lease_ref="credential-lease://v9-7/redacted",
        service_account_id="service_account_v9_7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="production.deploy",
        expires_at="2999-01-01T00:00:00+00:00",
    )
    expired = credential_lease_decision(
        ctx,
        credential_lease_ref="credential-lease://v9-7/redacted",
        service_account_id="service_account_v9_7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="terminal.audit.review",
        expires_at="2000-01-01T00:00:00+00:00",
    )
    revoked = credential_lease_decision(
        ctx,
        credential_lease_ref="credential-lease://v9-7/redacted",
        service_account_id="service_account_v9_7",
        audience="provider:minimax",
        operation="terminal.audit.review",
        requested_audience="provider:minimax",
        requested_operation="terminal.audit.review",
        expires_at="2999-01-01T00:00:00+00:00",
        revoked=True,
    )

    assert wrong_operation.denial_reason == "operation_mismatch"
    assert expired.denial_reason == "lease_expired"
    assert revoked.denial_reason == "lease_revoked"


def test_v9_7_raw_secret_access_denied() -> None:
    with pytest.raises(V97GovernanceError) as excinfo:
        credential_lease_decision(
            make_context(),
            credential_lease_ref="credential-lease://v9-7/raw_secret",
            service_account_id="service_account_v9_7",
            audience="provider:minimax",
            operation="terminal.audit.review",
            requested_audience="provider:minimax",
            requested_operation="terminal.audit.review",
            expires_at="2999-01-01T00:00:00+00:00",
        )

    assert excinfo.value.reason == "raw_sensitive_data"


def test_v9_7_audit_export_append_only_and_mutation_denied() -> None:
    export = create_audit_export_package(make_context(), requested_by="user_v9_7_reviewer", included_refs=["audit://v9-7/source"])
    denial = reject_audit_export_mutation(export, attempted_action="overwrite")

    assert export.append_only is True
    assert export.immutable is True
    assert export.readonly is True
    assert set(export.allowed_actions) == {"view", "export", "open_evidence"}
    assert denial["policy_decision"] == "deny"


def test_v9_7_incident_timeline_records_required_events() -> None:
    fixture = build_v9_7_governance_fixture(make_context())
    event_types = {event["event_type"] for event in fixture["incident_timeline"]}

    assert {"policy_denied", "credential_denied", "timeout", "worker_lost"} <= event_types
    assert all(event["readonly"] is True for event in fixture["incident_timeline"])


def test_v9_7_evidence_hardening_scan_pass_and_rejects_bad_payload() -> None:
    report = evidence_hardening_report(make_context(), scanned_refs=["audit://v9-7/source"], payloads=[{"safe_ref": "evidence://v9-7/safe"}])
    bad = evidence_hardening_report(make_context(), scanned_refs=["audit://v9-7/bad"], payloads=[{"claim": "production automation ready"}])

    assert report.policy_decision == "allow"
    assert report.redaction_status == "PASS"
    assert report.claim_scan_status == "PASS"
    assert bad.policy_decision == "deny"
    assert bad.claim_scan_status == "FAIL"


def test_v9_7_browser_automation_blocked_without_separate_prd() -> None:
    fixture = build_v9_7_governance_fixture(make_context())

    assert fixture["browser_automation_policy"]["browser_account_automation_allowed"] is False
    assert fixture["browser_automation_policy"]["separate_prd_required"] is True
    assert fixture["browser_automation_policy"]["policy_decision"] == "deny_without_separate_prd"


def test_v9_7_production_automation_ready_claim_denied() -> None:
    fixture = build_v9_7_governance_fixture(make_context())
    acceptance = json.loads(json.dumps(fixture, ensure_ascii=False))

    assert acceptance["terminal_automation_policy"]["production_terminal_automation_ready"] is False
    assert acceptance["browser_automation_policy"]["browser_account_automation_allowed"] is False


def test_v9_7_evidence_script_generates_package() -> None:
    subprocess.run(["./.venv/bin/python", "-m", "tools.v9.generate_v9_7_production_governance_evidence"], check=True)

    required = [
        "index.html",
        "acceptance-data.json",
        "result-summary.md",
        "governance-fixture.json",
        "tenant-isolation-decisions.json",
        "credential-lease-decisions.json",
        "service-account-binding-decisions.json",
        "audit-export-package.json",
        "incident-timeline.json",
        "evidence-hardening-report.json",
        "terminal-automation-policy.json",
        "browser-automation-policy.json",
    ]
    missing = [name for name in required if not (OUT_DIR / name).exists()]
    assert missing == []

    data = json.loads((OUT_DIR / "acceptance-data.json").read_text(encoding="utf-8"))
    assert data["stage_id"] == "V9-7"
    assert data["status"] == "PASS"
    assert data["production_automation_ready"] is False
    assert data["production_terminal_automation_ready"] is False
    assert data["production_browser_automation_ready"] is False
