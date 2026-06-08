from __future__ import annotations

import asyncio
import json
from pathlib import Path

from data_service.__main__ import knowledge_main
from data_service.code_assets.coding_agent.persistence import patch_plan_path
from data_service.code_assets.coding_agent.service import CodingAgentActionabilityService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _repo_hashes(repo: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(repo.rglob("*")):
        if path.is_file():
            result[str(path.relative_to(repo))] = path.read_bytes().hex()
    return result


def _patch_plan(payload: dict) -> dict:
    if "data" in payload and "patch_plan" in payload["data"]:
        return payload["data"]["patch_plan"]
    return payload


def _assert_patch_plan(payload: dict, *, repo: Path, expected_schema: str = "v2.12") -> dict:
    plan = _patch_plan(payload)
    serialized = json.dumps(plan, ensure_ascii=False)
    assert plan["schema_version"] == expected_schema
    assert plan["patch_plan_id"]
    assert plan["status"] in {"ready_for_review", "needs_review", "blocked"}
    assert plan["readiness"]["status"] == plan["status"]
    assert isinstance(plan["readiness"]["score"], float)
    assert plan["readiness"]["reason_codes"]
    assert "readiness_score" not in plan
    assert "edit_options" not in plan
    assert plan["mutates_code"] is False
    assert plan["executes_runtime"] is False
    assert str(repo) not in serialized
    assert plan["artifact_refs"]
    assert any(ref["type"] == "patch_plan" for ref in plan["artifact_refs"])
    assert isinstance(plan["edit_candidates"], list)
    assert isinstance(plan["patch_options"], list)
    assert isinstance(plan["validation_plan"], list)
    assert isinstance(plan["rollback_plan"], list)
    for candidate in plan["edit_candidates"]:
        assert candidate["candidate_id"]
        assert candidate.get("path") or candidate.get("source_file")
        assert candidate["line_range"]
        assert candidate.get("evidence_refs") or candidate.get("needs_review")
    for command in plan["validation_plan"]:
        assert command["execution_policy"] == "plan_only"
    covered = {candidate_id for row in plan["rollback_plan"] for candidate_id in row.get("covers_candidate_ids", [])}
    for candidate in plan["edit_candidates"]:
        assert candidate["candidate_id"] in covered
    for option in plan["patch_options"]:
        assert option["candidate_ids"]
        assert option["validation_command_ids"]
        assert option["rollback_step_ids"]
        assert option.get("evidence_refs") or option.get("needs_review")
    section_ids = {section["section_id"] for section in plan["user_sections"]}
    assert {"proposed_files", "patch_options", "evidence_and_needs_review", "validation_plan", "rollback_plan", "readiness_and_blockers"} <= section_ids
    return plan


def test_v212_patch_plan_service_schema_and_no_source_mutation(tmp_path, monkeypatch):
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = CodingAgentActionabilityService(workspace, workspace_id=workspace_id)
    before = _repo_hashes(repo)

    payload = service.create_patch_plan(codebase_id, task="修改 architecture docs alignment API route behavior 并更新测试", snapshot_id=snapshot_id)
    plan = _assert_patch_plan(payload, repo=repo)

    assert patch_plan_path(workspace, codebase_id, plan["patch_plan_id"]).exists()
    assert service.read_patch_plan(codebase_id, plan["patch_plan_id"])["patch_plan_id"] == plan["patch_plan_id"]
    assert before == _repo_hashes(repo)


def test_v212_patch_plan_low_readiness_blocker(tmp_path, monkeypatch):
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = CodingAgentActionabilityService(workspace, workspace_id=workspace_id)

    payload = service.create_patch_plan(codebase_id, task="zzzzzzzz impossible broad risky request", focus_paths=["missing/path.py"], snapshot_id=snapshot_id)
    plan = _patch_plan(payload)

    assert plan["schema_version"] == "v2.12"
    assert plan["status"] == "blocked"
    assert plan["readiness"]["score"] < 0.8
    assert any(item["code"] == "NO_EDIT_CANDIDATES" for item in plan["unresolved"])
    assert str(repo) not in json.dumps(plan, ensure_ascii=False)


def test_v212_patch_plan_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = CodingAgentActionabilityService(workspace, workspace_id=workspace_id)
    service_plan = _assert_patch_plan(service.create_patch_plan(codebase_id, task="add API route behavior", snapshot_id=snapshot_id), repo=repo)

    http_create = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans",
        json={"task": "add API route behavior", "snapshot_id": snapshot_id},
    )
    assert http_create.status_code == 200
    http_plan = _assert_patch_plan(_v2(http_create.json()), repo=repo)
    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/patch-plans/{http_plan['patch_plan_id']}")
    assert http_read.status_code == 200
    http_read_plan = _assert_patch_plan(_v2(http_read.json()), repo=repo)
    assert http_read_plan["patch_plan_id"] == http_plan["patch_plan_id"]

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_create = asyncio.run(dispatcher.call_tool("knowledge_code_patch_plan_create", {"workspace_id": workspace_id, "codebase_id": codebase_id, "task": "add API route behavior"}))
    mcp_plan = _assert_patch_plan(_v2(mcp_create), repo=repo)
    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_patch_plan_read", {"workspace_id": workspace_id, "codebase_id": codebase_id, "patch_plan_id": mcp_plan["patch_plan_id"]}))
    assert _assert_patch_plan(_v2(mcp_read), repo=repo)["patch_plan_id"] == mcp_plan["patch_plan_id"]

    assert knowledge_main(["code", "coding-agent", "patch-plan", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--task", "add API route behavior"]) == 0
    cli_plan = _assert_patch_plan(_v2(json.loads(capsys.readouterr().out)), repo=repo)
    assert knowledge_main(["code", "coding-agent", "patch-plan-read", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--patch-plan-id", cli_plan["patch_plan_id"]]) == 0
    cli_read = _assert_patch_plan(_v2(json.loads(capsys.readouterr().out)), repo=repo)

    stable_fields = ("schema_version", "workspace_id", "codebase_id", "snapshot_id", "status", "mutates_code", "executes_runtime")
    for field in stable_fields:
        assert http_plan[field] == mcp_plan[field] == cli_plan[field]
    assert http_plan["readiness"]["status"] == mcp_plan["readiness"]["status"] == cli_plan["readiness"]["status"]
    assert cli_read["patch_plan_id"] == cli_plan["patch_plan_id"]
    assert service_plan["schema_version"] == "v2.12"
