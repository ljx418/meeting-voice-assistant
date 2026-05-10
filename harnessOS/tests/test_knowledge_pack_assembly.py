from __future__ import annotations

from apps.gateway.connectors import DATA_SERVICE_CAPABILITIES, DATA_SERVICE_TOOLS
from core.packs import build_default_pack_registry


def test_knowledge_pack_assembly_exposes_phase_e_contracts():
    registry = build_default_pack_registry()
    pack = registry.get_pack("knowledge")
    assert pack is not None

    assert pack.workflows == ("knowledge.workflow",)
    assert pack.skills == (
        "knowledge-ingest",
        "knowledge-search",
        "knowledge-summarize",
        "citation",
    )
    assert pack.policy_bundles == ("knowledge.default",)
    assert pack.connectors == ("local.knowledge", "data_service_mcp")
    assert pack.artifact_kinds == ("source_reference", "note", "brief", "citation_bundle")
    assert pack.artifact_schemas["note"]["parents"] == ["source_reference"]
    assert pack.artifact_schemas["brief"]["parents"] == ["source_reference"]
    assert pack.artifact_schemas["citation_bundle"]["parents"] == ["brief"]


def test_knowledge_pack_get_assembles_with_required_data_service_capabilities():
    registry = build_default_pack_registry()
    assembly = registry.evaluate_assembly(
        "knowledge",
        supported_workflows={"knowledge.workflow"},
        available_connectors={"local.knowledge", "data_service_mcp"},
        available_connector_capabilities={
            "data_service_mcp": {
                "capabilities": set(DATA_SERVICE_CAPABILITIES),
                "tools": set(DATA_SERVICE_TOOLS),
                "resources": {
                    "data_service://summary",
                    "data_service://layout",
                    "data_service://build-status",
                    "data_service://quality-report",
                },
            }
        },
        available_policy_bundles={"knowledge.default"},
    )

    assert assembly.status == "assembled"
    assert assembly.missing_dependencies == ()
    assert assembly.disabled_reason == ""
