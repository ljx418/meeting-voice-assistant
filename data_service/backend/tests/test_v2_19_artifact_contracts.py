from __future__ import annotations

import asyncio
import json

from data_service.__main__ import knowledge_main
from data_service.code_assets.artifacts import codebase_dir
from data_service.code_assets.platform.console import PlatformConsoleService
from data_service.code_assets.platform.contracts import ArtifactContractService
from data_service.code_assets.platform.persistence import contract_registry_path, validation_report_path
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _v2


def _contracts(payload: dict) -> dict:
    if "data" in payload and "artifact_contracts" in payload["data"]:
        return payload["data"]["artifact_contracts"]
    if "registry" in payload and "validation_report" in payload:
        return {
            "schema_version": "v2.19",
            "artifact_type": "artifact_contract_bundle",
            "registry": payload["registry"],
            "validation_report": payload["validation_report"],
            "artifact_refs": payload.get("artifact_refs", []),
        }
    return payload


def _assert_contracts(payload: dict, *, workspace_id: str, codebase_id: str, repo: str, workspace_path: str) -> dict:
    contracts = _contracts(payload)
    serialized = json.dumps(contracts, ensure_ascii=False)
    assert contracts["schema_version"] == "v2.19"
    assert contracts["artifact_type"] == "artifact_contract_bundle"
    registry = contracts["registry"]
    report = contracts["validation_report"]
    assert registry["workspace_id"] == workspace_id
    assert registry["codebase_id"] == codebase_id
    assert registry["validation_summary"]["checked_count"] > 0
    assert report["summary"]["checked_count"] == registry["validation_summary"]["checked_count"]
    rows = [item for item in registry["contracts"] if isinstance(item, dict)]
    paths = {item.get("artifact_path") for item in rows}
    assert "platform/console/platform_console.json" in paths
    assert any(item.get("artifact_family") == "platform_console" and item.get("status") == "passed" for item in rows)
    assert repo not in serialized
    assert workspace_path not in serialized
    return contracts


def test_v219_artifact_contract_service_and_negative_fixtures(tmp_path, monkeypatch):
    _client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    PlatformConsoleService(workspace, workspace_id=workspace_id).build_console(codebase_id, snapshot_id=snapshot_id)

    root = codebase_dir(workspace, codebase_id)
    bad_json = root / "platform" / "bad_missing_schema.json"
    bad_json.parent.mkdir(parents=True, exist_ok=True)
    bad_json.write_text(json.dumps({"artifact_type": "bad_fixture"}), encoding="utf-8")
    bad_jsonl = root / "platform" / "bad_rows.jsonl"
    bad_jsonl.write_text('{"ok": true}\nnot-json\n', encoding="utf-8")

    service = ArtifactContractService(workspace, workspace_id=workspace_id)
    payload = _assert_contracts(
        service.build_contracts(codebase_id),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )
    assert contract_registry_path(workspace, codebase_id).exists()
    assert validation_report_path(workspace, codebase_id).exists()
    findings = payload["validation_report"]["findings"]
    assert any(item["artifact_path"] == "platform/bad_missing_schema.json" and item["code"] == "missing_schema_version" for item in findings)
    assert any(item["artifact_path"] == "platform/bad_rows.jsonl" and item["code"] == "invalid_jsonl_row" for item in findings)
    assert payload["validation_report"]["summary"]["failed_count"] >= 1


def test_v219_artifact_contract_http_mcp_cli_parity(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    PlatformConsoleService(workspace, workspace_id=workspace_id).build_console(codebase_id, snapshot_id=snapshot_id)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/contracts/build")
    assert http_build.status_code == 200
    http_contracts = _assert_contracts(
        _v2(http_build.json()),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/platform/contracts")
    assert http_read.status_code == 200
    _assert_contracts(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, repo=str(repo), workspace_path=str(workspace))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(
        dispatcher.call_tool(
            "knowledge_code_platform_contracts_build",
            {"workspace_id": workspace_id, "codebase_id": codebase_id},
        )
    )
    mcp_contracts = _assert_contracts(
        _v2(mcp_build),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )

    assert knowledge_main(["code", "platform", "contracts", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_contracts = _assert_contracts(
        _v2(json.loads(capsys.readouterr().out)),
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        repo=str(repo),
        workspace_path=str(workspace),
    )

    assert http_contracts["registry"]["validation_summary"]["checked_count"] == mcp_contracts["registry"]["validation_summary"]["checked_count"]
    assert http_contracts["registry"]["validation_summary"] == cli_contracts["registry"]["validation_summary"]
