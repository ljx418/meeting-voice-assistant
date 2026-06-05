from pathlib import Path

from core.product_console.v8_final_acceptance import (
    DEFAULT_V89_EVIDENCE_DIR,
    build_v8_9_final_acceptance_readiness,
    write_v8_9_final_acceptance_framework,
)


def test_v8_9_allows_final_claim_when_v8_7_runtime_evidence_passes() -> None:
    data = build_v8_9_final_acceptance_readiness()
    assert data["status"] == "PASS"
    assert data["final_claim_allowed"] is True
    assert data["blockers"] == []
    assert data["stage_evidence"]["V8-4"]["status"] == "PASS"
    assert data["stage_evidence"]["V8-6"]["status"] == "PASS"
    assert data["stage_evidence"]["V8-7"]["status"] == "PASS"
    assert data["stage_evidence"]["V8-8"]["status"] == "PASS"


def test_v8_9_framework_evidence_outputs(tmp_path: Path) -> None:
    data = write_v8_9_final_acceptance_framework(tmp_path)
    assert data["status"] == "PASS"
    required = ["index.html", "final-readiness-data.json", "result-summary.md", "claims-scan.md", "redaction-scan.md"]
    assert [name for name in required if not (tmp_path / name).exists()] == []
    assert "status: PASS" in (tmp_path / "result-summary.md").read_text(encoding="utf-8")


def test_v8_9_default_evidence_dir_is_v8_design_path() -> None:
    assert DEFAULT_V89_EVIDENCE_DIR.as_posix().endswith("docs/design/V8.x/evidence/v8-9-final-acceptance-framework")
