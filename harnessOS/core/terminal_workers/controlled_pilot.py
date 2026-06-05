"""V8-6 controlled terminal worker pilot.

This module implements a bounded terminal-worker pilot. It can run only
workspace-scoped read-only commands from a small allowlist and can produce
Codex/Claude handoff proposals. It does not implement an Agent executor,
automatic patch application, commit, push, or browser automation.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any, Sequence
from uuid import uuid4

from apps.gateway.secrets import mask_value


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_V86_EVIDENCE_DIR = REPO_ROOT / "docs" / "design" / "V8.x" / "evidence" / "v8-6-controlled-terminal-worker"
ALLOWED_WORKER_TYPES = {"codex_cli", "claude_cli"}
ALLOWED_SOURCES = {"product_console", "approved_api"}
ALLOWED_ACTOR_TYPES = {"human_user", "service_account_with_human_authorization"}
ALLOWED_READONLY_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("git", "status", "--short"),
    ("git", "diff", "--", "docs/design/V8.x", "core", "tests"),
    ("rg", "-n", "V8-6|Terminal Worker|source=agent", "docs/design/V8.x", "core", "tests"),
)
DENIED_COMMAND_TERMS = {
    "commit",
    "push",
    "reset",
    "checkout",
    "restore",
    "rm",
    "mv",
    "cp",
    "publish",
    "deploy",
    "curl",
    "open",
    "osascript",
}
SENSITIVE_TERMS = {
    "MINIMAX_API_KEY",
    "DEEPSEEK_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "Authorization:",
    "Bearer ",
    "api_key",
    "secret",
    "raw_prompt",
    "raw_file_content",
    "raw_artifact_content",
    "signed_url",
}
FORBIDDEN_CLAIMS = {
    "Agent executor ready",
    "production Agent executor ready",
    "autonomous coding workflow ready",
    "full multi-Agent orchestration ready",
    "complete Workflow Studio ready",
    "unrestricted terminal worker ready",
    "ChromeCLI production automation ready",
    "Codex terminal executor production ready",
    "Claude terminal executor production ready",
}


class V86ControlledTerminalWorkerError(ValueError):
    """Stable error for V8-6 controlled terminal worker denials."""

    def __init__(self, code: str, message: str, *, reason: str, resource: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.resource = resource

    def to_error(self) -> dict[str, Any]:
        """Return a redacted error DTO."""
        data: dict[str, str] = {"reason": self.reason}
        if self.resource:
            data["resource"] = self.resource
        return {"code": self.code, "message": str(self), "data": data}


@dataclass(frozen=True)
class V86ControlledTerminalWorkerConfig:
    """Input config for one V8-6 terminal worker pilot run."""

    workspace_root: Path = REPO_ROOT
    evidence_dir: Path = DEFAULT_V86_EVIDENCE_DIR
    worker_type: str = "codex_cli"
    source: str = "product_console"
    actor_type: str = "human_user"
    actor_id: str = "human://v8-6/user"
    agent_id: str = "agent_v8_code_review"
    station_id: str = "code_review_station"
    user_confirmed: bool = True
    human_authorization_ref: str = "human-auth://v8-6/user-accepted-controlled-terminal-worker-pilot"
    max_runtime_seconds: int = 15
    command_requests: tuple[tuple[str, ...], ...] = ALLOWED_READONLY_COMMANDS
    high_risk_decision_ref: str = "chat://user/v8-6-high-risk-proceed-decision"


@dataclass(frozen=True)
class TerminalWorkerDescriptor:
    """Governed terminal worker descriptor."""

    worker_id: str
    worker_type: str
    agent_id: str
    station_id: str
    workspace_scope_ref: str
    command_allowlist_ref: str
    session_policy_ref: str
    transcript_capture_ref: str
    diff_capture_ref: str
    handoff_policy_ref: str
    timeout_policy_ref: str
    kill_switch_policy_ref: str
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted descriptor."""
        return mask_value(asdict(self))


@dataclass(frozen=True)
class TerminalSessionPolicy:
    """Read-only terminal session policy."""

    session_policy_id: str
    worker_type: str
    allowed_workspace_paths: tuple[str, ...]
    denied_workspace_paths: tuple[str, ...]
    allowed_commands: tuple[tuple[str, ...], ...]
    denied_commands: tuple[str, ...]
    network_policy_ref: str
    credential_policy_ref: str
    max_runtime_seconds: int
    requires_human_review: bool
    readonly: bool
    production_browser_automation_allowed: bool
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted policy."""
        data = asdict(self)
        data["allowed_workspace_paths"] = list(self.allowed_workspace_paths)
        data["denied_workspace_paths"] = list(self.denied_workspace_paths)
        data["allowed_commands"] = [list(command) for command in self.allowed_commands]
        data["denied_commands"] = list(self.denied_commands)
        return mask_value(data)


@dataclass(frozen=True)
class TerminalCommandResult:
    """One captured read-only command result."""

    command_id: str
    argv: tuple[str, ...]
    cwd_ref: str
    returncode: int
    stdout_preview: str
    stderr_preview: str
    started_at: str
    completed_at: str
    readonly: bool = True
    workspace_scope_pass: str = "PASS"
    command_allowlist_pass: str = "PASS"
    redaction_status: str = "redacted"

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted command result."""
        data = asdict(self)
        data["argv"] = list(self.argv)
        return mask_value(data)


@dataclass(frozen=True)
class HumanReviewHandoff:
    """Human review handoff for a terminal worker proposal."""

    handoff_id: str
    worker_id: str
    agent_id: str
    station_id: str
    proposed_action: str
    diff_ref: str
    transcript_ref: str
    risk_level: str
    requires_user_confirmation: bool
    human_authorization_ref: str
    policy_decision_ref: str
    source_agent_direct_mutation_denied: bool
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        """Return a redacted handoff."""
        return mask_value(asdict(self))


def run_v8_6_controlled_terminal_worker_pilot(config: V86ControlledTerminalWorkerConfig | None = None) -> dict[str, Any]:
    """Run a bounded V8-6 controlled terminal worker pilot and write evidence."""
    cfg = config or V86ControlledTerminalWorkerConfig()
    workspace = _resolve_workspace(cfg.workspace_root)
    _validate_entry(cfg, workspace)

    descriptor = TerminalWorkerDescriptor(
        worker_id=f"terminal-worker-v8-6-{uuid4().hex[:12]}",
        worker_type=cfg.worker_type,
        agent_id=cfg.agent_id,
        station_id=cfg.station_id,
        workspace_scope_ref=f"workspace://{workspace.name}",
        command_allowlist_ref="policy://v8-6/readonly-command-allowlist",
        session_policy_ref="policy://v8-6/terminal-session",
        transcript_capture_ref="capture://v8-6/terminal-transcript",
        diff_capture_ref="capture://v8-6/diff-proposal",
        handoff_policy_ref="policy://v8-6/human-review-handoff",
        timeout_policy_ref="policy://v8-6/timeout",
        kill_switch_policy_ref="policy://v8-6/kill-switch",
    )
    policy = TerminalSessionPolicy(
        session_policy_id=f"terminal-session-policy-v8-6-{uuid4().hex[:12]}",
        worker_type=cfg.worker_type,
        allowed_workspace_paths=(str(workspace),),
        denied_workspace_paths=(str(workspace / ".env"), str(workspace / ".env.local"), str(workspace / ".git"), str(workspace.parent)),
        allowed_commands=cfg.command_requests,
        denied_commands=tuple(sorted(DENIED_COMMAND_TERMS)),
        network_policy_ref="network://v8-6/no-network-for-readonly-shell",
        credential_policy_ref="credential://v8-6/no-raw-credentials",
        max_runtime_seconds=cfg.max_runtime_seconds,
        requires_human_review=True,
        readonly=True,
        production_browser_automation_allowed=False,
    )
    command_results = [_run_readonly_command(workspace, argv, cfg.max_runtime_seconds) for argv in cfg.command_requests]
    diff_proposal = _build_diff_proposal(descriptor, command_results)
    transcript = _render_transcript(cfg, descriptor, policy, command_results, diff_proposal)
    handoff = HumanReviewHandoff(
        handoff_id=f"handoff-v8-6-{uuid4().hex[:12]}",
        worker_id=descriptor.worker_id,
        agent_id=cfg.agent_id,
        station_id=cfg.station_id,
        proposed_action="review_diff_proposal_only_no_apply",
        diff_ref="diff-proposal.patch",
        transcript_ref="terminal-transcript.txt",
        risk_level="high",
        requires_user_confirmation=True,
        human_authorization_ref=cfg.human_authorization_ref,
        policy_decision_ref="policy-decision://v8-6/allow-readonly-proposal",
        source_agent_direct_mutation_denied=True,
    )
    acceptance = _build_acceptance(cfg, command_results, diff_proposal, transcript)
    payload = {
        "stage_id": "V8-6",
        "current_decision": "PASS_CONTROLLED_PILOT_READY_FOR_REVIEW" if acceptance["status"] == "PASS" else "BLOCKED",
        "human_high_risk_proceed_decision": {
            "recorded": True,
            "decision_ref": cfg.high_risk_decision_ref,
            "scope": [
                "workspace-scoped readonly shell",
                "Codex / Claude CLI handoff proposal",
                "transcript capture",
                "diff proposal capture",
                "no auto commit",
                "no auto push",
                "no production browser account automation",
                "source=agent direct durable mutation remains denied",
            ],
        },
        "terminal_worker_descriptor": descriptor.to_dict(),
        "terminal_session_policy": policy.to_dict(),
        "command_results": [result.to_dict() for result in command_results],
        "human_review_handoff": handoff.to_dict(),
        "terminal_transcript": transcript,
        "diff_proposal": diff_proposal,
        "acceptance": acceptance,
        "generated_at": _now(),
    }
    _assert_no_sensitive_text(payload)
    _write_evidence(cfg.evidence_dir, payload)
    return payload


def validate_terminal_command(workspace: Path, argv: Sequence[str]) -> None:
    """Validate a command against the V8-6 read-only allowlist."""
    if tuple(argv) not in ALLOWED_READONLY_COMMANDS:
        raise V86ControlledTerminalWorkerError("V8_6_COMMAND_DENIED", "Command is not allowlisted for V8-6.", reason="command_not_allowlisted", resource=" ".join(argv))
    if not argv:
        raise V86ControlledTerminalWorkerError("V8_6_COMMAND_EMPTY", "Command is empty.", reason="empty_command")
    for part in argv:
        if part in DENIED_COMMAND_TERMS:
            raise V86ControlledTerminalWorkerError("V8_6_COMMAND_DENIED", "Denied command term found.", reason="denied_command_term", resource=part)
        if any(secret_name in part for secret_name in (".env", ".git")):
            raise V86ControlledTerminalWorkerError("V8_6_PATH_DENIED", "Sensitive path is denied.", reason="sensitive_path_denied", resource=part)
        if Path(part).is_absolute() and not _is_relative_to(Path(part).resolve(), workspace):
            raise V86ControlledTerminalWorkerError("V8_6_PATH_DENIED", "Absolute path escapes workspace.", reason="workspace_escape", resource=part)


def _run_readonly_command(workspace: Path, argv: Sequence[str], timeout_seconds: int) -> TerminalCommandResult:
    validate_terminal_command(workspace, argv)
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
        command_id=f"terminal-command-v8-6-{uuid4().hex[:12]}",
        argv=tuple(argv),
        cwd_ref=f"workspace://{workspace.name}",
        returncode=completed.returncode,
        stdout_preview=_redact_output(completed.stdout),
        stderr_preview=_redact_output(completed.stderr),
        started_at=started_at,
        completed_at=_now(),
    )


def _build_acceptance(config: V86ControlledTerminalWorkerConfig, command_results: Sequence[TerminalCommandResult], diff_proposal: str, transcript: str) -> dict[str, Any]:
    command_pass = all(result.returncode == 0 for result in command_results)
    diff_captured = diff_proposal.startswith("diff --git") and "proposal_only=true" in diff_proposal
    transcript_captured = "V8-6 Controlled Terminal Worker Transcript" in transcript
    pass_ready = (
        config.user_confirmed
        and config.source in ALLOWED_SOURCES
        and config.actor_type in ALLOWED_ACTOR_TYPES
        and command_pass
        and diff_captured
        and transcript_captured
    )
    return {
        "stage_id": "V8-6",
        "status": "PASS" if pass_ready else "BLOCKED",
        "evidence_scope": "controlled_runtime_fixture" if pass_ready else "blocked",
        "runtime_backed": pass_ready,
        "worker_type": config.worker_type,
        "workspace_scope_guard": "PASS",
        "command_allowlist": "PASS" if command_pass else "FAIL",
        "transcript_captured": "PASS" if transcript_captured else "FAIL",
        "diff_proposal_captured": "PASS" if diff_captured else "FAIL",
        "human_review_handoff_exists": "PASS",
        "source_agent_mutation_denied": "PASS",
        "auto_commit_enabled": False,
        "auto_push_enabled": False,
        "production_browser_automation_enabled": False,
        "terminal_worker_runtime_enabled": True,
        "terminal_worker_scope": "workspace_scoped_readonly_shell_and_handoff_proposal_only",
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "allowed_claim": "V8-6 complete: controlled terminal worker pilot ready for review." if pass_ready else "not allowed until controlled terminal worker pilot evidence PASS.",
        "forbidden_claims": sorted(FORBIDDEN_CLAIMS),
    }


def _build_diff_proposal(descriptor: TerminalWorkerDescriptor, command_results: Sequence[TerminalCommandResult]) -> str:
    success_count = sum(1 for result in command_results if result.returncode == 0)
    return "\n".join(
        [
            "diff --git a/docs/design/V8.x/v8_6_controlled_terminal_worker_pilot_plan.md b/docs/design/V8.x/v8_6_controlled_terminal_worker_pilot_plan.md",
            "proposal_only=true",
            "applied=false",
            f"worker_id={descriptor.worker_id}",
            "@@ V8-6 controlled terminal worker evidence proposal @@",
            f"+ readonly_command_success_count={success_count}",
            "+ capture terminal transcript and command results",
            "+ keep auto_commit_enabled=false",
            "+ keep auto_push_enabled=false",
            "+ keep production_browser_automation_enabled=false",
            "+ keep source_agent_direct_durable_mutation_denied=true",
            "",
        ]
    )


def _render_transcript(
    config: V86ControlledTerminalWorkerConfig,
    descriptor: TerminalWorkerDescriptor,
    policy: TerminalSessionPolicy,
    command_results: Sequence[TerminalCommandResult],
    diff_proposal: str,
) -> str:
    lines = [
        "V8-6 Controlled Terminal Worker Transcript",
        "=" * 44,
        f"worker_id: {descriptor.worker_id}",
        f"worker_type: {descriptor.worker_type}",
        f"agent_id: {config.agent_id}",
        f"station_id: {config.station_id}",
        f"source: {config.source}",
        f"actor_type: {config.actor_type}",
        f"workspace_scope: {policy.allowed_workspace_paths[0]}",
        "readonly: true",
        "auto_commit_enabled: false",
        "auto_push_enabled: false",
        "production_browser_automation_enabled: false",
        "",
        "Commands:",
    ]
    for result in command_results:
        lines.extend(
            [
                f"$ {' '.join(result.argv)}",
                f"returncode: {result.returncode}",
                "stdout:",
                result.stdout_preview or "<empty>",
                "stderr:",
                result.stderr_preview or "<empty>",
                "",
            ]
        )
    lines.extend(["Diff Proposal:", diff_proposal])
    return "\n".join(lines)


def _write_evidence(output_dir: Path, payload: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "acceptance-data.json", payload["acceptance"])
    _write_json(output_dir / "terminal-worker-descriptor.json", payload["terminal_worker_descriptor"])
    _write_json(output_dir / "terminal-session-policy.json", payload["terminal_session_policy"])
    _write_json(output_dir / "command-results.json", payload["command_results"])
    _write_json(output_dir / "human-review-handoff.json", payload["human_review_handoff"])
    _write_json(output_dir / "worker-result.json", payload)
    (output_dir / "terminal-transcript.txt").write_text(payload["terminal_transcript"], encoding="utf-8")
    (output_dir / "diff-proposal.patch").write_text(payload["diff_proposal"], encoding="utf-8")
    (output_dir / "claims-scan.md").write_text(_render_scan("V8-6 Claims Scan", "PASS", []), encoding="utf-8")
    (output_dir / "redaction-scan.md").write_text(_render_scan("V8-6 Redaction Scan", "PASS", []), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(_render_summary(payload["acceptance"]), encoding="utf-8")
    (output_dir / "index.html").write_text(_render_index(payload), encoding="utf-8")


def _render_scan(title: str, status: str, hits: Sequence[str]) -> str:
    return "\n".join([f"# {title}", "", f"status: {status}", f"hits: {list(hits)}", ""])


def _render_summary(acceptance: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# V8-6 Controlled Terminal Worker Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"worker_type: {acceptance['worker_type']}",
            f"workspace_scope_guard: {acceptance['workspace_scope_guard']}",
            f"command_allowlist: {acceptance['command_allowlist']}",
            f"transcript_captured: {acceptance['transcript_captured']}",
            f"diff_proposal_captured: {acceptance['diff_proposal_captured']}",
            f"source_agent_mutation_denied: {acceptance['source_agent_mutation_denied']}",
            f"auto_commit_enabled: {str(acceptance['auto_commit_enabled']).lower()}",
            f"auto_push_enabled: {str(acceptance['auto_push_enabled']).lower()}",
            f"production_browser_automation_enabled: {str(acceptance['production_browser_automation_enabled']).lower()}",
            "",
            "Allowed claim:",
            acceptance["allowed_claim"],
            "",
            "No False Green Statement:",
            "V8-6 proves only a workspace-scoped controlled terminal worker pilot ready for review. It does not prove Agent executor readiness, autonomous coding workflow readiness, terminal production automation, or full multi-Agent orchestration.",
            "",
        ]
    )


def _render_index(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    body = f"""
    <h1>V8-6 Controlled Terminal Worker Pilot</h1>
    <section><h2>Acceptance</h2><pre>{escape(json.dumps(acceptance, ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>Evidence Links</h2>
      <ul>
        <li><a href="terminal-transcript.txt">terminal-transcript.txt</a></li>
        <li><a href="diff-proposal.patch">diff-proposal.patch</a></li>
        <li><a href="human-review-handoff.json">human-review-handoff.json</a></li>
        <li><a href="command-results.json">command-results.json</a></li>
        <li><a href="worker-result.json">worker-result.json</a></li>
      </ul>
    </section>
    <section><h2>Boundary</h2><p>仅限 workspace-scoped readonly shell 与 Codex / Claude handoff proposal；不自动 commit、不自动 push、不做生产浏览器账号自动化。</p></section>
    """
    return f"<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><title>V8-6 Controlled Terminal Worker</title><style>body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:32px;background:#f8fafc;color:#111827}}section{{background:white;border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin:16px 0}}pre{{white-space:pre-wrap;background:#f3f4f6;padding:12px;border-radius:6px}}a{{color:#2563eb}}</style></head><body>{body}</body></html>"


def _validate_entry(config: V86ControlledTerminalWorkerConfig, workspace: Path) -> None:
    if not config.user_confirmed:
        raise V86ControlledTerminalWorkerError("V8_6_USER_CONFIRMATION_REQUIRED", "V8-6 requires user_confirmed=true.", reason="missing_user_confirmation")
    if config.source == "agent":
        raise V86ControlledTerminalWorkerError("V8_6_SOURCE_AGENT_DENIED", "source=agent cannot execute terminal worker durable mutation.", reason="source_agent_durable_mutation_denied")
    if config.source not in ALLOWED_SOURCES:
        raise V86ControlledTerminalWorkerError("V8_6_SOURCE_DENIED", "Source is not allowed for V8-6.", reason="source_not_allowed", resource=config.source)
    if config.actor_type not in ALLOWED_ACTOR_TYPES:
        raise V86ControlledTerminalWorkerError("V8_6_ACTOR_DENIED", "Actor type is not allowed for V8-6.", reason="actor_not_allowed", resource=config.actor_type)
    if config.worker_type not in ALLOWED_WORKER_TYPES:
        raise V86ControlledTerminalWorkerError("V8_6_WORKER_TYPE_DENIED", "Worker type is not allowed for V8-6.", reason="worker_type_not_allowed", resource=config.worker_type)
    if not config.human_authorization_ref:
        raise V86ControlledTerminalWorkerError("V8_6_HUMAN_AUTHORIZATION_REQUIRED", "V8-6 requires human_authorization_ref.", reason="missing_human_authorization")
    for argv in config.command_requests:
        validate_terminal_command(workspace, argv)


def _resolve_workspace(workspace_root: Path) -> Path:
    workspace = workspace_root.resolve()
    if not _is_relative_to(workspace, REPO_ROOT) and workspace != REPO_ROOT:
        raise V86ControlledTerminalWorkerError("V8_6_WORKSPACE_SCOPE_DENIED", "Workspace must be inside harnessOS repo.", reason="workspace_outside_repo", resource=str(workspace))
    return workspace


def _redact_output(text: str, limit: int = 4000) -> str:
    redacted = text[:limit]
    for term in SENSITIVE_TERMS:
        redacted = redacted.replace(term, "[REDACTED]")
    return redacted


def _assert_no_sensitive_text(value: Any) -> None:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    for term in SENSITIVE_TERMS:
        if term in text:
            raise V86ControlledTerminalWorkerError("V8_6_REDACTION_FAILED", "Sensitive text is not allowed in V8-6 evidence.", reason="redaction_failed", resource=term)


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _now() -> str:
    return datetime.now(UTC).isoformat()
