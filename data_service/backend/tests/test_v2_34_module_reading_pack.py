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

from backend.tests.test_v2_32_lightweight_relationship_graph import _bootstrap_codebase, _create_workspace, _make_repo


def _assert_no_abs_path(payload: object, *paths: Path) -> None:
    text = json.dumps(payload, ensure_ascii=False)
    assert "/Users/" not in text
    assert "/private/var" not in text
    assert "/var/folders" not in text
    for path in paths:
        assert str(path) not in text


def _assert_reading_pack_payload(payload: dict, *, max_tokens: int) -> str:
    pack = payload["data"]["reading_pack"]
    ledger = payload["data"]["token_ledger"]
    markdown = payload["data"]["markdown"]
    assert pack["schema_version"] == "v2.34"
    assert pack["pack_id"]
    assert ledger["pack_id"] == pack["pack_id"]
    assert ledger["cache_key"].startswith("readcache_")
    assert ledger["max_tokens"] == max_tokens
    assert "Module Reading Pack" in markdown
    assert pack["required_reads"] or pack["blockers"]
    assert pack["token_ledger"]["included_tokens"] == ledger["included_tokens"]
    if ledger["included_tokens"] > max_tokens:
        assert any(blocker["code"] == "TOKEN_BUDGET_TOO_SMALL" for blocker in pack["blockers"])
    for step in pack["recommended_next_steps"]:
        assert step.get("evidence_refs") or step.get("needs_review")
    for item in pack["required_reads"] + pack["optional_reads"]:
        assert item["estimated_tokens"] > 0
        assert item.get("evidence_refs") or item.get("needs_review")
    for item in ledger.get("omitted_items") or []:
        assert item["reason"]
    return str(pack["pack_id"])


def test_v2_34_module_reading_pack_http_mcp_cli_and_token_ledger(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    workspace_root = tmp_path / "managed"
    _make_repo(repo)
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))

    tool_names = {spec["name"] for spec in all_tool_specs()}
    assert "knowledge_code_module_reading_pack" in tool_names
    assert "knowledge_code_module_reading_pack_read" in tool_names

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase100 Reading Pack")
    codebase_id, snapshot_id = _bootstrap_codebase(client, repo, workspace_id)

    built = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/reading-pack",
        json={"snapshot_id": snapshot_id, "task": "新增 HTTP API 并补测试", "max_tokens": 900, "max_items": 40},
    )
    assert built.status_code == 200, built.text
    pack_id = _assert_reading_pack_payload(built.json(), max_tokens=900)
    _assert_no_abs_path(built.json(), repo, workspace_root)

    small_budget = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/reading-pack",
        json={"snapshot_id": snapshot_id, "task": "新增 HTTP API 并补测试", "max_tokens": 100, "max_items": 40},
    )
    assert small_budget.status_code == 200, small_budget.text
    _assert_reading_pack_payload(small_budget.json(), max_tokens=100)

    read_back = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/reading-pack/{pack_id}")
    assert read_back.status_code == 200, read_back.text
    assert read_back.json()["data"]["reading_pack"]["pack_id"] == pack_id

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(
        default_workspace=workspace_root / "_default",
        workspace_runtime=runtime,
        build_runtime=BuildRuntime(runtime),
    )
    mcp_payload = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_module_reading_pack_read",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "pack_id": pack_id},
        )
    )
    assert mcp_payload["status"] == "ok"
    assert mcp_payload["data"]["reading_pack"]["pack_id"] == pack_id
    _assert_no_abs_path(mcp_payload, repo, workspace_root)

    exit_code = knowledge_main(
        [
            "code",
            "coding-agent",
            "reading-pack-read",
            "--workspace-root",
            str(workspace_root),
            "--workspace-id",
            workspace_id,
            "--codebase-id",
            codebase_id,
            "--pack-id",
            pack_id,
        ]
    )
    assert exit_code == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload["data"]["reading_pack"]["pack_id"] == pack_id
    _assert_no_abs_path(cli_payload, repo, workspace_root)
