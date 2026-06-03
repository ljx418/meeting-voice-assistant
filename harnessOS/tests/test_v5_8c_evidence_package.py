from __future__ import annotations

import json
from pathlib import Path

from scripts.v5_8c_lineage_recovery_evidence import build_evidence, write_evidence


def test_v5_8c_evidence_package_contains_lineage_and_readonly_report(tmp_path: Path) -> None:
    evidence = build_evidence()
    write_evidence(evidence, tmp_path)

    data = json.loads((tmp_path / "lineage-recovery-evidence.json").read_text(encoding="utf-8"))
    report = json.loads((tmp_path / "runtime-report-projection.json").read_text(encoding="utf-8"))
    html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert data["status"] == "PASS"
    assert data["source_evidence"]["real_provider_backed"] is True
    assert data["artifact_lineage"]
    assert data["distributed_runtime_complete"] is False
    assert data["production_ready"] is False
    assert report["readonly"] is True
    assert report["report_actions"] == ["view", "export"]
    assert "Artifact Lineage" in html


def test_v5_8c_evidence_package_redacts_sensitive_terms(tmp_path: Path) -> None:
    evidence = build_evidence()
    write_evidence(evidence, tmp_path)

    combined = "\n".join(path.read_text(encoding="utf-8") for path in tmp_path.rglob("*") if path.is_file())
    for forbidden in [
        "capability_token",
        "subscription_token",
        "Authorization",
        "Bearer",
        "raw_trace_payload",
        "raw_artifact_content",
        "raw_connector_payload",
        "raw prompt",
        "upstream signed URL",
    ]:
        assert forbidden not in combined
