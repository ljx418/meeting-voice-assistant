"""V4.0-N canvas editing readiness source contract tests."""

from __future__ import annotations

from apps.api.routers import bff


REQUIRED_CATALOG_FIELDS = {
    "catalog_id",
    "catalog_version",
    "node_template_id",
    "station_kind",
    "schema_version",
    "allowed_skill_refs",
    "allowed_connector_refs",
    "allowed_artifact_kinds",
    "allowed_quality_rules",
    "allowed_approval_policies",
}


def test_node_catalog_contracts_have_required_controlled_fields() -> None:
    assert bff.NODE_CATALOG_CONTRACTS
    for node_template_id, contract in bff.NODE_CATALOG_CONTRACTS.items():
        assert REQUIRED_CATALOG_FIELDS <= set(contract)
        assert contract["node_template_id"] == node_template_id
        assert isinstance(contract["allowed_skill_refs"], list)
        assert isinstance(contract["allowed_connector_refs"], list)


def test_canvas_intents_remain_proposal_only_operations() -> None:
    assert bff.CANVAS_PATCH_OPERATIONS["node_add"] == {"add_station"}
    assert bff.CANVAS_PATCH_OPERATIONS["edge_add"] == {"update_edge"}
    assert "add_edge" not in bff.CANVAS_PATCH_OPERATIONS["edge_add"]
    assert {"apply_patch", "publish_version"} <= bff.FORBIDDEN_AGENT_ACTION_INTENTS


def test_inspector_operations_use_field_allowlists() -> None:
    assert bff.INSPECTOR_OPERATION_FIELDS["update_station_prompt"] == {"station_id", "prompt_ref", "prompt_patch"}
    assert "raw_trace_payload" not in set().union(*bff.INSPECTOR_OPERATION_FIELDS.values())
    assert "position" not in set().union(*bff.INSPECTOR_OPERATION_FIELDS.values())
