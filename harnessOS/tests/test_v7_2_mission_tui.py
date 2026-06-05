from __future__ import annotations

import json
import subprocess
from pathlib import Path

from core.product_console.v7_2_mission_tui import build_mission_tui_state, render_mission_tui_text, scan_mission_tui_output


GOAL = "递归总结 Desktop/技术分享 下的 Markdown 技术文档"
OUT_DIR = Path("docs/design/V7.x/evidence/v7-2-explainable-tui")


def test_harness_tui_command_exists_and_accepts_natural_language_goal() -> None:
    result = subprocess.run(["./.venv/bin/python", "-m", "cli.main", "tui", GOAL], check=True, capture_output=True, text=True)

    assert result.returncode == 0
    assert GOAL in result.stdout
    assert "HarnessOS Mission TUI" in result.stdout


def test_tui_renders_state_timeline() -> None:
    text = render_mission_tui_text(build_mission_tui_state(GOAL))

    for state in ("IntentCaptured", "SpecDrafted", "SchemaValidated", "DiffReady", "AwaitingConfirmation"):
        assert state in text


def test_tui_renders_available_actions_and_forbidden_reasons() -> None:
    text = render_mission_tui_text(build_mission_tui_state(GOAL))

    assert "workflow.patch.propose" in text
    assert "workflow.instance.start" in text
    assert "source_agent_denied" in text
    assert "requires_user_confirmation" in text


def test_tui_links_blueprint_report_evidence() -> None:
    text = render_mission_tui_text(build_mission_tui_state(GOAL))

    assert "drawio://v7-2" in text
    assert "runtime-report://not-started/transcript-only" in text
    assert "evidence://v7-2" in text


def test_tui_blocks_mutation_before_user_confirmation() -> None:
    state = build_mission_tui_state(GOAL)
    start_action = next(action for action in state.available_actions if action["operation"] == "workflow.instance.start")

    assert start_action["requires_user_confirmation"] is True
    assert start_action["agent_executable"] is False
    assert start_action["policy_decision"] == "needs_review"


def test_tui_blocks_source_agent_direct_mutation() -> None:
    state = build_mission_tui_state(GOAL)
    reason = next(reason for reason in state.forbidden_reasons if reason["reason_code"] == "source_agent_denied")

    assert reason["source"] == "agent"
    assert "不能直接执行" in reason["human_readable_summary"]


def test_tui_state_is_transcript_only_not_runtime_backed() -> None:
    state = build_mission_tui_state(GOAL)

    assert state.transcript_only is True
    assert state.runtime_backed is False
    assert state.runtime_truth_boundary == "tui_is_workflow_head_not_runtime_truth"


def test_tui_no_false_green_copy_or_sensitive_leakage() -> None:
    text = render_mission_tui_text(build_mission_tui_state(GOAL))
    scan = scan_mission_tui_output(text)

    assert scan["status"] == "PASS"
    assert scan["forbidden_copy_hits"] == []
    assert scan["sensitive_hits"] == []


def test_v7_2_evidence_script_generates_package() -> None:
    subprocess.run(["./.venv/bin/python", "scripts/v7_2_mission_tui_evidence.py"], check=True)

    required = [
        "index.html",
        "tui-transcript.txt",
        "acceptance-data.json",
        "result-summary.md",
        "claims-scan.md",
        "redaction-scan.md",
        "raw/mission-tui-state.json",
        "raw/cli-result.json",
    ]
    missing = [name for name in required if not (OUT_DIR / name).exists()]
    assert missing == []

    data = json.loads((OUT_DIR / "acceptance-data.json").read_text(encoding="utf-8"))
    assert data["stage_id"] == "V7-2"
    assert data["status"] == "PASS"
    assert data["evidence_scope"] == "transcript_only"
    assert data["runtime_backed"] is False
    assert data["transcript_only"] is True
    assert data["claim_violations"] == []
    assert data["redaction_status"] == "PASS"
