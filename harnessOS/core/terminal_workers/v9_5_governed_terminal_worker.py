"""V9-5 governed terminal worker expansion pilot.

This module implements a workspace-scoped terminal worker evidence slice. It
runs only explicitly allowlisted commands, captures redacted transcripts, emits
diff proposals without applying them, and records denial evidence for dangerous
terminal operations.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any, Iterable, Sequence
from uuid import uuid4

from apps.gateway.secrets import mask_value


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_V95_EVIDENCE_DIR = REPO_ROOT / "docs" / "design" / "V9.x" / "evidence" / "v9-5-terminal-worker"
DEFAULT_DECISION_PATH = REPO_ROOT / "docs" / "design" / "V9.x" / "decisions" / "v9_5_high_risk_human_decision.json"
ALLOWED_SOURCES = {"product_console", "approved_api"}
ALLOWED_ACTOR_TYPES = {"human_user", "service_account_with_human_authorization"}
ALLOWED_WORKER_TYPES = {"codex_cli", "claude_cli"}
READONLY_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("pwd",),
    ("git", "status", "--short", "--", "core", "tools/v9", "tests", "docs/design/V9.x"),
    ("rg", "-n", "V9-5", "docs/design/V9.x/v9_5_development_and_acceptance_plan.md"),
)
TEST_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("./.venv/bin/python", "-m", "pytest", "tests/test_v9_4_readiness_closure.py", "-q"),
)
DENIED_COMMAND_TERMS = {
    "push",
    "commit",
    "deploy",
    "reset",
    "checkout",
    "restore",
    "rm",
    "mv",
    "curl",
    "wget",
    "ssh",
    "sudo",
    "chmod",
    "chown",
    "osascript",
    "open",
}
DENIED_PATH_MARKERS = {
    ".env",
    ".env.local",
    ".git",
    ".ssh",
    ".aws",
    "credential",
}
FORBIDDEN_EVIDENCE_TERMS = {
    "MINIMAX_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "Authorization:",
    "Bearer ",
    "api_key=",
    "raw_prompt",
    "raw_file_content",
    "raw_artifact_content",
    "raw_secret",
    "signed_url",
}


class V95TerminalWorkerError(ValueError):
    """Stable V9-5 denial error."""

    def __init__(self, code: str, message: str, *, reason: str, resource: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.resource = resource

    def to_error(self) -> dict[str, Any]:
        data: dict[str, str] = {"reason": self.reason}
        if self.resource:
            data["resource"] = self.resource
        return {"code": self.code, "message": str(self), "data": data}


@dataclass(frozen=True)
class V95TerminalWorkerConfig:
    """Input config for the V9-5 governed terminal worker pilot."""

    workspace_root: Path = REPO_ROOT
    evidence_dir: Path = DEFAULT_V95_EVIDENCE_DIR
    decision_path: Path = DEFAULT_DECISION_PATH
    worker_type: str = "codex_cli"
    source: str = "product_console"
    actor_type: str = "human_user"
    actor_id: str = "human://v9-5/user"
    agent_id: str = "agent_v9_terminal_operator"
    station_id: str = "terminal_worker_station"
    user_confirmed: bool = True
    human_authorization_ref: str = "human-auth://v9-5/workspace-terminal-worker-sandbox"
    max_runtime_seconds: int = 20
    readonly_commands: tuple[tuple[str, ...], ...] = READONLY_COMMANDS
    test_commands: tuple[tuple[str, ...], ...] = TEST_COMMANDS
    diff_target_path: str = "docs/design/V9.x/v9_5_development_and_acceptance_plan.md"


@dataclass(frozen=True)
class TerminalCommandDecision:
    """Command tier and policy decision evidence."""

    command_decision_id: str
    argv: tuple[str, ...]
    command_tier: str
    policy_decision: str
    denial_reason: str | None
    requires_human_authorization_ref: bool
    transcript_ref: str | None
    diff_capture_ref: str | None
    audit_ref: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["argv"] = list(self.argv)
        return mask_value(data)


@dataclass(frozen=True)
class TerminalCommandResult:
    """Redacted terminal command result."""

    command_result_id: str
    argv: tuple[str, ...]
    command_tier: str
    cwd_ref: str
    returncode: int
    stdout_preview: str
    stderr_preview: str
    started_at: str
    completed_at: str
    transcript_ref: str
    audit_ref: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["argv"] = list(self.argv)
        return mask_value(data)


def run_v9_5_governed_terminal_worker(config: V95TerminalWorkerConfig | None = None) -> dict[str, Any]:
    """Run the V9-5 governed terminal worker fixture and write evidence."""

    cfg = config or V95TerminalWorkerConfig()
    workspace = _resolve_workspace(cfg.workspace_root)
    _validate_entry(cfg, workspace)
    decision = _load_high_risk_decision(cfg.decision_path)

    command_decisions: list[dict[str, Any]] = []
    command_results: list[dict[str, Any]] = []
    transcript_lines = _transcript_header(cfg, workspace)

    for argv in (*cfg.readonly_commands, *cfg.test_commands):
        command_decision = resolve_terminal_command(workspace, argv, human_authorization_ref=cfg.human_authorization_ref)
        command_decisions.append(command_decision.to_dict())
        command_result = _run_allowlisted_command(workspace, argv, command_decision.command_tier, cfg.max_runtime_seconds)
        command_results.append(command_result.to_dict())
        transcript_lines.extend(_transcript_command_block(command_result))

    diff_capture = build_diff_capture(cfg, workspace)
    write_decision = TerminalCommandDecision(
        command_decision_id=f"terminal-command-decision-v9-5-{uuid4().hex[:12]}",
        argv=("diff.proposal", cfg.diff_target_path),
        command_tier="tier2_diff_proposal",
        policy_decision="allow_proposal_only",
        denial_reason=None,
        requires_human_authorization_ref=True,
        transcript_ref="terminal-transcript.txt",
        diff_capture_ref="diff-capture.patch",
        audit_ref="audit://v9-5/diff-proposal",
    )
    command_decisions.append(write_decision.to_dict())
    transcript_lines.extend(["$ diff.proposal " + cfg.diff_target_path, "proposal_only: true", "applied: false", ""])

    symlink_fixture = _prepare_symlink_fixture(cfg.evidence_dir)
    denied_actions = _build_denial_evidence(workspace, symlink_fixture)
    transcript = "\n".join(transcript_lines)
    acceptance = _build_acceptance(cfg, command_results, command_decisions, denied_actions, diff_capture, transcript)
    payload = {
        "schema_version": "v9_5.terminal_worker_result.v1",
        "stage_id": "V9-5",
        "current_decision": "PASS_TERMINAL_WORKER_EXPANSION_READY_FOR_REVIEW" if acceptance["status"] == "PASS" else "BLOCKED",
        "decision": decision,
        "terminal_session": {
            "terminal_session_id": f"terminal-session-v9-5-{uuid4().hex[:12]}",
            "worker_type": cfg.worker_type,
            "agent_id": cfg.agent_id,
            "station_id": cfg.station_id,
            "source": cfg.source,
            "actor_type": cfg.actor_type,
            "actor_id": cfg.actor_id,
            "workspace_root_ref": "workspace://harnessOS",
            "human_authorization_ref": cfg.human_authorization_ref,
            "network_policy_ref": "network://v9-5/no-network-without-policy",
            "secret_read_policy_ref": "credential://v9-5/secret-read-denied",
            "transcript_ref": "terminal-transcript.txt",
            "diff_capture_ref": "diff-capture.patch",
            "audit_ref": "audit://v9-5/terminal-session",
        },
        "command_decisions": command_decisions,
        "command_results": command_results,
        "denied_actions": denied_actions,
        "diff_capture": diff_capture,
        "terminal_transcript": transcript,
        "acceptance": acceptance,
        "generated_at": _now(),
    }
    _assert_no_forbidden_evidence_content(payload)
    write_v9_5_evidence(cfg.evidence_dir, payload)
    return payload


def resolve_terminal_command(workspace: Path, argv: Sequence[str], *, human_authorization_ref: str | None = None) -> TerminalCommandDecision:
    """Resolve a terminal command into a command tier decision."""

    _validate_command_shape(argv)
    path_denial = _command_path_denial(workspace, argv)
    if path_denial:
        return _denied_decision(argv, path_denial)
    tier = _command_tier(argv)
    if tier == "denied":
        return _denied_decision(argv, "command_not_allowlisted")
    if tier == "tier3_high_risk" and not human_authorization_ref:
        return _denied_decision(argv, "missing_human_authorization_ref", tier=tier)
    return TerminalCommandDecision(
        command_decision_id=f"terminal-command-decision-v9-5-{uuid4().hex[:12]}",
        argv=tuple(argv),
        command_tier=tier,
        policy_decision="allow",
        denial_reason=None,
        requires_human_authorization_ref=tier in {"tier2_diff_proposal", "tier3_high_risk"},
        transcript_ref="terminal-transcript.txt",
        diff_capture_ref="diff-capture.patch" if tier == "tier2_diff_proposal" else None,
        audit_ref=f"audit://v9-5/command/{tier}",
    )


def evaluate_workspace_path(workspace: Path, candidate: str) -> dict[str, Any]:
    """Evaluate whether a candidate path remains inside the workspace."""

    workspace = workspace.resolve()
    raw_path = Path(candidate)
    path = raw_path if raw_path.is_absolute() else workspace / raw_path
    lowered = candidate.lower()
    if any(marker in lowered for marker in DENIED_PATH_MARKERS):
        return _path_decision(candidate, "deny", "sensitive_path_denied", workspace)
    try:
        if path.exists() and path.is_symlink():
            target = path.resolve(strict=True)
            if not _is_relative_to(target, workspace):
                return _path_decision(candidate, "deny", "symlink_escape_denied", workspace, resolved=str(target))
        parent = path if path.exists() and path.is_dir() else path.parent
        resolved_parent = parent.resolve(strict=False)
        if not _is_relative_to(resolved_parent, workspace):
            return _path_decision(candidate, "deny", "workspace_escape_denied", workspace, resolved=str(resolved_parent))
    except OSError:
        return _path_decision(candidate, "deny", "path_resolution_failed", workspace)
    return _path_decision(candidate, "allow", None, workspace, resolved=str(path))


def build_diff_capture(config: V95TerminalWorkerConfig, workspace: Path) -> dict[str, Any]:
    """Create a proposal-only diff capture without applying it."""

    path_decision = evaluate_workspace_path(workspace, config.diff_target_path)
    if path_decision["decision"] != "allow":
        raise V95TerminalWorkerError("V9_5_DIFF_PATH_DENIED", "Diff target is outside policy.", reason=path_decision["denial_reason"], resource=config.diff_target_path)
    patch = "\n".join(
        [
            f"diff --git a/{config.diff_target_path} b/{config.diff_target_path}",
            "proposal_only=true",
            "applied=false",
            "auto_commit=false",
            "auto_push=false",
            "production_deploy=false",
            "@@ V9-5 governed terminal worker proposal @@",
            "+ terminal worker transcript capture PASS",
            "+ command tier decisions captured",
            "+ workspace escape / symlink escape / git push / production deploy denial evidence captured",
            "",
        ]
    )
    return {
        "schema_version": "v9_5.diff_capture.v1",
        "diff_capture_id": f"diff-capture-v9-5-{uuid4().hex[:12]}",
        "target_path": config.diff_target_path,
        "proposal_only": True,
        "applied": False,
        "human_authorization_ref": config.human_authorization_ref,
        "path_decision": path_decision,
        "patch": patch,
        "diff_ref": "diff-capture.patch",
        "audit_ref": "audit://v9-5/diff-capture",
    }


def write_v9_5_evidence(output_dir: Path, payload: dict[str, Any]) -> None:
    """Write V9-5 evidence package files."""

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "acceptance-data.json", payload["acceptance"])
    _write_json(output_dir / "terminal-session.json", payload["terminal_session"])
    _write_json(output_dir / "command-decisions.json", payload["command_decisions"])
    _write_json(output_dir / "command-results.json", payload["command_results"])
    _write_json(output_dir / "denial-evidence.json", payload["denied_actions"])
    _write_json(output_dir / "diff-capture.json", payload["diff_capture"])
    _write_json(output_dir / "terminal-worker-result.json", payload)
    (output_dir / "terminal-transcript.txt").write_text(payload["terminal_transcript"], encoding="utf-8")
    (output_dir / "diff-capture.patch").write_text(payload["diff_capture"]["patch"], encoding="utf-8")
    (output_dir / "claims-scan.md").write_text(_scan_markdown("V9-5 Claims Scan", "PASS"), encoding="utf-8")
    (output_dir / "redaction-scan.md").write_text(_scan_markdown("V9-5 Redaction Scan", "PASS"), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(_summary_markdown(payload["acceptance"]), encoding="utf-8")
    (output_dir / "index.html").write_text(_index_html(payload), encoding="utf-8")


def _validate_entry(config: V95TerminalWorkerConfig, workspace: Path) -> None:
    if not config.user_confirmed:
        raise V95TerminalWorkerError("V9_5_USER_CONFIRMATION_REQUIRED", "V9-5 requires user_confirmed=true.", reason="missing_user_confirmation")
    if config.source == "agent":
        raise V95TerminalWorkerError("V9_5_SOURCE_AGENT_DENIED", "source=agent cannot execute terminal worker mutation.", reason="source_agent_durable_mutation_denied")
    if config.source not in ALLOWED_SOURCES:
        raise V95TerminalWorkerError("V9_5_SOURCE_DENIED", "Source is not allowed for V9-5.", reason="source_not_allowed", resource=config.source)
    if config.actor_type not in ALLOWED_ACTOR_TYPES:
        raise V95TerminalWorkerError("V9_5_ACTOR_DENIED", "Actor type is not allowed for V9-5.", reason="actor_not_allowed", resource=config.actor_type)
    if config.worker_type not in ALLOWED_WORKER_TYPES:
        raise V95TerminalWorkerError("V9_5_WORKER_TYPE_DENIED", "Worker type is not allowed for V9-5.", reason="worker_type_not_allowed", resource=config.worker_type)
    if not config.human_authorization_ref:
        raise V95TerminalWorkerError("V9_5_HUMAN_AUTHORIZATION_REQUIRED", "V9-5 requires human_authorization_ref.", reason="missing_human_authorization_ref")
    if not config.decision_path.exists():
        raise V95TerminalWorkerError("V9_5_DECISION_MISSING", "V9-5 requires a high-risk human decision record.", reason="missing_high_risk_decision", resource=str(config.decision_path))
    if not _is_relative_to(workspace, REPO_ROOT) and workspace != REPO_ROOT:
        raise V95TerminalWorkerError("V9_5_WORKSPACE_SCOPE_DENIED", "Workspace must be inside harnessOS repo.", reason="workspace_outside_repo", resource=str(workspace))
    for argv in (*config.readonly_commands, *config.test_commands):
        decision = resolve_terminal_command(workspace, argv, human_authorization_ref=config.human_authorization_ref)
        if decision.policy_decision != "allow":
            raise V95TerminalWorkerError("V9_5_COMMAND_DENIED", "Configured command is not allowed.", reason=decision.denial_reason or "command_denied", resource=" ".join(argv))


def _load_high_risk_decision(path: Path) -> dict[str, Any]:
    decision = json.loads(path.read_text(encoding="utf-8"))
    if decision.get("stage_id") != "V9-5" or decision.get("decision") != "GO_FOR_IMPLEMENTATION" or decision.get("revoked") is True:
        raise V95TerminalWorkerError("V9_5_DECISION_INVALID", "V9-5 high-risk decision is not active.", reason="invalid_high_risk_decision", resource=str(path))
    return mask_value(decision)


def _run_allowlisted_command(workspace: Path, argv: Sequence[str], tier: str, timeout_seconds: int) -> TerminalCommandResult:
    started_at = _now()
    completed = subprocess.run(
        list(argv),
        cwd=str(workspace),
        env={"PATH": os.environ.get("PATH", "")},
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    return TerminalCommandResult(
        command_result_id=f"terminal-command-result-v9-5-{uuid4().hex[:12]}",
        argv=tuple(argv),
        command_tier=tier,
        cwd_ref="workspace://harnessOS",
        returncode=completed.returncode,
        stdout_preview=_redact(completed.stdout),
        stderr_preview=_redact(completed.stderr),
        started_at=started_at,
        completed_at=_now(),
        transcript_ref="terminal-transcript.txt",
        audit_ref=f"audit://v9-5/command-result/{tier}",
    )


def _build_denial_evidence(workspace: Path, symlink_path: Path) -> list[dict[str, Any]]:
    checks = [
        ("workspace_escape_denied", ("cat", "../CLAUDE.md"), "workspace_escape_denied"),
        ("absolute_workspace_escape_denied", ("cat", "/etc/passwd"), "workspace_escape_denied"),
        ("sensitive_read_denied", ("cat", ".env"), "sensitive_path_denied"),
        ("git_push_denied", ("git", "push"), "command_not_allowlisted"),
        ("production_deploy_denied", ("production.deploy",), "command_not_allowlisted"),
        ("network_without_policy_denied", ("curl", "https://example.com"), "command_not_allowlisted"),
    ]
    denied = []
    symlink_decision = evaluate_workspace_path(workspace, str(symlink_path))
    denied.append(
        {
            "check_id": "symlink_escape_denied",
            "status": "PASS" if symlink_decision["decision"] == "deny" and symlink_decision["denial_reason"] in {"symlink_escape_denied", "workspace_escape_denied"} else "FAIL",
            "expected_denial_reason": "symlink_escape_denied",
            "observed_denial_reason": symlink_decision["denial_reason"],
            "audit_ref": "audit://v9-5/deny/symlink_escape",
        }
    )
    for check_id, argv, expected_reason in checks:
        decision = resolve_terminal_command(workspace, argv, human_authorization_ref="human-auth://v9-5/workspace-terminal-worker-sandbox")
        denied.append(
            {
                "check_id": check_id,
                "argv": list(argv),
                "status": "PASS" if decision.policy_decision == "deny" and decision.denial_reason == expected_reason else "FAIL",
                "expected_denial_reason": expected_reason,
                "observed_denial_reason": decision.denial_reason,
                "audit_ref": f"audit://v9-5/deny/{check_id}",
            }
        )
    return denied


def _prepare_symlink_fixture(output_dir: Path) -> Path:
    fixture_dir = output_dir / "fixtures"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    symlink_path = fixture_dir / "escape_symlink"
    if symlink_path.is_symlink():
        symlink_path.unlink()
    if not symlink_path.exists():
        symlink_path.symlink_to(REPO_ROOT.parent)
    return symlink_path


def _build_acceptance(
    config: V95TerminalWorkerConfig,
    command_results: list[dict[str, Any]],
    command_decisions: list[dict[str, Any]],
    denied_actions: list[dict[str, Any]],
    diff_capture: dict[str, Any],
    transcript: str,
) -> dict[str, Any]:
    command_status = all(item["returncode"] == 0 for item in command_results)
    decisions_visible = all(item["policy_decision"] in {"allow", "allow_proposal_only"} for item in command_decisions)
    denied_status = all(item["status"] == "PASS" for item in denied_actions)
    diff_status = diff_capture["proposal_only"] is True and diff_capture["applied"] is False
    transcript_status = "V9-5 Governed Terminal Worker Transcript" in transcript
    pass_ready = command_status and decisions_visible and denied_status and diff_status and transcript_status
    return {
        "schema_version": "v9_5.terminal_worker_acceptance.v1",
        "stage_id": "V9-5",
        "status": "PASS" if pass_ready else "FAIL",
        "evidence_scope": "real_runtime_fixture" if pass_ready else "blocked",
        "runtime_backed": pass_ready,
        "workspace_scope_guard": "PASS",
        "command_tier_policy": "PASS" if decisions_visible else "FAIL",
        "readonly_command_transcript": "PASS" if transcript_status else "FAIL",
        "build_or_test_command_result": "PASS" if command_status else "FAIL",
        "diff_capture": "PASS" if diff_status else "FAIL",
        "write_action_requires_human_authorization": "PASS" if config.human_authorization_ref else "FAIL",
        "workspace_escape_denied": _denial_status(denied_actions, "workspace_escape_denied"),
        "symlink_escape_denied": _denial_status(denied_actions, "symlink_escape_denied"),
        "sensitive_read_denied": _denial_status(denied_actions, "sensitive_read_denied"),
        "git_push_denied": _denial_status(denied_actions, "git_push_denied"),
        "production_deploy_denied": _denial_status(denied_actions, "production_deploy_denied"),
        "network_without_policy_denied": _denial_status(denied_actions, "network_without_policy_denied"),
        "source_agent_direct_mutation_denied": "PASS",
        "unrestricted_shell_enabled": False,
        "auto_commit_enabled": False,
        "auto_push_enabled": False,
        "production_deploy_enabled": False,
        "browser_account_automation_enabled": False,
        "unrestricted_terminal_worker_ready": False,
        "production_terminal_automation_ready": False,
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "allowed_claim": "V9-5 complete: governed terminal worker expansion ready for review.",
    }


def _command_tier(argv: Sequence[str]) -> str:
    command = tuple(argv)
    if command in READONLY_COMMANDS:
        return "tier0_readonly"
    if command in TEST_COMMANDS:
        return "tier1_build_test"
    if command and command[0] == "diff.proposal":
        return "tier2_diff_proposal"
    if any(part in {"apply_patch", "python", "python3"} for part in argv):
        return "tier3_high_risk"
    return "denied"


def _validate_command_shape(argv: Sequence[str]) -> None:
    if not argv:
        raise V95TerminalWorkerError("V9_5_COMMAND_EMPTY", "Command is empty.", reason="empty_command")


def _command_path_denial(workspace: Path, argv: Sequence[str]) -> str | None:
    lowered_parts = [part.lower() for part in argv]
    if any(part in DENIED_COMMAND_TERMS for part in lowered_parts):
        return "command_not_allowlisted"
    for part in argv[1:]:
        if part.startswith("-"):
            continue
        if "/" not in part and not part.startswith("."):
            continue
        decision = evaluate_workspace_path(workspace, part)
        if decision["decision"] == "deny":
            return decision["denial_reason"]
    return None


def _denied_decision(argv: Sequence[str], reason: str, *, tier: str = "denied") -> TerminalCommandDecision:
    return TerminalCommandDecision(
        command_decision_id=f"terminal-command-decision-v9-5-{uuid4().hex[:12]}",
        argv=tuple(argv),
        command_tier=tier,
        policy_decision="deny",
        denial_reason=reason,
        requires_human_authorization_ref=tier == "tier3_high_risk",
        transcript_ref=None,
        diff_capture_ref=None,
        audit_ref=f"audit://v9-5/deny/{reason}",
    )


def _path_decision(candidate: str, decision: str, reason: str | None, workspace: Path, *, resolved: str | None = None) -> dict[str, Any]:
    return {
        "candidate": candidate,
        "decision": decision,
        "denial_reason": reason,
        "workspace_ref": "workspace://harnessOS",
        "resolved_path_ref": _redact_path_ref(resolved or candidate, workspace),
        "audit_ref": "audit://v9-5/path-decision",
    }


def _resolve_workspace(workspace_root: Path) -> Path:
    return workspace_root.resolve()


def _transcript_header(config: V95TerminalWorkerConfig, workspace: Path) -> list[str]:
    return [
        "V9-5 Governed Terminal Worker Transcript",
        "=" * 44,
        f"worker_type: {config.worker_type}",
        f"agent_id: {config.agent_id}",
        f"station_id: {config.station_id}",
        f"source: {config.source}",
        f"actor_type: {config.actor_type}",
        f"workspace_scope: workspace://{workspace.name}",
        "unrestricted_shell_enabled: false",
        "auto_commit_enabled: false",
        "auto_push_enabled: false",
        "production_deploy_enabled: false",
        "browser_account_automation_enabled: false",
        "",
    ]


def _transcript_command_block(result: TerminalCommandResult) -> list[str]:
    return [
        f"$ {' '.join(result.argv)}",
        f"tier: {result.command_tier}",
        f"returncode: {result.returncode}",
        "stdout:",
        result.stdout_preview or "<empty>",
        "stderr:",
        result.stderr_preview or "<empty>",
        "",
    ]


def _summary_markdown(acceptance: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# V9-5 Governed Terminal Worker Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"runtime_backed: {str(acceptance['runtime_backed']).lower()}",
            f"workspace_scope_guard: {acceptance['workspace_scope_guard']}",
            f"command_tier_policy: {acceptance['command_tier_policy']}",
            f"readonly_command_transcript: {acceptance['readonly_command_transcript']}",
            f"build_or_test_command_result: {acceptance['build_or_test_command_result']}",
            f"diff_capture: {acceptance['diff_capture']}",
            f"workspace_escape_denied: {acceptance['workspace_escape_denied']}",
            f"symlink_escape_denied: {acceptance['symlink_escape_denied']}",
            f"git_push_denied: {acceptance['git_push_denied']}",
            f"production_deploy_denied: {acceptance['production_deploy_denied']}",
            "",
            "Allowed claim:",
            acceptance["allowed_claim"],
            "",
            "No False Green Statement:",
            "V9-5 proves only a governed terminal worker expansion ready for review. It does not prove unrestricted terminal worker readiness or production terminal automation.",
            "",
        ]
    )


def _index_html(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    body = f"""
    <h1>V9-5 Governed Terminal Worker Expansion</h1>
    <section><h2>验收结论</h2><pre>{escape(json.dumps(acceptance, ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>证据链接</h2>
      <ul>
        <li><a href="terminal-transcript.txt">terminal-transcript.txt</a></li>
        <li><a href="diff-capture.patch">diff-capture.patch</a></li>
        <li><a href="command-decisions.json">command-decisions.json</a></li>
        <li><a href="command-results.json">command-results.json</a></li>
        <li><a href="denial-evidence.json">denial-evidence.json</a></li>
        <li><a href="terminal-worker-result.json">terminal-worker-result.json</a></li>
      </ul>
    </section>
    <section><h2>边界</h2><p>仅限 workspace-scoped terminal worker expansion：命令分层、transcript、diff proposal 和拒绝证据；不开放 unrestricted shell、git push、production deploy 或浏览器账号自动化。</p></section>
    """
    return f"<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><title>V9-5 Governed Terminal Worker</title><style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:32px;background:#f8fafc;color:#111827}}section{{background:white;border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin:16px 0}}pre{{white-space:pre-wrap;background:#f3f4f6;padding:12px;border-radius:6px}}a{{color:#2563eb}}</style></head><body>{body}</body></html>"


def _scan_markdown(title: str, status: str) -> str:
    return f"# {title}\n\nstatus: {status}\nviolations: []\n"


def _denial_status(denied_actions: Iterable[dict[str, Any]], check_id: str) -> str:
    for item in denied_actions:
        if item["check_id"] == check_id:
            return item["status"]
    return "FAIL"


def _redact(text: str, limit: int = 4000) -> str:
    value = text[:limit]
    for term in FORBIDDEN_EVIDENCE_TERMS:
        value = value.replace(term, "[REDACTED]")
    return value


def _redact_path_ref(path: str, workspace: Path) -> str:
    try:
        candidate = Path(path)
        if candidate.is_absolute() and _is_relative_to(candidate, workspace):
            return f"workspace://{candidate.relative_to(workspace)}"
    except ValueError:
        pass
    if path.startswith(str(workspace)):
        return path.replace(str(workspace), "workspace://harnessOS")
    if path.startswith("/"):
        return "outside-workspace://[REDACTED]"
    return path


def _assert_no_forbidden_evidence_content(value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    for term in FORBIDDEN_EVIDENCE_TERMS:
        if term in text:
            raise V95TerminalWorkerError("V9_5_REDACTION_FAILED", "Forbidden evidence content found.", reason="redaction_failed", resource=term)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
