from __future__ import annotations

import json
import subprocess
from pathlib import Path

from core.product_console.v8_station_agent_workflow import V8StationAgentRunConfig, run_v8_station_agent_workflow
from core.workflows.v4_u5e_local_document_workflow import FakeLLMProviderAdapter


FIXTURE = Path("tests/fixtures/desktop/技术分享")
GOAL = "递归总结 tests/fixtures/desktop/技术分享 下的 Markdown 技术文档"


def test_v8_fake_provider_cannot_pass_but_produces_station_agent_evidence(tmp_path: Path) -> None:
    result = run_v8_station_agent_workflow(
        V8StationAgentRunConfig(goal=GOAL, requested_path="tests/fixtures/desktop/技术分享", fixture_root=FIXTURE, output_dir=tmp_path),
        provider_adapter=FakeLLMProviderAdapter(),
    )

    acceptance = result["acceptance"]
    assert acceptance["stage_id"] == "V8-4"
    assert acceptance["status"] == "BLOCKED"
    assert acceptance["station_count"] == acceptance["agent_descriptor_count"]
    assert acceptance["workflow_explainer_agent_exists"] is True
    assert acceptance["agent_context_envelope_count"] == acceptance["station_count"]
    assert acceptance["agent_invocation_count"] == acceptance["station_count"]
    assert acceptance["source_agent_mutation_denied"] == "PASS"
    assert acceptance["scanner_actual_read_count"] == 5
    assert acceptance["provider_invocation_count"] == 4
    assert "real LLM provider invocation evidence" in acceptance["blockers"]


def test_v8_evidence_package_contains_required_outputs_and_no_raw_content(tmp_path: Path) -> None:
    run_v8_station_agent_workflow(
        V8StationAgentRunConfig(goal=GOAL, requested_path="tests/fixtures/desktop/技术分享", fixture_root=FIXTURE, output_dir=tmp_path),
        provider_adapter=FakeLLMProviderAdapter(),
    )

    required = [
        "index.html",
        "workflow.drawio",
        "workflow_status.drawio",
        "workflow_board.html",
        "agent-evidence.html",
        "station-agent-registry.json",
        "station-agent-descriptors.json",
        "agent-context-envelopes.json",
        "agent-invocation-evidence.json",
        "agent-capability-decisions.json",
        "agent-run-results.json",
        "acceptance-data.json",
        "claims-scan.md",
        "redaction-scan.md",
        "result-summary.md",
        "raw/terminal-worker-blocked.json",
    ]
    assert [name for name in required if not (tmp_path / name).exists()] == []

    data = json.loads((tmp_path / "acceptance-data.json").read_text(encoding="utf-8"))
    assert data["terminal_worker_enabled"] is False
    assert "status: PASS" in (tmp_path / "claims-scan.md").read_text(encoding="utf-8")
    assert "status: PASS" in (tmp_path / "redaction-scan.md").read_text(encoding="utf-8")
    assert '"content":' not in (tmp_path / "local-document-workflow-result.json").read_text(encoding="utf-8")


def test_v8_cli_requires_user_confirmation() -> None:
    result = subprocess.run(
        ["./.venv/bin/python", "-m", "cli.main", "tui", "--v8-station-agent", GOAL],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "--run requires --user-confirmed" in result.stderr


def test_v8_source_agent_is_denied(tmp_path: Path) -> None:
    try:
        run_v8_station_agent_workflow(
            V8StationAgentRunConfig(goal=GOAL, requested_path="tests/fixtures/desktop/技术分享", source="agent", output_dir=tmp_path),
            provider_adapter=FakeLLMProviderAdapter(),
        )
    except ValueError as exc:
        assert "source=agent" in str(exc)
    else:
        raise AssertionError("source=agent should be denied")
