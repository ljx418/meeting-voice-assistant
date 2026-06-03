import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.code_assets.context.service import CodebaseAgentContextService
from data_service.code_assets.inventory import CodebaseInventoryService
from data_service.code_assets.overview import CodebaseOverviewService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.code_assets.symbols import CodebaseSymbolIndexService
from data_service.code_assets.trace import CodebaseTraceService


PROJECT_READING_TASK = "请阅读并汇总当前项目的定位、入口、公开能力、核心模块、存储结构和证据。"
DEVELOPMENT_TASK = "新增一个 codebase MCP tool，并同步 HTTP API、CLI 和测试。"


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _prepare_real_repo(workspace: Path, workspace_id: str, repo_root: Path):
    registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
    asset = registry.import_codebase(path=str(repo_root))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    CodebaseInventoryService(workspace, workspace_id=workspace_id).build_inventory(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseSymbolIndexService(workspace, workspace_id=workspace_id).build_symbol_index(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseTraceService(workspace, workspace_id=workspace_id).build_trace(asset.codebase_id, snapshot_id=snapshot_id)
    CodebaseOverviewService(workspace, workspace_id=workspace_id).build_overview(asset.codebase_id, snapshot_id=snapshot_id)
    return asset.codebase_id, snapshot_id


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_path_values(payloads: list[dict], *paths: Path):
    raw = json.dumps(payloads, ensure_ascii=False)
    for path in paths:
        assert str(path) not in raw


def _assert_claims_are_evidence_backed(items: list[dict]):
    assert items
    for item in items:
        assert item.get("evidence") or item.get("needs_review") is True


def test_v2_agent_context_pack_project_brief_and_task_context_real_repo(tmp_path, monkeypatch, capsys):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase7 Context")
    workspace = workspace_root / workspace_id
    codebase_id, snapshot_id = _prepare_real_repo(workspace, workspace_id, repo_root)

    service = CodebaseAgentContextService(workspace, workspace_id=workspace_id)
    direct_project = service.create_pack(
        codebase_id,
        snapshot_id=snapshot_id,
        mode="project_brief",
        task=PROJECT_READING_TASK,
        output_format="json",
        max_tokens=16000,
    )
    assert (workspace / "assets" / "codebase" / codebase_id / "agent_context" / f"{direct_project['pack_id']}.json").exists()
    assert not (workspace / "lifecycle" / "sources.json").exists()
    assert direct_project["mode"] == "project_brief"
    assert direct_project["project_summary"]["project_one_liner"]
    assert direct_project["relevant_capabilities"]
    assert direct_project["relevant_public_surface"]
    assert direct_project["relevant_files"]
    assert direct_project["relevant_symbols"]
    _assert_claims_are_evidence_backed(direct_project["implementation_guidance"])
    _assert_claims_are_evidence_backed(direct_project["risks"])
    _assert_claims_are_evidence_backed(direct_project["suggested_tests"])
    _assert_claims_are_evidence_backed(direct_project["recommended_next_steps"])

    http_task = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-pack",
        json={
            "snapshot_id": snapshot_id,
            "mode": "task_context",
            "task": DEVELOPMENT_TASK,
            "format": "markdown",
            "max_tokens": 16000,
        },
    ).json()
    task_pack = _v2(http_task)["data"]["context_pack"]
    assert task_pack["mode"] == "task_context"
    assert task_pack["format"] == "markdown"
    assert "# Agent Context Pack" in task_pack["content"]
    assert task_pack["task_interpretation"]["task"] == DEVELOPMENT_TASK
    assert task_pack["pack_id"] != direct_project["pack_id"]
    assert task_pack["relevant_public_surface"] != direct_project["relevant_public_surface"] or task_pack["task_interpretation"] != direct_project["task_interpretation"]

    readback = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-packs/{task_pack['pack_id']}").json()
    assert _v2(readback)["data"]["context_pack"]["pack_id"] == task_pack["pack_id"]

    from data_service.__main__ import knowledge_main
    from data_service.mcp_build_runtime import BuildRuntime
    from data_service.mcp_dispatcher import MCPToolDispatcher
    from data_service.mcp_workspace_runtime import WorkspaceRuntime

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(
        default_workspace=workspace_root / "_default",
        workspace_runtime=runtime,
        build_runtime=BuildRuntime(runtime),
    )
    mcp_project = asyncio.run(
        dispatcher.call_tool(
            "knowledge_agent_context_pack",
            {
                "workspace_id": workspace_id,
                "codebase_id": codebase_id,
                "snapshot_id": snapshot_id,
                "mode": "project_brief",
                "task": PROJECT_READING_TASK,
                "format": "json",
            },
        )
    )
    assert _v2(mcp_project)["data"]["context_pack"]["snapshot_id"] == snapshot_id

    assert (
        knowledge_main(
            [
                "code",
                "context-pack",
                "--workspace-root",
                str(workspace_root),
                "--workspace-id",
                workspace_id,
                "--codebase-id",
                codebase_id,
                "--snapshot-id",
                snapshot_id,
                "--mode",
                "task_context",
                "--task",
                DEVELOPMENT_TASK,
                "--format",
                "json",
            ]
        )
        == 0
    )
    cli_payload = json.loads(capsys.readouterr().out)
    assert _v2(cli_payload)["data"]["context_pack"]["mode"] == "task_context"
    _assert_no_path_values([http_task, readback, mcp_project, cli_payload], repo_root, workspace_root)


def test_v2_agent_context_pack_token_budget_preserves_evidence_rules(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase7 Budget")
    workspace = workspace_root / workspace_id
    codebase_id, snapshot_id = _prepare_real_repo(workspace, workspace_id, repo_root)

    response = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-pack",
        json={
            "snapshot_id": snapshot_id,
            "mode": "task_context",
            "task": DEVELOPMENT_TASK,
            "format": "json",
            "max_tokens": 256,
        },
    )
    assert response.status_code == 200
    pack = _v2(response.json())["data"]["context_pack"]
    assert pack["omitted_items"]
    _assert_claims_are_evidence_backed(pack["implementation_guidance"])
    _assert_claims_are_evidence_backed(pack["risks"])
    _assert_claims_are_evidence_backed(pack["suggested_tests"])
