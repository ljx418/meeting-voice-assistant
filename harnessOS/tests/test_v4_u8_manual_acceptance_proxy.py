import json
from pathlib import Path

from scripts.v4_u8_manual_acceptance_proxy import generate_manual_acceptance_proxy


OUTPUT_DIR = Path("docs/design/V4.x/evidence/manual-acceptance")


def test_u8_manual_acceptance_proxy_generates_static_report(tmp_path: Path) -> None:
    report = generate_manual_acceptance_proxy(tmp_path)

    assert report["status"] == "PASS"
    assert (tmp_path / "u8-manual-acceptance-report.html").exists()
    assert (tmp_path / "u8-manual-acceptance-data.json").exists()
    html = (tmp_path / "u8-manual-acceptance-report.html").read_text(encoding="utf-8")
    assert "https://cdn" not in html
    assert "本报告只读取现有证据" in html
    assert "Agent executor" in html


def test_u8_manual_acceptance_proxy_checks_u7_and_ux12_evidence() -> None:
    data = json.loads((OUTPUT_DIR / "u8-manual-acceptance-data.json").read_text(encoding="utf-8"))
    checks = {item["check_id"]: item for item in data["checks"]}

    assert data["status"] == "PASS"
    assert checks["reality_check"]["status"] == "PASS"
    assert checks["claims_redaction"]["status"] == "PASS"
    assert checks["ux-08_provider_runtime"]["details"]["provider_invocation_count"] >= 7
    assert checks["ux-09_provider_runtime"]["details"]["provider_invocation_count"] >= 7
    assert checks["ux-10_provider_runtime"]["details"]["provider_invocation_count"] >= 12
    assert checks["ux12_real_llm_local_docs"]["details"]["scanner_actual_read_count"] > 0
    assert checks["ux12_real_llm_local_docs"]["details"]["provider_invocation_count"] > 0


def test_u8_manual_acceptance_proxy_no_false_green_boundaries() -> None:
    data = json.loads((OUTPUT_DIR / "u8-manual-acceptance-data.json").read_text(encoding="utf-8"))

    assert data["no_false_green"]["complete_web_studio"] is False
    assert data["no_false_green"]["agent_executor"] is False
    assert data["no_false_green"]["production_runtime"] is False
    assert data["no_false_green"]["unrestricted_orchestration"] is False
    assert "V4-U8 complete: V4 dev/local closure package ready for human acceptance." == data["allowed_claim"]
