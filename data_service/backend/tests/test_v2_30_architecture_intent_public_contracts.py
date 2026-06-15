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


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200, response.text
    return response.json()["data"]["workspace"]["workspace_id"]


def _make_repo(root: Path) -> None:
    _write(
        root / "docs/target_architecture.md",
        """# Target Architecture

- HTTP API public interface exposes workflow capability.
- MCP tool registry exposes architecture intent review capability.
- Runtime workflow uses runtime descriptor evidence only.
- Quality acceptance gate is covered by tests.
""",
    )
    _write(root / "backend/api.py", "def http_api_handler():\n    return {'ok': True}\n")
    _write(root / "backend/mcp_tools.py", "TOOLS = ['architecture_intent']\n")
    _write(root / "backend/workflow.py", "def run_workflow():\n    return True\n")
    _write(root / "runtime/workflow.yaml", "workflow: descriptor-only\n")
    _write(root / "tests/test_quality.py", "def test_quality_gate():\n    assert True\n")


def _assert_no_path_leak(payload: object, *paths: Path) -> None:
    text = json.dumps(payload, ensure_ascii=False)
    assert "/Users/" not in text
    assert "/private/var" not in text
    assert "/var/folders" not in text
    for path in paths:
        assert str(path) not in text


def test_v2_30_architecture_intent_public_contracts_http_mcp_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "repo"
    workspace_root = tmp_path / "managed"
    _make_repo(repo)
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))

    tool_names = {spec["name"] for spec in all_tool_specs()}
    assert "knowledge_architecture_intent_build" in tool_names
    assert "knowledge_architecture_intent_report" in tool_names
    assert "knowledge_architecture_context_pack_v4" in tool_names

    client = TestClient(app)
    workspace_id = _create_workspace(client, "Phase96B Public Contracts")
    imported = client.post(f"/api/workspaces/{workspace_id}/codebases", json={"path": str(repo), "codebase_id": "phase96b"})
    assert imported.status_code == 200, imported.text
    codebase_id = imported.json()["data"]["codebase"]["codebase_id"]
    snapshot = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/snapshots", json={})
    assert snapshot.status_code == 200, snapshot.text
    snapshot_id = snapshot.json()["data"]["snapshot"]["snapshot_id"]

    built = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/build", json={"snapshot_id": snapshot_id})
    assert built.status_code == 200, built.text
    built_payload = built.json()
    assert built_payload["status"] == "ok"
    assert built_payload["data"]["architecture_intent"]["snapshot_id"] == snapshot_id
    assert built_payload["data"]["architecture_intent"]["diagram_verification"]["summary"]["verification_count"] > 0
    _assert_no_path_leak(built_payload, repo, workspace_root)

    http_report = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/report")
    assert http_report.status_code == 200, http_report.text
    http_payload = http_report.json()
    http_report_data = http_payload["data"]["architecture_intent_report"]
    assert http_report_data["report"]["summary"]["verification_count"] > 0
    assert "Target Architecture from Documents" in http_report_data["html"]
    _assert_no_path_leak(http_payload, repo, workspace_root)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_architecture_intent_report", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert mcp_payload["status"] == "ok"
    mcp_report_data = mcp_payload["data"]["architecture_intent_report"]
    assert mcp_report_data["snapshot_id"] == http_report_data["snapshot_id"]
    assert mcp_report_data["report"]["summary"]["verification_count"] == http_report_data["report"]["summary"]["verification_count"]
    _assert_no_path_leak(mcp_payload, repo, workspace_root)

    assert knowledge_main(["code", "architecture-intent", "report", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    cli_report_data = cli_payload["data"]["architecture_intent_report"]
    assert cli_report_data["snapshot_id"] == http_report_data["snapshot_id"]
    assert cli_report_data["report"]["summary"]["verification_count"] == http_report_data["report"]["summary"]["verification_count"]
    _assert_no_path_leak(cli_payload, repo, workspace_root)

    alignment_id = http_report_data["report"]["verification_samples"][0]["verification_id"]
    before = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/governance").json()
    before_count = before["data"]["architecture_intent_governance"]["summary"].get("confirmed_fact_count", 0)
    confirmed = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/confirm",
        json={"snapshot_id": snapshot_id, "target_type": "diagram_code_verification", "target_id": alignment_id, "note": "accept via public contract", "reviewer": "test"},
    )
    assert confirmed.status_code == 200, confirmed.text
    assert confirmed.json()["data"]["architecture_intent_governance"]["summary"]["confirmed_fact_count"] == before_count + 1
    revoked = asyncio.run(
        dispatcher.call_tool(
            "knowledge_architecture_intent_revoke",
            {
                "workspace_id": workspace_id,
                "codebase_id": codebase_id,
                "snapshot_id": snapshot_id,
                "target_type": "diagram_code_verification",
                "target_id": alignment_id,
                "note": "revoke via MCP",
                "reviewer": "test",
            },
        )
    )
    assert revoked["status"] == "ok"
    assert revoked["data"]["architecture_intent_governance"]["summary"]["confirmed_fact_count"] == before_count

    context = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/intent/context-pack")
    assert context.status_code == 200
    context_payload = context.json()["data"]["architecture_context_pack_v4"]["context_pack"]
    assert all(item.get("evidence_refs") or item.get("needs_review") for item in context_payload["recommendations"])
