from __future__ import annotations

import json
from pathlib import Path

from data_service.code_assets.architecture_intent.diagram_claims import build_diagram_claims, read_diagram_claims
from data_service.code_assets.architecture_intent.paths import (
    architecture_intent_diagram_claim_summary_path,
    architecture_intent_diagram_claims_path,
    architecture_intent_diagram_relations_path,
)
from data_service.code_assets.architecture_intent.source_model import build_architecture_source_model


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _prepare_source_model(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repo"
    workspace = tmp_path / "workspace"
    _write(
        root / "docs/target.drawio",
        """<mxfile><diagram id="p1" name="目标架构"><mxGraphModel><root>
        <mxCell id="0"/><mxCell id="1" parent="0"/>
        <mxCell id="node1" value="Workflow Engine" vertex="1" parent="1"/>
        <mxCell id="node2" value="MCP Interface" vertex="1" parent="1"/>
        <mxCell id="edge1" source="node1" target="node2" edge="1" parent="1"/>
        <mxCell id="edge2" value="validates" source="node2" target="node1" edge="1" parent="1"/>
        </root></mxGraphModel></diagram></mxfile>""",
    )
    _write(
        root / "docs/architecture.md",
        """# Target Architecture

- Governance boundary must be visible.
- 禁止把文档 claim 当作 code fact。

```mermaid
graph TD
  Agent Runtime --> Workflow Engine
  Workflow Engine --> Artifact Store
```
""",
    )
    files = [
        {"path": "docs/target.drawio", "included": True, "line_range": [1, 1]},
        {"path": "docs/architecture.md", "included": True, "line_range": [1, 10]},
    ]
    build_architecture_source_model(
        workspace=workspace,
        workspace_id="ws",
        codebase_id="cb",
        snapshot_id="snap",
        root=root,
        files=files,
    )
    return workspace, "cb"


def test_phase92_builds_claims_and_relations_without_code_fact_overclaim(tmp_path: Path) -> None:
    workspace, codebase_id = _prepare_source_model(tmp_path)
    payload = build_diagram_claims(workspace=workspace, workspace_id="ws", codebase_id=codebase_id, snapshot_id="snap")

    assert payload["summary"]["claim_count"] >= 5
    assert payload["summary"]["relation_count"] >= 3
    assert architecture_intent_diagram_claims_path(workspace, codebase_id).exists()
    assert architecture_intent_diagram_relations_path(workspace, codebase_id).exists()
    assert architecture_intent_diagram_claim_summary_path(workspace, codebase_id).exists()

    claims = payload["claims"]
    relations = payload["relations"]
    assert any(row["label"] == "Workflow Engine" and row["claim_type"] == "workflow" for row in claims)
    assert any(row["claim_type"] == "public_interface" for row in claims)
    assert any(row["claim_type"] == "boundary" for row in claims)
    assert any(row["claim_type"] == "forbidden_claim" for row in claims)
    assert all(row["source_kind"] == "document_claim" for row in claims)
    assert all(row["confidence"] <= 0.75 for row in claims if row["source_block_type"] == "diagram_node")

    assert any(row["relation_type"] == "validates" for row in relations)
    unlabeled = [row for row in relations if row["source_locator"].get("cell_id") == "edge1"]
    assert unlabeled
    assert unlabeled[0]["needs_review"][0]["code"] == "UNLABELED_DIAGRAM_EDGE"
    assert all(row["semantic_limit"] == "not_runtime_call" for row in relations)
    assert not any(row["relation_type"] in {"runtime_calls", "data_flow", "control_flow"} for row in relations)

    reloaded = read_diagram_claims(workspace=workspace, codebase_id=codebase_id)
    assert reloaded["summary"]["claim_count"] == payload["summary"]["claim_count"]
    serialized = json.dumps(reloaded, ensure_ascii=False)
    assert "/Users/" not in serialized
    assert "<script" not in serialized.lower()


def test_phase92_token_like_markdown_stays_document_claim(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    workspace = tmp_path / "workspace"
    _write(root / "docs/notes.md", "- API Gateway target architecture\n")
    build_architecture_source_model(
        workspace=workspace,
        workspace_id="ws",
        codebase_id="cb",
        snapshot_id="snap",
        root=root,
        files=[{"path": "docs/notes.md", "included": True}],
    )
    payload = build_diagram_claims(workspace=workspace, workspace_id="ws", codebase_id="cb", snapshot_id="snap")
    assert payload["claims"]
    assert all(row["source_kind"] == "document_claim" for row in payload["claims"])
    assert not any(row.get("code_evidence_refs") for row in payload["claims"])
