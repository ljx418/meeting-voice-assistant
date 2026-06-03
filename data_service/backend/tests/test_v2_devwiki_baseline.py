import asyncio
import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.code_assets.devwiki.model import REQUIRED_PAGE_SLUGS
from data_service.code_assets.devwiki.service import CodebaseDevWikiService
from data_service.code_assets.inventory import CodebaseInventoryService
from data_service.code_assets.overview import CodebaseOverviewService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.code_assets.symbols import CodebaseSymbolIndexService
from data_service.code_assets.trace import CodebaseTraceService


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


def _hashes(paths: list[Path]) -> dict[str, str]:
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def _v20_artifact_paths(workspace: Path, codebase_id: str, snapshot_id: str) -> list[Path]:
    base = workspace / "assets" / "codebase" / codebase_id
    snap = base / "snapshots" / snapshot_id
    return [
        snap / "snapshot.json",
        snap / "files.jsonl",
        snap / "inventory_summary.json",
        snap / "surfaces.jsonl",
        snap / "capabilities.jsonl",
        snap / "symbol_summary.json",
        snap / "symbols.jsonl",
        snap / "imports.jsonl",
        snap / "mapping_summary.json",
        snap / "evidence.jsonl",
        base / "overview.json",
    ]


def _assert_no_path_values(payloads: list[dict], *paths: Path):
    raw = json.dumps(payloads, ensure_ascii=False)
    for path in paths:
        assert str(path) not in raw


def _markdown_section_count(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.startswith("## "))


def test_v2_devwiki_build_read_http_mcp_cli_converge_real_repo(tmp_path, monkeypatch, capsys):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase8 DevWiki")
    workspace = workspace_root / workspace_id
    codebase_id, snapshot_id = _prepare_real_repo(workspace, workspace_id, repo_root)
    before_hashes = _hashes(_v20_artifact_paths(workspace, codebase_id, snapshot_id))

    service = CodebaseDevWikiService(workspace, workspace_id=workspace_id)
    result = service.build_devwiki(codebase_id, snapshot_id=snapshot_id)
    after_hashes = _hashes(_v20_artifact_paths(workspace, codebase_id, snapshot_id))
    assert before_hashes == after_hashes
    assert result["index"]["page_count"] == len(REQUIRED_PAGE_SLUGS)
    assert not (workspace / "lifecycle" / "sources.json").exists()

    devwiki_root = workspace / "assets" / "codebase" / codebase_id / "devwiki"
    assert (devwiki_root / "index.json").exists()
    for slug in REQUIRED_PAGE_SLUGS:
        json_path = devwiki_root / "pages" / f"{slug}.json"
        md_path = devwiki_root / "pages" / f"{slug}.md"
        assert json_path.exists()
        assert md_path.exists()
        page = json.loads(json_path.read_text(encoding="utf-8"))
        markdown = md_path.read_text(encoding="utf-8")
        assert page["snapshot_id"] == snapshot_id
        assert page["sections"]
        assert _markdown_section_count(markdown) == len(page["sections"])
        assert page["evidence"] or page["needs_review"]
        for section in page["sections"]:
            assert section["generated_from"]
            assert "source_artifact_refs" in section
            assert section["evidence"] or section["needs_review"]

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

    http_build = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/build",
        json={"snapshot_id": snapshot_id},
    ).json()
    http_page = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/pages/project-overview").json()
    mcp_page = asyncio.run(
        dispatcher.call_tool(
            "knowledge_devwiki_read",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "page_slug": "project-overview"},
        )
    )
    assert (
        knowledge_main(
            [
                "code",
                "devwiki",
                "read",
                "--workspace-root",
                str(workspace_root),
                "--workspace-id",
                workspace_id,
                "--codebase-id",
                codebase_id,
                "--page-slug",
                "project-overview",
            ]
        )
        == 0
    )
    cli_page = json.loads(capsys.readouterr().out)

    assert _v2(http_build)["ok"] is True
    http_v2 = _v2(http_page)
    mcp_v2 = _v2(mcp_page)
    cli_v2 = _v2(cli_page)
    assert {http_v2["ok"], mcp_v2["ok"], cli_v2["ok"]} == {True}
    assert {http_v2["snapshot_id"], mcp_v2["snapshot_id"], cli_v2["snapshot_id"]} == {snapshot_id}
    assert {
        http_v2["data"]["page"]["page_id"],
        mcp_v2["data"]["page"]["page_id"],
        cli_v2["data"]["page"]["page_id"],
    } == {"devwiki:project-overview"}
    assert {
        len(http_v2["data"]["page"]["evidence"]),
        len(mcp_v2["data"]["page"]["evidence"]),
        len(cli_v2["data"]["page"]["evidence"]),
    }
    _assert_no_path_values([http_build, http_page, mcp_page, cli_page], repo_root, workspace_root)


def test_v2_devwiki_missing_v20_artifact_returns_structured_error(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo_root))

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase8 DevWiki Missing")
    workspace = workspace_root / workspace_id
    codebase_id, snapshot_id = _prepare_real_repo(workspace, workspace_id, repo_root)
    (workspace / "assets" / "codebase" / codebase_id / "overview.json").unlink()

    response = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/devwiki/build",
        json={"snapshot_id": snapshot_id},
    )
    assert response.status_code == 404
    payload = response.json()
    assert payload["v2"]["ok"] is False
    assert payload["v2"]["error"]["code"] == "V20_ARTIFACT_MISSING"
