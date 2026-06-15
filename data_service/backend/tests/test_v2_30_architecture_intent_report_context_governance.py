from __future__ import annotations

import hashlib
import json
from pathlib import Path

from data_service.code_assets.architecture_intent.context_pack import build_architecture_context_pack_v4, read_architecture_context_pack_v4
from data_service.code_assets.architecture_intent.diagram_claims import build_diagram_claims
from data_service.code_assets.architecture_intent.diagram_verification import build_diagram_code_verification, read_diagram_code_verification
from data_service.code_assets.architecture_intent.governance import (
    confirm_architecture_target,
    read_architecture_governance,
    revoke_architecture_confirmation,
)
from data_service.code_assets.architecture_intent.intent_inference import build_intent_inference
from data_service.code_assets.architecture_intent.paths import (
    architecture_context_pack_v4_json_path,
    architecture_context_pack_v4_markdown_path,
    architecture_intent_diff_mermaid_path,
    architecture_intent_report_html_path,
    architecture_intent_report_json_path,
)
from data_service.code_assets.architecture_intent.proof_graph import build_code_proof_graph
from data_service.code_assets.architecture_intent.report import REPORT_SECTIONS, build_architecture_intent_report, read_architecture_intent_report
from data_service.code_assets.architecture_intent.source_model import build_architecture_source_model


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _prepare_verification(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repo"
    workspace = tmp_path / "workspace"
    _write(
        root / "docs/arch.md",
        """# Target Architecture

- HTTP API public interface exposes workflow capability.
- Runtime workflow uses runtime descriptor evidence only.
- Quality acceptance gate is covered by tests.
- Provider adapter boundary is configured by manifest.
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
    build_diagram_code_verification(workspace=workspace, workspace_id="ws", codebase_id="cb", snapshot_id="snap")
    return workspace, "cb"


def test_phase96_report_context_and_governance_hash_gate(tmp_path: Path) -> None:
    workspace, codebase_id = _prepare_verification(tmp_path)
    source_artifacts = sorted((workspace / "assets" / "codebase" / codebase_id / "architecture" / "intent").glob("*/*.json*"))
    before_hash = {path: _sha(path) for path in source_artifacts if "governance" not in path.parts and "report" not in path.parts and "context" not in path.parts}

    verification = read_diagram_code_verification(workspace=workspace, codebase_id=codebase_id)
    target_id = verification["alignments"][0]["verification_id"]
    confirm_architecture_target(workspace=workspace, workspace_id="ws", codebase_id=codebase_id, snapshot_id="snap", target_type="diagram_code_verification", target_id=target_id, note="accepted for test")
    governance = read_architecture_governance(workspace=workspace, codebase_id=codebase_id)
    assert governance["summary"]["confirmed_fact_count"] == 1
    revoke_architecture_confirmation(workspace=workspace, workspace_id="ws", codebase_id=codebase_id, snapshot_id="snap", target_type="diagram_code_verification", target_id=target_id, note="revoke for test")
    governance = read_architecture_governance(workspace=workspace, codebase_id=codebase_id)
    assert governance["summary"]["confirmed_fact_count"] == 0
    after_hash = {path: _sha(path) for path in before_hash}
    assert before_hash == after_hash

    context = build_architecture_context_pack_v4(workspace=workspace, workspace_id="ws", codebase_id=codebase_id, snapshot_id="snap", mode="architecture_review")
    assert architecture_context_pack_v4_json_path(workspace, codebase_id).exists()
    assert architecture_context_pack_v4_markdown_path(workspace, codebase_id).exists()
    assert context["context_pack"]["mode"] == "architecture_review"
    assert all(rec["evidence_refs"] or rec["needs_review"] for rec in context["context_pack"]["recommendations"])

    report = build_architecture_intent_report(workspace=workspace, workspace_id="ws", codebase_id=codebase_id, snapshot_id="snap")
    assert architecture_intent_report_json_path(workspace, codebase_id).exists()
    assert architecture_intent_report_html_path(workspace, codebase_id).exists()
    assert architecture_intent_diff_mermaid_path(workspace, codebase_id).exists()
    html = report["html"]
    mermaid = report["mermaid"]
    assert html.startswith("<!doctype html>")
    assert all(section in html for section in REPORT_SECTIONS)
    assert "flowchart TD" in mermaid
    report_node_ids = {node["node_id"] for node in report["report"]["nodes"]}
    assert report_node_ids
    assert len([line for line in mermaid.splitlines() if line.strip().startswith("n_")]) <= len(report_node_ids)

    reloaded = read_architecture_intent_report(workspace=workspace, codebase_id=codebase_id)
    pack = read_architecture_context_pack_v4(workspace=workspace, codebase_id=codebase_id)
    serialized = json.dumps({"report": reloaded, "pack": pack, "governance": governance}, ensure_ascii=False)
    assert "/Users/" not in serialized
    assert "/private/tmp" not in serialized
