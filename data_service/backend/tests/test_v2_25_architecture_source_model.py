from __future__ import annotations

import json
from pathlib import Path

from data_service.code_assets.architecture_intent.paths import (
    architecture_intent_diagram_cells_path,
    architecture_intent_source_blocks_path,
    architecture_intent_source_summary_path,
    architecture_intent_sources_path,
)
from data_service.code_assets.architecture_intent.source_model import build_architecture_source_model, read_architecture_source_model


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_phase91_source_model_classifies_sources_and_writes_artifacts(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    workspace = tmp_path / "workspace"
    _write(root / "README.md", "# Project\n\n```mermaid\ngraph TD\nA-->B\n```\n")
    _write(root / "docs/V2_25_TARGET_ARCHITECTURE.md", "# Target\n\n- Runtime boundary\n| A | B |\n")
    _write(
        root / "docs/target.drawio",
        """<mxfile><diagram id="p1" name="目标架构"><mxGraphModel><root>
        <mxCell id="0"/><mxCell id="1" parent="0"/>
        <mxCell id="node1" value="Workflow Engine" vertex="1" parent="1"/>
        <mxCell id="edge1" source="node1" target="node2" edge="1" parent="1"/>
        </root></mxGraphModel></diagram></mxfile>""",
    )
    _write(root / "backend/service.py", "def handler():\n    return 1\n")
    _write(root / "tests/test_service.py", "def test_handler():\n    assert True\n")
    _write(root / "pyproject.toml", "[tool.test]\n")
    _write(root / "runtime/execution_trace.json", '{"ok": true}\n')
    files = [
        {"path": "README.md", "included": True, "line_range": [1, 5]},
        {"path": "docs/V2_25_TARGET_ARCHITECTURE.md", "included": True, "line_range": [1, 3]},
        {"path": "docs/target.drawio", "included": True, "line_range": [1, 1]},
        {"path": "backend/service.py", "included": True, "line_range": [1, 2]},
        {"path": "tests/test_service.py", "included": True, "line_range": [1, 2]},
        {"path": "pyproject.toml", "included": True, "line_range": [1, 1]},
        {"path": "runtime/execution_trace.json", "included": True, "line_range": [1, 1]},
    ]

    payload = build_architecture_source_model(
        workspace=workspace,
        workspace_id="ws",
        codebase_id="cb",
        snapshot_id="snap",
        root=root,
        files=files,
    )

    summary = payload["summary"]
    assert summary["source_count"] == 7
    assert summary["source_type_counts"]["markdown"] >= 2
    assert summary["source_type_counts"]["drawio"] == 1
    assert summary["source_type_counts"]["code"] == 1
    assert summary["source_type_counts"]["test"] == 1
    assert summary["source_type_counts"]["config"] == 1
    assert summary["source_type_counts"]["runtime_descriptor"] == 1
    assert summary["diagram_cell_count"] >= 2
    assert summary["source_block_count"] >= 3

    sources = payload["sources"]
    assert {row["authority_role"] for row in sources} >= {"target", "implementation"}
    runtime = next(row for row in sources if row["source_type"] == "runtime_descriptor")
    assert runtime["needs_review"][0]["code"] == "RUNTIME_DESCRIPTOR_ONLY"
    assert all(not row["path"].startswith("/") for row in sources)

    cells = payload["diagram_cells"]
    assert any(cell["label"] == "Workflow Engine" for cell in cells)
    assert all("cell_id" in cell["locator"] for cell in cells)

    blocks = payload["source_blocks"]
    assert any(block["block_type"] == "mermaid" for block in blocks)
    assert any(block["block_type"] == "heading" for block in blocks)

    assert architecture_intent_sources_path(workspace, "cb").exists()
    assert architecture_intent_source_blocks_path(workspace, "cb").exists()
    assert architecture_intent_diagram_cells_path(workspace, "cb").exists()
    assert architecture_intent_source_summary_path(workspace, "cb").exists()

    reloaded = read_architecture_source_model(workspace=workspace, codebase_id="cb")
    assert reloaded["summary"]["source_count"] == summary["source_count"]
    assert len(reloaded["diagram_cells"]) == len(cells)


def test_phase91_source_model_redacts_absolute_paths_and_skips_unsafe_records(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    workspace = tmp_path / "workspace"
    _write(root / "docs/plan.md", "# Plan\n\n- temp workspace `/private/tmp`\n")
    payload = build_architecture_source_model(
        workspace=workspace,
        workspace_id="ws",
        codebase_id="cb",
        snapshot_id="snap",
        root=root,
        files=[
            {"path": "/Users/example/secret.md", "included": True},
            {"path": "../escape.md", "included": True},
            {"path": "docs/plan.md", "included": True},
        ],
    )

    serialized = json.dumps(payload, ensure_ascii=False)
    assert "/Users/example" not in serialized
    assert "/private/tmp" not in serialized
    assert "../escape" not in serialized
    assert payload["summary"]["source_count"] == 1
    assert payload["sources"][0]["path"] == "docs/plan.md"
