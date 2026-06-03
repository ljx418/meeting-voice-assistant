from __future__ import annotations

import json
from pathlib import Path

from scripts.v5_6_thin_web_console_evidence import OUTPUT_DIR, main


def test_v5_6_evidence_package_generation() -> None:
    assert main() == 0
    required = {
        "thin-web-console.html",
        "thin-web-console-state.json",
        "runtime-report-panel.json",
        "evidence-review-panel.json",
        "audit-export-panel.json",
        "external-app-admin-panel.json",
        "manual-confirmation-dialog.json",
        "network-assertions.json",
        "result-summary.md",
        "result-summary.json",
    }
    existing = {path.name for path in Path(OUTPUT_DIR).iterdir() if path.is_file()}
    assert required.issubset(existing)
    summary = json.loads((Path(OUTPUT_DIR) / "result-summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "PASS"
    assert summary["evidence_scope"] == "real_v5_devlocal_evidence"

