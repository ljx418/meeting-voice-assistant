from pathlib import Path


U5C = Path("docs/design/V4.x/v4_u5c_mission_console_closed_loop_plan.md")
U5D = Path("docs/design/V4.x/v4_u5d_review_console_evidence_chain_plan.md")
U5 = Path("docs/design/V4.x/v4_u5_scenario_path_acceptance_plan.md")
U6 = Path("docs/design/V4.x/v4_u6_unified_experience_gate_plan.md")
README = Path("docs/design/V4.x/00_README.md")
HISTORICAL_ACCEPTANCE = Path("docs/design/V4.x/harnessos_v4_unified_reframe_pack/04_acceptance_matrix.md")


def test_u5c_plan_requires_state_projection_and_user_confirmed_mutations():
    text = U5C.read_text(encoding="utf-8")

    for required in [
        "ExperienceStateProjection",
        "IntentCaptured",
        "SpecDrafted",
        "SchemaValidated",
        "DiffReady",
        "AwaitingConfirmation",
        "UserConfirmed",
        "EvidenceRecorded",
        "AvailableAction",
        "ForbiddenActionReason",
        "user_confirmed=true",
        "source=agent 不能执行 mutation",
        "Mission Console 不能被描述为 Agent executor",
    ]:
        assert required in text


def test_u5d_plan_keeps_evidence_chain_readonly_and_handoff_only():
    text = U5D.read_text(encoding="utf-8")

    for required in [
        "ReviewActionDTO",
        "target_refs",
        "EvidenceReportDTO",
        "view",
        "export",
        "open_handoff",
        "Evidence Chain 不出现 Apply / Publish / Approve / Reject / Execute / Run",
        "Evidence Chain 不出现 自动应用 / 自动发布 / Agent 已执行",
        "source=agent 不能 rerun",
    ]:
        assert required in text


def test_u5_and_u6_are_blocked_by_ux12_until_real_llm_evidence_exists():
    u5_text = U5.read_text(encoding="utf-8")
    u6_text = U6.read_text(encoding="utf-8")

    assert "UX-01 到 UX-12" in u5_text
    assert "UX-12 必须 real_llm 或明确 BLOCKED" in u5_text
    assert "无 FAIL / BLOCKED" in u6_text
    assert "MiniMax" in u6_text
    assert "provider_config_source" in u6_text
    assert "无 LLM key 时不得标记 PASS" in u6_text


def test_legacy_ux11_acceptance_snapshot_is_marked_deprecated():
    readme_text = README.read_text(encoding="utf-8")
    historical_text = HISTORICAL_ACCEPTANCE.read_text(encoding="utf-8")

    assert "canonical 验收矩阵" in readme_text
    assert "UX-01 到 UX-12" in readme_text
    assert "historical/deprecated" in historical_text
    assert "不得用本文件绕过 UX-12" in historical_text
