from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path

from data_service.__main__ import knowledge_main
from data_service.code_assets.coding_agent.service import CodingAgentActionabilityService
from data_service.code_assets.coding_agent_v2_16.persistence import patch_preview_diff_path, patch_preview_path
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _preview(payload: dict) -> dict:
    if "data" in payload and "patch_preview" in payload["data"]:
        return payload["data"]["patch_preview"]
    return payload


def _apply(payload: dict) -> dict:
    if "data" in payload and "patch_apply" in payload["data"]:
        return payload["data"]["patch_apply"]
    return payload


def _repo_hash(repo: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(repo.rglob("*")):
        if path.is_file() and ".git" not in path.parts:
            digest.update(str(path.relative_to(repo)).encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _public_path(item: dict) -> str:
    return str(item.get("path") or item.get("debug_paths", {}).get("path") or "")


def _assert_preview(payload: dict, *, workspace_id: str, codebase_id: str, repo: str, workspace_path: str) -> dict:
    preview = _preview(payload)
    serialized = json.dumps(preview, ensure_ascii=False)
    assert preview["schema_version"] == "v2.16"
    assert preview["workspace_id"] == workspace_id
    assert preview["codebase_id"] == codebase_id
    assert preview["mutates_source"] is False
    assert preview["approval_state"]["status"] == "approval_required"
    assert preview["summary"]["diff_available"] is True
    assert preview["rollback_plan"]
    assert preview["diff_ref"]
    for item in preview["target_hashes_before"]:
        assert _public_path(item)
        assert not _public_path(item).startswith("/")
    for step in preview["rollback_plan"]:
        assert _public_path(step)
        assert not _public_path(step).startswith("/")
    assert str(repo) not in serialized
    assert str(workspace_path) not in serialized
    return preview


def test_v216_patch_sandbox_preview_is_read_only(tmp_path, monkeypatch):
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    before = _repo_hash(repo)
    service = CodingAgentActionabilityService(workspace, workspace_id=workspace_id)

    preview = _assert_preview(service.create_patch_preview(codebase_id, task="add API route behavior", snapshot_id=snapshot_id), workspace_id=workspace_id, codebase_id=codebase_id, repo=str(repo), workspace_path=str(workspace))
    assert patch_preview_path(workspace, codebase_id, preview["preview_id"]).exists()
    assert patch_preview_diff_path(workspace, codebase_id, preview["preview_id"]).exists()
    assert _repo_hash(repo) == before

    apply_result = service.apply_patch_preview(codebase_id, preview["preview_id"])
    assert _apply(apply_result)["status"] == "blocked"
    assert _apply(apply_result)["error"]["code"] == "PATCH_APPLY_REQUIRES_HUMAN_APPROVAL"
    assert _repo_hash(repo) == before


def test_v216_patch_sandbox_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    before = _repo_hash(repo)

    http_create = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-sandbox/previews",
        json={"task": "add API route behavior", "snapshot_id": snapshot_id},
    )
    assert http_create.status_code == 200
    http_preview = _assert_preview(_v2(http_create.json()), workspace_id=workspace_id, codebase_id=codebase_id, repo=str(repo), workspace_path=str(workspace))

    http_apply = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-sandbox/previews/{http_preview['preview_id']}/apply")
    assert http_apply.status_code == 200
    assert _apply(_v2(http_apply.json()))["status"] == "blocked"

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_read = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_patch_preview_read",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "preview_id": http_preview["preview_id"]},
        )
    )
    mcp_preview = _assert_preview(_v2(mcp_read), workspace_id=workspace_id, codebase_id=codebase_id, repo=str(repo), workspace_path=str(workspace))

    assert knowledge_main(["code", "coding-agent", "patch-preview-read", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--preview-id", http_preview["preview_id"]]) == 0
    cli_preview = _assert_preview(_v2(json.loads(capsys.readouterr().out)), workspace_id=workspace_id, codebase_id=codebase_id, repo=str(repo), workspace_path=str(workspace))

    assert http_preview["preview_id"] == mcp_preview["preview_id"] == cli_preview["preview_id"]
    assert _repo_hash(repo) == before
