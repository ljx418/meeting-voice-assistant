from __future__ import annotations

import json
from pathlib import Path

from scripts.v5_7a_design_gate_evidence import OUTPUT_DIR, main


def test_v5_7a_design_gate_evidence_package_generation() -> None:
    assert main() == 0
    required = {
        "contract-audit.json",
        "execution-envelope.example.json",
        "sandbox-input-descriptor.example.json",
        "rollback-descriptor.example.json",
        "kill-switch-decision.example.json",
        "execution-evidence.example.json",
        "result-summary.json",
        "result-summary.md",
    }
    existing = {path.name for path in Path(OUTPUT_DIR).iterdir() if path.is_file()}
    assert required.issubset(existing)
    summary = json.loads((Path(OUTPUT_DIR) / "result-summary.json").read_text(encoding="utf-8"))
    audit = json.loads((Path(OUTPUT_DIR) / "contract-audit.json").read_text(encoding="utf-8"))
    assert summary["status"] == "PASS"
    assert summary["design_only"] is True
    assert summary["runtime_execution_enabled"] is False
    assert audit["blocking_findings"] == []

