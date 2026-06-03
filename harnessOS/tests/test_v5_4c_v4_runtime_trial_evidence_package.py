from __future__ import annotations

import json
from pathlib import Path

from scripts.v5_4c_existing_v4_runtime_trial_evidence import FORBIDDEN_TERMS, generate_existing_v4_runtime_trial_evidence


def test_v5_4c_evidence_package_can_be_generated(tmp_path) -> None:
    manifest = generate_existing_v4_runtime_trial_evidence(tmp_path)

    assert manifest["status"] == "completed"
    assert "runtime-report.html" in manifest["files"]
    assert "v5-4c-bridge-evidence.json" in manifest["files"]


def test_v5_4c_evidence_package_is_complete() -> None:
    evidence_dir = Path("docs/design/V5.x/evidence/v5-4c-existing-v4-runtime-trial")
    required = {
        "tui-transcript.txt",
        "runtime-start-result.json",
        "runtime-failed-result.json",
        "station-rerun-result.json",
        "continue-downstream-result.json",
        "source-agent-denial.json",
        "existing-runtime-evidence.json",
        "v5-4c-bridge-evidence.json",
        "runtime-report.html",
        "evidence-chain.html",
        "runtime-bridge.drawio",
        "result-summary.md",
    }

    assert required.issubset({path.name for path in evidence_dir.iterdir() if path.is_file()})


def test_v5_4c_evidence_package_uses_real_devlocal_runtime() -> None:
    evidence_dir = Path("docs/design/V5.x/evidence/v5-4c-existing-v4-runtime-trial")
    start = json.loads((evidence_dir / "runtime-start-result.json").read_text(encoding="utf-8"))
    rerun = json.loads((evidence_dir / "station-rerun-result.json").read_text(encoding="utf-8"))
    denial = json.loads((evidence_dir / "source-agent-denial.json").read_text(encoding="utf-8"))

    assert start["runtime_result"]["backed_by"] == "generic_controlled_runtime"
    assert start["bridge_evidence"]["runtime_backed"] is True
    assert start["bridge_evidence"]["devlocal_only"] is True
    assert rerun["runtime_result"]["downstream_stale"]
    assert denial["status"] == "blocked"
    assert denial["blocked_reason"] == "source_agent_cannot_execute_mutation"


def test_v5_4c_evidence_package_is_redacted() -> None:
    evidence_dir = Path("docs/design/V5.x/evidence/v5-4c-existing-v4-runtime-trial")
    combined = "\n".join(path.read_text(encoding="utf-8") for path in evidence_dir.iterdir() if path.is_file())
    for term in FORBIDDEN_TERMS:
        assert term not in combined
