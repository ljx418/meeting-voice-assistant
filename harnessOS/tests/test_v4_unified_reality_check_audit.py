import json
from pathlib import Path


AUDIT_DIR = Path("docs/design/V4.x/evidence/unified-experience/reality-check")


def test_reality_check_outputs_exist():
    for filename in [
        "index.html",
        "audit-data.json",
        "result-summary.md",
        "claims-audit.md",
        "evidence-inventory.json",
    ]:
        assert (AUDIT_DIR / filename).exists()


def test_reality_check_covers_ux_01_to_ux_11_with_required_fields():
    data = json.loads((AUDIT_DIR / "audit-data.json").read_text())
    cases = {case["ux_id"]: case for case in data["ux_cases"]}

    assert set(cases) == {f"UX-{index:02d}" for index in range(1, 13)}
    for case in cases.values():
        for field in [
            "status",
            "evidence_scope",
            "runtime_backed",
            "deterministic_only",
            "transcript_only",
            "report_only",
            "false_green_risk",
            "claim_risk",
            "evidence_refs",
            "commands_run",
            "missing_evidence",
            "notes",
        ]:
            assert field in case


def test_reality_check_allows_u6_after_u7_provider_backed_scenario_evidence():
    data = json.loads((AUDIT_DIR / "audit-data.json").read_text())

    assert data["recommendation"]["allow_enter_v4_u6"] is True
    assert data["recommendation"]["requires_human_proceed_decision"] is False
    assert data["recommendation"]["status_counts"]["PASS"] == 12
    assert data["recommendation"]["status_counts"]["PARTIAL"] == 0
    assert data["recommendation"]["high_false_green_risk_ux"] == []


def test_reality_check_tracks_real_llm_local_document_workflow_gate():
    data = json.loads((AUDIT_DIR / "audit-data.json").read_text())
    cases = {case["ux_id"]: case for case in data["ux_cases"]}

    if cases["UX-12"]["status"] == "PASS":
        assert cases["UX-12"]["evidence_scope"] == "real_runtime"
        assert cases["UX-12"]["runtime_backed"] is True
        assert cases["UX-12"]["false_green_risk"] == "LOW"
        assert not cases["UX-12"]["missing_evidence"]
    else:
        assert cases["UX-12"]["status"] == "BLOCKED"
        assert cases["UX-12"]["evidence_scope"] == "planned_contract"
        assert cases["UX-12"]["false_green_risk"] == "HIGH"
        assert "MiniMax or OpenAI-compatible provider invocation evidence" in cases["UX-12"]["missing_evidence"]


def test_reality_check_html_is_static_and_has_raw_links():
    html = (AUDIT_DIR / "index.html").read_text()

    assert "https://cdn" not in html
    assert "audit-data.json" in html
    assert "claims-audit.md" in html
    assert "evidence-inventory.json" in html
    assert "V4 Unified Experience Reality Check Audit" in html
