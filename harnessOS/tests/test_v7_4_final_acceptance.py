from __future__ import annotations

import json
import subprocess
from pathlib import Path


OUT_DIR = Path("docs/design/V7.x/evidence/final-acceptance")


def test_v7_4_final_acceptance_script_generates_pass_package() -> None:
    subprocess.run(["./.venv/bin/python", "scripts/v7_4_final_acceptance.py"], check=True)

    required = [
        "index.html",
        "acceptance-data.json",
        "claims-scan.md",
        "redaction-scan.md",
        "result-summary.md",
    ]
    assert [name for name in required if not (OUT_DIR / name).exists()] == []
    data = json.loads((OUT_DIR / "acceptance-data.json").read_text(encoding="utf-8"))

    assert data["stage_id"] == "V7-4"
    assert data["status"] == "PASS"
    assert data["v7_allowed_claim"] == "V7 complete: small studio production pilot and explainable TUI baseline ready for review."
    assert data["stage_results"]["V7-3"]["status"] == "PASS"
    assert data["stage_results"]["V7-3"]["evidence_scope"] in {"real_runtime", "real_runtime_fixture"}
    assert data["stage_results"]["V7-3"]["provider_invocation_count"] > 0
    assert data["stage_results"]["V7-3"]["scanner_actual_read_count"] > 0
    assert data["missing_evidence"] == []
    assert data["claim_scan"] == "PASS"
    assert data["redaction_scan"] == "PASS"


def test_v7_4_dashboard_is_readonly() -> None:
    subprocess.run(["./.venv/bin/python", "scripts/v7_4_final_acceptance.py"], check=True)
    html = (OUT_DIR / "index.html").read_text(encoding="utf-8")

    assert "<form" not in html.lower()
    for copy in ["Apply", "Publish", "Execute", "Run"]:
        assert f">{copy}<" not in html
    assert "/v1/rpc" not in html
    assert "/v1/events/subscribe" not in html
