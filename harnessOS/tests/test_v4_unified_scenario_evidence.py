from pathlib import Path


EVIDENCE_ROOT = Path("docs/design/V4.x/evidence/unified-experience")


def test_every_ux_case_has_required_evidence_summary_fields():
    for idx in range(1, 13):
        ux_id = f"UX-{idx:02d}"
        summary = EVIDENCE_ROOT / ux_id / "result-summary.md"
        assert summary.exists(), f"missing summary for {ux_id}"
        text = summary.read_text()
        for field in [
            f"ux_id: {ux_id}",
            "status:",
            "evidence_scope:",
            "evidence_refs:",
            "runtime_backed:",
            "deterministic_only:",
            "false_green_risk:",
            "notes:",
        ]:
            assert field in text


def test_multi_agent_scenarios_have_u7_provider_backed_evidence_without_false_green():
    for ux_id in ["UX-08", "UX-09", "UX-10"]:
        text = (EVIDENCE_ROOT / ux_id / "result-summary.md").read_text()
        assert "status: PASS" in text
        assert "evidence_scope: real_runtime" in text
        assert "deterministic_only: false" in text
        assert "false_green_risk: MEDIUM" in text
        assert (
            "does not prove production" in text
            or "does not prove autonomous" in text
            or "does not prove Agent executor" in text
        )


def test_root_summary_requires_manual_proceed_for_u6():
    text = (EVIDENCE_ROOT / "result-summary.md").read_text()
    assert "status: PASS" in text
    assert "u6_entry_recommendation: passed_after_u7_reality_recheck" in text
    assert "pass_count: 12" in text
    assert "partial_count: 0" in text
    assert "blocked_count: 0" in text
    assert "UX-12" in text
    assert "V4-U7" in text


def test_u5a_machine_readable_artifact_and_quality_evidence_exists():
    artifacts = Path("docs/design/V4.2/evidence/headless-interaction/artifacts.json")
    quality = Path("docs/design/V4.2/evidence/headless-interaction/quality.json")

    assert artifacts.exists()
    assert quality.exists()
    assert "producer_station_id" in artifacts.read_text()
    assert "lineage_refs" in artifacts.read_text()
    assert "station_id" in quality.read_text()
    assert "artifact_id" in quality.read_text()
