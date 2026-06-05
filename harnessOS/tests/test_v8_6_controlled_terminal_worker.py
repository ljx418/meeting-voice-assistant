import subprocess
import sys
from pathlib import Path

import pytest

from core.terminal_workers.controlled_pilot import (
    DEFAULT_V86_EVIDENCE_DIR,
    REPO_ROOT,
    V86ControlledTerminalWorkerConfig,
    V86ControlledTerminalWorkerError,
    run_v8_6_controlled_terminal_worker_pilot,
    validate_terminal_command,
)


def test_v8_6_allowlisted_readonly_command_passes() -> None:
    validate_terminal_command(REPO_ROOT, ("git", "status", "--short"))


def test_v8_6_denies_non_allowlisted_write_command() -> None:
    with pytest.raises(V86ControlledTerminalWorkerError) as exc:
        validate_terminal_command(REPO_ROOT, ("git", "commit"))
    assert exc.value.reason == "command_not_allowlisted"


def test_v8_6_denies_sensitive_path_argument() -> None:
    with pytest.raises(V86ControlledTerminalWorkerError) as exc:
        validate_terminal_command(REPO_ROOT, ("rg", "-n", "x", ".env"))
    assert exc.value.reason == "command_not_allowlisted"


def test_v8_6_source_agent_denied(tmp_path: Path) -> None:
    with pytest.raises(V86ControlledTerminalWorkerError) as exc:
        run_v8_6_controlled_terminal_worker_pilot(V86ControlledTerminalWorkerConfig(source="agent", evidence_dir=tmp_path))
    assert exc.value.reason == "source_agent_durable_mutation_denied"


def test_v8_6_requires_user_confirmation(tmp_path: Path) -> None:
    with pytest.raises(V86ControlledTerminalWorkerError) as exc:
        run_v8_6_controlled_terminal_worker_pilot(V86ControlledTerminalWorkerConfig(user_confirmed=False, evidence_dir=tmp_path))
    assert exc.value.reason == "missing_user_confirmation"


def test_v8_6_controlled_terminal_worker_evidence_package(tmp_path: Path) -> None:
    result = run_v8_6_controlled_terminal_worker_pilot(V86ControlledTerminalWorkerConfig(evidence_dir=tmp_path))
    acceptance = result["acceptance"]
    assert acceptance["status"] == "PASS"
    assert acceptance["evidence_scope"] == "controlled_runtime_fixture"
    assert acceptance["workspace_scope_guard"] == "PASS"
    assert acceptance["command_allowlist"] == "PASS"
    assert acceptance["transcript_captured"] == "PASS"
    assert acceptance["diff_proposal_captured"] == "PASS"
    assert acceptance["source_agent_mutation_denied"] == "PASS"
    assert acceptance["auto_commit_enabled"] is False
    assert acceptance["auto_push_enabled"] is False
    assert acceptance["production_browser_automation_enabled"] is False

    required = [
        "index.html",
        "acceptance-data.json",
        "terminal-worker-descriptor.json",
        "terminal-session-policy.json",
        "terminal-transcript.txt",
        "command-results.json",
        "diff-proposal.patch",
        "human-review-handoff.json",
        "worker-result.json",
        "claims-scan.md",
        "redaction-scan.md",
        "result-summary.md",
    ]
    assert [name for name in required if not (tmp_path / name).exists()] == []
    assert "proposal_only=true" in (tmp_path / "diff-proposal.patch").read_text(encoding="utf-8")
    transcript = (tmp_path / "terminal-transcript.txt").read_text(encoding="utf-8")
    assert "auto_commit_enabled: false" in transcript
    assert "auto_push_enabled: false" in transcript
    assert "production_browser_automation_enabled: false" in transcript
    assert "status: PASS" in (tmp_path / "claims-scan.md").read_text(encoding="utf-8")
    assert "status: PASS" in (tmp_path / "redaction-scan.md").read_text(encoding="utf-8")


def test_v8_6_default_evidence_dir_is_v8_design_path() -> None:
    assert DEFAULT_V86_EVIDENCE_DIR.as_posix().endswith("docs/design/V8.x/evidence/v8-6-controlled-terminal-worker")


def test_v8_6_cli_requires_user_confirmation(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "cli/main.py",
            "tui",
            "--v8-terminal-worker",
            "--evidence-dir",
            str(tmp_path),
            "V8-6 controlled terminal worker pilot",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "--run requires --user-confirmed" in completed.stderr
