import json
from pathlib import Path

from scripts.v4_u9_final_acceptance import generate_u9_acceptance


OUTPUT_DIR = Path("docs/design/V4.x/evidence/final-human-acceptance")
V5_BRIEF = Path("docs/design/V5.x/v5_0_production_productization_planning_brief.md")


def test_u9_final_acceptance_generates_static_report(tmp_path: Path) -> None:
    v5_dir = tmp_path / "V5.x"

    report = generate_u9_acceptance(tmp_path, v5_dir)

    assert report["status"] == "PASS"
    assert (tmp_path / "u9-final-acceptance-report.html").exists()
    assert (tmp_path / "u9-final-acceptance-data.json").exists()
    assert (tmp_path / "u9-prd-spec-review.md").exists()
    assert (tmp_path / "u9-false-green-audit.md").exists()
    assert (v5_dir / "v5_0_production_productization_planning_brief.md").exists()

    html = (tmp_path / "u9-final-acceptance-report.html").read_text(encoding="utf-8")
    assert "V4-U9 最终人工验收与 V5 移交报告" in html
    assert "不新增运行时能力" in html
    assert "https://cdn" not in html
    assert "<script" not in html


def test_u9_final_acceptance_covers_all_ux_and_prd_paths() -> None:
    data = json.loads((OUTPUT_DIR / "u9-final-acceptance-data.json").read_text(encoding="utf-8"))

    assert data["status"] == "PASS"
    assert data["allowed_claim"] == (
        "V4-U9 complete: V4 dev/local final human acceptance and V5 handoff package ready for review."
    )
    assert len(data["ux_cases"]) == 12
    assert {case["status"] for case in data["ux_cases"]} == {"PASS"}
    assert all(item["status"] == "PASS" for item in data["prd_spec_review"])
    assert data["false_green_audit"]["status"] == "PASS"


def test_u9_v5_handoff_is_planning_only() -> None:
    data = json.loads((OUTPUT_DIR / "u9-final-acceptance-data.json").read_text(encoding="utf-8"))
    text = V5_BRIEF.read_text(encoding="utf-8")

    assert data["v5_handoff"]["status"] == "planned_future"
    assert "本文不实现 V5" in text
    assert "不改变 V4 的 dev/local closure 边界" in text
    assert "does not change V4 closure claims" in data["v5_handoff"]["boundary"]


def test_u9_false_green_audit_preserves_v4_boundaries() -> None:
    data = json.loads((OUTPUT_DIR / "u9-final-acceptance-data.json").read_text(encoding="utf-8"))
    checks = {item["name"]: item for item in data["false_green_audit"]["checks"]}

    assert checks["claim_guard"]["status"] == "PASS"
    assert checks["redaction"]["status"] == "PASS"
    assert checks["no_runtime_overclaim"]["details"]["agent_builder_not_executor"] is True
    assert checks["no_runtime_overclaim"]["details"]["provider_backed_not_production"] is True
