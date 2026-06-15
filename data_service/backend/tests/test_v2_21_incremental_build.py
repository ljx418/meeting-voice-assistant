from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.platform.incremental import PlatformIncrementalService
from data_service.code_assets.platform.persistence import cache_decisions_path, incremental_build_plan_path, scan_profile_path
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _incremental(payload: dict) -> dict:
    if "data" in payload and "incremental_build" in payload["data"]:
        return payload["data"]["incremental_build"]
    if "plan" in payload and "cache_decisions" in payload:
        return {
            "schema_version": "v2.21",
            "artifact_type": "incremental_build_bundle",
            "plan": payload["plan"],
            "cache_decisions": payload["cache_decisions"],
            "scan_profile": payload["scan_profile"],
            "artifact_refs": payload.get("artifact_refs", []),
        }
    return payload


def _second_snapshot(workspace, workspace_id: str, codebase_id: str, repo) -> str:
    changed = repo / "backend" / "app" / "main.py"
    changed.write_text("print('changed for v2.21 incremental plan')\n", encoding="utf-8")
    return CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(codebase_id)["snapshot"]["snapshot_id"]


def _assert_incremental(payload: dict, *, workspace_id: str, codebase_id: str, from_snapshot_id: str, to_snapshot_id: str, changed_path: str, repo: str, workspace_path: str) -> dict:
    bundle = _incremental(payload)
    serialized = json.dumps(bundle, ensure_ascii=False)
    assert bundle["schema_version"] == "v2.21"
    assert bundle["artifact_type"] == "incremental_build_bundle"
    plan = bundle["plan"]
    decisions = bundle["cache_decisions"]
    profile = bundle["scan_profile"]
    assert plan["schema_version"] == "v2.21"
    assert plan["artifact_type"] == "incremental_build_plan"
    assert plan["workspace_id"] == workspace_id
    assert plan["codebase_id"] == codebase_id
    assert plan["from_snapshot_id"] == from_snapshot_id
    assert plan["to_snapshot_id"] == to_snapshot_id
    assert plan["summary"]["changed_file_count"] >= 1
    observed_paths = {
        row.get("path") or row.get("source_file") or (row.get("debug_paths") or {}).get("path")
        for row in plan["changed_files"]
    }
    assert changed_path in observed_paths
    assert decisions
    assert all(item.get("reason") for item in decisions)
    assert any(item["decision"] in {"refresh", "invalidate", "full_rebuild_required"} for item in decisions)
    assert not all(item["decision"] == "reuse" for item in decisions)
    assert profile["changed_file_count"] == plan["summary"]["changed_file_count"]
    assert profile["budget"]["status"] in {"within_budget", "over_budget"}
    assert bundle["artifact_refs"]
    assert repo not in serialized
    assert workspace_path not in serialized
    return bundle


def test_v221_incremental_plan_service(tmp_path, monkeypatch):
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    second_snapshot_id = _second_snapshot(workspace, workspace_id, codebase_id, repo)
    service = PlatformIncrementalService(workspace, workspace_id=workspace_id)

    bundle = _assert_incremental(
        service.build_incremental_plan(codebase_id, from_snapshot_id=snapshot_id, to_snapshot_id=second_snapshot_id),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        from_snapshot_id=snapshot_id,
        to_snapshot_id=second_snapshot_id,
        changed_path="backend/app/main.py",
        repo=str(repo),
        workspace_path=str(workspace),
    )
    assert incremental_build_plan_path(workspace, codebase_id).exists()
    assert cache_decisions_path(workspace, codebase_id).exists()
    assert scan_profile_path(workspace, codebase_id).exists()
    readback = _assert_incremental(
        service.read_incremental_plan(codebase_id),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        from_snapshot_id=snapshot_id,
        to_snapshot_id=second_snapshot_id,
        changed_path="backend/app/main.py",
        repo=str(repo),
        workspace_path=str(workspace),
    )
    assert bundle["plan"]["summary"] == readback["plan"]["summary"]


def test_v221_incremental_plan_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    second_snapshot_id = _second_snapshot(workspace, workspace_id, codebase_id, repo)

    http_build = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/incremental/build",
        json={"from_snapshot_id": snapshot_id, "to_snapshot_id": second_snapshot_id},
    )
    assert http_build.status_code == 200
    http_incremental = _assert_incremental(
        _v2(http_build.json()),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        from_snapshot_id=snapshot_id,
        to_snapshot_id=second_snapshot_id,
        changed_path="backend/app/main.py",
        repo=str(repo),
        workspace_path=str(workspace),
    )

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/incremental")
    assert http_read.status_code == 200
    _assert_incremental(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, from_snapshot_id=snapshot_id, to_snapshot_id=second_snapshot_id, changed_path="backend/app/main.py", repo=str(repo), workspace_path=str(workspace))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_platform_incremental_build",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "from_snapshot_id": snapshot_id, "to_snapshot_id": second_snapshot_id},
        )
    )
    mcp_incremental = _assert_incremental(
        _v2(mcp_build),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        from_snapshot_id=snapshot_id,
        to_snapshot_id=second_snapshot_id,
        changed_path="backend/app/main.py",
        repo=str(repo),
        workspace_path=str(workspace),
    )

    assert knowledge_main(
        [
            "code",
            "platform",
            "incremental",
            "--workspace-root",
            str(workspace_root),
            "--workspace-id",
            workspace_id,
            "--codebase-id",
            codebase_id,
        ]
    ) == 0
    cli_incremental = _assert_incremental(
        _v2(json.loads(capsys.readouterr().out)),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        from_snapshot_id=snapshot_id,
        to_snapshot_id=second_snapshot_id,
        changed_path="backend/app/main.py",
        repo=str(repo),
        workspace_path=str(workspace),
    )

    assert http_incremental["plan"]["summary"] == mcp_incremental["plan"]["summary"]
    assert http_incremental["plan"]["summary"] == cli_incremental["plan"]["summary"]
    assert len(http_incremental["cache_decisions"]) == len(cli_incremental["cache_decisions"])
