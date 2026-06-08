from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.coding_agent.persistence import actionability_definitions_path, actionability_index_path, actionability_references_path, actionability_test_mapping_path
from data_service.code_assets.coding_agent.service import CodingAgentActionabilityService, FORBIDDEN_RELATION_TYPES
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _assert_actionability(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo_path: str) -> None:
    actionability = payload["data"]["actionability"] if "data" in payload else payload
    index = actionability["index"]
    assert index["schema_version"] == "v2.11"
    assert index["workspace_id"] == workspace_id
    assert index["codebase_id"] == codebase_id
    assert index["snapshot_id"] == snapshot_id
    assert index["summary"]["definition_count"] >= 3
    assert index["summary"]["reference_count"] >= 1
    assert index["summary"]["forbidden_relation_count"] == 0
    providers = {item["provider"]: item for item in index["provider_status"]}
    assert providers["python_ast"]["mandatory"] is True
    assert providers["python_ast"]["status"] == "available"
    assert providers["tree_sitter"]["status"] == "unavailable"
    assert providers["lsp"]["status"] == "unavailable"
    assert actionability["definitions"]
    assert actionability["references"]
    assert not {row["relation_type"] for row in actionability["references"]} & FORBIDDEN_RELATION_TYPES
    assert str(repo_path) not in json.dumps(actionability, ensure_ascii=False)
    for definition in actionability["definitions"][:20]:
        assert definition["evidence_refs"]
        assert definition.get("path") or definition.get("source_file")
        assert definition["line_range"][0] >= 1


def _assert_impact(payload: dict, *, repo_path: str) -> dict:
    impact = payload["data"]["impact"] if "data" in payload else payload
    assert impact["schema_version"] == "v2.11"
    assert impact["impact_id"]
    assert impact["summary"]["candidate_count"] >= 1
    assert impact["summary"]["forbidden_claims"] == []
    assert impact["impacted_targets"]
    assert str(repo_path) not in json.dumps(impact, ensure_ascii=False)
    for item in impact["impacted_targets"][:10]:
        assert item["status"] in {"accepted", "needs_review"}
        assert item["reason_codes"]
        if item["status"] == "accepted":
            assert item["evidence_refs"]
    return impact


def _assert_task_plan(payload: dict, *, repo_path: str) -> dict:
    plan = payload["data"]["task_plan"] if "data" in payload else payload
    assert plan["schema_version"] == "v2.11"
    assert plan["summary"]["mutates_code"] is False
    assert plan["summary"]["executes_runtime"] is False
    assert plan["recommended_edits"]
    assert str(repo_path) not in json.dumps(plan, ensure_ascii=False)
    for item in plan["recommended_edits"]:
        assert item.get("evidence_refs") or item.get("needs_review")
    return plan


def test_v211_actionability_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = CodingAgentActionabilityService(workspace, workspace_id=workspace_id)

    actionability = service.build_actionability(codebase_id, snapshot_id=snapshot_id)
    assert actionability_index_path(workspace, codebase_id).exists()
    assert actionability_definitions_path(workspace, codebase_id).exists()
    assert actionability_references_path(workspace, codebase_id).exists()
    assert actionability_test_mapping_path(workspace, codebase_id).exists()
    _assert_actionability(actionability, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    api_impact = service.analyze_impact(codebase_id, task="新增 HTTP API behavior 并更新 route handler 测试", snapshot_id=snapshot_id)
    _assert_impact(api_impact, repo_path=str(repo))
    mcp_cli_impact = service.analyze_impact(codebase_id, task="修改 MCP CLI capability registration", snapshot_id=snapshot_id)
    _assert_impact(mcp_cli_impact, repo_path=str(repo))
    test_impact = service.analyze_impact(codebase_id, task="investigate missing test mapping for ArchitectureService", snapshot_id=snapshot_id)
    _assert_impact(test_impact, repo_path=str(repo))

    plan = service.create_task_plan(codebase_id, task="修改 MCP CLI capability registration", snapshot_id=snapshot_id)
    _assert_task_plan(plan, repo_path=str(repo))

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/actionability/build", json={"snapshot_id": snapshot_id})
    assert http_build.status_code == 200
    _assert_actionability(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/actionability")
    assert http_read.status_code == 200
    _assert_actionability(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    http_impact = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/impact", json={"task": "add API route behavior", "snapshot_id": snapshot_id})
    assert http_impact.status_code == 200
    _assert_impact(_v2(http_impact.json()), repo_path=str(repo))

    http_plan = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-plan", json={"task": "add API route behavior", "snapshot_id": snapshot_id})
    assert http_plan.status_code == 200
    _assert_task_plan(_v2(http_plan.json()), repo_path=str(repo))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_actionability = asyncio.run(dispatcher.call_tool("knowledge_code_actionability_read", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_actionability(_v2(mcp_actionability), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))
    mcp_plan = asyncio.run(dispatcher.call_tool("knowledge_code_task_plan", {"workspace_id": workspace_id, "codebase_id": codebase_id, "task": "add API route behavior"}))
    _assert_task_plan(_v2(mcp_plan), repo_path=str(repo))

    assert knowledge_main(["code", "coding-agent", "actionability", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_actionability = json.loads(capsys.readouterr().out)
    _assert_actionability(_v2(cli_actionability), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    assert knowledge_main(["code", "coding-agent", "task-plan", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--task", "add API route behavior"]) == 0
    cli_plan = json.loads(capsys.readouterr().out)
    _assert_task_plan(_v2(cli_plan), repo_path=str(repo))
