from __future__ import annotations

import json
from pathlib import Path

from data_service.code_assets.architecture_intent.diagram_claims import build_diagram_claims
from data_service.code_assets.architecture_intent.diagram_verification import build_diagram_code_verification, read_diagram_code_verification
from data_service.code_assets.architecture_intent.intent_inference import build_intent_inference
from data_service.code_assets.architecture_intent.paths import (
    architecture_intent_architecture_diff_path,
    architecture_intent_diagram_code_alignment_path,
    architecture_intent_undocumented_code_facts_path,
    architecture_intent_verification_summary_path,
)
from data_service.code_assets.architecture_intent.proof_graph import build_code_proof_graph
from data_service.code_assets.architecture_intent.source_model import build_architecture_source_model


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _prepare_intent(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repo"
    workspace = tmp_path / "workspace"
    _write(
        root / "docs/arch.md",
        """# Target Architecture

- HTTP API public interface exposes workflow capability.
- Runtime workflow uses runtime descriptor evidence only.
- Quality acceptance gate is covered by tests.
- Provider adapter boundary is configured by manifest.
- 禁止把架构图关系写成运行时调用图。
""",
    )
    _write(root / "backend/api.py", "def http_api_handler():\n    return {'ok': True}\n")
    _write(root / "backend/workflow.py", "def run_workflow():\n    return True\n")
    _write(root / "config/provider.yaml", "provider: local\nadapter: manifest\n")
    _write(root / "tests/test_quality.py", "def test_quality_gate():\n    assert True\n")
    _write(root / "runtime/runtime_descriptor.json", '{"runtime": "descriptor only"}\n')
    files = [
        {"path": "docs/arch.md", "included": True},
        {"path": "backend/api.py", "included": True},
        {"path": "backend/workflow.py", "included": True},
        {"path": "config/provider.yaml", "included": True},
        {"path": "tests/test_quality.py", "included": True},
        {"path": "runtime/runtime_descriptor.json", "included": True},
    ]
    build_architecture_source_model(workspace=workspace, workspace_id="ws", codebase_id="cb", snapshot_id="snap", root=root, files=files)
    build_diagram_claims(workspace=workspace, workspace_id="ws", codebase_id="cb", snapshot_id="snap")
    build_code_proof_graph(workspace=workspace, workspace_id="ws", codebase_id="cb", snapshot_id="snap")
    build_intent_inference(workspace=workspace, workspace_id="ws", codebase_id="cb", snapshot_id="snap")
    return workspace, "cb"


def test_phase95_builds_diagram_code_verification_with_hard_gates(tmp_path: Path) -> None:
    workspace, codebase_id = _prepare_intent(tmp_path)
    payload = build_diagram_code_verification(workspace=workspace, workspace_id="ws", codebase_id=codebase_id, snapshot_id="snap")

    assert payload["summary"]["verification_count"] > 0
    assert payload["summary"]["status_counts"].get("accepted", 0) > 0
    assert payload["summary"]["undocumented_code_fact_count"] > 0
    assert payload["summary"]["accepted_gate_violation_count"] == 0
    assert payload["summary"]["token_only_accepted_count"] == 0
    assert architecture_intent_diagram_code_alignment_path(workspace, codebase_id).exists()
    assert architecture_intent_undocumented_code_facts_path(workspace, codebase_id).exists()
    assert architecture_intent_architecture_diff_path(workspace, codebase_id).exists()
    assert architecture_intent_verification_summary_path(workspace, codebase_id).exists()

    accepted = [row for row in payload["alignments"] if row["match_status"] == "accepted"]
    assert accepted
    assert all(row["match_strategy"] != "token_overlap_only" for row in accepted)
    assert all(row["confidence"] >= 0.80 for row in accepted)
    assert all(row["document_evidence_refs"] and row["code_evidence_refs"] for row in accepted)
    assert all(all((row["accepted_gate"] or {}).values()) for row in accepted)
    assert all(row["match_status"] != "accepted" for row in payload["alignments"] if row["match_strategy"] == "token_overlap_only")

    reloaded = read_diagram_code_verification(workspace=workspace, codebase_id=codebase_id)
    assert reloaded["summary"]["verification_count"] == payload["summary"]["verification_count"]
    serialized = json.dumps(reloaded, ensure_ascii=False)
    assert "/Users/" not in serialized
    assert "/private/tmp" not in serialized
