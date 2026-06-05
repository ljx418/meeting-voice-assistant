from __future__ import annotations

import json
import subprocess
from pathlib import Path

from core.product_console.v7_3_workflow_run import V73RunConfig, run_v7_3_workflow, validate_supported_goal
from core.workflows.v4_u5e_local_document_workflow import FakeLLMProviderAdapter


FIXTURE = Path("tests/fixtures/desktop/技术分享")
GOAL = "递归总结 tests/fixtures/desktop/技术分享 下的 Markdown 技术文档"


def test_v7_3_rejects_generic_goal() -> None:
    try:
        validate_supported_goal("帮我创建一个任意视频生产工作流")
    except ValueError as exc:
        assert "unsupported workflow goal" in str(exc)
    else:
        raise AssertionError("generic goal should be rejected")


def test_v7_3_fake_provider_cannot_pass(tmp_path: Path) -> None:
    result = run_v7_3_workflow(
        V73RunConfig(goal=GOAL, requested_path="tests/fixtures/desktop/技术分享", fixture_root=FIXTURE, output_dir=tmp_path),
        provider_adapter=FakeLLMProviderAdapter(),
    )

    acceptance = result["acceptance"]
    assert acceptance["stage_id"] == "V7-3"
    assert acceptance["status"] == "BLOCKED"
    assert acceptance["runtime_backed"] is False
    assert acceptance["fallback_demo_only"] is True
    assert acceptance["scanner_actual_read_count"] == 5
    assert acceptance["provider_invocation_count"] == 4
    assert "real LLM provider invocation evidence" in acceptance["missing_evidence"]


def test_v7_3_evidence_package_contains_required_files_and_no_false_green(tmp_path: Path) -> None:
    run_v7_3_workflow(
        V73RunConfig(goal=GOAL, requested_path="tests/fixtures/desktop/技术分享", fixture_root=FIXTURE, output_dir=tmp_path),
        provider_adapter=FakeLLMProviderAdapter(),
    )

    required = [
        "index.html",
        "tui-transcript.txt",
        "workflow.json",
        "workflow.yaml",
        "workflow.drawio",
        "workflow_status.drawio",
        "workflow_board.html",
        "artifacts.html",
        "quality.html",
        "evidence.html",
        "local-document-workflow-result.json",
        "evidence_chain.json",
        "quality_report.json",
        "acceptance-data.json",
        "claims-scan.md",
        "redaction-scan.md",
        "result-summary.md",
        "raw/mission-state.json",
        "raw/workflow-diff.json",
        "raw/user-confirmed-handoff.json",
        "raw/provider-redacted-summary.json",
    ]
    assert [name for name in required if not (tmp_path / name).exists()] == []

    acceptance = json.loads((tmp_path / "acceptance-data.json").read_text(encoding="utf-8"))
    assert acceptance["status"] == "BLOCKED"
    assert "status: PASS" in (tmp_path / "claims-scan.md").read_text(encoding="utf-8")
    assert "status: PASS" in (tmp_path / "redaction-scan.md").read_text(encoding="utf-8")
    assert '"content":' not in (tmp_path / "local-document-workflow-result.json").read_text(encoding="utf-8")


def test_v7_3_source_agent_and_missing_confirmation_denied(tmp_path: Path) -> None:
    try:
        run_v7_3_workflow(
            V73RunConfig(goal=GOAL, requested_path="tests/fixtures/desktop/技术分享", source="agent", output_dir=tmp_path),
            provider_adapter=FakeLLMProviderAdapter(),
        )
    except ValueError as exc:
        assert "source=agent" in str(exc)
    else:
        raise AssertionError("source=agent should be denied")

    try:
        run_v7_3_workflow(
            V73RunConfig(goal=GOAL, requested_path="tests/fixtures/desktop/技术分享", user_confirmed=False, output_dir=tmp_path),
            provider_adapter=FakeLLMProviderAdapter(),
        )
    except ValueError as exc:
        assert "user_confirmed=true" in str(exc)
    else:
        raise AssertionError("missing confirmation should be denied")


def test_harness_tui_run_requires_user_confirmation() -> None:
    result = subprocess.run(
        ["./.venv/bin/python", "-m", "cli.main", "tui", "--run", GOAL],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "--user-confirmed" in result.stderr
