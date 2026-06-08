from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.coding_agent_v2_16.persistence import (
    provider_decision_path,
    provider_registry_path,
)
from data_service.code_assets.coding_agent.service import CodingAgentActionabilityService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _provider_registry(payload: dict) -> dict:
    if "data" in payload and "provider_registry" in payload["data"]:
        return payload["data"]["provider_registry"]
    return payload


def _providers_by_id(registry: dict) -> dict[str, dict]:
    return {str(provider["provider_id"]): provider for provider in registry["providers"]}


def _assert_provider_registry(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: str, workspace_path: str) -> dict:
    registry = _provider_registry(payload)
    serialized = json.dumps(registry, ensure_ascii=False)
    assert registry["schema_version"] == "v2.16"
    assert registry["workspace_id"] == workspace_id
    assert registry["codebase_id"] == codebase_id
    assert registry["snapshot_id"] == snapshot_id
    assert registry["summary"]["provider_count"] >= 6
    assert registry["summary"]["execution_supported_count"] >= 3
    assert registry["summary"]["known_count"] == registry["summary"]["provider_count"]
    assert registry["summary"]["unsupported_count"] >= 1
    assert registry["summary"]["missing_credential_count"] >= 1
    assert registry["artifact_refs"]
    assert registry["decision_records"]
    assert registry["source_phase"] == "V2.16 Phase 76"
    assert str(repo) not in serialized
    assert str(workspace_path) not in serialized
    for forbidden in ["api_key", "authorization", "traceback", "secret", "/Users/"]:
        assert forbidden not in serialized.lower()

    providers = _providers_by_id(registry)
    ast_provider = providers["semantic:python_ast"]
    assert ast_provider["known"] is True
    assert ast_provider["configured"] is True
    assert ast_provider["execution_supported"] is True
    assert ast_provider["available"] is True
    assert ast_provider["accepted"] is True
    assert ast_provider["status"] == "available"
    assert ast_provider["evidence"]

    for provider_id in {"semantic:tree_sitter", "semantic:jedi", "semantic:lsp"}:
        provider = providers[provider_id]
        assert provider["known"] is True
        assert provider["available"] is False
        assert provider["accepted"] is False
        assert provider["execution_supported"] is False
        assert provider["status"] in {"provider_unavailable", "provider_unsupported"}
        assert provider["reason_code"] in {"PROVIDER_UNAVAILABLE", "PROVIDER_UNSUPPORTED"}

    assert providers["runtime:local_profile_runner"]["status"] == "available"
    assert providers["patch:sandbox_preview"]["status"] == "available"
    assert providers["external:llm_review"]["status"] in {"provider_missing_credential", "provider_unsupported"}
    assert providers["external:llm_review"]["reason_code"] in {"PROVIDER_MISSING_CREDENTIAL", "PROVIDER_UNSUPPORTED"}
    assert any(record["selected_provider"] == "semantic:python_ast" and record["decision"] == "accepted_baseline" for record in registry["decision_records"])
    assert any("semantic:lsp" in record.get("unsupported_providers", []) for record in registry["decision_records"])
    return registry


def test_v216_provider_registry_service_artifacts(tmp_path, monkeypatch):
    for env_name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MINIMAX_API_KEY"):
        monkeypatch.delenv(env_name, raising=False)
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = CodingAgentActionabilityService(workspace, workspace_id=workspace_id)

    registry = service.build_provider_registry(codebase_id, snapshot_id=snapshot_id)
    _assert_provider_registry(registry, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))
    assert provider_registry_path(workspace, codebase_id).exists()
    for decision in registry["decision_records"]:
        assert provider_decision_path(workspace, codebase_id, decision["decision_id"]).exists()

    readback = service.read_provider_registry(codebase_id)
    assert readback["summary"] == registry["summary"]
    assert [provider["provider_id"] for provider in readback["providers"]] == [provider["provider_id"] for provider in registry["providers"]]


def test_v216_provider_registry_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    for env_name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MINIMAX_API_KEY"):
        monkeypatch.delenv(env_name, raising=False)
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)

    http_build = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/providers/build",
        json={"snapshot_id": snapshot_id},
    )
    assert http_build.status_code == 200
    http_registry = _assert_provider_registry(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/providers")
    assert http_read.status_code == 200
    assert _provider_registry(_v2(http_read.json()))["summary"] == http_registry["summary"]

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_provider_registry_build",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id},
        )
    )
    mcp_registry = _assert_provider_registry(_v2(mcp_build), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    assert knowledge_main(["code", "coding-agent", "providers", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_registry = _assert_provider_registry(_v2(json.loads(capsys.readouterr().out)), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    assert http_registry["summary"] == mcp_registry["summary"] == cli_registry["summary"]
    assert [provider["provider_id"] for provider in http_registry["providers"]] == [provider["provider_id"] for provider in mcp_registry["providers"]] == [provider["provider_id"] for provider in cli_registry["providers"]]
    assert len(http_registry["artifact_refs"]) == len(mcp_registry["artifact_refs"]) == len(cli_registry["artifact_refs"])
