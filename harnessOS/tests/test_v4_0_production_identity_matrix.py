"""V4.0-S production identity matrix contract tests."""

from __future__ import annotations

import json
from pathlib import Path


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_s_production_auth_tenant_boundary_design_contract.json")
REQUIRED_FIELDS = {
    "tenant_id",
    "app_id",
    "project_id",
    "workspace_id",
    "user_id",
    "actor_type",
    "actor_id",
    "service_account_id",
    "agent_id",
    "session_id",
}
REQUIRED_METADATA = {
    "source_of_truth",
    "trusted_source",
    "client_supplied_allowed",
    "server_bound_required",
    "token_claim_allowed",
    "audit_required",
    "current_status",
    "production_gap",
    "risk_level",
    "blocking_for_production",
}


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_identity_matrix_covers_required_fields_and_metadata() -> None:
    identity_fields = {item["field"]: item for item in _contract()["identity_fields"]}
    assert set(identity_fields) == REQUIRED_FIELDS
    for field, item in identity_fields.items():
        assert REQUIRED_METADATA <= set(item), field
        assert item["server_bound_required"] is True
        assert item["audit_required"] is True
        assert item["blocking_for_production"] is True
        assert item["risk_level"] in {"critical", "high", "medium", "low"}


def test_identity_matrix_separates_dev_local_scope_from_production_gaps() -> None:
    identity_fields = {item["field"]: item for item in _contract()["identity_fields"]}
    for field in ("app_id", "project_id", "workspace_id"):
        assert identity_fields[field]["current_status"] == "current_dev_local_scope_guard"
        assert identity_fields[field]["blocking_for_production"] is True
        assert "Production" in identity_fields[field]["production_gap"]
    for field in ("tenant_id", "user_id", "service_account_id", "actor_type", "actor_id"):
        assert identity_fields[field]["current_status"] == "production_gap"
        assert identity_fields[field]["client_supplied_allowed"] is False
        assert identity_fields[field]["blocking_for_production"] is True
    assert identity_fields["agent_id"]["current_status"] == "dev_local_agenttalk_identity_only"
    assert "not executor identity" in identity_fields["agent_id"]["production_gap"]
