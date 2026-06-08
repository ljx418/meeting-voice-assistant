from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.coding_agent.service import CodingAgentActionabilityService
from data_service.code_assets.coding_agent_v2_16.persistence import (
    runtime_profile_run_path,
    runtime_profiles_path,
)
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _profiles(payload: dict) -> dict:
    if "data" in payload and "runtime_profiles" in payload["data"]:
        return payload["data"]["runtime_profiles"]
    return payload


def _profile_run(payload: dict) -> dict:
    if "data" in payload and "runtime_profile_run" in payload["data"]:
        return payload["data"]["runtime_profile_run"]
    return payload


def _assert_profiles(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: str, workspace_path: str) -> dict:
    profiles = _profiles(payload)
    serialized = json.dumps(profiles, ensure_ascii=False)
    assert profiles["schema_version"] == "v2.16"
    assert profiles["workspace_id"] == workspace_id
    assert profiles["codebase_id"] == codebase_id
    assert profiles["snapshot_id"] == snapshot_id
    assert profiles["policy"]["default"] == "deny"
    assert profiles["policy"]["requires_profile_id"] is True
    assert profiles["policy"]["writes_source"] is False
    assert profiles["summary"]["profile_count"] >= 1
    assert profiles["profiles"]
    assert str(repo) not in serialized
    assert str(workspace_path) not in serialized
    for profile in profiles["profiles"]:
        assert profile["profile_id"]
        assert profile["command_id"]
        assert profile["writes_source"] is False
        assert profile["allowed_args_policy"]["user_args_allowed"] is False
        if profile.get("command_template"):
            assert not profile["command_template"].startswith("/")
            assert "/Users/" not in profile["command_template"]
    return profiles


def _assert_profile_run(payload: dict, *, repo: str, workspace_path: str, expected_status: str | None = None) -> dict:
    run = _profile_run(payload)
    serialized = json.dumps(run, ensure_ascii=False)
    assert run["schema_version"] == "v2.16"
    assert run["status"] in {"passed", "failed", "timeout", "blocked"}
    if expected_status:
        assert run["status"] == expected_status
    assert str(repo) not in serialized
    assert str(workspace_path) not in serialized
    assert run["logs"]["redacted"] is True
    return run


def test_v216_runtime_profiles_service_artifacts(tmp_path, monkeypatch):
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = CodingAgentActionabilityService(workspace, workspace_id=workspace_id)

    profiles = _assert_profiles(service.build_runtime_profiles(codebase_id, snapshot_id=snapshot_id), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))
    assert runtime_profiles_path(workspace, codebase_id).exists()

    blocked = _assert_profile_run(service.run_runtime_profile(codebase_id, profile_id="not-registered", snapshot_id=snapshot_id), repo=str(repo), workspace_path=str(workspace), expected_status="blocked")
    assert blocked["error"]["code"] == "RUNTIME_PROFILE_NOT_REGISTERED"
    assert not blocked["artifact_refs"]

    run = _assert_profile_run(service.run_runtime_profile(codebase_id, profile_id=profiles["profiles"][0]["profile_id"], snapshot_id=snapshot_id), repo=str(repo), workspace_path=str(workspace))
    assert run["profile_id"] == profiles["profiles"][0]["profile_id"]
    assert runtime_profile_run_path(workspace, codebase_id, run["profile_run_id"]).exists()


def test_v216_runtime_profiles_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)

    http_build = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/profiles/build",
        json={"snapshot_id": snapshot_id},
    )
    assert http_build.status_code == 200
    http_profiles = _assert_profiles(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))
    profile_id = http_profiles["profiles"][0]["profile_id"]

    http_run = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/profile-runs",
        json={"profile_id": profile_id, "snapshot_id": snapshot_id},
    )
    assert http_run.status_code == 200
    http_profile_run = _assert_profile_run(_v2(http_run.json()), repo=str(repo), workspace_path=str(workspace))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_profiles_payload = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_runtime_profiles_build",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id},
        )
    )
    mcp_profiles = _assert_profiles(_v2(mcp_profiles_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    assert knowledge_main(["code", "coding-agent", "runtime-profiles", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_profiles = _assert_profiles(_v2(json.loads(capsys.readouterr().out)), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    assert http_profiles["summary"] == mcp_profiles["summary"] == cli_profiles["summary"]
    assert [item["profile_id"] for item in http_profiles["profiles"]] == [item["profile_id"] for item in mcp_profiles["profiles"]] == [item["profile_id"] for item in cli_profiles["profiles"]]

    assert knowledge_main(["code", "coding-agent", "runtime-profile-result", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--profile-run-id", http_profile_run["profile_run_id"]]) == 0
    cli_run = _assert_profile_run(_v2(json.loads(capsys.readouterr().out)), repo=str(repo), workspace_path=str(workspace))
    assert cli_run["profile_run_id"] == http_profile_run["profile_run_id"]
