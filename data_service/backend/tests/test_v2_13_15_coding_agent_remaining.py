from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.coding_agent.persistence import (
    context_export_path,
    fingerprint_index_path,
    runtime_log_path,
    runtime_registry_path,
    runtime_run_path,
    snapshot_diff_path,
    workbench_html_path,
    workbench_mermaid_path,
    workbench_payload_path,
)
from data_service.code_assets.coding_agent.service import CodingAgentActionabilityService
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _runtime(payload: dict) -> dict:
    if "data" in payload and "runtime_commands" in payload["data"]:
        return payload["data"]["runtime_commands"]
    return payload


def _runtime_run(payload: dict) -> dict:
    if "data" in payload and "runtime_run" in payload["data"]:
        return payload["data"]["runtime_run"]
    return payload


def _diff(payload: dict) -> dict:
    if "data" in payload and "incremental_diff" in payload["data"]:
        return payload["data"]["incremental_diff"]
    return payload


def _workbench(payload: dict) -> dict:
    if "data" in payload and "workbench" in payload["data"]:
        return payload["data"]["workbench"]
    return payload


def _export(payload: dict) -> dict:
    if "data" in payload and "context_export" in payload["data"]:
        return payload["data"]["context_export"]
    return payload


def _assert_runtime_registry(payload: dict, *, repo: str) -> dict:
    registry = _runtime(payload)
    serialized = json.dumps(registry, ensure_ascii=False)
    assert registry["schema_version"] == "v2.13"
    assert registry["policy"]["default"] == "deny"
    assert registry["summary"]["allowlisted_command_count"] >= 1
    assert registry["allowlisted_commands"]
    assert str(repo) not in serialized
    for command in registry["allowlisted_commands"]:
        assert command["command_id"]
        assert command["command_type"] in {"pytest", "python_ast_check"}
        assert command["evidence_refs"]
    return registry


def _assert_runtime_run(payload: dict, *, repo: str, expected_status: str = "passed") -> dict:
    run = _runtime_run(payload)
    serialized = json.dumps(run, ensure_ascii=False)
    assert run["schema_version"] == "v2.13"
    assert run["status"] == expected_status
    assert str(repo) not in serialized
    assert run["logs"]["redacted"] is True
    if expected_status == "passed":
        assert run["exit_code"] == 0
        assert run["artifact_refs"]
    else:
        assert run["error"]["code"] == "RUNTIME_COMMAND_NOT_ALLOWLISTED"
    return run


def _assert_diff(payload: dict, *, changed_path: str, repo: str) -> dict:
    diff = _diff(payload)
    serialized = json.dumps(diff, ensure_ascii=False)
    assert diff["schema_version"] == "v2.14"
    assert diff["diff_id"]
    assert diff["summary"]["changed_file_count"] >= 1
    assert changed_path in {row.get("path") or row.get("source_file") for row in diff["changed_files"]}
    assert "created_at" not in json.dumps(diff["identity_inputs"], ensure_ascii=False)
    assert str(repo) not in serialized
    for row in diff["changed_files"]:
        assert row["change_type"] in {"added", "modified", "deleted"}
        assert row["fingerprint"]
    return diff


def _assert_workbench(payload: dict, *, repo: str) -> dict:
    workbench = _workbench(payload)
    serialized = json.dumps(workbench, ensure_ascii=False)
    assert workbench["schema_version"] == "v2.15"
    assert workbench["summary"]["patch_plan_count"] >= 1
    assert workbench["summary"]["runtime_run_count"] >= 1
    assert workbench["summary"]["incremental_diff_count"] >= 1
    assert workbench["capability_graph"]["nodes"]
    node_ids = {node["node_id"] for node in workbench["capability_graph"]["nodes"]}
    for edge in workbench["capability_graph"]["edges"]:
        assert edge["from"] in node_ids
        assert edge["to"] in node_ids
    assert {section["section_id"] for section in workbench["sections"]} >= {"architecture_map", "runtime_evidence", "incremental_drift", "blockers"}
    assert str(repo) not in serialized
    return workbench


def test_v213_v214_v215_service_e2e_with_real_fixture(tmp_path, monkeypatch):
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = CodingAgentActionabilityService(workspace, workspace_id=workspace_id)
    patch_plan = service.create_patch_plan(codebase_id, task="add API route behavior", snapshot_id=snapshot_id)

    registry = _assert_runtime_registry(service.build_runtime_registry(codebase_id, snapshot_id=snapshot_id, patch_plan_id=patch_plan["patch_plan_id"]), repo=str(repo))
    assert runtime_registry_path(workspace, codebase_id).exists()
    blocked = _assert_runtime_run(service.run_runtime_command(codebase_id, command_id="not-registered", snapshot_id=snapshot_id), repo=str(repo), expected_status="blocked")
    assert not blocked["artifact_refs"]

    command_id = registry["allowlisted_commands"][0]["command_id"]
    run = _assert_runtime_run(service.run_runtime_command(codebase_id, command_id=command_id, patch_plan_id=patch_plan["patch_plan_id"]), repo=str(repo))
    assert runtime_run_path(workspace, codebase_id, run["run_id"]).exists()
    assert runtime_log_path(workspace, codebase_id, run["run_id"], "stdout").exists()
    assert runtime_log_path(workspace, codebase_id, run["run_id"], "stderr").exists()

    changed_file = repo / "backend" / "app" / "main.py"
    changed_file.write_text("print('changed deterministic fixture')\n", encoding="utf-8")
    second_snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(codebase_id)["snapshot"]["snapshot_id"]
    diff = _assert_diff(service.build_incremental_diff(codebase_id, from_snapshot_id=snapshot_id, to_snapshot_id=second_snapshot_id, task="change backend app main"), changed_path="backend/app/main.py", repo=str(repo))
    assert snapshot_diff_path(workspace, codebase_id, diff["diff_id"]).exists()
    assert fingerprint_index_path(workspace, codebase_id, snapshot_id).exists()
    assert service.read_incremental_timeline(codebase_id)["event_count"] >= 1

    workbench = _assert_workbench(service.build_workbench(codebase_id, snapshot_id=second_snapshot_id), repo=str(repo))
    assert workbench_payload_path(workspace, codebase_id).exists()
    html_view = service.read_workbench_view(codebase_id, "html")
    mermaid_view = service.read_workbench_view(codebase_id, "mermaid")
    assert workbench_html_path(workspace, codebase_id).exists()
    assert workbench_mermaid_path(workspace, codebase_id).exists()
    assert "<script" not in html_view["content"].lower()
    assert "flowchart TD" in mermaid_view["content"]
    export = _export(service.create_workbench_context_export(codebase_id, mode="coding_agent", max_items=10))
    assert export["schema_version"] == "v2.15"
    assert {"V2.13", "V2.14", "V2.15"} <= set(export["source_phase_refs"])
    for recommendation in export["recommendations"]:
        assert recommendation["evidence_refs"] or recommendation["needs_review"]
    assert context_export_path(workspace, codebase_id, export["export_id"]).exists()


def test_v213_v214_v215_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = CodingAgentActionabilityService(workspace, workspace_id=workspace_id)
    patch_plan = service.create_patch_plan(codebase_id, task="add API route behavior", snapshot_id=snapshot_id)

    http_registry = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/commands",
        json={"snapshot_id": snapshot_id, "patch_plan_id": patch_plan["patch_plan_id"]},
    )
    assert http_registry.status_code == 200
    http_commands = _assert_runtime_registry(_v2(http_registry.json()), repo=str(repo))
    command_id = http_commands["allowlisted_commands"][0]["command_id"]

    http_run = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/runs",
        json={"command_id": command_id, "patch_plan_id": patch_plan["patch_plan_id"]},
    )
    assert http_run.status_code == 200
    http_run_payload = _assert_runtime_run(_v2(http_run.json()), repo=str(repo))

    changed_file = repo / "backend" / "app" / "main.py"
    changed_file.write_text("print('changed through parity test')\n", encoding="utf-8")
    second_snapshot_id = CodebaseSnapshotService(workspace, workspace_id=workspace_id).create_snapshot(codebase_id)["snapshot"]["snapshot_id"]
    http_diff = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/incremental/diff",
        json={"from_snapshot_id": snapshot_id, "to_snapshot_id": second_snapshot_id, "task": "change backend app main"},
    )
    assert http_diff.status_code == 200
    http_diff_payload = _assert_diff(_v2(http_diff.json()), changed_path="backend/app/main.py", repo=str(repo))

    http_workbench = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench/build", json={"snapshot_id": second_snapshot_id})
    assert http_workbench.status_code == 200
    http_workbench_payload = _assert_workbench(_v2(http_workbench.json()), repo=str(repo))
    http_export = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/workbench/context-export", json={"mode": "coding_agent", "max_items": 10})
    assert http_export.status_code == 200
    assert _export(_v2(http_export.json()))["schema_version"] == "v2.15"

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_registry = asyncio.run(dispatcher.call_tool("knowledge_code_runtime_commands", {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id}))
    mcp_commands = _assert_runtime_registry(_v2(mcp_registry), repo=str(repo))
    mcp_run = asyncio.run(dispatcher.call_tool("knowledge_code_runtime_run", {"workspace_id": workspace_id, "codebase_id": codebase_id, "command_id": command_id}))
    mcp_run_payload = _assert_runtime_run(_v2(mcp_run), repo=str(repo))
    mcp_diff = asyncio.run(dispatcher.call_tool("knowledge_code_incremental_diff_read", {"workspace_id": workspace_id, "codebase_id": codebase_id, "diff_id": http_diff_payload["diff_id"]}))
    assert _assert_diff(_v2(mcp_diff), changed_path="backend/app/main.py", repo=str(repo))["diff_id"] == http_diff_payload["diff_id"]
    mcp_workbench = asyncio.run(dispatcher.call_tool("knowledge_code_workbench_read", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _assert_workbench(_v2(mcp_workbench), repo=str(repo))["workbench_id"] == http_workbench_payload["workbench_id"]

    assert knowledge_main(["code", "coding-agent", "runtime-commands", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_commands = _assert_runtime_registry(_v2(json.loads(capsys.readouterr().out)), repo=str(repo))
    assert knowledge_main(["code", "coding-agent", "runtime-run", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--command-id", cli_commands["allowlisted_commands"][0]["command_id"]]) == 0
    cli_run = _assert_runtime_run(_v2(json.loads(capsys.readouterr().out)), repo=str(repo))
    assert knowledge_main(["code", "coding-agent", "incremental-read", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--diff-id", http_diff_payload["diff_id"]]) == 0
    cli_diff = _assert_diff(_v2(json.loads(capsys.readouterr().out)), changed_path="backend/app/main.py", repo=str(repo))
    assert knowledge_main(["code", "coding-agent", "workbench-read", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_workbench = _assert_workbench(_v2(json.loads(capsys.readouterr().out)), repo=str(repo))

    assert http_commands["schema_version"] == mcp_commands["schema_version"] == cli_commands["schema_version"] == "v2.13"
    assert http_run_payload["schema_version"] == mcp_run_payload["schema_version"] == cli_run["schema_version"] == "v2.13"
    assert http_diff_payload["schema_version"] == cli_diff["schema_version"] == "v2.14"
    assert http_workbench_payload["schema_version"] == cli_workbench["schema_version"] == "v2.15"
