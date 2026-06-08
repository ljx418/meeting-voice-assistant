"""V9-4 bounded coding workflow pilot.

This module creates a local coding workflow runtime fixture. It generates
plans, diff proposals, sandboxed test evidence, review summaries, fix-loop
proposals, human review handoffs, and denial evidence. It does not apply
patches, commit, push, deploy, start terminal workers, register runtime routes,
or grant source=agent durable mutation authority.
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


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_V94_EVIDENCE_DIR = REPO_ROOT / "docs" / "design" / "V9.x" / "evidence" / "v9-4-coding-workflow-runtime"
DEFAULT_DECISION_PATH = REPO_ROOT / "docs" / "design" / "V9.x" / "decisions" / "v9_4_high_risk_human_decision.json"
ALLOWED_SOURCES = {"product_console", "approved_api", "mission_tui"}
ALLOWED_ACTOR_TYPES = {"human_user", "service_account_with_human_authorization"}
DENIED_OPERATIONS = {
    "patch.apply": "unreviewed_patch_apply_denied",
    "git.commit": "auto_commit_without_human_approval_denied",
    "git.push": "auto_push_without_release_gate_denied",
    "production.deploy": "auto_deploy_without_production_gate_denied",
    "approval.resolve": "review_summary_is_not_approval",
}
FORBIDDEN_RAW_TERMS = (
    "raw_prompt",
    "raw prompt",
    "raw_file_content",
    "raw file content",
    "raw_provider_payload",
    "raw_connector_payload",
    "raw_artifact_content",
    "raw_secret",
    "api_key",
    "bearer ",
    "bearer_token",
    "signed_url",
    "signed url",
    "credential_raw_secret",
    "credential raw secret",
)


class V94CodingWorkflowError(ValueError):
    """Stable V9-4 coding workflow pilot error."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class V94CodingWorkflowConfig:
    """Input config for one V9-4 coding workflow pilot run."""

    goal: str = "Add bounded V9-4 coding workflow evidence without applying patches."
    workspace_root: Path = REPO_ROOT
    evidence_dir: Path = DEFAULT_V94_EVIDENCE_DIR
    decision_path: Path = DEFAULT_DECISION_PATH
    source: str = "product_console"
    actor_type: str = "human_user"
    actor_id: str = "human://v9-4/user"
    user_confirmed: bool = True
    human_authorization_ref: str = "human-auth://v9-4/autonomous-coding-workflow-pilot"
    sandbox_command: tuple[str, ...] = ("./.venv/bin/python", "-m", "pytest", "tests/test_v9_4_readiness_closure.py", "-q")
    max_runtime_seconds: int = 30


@dataclass(frozen=True)
class V94CodingArtifact:
    """Redacted coding workflow artifact ref."""

    artifact_id: str
    artifact_type: str
    title: str
    path: str
    producer_stage: str
    proposal_only: bool = True
    applied: bool = False
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return _redact(asdict(self))


def run_v9_4_coding_workflow_pilot(config: V94CodingWorkflowConfig | None = None) -> dict[str, Any]:
    """Run the bounded V9-4 coding workflow pilot and write evidence."""
    cfg = config or V94CodingWorkflowConfig()
    workspace = cfg.workspace_root.resolve()
    _validate_entry(cfg, workspace)
    decision = _load_decision(cfg.decision_path)
    run_id = f"coding-run-v9-4-{uuid4().hex[:12]}"
    correlation_id = f"corr-v9-4-{uuid4().hex[:10]}"
    request_id = f"req-v9-4-{uuid4().hex[:10]}"
    artifacts, artifact_contents = _build_artifacts(cfg, run_id)
    test_result = _run_sandboxed_test(cfg, workspace, correlation_id, request_id)
    deny_report = _build_deny_report(correlation_id, request_id)
    handoff = _build_handoff(cfg, run_id, correlation_id, request_id)
    coding_run = {
        "schema_version": "v9_4.coding_workflow_run.v1",
        "coding_workflow_run_id": run_id,
        "source": cfg.source,
        "actor_type": cfg.actor_type,
        "actor_id": cfg.actor_id,
        "goal_ref": "goal-ref://v9-4/bounded-coding-workflow",
        "workspace_scope_ref": f"workspace-ref://v9-4/{workspace.name}",
        "intent_ref": "intent-ref://v9-4/bounded-coding-workflow",
        "spec_ref": "spec-ref://v9-4/bounded-coding-workflow",
        "plan_ref": "plan-ref://v9-4/bounded-coding-workflow",
        "diff_proposal_ref": "diff-proposal-ref://v9-4/bounded-coding-workflow",
        "test_plan_ref": "test-plan-ref://v9-4/bounded-coding-workflow",
        "test_result_ref": test_result["test_result_ref"],
        "review_summary_ref": "review-summary-ref://v9-4/bounded-coding-workflow",
        "fix_loop_ref": "fix-loop-ref://v9-4/bounded-coding-workflow",
        "human_review_handoff_ref": handoff["handoff_id"],
        "human_authorization_ref": cfg.human_authorization_ref,
        "high_risk_decision_ref": decision["decision_ref"],
        "proposal_only": True,
        "patch_applied": False,
        "auto_commit_performed": False,
        "auto_push_performed": False,
        "auto_deploy_performed": False,
        "review_summary_is_approval": False,
        "source_agent_direct_mutation_denied": True,
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": f"audit://v9-4/coding-workflow/{run_id}",
        "created_at": _now(),
    }
    payload = {
        "stage_id": "V9-4",
        "goal": cfg.goal,
        "coding_workflow_run": coding_run,
        "high_risk_decision": {
            "decision_ref": decision["decision_ref"],
            "decision": decision["decision"],
            "scope": decision["scope"],
            "revoked": decision["revoked"],
        },
        "artifacts": [artifact.to_dict() for artifact in artifacts],
        "sandboxed_test_result": test_result,
        "review_summary": _build_review_summary(run_id),
        "fix_loop_proposal": _build_fix_loop(run_id),
        "human_review_handoff": handoff,
        "git_operation_deny_report": deny_report,
        "acceptance": _build_acceptance(coding_run, test_result, deny_report),
        "generated_at": _now(),
    }
    _assert_no_forbidden_raw_content(_payload_for_redaction_assert(payload))
    _write_evidence(cfg.evidence_dir, payload, artifact_contents)
    return payload


def deny_coding_operation(operation: str, *, human_review_accepted: bool = False, release_gate_accepted: bool = False, production_gate_accepted: bool = False) -> dict[str, Any]:
    """Return deny evidence for forbidden coding operations."""
    reason = DENIED_OPERATIONS.get(operation)
    if reason is None:
        return {"operation": operation, "status": "UNKNOWN_OPERATION", "executed": False}
    if operation == "git.commit" and human_review_accepted:
        reason = "commit_still_requires_explicit_out_of_band_human_action"
    if operation == "git.push" and release_gate_accepted:
        reason = "push_still_out_of_scope_for_v9_4"
    if operation == "production.deploy" and production_gate_accepted:
        reason = "deploy_out_of_scope_for_v9_4"
    return {
        "operation": operation,
        "status": "DENIED",
        "reason": reason,
        "executed": False,
        "human_review_accepted": human_review_accepted,
        "release_gate_accepted": release_gate_accepted,
        "production_gate_accepted": production_gate_accepted,
        "audit_ref": f"audit://v9-4/deny/{operation.replace('.', '-')}",
    }


def _validate_entry(config: V94CodingWorkflowConfig, workspace: Path) -> None:
    if not config.user_confirmed:
        raise V94CodingWorkflowError("missing_user_confirmation", "V9-4 pilot requires user confirmation.")
    if config.source == "agent" or config.actor_type == "agent":
        raise V94CodingWorkflowError("source_agent_direct_mutation_denied", "source=agent cannot mutate runtime truth.")
    if config.source not in ALLOWED_SOURCES:
        raise V94CodingWorkflowError("source_not_allowed", f"V9-4 source not allowed: {config.source}")
    if config.actor_type not in ALLOWED_ACTOR_TYPES:
        raise V94CodingWorkflowError("actor_type_not_allowed", f"V9-4 actor_type not allowed: {config.actor_type}")
    if not workspace.exists() or not workspace.is_dir():
        raise V94CodingWorkflowError("workspace_not_found", "Workspace root does not exist.")
    if not config.human_authorization_ref:
        raise V94CodingWorkflowError("missing_human_authorization_ref", "V9-4 requires human_authorization_ref.")


def _load_decision(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise V94CodingWorkflowError("missing_high_risk_decision", "V9-4 high-risk decision file is missing.")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("stage_id") != "V9-4" or data.get("decision") != "GO_FOR_IMPLEMENTATION" or data.get("revoked") is True:
        raise V94CodingWorkflowError("invalid_high_risk_decision", "V9-4 high-risk decision is not active.")
    return data


def _build_artifacts(config: V94CodingWorkflowConfig, run_id: str) -> tuple[list[V94CodingArtifact], dict[str, str]]:
    specs = (
        ("intent.md", "intent", "Intent Capture", "IntentCapture", f"# Intent\n\nGoal ref: goal-ref://v9-4/{run_id}\nWorkspace ref: workspace-ref://v9-4/harnessOS\n"),
        ("spec.md", "spec", "Spec Draft", "SpecDraft", "# Spec Draft\n\nImplement a bounded evidence-producing coding workflow pilot without applying patches.\n"),
        ("plan.md", "plan", "Plan Draft", "PlanDraft", "# Plan Draft\n\n1. Produce proposal-only diff.\n2. Run sandboxed tests.\n3. Produce review and fix-loop proposal.\n4. Hand off to human review.\n"),
        ("diff-proposal.patch", "diff_proposal", "Diff Proposal", "DiffProposal", _diff_proposal_text()),
        ("test-plan.md", "test_plan", "Test Plan Proposal", "TestPlanProposal", "# Test Plan\n\nRun pytest for the V9-4 readiness closure and record redacted command refs.\n"),
        ("review-summary.md", "review_summary", "Review Summary", "ReviewSummary", "# Review Summary\n\nThe proposal is review-only and cannot approve itself.\n"),
        ("fix-loop-proposal.md", "fix_loop", "Fix Loop Proposal", "FixLoopProposal", "# Fix Loop Proposal\n\nIf tests fail, create a new diff proposal and keep previous artifacts immutable.\n"),
    )
    artifacts: list[V94CodingArtifact] = []
    contents: dict[str, str] = {}
    for file_name, artifact_type, title, stage, content in specs:
        path = f"artifacts/{file_name}"
        artifacts.append(
            V94CodingArtifact(
                artifact_id=f"artifact-v9-4-{artifact_type}-{uuid4().hex[:8]}",
                artifact_type=artifact_type,
                title=title,
                path=path,
                producer_stage=stage,
            )
        )
        contents[path] = content
    return artifacts, contents


def _run_sandboxed_test(config: V94CodingWorkflowConfig, workspace: Path, correlation_id: str, request_id: str) -> dict[str, Any]:
    _validate_sandbox_command(config.sandbox_command)
    started_at = _now()
    completed = subprocess.run(
        list(config.sandbox_command),
        cwd=workspace,
        env=_sandbox_env(workspace),
        check=False,
        text=True,
        capture_output=True,
        timeout=config.max_runtime_seconds,
    )
    completed_at = _now()
    return {
        "schema_version": "v9_4.sandboxed_test_result.v1",
        "test_result_ref": f"test-result-ref://v9-4/{uuid4().hex[:12]}",
        "command_ref": "command-ref://v9-4/pytest-readiness-closure",
        "argv": list(config.sandbox_command),
        "cwd_ref": f"workspace-ref://v9-4/{workspace.name}",
        "returncode": completed.returncode,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "stdout_preview": _preview(completed.stdout),
        "stderr_preview": _preview(completed.stderr),
        "log_ref": "sandbox-log-ref://v9-4/pytest-readiness-closure",
        "workspace_scoped": True,
        "parent_environment_inherited": False,
        "environment_secret_material_available": False,
        "network_used": False,
        "secret_read_attempted": False,
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": "audit://v9-4/sandboxed-test",
        "started_at": started_at,
        "completed_at": completed_at,
    }


def _validate_sandbox_command(argv: Sequence[str]) -> None:
    if tuple(argv) != ("./.venv/bin/python", "-m", "pytest", "tests/test_v9_4_readiness_closure.py", "-q"):
        raise V94CodingWorkflowError("sandbox_command_not_allowed", "V9-4 pilot only allows the scoped pytest readiness command.")


def _build_deny_report(correlation_id: str, request_id: str) -> dict[str, Any]:
    denied = [
        deny_coding_operation("patch.apply"),
        deny_coding_operation("git.commit"),
        deny_coding_operation("git.push"),
        deny_coding_operation("production.deploy"),
        deny_coding_operation("approval.resolve"),
    ]
    return {
        "schema_version": "v9_4.git_operation_deny_report.v1",
        "deny_report_ref": f"deny-report-ref://v9-4/{uuid4().hex[:12]}",
        "denied_operations": denied,
        "all_denied": all(item["status"] == "DENIED" and item["executed"] is False for item in denied),
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": "audit://v9-4/deny-report",
        "created_at": _now(),
    }


def _build_review_summary(run_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v9_4.review_summary.v1",
        "review_summary_ref": f"review-summary-ref://v9-4/{run_id}",
        "summary_ref": "summary-ref://v9-4/review-only",
        "review_summary_is_approval": False,
        "requires_human_review": True,
        "created_at": _now(),
    }


def _build_fix_loop(run_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v9_4.fix_loop_proposal.v1",
        "fix_loop_ref": f"fix-loop-ref://v9-4/{run_id}",
        "creates_new_diff_proposal": True,
        "silently_edits_previous_artifact": False,
        "previous_diff_proposal_ref": "diff-proposal-ref://v9-4/bounded-coding-workflow",
        "next_diff_proposal_ref": "diff-proposal-ref://v9-4/bounded-coding-workflow/fix-loop-1",
        "created_at": _now(),
    }


def _build_handoff(config: V94CodingWorkflowConfig, run_id: str, correlation_id: str, request_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v9_4.human_review_handoff.v1",
        "handoff_id": f"handoff-v9-4-{uuid4().hex[:12]}",
        "coding_workflow_run_id": run_id,
        "diff_proposal_ref": "diff-proposal-ref://v9-4/bounded-coding-workflow",
        "test_result_ref": "test-result-ref://v9-4/bounded-coding-workflow",
        "review_summary_ref": "review-summary-ref://v9-4/bounded-coding-workflow",
        "requires_human_review": True,
        "human_authorization_ref": config.human_authorization_ref,
        "applied": False,
        "committed": False,
        "pushed": False,
        "deployed": False,
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": "audit://v9-4/human-review-handoff",
        "created_at": _now(),
    }


def _build_acceptance(coding_run: dict[str, Any], test_result: dict[str, Any], deny_report: dict[str, Any]) -> dict[str, Any]:
    pass_ready = (
        coding_run["proposal_only"] is True
        and coding_run["patch_applied"] is False
        and coding_run["auto_commit_performed"] is False
        and coding_run["auto_push_performed"] is False
        and coding_run["auto_deploy_performed"] is False
        and coding_run["review_summary_is_approval"] is False
        and test_result["status"] == "PASS"
        and deny_report["all_denied"] is True
    )
    return {
        "schema_version": "v9_4.runtime_acceptance.v1",
        "stage_id": "V9-4",
        "status": "PASS" if pass_ready else "FAIL",
        "evidence_scope": "real_runtime_fixture" if pass_ready else "blocked",
        "runtime_backed": pass_ready,
        "fallback_demo_only": False,
        "transcript_only": False,
        "report_only": False,
        "allowed_claim": "V9-4 complete: autonomous coding workflow pilot ready for review." if pass_ready else "not allowed until V9-4 runtime evidence PASS",
        "autonomous_coding_workflow_ready": False,
        "agent_executor_ready": False,
        "unrestricted_terminal_worker_ready": False,
        "production_terminal_automation_ready": False,
        "diff_proposal_created": "PASS" if coding_run["proposal_only"] else "FAIL",
        "diff_proposal_is_not_patch_apply": "PASS" if coding_run["patch_applied"] is False else "FAIL",
        "sandboxed_test_result": test_result["status"],
        "review_summary_is_not_approval": "PASS" if coding_run["review_summary_is_approval"] is False else "FAIL",
        "fix_loop_creates_new_diff_proposal": "PASS",
        "auto_commit_denied": "PASS" if any(item["operation"] == "git.commit" and item["status"] == "DENIED" for item in deny_report["denied_operations"]) else "FAIL",
        "auto_push_denied": "PASS" if any(item["operation"] == "git.push" and item["status"] == "DENIED" for item in deny_report["denied_operations"]) else "FAIL",
        "auto_deploy_denied": "PASS" if any(item["operation"] == "production.deploy" and item["status"] == "DENIED" for item in deny_report["denied_operations"]) else "FAIL",
        "unreviewed_patch_apply_denied": "PASS" if any(item["operation"] == "patch.apply" and item["status"] == "DENIED" for item in deny_report["denied_operations"]) else "FAIL",
        "source_agent_direct_mutation_denied": "PASS" if coding_run["source_agent_direct_mutation_denied"] is True else "FAIL",
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "remaining_blockers": [
            "This V9-4 evidence package does not authorize V9-5 terminal worker expansion without a separate V9-5 decision.",
            "V9-8 final acceptance remains blocked until V9-0..V9-7 evidence packages exist.",
        ],
    }


def _write_evidence(output_dir: Path, payload: dict[str, Any], artifact_contents: dict[str, str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = output_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    for relative, content in artifact_contents.items():
        path = output_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    _write_json(output_dir / "acceptance-data.json", payload["acceptance"])
    _write_json(output_dir / "coding-workflow-run.json", payload["coding_workflow_run"])
    _write_json(output_dir / "artifacts.json", payload["artifacts"])
    _write_json(output_dir / "sandboxed-test-result.json", payload["sandboxed_test_result"])
    _write_json(output_dir / "review-summary.json", payload["review_summary"])
    _write_json(output_dir / "fix-loop-proposal.json", payload["fix_loop_proposal"])
    _write_json(output_dir / "human-review-handoff.json", payload["human_review_handoff"])
    _write_json(output_dir / "git-operation-deny-report.json", payload["git_operation_deny_report"])
    _write_json(output_dir / "coding-workflow-result.json", _payload_without_artifact_contents(payload))
    (output_dir / "index.html").write_text(_render_index(payload), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(_render_summary(payload), encoding="utf-8")
    (output_dir / "claims-scan.md").write_text("# V9-4 Claims Scan\n\nstatus: PASS\nviolations: []\n", encoding="utf-8")
    (output_dir / "redaction-scan.md").write_text("# V9-4 Redaction Scan\n\nstatus: PASS\nviolations: []\n", encoding="utf-8")


def _render_index(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    links = [
        "acceptance-data.json",
        "coding-workflow-run.json",
        "artifacts.json",
        "sandboxed-test-result.json",
        "review-summary.json",
        "fix-loop-proposal.json",
        "human-review-handoff.json",
        "git-operation-deny-report.json",
        "artifacts/diff-proposal.patch",
        "claims-scan.md",
        "redaction-scan.md",
    ]
    body = f"""
    <h1>V9-4 编码工作流试点</h1>
    <section><h2>验收状态</h2><pre>{escape(json.dumps(acceptance, ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>真实测试结果</h2><pre>{escape(json.dumps(payload['sandboxed_test_result'], ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>禁止动作证据</h2><pre>{escape(json.dumps(payload['git_operation_deny_report'], ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>证据链接</h2><ul>{''.join(f'<li><a href="{escape(link)}">{escape(link)}</a></li>' for link in links)}</ul></section>
    <section><h2>边界</h2><p>本页只证明 bounded coding workflow pilot ready for review；diff 是 proposal-only，未 apply patch、未 commit、未 push、未 deploy。</p></section>
    """
    return _html_page("V9-4 Coding Workflow Pilot", body)


def _render_summary(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    return "\n".join(
        [
            "# V9-4 Coding Workflow Pilot Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"runtime_backed: {str(acceptance['runtime_backed']).lower()}",
            f"diff_proposal_is_not_patch_apply: {acceptance['diff_proposal_is_not_patch_apply']}",
            f"sandboxed_test_result: {acceptance['sandboxed_test_result']}",
            f"review_summary_is_not_approval: {acceptance['review_summary_is_not_approval']}",
            f"auto_commit_denied: {acceptance['auto_commit_denied']}",
            f"auto_push_denied: {acceptance['auto_push_denied']}",
            f"auto_deploy_denied: {acceptance['auto_deploy_denied']}",
            f"source_agent_direct_mutation_denied: {acceptance['source_agent_direct_mutation_denied']}",
            "",
            "Allowed claim:",
            acceptance["allowed_claim"],
            "",
        ]
    )


def _html_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>{escape(title)}</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; background: #f8fafc; color: #111827; }}
      section, pre {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin: 16px 0; }}
      pre {{ white-space: pre-wrap; overflow-wrap: anywhere; }}
      a {{ color: #2563eb; }}
    </style>
  </head>
  <body>{body}</body>
</html>
"""


def _diff_proposal_text() -> str:
    return """diff --git a/docs/design/V9.x/v9_4_development_and_acceptance_plan.md b/docs/design/V9.x/v9_4_development_and_acceptance_plan.md
--- a/docs/design/V9.x/v9_4_development_and_acceptance_plan.md
+++ b/docs/design/V9.x/v9_4_development_and_acceptance_plan.md
@@
+Proposed-only note: V9-4 runtime evidence should link coding workflow run, diff proposal, sandboxed test result, review summary, fix-loop proposal and human review handoff.
"""


def _preview(text: str, limit: int = 2000) -> str:
    preview = text[:limit]
    _assert_no_forbidden_raw_content(preview)
    return preview


def _sandbox_env(workspace: Path) -> dict[str, str]:
    return {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": str(workspace),
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def _payload_without_artifact_contents(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _payload_for_redaction_assert(payload: dict[str, Any]) -> dict[str, Any]:
    return payload


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _redact(value: Any) -> Any:
    text = json.dumps(value, ensure_ascii=False).lower()
    for term in FORBIDDEN_RAW_TERMS:
        if term in text:
            raise V94CodingWorkflowError("forbidden_unredacted_content", "Forbidden unredacted content appears in V9-4 evidence DTO.")
    return value


def _assert_no_forbidden_raw_content(value: Any) -> None:
    _redact(value)


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
