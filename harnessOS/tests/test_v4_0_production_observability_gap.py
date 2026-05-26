"""V4.0-R observability and audit preflight tests."""

from __future__ import annotations

import json
from pathlib import Path


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_r_production_readiness_preflight_contract.json")
COMPLETION_PATH = Path("docs/design/V4.0/v4_0_r_production_readiness_preflight_completion_note.md")


def test_observability_and_audit_gaps_are_explicit() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert set(contract["observability_and_audit_gaps"]) >= {
        "trace retention gap",
        "operation evidence retention gap",
        "governance review export gap",
        "security audit log gap",
        "correlation_id coverage",
        "idempotency_key coverage",
        "actor_id coverage",
        "request_id coverage",
        "error taxonomy",
        "metrics gap",
        "alerting gap",
        "incident timeline gap",
        "SLO / SLA gap",
    }
    gaps = {gap["category"]: gap for gap in contract["production_gaps"]}
    assert gaps["audit_retention"]["status"] == "open_gap"
    assert gaps["observability_metrics_alerting"]["blocking_for_production"] is True


def test_operation_evidence_is_documented_as_dev_local_not_production_audit_export() -> None:
    completion = COMPLETION_PATH.read_text(encoding="utf-8")
    assert "V4.0-M operation evidence remains dev/local baseline" in completion
    assert "R adds no production auth, SSO, tenant, token lifecycle, quota, production onboarding, or audit export routes" in completion
