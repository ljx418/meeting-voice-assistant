"""V4.0-S tenant isolation design matrix tests."""

from __future__ import annotations

import json
from pathlib import Path


CONTRACT_PATH = Path("docs/design/V4.0/v4_0_s_production_auth_tenant_boundary_design_contract.json")
REQUIRED_BOUNDARIES = {
    "workspace ownership",
    "project ownership",
    "resource ownership",
    "agent session ownership",
    "workflow instance ownership",
    "patch ownership",
    "handoff ownership",
    "evidence ownership",
    "audit ownership",
}
REQUIRED_DENIAL_RULES = {
    "cross-tenant denied",
    "cross-scope denied",
    "same-tenant wrong-workspace denied",
    "same-workspace wrong-resource denied",
    "same-instance wrong-agent-session denied",
    "same-instance wrong-proposal/handoff/evidence denied",
}


def test_tenant_isolation_matrix_covers_ownership_boundaries_and_denial_rules() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    matrix = contract["tenant_isolation_matrix"]
    assert {item["boundary"] for item in matrix} == REQUIRED_BOUNDARIES
    joined_rules = "\n".join(item["denial_rule"] for item in matrix)
    for rule in REQUIRED_DENIAL_RULES:
        assert rule in joined_rules
    for item in matrix:
        assert item["ownership_chain"].startswith("tenant_id -> app_id -> project_id -> workspace_id") or item[
            "ownership_chain"
        ].startswith("tenant_id -> app_id -> project_id")
        assert item["current_status"] in {"design_only", "current_dev_local_scope_guard_plus_design_gap"}
