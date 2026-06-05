from __future__ import annotations

import asyncio
import json
import re

from data_service.__main__ import knowledge_main
from data_service.code_assets.architecture.service import ArchitectureService
from data_service.code_assets.architecture.reconstruction import render_reconstructed_architecture_html, render_reconstructed_architecture_mermaid
from data_service.code_assets.artifacts import architecture_doc_view_path, architecture_reconstructed_model_path
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from test_v2_7_document_registry import _prepare, _prepare_alignment_artifacts, _v2


def _assert_reconstructed(payload: dict, *, workspace_id: str, codebase_id: str, snapshot_id: str, repo_path: str) -> None:
    model = payload["data"]["reconstructed_architecture"] if "data" in payload else payload
    assert model["schema_version"] == "v2.7"
    assert model["workspace_id"] == workspace_id
    assert model["codebase_id"] == codebase_id
    assert model["snapshot_id"] == snapshot_id
    assert model["artifact_refs"]
    assert model["target_nodes"]
    assert model["current_nodes"]
    assert model["diff_nodes"]
    assert model["summary"]["target_node_count"] >= len(model["target_nodes"])
    assert model["summary"]["current_node_count"] >= len(model["current_nodes"])
    assert model["summary"]["diff_node_count"] >= len(model["diff_nodes"])
    assert model["sections"]["target_from_documents"]
    assert model["sections"]["current_from_code"]
    assert model["sections"]["gap_and_drift"]
    assert str(repo_path) not in json.dumps(model, ensure_ascii=False)

    node_ids = {item["node_id"] for item in [*model["target_nodes"], *model["current_nodes"], *model["diff_nodes"]]}
    assert node_ids
    assert set(model["summary"]["rendered_node_ids"]).issubset(node_ids)
    for node in [*model["target_nodes"], *model["current_nodes"], *model["diff_nodes"]]:
        assert node["node_id"] in node_ids
        assert node["section"] in {"target_from_documents", "current_from_code", "gap_and_drift"}
        assert node["source_kind"] in {"document_claim", "code_fact", "alignment", "quality_finding", "explicit_inference"}
        assert node["source_refs"]
    for edge in model["edges"]:
        assert edge["from_node_id"] in node_ids
        assert edge["to_node_id"] in node_ids


def _assert_html_view(payload: dict, *, repo_path: str) -> None:
    view = payload["data"]["view"] if "data" in payload else payload
    html = view["content"]
    assert view["content_type"] == "text/html"
    assert "Architecture Relationship Overview" in html
    assert 'role="img" aria-label="Architecture relationship overview"' in html
    assert "Target Architecture from Documents" in html
    assert "Current Architecture from Code" in html
    assert "Gaps and Drift" in html
    assert "<script>alert" not in html
    assert str(repo_path) not in html
    assert re.search(r'data-node-id="[^"]+"', html)


def _assert_mermaid_view(payload: dict, *, model: dict, repo_path: str) -> None:
    view = payload["data"]["view"] if "data" in payload else payload
    mermaid = view["content"]
    assert view["content_type"] == "text/mermaid"
    assert mermaid.startswith("flowchart LR")
    assert "%% persisted_node_ids" in mermaid
    assert "<script>" not in mermaid
    assert str(repo_path) not in mermaid
    persisted_ids = set(model["summary"]["rendered_node_ids"])
    comment_ids = {line.split("=", 1)[1] for line in mermaid.splitlines() if line.startswith("%% n") and "=" in line}
    assert comment_ids
    assert comment_ids.issubset(persisted_ids)


def test_v27_phase53_renderer_escapes_unsafe_labels():
    model = {
        "schema_version": "v2.7",
        "workspace_id": "ws",
        "codebase_id": "cb",
        "snapshot_id": "snap",
        "summary": {"rendered_node_ids": ["target:unsafe"]},
        "target_nodes": [
            {
                "node_id": "target:unsafe",
                "node_type": "component",
                "label": "<script>alert('x')</script> Mermaid[bad]{bad}",
                "section": "target_from_documents",
                "source_kind": "document_claim",
                "source_refs": [{"type": "architecture_doc_claim", "claim_id": "claim_unsafe"}],
                "confidence": 0.8,
                "needs_review": [],
            }
        ],
        "current_nodes": [],
        "diff_nodes": [],
        "edges": [],
    }
    html = render_reconstructed_architecture_html(model)
    mermaid = render_reconstructed_architecture_mermaid(model)
    assert "&lt;script&gt;alert" in html
    assert "<script>alert" not in html
    assert "Mermaid(bad)(bad)" in mermaid
    assert "<script>" not in mermaid


def test_v27_phase53_reconstructed_architecture_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, snapshot_id, repo = _prepare(tmp_path, monkeypatch)
    service = _prepare_alignment_artifacts(workspace, workspace_id, codebase_id, snapshot_id)
    service.build_document_code_alignment(codebase_id)

    direct = service.build_reconstructed_architecture(codebase_id)
    assert architecture_reconstructed_model_path(workspace, codebase_id).exists()
    assert architecture_doc_view_path(workspace, codebase_id, "document_code_architecture_report.html").exists()
    assert architecture_doc_view_path(workspace, codebase_id, "document_code_architecture_diff.mmd").exists()
    _assert_reconstructed(direct, workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))
    _assert_html_view({"data": {"view": service.read_document_architecture_view(codebase_id, "document_code_architecture_report.html")}}, repo_path=str(repo))
    _assert_mermaid_view({"data": {"view": service.read_document_architecture_view(codebase_id, "document_code_architecture_diff.mmd")}}, model=direct, repo_path=str(repo))

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed/build")
    assert http_build.status_code == 200
    _assert_reconstructed(_v2(http_build.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed")
    assert http_read.status_code == 200
    _assert_reconstructed(_v2(http_read.json()), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    http_html = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/views/document_code_architecture_report.html")
    assert http_html.status_code == 200
    _assert_html_view(_v2(http_html.json()), repo_path=str(repo))

    http_mermaid = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/views/document_code_architecture_diff.mmd")
    assert http_mermaid.status_code == 200
    _assert_mermaid_view(_v2(http_mermaid.json()), model=direct, repo_path=str(repo))

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_payload = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_reconstructed", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_reconstructed(_v2(mcp_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))
    mcp_view = asyncio.run(dispatcher.call_tool("knowledge_code_architecture_doc_view", {"workspace_id": workspace_id, "codebase_id": codebase_id, "view_id": "document_code_architecture_report.html"}))
    _assert_html_view(_v2(mcp_view), repo_path=str(repo))

    assert knowledge_main(["code", "architecture", "docs-reconstructed", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    _assert_reconstructed(_v2(cli_payload), workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, repo_path=str(repo))

    assert knowledge_main(["code", "architecture", "docs-view", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--view-id", "document_code_architecture_diff.mmd"]) == 0
    cli_view = json.loads(capsys.readouterr().out)
    _assert_mermaid_view(_v2(cli_view), model=direct, repo_path=str(repo))


def test_v27_phase53_reconstruction_requires_alignment(tmp_path, monkeypatch):
    client, _workspace_root, workspace, workspace_id, codebase_id, snapshot_id, _repo = _prepare(tmp_path, monkeypatch)
    _prepare_alignment_artifacts(workspace, workspace_id, codebase_id, snapshot_id)

    response = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed/build")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "ARCHITECTURE_DOC_ALIGNMENT_NOT_BUILT"
