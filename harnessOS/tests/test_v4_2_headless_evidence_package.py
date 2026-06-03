"""V4.2-A headless evidence package tests."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.v4_2_headless_evidence import FORBIDDEN_TERMS, generate_evidence_package


EVIDENCE_DIR = Path("docs/design/V4.2/evidence/headless-interaction")


def test_evidence_package_contains_required_outputs() -> None:
    required = {
        "tui-transcript.txt",
        "workflow.yaml",
        "workflow.json",
        "workflow.schema.json",
        "workflow.drawio",
        "workflow_status.drawio",
        "artifact_lineage.drawio",
        "workflow_board.html",
        "artifacts.html",
        "quality.html",
        "evidence.html",
        "thin_web_console.html",
        "exported-runtime-result.json",
        "operation-evidence.json",
        "result-summary.md",
    }

    assert required.issubset({path.name for path in EVIDENCE_DIR.iterdir() if path.is_file()})


def test_evidence_package_is_backed_by_real_v41_workflow_path() -> None:
    runtime = json.loads((EVIDENCE_DIR / "exported-runtime-result.json").read_text(encoding="utf-8"))
    evidence = json.loads((EVIDENCE_DIR / "operation-evidence.json").read_text(encoding="utf-8"))

    assert runtime["source"] == "v4_1_local_workflow_path"
    assert runtime["status"] == "completed"
    assert len(runtime["nodes"]) == 9
    assert {artifact["name"] for artifact in runtime["artifacts"]} == {
        "AgentOS_总结.md",
        "前端低代码_总结.md",
        "项目复盘_总结.md",
        "总览总结.md",
        "quality_report.json",
    }
    assert {"workflow.folder_summary.apply", "workflow.folder_summary.publish", "workflow.folder_summary.run"}.issubset(
        {item["operation"] for item in evidence}
    )


def test_evidence_package_does_not_fabricate_generic_runtime_evidence() -> None:
    text = (EVIDENCE_DIR / "result-summary.md").read_text(encoding="utf-8")
    evidence = json.loads((EVIDENCE_DIR / "operation-evidence.json").read_text(encoding="utf-8"))

    assert "Generic controlled execution runtime is deferred to V4.2-B/C: PASS" in text
    assert all(item["operation"].startswith("workflow.folder_summary.") for item in evidence)
    assert "workflow.instance.start" not in json.dumps(evidence, ensure_ascii=False)
    assert "station.rerun" not in json.dumps(evidence, ensure_ascii=False)


def test_generated_package_can_be_rebuilt_with_real_fixture(tmp_path) -> None:
    manifest = generate_evidence_package(tmp_path)

    assert manifest["status"] == "completed"
    assert "workflow.drawio" in manifest["files"]
    assert "workflow_board.html" in manifest["files"]


def test_evidence_package_is_redacted() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in EVIDENCE_DIR.iterdir() if path.is_file())
    for term in FORBIDDEN_TERMS:
        assert term not in combined
