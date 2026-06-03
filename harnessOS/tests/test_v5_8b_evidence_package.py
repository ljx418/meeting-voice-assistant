from __future__ import annotations

import json
from pathlib import Path

from scripts.v5_8b_distributed_coordination_evidence import build_evidence, write_evidence


def test_v5_8b_evidence_package_contains_real_source_evidence_and_boundaries(tmp_path: Path) -> None:
    evidence = build_evidence()
    write_evidence(evidence, tmp_path)

    data = json.loads((tmp_path / "coordination-evidence.json").read_text(encoding="utf-8"))
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    summary = (tmp_path / "result-summary.md").read_text(encoding="utf-8")

    assert data["status"] == "PASS"
    assert data["real_provider_backed_source_count"] == 3
    assert data["distributed_runtime_complete"] is False
    assert data["production_ready"] is False
    assert data["source_agent_can_mutate"] is False
    assert data["production_routes_added"] is False
    assert data["production_workers_started"] is False
    assert all(scenario["source_evidence"]["real_provider_backed"] is True for scenario in data["scenarios"])
    assert "No False Green" in summary
    assert "不证明完整分布式多 Agent 运行时" in html


def test_v5_8b_evidence_package_redacts_sensitive_terms(tmp_path: Path) -> None:
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
