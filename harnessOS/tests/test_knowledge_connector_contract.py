from __future__ import annotations

from apps.gateway.connectors import ConnectorRegistry
from core.services import CoreAppService
from core.stores import CoreSQLiteStore


def test_data_service_mcp_connector_declares_phase_e_capabilities(tmp_path):
    registry = ConnectorRegistry(core_service=CoreAppService(CoreSQLiteStore(tmp_path / "core.sqlite3")))
    connector = registry.get_connector("data_service_mcp")

    assert connector["domain"] == "knowledge"
    assert connector["kind"] == "mcp_stdio"
    assert connector["execution_mode"] in {"stub", "stdio"}
    assert connector["trust_level"] == "trusted_local"
    assert connector["app_scope"] == ["knowledge"]
    assert set(connector["capabilities"]["capabilities"]) >= {
        "knowledge.lifecycle",
        "knowledge.source",
        "knowledge.build",
        "knowledge.query",
        "knowledge.summarize",
        "knowledge.citation",
    }
    assert set(connector["capabilities"]["tools"]) >= {
        "knowledge_workspace_create",
        "knowledge_source_import",
        "knowledge_build_start",
        "knowledge_build_status",
        "knowledge_query_v2",
        "knowledge_ingest_v2",
    }


def test_data_service_mcp_missing_tool_is_explainable(tmp_path):
    registry = ConnectorRegistry(core_service=CoreAppService(CoreSQLiteStore(tmp_path / "core.sqlite3")))
    connector = registry.get_connector("data_service_mcp")

    assert "missing_tool" not in connector["capabilities"]["tools"]
    assert connector["health"] in {"contract_stub", "available", "configured"}
    assert connector["metadata"]["execution"] in {"deferred", "mcp_stdio"}
    assert isinstance(connector["metadata"]["health_details"], dict)
