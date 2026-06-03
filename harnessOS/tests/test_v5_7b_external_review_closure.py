from __future__ import annotations

import json
from pathlib import Path


EVIDENCE_DIR = Path("docs/design/V5.x/evidence/v5-7b-external-review")


def test_v5_7b_external_review_package_exists_and_is_parseable() -> None:
    required = [
        "index.html",
        "external-review-summary.md",
        "dependency-acceptance-decisions.md",
        "dependency-acceptance-decisions.json",
        "v5-7b-runtime-slice-review.md",
        "v5-7b-runtime-slice-review.json",
        "v5-8-entry-decision.json",
    ]

    for name in required:
        assert (EVIDENCE_DIR / name).exists(), name

    json.load((EVIDENCE_DIR / "dependency-acceptance-decisions.json").open(encoding="utf-8"))
    json.load((EVIDENCE_DIR / "v5-7b-runtime-slice-review.json").open(encoding="utf-8"))
    json.load((EVIDENCE_DIR / "v5-8-entry-decision.json").open(encoding="utf-8"))


def test_v5_7b_dependencies_are_accepted_only_for_v5_8_planning_entry() -> None:
    data = json.load((EVIDENCE_DIR / "dependency-acceptance-decisions.json").open(encoding="utf-8"))
    dependencies = {item["dependency_id"]: item for item in data["dependencies"]}

    assert data["current_decision"] == "ACCEPTED_FOR_V5_8_PLANNING_ENTRY"
    assert data["entry_result"]["v5_8_planning_may_start"] is True
    assert data["entry_result"]["v5_8_runtime_implementation_may_start"] is False
    for dependency_id in [
        "v5_1_tenant_boundary",
        "v5_2_credential_boundary",
        "v5_3_audit_export",
        "v5_4a_safety_gate",
        "v5_4c_devlocal_bridge",
        "v5_6_product_console_manual_confirmation",
    ]:
        assert dependencies[dependency_id]["status"] == "ACCEPTED_FOR_V5_8_PLANNING_ENTRY"
        assert "V5-8 planning" in dependencies[dependency_id]["accepted_scope"]
        assert dependencies[dependency_id]["not_accepted_as"]
    assert dependencies["v5_5_external_app_onboarding_boundary"]["status"] == "DEFERRED_EXTERNAL_APP_SOURCE_DISABLED"


def test_v5_7b_runtime_review_does_not_approve_routes_or_workers() -> None:
    data = json.load((EVIDENCE_DIR / "v5-7b-runtime-slice-review.json").open(encoding="utf-8"))

    assert data["status"] == "ACCEPTED_FOR_V5_8_PLANNING_ENTRY"
    assert data["verified_controls"]["no_production_executor_route"] is True
    assert data["verified_controls"]["no_production_runtime_worker"] is True
    assert data["verified_controls"]["source_agent_durable_mutation_denied"] is True
    assert data["entry_result"]["production_route_approved"] is False
    assert data["entry_result"]["production_worker_approved"] is False
    assert data["entry_result"]["v5_8_runtime_implementation_approved"] is False


def test_v5_8_entry_decision_is_planning_only() -> None:
    data = json.load((EVIDENCE_DIR / "v5-8-entry-decision.json").open(encoding="utf-8"))

    assert data["decision"] == "GO_FOR_V5_8_PLANNING_AND_PRE_IMPLEMENTATION_AUDIT"
    assert data["decision_scope"] == "planning_only"
    assert data["v5_8_runtime_implementation_allowed"] is False
    assert "v5_8_no_false_green_claim_scan" in data["required_before_v5_8_runtime_implementation"]
