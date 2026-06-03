from __future__ import annotations

import json
from pathlib import Path

from scripts.v5_8e_final_acceptance import build_acceptance, write_acceptance


def test_v5_8e_final_acceptance_passes_with_all_stage_and_scenario_evidence(tmp_path: Path) -> None:
    data = build_acceptance()
    write_acceptance(data, tmp_path)

    saved = json.loads((tmp_path / "final-acceptance-data.json").read_text(encoding="utf-8"))
    html = (tmp_path / "index.html").read_text(encoding="utf-8")

    assert saved["status"] == "PASS"
    assert saved["distributed_runtime_slice_ready_for_review"] is True
    assert saved["full_multi_agent_orchestration_ready"] is False
    assert saved["agent_executor_ready"] is False
    assert saved["production_controlled_executor_ready"] is False
    assert saved["source_agent_can_mutate"] is False
    assert all(item["status"] == "PASS" for item in saved["stage_refs"])
    assert all(item["status"] == "PASS" for item in saved["scenario_refs"])
    assert saved["claim_violations"] == []
    assert "V5-8E 最终验收包" in html


def test_v5_8e_final_acceptance_outputs_no_forbidden_secret_terms(tmp_path: Path) -> None:
    data = build_acceptance()
    write_acceptance(data, tmp_path)

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
