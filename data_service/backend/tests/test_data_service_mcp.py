import json
import asyncio
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
V15_DOCS_ROOT = REPO_ROOT / "docs" / "V1.5"


def _assert_no_public_path_keys(payload, *, path=()):
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in {"debug_path", "debug_paths"}:
                continue
            assert key not in {
                "path",
                "paths",
                "workspace",
                "workspace_path",
                "original_path",
                "distill_path",
                "rules_path",
                "feedback_path",
                "units_path",
                "db_path",
                "request_path",
                "root",
                "artifacts",
            }, f"public path key leaked at {'.'.join((*path, key))}"
            _assert_no_public_path_keys(value, path=(*path, key))
    elif isinstance(payload, list):
        for index, item in enumerate(payload):
            _assert_no_public_path_keys(item, path=(*path, str(index)))


def _cli_command_choices():
    from data_service.__main__ import _build_parser

    parser = _build_parser()
    return next(action for action in parser._actions if getattr(action, "choices", None)).choices


def _cli_quality_subcommands():
    quality_parser = _cli_command_choices()["quality"]
    quality_action = next(action for action in quality_parser._actions if getattr(action, "choices", None))
    return set(quality_action.choices)


@pytest.mark.asyncio
async def test_data_service_mcp_lists_quality_tools():
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    tools = await mcp_stdio.list_tools()

    assert {tool.name for tool in tools} >= {
        "knowledge_ingest",
        "knowledge_query",
        "knowledge_distill_preview",
        "knowledge_source_trace",
        "knowledge_quality_summary",
        "knowledge_correction_plan",
        "knowledge_quality_feedback",
        "knowledge_correction_rules",
        "knowledge_review_correction_rule",
        "knowledge_ingest_v2",
        "knowledge_query_v2",
        "knowledge_quality_summary_v2",
        "knowledge_correction_plan_v2",
        "knowledge_quality_feedback_v2",
        "knowledge_correction_rules_v2",
        "knowledge_review_correction_rule_v2",
        "knowledge_workspace_create",
        "knowledge_workspace_list",
        "knowledge_workspace_describe",
        "knowledge_workspace_archive",
        "knowledge_source_import",
        "knowledge_source_list",
        "knowledge_source_remove",
        "knowledge_build_start",
        "knowledge_build_status",
        "knowledge_build_cancel",
        "knowledge_session_create",
        "knowledge_session_get",
        "knowledge_session_list",
        "knowledge_session_close",
        "knowledge_session_delete",
        "knowledge_session_ingest",
        "knowledge_session_build_start",
        "knowledge_session_build_status",
        "knowledge_session_build_cancel",
        "knowledge_graph_snapshot",
        "knowledge_graph_neighbors",
        "knowledge_community_summary",
        "knowledge_session_query",
        "knowledge_actor_summary",
        "knowledge_codebase_import",
        "knowledge_codebase_list",
        "knowledge_codebase_snapshot",
        "knowledge_codebase_describe",
        "knowledge_codebase_archive",
        "knowledge_project_inventory",
        "knowledge_code_symbol_search",
        "knowledge_public_surface_trace",
        "knowledge_project_overview",
        "knowledge_agent_context_pack",
        "knowledge_devwiki_build",
        "knowledge_devwiki_read",
        "knowledge_code_graph_build",
        "knowledge_code_graph_snapshot",
        "knowledge_code_graph_neighbors",
        "knowledge_code_graph_mermaid",
        "knowledge_code_quality_feedback",
        "knowledge_code_quality_summary",
        "knowledge_code_quality_rules_build",
        "knowledge_code_quality_rule_review",
        "knowledge_code_quality_plan",
    }


@pytest.mark.asyncio
async def test_data_service_mcp_tool_registry_contract():
    pytest.importorskip("mcp")
    from data_service.mcp_tool_registry import V2_TOOL_MAP, all_tool_specs

    specs = all_tool_specs()
    names = [spec["name"] for spec in specs]

    assert len(names) >= 103
    assert len(names) == len(set(names))
    assert set(V2_TOOL_MAP) <= set(names)
    assert set(V2_TOOL_MAP.values()) <= set(names)
    assert {
        "knowledge_workspace_create",
        "knowledge_source_import",
        "knowledge_build_start",
        "knowledge_distill_preview",
        "knowledge_source_trace",
        "knowledge_session_build_start",
        "knowledge_query_v2",
        "knowledge_codebase_import",
        "knowledge_codebase_list",
        "knowledge_codebase_snapshot",
        "knowledge_codebase_describe",
        "knowledge_codebase_archive",
        "knowledge_project_inventory",
        "knowledge_code_symbol_search",
        "knowledge_project_overview",
        "knowledge_agent_context_pack",
        "knowledge_code_graph_snapshot",
        "knowledge_code_graph_neighbors",
        "knowledge_code_quality_summary",
        "knowledge_architecture_model_build",
        "knowledge_architecture_model_read",
        "knowledge_architecture_alignment",
        "knowledge_architecture_findings",
        "knowledge_code_architecture_build",
        "knowledge_code_architecture_roles",
        "knowledge_code_architecture_patterns",
        "knowledge_code_architecture_view",
        "knowledge_code_architecture_scale_build",
        "knowledge_code_architecture_scale_profile",
        "knowledge_code_architecture_scale_readback",
        "knowledge_code_architecture_inventory_build",
        "knowledge_code_architecture_language_facts",
        "knowledge_code_architecture_language_providers_build",
        "knowledge_code_architecture_language_providers",
        "knowledge_code_architecture_workflow_runtime_build",
        "knowledge_code_architecture_workflow_runtime",
        "knowledge_code_architecture_relationship_chains_v3_build",
        "knowledge_code_architecture_relationship_chains_v3",
        "knowledge_code_architecture_document_semantics_v3_build",
        "knowledge_code_architecture_document_semantics_v3",
        "knowledge_code_architecture_context_pack_optimized",
        "knowledge_code_architecture_context_pack_optimized_read",
        "knowledge_code_architecture_profile_regression_build",
        "knowledge_code_architecture_profile_regression",
        "knowledge_code_architecture_config_inventory",
        "knowledge_code_architecture_deployment_inventory",
        "knowledge_code_architecture_schema_inventory",
        "knowledge_code_architecture_taxonomy_build",
        "knowledge_code_architecture_taxonomy",
        "knowledge_code_architecture_review_queue_build",
        "knowledge_code_architecture_review_queue",
        "knowledge_code_architecture_large_project_views_build",
        "knowledge_code_architecture_large_project_view",
        "knowledge_code_architecture_docs_build",
        "knowledge_code_architecture_docs_list",
        "knowledge_code_architecture_doc_claims_build",
        "knowledge_code_architecture_doc_claims",
        "knowledge_code_architecture_doc_quality_build",
        "knowledge_code_architecture_doc_quality",
        "knowledge_code_architecture_doc_code_alignment_build",
        "knowledge_code_architecture_doc_code_alignment",
        "knowledge_code_architecture_reconstructed_build",
        "knowledge_code_architecture_reconstructed",
        "knowledge_code_architecture_doc_view",
        "knowledge_code_architecture_views_build",
        "knowledge_code_architecture_views",
        "knowledge_code_architecture_view_v2_8",
        "knowledge_code_architecture_graph_summary_build",
        "knowledge_code_architecture_graph_summary",
        "knowledge_code_architecture_graph_view",
        "knowledge_code_architecture_code_fact_chains_build",
        "knowledge_code_architecture_code_fact_chains",
    } <= set(names)


def test_console_mcp_contract_snapshot_matches_registry():
    from data_service.mcp_resources import RESOURCE_SPECS, canonical_resource_uri
    from data_service.mcp_tool_registry import all_tool_specs

    contract_source = (REPO_ROOT / "frontend" / "src" / "data" / "mcpContract.ts").read_text(encoding="utf-8")
    console_tool_names = re.findall(r"name: '(knowledge_[^']+)'", contract_source)
    console_resource_uris = re.findall(r"uri: '([^']+)'", contract_source)

    registry_tool_names = [spec["name"] for spec in all_tool_specs()]
    canonical_resource_uris = {spec["uri"] for spec in RESOURCE_SPECS}

    assert console_tool_names == registry_tool_names
    assert canonical_resource_uris <= {canonical_resource_uri(uri) for uri in console_resource_uris}


def test_phaseg1_interface_matrix_documents_current_entrypoints():
    from app.api.v1.data_service import router
    from data_service.__main__ import _build_parser

    contract_source = (REPO_ROOT / "frontend" / "src" / "data" / "mcpContract.ts").read_text(encoding="utf-8")
    report_source = (V15_DOCS_ROOT / "PHASE-G1-INTERFACE-CONVERGENCE-BASELINE-REPORT-2026-05-11.md").read_text(
        encoding="utf-8"
    )
    matrix_source = (V15_DOCS_ROOT / "interface-convergence-matrix.md").read_text(encoding="utf-8")

    for capability in ["workspace", "source", "build", "query", "distill", "graph", "trace", "quality", "session"]:
        assert f"capability: '{capability}'" in contract_source
        assert capability in matrix_source

    route_paths = {
        getattr(route, "path", "").removeprefix("/knowledge")
        for route in router.routes
    }
    assert {
        "/workspaces/create",
        "/sources/import",
        "/build/start",
        "/query",
        "/graph",
        "/distill",
        "/source/trace",
        "/quality/feedback",
    } <= route_paths

    parser = _build_parser()
    subparser_action = next(action for action in parser._actions if getattr(action, "choices", None))
    assert {"ingest", "summary", "distill", "boundary", "graphrag-execute", "query"} <= set(subparser_action.choices)

    assert "MCP 是默认主入口" in report_source
    assert "不新增 MCP tool、HTTP route 或 CLI command" in report_source
    assert "/api/v1/knowledge/*" in matrix_source


@pytest.mark.asyncio
async def test_phaseg2_query_contract_shared_by_mcp_http_and_cli(tmp_path, monkeypatch, capsys):
    pytest.importorskip("mcp")
    import sys

    from app.main import app
    from data_service import mcp_stdio
    from data_service.__main__ import main as cli_main
    from data_service.models import QueryMode
    from data_service.service import DataService
    from fastapi.testclient import TestClient

    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    workspace = tmp_path / "workspace"
    doc = tmp_path / "phaseg2-query.md"
    doc.write_text("# PhaseG2 Query\n\nPhaseG2 aligns MCP, HTTP, and CLI query contracts.\n", encoding="utf-8")

    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)

    http_payload = TestClient(app).post(
        "/api/v1/knowledge/query",
        json={
            "workspace": str(workspace),
            "query": "PhaseG2",
            "mode": QueryMode.HYBRID.value,
            "top_k": 5,
        },
    ).json()
    mcp_payload = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_query",
                {
                    "workspace": str(workspace),
                    "query": "PhaseG2",
                    "mode": QueryMode.HYBRID.value,
                    "top_k": 5,
                },
            )
        )[0].text
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "data_service",
            "query",
            "PhaseG2",
            "--workspace",
            str(workspace),
            "--mode",
            QueryMode.HYBRID.value,
            "--top-k",
            "5",
        ],
    )
    assert cli_main() == 0
    cli_payload = json.loads(capsys.readouterr().out)

    expected_keys = {"mode", "query", "answer", "hits", "engine_payloads"}
    assert set(http_payload) == expected_keys
    assert set(mcp_payload) == expected_keys
    assert set(cli_payload) == expected_keys
    for payload in [mcp_payload, cli_payload]:
        assert payload["mode"] == http_payload["mode"] == QueryMode.HYBRID.value
        assert payload["query"] == http_payload["query"] == "PhaseG2"
        assert payload["answer"] == http_payload["answer"]
        assert [hit["title"] for hit in payload["hits"]] == [hit["title"] for hit in http_payload["hits"]]
        assert set(payload["engine_payloads"]) == {"llmwiki", "graphrag"}


@pytest.mark.asyncio
async def test_phaseg28_distill_preview_mcp_reuses_shared_contract(tmp_path, monkeypatch):
    pytest.importorskip("mcp")
    from app.main import app
    from data_service import mcp_stdio
    from data_service.distill_contract import run_distill_contract
    from data_service.mcp_tool_registry import all_tool_specs
    from data_service.service import DataService
    from fastapi.testclient import TestClient

    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    workspace = tmp_path / "workspace"
    doc = tmp_path / "phaseg28-distill.md"
    doc.write_text("# PhaseG28 Distill\n\nPhaseG28 opens MCP distill preview via shared contract.\n", encoding="utf-8")

    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.build_distilled_units(plan)

    mcp_payload = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_distill_preview",
                {"workspace": str(workspace), "limit": 5, "typed_unit_type": "concept"},
            )
        )[0].text
    )
    helper_payload = run_distill_contract(service, limit=5, typed_unit_type="concept")
    http_payload = TestClient(app).post(
        "/api/v1/knowledge/distill",
        json={"workspace": str(workspace), "limit": 5, "typed_unit_type": "concept"},
    ).json()

    assert mcp_payload == helper_payload
    assert mcp_payload == http_payload
    assert set(mcp_payload) == {
        "workspace",
        "schema_version",
        "manifest",
        "schema",
        "sources",
        "source_profiles",
        "source",
        "units",
        "available_source_count",
        "provenance_overview",
        "filters",
    }

    specs = {spec["name"]: spec for spec in all_tool_specs()}
    schema = specs["knowledge_distill_preview"]["inputSchema"]
    assert set(schema["properties"]) == {
        "workspace",
        "workspace_id",
        "source_id",
        "limit",
        "kind",
        "typed_unit_type",
        "min_importance",
        "llm_enriched_only",
        "authority",
        "min_source_weight",
        "min_source_density",
    }
    assert schema.get("required") is None


@pytest.mark.asyncio
async def test_phaseg29_source_trace_mcp_reuses_shared_contract(tmp_path, monkeypatch, capsys):
    pytest.importorskip("mcp")
    from app.main import app
    from data_service import mcp_stdio
    from data_service.__main__ import knowledge_main
    from data_service.mcp_tool_registry import all_tool_specs
    from data_service.service import DataService
    from data_service.source_trace_contract import source_trace_payload
    from fastapi.testclient import TestClient

    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    workspace = tmp_path / "workspace"
    doc = tmp_path / "phaseg29-trace.md"
    doc.write_text("# PhaseG29 Trace\n\nPhaseG29 opens MCP source trace via shared contract.\n", encoding="utf-8")

    service = DataService(workspace)
    plan = service.build_ingest_plan([str(doc)])
    service.run_default_pipeline(plan)
    source_id = service.read_distill_bundle(limit=5)["sources"][0]["source_id"]

    mcp_payload = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_trace",
                {"workspace": str(workspace), "source_id": source_id, "limit": 5},
            )
        )[0].text
    )
    helper_payload = source_trace_payload(service, source_id, limit=5)
    http_payload = TestClient(app).post(
        "/api/v1/knowledge/source/trace",
        json={"workspace": str(workspace), "source_id": source_id, "limit": 5},
    ).json()

    assert knowledge_main(["trace", "source", "--workspace", str(workspace), "--source-id", source_id, "--limit", "5"]) == 0
    cli_payload = json.loads(capsys.readouterr().out)

    assert mcp_payload == helper_payload
    assert mcp_payload == http_payload
    assert mcp_payload == cli_payload
    assert {"workspace", "source_id", "source", "distill", "llmwiki", "graphrag", "trace_summary"} <= set(mcp_payload)

    specs = {spec["name"]: spec for spec in all_tool_specs()}
    schema = specs["knowledge_source_trace"]["inputSchema"]
    assert set(schema["properties"]) == {"workspace", "workspace_id", "source_id", "limit"}
    assert schema.get("required") == ["source_id"]

def test_session_graph_service_boundary_contract():
    from app.graphrag.service import SESSION_GRAPH_MODEL_VERSION, SessionGraphService

    service = SessionGraphService(workspace_id="kb_boundary")
    graph = service.build_graph(
        session_id="ksess_boundary",
        units=[
            {
                "unit_id": "unit_1",
                "unit_type": "decision",
                "text": "确认最终验收通过。",
                "confidence": 0.9,
                "source_refs": [{"source_id": "src_1", "record_id": "turn-0001"}],
                "topics": ["最终验收"],
                "entities": ["最终验收"],
            }
        ],
        relations=[
            {
                "source": "actor:speaker_0",
                "target": "unit:unit_1",
                "type": "actor_proposed_decision",
                "weight": 0.91,
                "source_refs": [{"source_id": "src_1", "record_id": "turn-0001"}],
            },
            {
                "source": "unit:unit_1",
                "target": "source:src_1",
                "type": "unit_related_to_source",
                "weight": 1.0,
                "source_refs": [{"source_id": "src_1", "record_id": "turn-0001"}],
            },
            {
                "source": "unit:unit_1",
                "target": "topic:topic",
                "type": "unit_about_topic",
                "weight": 0.8,
                "source_refs": [{"source_id": "src_1", "record_id": "turn-0001"}],
                "label": "最终验收",
            },
        ],
        actors={"speaker_0": {"actor_id": "speaker_0", "label": "张三", "role": "speaker"}},
        source_nodes={"src_1": {"source_id": "src_1", "title": "会议转写", "source_type": "transcript", "content_format": "turns"}},
    )

    assert graph["graph_model_version"] == SESSION_GRAPH_MODEL_VERSION
    assert graph["stats"]["actor_count"] == 1
    assert graph["stats"]["unit_count"] == 1
    assert any(edge["type"] == "actor_proposed_decision" for edge in graph["edges"])
    summary = service.actor_summary(graph, actor_id="speaker_0")
    assert summary["decisions"][0]["source_refs"][0]["record_id"] == "turn-0001"


def test_session_relation_extractor_boundary_contract():
    from app.graphrag.service import SessionRelationExtractor

    extractor = SessionRelationExtractor()
    units, relations, actors, source_nodes = extractor.extract(
        session_id="ksess_extract",
        sources=[
            {
                "source": {
                    "source_id": "src_a",
                    "title": "会议转写 A",
                    "source_type": "transcript",
                    "content_format": "turns",
                    "related_source_ids": ["src_b"],
                },
                "records": [
                    {
                        "record_id": "turn-0001",
                        "actor_id": "speaker_0",
                        "actor_label": "张三",
                        "role": "speaker",
                        "start_time": 1.0,
                        "end_time": 3.0,
                        "text": "确认最终验收通过。",
                    },
                    {
                        "record_id": "turn-0002",
                        "actor_id": "speaker_1",
                        "actor_label": "李四",
                        "role": "speaker",
                        "text": "我负责提交发布计划。",
                    },
                ],
            },
            {
                "source": {
                    "source_id": "src_b",
                    "title": "会议转写 B",
                    "source_type": "transcript",
                    "content_format": "turns",
                },
                "records": [
                    {
                        "record_id": "turn-0003",
                        "actor_id": "speaker_2",
                        "actor_label": "王五",
                        "role": "speaker",
                        "text": "风险是上线环境延期。",
                    }
                ],
            },
        ],
    )

    assert {unit["unit_type"] for unit in units} >= {"decision", "task", "risk"}
    assert set(actors) == {"speaker_0", "speaker_1", "speaker_2"}
    assert set(source_nodes) == {"src_a", "src_b"}
    assert any(relation["type"] == "actor_proposed_decision" for relation in relations)
    assert any(relation["type"] == "actor_accepted_task" for relation in relations)
    assert any(relation["type"] == "actor_raised_risk" for relation in relations)
    assert any(relation["type"] == "source_related_to_source" for relation in relations)
    assert all(unit["source_refs"][0]["record_id"].startswith("turn-") for unit in units)


@pytest.mark.asyncio
async def test_data_service_mcp_resources_contract(tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio
    from data_service.mcp_resources import read_resource_payload
    from data_service.mcp_workspace_runtime import WorkspaceRuntime
    from data_service.service import DataService

    resources = await mcp_stdio.list_resources()
    assert [str(resource.uri) for resource in resources] == [
        "data-service://summary",
        "data-service://layout",
    ]

    legacy_layout = await mcp_stdio.read_resource("data_service://layout")
    assert str(legacy_layout.uri) == "data-service://layout"
    assert legacy_layout.mimeType == "application/json"
    assert json.loads(legacy_layout.text)["workspace"]

    service = DataService(tmp_path / "resource-workspace")
    runtime = WorkspaceRuntime(service.workspace)
    summary_mime, summary_text = read_resource_payload(
        "data_service://summary",
        service=service,
        layout_payload=runtime.layout_payload,
    )
    assert summary_mime == "text/markdown"
    assert "Data Service Summary" in summary_text


@pytest.mark.asyncio
async def test_data_service_mcp_dispatcher_v2_archive_blocked(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service.mcp_build_runtime import BuildRuntime
    from data_service.mcp_dispatcher import MCPToolDispatcher
    from data_service.mcp_workspace_runtime import WorkspaceRuntime

    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    default_workspace = tmp_path / "default"
    workspace_runtime = WorkspaceRuntime(default_workspace)
    dispatcher = MCPToolDispatcher(
        default_workspace=default_workspace,
        workspace_runtime=workspace_runtime,
        build_runtime=BuildRuntime(workspace_runtime),
    )

    created = await dispatcher.call_tool("knowledge_workspace_create", {"name": "Dispatch Contract"})
    workspace_id = created["workspace_id"]
    archived = await dispatcher.call_tool(
        "knowledge_workspace_archive",
        {"workspace_id": workspace_id, "reason": "contract test"},
    )
    assert archived["data"]["workspace"]["status"] == "archived"

    blocked = await dispatcher.call_tool(
        "knowledge_quality_feedback_v2",
        {
            "workspace_id": workspace_id,
            "target_type": "source",
            "target_id": "src_missing",
            "action": "note",
        },
    )
    assert blocked["status"] == "blocked"
    assert "archived" in blocked["warnings"][0]

    with pytest.raises(ValueError, match="Unknown tool"):
        await dispatcher.call_tool("knowledge_missing_tool", {})


@pytest.mark.asyncio
async def test_data_service_mcp_external_payload_hides_internal_paths(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source_file = source_root / "contract.md"
    source_file.write_text("# Contract\n\nPhaseC path contract.", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    created = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Contract KB"}))[0].text)
    workspace_id = created["workspace_id"]
    imported = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_import",
                {"workspace_id": workspace_id, "paths": [str(source_file)]},
            )
        )[0].text
    )
    started = json.loads((await mcp_stdio.call_tool("knowledge_build_start", {"workspace_id": workspace_id}))[0].text)
    operation_id = started["operation_id"]
    for _ in range(80):
        status = json.loads(
            (
                await mcp_stdio.call_tool(
                    "knowledge_build_status",
                    {"workspace_id": workspace_id, "operation_id": operation_id},
                )
            )[0].text
        )
        if status["status"] in {"completed", "failed", "blocked", "cancelled"}:
            break
        await asyncio.sleep(0.05)
    described = json.loads((await mcp_stdio.call_tool("knowledge_workspace_describe", {"workspace_id": workspace_id}))[0].text)

    for payload in [created, imported, started, status, described]:
        _assert_no_public_path_keys(payload)
    assert created["artifact_refs"][0]["artifact_ref"].startswith("artifact://")
    assert "debug_path" in created["artifact_refs"][0]
    assert imported["data"]["sources"][0]["debug_paths"]["path"]
    assert "artifact_refs" in status["data"]
    assert "artifacts" in status["data"]["debug_paths"]


@pytest.mark.asyncio
async def test_data_service_mcp_workspace_lifecycle(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))

    created = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_workspace_create",
                {"name": "Project Knowledge", "owner": "harness", "tags": ["demo"]},
            )
        )[0].text
    )
    assert created["status"] == "ok"
    assert created["workspace_id"] == "project-knowledge"
    assert created["operation_id"] is None
    assert created["warnings"] == []
    assert created["data"]["capabilities"]["build"] is True

    listed = json.loads((await mcp_stdio.call_tool("knowledge_workspace_list", {"owner": "harness"}))[0].text)
    assert listed["data"]["items"][0]["workspace_id"] == "project-knowledge"

    described = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_workspace_describe",
                {"workspace_id": "project-knowledge"},
            )
        )[0].text
    )
    assert described["workspace_id"] == "project-knowledge"
    assert "layout" in described["data"]
    assert "engines" in described["data"]

    archived = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_workspace_archive",
                {"workspace_id": "project-knowledge", "reason": "test done"},
            )
        )[0].text
    )
    assert archived["data"]["workspace"]["status"] == "archived"

    archived_feedback = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_quality_feedback_v2",
                {
                    "workspace_id": "project-knowledge",
                    "target_type": "source",
                    "target_id": "x",
                    "action": "note",
                },
            )
        )[0].text
    )
    assert archived_feedback["status"] == "blocked"


@pytest.mark.asyncio
async def test_data_service_mcp_source_import_is_idempotent(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source_file = source_root / "note.md"
    source_file.write_text("# Note\n\nHarness MCP source.", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    created = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Import KB"}))[0].text)
    workspace_id = created["workspace_id"]

    first = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_import",
                {"workspace_id": workspace_id, "paths": [str(source_file)]},
            )
        )[0].text
    )
    assert first["status"] == "ok"
    assert first["data"]["sources"][0]["status"] == "imported"
    assert first["data"]["sources"][0]["sha256"]
    source_id = first["data"]["sources"][0]["source_id"]

    second = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_import",
                {"workspace_id": workspace_id, "paths": [str(source_file)]},
            )
        )[0].text
    )
    assert second["data"]["sources"][0]["status"] == "duplicate"
    assert second["data"]["sources"][0]["source_id"] == source_id

    listed = json.loads((await mcp_stdio.call_tool("knowledge_source_list", {"workspace_id": workspace_id}))[0].text)
    assert len(listed["data"]["items"]) == 1
    assert listed["data"]["items"][0]["source_id"] == source_id


@pytest.mark.asyncio
async def test_data_service_mcp_source_import_rejects_disallowed_and_symlink(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    root = tmp_path / "managed"
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"
    allowed.mkdir()
    outside.mkdir()
    outside_file = outside / "secret.md"
    outside_file.write_text("secret", encoding="utf-8")
    symlink = allowed / "escape.md"
    symlink.symlink_to(outside_file)
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(allowed))

    created = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Secure KB"}))[0].text)
    workspace_id = created["workspace_id"]

    outside_result = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_import",
                {"workspace_id": workspace_id, "paths": [str(outside_file)]},
            )
        )[0].text
    )
    assert outside_result["status"] == "blocked"
    assert "Source path is outside allowed roots" in outside_result["warnings"][0]

    symlink_result = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_import",
                {"workspace_id": workspace_id, "paths": [str(symlink)]},
            )
        )[0].text
    )
    assert symlink_result["status"] == "blocked"
    assert "Source path is outside allowed roots" in symlink_result["warnings"][0]


@pytest.mark.asyncio
async def test_data_service_mcp_build_operation_lifecycle(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source_file = source_root / "build.md"
    source_file.write_text("# Build Note\n\nHarness build content.", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))
    created = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Build KB"}))[0].text)
    workspace_id = created["workspace_id"]
    await mcp_stdio.call_tool("knowledge_source_import", {"workspace_id": workspace_id, "paths": [str(source_file)]})

    started = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_build_start",
                {"workspace_id": workspace_id, "mode": "llmwiki_only"},
            )
        )[0].text
    )
    assert started["status"] == "queued"
    assert started["operation_id"]
    assert started["data"]["stage"] == "queued"
    operation_id = started["operation_id"]

    status = None
    for _ in range(80):
        status = json.loads(
            (
                await mcp_stdio.call_tool(
                    "knowledge_build_status",
                    {"workspace_id": workspace_id, "operation_id": operation_id},
                )
            )[0].text
        )
        if status["status"] in {"completed", "failed", "blocked"}:
            break
        await asyncio.sleep(0.05)
    assert status is not None
    assert status["status"] == "completed"
    assert status["data"]["stage"] == "completed"
    assert status["data"]["progress"] == 1.0
    assert status["data"]["retryable"] is False

    sources = json.loads((await mcp_stdio.call_tool("knowledge_source_list", {"workspace_id": workspace_id}))[0].text)
    assert sources["data"]["items"][0]["ingest_status"] == "built"

    completed_cancel = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_build_cancel",
                {"workspace_id": workspace_id, "operation_id": operation_id, "reason": "test"},
            )
        )[0].text
    )
    assert completed_cancel["status"] == "completed"
    assert completed_cancel["warnings"]


@pytest.mark.asyncio
async def test_data_service_mcp_build_cancel_queued_operation(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    created = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Cancel KB"}))[0].text)
    workspace_id = created["workspace_id"]
    started = json.loads((await mcp_stdio.call_tool("knowledge_build_start", {"workspace_id": workspace_id}))[0].text)
    cancelled = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_build_cancel",
                {"workspace_id": workspace_id, "operation_id": started["operation_id"], "reason": "test"},
            )
        )[0].text
    )
    assert cancelled["status"] in {"cancelled", "blocked"}


@pytest.mark.asyncio
async def test_data_service_mcp_build_operations_queue_by_workspace(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source_file = source_root / "queue.md"
    source_file.write_text("# Queue Note\n\nBuild queue fixture.", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    workspace_id = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Queue KB"}))[0].text)["workspace_id"]
    await mcp_stdio.call_tool("knowledge_source_import", {"workspace_id": workspace_id, "paths": [str(source_file)]})

    first = json.loads((await mcp_stdio.call_tool("knowledge_build_start", {"workspace_id": workspace_id, "mode": "llmwiki_only"}))[0].text)
    second = json.loads((await mcp_stdio.call_tool("knowledge_build_start", {"workspace_id": workspace_id, "mode": "llmwiki_only"}))[0].text)

    assert first["status"] == "queued"
    assert second["status"] == "queued"
    assert first["operation_id"] != second["operation_id"]

    final = {}
    for operation_id in (first["operation_id"], second["operation_id"]):
        for _ in range(100):
            status = json.loads(
                (
                    await mcp_stdio.call_tool(
                        "knowledge_build_status",
                        {"workspace_id": workspace_id, "operation_id": operation_id},
                    )
                )[0].text
            )
            if status["status"] in {"completed", "failed", "blocked", "cancelled"}:
                final[operation_id] = status
                break
            await asyncio.sleep(0.05)

    assert final[first["operation_id"]]["status"] == "completed"
    assert final[second["operation_id"]]["status"] == "completed"


@pytest.mark.asyncio
async def test_data_service_mcp_marks_interrupted_running_operation_retryable(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    created = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Interrupted KB"}))[0].text)
    workspace_id = created["workspace_id"]
    workspace_path = tmp_path / "managed" / workspace_id
    operation_id = "op_interrupted"
    operation_path = workspace_path / "lifecycle" / "operations" / f"{operation_id}.json"
    operation_path.parent.mkdir(parents=True, exist_ok=True)
    operation_path.write_text(
        json.dumps(
            {
                "operation_id": operation_id,
                "workspace_id": workspace_id,
                "mode": "full",
                "status": "running",
                "stage": "distill",
                "progress": 0.25,
                "error": None,
                "retryable": True,
                "artifacts": [],
                "created_at": "2026-05-02T00:00:00Z",
                "updated_at": "2026-05-02T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )

    started = json.loads((await mcp_stdio.call_tool("knowledge_build_start", {"workspace_id": workspace_id}))[0].text)
    assert started["status"] == "queued"

    interrupted = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_build_status",
                {"workspace_id": workspace_id, "operation_id": operation_id},
            )
        )[0].text
    )
    assert interrupted["status"] == "failed"
    assert interrupted["data"]["retryable"] is True
    assert interrupted["data"]["error"]["code"] == "server_interrupted"
    assert interrupted["data"]["error"]["retryable"] is True


@pytest.mark.asyncio
async def test_data_service_mcp_lifecycle_workspaces_are_isolated(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    root = tmp_path / "managed"
    source_root = tmp_path / "sources"
    source_root.mkdir()
    source_a = source_root / "a.md"
    source_a.write_text("A", encoding="utf-8")
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_SOURCE_ROOTS", str(source_root))

    workspace_a = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "A"}))[0].text)["workspace_id"]
    workspace_b = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "B"}))[0].text)["workspace_id"]
    await mcp_stdio.call_tool("knowledge_source_import", {"workspace_id": workspace_a, "paths": [str(source_a)]})

    sources_a = json.loads((await mcp_stdio.call_tool("knowledge_source_list", {"workspace_id": workspace_a}))[0].text)
    sources_b = json.loads((await mcp_stdio.call_tool("knowledge_source_list", {"workspace_id": workspace_b}))[0].text)

    assert len(sources_a["data"]["items"]) == 1
    assert sources_b["data"]["items"] == []


@pytest.mark.asyncio
async def test_data_service_mcp_existing_tools_accept_workspace_id(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    created = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Opaque ID KB"}))[0].text)
    workspace_id = created["workspace_id"]
    imported = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_import",
                {
                    "workspace_id": workspace_id,
                    "texts": [
                        {
                            "title": "Harness Note",
                            "content": "# Harness Note\n\nOpaque workspace id query content.",
                            "metadata": {"kind": "fixture"},
                        }
                    ],
                },
            )
        )[0].text
    )
    assert imported["data"]["sources"][0]["status"] == "imported"

    started = json.loads((await mcp_stdio.call_tool("knowledge_build_start", {"workspace_id": workspace_id, "mode": "llmwiki_only"}))[0].text)
    for _ in range(80):
        status = json.loads(
            (
                await mcp_stdio.call_tool(
                    "knowledge_build_status",
                    {"workspace_id": workspace_id, "operation_id": started["operation_id"]},
                )
            )[0].text
        )
        if status["status"] in {"completed", "failed", "blocked"}:
            break
        await asyncio.sleep(0.05)
    assert status["status"] == "completed"

    query = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_query",
                {"workspace_id": workspace_id, "query": "Opaque workspace", "mode": "llmwiki", "top_k": 3},
            )
        )[0].text
    )
    assert query["mode"] == "llmwiki"

    feedback = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_quality_feedback",
                {
                    "workspace_id": workspace_id,
                    "target_type": "source",
                    "target_id": imported["data"]["sources"][0]["source_id"],
                    "action": "note",
                    "reason": "workspace_id feedback path",
                },
            )
        )[0].text
    )
    assert feedback["workspace"].endswith(workspace_id)

    summary = json.loads((await mcp_stdio.call_tool("knowledge_quality_summary", {"workspace_id": workspace_id}))[0].text)
    assert summary["quality"]["manual_feedback"]["feedback_count"] == 1

    query_v2 = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_query_v2",
                {"workspace_id": workspace_id, "query": "Opaque workspace", "mode": "llmwiki", "top_k": 3},
            )
        )[0].text
    )
    assert query_v2["status"] == "ok"
    assert query_v2["workspace_id"] == workspace_id
    assert query_v2["data"]["mode"] == "llmwiki"

    feedback_v2 = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_quality_feedback_v2",
                {
                    "workspace_id": workspace_id,
                    "target_type": "source",
                    "target_id": imported["data"]["sources"][0]["source_id"],
                    "action": "note",
                    "reason": "v2 envelope feedback path",
                },
            )
        )[0].text
    )
    assert feedback_v2["status"] == "ok"
    assert feedback_v2["data"]["debug_paths"]["workspace"].endswith(workspace_id)

    summary_v2 = json.loads((await mcp_stdio.call_tool("knowledge_quality_summary_v2", {"workspace_id": workspace_id}))[0].text)
    assert summary_v2["status"] == "ok"
    assert summary_v2["data"]["quality"]["manual_feedback"]["feedback_count"] == 2


@pytest.mark.asyncio
async def test_data_service_mcp_lifecycle_unknown_ids_return_blocked(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    workspace_id = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Blocked KB"}))[0].text)["workspace_id"]

    unknown_source = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_source_remove",
                {"workspace_id": workspace_id, "source_id": "missing"},
            )
        )[0].text
    )
    assert unknown_source["status"] == "blocked"
    assert "Unknown source_id" in unknown_source["warnings"][0]
    assert unknown_source["data"]["error"]["code"] == "unknown_source_id"
    assert unknown_source["data"]["error"]["retryable"] is False

    unknown_operation = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_build_status",
                {"workspace_id": workspace_id, "operation_id": "missing"},
            )
        )[0].text
    )
    assert unknown_operation["status"] == "blocked"
    assert "Unknown operation_id" in unknown_operation["warnings"][0]
    assert unknown_operation["data"]["error"]["code"] == "unknown_operation_id"
    assert unknown_operation["data"]["error"]["retryable"] is False


@pytest.mark.asyncio
async def test_data_service_mcp_quality_feedback_review_and_plan(tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    workspace = tmp_path / "workspace"
    feedback_content = await mcp_stdio.call_tool(
        "knowledge_quality_feedback",
        {
            "workspace": str(workspace),
            "target_type": "entity",
            "target_id": "old-topic",
            "action": "merge_suggest",
            "label": "Old Topic",
            "suggested_value": "Canonical Topic",
            "reason": "Agent 识别为同一 topic",
            "metadata": {"source": "mcp-test"},
        },
    )
    feedback = json.loads(feedback_content[0].text)
    assert feedback["target_type"] == "entity"
    assert feedback["metadata"]["source"] == "mcp-test"

    rules_content = await mcp_stdio.call_tool(
        "knowledge_correction_rules",
        {"workspace": str(workspace), "limit": 10},
    )
    rules = json.loads(rules_content[0].text)
    assert rules["total_count"] == 1
    rule_id = rules["items"][0]["rule_id"]

    review_content = await mcp_stdio.call_tool(
        "knowledge_review_correction_rule",
        {
            "workspace": str(workspace),
            "rule_id": rule_id,
            "status": "approved",
            "reviewer": "agent",
            "note": "受控批准",
        },
    )
    reviewed = json.loads(review_content[0].text)
    assert reviewed["rule"]["status"] == "approved"
    assert reviewed["correction_plan"]["source_rule_count"] == 1

    plan_content = await mcp_stdio.call_tool(
        "knowledge_correction_plan",
        {"workspace": str(workspace)},
    )
    plan = json.loads(plan_content[0].text)
    assert plan["source_rule_count"] == 1
    assert plan["summary"]["action_count"] == 1
    assert plan["actions"][0]["impact"]["summary"]["total_matches"] == 0

    summary_content = await mcp_stdio.call_tool(
        "knowledge_quality_summary",
        {"workspace": str(workspace)},
    )
    summary = json.loads(summary_content[0].text)
    assert summary["quality"]["manual_feedback"]["feedback_count"] == 1
    assert summary["quality"]["correction_rules"]["status_counts"]["approved"] == 1
    assert summary["quality_correction_plan"]["summary"]["action_count"] == 1


def test_phaseg8_quality_summary_and_correction_plan_contract_documented():
    from app.api.v1.data_service import router
    from data_service.mcp_tool_registry import V2_TOOL_MAP, all_tool_specs

    contract_source = (V15_DOCS_ROOT / "quality-contract.md").read_text(encoding="utf-8")
    matrix_source = (V15_DOCS_ROOT / "interface-convergence-matrix.md").read_text(encoding="utf-8")
    specs = {spec["name"]: spec for spec in all_tool_specs()}

    assert {"knowledge_quality_summary", "knowledge_correction_plan"} <= set(specs)
    assert V2_TOOL_MAP["knowledge_quality_summary_v2"] == "knowledge_quality_summary"
    assert V2_TOOL_MAP["knowledge_correction_plan_v2"] == "knowledge_correction_plan"

    summary_schema = specs["knowledge_quality_summary"]["inputSchema"]
    plan_schema = specs["knowledge_correction_plan"]["inputSchema"]
    assert set(summary_schema["properties"]) == {"workspace", "workspace_id"}
    assert set(plan_schema["properties"]) == {"workspace", "workspace_id", "rebuild"}
    assert summary_schema.get("required") is None
    assert plan_schema.get("required") is None

    route_paths = {getattr(route, "path", "") for route in router.routes}
    assert "/knowledge/quality/summary" not in route_paths
    assert "/knowledge/quality/corrections/plan" in route_paths

    assert _cli_quality_subcommands() == {
        "summary",
        "correction-plan",
        "feedback-list",
        "feedback",
        "rules",
        "rules-build",
        "review",
    }

    for required_text in [
        "knowledge_quality_summary",
        "knowledge_correction_plan",
        "workspace_id",
        "rebuild",
        "quality_feedback",
        "quality_correction_rules",
        "quality_correction_plan",
        "source_rule_count",
        "actions",
        "/api/v1/knowledge/quality/corrections/plan",
        "不新增 HTTP route",
        "PhaseG14 开放写入型 CLI command",
    ]:
        assert required_text in contract_source
    assert "PhaseG8 已固化 Quality Summary / Correction Plan" in matrix_source


@pytest.mark.asyncio
async def test_phaseg8_quality_summary_and_correction_plan_shapes_stay_stable(tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    workspace = tmp_path / "workspace"
    await mcp_stdio.call_tool(
        "knowledge_quality_feedback",
        {
            "workspace": str(workspace),
            "target_type": "entity",
            "target_id": "phaseg8-topic",
            "action": "rename_suggest",
            "label": "PhaseG8 Topic",
            "suggested_value": "Quality Contract Topic",
            "reason": "PhaseG8 contract drift test",
            "metadata": {"phase": "G8"},
        },
    )
    rules = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_correction_rules",
                {"workspace": str(workspace), "limit": 10},
            )
        )[0].text
    )
    rule_id = rules["items"][0]["rule_id"]
    await mcp_stdio.call_tool(
        "knowledge_review_correction_rule",
        {
            "workspace": str(workspace),
            "rule_id": rule_id,
            "status": "approved",
            "reviewer": "phaseg8",
            "note": "contract shape approval",
        },
    )

    plan = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_correction_plan",
                {"workspace": str(workspace)},
            )
        )[0].text
    )
    summary = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_quality_summary",
                {"workspace": str(workspace)},
            )
        )[0].text
    )

    assert set(summary) == {
        "workspace",
        "quality",
        "quality_feedback",
        "quality_correction_rules",
        "quality_correction_plan",
    }
    assert {"manual_feedback", "correction_rules", "correction_plan"} <= set(summary["quality"])
    assert isinstance(summary["quality_feedback"], list)
    assert isinstance(summary["quality_correction_rules"], list)
    assert summary["quality"]["manual_feedback"]["feedback_count"] == 1
    assert summary["quality"]["correction_rules"]["status_counts"]["approved"] == 1

    assert set(plan) == {
        "schema_version",
        "workspace",
        "generated_at",
        "source_rule_count",
        "actions",
        "summary",
        "notes",
    }
    assert plan["schema_version"] == "1.0"
    assert plan["source_rule_count"] == 1
    assert plan["summary"]["action_count"] == 1
    assert {
        "action_count",
        "action_counts",
        "target_engine_counts",
        "target_type_counts",
        "impacted_action_count",
        "impact_counts",
    } <= set(plan["summary"])
    assert {
        "action_id",
        "source_rule_id",
        "source_feedback_id",
        "target_type",
        "target_id",
        "action",
        "current_label",
        "proposed_value",
        "target_engines",
        "impact",
    } <= set(plan["actions"][0])
    assert "summary" in plan["actions"][0]["impact"]


def test_phaseg9_quality_feedback_rules_review_contract_documented():
    from app.api.v1.data_service import router
    from data_service.mcp_quality_tools import RULE_STATUSES
    from data_service.mcp_tool_registry import V2_TOOL_MAP, all_tool_specs

    contract_source = (V15_DOCS_ROOT / "quality-contract.md").read_text(encoding="utf-8")
    matrix_source = (V15_DOCS_ROOT / "interface-convergence-matrix.md").read_text(encoding="utf-8")
    specs = {spec["name"]: spec for spec in all_tool_specs()}

    assert {
        "knowledge_quality_feedback",
        "knowledge_correction_rules",
        "knowledge_review_correction_rule",
    } <= set(specs)
    assert V2_TOOL_MAP["knowledge_quality_feedback_v2"] == "knowledge_quality_feedback"
    assert V2_TOOL_MAP["knowledge_correction_rules_v2"] == "knowledge_correction_rules"
    assert V2_TOOL_MAP["knowledge_review_correction_rule_v2"] == "knowledge_review_correction_rule"

    feedback_schema = specs["knowledge_quality_feedback"]["inputSchema"]
    rules_schema = specs["knowledge_correction_rules"]["inputSchema"]
    review_schema = specs["knowledge_review_correction_rule"]["inputSchema"]
    assert set(feedback_schema["properties"]) == {
        "workspace",
        "workspace_id",
        "target_type",
        "target_id",
        "action",
        "label",
        "suggested_value",
        "reason",
        "metadata",
    }
    assert feedback_schema["required"] == ["target_type", "target_id", "action"]
    assert set(rules_schema["properties"]) == {"workspace", "workspace_id", "limit", "status"}
    assert rules_schema["properties"]["status"]["enum"] == RULE_STATUSES
    assert rules_schema.get("required") is None
    assert set(review_schema["properties"]) == {
        "workspace",
        "workspace_id",
        "rule_id",
        "status",
        "reviewer",
        "note",
    }
    assert review_schema["properties"]["status"]["enum"] == RULE_STATUSES
    assert review_schema["required"] == ["rule_id", "status"]

    route_paths = {getattr(route, "path", "") for route in router.routes}
    assert {
        "/knowledge/quality/feedback",
        "/knowledge/quality/feedback/list",
        "/knowledge/quality/corrections",
        "/knowledge/quality/corrections/build",
        "/knowledge/quality/corrections/review",
    } <= route_paths

    assert _cli_quality_subcommands() == {
        "summary",
        "correction-plan",
        "feedback-list",
        "feedback",
        "rules",
        "rules-build",
        "review",
    }

    for required_text in [
        "PhaseG9",
        "knowledge_quality_feedback",
        "knowledge_correction_rules",
        "knowledge_review_correction_rule",
        "target_type",
        "target_id",
        "action",
        "rule_id",
        "status",
        "rules_path",
        "source_feedback_id",
        "correction_plan.source_rule_count",
        "写入型 CLI command 已开放",
        "Review 必须保持 non-destructive governance",
    ]:
        assert required_text in contract_source
    assert "PhaseG9 已固化 Quality Feedback / Rules / Review" in matrix_source


def test_phaseg14_quality_cli_stage3_commands_documented():
    contract_source = (V15_DOCS_ROOT / "quality-contract.md").read_text(encoding="utf-8")
    matrix_source = (V15_DOCS_ROOT / "interface-convergence-matrix.md").read_text(encoding="utf-8")
    import data_service.__main__ as cli_module

    command_choices = _cli_command_choices()
    assert set(command_choices) == {
        "ingest",
        "summary",
        "distill",
        "boundary",
        "graphrag-execute",
        "query",
        "quality",
    }
    assert _cli_quality_subcommands() == {
        "summary",
        "correction-plan",
        "feedback-list",
        "feedback",
        "rules",
        "rules-build",
        "review",
    }
    knowledge_parser = cli_module._build_knowledge_parser()
    knowledge_action = next(action for action in knowledge_parser._actions if getattr(action, "choices", None))
    assert knowledge_parser.prog == "knowledge"
    assert set(knowledge_action.choices) == {"quality", "query", "workspace", "source", "build", "graph", "trace", "code"}
    code_parser = knowledge_action.choices["code"]
    code_action = next(action for action in code_parser._actions if getattr(action, "choices", None))
    assert set(code_action.choices) == {
        "import",
        "list",
        "snapshot",
        "inventory",
        "symbols",
        "trace",
        "overview",
        "context-pack",
            "devwiki",
            "graph",
                "platform",
                "quality",
                "architecture",
                "architecture-intent",
                "coding-agent",
                "describe",
                "archive",
            }
    workspace_parser = knowledge_action.choices["workspace"]
    workspace_action = next(action for action in workspace_parser._actions if getattr(action, "choices", None))
    assert set(workspace_action.choices) == {"create", "list", "describe", "archive"}
    source_parser = knowledge_action.choices["source"]
    source_action = next(action for action in source_parser._actions if getattr(action, "choices", None))
    assert set(source_action.choices) == {"import", "list", "remove"}
    build_parser = knowledge_action.choices["build"]
    build_action = next(action for action in build_parser._actions if getattr(action, "choices", None))
    assert set(build_action.choices) == {"start", "status", "cancel"}
    graph_parser = knowledge_action.choices["graph"]
    graph_action = next(action for action in graph_parser._actions if getattr(action, "choices", None))
    assert set(graph_action.choices) == {"snapshot", "neighbors", "community", "query", "session"}
    trace_parser = knowledge_action.choices["trace"]
    trace_action = next(action for action in trace_parser._actions if getattr(action, "choices", None))
    assert set(trace_action.choices) == {"source"}
    assert callable(cli_module.knowledge_main)

    for required_text in [
        "PhaseG12 Quality CLI planned 迁移窗口",
        "PhaseG13 Quality CLI 只读 preview",
        "PhaseG14 Quality CLI 写入型命令",
        "PhaseG15 knowledge quality alias",
        "data_service quality summary --workspace-id research-vault",
        "knowledge quality summary --workspace-id research-vault",
        "data_service quality correction-plan --workspace-id research-vault --rebuild",
        "data_service quality feedback --workspace-id research-vault",
        "data_service quality feedback-list --workspace-id research-vault",
        "data_service quality rules --workspace-id research-vault",
        "data_service quality rules-build --workspace-id research-vault",
        "data_service quality review --workspace-id research-vault",
        "Stage 1",
        "Stage 2",
        "Stage 3",
        "Stage 4",
        "PhaseG13 开放只读 CLI preview",
        "PhaseG14 开放写入型 CLI command",
        "PhaseG15 提供 `knowledge_main` entrypoint-ready alias",
        "PhaseG17 冻结 `knowledge` 顶层命令只包含 `quality`",
        "PhaseG18 开放 `knowledge query`",
        "knowledge query PhaseG18 --workspace-id research-vault",
        "PhaseG18-G23 已按能力组逐步开放 query",
        "不得一次性开放 `knowledge distill/graph 扩展`",
        "写入型 CLI command 已开放",
        "必须复用 `data_service.quality_contract` helper 或现有 MCP handler",
    ]:
        assert required_text in contract_source
    assert "PhaseG29 已开放 MCP knowledge_source_trace" in matrix_source
    graph_contract = (V15_DOCS_ROOT / "graph-cli-contract.md").read_text(encoding="utf-8")
    assert "PhaseG24 固化 `knowledge graph` advanced 子命令迁移窗口" in graph_contract
    assert "knowledge graph neighbors" in graph_contract
    assert "knowledge graph session" in graph_contract


@pytest.mark.asyncio
async def test_phaseg9_quality_feedback_rules_review_shapes_stay_stable(tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    workspace = tmp_path / "workspace"
    feedback = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_quality_feedback",
                {
                    "workspace": str(workspace),
                    "target_type": "entity",
                    "target_id": "phaseg9-topic",
                    "action": "merge_suggest",
                    "label": "PhaseG9 Topic",
                    "suggested_value": "Quality Governance Topic",
                    "reason": "PhaseG9 contract drift test",
                    "metadata": {"phase": "G9"},
                },
            )
        )[0].text
    )

    assert set(feedback) == {
        "feedback_id",
        "created_at",
        "workspace",
        "target_type",
        "target_id",
        "action",
        "label",
        "suggested_value",
        "reason",
        "metadata",
    }
    assert feedback["target_type"] == "entity"
    assert feedback["metadata"] == {"phase": "G9"}

    rules = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_correction_rules",
                {"workspace": str(workspace), "limit": 10, "status": "draft"},
            )
        )[0].text
    )
    assert set(rules) == {
        "workspace",
        "rules_path",
        "items",
        "total_count",
        "filtered_count",
        "summary",
        "generated_at",
        "schema_version",
    }
    assert rules["schema_version"] == "1.0"
    assert rules["total_count"] == 1
    assert rules["filtered_count"] == 1
    assert {"rule_count", "status_counts", "rule_type_counts", "target_type_counts"} <= set(rules["summary"])
    assert rules["summary"]["status_counts"]["draft"] == 1
    rule = rules["items"][0]
    assert {
        "rule_id",
        "rule_type",
        "status",
        "target_type",
        "target_id",
        "current_label",
        "proposed_value",
        "reason",
        "source_feedback_id",
        "created_at",
        "metadata",
    } <= set(rule)
    assert rule["source_feedback_id"] == feedback["feedback_id"]

    reviewed = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_review_correction_rule",
                {
                    "workspace": str(workspace),
                    "rule_id": rule["rule_id"],
                    "status": "approved",
                    "reviewer": "phaseg9",
                    "note": "contract review approval",
                },
            )
        )[0].text
    )
    assert set(reviewed) == {"workspace", "rules_path", "rule", "summary", "correction_plan"}
    assert reviewed["rule"]["rule_id"] == rule["rule_id"]
    assert reviewed["rule"]["status"] == "approved"
    assert reviewed["rule"]["reviewer"] == "phaseg9"
    assert reviewed["rule"]["review_note"] == "contract review approval"
    assert reviewed["summary"]["status_counts"]["approved"] == 1
    assert set(reviewed["correction_plan"]) == {"summary", "source_rule_count"}
    assert reviewed["correction_plan"]["source_rule_count"] == 1
    assert reviewed["correction_plan"]["summary"]["action_count"] == 1


@pytest.mark.asyncio
async def test_data_service_mcp_rejects_unbounded_query_limits(tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    with pytest.raises(ValueError, match="top_k must be between 1 and 50"):
        await mcp_stdio.call_tool(
            "knowledge_query",
            {"workspace": str(tmp_path / "workspace"), "query": "test", "top_k": 1000000},
        )


@pytest.mark.asyncio
async def test_data_service_mcp_keeps_per_call_workspaces_isolated(tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    workspace_a = tmp_path / "workspace-a"
    workspace_b = tmp_path / "workspace-b"
    await mcp_stdio.call_tool(
        "knowledge_quality_feedback",
        {
            "workspace": str(workspace_a),
            "target_type": "entity",
            "target_id": "a",
            "action": "rename_suggest",
            "suggested_value": "A",
        },
    )

    summary_a = json.loads((await mcp_stdio.call_tool("knowledge_quality_summary", {"workspace": str(workspace_a)}))[0].text)
    summary_b = json.loads((await mcp_stdio.call_tool("knowledge_quality_summary", {"workspace": str(workspace_b)}))[0].text)

    assert summary_a["quality"]["manual_feedback"]["feedback_count"] == 1
    assert summary_b["quality"]["manual_feedback"]["feedback_count"] == 0


@pytest.mark.asyncio
async def test_data_service_mcp_session_lifecycle_ingest_build_and_delete(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    workspace_id = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Meeting KB"}))[0].text)["workspace_id"]

    created = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_session_create",
                {
                    "workspace_id": workspace_id,
                    "external_id": "meeting-2026-05-08-001",
                    "session_type": "meeting",
                    "title": "项目发布计划会议",
                    "ephemeral": True,
                    "ttl_seconds": 86400,
                    "metadata": {"meeting_id": "meeting-2026-05-08-001"},
                },
            )
        )[0].text
    )
    assert created["status"] == "ok"
    assert created["data"]["created"] is True
    session_id = created["data"]["session"]["session_id"]

    duplicate = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_session_create",
                {
                    "workspace_id": workspace_id,
                    "external_id": "meeting-2026-05-08-001",
                    "session_type": "meeting",
                },
            )
        )[0].text
    )
    assert duplicate["data"]["created"] is False
    assert duplicate["data"]["session"]["session_id"] == session_id

    turns = [
        {"record_id": "turn-0001", "actor_id": "speaker_0", "actor_label": "张三", "role": "speaker", "start_time": 1.0, "end_time": 4.0, "text": "我们下周一完成最终验收。"},
        {"record_id": "turn-0002", "actor_id": "speaker_1", "actor_label": "李四", "role": "speaker", "start_time": 4.0, "end_time": 8.0, "text": "我负责整理发布材料和测试报告。"},
        {"record_id": "turn-0003", "actor_id": "speaker_2", "actor_label": "王五", "role": "speaker", "start_time": 8.0, "end_time": 12.0, "text": "风险是验收环境可能延期。"},
        {"record_id": "turn-0004", "actor_id": "speaker_0", "actor_label": "张三", "role": "speaker", "start_time": 12.0, "end_time": 15.0, "text": "测试今天必须完成。"},
        {"record_id": "turn-0005", "actor_id": "speaker_1", "actor_label": "李四", "role": "speaker", "start_time": 15.0, "end_time": 18.0, "text": "发布计划需要客户确认吗？"},
        {"record_id": "turn-0006", "actor_id": "speaker_2", "actor_label": "王五", "role": "speaker", "start_time": 18.0, "end_time": 20.0, "text": "我会跟进验收环境问题。"},
        {"record_id": "turn-0007", "actor_id": "speaker_0", "actor_label": "张三", "role": "speaker", "start_time": 20.0, "end_time": 24.0, "text": "确认发布计划按原排期推进。"},
        {"record_id": "turn-0008", "actor_id": "speaker_1", "actor_label": "李四", "role": "speaker", "start_time": 24.0, "end_time": 28.0, "text": "我提交最终验收材料。"},
        {"record_id": "turn-0009", "actor_id": "speaker_2", "actor_label": "王五", "role": "speaker", "start_time": 28.0, "end_time": 32.0, "text": "如果测试失败，需要回滚方案。"},
        {"record_id": "turn-0010", "actor_id": "speaker_0", "actor_label": "张三", "role": "speaker", "start_time": 32.0, "end_time": 36.0, "text": "最终验收通过后发布。"},
    ]
    ingested = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_session_ingest",
                {
                    "workspace_id": workspace_id,
                    "session_id": session_id,
                    "source_type": "transcript",
                    "content_format": "turns",
                    "title": "项目发布计划会议转写",
                    "records": turns,
                    "metadata": {"meeting_id": "meeting-2026-05-08-001", "language": "zh"},
                },
            )
        )[0].text
    )
    assert ingested["data"]["source"]["record_count"] == 10

    started = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_session_build_start",
                {"workspace_id": workspace_id, "session_id": session_id, "mode": "full"},
            )
        )[0].text
    )
    operation_id = started["operation_id"]
    for _ in range(80):
        status = json.loads(
            (
                await mcp_stdio.call_tool(
                    "knowledge_session_build_status",
                    {"workspace_id": workspace_id, "session_id": session_id, "operation_id": operation_id},
                )
            )[0].text
        )
        if status["status"] in {"succeeded", "failed", "blocked", "cancelled"}:
            break
        await asyncio.sleep(0.05)
    assert status["status"] == "succeeded"
    assert status["data"]["results"]["unit_count"] >= 10

    snapshot = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_graph_snapshot",
                {"workspace_id": workspace_id, "scope": "session", "session_id": session_id, "node_types": ["actor", "unit", "topic", "entity", "source"]},
            )
        )[0].text
    )
    nodes = snapshot["data"]["nodes"]
    edges = snapshot["data"]["edges"]
    assert {node["type"] for node in nodes} >= {"actor", "unit", "topic", "entity", "source"}
    assert {node["id"] for node in nodes} >= {"actor:speaker_0", "actor:speaker_1", "actor:speaker_2"}
    assert any(edge["type"] == "actor_proposed_decision" for edge in edges)
    assert any(edge["source_refs"][0]["record_id"] == "turn-0001" for edge in edges if edge.get("source_refs"))
    assert snapshot["data"]["communities"]

    actor_summary = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_actor_summary",
                {"workspace_id": workspace_id, "session_id": session_id, "actor_id": "speaker_0", "unit_types": ["statement", "decision", "task", "risk", "question"]},
            )
        )[0].text
    )
    assert actor_summary["data"]["actor"]["label"] == "张三"
    assert actor_summary["data"]["decisions"]
    assert all(ref["record_id"].startswith("turn-") for ref in actor_summary["data"]["source_refs"])

    query = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_session_query",
                {"workspace_id": workspace_id, "session_id": session_id, "query": "最终验收", "top_k": 5},
            )
        )[0].text
    )
    assert query["data"]["hits"]
    assert "workspace_context" not in query["data"]

    closed = json.loads((await mcp_stdio.call_tool("knowledge_session_close", {"workspace_id": workspace_id, "session_id": session_id}))[0].text)
    assert closed["status"] == "closed"
    blocked_write = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_session_ingest",
                {"workspace_id": workspace_id, "session_id": session_id, "content_format": "text", "content": "closed write"},
            )
        )[0].text
    )
    assert blocked_write["status"] == "blocked"

    deleted = json.loads((await mcp_stdio.call_tool("knowledge_session_delete", {"workspace_id": workspace_id, "session_id": session_id}))[0].text)
    assert deleted["status"] == "disposed"
    disposed_snapshot = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_graph_snapshot",
                {"workspace_id": workspace_id, "scope": "session", "session_id": session_id},
            )
        )[0].text
    )
    assert disposed_snapshot["status"] == "disposed"
    assert disposed_snapshot["data"]["error"]["code"] == "session_disposed"
    assert disposed_snapshot["data"]["error"]["retryable"] is False


@pytest.mark.asyncio
async def test_data_service_mcp_session_scope_isolates_two_sessions(monkeypatch, tmp_path):
    pytest.importorskip("mcp")
    from data_service import mcp_stdio

    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(tmp_path / "managed"))
    workspace_id = json.loads((await mcp_stdio.call_tool("knowledge_workspace_create", {"name": "Scoped KB"}))[0].text)["workspace_id"]

    async def build_session(external_id, actor_id, text):
        created = json.loads((await mcp_stdio.call_tool("knowledge_session_create", {"workspace_id": workspace_id, "external_id": external_id}))[0].text)
        session_id = created["data"]["session"]["session_id"]
        await mcp_stdio.call_tool(
            "knowledge_session_ingest",
            {
                "workspace_id": workspace_id,
                "session_id": session_id,
                "source_type": "transcript",
                "content_format": "turns",
                "records": [{"record_id": "turn-0001", "actor_id": actor_id, "actor_label": actor_id, "text": text}],
            },
        )
        started = json.loads((await mcp_stdio.call_tool("knowledge_session_build_start", {"workspace_id": workspace_id, "session_id": session_id}))[0].text)
        for _ in range(80):
            status = json.loads(
                (
                    await mcp_stdio.call_tool(
                        "knowledge_session_build_status",
                        {"workspace_id": workspace_id, "session_id": session_id, "operation_id": started["operation_id"]},
                    )
                )[0].text
            )
            if status["status"] in {"succeeded", "failed", "blocked", "cancelled"}:
                break
            await asyncio.sleep(0.05)
        assert status["status"] == "succeeded"
        return session_id

    session_a = await build_session("meeting-a", "speaker_a", "A 项目最终验收通过。")
    session_b = await build_session("meeting-b", "speaker_b", "B 项目预算风险需要处理。")

    query_a = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_session_query",
                {"workspace_id": workspace_id, "session_id": session_a, "query": "预算风险", "top_k": 10},
            )
        )[0].text
    )
    assert query_a["data"]["hits"] == []

    snapshot_a = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_graph_snapshot",
                {"workspace_id": workspace_id, "scope": "session", "session_id": session_a},
            )
        )[0].text
    )
    snapshot_b = json.loads(
        (
            await mcp_stdio.call_tool(
                "knowledge_graph_snapshot",
                {"workspace_id": workspace_id, "scope": "session", "session_id": session_b},
            )
        )[0].text
    )
    assert snapshot_a["data"]["communities"][0]["id"] != snapshot_b["data"]["communities"][0]["id"]
    assert "speaker_b" not in {node["id"].replace("actor:", "") for node in snapshot_a["data"]["nodes"] if node["type"] == "actor"}
