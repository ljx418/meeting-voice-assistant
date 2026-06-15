from __future__ import annotations

import json
from pathlib import Path

from data_service.code_assets.architecture_intent.diagram_claims import build_diagram_claims
from data_service.code_assets.architecture_intent.intent_inference import build_intent_inference, read_intent_inference
from data_service.code_assets.architecture_intent.paths import (
    architecture_intent_candidates_path,
    architecture_intent_counter_evidence_path,
    architecture_intent_inference_summary_path,
)
from data_service.code_assets.architecture_intent.proof_graph import build_code_proof_graph
from data_service.code_assets.architecture_intent.source_model import build_architecture_source_model


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _prepare_proof_graph(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repo"
    workspace = tmp_path / "workspace"
    _write(
        root / "docs/arch.md",
        """# Target Architecture

- Public API capability exposes workflow evidence through HTTP and MCP.
- Runtime workflow validates artifact evidence but is not a runtime trace.
- Storage artifact persistence is governed by acceptance gates.
- Provider adapter boundary keeps unsupported providers as unavailable.
- Quality gate blocks claims without evidence.
- 禁止把文档图当作运行时调用图。
""",
    )
    _write(root / "backend/service.py", "def run_workflow():\n    return True\n")
    _write(root / "backend/api.py", "def api_handler():\n    return run_workflow()\n")
    _write(root / "config/provider.yaml", "provider: local\nartifact_store: workspace\n")
    _write(root / "tests/test_runtime.py", "def test_run_workflow():\n    assert True\n")
    _write(root / "runtime/execution_descriptor.json", '{"runtime": "descriptor only"}\n')
    files = [
        {"path": "docs/arch.md", "included": True},
        {"path": "backend/service.py", "included": True},
        {"path": "backend/api.py", "included": True},
        {"path": "config/provider.yaml", "included": True},
        {"path": "tests/test_runtime.py", "included": True},
        {"path": "runtime/execution_descriptor.json", "included": True},
    ]
    build_architecture_source_model(workspace=workspace, workspace_id="ws", codebase_id="cb", snapshot_id="snap", root=root, files=files)
    build_diagram_claims(workspace=workspace, workspace_id="ws", codebase_id="cb", snapshot_id="snap")
    build_code_proof_graph(workspace=workspace, workspace_id="ws", codebase_id="cb", snapshot_id="snap")
    return workspace, "cb"


def test_phase94_builds_intent_candidates_with_counter_evidence(tmp_path: Path) -> None:
    workspace, codebase_id = _prepare_proof_graph(tmp_path)
    payload = build_intent_inference(workspace=workspace, workspace_id="ws", codebase_id=codebase_id, snapshot_id="snap")

    assert payload["summary"]["intent_candidate_count"] > 0
    assert payload["summary"]["counter_evidence_count"] >= 0
    assert payload["summary"]["llm_field_count"] == 0
    assert architecture_intent_candidates_path(workspace, codebase_id).exists()
    assert architecture_intent_counter_evidence_path(workspace, codebase_id).exists()
    assert architecture_intent_inference_summary_path(workspace, codebase_id).exists()

    candidates = payload["intent_candidates"]
    assert any(candidate["intent_type"] == "workflow" for candidate in candidates)
    assert any(candidate["intent_type"] == "public_surface_strategy" for candidate in candidates)
    assert all(candidate["evidence_bundle_refs"] or candidate["needs_review"] for candidate in candidates)
    assert all(recommendation["evidence_bundle_refs"] or recommendation["needs_review"] for candidate in candidates for recommendation in candidate["recommendations"])
    assert not all(candidate["status"] == "accepted" for candidate in candidates)
    assert all("llm" not in json.dumps(candidate).lower() for candidate in candidates)

    reloaded = read_intent_inference(workspace=workspace, codebase_id=codebase_id)
    assert reloaded["summary"]["intent_candidate_count"] == payload["summary"]["intent_candidate_count"]
    serialized = json.dumps(reloaded, ensure_ascii=False)
    assert "/Users/" not in serialized
    assert "/private/tmp" not in serialized
