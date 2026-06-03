"""V4.2-C controlled runtime evidence package tests."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.v4_2_controlled_runtime_evidence import FORBIDDEN_TERMS, generate_controlled_runtime_evidence


EVIDENCE_DIR = Path("docs/design/V4.2/evidence/controlled-runtime")


def test_controlled_runtime_evidence_package_contains_required_outputs() -> None:
    required = {
        "tui-transcript.txt",
        "workflow.yaml",
        "runtime-start-result.json",
        "station-rerun-result.json",
        "attempt-history.json",
        "downstream-stale.json",
        "runtime-evidence.json",
        "workflow_status.drawio",
        "rerun_history.drawio",
        "runtime_report.html",
        "evidence.html",
        "result-summary.md",
    }

    assert required.issubset({path.name for path in EVIDENCE_DIR.iterdir() if path.is_file()})


def test_controlled_runtime_evidence_package_uses_real_runtime_results() -> None:
    start = json.loads((EVIDENCE_DIR / "runtime-start-result.json").read_text(encoding="utf-8"))
    rerun = json.loads((EVIDENCE_DIR / "station-rerun-result.json").read_text(encoding="utf-8"))
    evidence = json.loads((EVIDENCE_DIR / "runtime-evidence.json").read_text(encoding="utf-8"))

    assert start["backed_by"] == "generic_controlled_runtime"
    assert start["status"] == "completed"
    assert len(start["nodes"]) == 9
    assert rerun["status"] == "waiting_user_confirmation"
    assert rerun["downstream_stale"]
    assert {"workflow.instance.start", "station.rerun", "workflow.instance.continue_downstream"}.issubset(
        {item["operation"] for item in evidence}
    )
    assert all(item["user_confirmed"] is True for item in evidence)
    assert all(item["source"] != "agent" for item in evidence)


def test_controlled_runtime_evidence_package_can_be_rebuilt(tmp_path) -> None:
    manifest = generate_controlled_runtime_evidence(tmp_path)

    assert manifest["status"] == "completed"
    assert "workflow_status.drawio" in manifest["files"]
    assert "runtime_report.html" in manifest["files"]


def test_controlled_runtime_evidence_package_is_redacted() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in EVIDENCE_DIR.iterdir() if path.is_file())
    for term in FORBIDDEN_TERMS:
        assert term not in combined
