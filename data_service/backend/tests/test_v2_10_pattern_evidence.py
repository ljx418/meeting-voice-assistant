from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.artifacts import (
    architecture_accepted_pattern_evidence_v210_path,
    architecture_adapter_attempts_v210_path,
    architecture_ast_bindings_v210_path,
    architecture_definition_lookups_v210_path,
    architecture_pattern_adapter_registry_v210_path,
    architecture_pattern_evidence_summary_v210_path,
    architecture_runtime_candidates_v210_path,
    architecture_v210_view_path,
)
from data_service.code_assets.architecture.pattern_evidence_v2 import BUILT_IN_ADAPTERS
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _assert_pattern_payload(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo_path: str) -> None:
    patterns = payload["data"]["pattern_evidence_v2"] if "data" in payload else payload
    assert patterns["schema_version"] == "v2.10"
    summary = patterns["summary"]
    assert summary["workspace_id"] == workspace_id
    assert summary["codebase_id"] == codebase_id
    assert summary["snapshot_id"] == snapshot_id
    assert summary["adapter_count"] >= len(BUILT_IN_ADAPTERS)
    assert summary["attempt_count"] >= summary["adapter_count"]
    assert summary["accepted_evidence_count"] >= 1
    assert patterns["registry"]["adapters"]
    adapter_ids = {item["adapter_id"] for item in patterns["registry"]["adapters"]}
    assert "python_decorator_registration" in adapter_ids
    assert "runtime_introspection_candidate" in adapter_ids
    runtime = [item for item in patterns["registry"]["adapters"] if item["adapter_id"] == "runtime_introspection_candidate"][0]
    assert runtime["status"] == "disabled"
    assert patterns["attempts"]
    accepted_evidence = list(patterns.get("accepted_evidence") or [item for item in patterns.get("bindings", []) if item.get("status") == "accepted"])
    assert accepted_evidence
    for item in accepted_evidence:
        assert item["status"] == "accepted"
        assert item["truth_check"] == "passed"
        assert item["confidence"] >= 0.85
        assert item["source_path"]
        assert item["definition_path"]
        assert len(item["definition_line_range"]) == 2
        assert item["evidence_refs"]
        assert not str(item["source_path"]).startswith("/")
    serialized = json.dumps(patterns, ensure_ascii=False)
    assert repo_path not in serialized
    for item in accepted_evidence:
        assert item.get("semantic_claim") not in {"runtime_call", "data_flow", "control_flow"}


def _assert_blockers_payload(payload: dict) -> None:
    blockers = payload["data"]["pattern_blockers"] if "data" in payload else payload
    assert blockers["schema_version"] == "v2.10"
    assert "blockers" in blockers
    assert blockers["summary"]["schema_version"] == "v2.10"


def _assert_view(payload: dict, *, repo_path: str) -> None:
    view = payload["data"]["view"] if "data" in payload else payload
    assert view["schema_version"] == "v2.10"
    assert view["content_type"] in {"text/html", "text/mermaid"}
    assert view["content"]
    assert "<script>" not in view["content"]
    assert repo_path not in view["content"]


def test_v210_pattern_evidence_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = ArchitectureService(workspace, workspace_id=workspace_id)

    direct = service.build_pattern_evidence_v2(codebase_id, snapshot_id=snapshot_id)
    assert architecture_pattern_adapter_registry_v210_path(workspace, codebase_id).exists()
    assert architecture_adapter_attempts_v210_path(workspace, codebase_id).exists()
    assert architecture_ast_bindings_v210_path(workspace, codebase_id).exists()
    assert architecture_definition_lookups_v210_path(workspace, codebase_id).exists()
    assert architecture_runtime_candidates_v210_path(workspace, codebase_id).exists()
    assert architecture_accepted_pattern_evidence_v210_path(workspace, codebase_id).exists()
    assert architecture_pattern_evidence_summary_v210_path(workspace, codebase_id).exists()
    assert architecture_ast_bindings_v210_path(workspace, codebase_id).name == "adapter_matches.jsonl"
    assert architecture_definition_lookups_v210_path(workspace, codebase_id).name == "definition_lookup_results.jsonl"
    assert architecture_runtime_candidates_v210_path(workspace, codebase_id).name == "runtime_introspection_candidates.jsonl"
    assert architecture_accepted_pattern_evidence_v210_path(workspace, codebase_id).name == "accepted_pattern_evidence.jsonl"
    assert architecture_v210_view_path(workspace, codebase_id, "pattern_evidence_report.html").name == "architecture_pattern_evidence_report.html"
    assert architecture_v210_view_path(workspace, codebase_id, "pattern_evidence_map.mmd").name == "architecture_pattern_adapter_map.mmd"
    _assert_pattern_payload(direct, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))
    _assert_view(service.read_pattern_evidence_view_v2(codebase_id, "pattern_evidence_report.html"), repo_path=str(repo))
    _assert_view(service.read_pattern_evidence_view_v2(codebase_id, "pattern_evidence_map.mmd"), repo_path=str(repo))

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/build", json={"snapshot_id": snapshot_id})
    assert http_build.status_code == 200
    _assert_pattern_payload(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns")
    assert http_read.status_code == 200
    _assert_pattern_payload(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    http_blockers = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/blockers")
    assert http_blockers.status_code == 200
    _assert_blockers_payload(_v2(http_blockers.json()))

    http_view = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_10/patterns/views/pattern_evidence_report.html")
    assert http_view.status_code == 200
    _assert_view(_v2(http_view.json()), repo_path=str(repo))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_patterns_v2", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_pattern_payload(_v2(mcp_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))
    mcp_view = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_pattern_view", {"workspace_id": workspace_id, "codebase_id": codebase_id, "view_id": "pattern_evidence_map.mmd"}))
    _assert_view(_v2(mcp_view), repo_path=str(repo))

    assert knowledge_main(["code", "architecture", "patterns-v2", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_pattern_payload(_v2(cli_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    assert knowledge_main(["code", "architecture", "pattern-view", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--view-id", "pattern_evidence_map.mmd"]) == 0
    cli_view = json.loads(capsys.readouterr().out)
    _assert_view(_v2(cli_view), repo_path=str(repo))


def test_v210_no_project_specific_hardcode_in_generic_module():
    from data_service.code_assets.architecture import pattern_evidence_v2
    from data_service.code_assets.architecture import surface_evidence_v2

    for module in (pattern_evidence_v2, surface_evidence_v2):
        source = module.__loader__.get_source(module.__name__)
        assert source is not None
        assert "HarnessOS" not in source
        assert "harnessOS" not in source
        assert "harness" not in source.lower()
