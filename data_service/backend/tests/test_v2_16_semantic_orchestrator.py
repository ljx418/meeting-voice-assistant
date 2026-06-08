from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.coding_agent.service import CodingAgentActionabilityService
from data_service.code_assets.coding_agent_v2_16.persistence import (
    semantic_conflicts_path,
    semantic_index_path,
    semantic_provider_facts_path,
)
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


FORBIDDEN_CLAIMS = {"runtime_call", "runtime_calls", "data_flow", "control_flow", "type_inferred", "type_inferred_dependency"}


def _semantic(payload: dict) -> dict:
    if "data" in payload and "semantic_provider_index" in payload["data"]:
        return payload["data"]["semantic_provider_index"]
    if "index" in payload and "schema_version" not in payload:
        return {
            "schema_version": payload["index"]["schema_version"],
            "index": payload["index"],
            "provider_facts": payload.get("provider_facts", []),
            "provider_conflicts": payload.get("provider_conflicts", []),
            "artifact_refs": payload.get("artifact_refs", []),
        }
    return payload


def _assert_semantic(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: str, workspace_path: str) -> dict:
    semantic = _semantic(payload)
    serialized = json.dumps(semantic, ensure_ascii=False)
    assert semantic["schema_version"] == "v2.16"
    assert semantic["index"]["schema_version"] == "v2.16"
    assert semantic["index"]["workspace_id"] == workspace_id
    assert semantic["index"]["codebase_id"] == codebase_id
    assert semantic["index"]["snapshot_id"] == snapshot_id
    assert semantic["index"]["summary"]["provider_fact_count"] > 0
    assert semantic["index"]["summary"]["accepted_fact_count"] > 0
    assert semantic["index"]["summary"]["forbidden_claim_count"] == 0
    assert semantic["index"]["provider_blockers"]
    assert semantic["provider_facts"]
    assert semantic["artifact_refs"]
    assert str(repo) not in serialized
    assert str(workspace_path) not in serialized
    for forbidden in ["api_key", "authorization", "traceback", "secret", "/Users/"]:
        assert forbidden not in serialized.lower()

    accepted = [fact for fact in semantic["provider_facts"] if fact["status"] == "accepted"]
    assert accepted
    for fact in accepted[:20]:
        assert fact["provider_id"] == "semantic:python_ast"
        assert fact["extractor"] == "python_ast"
        assert fact["confidence"] > 0
        assert fact["source_file"]
        assert fact["claim_type"] not in FORBIDDEN_CLAIMS
        assert len(fact["line_range"]) == 2
        assert fact["evidence_refs"]
    return semantic


def test_v216_semantic_orchestrator_service_artifacts(tmp_path, monkeypatch):
    for env_name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MINIMAX_API_KEY"):
        monkeypatch.delenv(env_name, raising=False)
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = CodingAgentActionabilityService(workspace, workspace_id=workspace_id)

    payload = service.build_semantic_provider_index(codebase_id, snapshot_id=snapshot_id)
    semantic = _assert_semantic(payload, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))
    assert semantic_index_path(workspace, codebase_id).exists()
    assert semantic_provider_facts_path(workspace, codebase_id).exists()
    assert semantic_conflicts_path(workspace, codebase_id).exists()
    assert service.read_semantic_provider_index(codebase_id)["index"]["summary"] == semantic["index"]["summary"]


def test_v216_semantic_orchestrator_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    for env_name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MINIMAX_API_KEY"):
        monkeypatch.delenv(env_name, raising=False)
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)

    http_build = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/semantic/build",
        json={"snapshot_id": snapshot_id},
    )
    assert http_build.status_code == 200
    http_semantic = _assert_semantic(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/semantic")
    assert http_read.status_code == 200
    assert _semantic(_v2(http_read.json()))["index"]["summary"] == http_semantic["index"]["summary"]

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_semantic_providers_build",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id},
        )
    )
    mcp_semantic = _assert_semantic(_v2(mcp_build), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    assert knowledge_main(["code", "coding-agent", "semantic", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_semantic = _assert_semantic(_v2(json.loads(capsys.readouterr().out)), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    assert http_semantic["index"]["summary"] == mcp_semantic["index"]["summary"] == cli_semantic["index"]["summary"]
    assert len(http_semantic["artifact_refs"]) == len(mcp_semantic["artifact_refs"]) == len(cli_semantic["artifact_refs"])
