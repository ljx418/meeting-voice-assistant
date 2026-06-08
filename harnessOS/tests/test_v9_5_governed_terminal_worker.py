from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from core.terminal_workers.v9_5_governed_terminal_worker import (
    REPO_ROOT,
    V95TerminalWorkerConfig,
    V95TerminalWorkerError,
    evaluate_workspace_path,
    resolve_terminal_command,
    run_v9_5_governed_terminal_worker,
)


def test_v9_5_terminal_worker_generates_evidence_package(tmp_path: Path) -> None:
    payload = run_v9_5_governed_terminal_worker(V95TerminalWorkerConfig(evidence_dir=tmp_path))
    acceptance = payload["acceptance"]

    assert acceptance["status"] == "PASS"
    assert acceptance["evidence_scope"] == "real_runtime_fixture"
    assert acceptance["workspace_scope_guard"] == "PASS"
    assert acceptance["command_tier_policy"] == "PASS"
    assert acceptance["readonly_command_transcript"] == "PASS"
    assert acceptance["build_or_test_command_result"] == "PASS"
    assert acceptance["diff_capture"] == "PASS"
    assert acceptance["workspace_escape_denied"] == "PASS"
    assert acceptance["symlink_escape_denied"] == "PASS"
    assert acceptance["sensitive_read_denied"] == "PASS"
    assert acceptance["git_push_denied"] == "PASS"
    assert acceptance["production_deploy_denied"] == "PASS"
    assert acceptance["unrestricted_shell_enabled"] is False
    assert acceptance["auto_push_enabled"] is False
    assert acceptance["production_deploy_enabled"] is False

    required = [
        "acceptance-data.json",
        "terminal-session.json",
        "command-decisions.json",
        "command-results.json",
        "denial-evidence.json",
        "diff-capture.json",
        "terminal-worker-result.json",
        "terminal-transcript.txt",
        "diff-capture.patch",
        "index.html",
        "result-summary.md",
    ]
    assert [name for name in required if not (tmp_path / name).exists()] == []
    assert "proposal_only=true" in (tmp_path / "diff-capture.patch").read_text(encoding="utf-8")
    assert "unrestricted_shell_enabled: false" in (tmp_path / "terminal-transcript.txt").read_text(encoding="utf-8")


def test_v9_5_command_tier_and_denials() -> None:
    readonly = resolve_terminal_command(REPO_ROOT, ("git", "status", "--short", "--", "core", "tools/v9", "tests", "docs/design/V9.x"), human_authorization_ref="har-v9-5")
    test_command = resolve_terminal_command(REPO_ROOT, ("./.venv/bin/python", "-m", "pytest", "tests/test_v9_4_readiness_closure.py", "-q"), human_authorization_ref="har-v9-5")
    git_push = resolve_terminal_command(REPO_ROOT, ("git", "push"), human_authorization_ref="har-v9-5")
    deploy = resolve_terminal_command(REPO_ROOT, ("production.deploy",), human_authorization_ref="har-v9-5")
    network = resolve_terminal_command(REPO_ROOT, ("curl", "https://example.com"), human_authorization_ref="har-v9-5")

    assert readonly.command_tier == "tier0_readonly"
    assert readonly.policy_decision == "allow"
    assert test_command.command_tier == "tier1_build_test"
    assert test_command.policy_decision == "allow"
    assert git_push.policy_decision == "deny"
    assert git_push.denial_reason == "command_not_allowlisted"
    assert deploy.policy_decision == "deny"
    assert deploy.denial_reason == "command_not_allowlisted"
    assert network.policy_decision == "deny"
    assert network.denial_reason == "command_not_allowlisted"


def test_v9_5_workspace_path_guard_denies_escape_and_sensitive_path(tmp_path: Path) -> None:
    symlink = tmp_path / "escape"
    symlink.symlink_to(REPO_ROOT.parent)

    assert evaluate_workspace_path(REPO_ROOT, "../CLAUDE.md")["denial_reason"] == "workspace_escape_denied"
    assert evaluate_workspace_path(REPO_ROOT, ".env")["denial_reason"] == "sensitive_path_denied"
    assert evaluate_workspace_path(tmp_path, str(symlink))["denial_reason"] == "symlink_escape_denied"
    assert evaluate_workspace_path(REPO_ROOT, "docs/design/V9.x/v9_5_development_and_acceptance_plan.md")["decision"] == "allow"


def test_v9_5_source_agent_and_missing_confirmation_denied(tmp_path: Path) -> None:
    with pytest.raises(V95TerminalWorkerError) as source_exc:
        run_v9_5_governed_terminal_worker(V95TerminalWorkerConfig(evidence_dir=tmp_path / "source", source="agent"))
    assert source_exc.value.reason == "source_agent_durable_mutation_denied"

    with pytest.raises(V95TerminalWorkerError) as confirmation_exc:
        run_v9_5_governed_terminal_worker(V95TerminalWorkerConfig(evidence_dir=tmp_path / "confirmation", user_confirmed=False))
    assert confirmation_exc.value.reason == "missing_user_confirmation"


def test_v9_5_generator_writes_default_evidence() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "tools.v9.generate_v9_5_terminal_worker_evidence"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    data = json.loads(Path("docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json").read_text(encoding="utf-8"))
    assert data["status"] == "PASS"
    assert data["allowed_claim"] == "V9-5 complete: governed terminal worker expansion ready for review."
