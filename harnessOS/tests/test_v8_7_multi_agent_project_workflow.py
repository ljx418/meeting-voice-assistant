import subprocess
import sys
from pathlib import Path

import pytest

from core.product_console.v8_7_multi_agent_project_workflow import (
    DEFAULT_V87_EVIDENCE_DIR,
    V87ProjectWorkflowConfig,
    run_v8_7_multi_agent_project_workflow,
)


def test_v8_7_multi_agent_project_workflow_evidence_package(tmp_path: Path) -> None:
    result = run_v8_7_multi_agent_project_workflow(V87ProjectWorkflowConfig(evidence_dir=tmp_path))
    acceptance = result["acceptance"]

    assert acceptance["status"] == "PASS"
    assert acceptance["evidence_scope"] == "bounded_runtime_fixture"
    assert acceptance["runtime_backed"] is True
    assert acceptance["station_count"] == 8
    assert acceptance["agent_descriptor_count"] == 8
    assert acceptance["attempt_history_count"] == 8
    assert acceptance["artifact_count"] == 8
    assert acceptance["project_workflow_requires_explainer_agent"] == "PASS"
    assert acceptance["implementation_agent_uses_handoff_not_direct_shell"] == "PASS"
    assert acceptance["test_agent_uses_allowlisted_readonly_command"] == "PASS"
    assert acceptance["source_agent_mutation_denied"] == "PASS"
    assert acceptance["terminal_worker_status"] == "PASS"
    assert acceptance["auto_commit_enabled"] is False
    assert acceptance["auto_push_enabled"] is False
    assert acceptance["auto_publish_enabled"] is False
    assert acceptance["production_browser_automation_enabled"] is False
    assert acceptance["attempt_history_retained"] == "PASS"
    assert acceptance["review_artifact_exists"] == "PASS"
    assert acceptance["evidence_agent_links_transcript_diff_test_output"] == "PASS"
    assert acceptance["project_explainer_links_agent_evidence"] == "PASS"

    required = [
        "index.html",
        "acceptance-data.json",
        "project-workflow-spec.json",
        "project-agent-registry.json",
        "project-attempt-history.json",
        "project-artifacts.json",
        "project-handoffs.json",
        "project-evidence-bundle.json",
        "project-workflow-transcript.txt",
        "terminal-worker/index.html",
        "terminal-worker/terminal-transcript.txt",
        "terminal-worker/diff-proposal.patch",
        "terminal-worker/command-results.json",
        "claims-scan.md",
        "redaction-scan.md",
        "result-summary.md",
    ]
    assert [name for name in required if not (tmp_path / name).exists()] == []


def test_v8_7_requires_user_confirmation(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="user_confirmed=true"):
        run_v8_7_multi_agent_project_workflow(V87ProjectWorkflowConfig(evidence_dir=tmp_path, user_confirmed=False))


def test_v8_7_denies_source_agent(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="source=agent"):
        run_v8_7_multi_agent_project_workflow(V87ProjectWorkflowConfig(evidence_dir=tmp_path, source="agent"))


def test_v8_7_agent_descriptors_have_station_specific_bindings(tmp_path: Path) -> None:
    result = run_v8_7_multi_agent_project_workflow(V87ProjectWorkflowConfig(evidence_dir=tmp_path))
    descriptors = result["project_agent_registry"]["station_agent_descriptors"]
    assert {item["station_id"] for item in descriptors} == {
        "product_station",
        "architecture_station",
        "planning_station",
        "implementation_station",
        "test_station",
        "review_station",
        "evidence_station",
        "explainer_station",
    }
    assert all(item["memory_policy_ref"] for item in descriptors)
    assert all(item["tool_policy_ref"] for item in descriptors)
    assert all(item["skill_binding_refs"] for item in descriptors)
    implementation = next(item for item in descriptors if item["station_id"] == "implementation_station")
    assert implementation["mcp_binding_refs"] == [
        "agent-mcp-binding://v8-7/v8_7_implementation_agent/terminal_worker_readonly_handoff"
    ]


def test_v8_7_default_evidence_dir_is_v8_design_path() -> None:
    assert DEFAULT_V87_EVIDENCE_DIR.as_posix().endswith("docs/design/V8.x/evidence/v8-7-multi-agent-project-workflow")


def test_v8_7_cli_requires_user_confirmation(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "cli/main.py",
            "tui",
            "--v8-project-workflow",
            "--evidence-dir",
            str(tmp_path),
            "V8-7 bounded multi-agent project workflow pilot",
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "--run requires --user-confirmed" in completed.stderr
