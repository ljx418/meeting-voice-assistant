from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.platform.persistence import provider_capabilities_path, provider_execution_contract_path
from data_service.code_assets.platform.providers import PlatformProviderService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _providers(payload: dict) -> dict:
    if "data" in payload and "provider_plugins" in payload["data"]:
        return payload["data"]["provider_plugins"]
    if "provider_capabilities" in payload and "provider_execution_contract" in payload:
        return {
            "schema_version": "v2.22",
            "artifact_type": "provider_plugin_bundle",
            "provider_capabilities": payload["provider_capabilities"],
            "provider_execution_contract": payload["provider_execution_contract"],
            "artifact_refs": payload.get("artifact_refs", []),
        }
    return payload


def _assert_providers(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo: str, workspace_path: str) -> dict:
    bundle = _providers(payload)
    serialized = json.dumps(bundle, ensure_ascii=False)
    assert bundle["schema_version"] == "v2.22"
    assert bundle["artifact_type"] == "provider_plugin_bundle"
    capabilities = bundle["provider_capabilities"]
    contract = bundle["provider_execution_contract"]
    assert capabilities["schema_version"] == "v2.22"
    assert capabilities["artifact_type"] == "provider_capabilities"
    assert capabilities["workspace_id"] == workspace_id
    assert capabilities["codebase_id"] == codebase_id
    assert capabilities["snapshot_id"] == snapshot_id
    providers = {row["provider_id"]: row for row in capabilities["providers"]}
    ast = providers["semantic:python_ast"]
    assert ast["mandatory"] is True
    assert ast["configured"] is True
    assert ast["execution_supported"] is True
    assert ast["status"] == "ready"
    assert ast["accepted"] is True
    for provider_id in ("semantic:tree_sitter", "semantic:jedi", "semantic:lsp"):
        provider = providers[provider_id]
        assert provider["mandatory"] is False
        if not provider["execution_supported"]:
            assert provider["accepted"] is False
            assert provider["status"] in {"provider_unavailable", "provider_unsupported"}
    assert capabilities["summary"]["mandatory_ready_count"] >= 1
    assert contract["schema_version"] == "v2.22"
    assert contract["artifact_type"] == "provider_execution_contract"
    assert contract["contract"]["health_config_execution_separated"] is True
    execution = {row["provider_id"]: row for row in contract["provider_execution"]}
    assert execution["semantic:python_ast"]["execution_status"] == "execution_ready"
    assert any(row["health_known"] and not row["execution_supported"] for row in execution.values())
    assert "PROVIDER_UNSUPPORTED" in contract["public_error_codes"]
    assert bundle["artifact_refs"]
    assert repo not in serialized
    assert workspace_path not in serialized
    return bundle


def test_v222_provider_plugin_service(tmp_path, monkeypatch):
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = PlatformProviderService(workspace, workspace_id=workspace_id)

    bundle = _assert_providers(
        service.build_provider_artifacts(codebase_id, snapshot_id=snapshot_id),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )
    assert provider_capabilities_path(workspace, codebase_id).exists()
    assert provider_execution_contract_path(workspace, codebase_id).exists()
    readback = _assert_providers(
        service.read_provider_artifacts(codebase_id),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )
    assert bundle["provider_capabilities"]["summary"] == readback["provider_capabilities"]["summary"]


def test_v222_provider_plugin_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)

    http_build = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/providers/build",
        json={"snapshot_id": snapshot_id},
    )
    assert http_build.status_code == 200
    http_providers = _assert_providers(
        _v2(http_build.json()),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/providers")
    assert http_read.status_code == 200
    _assert_providers(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo=str(repo), workspace_path=str(workspace))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_platform_providers_build",
            {"workspace_id": workspace_id, "codebase_id": codebase_id, "snapshot_id": snapshot_id},
        )
    )
    mcp_providers = _assert_providers(
        _v2(mcp_build),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )

    assert knowledge_main(["code", "platform", "providers", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_providers = _assert_providers(
        _v2(json.loads(capsys.readouterr().out)),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=snapshot_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )

    assert http_providers["provider_capabilities"]["summary"] == mcp_providers["provider_capabilities"]["summary"]
    assert http_providers["provider_capabilities"]["summary"] == cli_providers["provider_capabilities"]["summary"]
