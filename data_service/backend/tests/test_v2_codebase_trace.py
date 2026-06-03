import asyncio
import json
from pathlib import Path
from urllib.parse import quote

from fastapi.testclient import TestClient

from app.main import app
from data_service.code_assets.artifacts import evidence_path, mapping_summary_path, mappings_path, read_json, read_jsonl, trace_index_path
from data_service.code_assets.inventory import CodebaseInventoryService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.code_assets.symbols import CodebaseSymbolIndexService
from data_service.code_assets.trace import CodebaseTraceService


FORBIDDEN_PUBLIC_KEYS = {"root_path", "workspace_path", "debug_paths", "path"}


def _assert_no_internal_paths(payload):
    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                assert key not in FORBIDDEN_PUBLIC_KEYS
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(payload)


def _assert_no_path_values(payload, *paths: Path):
    raw = json.dumps(payload, ensure_ascii=False)
    for path in paths:
        assert str(path) not in raw


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
    return asset, snapshot_id


def _truth_sample(repo_root: Path, evidence: list[dict], minimum: int = 10) -> None:
    sample = evidence[: min(minimum, len(evidence))]
    assert len(sample) == min(minimum, len(evidence))
    for item in sample:
        source_path = repo_root / item["path"]
        assert source_path.is_file()
        lines = source_path.read_text(encoding="utf-8").splitlines()
        assert 1 <= item["start_line"] <= len(lines)
        assert 1 <= item["end_line"] <= len(lines)
        snippet = "\n".join(lines[item["start_line"] - 1 : item["end_line"]]).strip()
        assert snippet


def test_v2_codebase_trace_service_real_repo_artifacts_coverage_and_truth_sampling(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))
    asset, snapshot_id = _prepare_real_repo(workspace, "phase5", repo_root)

    sources_manifest = workspace / "lifecycle" / "sources.json"
    before_sources = sources_manifest.read_text(encoding="utf-8") if sources_manifest.exists() else None
    result = CodebaseTraceService(workspace, workspace_id="phase5").build_trace(asset.codebase_id, snapshot_id=snapshot_id)
    after_sources = sources_manifest.read_text(encoding="utf-8") if sources_manifest.exists() else None
    assert after_sources == before_sources

    assert mappings_path(workspace, asset.codebase_id, snapshot_id).exists()
    assert evidence_path(workspace, asset.codebase_id, snapshot_id).exists()
    assert mapping_summary_path(workspace, asset.codebase_id, snapshot_id).exists()
    assert trace_index_path(workspace, asset.codebase_id, snapshot_id).exists()

    mappings = read_jsonl(mappings_path(workspace, asset.codebase_id, snapshot_id))
    evidence = read_jsonl(evidence_path(workspace, asset.codebase_id, snapshot_id))
    summary = read_json(mapping_summary_path(workspace, asset.codebase_id, snapshot_id), {})
    trace_index = read_json(trace_index_path(workspace, asset.codebase_id, snapshot_id), {})
    assert result["summary"]["mapping_count"] == len(mappings) == summary["mapping_count"]
    assert result["summary"]["evidence_count"] == len(evidence) == summary["evidence_count"]
    assert summary["success_mapping_confidence_min"] == 0.8
    assert summary["mapping_coverage_by_surface_type"]["http_api"]["mapped"] > 0
    assert summary["mapping_coverage_by_surface_type"]["mcp_tool"]["mapped"] > 0
    assert summary["mapping_coverage_by_surface_type"]["cli_command"]["mapped"] > 0
    for capability_id in ["source_import", "query", "build", "quality", "graph", "source_trace", "codebase_import"]:
        assert summary["evidence_coverage_by_capability"][capability_id]["covered"], capability_id
        assert summary["golden_checks"][capability_id]["passed"], summary["golden_checks"][capability_id]
    assert "mcp:knowledge_codebase_import" in trace_index["by_surface"]
    assert "codebase_import" in trace_index["by_capability"]
    assert any(item["from_id"] == "mcp:knowledge_codebase_import" and item["unresolved_reason"] is None for item in mappings)
    assert any(item["from_id"] == "http:POST:/api/workspaces/{workspace_id}/codebases" and item["unresolved_reason"] is None for item in mappings)
    assert all(item["confidence"] >= 0.8 for item in mappings if item["unresolved_reason"] is None)
    assert all(item["unresolved_reason"] for item in mappings if item["confidence"] < 0.8)
    _truth_sample(repo_root, evidence)
    _assert_no_path_values(result, repo_root, workspace)

    second = CodebaseTraceService(workspace, workspace_id="phase5").build_trace(asset.codebase_id, snapshot_id=snapshot_id)
    assert {item["mapping_id"] for item in second["mappings"]} == {item["mapping_id"] for item in mappings}
    assert {item["evidence_id"] for item in second["evidence"]} == {item["evidence_id"] for item in evidence}


def test_v2_codebase_trace_http_mcp_cli_real_repo(tmp_path, monkeypatch, capsys):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase5 Trace")
    imported = client.post(f"/api/workspaces/{workspace_id}/codebases", json={"path": str(repo_root)})
    assert imported.status_code == 200
    codebase_id = imported.json()["data"]["codebase"]["codebase_id"]
    snapshot = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots", json={})
    assert snapshot.status_code == 200
    snapshot_id = snapshot.json()["data"]["snapshot"]["snapshot_id"]
    assert client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory", json={}).status_code == 200
    assert client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols", json={}).status_code == 200

    missing = client.get(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/capability/codebase_import",
        params={"snapshot_id": snapshot_id},
    )
    assert missing.status_code == 404
    assert "Trace artifact not found" in missing.json()["detail"]

    built = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/build", json={})
    assert built.status_code == 200
    built_payload = built.json()
    assert built_payload["status"] == "ok"
    assert built_payload["data"]["trace"]["snapshot_id"] == snapshot_id
    assert built_payload["data"]["trace"]["summary"]["golden_checks"]["codebase_import"]["passed"]
    _assert_no_internal_paths(built_payload)
    _assert_no_path_values(built_payload, repo_root, workspace_root)

    surface_id = "mcp:knowledge_codebase_import"
    surface = client.get(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/surface/{quote(surface_id, safe='')}",
        params={"snapshot_id": snapshot_id},
    )
    assert surface.status_code == 200
    assert surface.json()["data"]["trace"]["mappings"]
    assert surface.json()["data"]["trace"]["evidence"]

    capability = client.get(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/capability/codebase_import",
        params={"snapshot_id": snapshot_id},
    )
    assert capability.status_code == 200
    assert "mcp:knowledge_codebase_import" in {item["surface_id"] for item in capability.json()["data"]["trace"]["surfaces"]}
    assert capability.json()["data"]["trace"]["symbols"]

    evidence = client.get(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/evidence",
        params={"snapshot_id": snapshot_id, "limit": 5},
    )
    assert evidence.status_code == 200
    assert evidence.json()["data"]["count"] == 5
    assert all("source_file" in item and "path" not in item for item in evidence.json()["data"]["items"])

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
    mcp_payload = asyncio.run(
        dispatcher.call_tool(
            "knowledge_public_surface_trace",
            {
                "workspace_id": workspace_id,
                "codebase_id": codebase_id,
                "snapshot_id": snapshot_id,
                "surface_id": surface_id,
                "build": False,
            },
        )
    )
    assert mcp_payload["status"] == "ok"
    assert mcp_payload["data"]["trace"]["evidence"]
    _assert_no_path_values(mcp_payload, repo_root, workspace_root)

    assert (
        knowledge_main(
            [
                "code",
                "trace",
                "--workspace-root",
                str(workspace_root),
                "--workspace-id",
                workspace_id,
                "--codebase-id",
                codebase_id,
                "--snapshot-id",
                snapshot_id,
                "--capability",
                "codebase_import",
            ]
        )
        == 0
    )
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload["data"]["trace"]["evidence"]
    assert "mcp:knowledge_codebase_import" in {item["surface_id"] for item in cli_payload["data"]["trace"]["surfaces"]}
    _assert_no_path_values(cli_payload, repo_root, workspace_root)
