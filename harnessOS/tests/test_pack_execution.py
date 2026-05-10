from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.packs import DomainPackManifest, build_default_pack_registry, build_pack_execution_plan, execute_pack_stub


def test_pack_execution_builds_knowledge_lifecycle_plan():
    registry = build_default_pack_registry()
    pack = registry.get_pack("knowledge")

    plan = build_pack_execution_plan(pack, template_id="knowledge.lifecycle")

    assert plan.status == "planned"
    assert plan.execution_order == (
        "workspace_create",
        "workspace_describe",
        "source_import",
        "build_start",
        "source_list",
        "build_status",
        "query",
        "quality_feedback",
        "correction_rules",
        "correction_plan",
    )
    assert plan.nodes[0]["uses"] == "data_service_mcp.knowledge_workspace_create"
    assert plan.nodes[6]["uses"] == "data_service_mcp.knowledge_query_v2"
    assert plan.edges[0] == {"source": "workspace_create", "target": "workspace_describe"}


def test_pack_execution_stub_produces_artifact_requests_with_parent_kinds():
    registry = build_default_pack_registry()
    pack = registry.get_pack("knowledge")

    result = execute_pack_stub(pack, template_id="knowledge.lifecycle")

    assert result.status == "stubbed"
    assert [request["kind"] for request in result.artifact_requests] == [
        "source_reference",
        "note",
        "brief",
        "citation_bundle",
    ]
    assert result.artifact_requests[1]["parent_kinds"] == ["source_reference"]
    assert result.artifact_requests[-1]["parent_kinds"] == ["brief"]
    assert result.node_results[0]["execution_deferred"] is True


def test_pack_execution_blocks_missing_agent_owner():
    manifest = DomainPackManifest(
        name="demo",
        version="0.1.0",
        domain="demo",
        status="active",
        connectors=("demo_connector",),
        workflow_templates={
            "demo.pipeline": {
                "nodes": [
                    {"id": "start", "type": "agent", "owner": "missing.agent", "outputs": ["brief"]}
                ],
                "edges": [],
            }
        },
    )

    plan = build_pack_execution_plan(manifest, template_id="demo.pipeline")
    result = execute_pack_stub(manifest, template_id="demo.pipeline")

    assert plan.status == "blocked"
    assert plan.missing_dependencies == ("agent:missing.agent",)
    assert result.status == "blocked"


def test_pack_execution_blocks_unsupported_node_type():
    manifest = DomainPackManifest(
        name="demo",
        version="0.1.0",
        domain="demo",
        status="active",
        workflow_templates={
            "demo.pipeline": {
                "kind": "typed_dag",
                "nodes": [
                    {"id": "start", "type": "agent_task", "outputs": ["brief"]}
                ],
                "edges": [],
            }
        },
    )

    plan = build_pack_execution_plan(manifest, template_id="demo.pipeline")

    assert plan.status == "blocked"
    assert plan.missing_dependencies == ("node_type:start:agent_task",)
