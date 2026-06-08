from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from core.workflows.v9_4_coding_workflow_pilot import (
    V94CodingWorkflowConfig,
    V94CodingWorkflowError,
    deny_coding_operation,
    run_v9_4_coding_workflow_pilot,
)


V9_ROOT = Path("docs/design/V9.x")
EVIDENCE_ROOT = V9_ROOT / "evidence" / "v9-4-coding-workflow-runtime"


def test_v9_4_coding_workflow_generates_proposal_only_runtime_evidence() -> None:
    payload = run_v9_4_coding_workflow_pilot(V94CodingWorkflowConfig(evidence_dir=Path("/tmp/v9-4-coding-test-evidence")))

    acceptance = payload["acceptance"]
    run = payload["coding_workflow_run"]

    assert acceptance["status"] == "PASS"
    assert acceptance["evidence_scope"] == "real_runtime_fixture"
    assert acceptance["runtime_backed"] is True
    assert run["proposal_only"] is True
    assert run["patch_applied"] is False
    assert run["auto_commit_performed"] is False
    assert run["auto_push_performed"] is False
    assert run["auto_deploy_performed"] is False
    assert run["review_summary_is_approval"] is False
    assert acceptance["autonomous_coding_workflow_ready"] is False
    assert acceptance["agent_executor_ready"] is False


def test_v9_4_sandboxed_test_result_uses_scoped_real_pytest_command() -> None:
    payload = run_v9_4_coding_workflow_pilot(V94CodingWorkflowConfig(evidence_dir=Path("/tmp/v9-4-coding-test-evidence")))
    result = payload["sandboxed_test_result"]

    assert result["status"] == "PASS"
    assert result["returncode"] == 0
    assert result["argv"] == ["./.venv/bin/python", "-m", "pytest", "tests/test_v9_4_readiness_closure.py", "-q"]
    assert result["workspace_scoped"] is True
    assert result["parent_environment_inherited"] is False
    assert result["environment_secret_material_available"] is False
    assert result["network_used"] is False
    assert result["secret_read_attempted"] is False


def test_v9_4_denies_patch_apply_commit_push_deploy_and_review_as_approval() -> None:
    assert deny_coding_operation("patch.apply")["reason"] == "unreviewed_patch_apply_denied"
    assert deny_coding_operation("git.commit")["reason"] == "auto_commit_without_human_approval_denied"
    assert deny_coding_operation("git.push")["reason"] == "auto_push_without_release_gate_denied"
    assert deny_coding_operation("production.deploy")["reason"] == "auto_deploy_without_production_gate_denied"
    assert deny_coding_operation("approval.resolve")["reason"] == "review_summary_is_not_approval"

    payload = run_v9_4_coding_workflow_pilot(V94CodingWorkflowConfig(evidence_dir=Path("/tmp/v9-4-coding-test-evidence")))
    deny_report = payload["git_operation_deny_report"]
    assert deny_report["all_denied"] is True
    assert all(item["executed"] is False for item in deny_report["denied_operations"])


def test_v9_4_entry_blocks_source_agent_missing_confirmation_or_unapproved_command() -> None:
    with pytest.raises(V94CodingWorkflowError, match="source=agent"):
        run_v9_4_coding_workflow_pilot(V94CodingWorkflowConfig(evidence_dir=Path("/tmp/v9-4-coding-test-evidence"), source="agent", actor_type="human_user"))
    with pytest.raises(V94CodingWorkflowError, match="requires user confirmation"):
        run_v9_4_coding_workflow_pilot(V94CodingWorkflowConfig(evidence_dir=Path("/tmp/v9-4-coding-test-evidence"), user_confirmed=False))
    with pytest.raises(V94CodingWorkflowError, match="only allows"):
        run_v9_4_coding_workflow_pilot(V94CodingWorkflowConfig(evidence_dir=Path("/tmp/v9-4-coding-test-evidence"), sandbox_command=("git", "status", "--short")))


def test_v9_4_evidence_generator_writes_acceptance_dashboard() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "tools.v9.generate_v9_4_coding_workflow_evidence"],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((EVIDENCE_ROOT / "acceptance-data.json").read_text(encoding="utf-8"))
    html = (EVIDENCE_ROOT / "index.html").read_text(encoding="utf-8")

    assert data["status"] == "PASS"
    assert data["diff_proposal_is_not_patch_apply"] == "PASS"
    assert data["sandboxed_test_result"] == "PASS"
    assert data["auto_commit_denied"] == "PASS"
    assert data["auto_push_denied"] == "PASS"
    assert data["auto_deploy_denied"] == "PASS"
    assert data["source_agent_direct_mutation_denied"] == "PASS"
    assert "V9-4 编码工作流试点" in html
    assert "执行器启动按钮" not in html
    assert "开始实现按钮" not in html
