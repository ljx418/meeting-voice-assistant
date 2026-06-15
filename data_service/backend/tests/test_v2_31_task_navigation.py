from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_tool_registry import all_tool_specs
from data_service.mcp_workspace_runtime import WorkspaceRuntime


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_repo(root: Path) -> None:
    _write(root / "README.md", "# Demo\n\nMCP tool and HTTP API project.\n")
    _write(
        root / "backend/api.py",
        """from fastapi import APIRouter

router = APIRouter()

@router.post('/items')
def create_item():
    return {'ok': True}
""",
    )
    _write(
        root / "backend/mcp_tools.py",
        """TOOL_SPECS = [{'name': 'knowledge_demo_tool'}]

def handle_demo_tool(arguments):
    return {'ok': True, 'arguments': arguments}
""",
    )
    _write(
        root / "backend/cli.py",
        """import argparse

def add_parser(subparsers):
    parser = subparsers.add_parser('demo')
    parser.set_defaults(command='demo')
""",
    )
    _write(root / "tests/test_mcp_tools.py", "def test_demo_tool():\n    assert True\n")


def _make_no_surface_repo(root: Path) -> None:
    _write(root / "README.md", "# Plain Library\n\nNo HTTP, MCP or CLI entrypoints.\n")
    _write(
        root / "lib/core.py",
        """def normalize_name(name: str) -> str:
    return name.strip().lower()

def build_message(name: str) -> str:
    return f"hello {normalize_name(name)}"
""",
    )
    _write(root / "tests/test_core.py", "from lib.core import build_message\n\ndef test_build_message():\n    assert build_message(' Ada ') == 'hello ada'\n")


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200, response.text
    return response.json()["data"]["workspace"]["workspace_id"]


def _bootstrap_codebase(client: TestClient, repo: Path, workspace_id: str) -> tuple[str, str]:
    imported = client.post(
        f"/api/workspaces/{workspace_id}/codebases",
        json={"path": str(repo), "codebase_id": "tasknav"},
    )
    assert imported.status_code == 200, imported.text
    codebase_id = imported.json()["data"]["codebase"]["codebase_id"]

    snapshot = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots", json={})
    assert snapshot.status_code == 200, snapshot.text
    snapshot_id = snapshot.json()["data"]["snapshot"]["snapshot_id"]

    inventory = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory",
        json={"snapshot_id": snapshot_id},
    )
    assert inventory.status_code == 200, inventory.text
    symbols = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols",
        json={"snapshot_id": snapshot_id},
    )
    assert symbols.status_code == 200, symbols.text
    trace = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/build",
        json={"snapshot_id": snapshot_id},
    )
    assert trace.status_code == 200, trace.text
    return codebase_id, snapshot_id


def _assert_no_abs_path(payload: object, *paths: Path) -> None:
    text = json.dumps(payload, ensure_ascii=False)
    assert "/Users/" not in text
    assert "/private/var" not in text
    assert "/var/folders" not in text
    for path in paths:
        assert str(path) not in text


def test_v2_31_task_navigation_http_mcp_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    workspace_root = tmp_path / "managed"
    _make_repo(repo)
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))

    tool_names = {spec["name"] for spec in all_tool_specs()}
    assert "knowledge_code_task_navigation_build" in tool_names
    assert "knowledge_code_task_navigation_prepare" in tool_names
    assert "knowledge_code_task_navigation_query_read" in tool_names

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase97 Task Navigation")
    codebase_id, snapshot_id = _bootstrap_codebase(client, repo, workspace_id)

    built = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation/build",
        json={"snapshot_id": snapshot_id},
    )
    assert built.status_code == 200, built.text
    built_payload = built.json()
    index = built_payload["data"]["task_navigation_index"]
    assert index["snapshot_id"] == snapshot_id
    assert index["summary"]["candidate_count"] > 0
    assert "relationship_graph" not in index
    _assert_no_abs_path(built_payload, repo, workspace_root)

    prepared = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation",
        json={"snapshot_id": snapshot_id, "task": "新增一个 MCP tool 并同步 HTTP API 和 CLI 命令", "limit": 20},
    )
    assert prepared.status_code == 200, prepared.text
    prepared_payload = prepared.json()
    query = prepared_payload["data"]["task_navigation_query"]
    assert query["task_type"] in {"mcp_tool", "api", "cli"}
    assert query["summary"]["matched_count"] > 0
    assert all(item.get("evidence_refs") or item.get("needs_review") for item in query["matched_candidates"])
    task_id = query["task_id"]
    _assert_no_abs_path(prepared_payload, repo, workspace_root)

    read_back = client.get(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation/{task_id}"
    )
    assert read_back.status_code == 200, read_back.text
    assert read_back.json()["data"]["task_navigation_query"]["task_id"] == task_id

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(
        default_workspace=workspace_root / "_default",
        workspace_runtime=runtime,
        build_runtime=BuildRuntime(runtime),
    )
    mcp_payload = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_task_navigation_prepare",
            {
                "workspace_id": workspace_id,
                "codebase_id": codebase_id,
                "snapshot_id": snapshot_id,
                "task": "新增 MCP tool",
                "limit": 10,
            },
        )
    )
    assert mcp_payload["status"] == "ok"
    assert mcp_payload["data"]["task_navigation_query"]["summary"]["matched_count"] > 0
    _assert_no_abs_path(mcp_payload, repo, workspace_root)

    exit_code = knowledge_main(
        [
            "code",
            "coding-agent",
            "task-navigation",
            "--workspace-root",
            str(workspace_root),
            "--workspace-id",
            workspace_id,
            "--codebase-id",
            codebase_id,
            "--snapshot-id",
            snapshot_id,
            "--task",
            "新增 MCP tool",
            "--limit",
            "10",
        ]
    )
    assert exit_code == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload["data"]["task_navigation_query"]["summary"]["matched_count"] > 0
    _assert_no_abs_path(cli_payload, repo, workspace_root)


def test_v2_31_task_navigation_allows_external_repo_without_public_surfaces(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "external_plain_repo"
    workspace_root = tmp_path / "managed"
    _make_no_surface_repo(repo)
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase97 No Surface Navigation")
    codebase_id, snapshot_id = _bootstrap_codebase(client, repo, workspace_id)

    built = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation/build",
        json={"snapshot_id": snapshot_id},
    )
    assert built.status_code == 200, built.text
    index = built.json()["data"]["task_navigation_index"]
    assert index["summary"]["candidate_count"] > 0
    assert index["summary"]["surface_candidate_count"] == 0
    assert index["blockers"]
    assert {item["code"] for item in index["blockers"]} == {"TASK_NAVIGATION_PUBLIC_SURFACES_UNAVAILABLE"}
    _assert_no_abs_path(built.json(), repo, workspace_root)

    relationships = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/relationships/build",
        json={"snapshot_id": snapshot_id},
    )
    assert relationships.status_code == 200, relationships.text
    graph = relationships.json()["data"]["relationship_graph"]
    assert graph["summary"]["relationship_count"] > 0
    blocker_codes = {item["code"] for item in graph["blockers"]}
    assert "RELATIONSHIP_PUBLIC_SURFACES_UNAVAILABLE" in blocker_codes
    assert "RELATIONSHIP_SURFACE_MAPPINGS_UNAVAILABLE" in blocker_codes
    _assert_no_abs_path(relationships.json(), repo, workspace_root)
