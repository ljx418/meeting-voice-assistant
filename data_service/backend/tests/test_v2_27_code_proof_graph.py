from __future__ import annotations

import json
from pathlib import Path

from data_service.code_assets.architecture_intent.diagram_claims import build_diagram_claims
from data_service.code_assets.architecture_intent.paths import (
    architecture_intent_evidence_bundles_path,
    architecture_intent_proof_edges_path,
    architecture_intent_proof_graph_summary_path,
    architecture_intent_proof_nodes_path,
)
from data_service.code_assets.architecture_intent.proof_graph import build_code_proof_graph, read_code_proof_graph
from data_service.code_assets.architecture_intent.source_model import build_architecture_source_model


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _prepare_claims(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repo"
    workspace = tmp_path / "workspace"
    _write(root / "docs/arch.md", "# Target Architecture\n\n- Runtime workflow validates artifact evidence.\n")
    _write(root / "backend/service.py", "def run():\n    return True\n")
    _write(root / "config/workflow.yaml", "workflow: demo\n")
    _write(root / "tests/test_runtime.py", "def test_run():\n    assert True\n")
    _write(root / "runtime/execution_trace.json", '{"runtime": "descriptor only"}\n')
    build_architecture_source_model(
        workspace=workspace,
        workspace_id="ws",
        codebase_id="cb",
        snapshot_id="snap",
        root=root,
        files=[
            {"path": "docs/arch.md", "included": True},
            {"path": "backend/service.py", "included": True},
            {"path": "config/workflow.yaml", "included": True},
            {"path": "tests/test_runtime.py", "included": True},
            {"path": "runtime/execution_trace.json", "included": True},
        ],
    )
    build_diagram_claims(workspace=workspace, workspace_id="ws", codebase_id="cb", snapshot_id="snap")
    return workspace, "cb"


def test_phase93_builds_proof_graph_with_safe_semantics(tmp_path: Path) -> None:
    workspace, codebase_id = _prepare_claims(tmp_path)
    payload = build_code_proof_graph(workspace=workspace, workspace_id="ws", codebase_id=codebase_id, snapshot_id="snap")

    assert payload["summary"]["proof_node_count"] > 0
    assert payload["summary"]["proof_edge_count"] > 0
    assert payload["summary"]["evidence_bundle_count"] > 0
    assert payload["summary"]["forbidden_edge_count"] == 0
    assert architecture_intent_proof_nodes_path(workspace, codebase_id).exists()
    assert architecture_intent_proof_edges_path(workspace, codebase_id).exists()
    assert architecture_intent_evidence_bundles_path(workspace, codebase_id).exists()
    assert architecture_intent_proof_graph_summary_path(workspace, codebase_id).exists()

    node_types = {node["node_type"] for node in payload["nodes"]}
    assert {"document_claim", "code_file", "config_fact", "test_fact", "runtime_descriptor"} <= node_types
    assert any(edge["edge_type"] == "documented_by" for edge in payload["edges"])
    assert any(edge["edge_type"] == "defined_by" for edge in payload["edges"])
    assert any(edge["edge_type"] == "configured_by" for edge in payload["edges"])
    assert any(edge["edge_type"] == "tested_by" for edge in payload["edges"])
    assert any(edge["edge_type"] == "described_by" for edge in payload["edges"])
    assert not any(edge["edge_type"] in {"runtime_calls", "data_flow", "control_flow", "type_inferred_dependency", "runtime_observed"} for edge in payload["edges"])
    assert not any(edge["semantic_limit"] == "runtime_observed" for edge in payload["edges"])
    assert all(node["semantic_limit"] == "descriptor_only" for node in payload["nodes"] if node["node_type"] == "runtime_descriptor")

    reloaded = read_code_proof_graph(workspace=workspace, codebase_id=codebase_id)
    assert reloaded["summary"]["proof_node_count"] == payload["summary"]["proof_node_count"]
    serialized = json.dumps(reloaded, ensure_ascii=False)
    assert "/Users/" not in serialized
    assert "/private/tmp" not in serialized
