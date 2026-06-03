from pathlib import Path


DOCS = [
    Path("docs/design/V4.x/v4_x_unified_development_plan.md"),
    Path("docs/design/V4.x/v4_x_unified_experience_completion_note.md"),
    Path("docs/design/V4.x/evidence/unified-experience/result-summary.md"),
    Path("docs/design/V4.x/v4_x_runtime_capability_matrix.md"),
]


def test_u5_substages_do_not_claim_unified_complete():
    plan = DOCS[0].read_text()
    for stage in ["V4-U5A", "V4-U5B", "V4-U5C", "V4-U5D"]:
        section = plan.split(f"##", 1)[-1]
        assert f"{stage} complete:" in plan
    assert "不要在 U5A/B/C/D 任一阶段声明 V4 unified complete" in plan


def test_completion_note_does_not_claim_u5_or_u6_complete():
    note = DOCS[1].read_text()
    assert "V4-U5C, V4-U5D, V4-U5, and final V4.x unified experience gate are not claimed" in note
    assert "V4-U5A complete: scenario evidence archive ready for review." in note
    assert "V4-U5B complete: experience state projection read-model ready for shared workflow heads." in note
    assert "V4-U5 complete: unified V4 user experience acceptance package ready for review" not in note


def test_forbidden_claims_are_only_listed_as_forbidden_or_not_proven():
    for path in DOCS:
        text = path.read_text()
        assert "Agent executor ready" not in text.replace("Agent executor ready", "Agent executor ready", 1) or (
            "禁止" in text or "does not prove" in text or "Forbidden" in text
        )
    root = DOCS[2].read_text()
    assert "does not prove complete Workflow Studio" in root
    assert "full multi-Agent orchestration" in root
