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


FORBIDDEN_RELATIONSHIP_TYPES = {
    "full_call_graph",
    "runtime_call_accepted",
    "data_flow",
    "control_flow",
    "runtime_topology",
    "type_inferred",
    "production_runtime_topology",
}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_repo(root: Path) -> None:
    _write(root / "README.md", "# Demo\n\nHTTP, MCP and CLI project.\n")
    _write(
        root / "backend/api.py",
        """from fastapi import APIRouter

router = APIRouter()

def normalize_item(name):
    return name.strip().lower()

@router.post('/items')
def create_item(name: str = 'Demo'):
    return {'name': normalize_item(name)}
""",
    )
    _write(
        root / "backend/mcp_tools.py",
        """TOOL_SPECS = [{'name': 'knowledge_demo_tool'}]

def handle_demo_tool(arguments):
    return {'ok': True, 'arguments': arguments}
""",
    )
    _write(root / "backend/data_service/mcp_tool_registry.py", "TOOL_SPECS = [{'name': 'knowledge_demo_tool'}]\n")
    _write(
        root / "backend/cli.py",
        """import argparse

def add_parser(subparsers):
    parser = subparsers.add_parser('demo')
    parser.set_defaults(command='demo')
""",
    )
    _write(root / "tests/test_api.py", "from backend.api import create_item\n\ndef test_create_item():\n    assert create_item(' X ')['name'] == 'x'\n")


def _bootstrap_codebase(client: TestClient, repo: Path, workspace_id: str) -> tuple[str, str]:
    imported = client.post(
        f"/api/workspaces/{workspace_id}/codebases",
        json={"path": str(repo), "codebase_id": "relations"},
    )
    assert imported.status_code == 200, imported.text
    codebase_id = imported.json()["data"]["codebase"]["codebase_id"]

    snapshot = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots", json={})
    assert snapshot.status_code == 200, snapshot.text
    snapshot_id = snapshot.json()["data"]["snapshot"]["snapshot_id"]
    for suffix in ["inventory", "symbols", "trace/build"]:
        response = client.post(
            f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/{suffix}",
            json={"snapshot_id": snapshot_id},
        )
        assert response.status_code == 200, response.text
    navigation = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/task-navigation/build",
        json={"snapshot_id": snapshot_id},
    )
    assert navigation.status_code == 200, navigation.text
    return codebase_id, snapshot_id


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200, response.text
    return response.json()["data"]["workspace"]["workspace_id"]


def _assert_no_abs_path(payload: object, *paths: Path) -> None:
    text = json.dumps(payload, ensure_ascii=False)
    assert "/Users/" not in text
    assert "/private/var" not in text
    assert "/var/folders" not in text
    for path in paths:
        assert str(path) not in text


def _assert_truth_sample(repo: Path, relationships: list[dict], limit: int = 30) -> None:
    sampled = 0
    accepted_count = 0
    for row in relationships:
        if row.get("truth_status") != "accepted":
            continue
        accepted_count += 1
        assert row.get("evidence_refs"), row
        assert row.get("line_range"), row
        source_path = str((row.get("source_ref") or {}).get("path") or (row.get("target_ref") or {}).get("path") or "")
        assert source_path, row
        if not source_path:
            continue
        path = repo / source_path
        if not path.exists():
            continue
        start, end = row["line_range"]
        lines = path.read_text(encoding="utf-8").splitlines()
        assert 1 <= int(start) <= int(end) <= len(lines)
        sampled += 1
        if sampled >= limit:
            break
    assert accepted_count > 0
    assert sampled > 0


def test_v2_32_lightweight_relationship_graph_http_mcp_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    workspace_root = tmp_path / "managed"
    _make_repo(repo)
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))

    tool_names = {spec["name"] for spec in all_tool_specs()}
    assert "knowledge_code_task_relationships_build" in tool_names
    assert "knowledge_code_task_relationships_read" in tool_names

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase98 Relationships")
    codebase_id, snapshot_id = _bootstrap_codebase(client, repo, workspace_id)

    built = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/relationships/build",
        json={"snapshot_id": snapshot_id},
    )
    assert built.status_code == 200, built.text
    payload = built.json()
    graph = payload["data"]["relationship_graph"]
    assert graph["snapshot_id"] == snapshot_id
    assert graph["summary"]["relationship_count"] > 0
    assert graph["summary"]["forbidden_relationship_count"] == 0
    relationship_types = {row["relationship_type"] for row in graph["relationships"]}
    assert relationship_types.isdisjoint(FORBIDDEN_RELATIONSHIP_TYPES)
    assert "module_imports_module" in relationship_types
    assert "registry_declared" in relationship_types
    assert {"surface_handled_by", "direct_call_ast"} & relationship_types
    raw_graph_path = workspace_root / workspace_id / "assets" / "codebase" / codebase_id / "coding_agent" / "task_navigation" / "relationship_graph.json"
    raw_graph = json.loads(raw_graph_path.read_text(encoding="utf-8"))
    _assert_truth_sample(repo, raw_graph["relationships"])
    _assert_no_abs_path(payload, repo, workspace_root)

    read_back = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/relationships")
    assert read_back.status_code == 200
    assert read_back.json()["data"]["relationship_graph"]["summary"]["relationship_count"] == graph["summary"]["relationship_count"]

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(
        default_workspace=workspace_root / "_default",
        workspace_runtime=runtime,
        build_runtime=BuildRuntime(runtime),
    )
    mcp_payload = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_task_relationships_read",
            {"workspace_id": workspace_id, "codebase_id": codebase_id},
        )
    )
    assert mcp_payload["status"] == "ok"
    assert mcp_payload["data"]["relationship_graph"]["summary"]["forbidden_relationship_count"] == 0
    _assert_no_abs_path(mcp_payload, repo, workspace_root)

    exit_code = knowledge_main(
        [
            "code",
            "coding-agent",
            "relationships",
            "--workspace-root",
            str(workspace_root),
            "--workspace-id",
            workspace_id,
            "--codebase-id",
            codebase_id,
        ]
    )
    assert exit_code == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload["data"]["relationship_graph"]["summary"]["relationship_count"] == graph["summary"]["relationship_count"]
    _assert_no_abs_path(cli_payload, repo, workspace_root)
