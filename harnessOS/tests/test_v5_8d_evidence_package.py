from __future__ import annotations

import json
from pathlib import Path

from scripts.v5_8d_policy_observability_evidence import build_evidence, write_evidence


def test_v5_8d_evidence_package_contains_policy_credential_and_audit_projection(tmp_path: Path) -> None:
    evidence = build_evidence()
    write_evidence(evidence, tmp_path)

    data = json.loads((tmp_path / "policy-observability-evidence.json").read_text(encoding="utf-8"))
    package = json.loads((tmp_path / "audit-export-projection.json").read_text(encoding="utf-8"))

    assert data["status"] == "PASS"
    assert data["source_evidence"]["real_provider_backed"] is True
    assert data["policy_credential_decision"]["worker_credential_refs"]
    assert data["distributed_runtime_complete"] is False
    assert data["production_ready"] is False
    assert package["readonly"] is True
    assert package["report_actions"] == ["view", "export"]
    assert len(package["audit_events"]) >= 2


def test_v5_8d_evidence_package_redacts_sensitive_terms(tmp_path: Path) -> None:
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
