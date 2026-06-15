import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.architecture.workflow_runtime_v2 import entrypoint_candidates_path, runtime_adapter_candidates_path, workflow_candidates_path, workflow_runtime_summary_path
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _write_repo(repo: Path) -> None:
    files = {
        ".github/workflows/ci.yml": "name: ci\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n",
        "Dockerfile": "FROM python:3.11-slim\nCMD [\"python\", \"backend/cli.py\"]\n",
        "docker-compose.yml": "services:\n  api:\n    build: .\n",
        "package.json": json.dumps({"scripts": {"dev": "vite --host 0.0.0.0", "test": "vitest"}}),
        "backend/cli.py": """import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run')
    return parser.parse_args()


if __name__ == "__main__":
    main()
""",
        "backend/runtime_adapter.py": """class WorkflowRuntimeAdapter:
    pass


def register_adapter(adapter):
    return adapter
""",
        "backend/agent_registry.py": """AGENTS = []


def register_agent(agent):
    AGENTS.append(agent)
""",
        "backend/console_app.py": """from rich.console import Console

console = Console()
""",
        "backend/tui_app.py": """import curses

def run_tui(stdscr):
    return stdscr
""",
        "README.md": "# Workflow Runtime Fixture\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V41 Workflow Runtime")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]
    snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(asset.codebase_id)["snapshot"]["snapshot_id"]
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, snapshot_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _all_candidates(payload: dict) -> list[dict]:
    return [*payload["workflow_candidates"], *payload["runtime_adapter_candidates"], *payload["entrypoint_candidates"]]


def _assert_no_absolute_path(payload: dict, repo: Path, workspace_root: Path) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in raw
    assert str(workspace_root) not in raw


def _assert_candidate_lines(repo: Path, candidates: list[dict]) -> None:
    assert candidates
    for item in candidates:
        assert not Path(item["path"]).is_absolute()
        assert item["evidence_refs"]
        start, end = item["line_range"]
        lines = (repo / item["path"]).read_text(encoding="utf-8", errors="replace").splitlines()
        assert 1 <= start <= end <= max(1, len(lines))
        assert "\n".join(lines[start - 1 : end]).strip()
        assert item["topology_claim"] is False
        if item["determinism"] == "heuristic":
            assert item["needs_review"]


def _assert_workflow_runtime_payload(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: Path, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.41_workflow_runtime"
    assert payload["workspace_id"] == workspace_id
    assert payload["codebase_id"] == codebase_id
    assert payload["snapshot_id"] == snapshot_id
    assert payload["summary"]["workflow_candidate_count"] >= 3
    assert payload["summary"]["runtime_adapter_candidate_count"] >= 2
    assert payload["summary"]["entrypoint_candidate_count"] >= 4
    candidates = _all_candidates(payload)
    types = {item["candidate_type"] for item in candidates}
    assert "workflow_manifest" in types
    assert "pipeline_config" in types
    assert "runtime_adapter" in types
    assert "agent_registry" in types
    assert "cli_entrypoint" in types
    assert "tui_entrypoint" in types
    assert "console_entrypoint" in types
    assert all("topology" not in item["candidate_type"] for item in candidates)
    _assert_candidate_lines(repo, candidates)
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v41_workflow_runtime_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)

    payload = service.build_workflow_runtime_candidates(codebase_id, snapshot_id=snapshot_id)
    _assert_workflow_runtime_payload(payload, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo, workspace_root=workspace_root)
    assert workflow_candidates_path(workspace, codebase_id).exists()
    assert runtime_adapter_candidates_path(workspace, codebase_id).exists()
    assert entrypoint_candidates_path(workspace, codebase_id).exists()
    assert workflow_runtime_summary_path(workspace, codebase_id).exists()

    read_payload = service.read_workflow_runtime_candidates(codebase_id)
    _assert_workflow_runtime_payload(read_payload, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=repo, workspace_root=workspace_root)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/workflow-runtime/build", json={"snapshot_id": snapshot_id})
    assert http_build.status_code == 200
    build_data = _v2(http_build.json())["data"]["workflow_runtime"]
    assert build_data["summary"]["workflow_candidate_count"] == len(payload["workflow_candidates"])
    assert build_data["workflow_candidates"]["total"] == len(payload["workflow_candidates"])
    _assert_no_absolute_path(build_data, repo, workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/workflow-runtime")
    assert http_read.status_code == 200
    read_data = _v2(http_read.json())["data"]["workflow_runtime"]
    assert read_data["runtime_adapter_candidates"]["total"] == len(payload["runtime_adapter_candidates"])
    assert read_data["entrypoint_candidates"]["total"] == len(payload["entrypoint_candidates"])
    assert read_data["artifact_refs"]
    _assert_no_absolute_path(read_data, repo, workspace_root)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_workflow_runtime_build", {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id}))
    assert _v2(mcp_build)["data"]["workflow_runtime"]["summary"]["entrypoint_candidate_count"] == len(payload["entrypoint_candidates"])
    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_workflow_runtime", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_read)["data"]["workflow_runtime"]["summary"]["runtime_adapter_candidate_count"] == len(payload["runtime_adapter_candidates"])

    assert knowledge_main(["code", "architecture", "workflow-runtime", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    assert _v2(cli_read)["data"]["workflow_runtime"]["summary"]["workflow_candidate_count"] == len(payload["workflow_candidates"])
    assert knowledge_main(["code", "architecture", "workflow-runtime-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--snapshot-id", snapshot_id]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    assert _v2(cli_build)["data"]["workflow_runtime"]["summary"]["entrypoint_candidate_count"] == len(payload["entrypoint_candidates"])


def test_v41_workflow_runtime_missing_returns_structured_error(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text("print('ok')\n", encoding="utf-8")
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V41 Missing")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]

    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{asset.codebase_id}/architecture/workflow-runtime")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_WORKFLOW_RUNTIME_NOT_BUILT"
