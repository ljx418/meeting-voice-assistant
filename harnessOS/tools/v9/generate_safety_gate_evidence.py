from __future__ import annotations

import html
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from core.policies.v9_agent_executor_safety import (
    V9AgentExecutorSafetyGate,
    V9SafetyGateError,
    build_approval_gate_decision,
    build_human_authorization_ref,
    build_kill_switch_decision,
    build_rollback_descriptor,
    build_timeout_policy,
)
from tools.v9.common import V9_ROOT, read_json, utc_now, write_json


OUT_DIR = V9_ROOT / "evidence" / "v9-1-safety-gate-implementation"
REPORTS = {
    "contract_validation": V9_ROOT / "reports" / "v9_1_contract_validation_report.json",
    "negative_tests": V9_ROOT / "reports" / "v9_1_negative_test_results.json",
    "no_false_green": V9_ROOT / "reports" / "v9_1_no_false_green_scan.json",
    "redaction": V9_ROOT / "reports" / "v9_1_redaction_scan.json",
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _clear_previous_outputs()
    _refresh_reports()
    scenarios = _run_scenarios()
    reports = {name: _report_summary(path) for name, path in REPORTS.items()}
    status = "PASS" if all(item["status"] == "PASS" for item in scenarios) and all(report["status"] == "PASS" for report in reports.values()) else "FAIL"
    data = {
        "schema_version": "v9_1.safety_gate_implementation.v1",
        "stage_id": "V9-1",
        "title": "V9-1 Agent Executor Safety Gate Implementation Evidence",
        "created_at": utc_now(),
        "status": status,
        "evidence_scope": "real_code_policy_validation",
        "runtime_backed": False,
        "runtime_execution_allowed": False,
        "runtime_executor_route_created": False,
        "runtime_worker_created": False,
        "controlled_executor_action_execution": False,
        "source_agent_durable_mutation_allowed": False,
        "agent_executor_ready": False,
        "controlled_executor_ready": False,
        "production_controlled_executor_ready": False,
        "full_multi_agent_orchestration_ready": False,
        "autonomous_coding_workflow_ready": False,
        "allowed_claim": "V9-1 complete: Agent Executor Safety Gate implementation ready for review.",
        "blocked_capability_claim_flags": {
            "agent_executor_ready": False,
            "controlled_executor_ready": False,
            "production_controlled_executor_ready": False,
            "full_multi_agent_orchestration_ready": False,
            "autonomous_coding_workflow_ready": False,
            "complete_workflow_studio_ready": False,
        },
        "scenarios": scenarios,
        "reports": reports,
        "source_refs": [
            "core/policies/v9_agent_executor_safety.py",
            "tests/test_v9_1_agent_executor_safety_gate.py",
            "docs/design/V9.x/decisions/v9_1_high_risk_human_decision.json",
            "docs/design/V9.x/v9_1_agent_executor_safety_gate_implementation_plan.md",
        ],
    }
    write_json(OUT_DIR / "acceptance-data.json", data)
    (OUT_DIR / "result-summary.md").write_text(_summary_markdown(data), encoding="utf-8")
    (OUT_DIR / "index.html").write_text(_html(data), encoding="utf-8")
    print(json.dumps({"status": status, "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0 if status == "PASS" else 1


def _clear_previous_outputs() -> None:
    for filename in ("acceptance-data.json", "index.html", "result-summary.md"):
        path = OUT_DIR / filename
        if path.exists():
            path.unlink()


def _refresh_reports() -> None:
    commands = [
        [sys.executable, "-m", "tools.v9.validate_schema_bundle", "--write-reports"],
        [sys.executable, "-m", "tools.v9.scan_no_false_green", "--write-report"],
        [sys.executable, "-m", "tools.v9.scan_redaction_forbidden_content", "--write-report"],
    ]
    for command in commands:
        subprocess.run(command, check=True, text=True, capture_output=True)


def _run_scenarios() -> list[dict[str, Any]]:
    scenario_defs: list[tuple[str, str, Callable[[], dict[str, Any]]]] = [
        ("workflow_start_safety_gate_allow_no_runtime_execution", "workflow.instance.start with user confirmation is accepted for safety-gate handoff only.", _scenario_workflow_start_allowed),
        ("source_agent_durable_mutation_denied", "source=agent durable mutation is denied even with user confirmation.", _scenario_source_agent_denied),
        ("missing_confirmation_or_authorization_denied", "Durable mutation without user confirmation or valid HumanAuthorizationRef is denied.", _scenario_missing_authorization_denied),
        ("valid_human_authorization_ref_allows_safety_gate", "Valid HumanAuthorizationRef can satisfy the safety-gate authorization contract.", _scenario_valid_har_allowed),
        ("expired_human_authorization_ref_denied", "Expired HumanAuthorizationRef is rejected.", _scenario_expired_har_denied),
        ("wrong_tenant_human_authorization_ref_denied", "Cross-tenant HumanAuthorizationRef is rejected.", _scenario_wrong_tenant_har_denied),
        ("artifact_write_requires_approval_gate", "artifact.write requires approval gate and remains runtime_execution_allowed=false.", _scenario_artifact_write_requires_approval),
        ("kill_switch_denied", "Kill switch denial blocks safety-gate handoff.", _scenario_kill_switch_denied),
        ("timeout_policy_required", "Timeout policy is required for candidate actions.", _scenario_timeout_required),
        ("rollback_descriptor_required", "Rollback descriptor is required for candidate actions.", _scenario_rollback_required),
        ("raw_content_rejected", "Raw prompt/content markers are rejected before a decision is returned.", _scenario_raw_content_rejected),
    ]
    scenarios = []
    for scenario_id, title, fn in scenario_defs:
        try:
            result = fn()
            passed = _scenario_passed(result)
            scenarios.append({"scenario_id": scenario_id, "title": title, "status": "PASS" if passed else "FAIL", **result})
        except Exception as exc:  # pragma: no cover - converted into evidence for audit readability.
            scenarios.append({"scenario_id": scenario_id, "title": title, "status": "FAIL", "error": repr(exc)})
    return scenarios


def _scenario_workflow_start_allowed() -> dict[str, Any]:
    envelope = _make_envelope()
    decision = _evaluate(envelope)
    return _expect_decision(decision, expected="allow", denial_reason=None)


def _scenario_source_agent_denied() -> dict[str, Any]:
    envelope = _make_envelope(source="agent", actor_type="agent")
    decision = _evaluate(envelope)
    return _expect_decision(decision, expected="deny", denial_reason="source_agent_durable_mutation_denied")


def _scenario_missing_authorization_denied() -> dict[str, Any]:
    envelope = _make_envelope(user_confirmed=False, human_authorization_ref=None)
    decision = _evaluate(envelope)
    return _expect_decision(decision, expected="deny", denial_reason="missing_user_confirmation_or_valid_human_authorization_ref")


def _scenario_valid_har_allowed() -> dict[str, Any]:
    envelope = _make_envelope(user_confirmed=False, human_authorization_ref="har-v9-1-valid")
    authorization = build_human_authorization_ref(ref="har-v9-1-valid", envelope=envelope)
    decision = _evaluate(envelope, human_authorization=authorization)
    return _expect_decision(decision, expected="allow", denial_reason=None)


def _scenario_expired_har_denied() -> dict[str, Any]:
    envelope = _make_envelope(user_confirmed=False, human_authorization_ref="har-v9-1-expired")
    authorization = build_human_authorization_ref(ref="har-v9-1-expired", envelope=envelope, expires_at="2020-01-01T00:00:00Z")
    decision = _evaluate(envelope, human_authorization=authorization)
    return _expect_decision(decision, expected="deny", denial_reason="missing_user_confirmation_or_valid_human_authorization_ref")


def _scenario_wrong_tenant_har_denied() -> dict[str, Any]:
    envelope = _make_envelope(user_confirmed=False, human_authorization_ref="har-v9-1-wrong-tenant")
    authorization = build_human_authorization_ref(ref="har-v9-1-wrong-tenant", envelope=envelope) | {"tenant_id": "tenant-other"}
    decision = _evaluate(envelope, human_authorization=authorization)
    return _expect_decision(decision, expected="deny", denial_reason="missing_user_confirmation_or_valid_human_authorization_ref")


def _scenario_artifact_write_requires_approval() -> dict[str, Any]:
    envelope = _make_envelope(operation="artifact.write")
    without_approval = _evaluate(envelope)
    with_approval = _evaluate(envelope, approval_gate=build_approval_gate_decision(envelope))
    first = _expect_decision(without_approval, expected="deny", denial_reason="approval_gate_required")
    second = _expect_decision(with_approval, expected="allow", denial_reason=None)
    return {
        "observed_decisions": [first["observed_decision"], second["observed_decision"]],
        "observed_denial_reasons": [first["observed_denial_reason"], second["observed_denial_reason"]],
        "runtime_execution_allowed": False,
        "redaction_status": second["redaction_status"],
        "passed": first["passed"] and second["passed"] and with_approval["requires_approval_gate"] is True,
    }


def _scenario_kill_switch_denied() -> dict[str, Any]:
    envelope = _make_envelope()
    decision = _evaluate(envelope, kill_switch=build_kill_switch_decision(envelope, allowed=False))
    return _expect_decision(decision, expected="deny", denial_reason="kill_switch_denied")


def _scenario_timeout_required() -> dict[str, Any]:
    envelope = _make_envelope()
    decision = V9AgentExecutorSafetyGate().evaluate(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    return _expect_decision(decision, expected="deny", denial_reason="missing_timeout_policy")


def _scenario_rollback_required() -> dict[str, Any]:
    envelope = _make_envelope()
    decision = V9AgentExecutorSafetyGate().evaluate(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
    ).to_dict()
    return _expect_decision(decision, expected="deny", denial_reason="missing_rollback_descriptor")


def _scenario_raw_content_rejected() -> dict[str, Any]:
    envelope = _make_envelope(payload_refs=["raw_prompt:blocked"])
    try:
        _evaluate(envelope)
    except V9SafetyGateError as exc:
        return {
            "observed_error_code": exc.code,
            "observed_reason": exc.reason,
            "runtime_execution_allowed": False,
            "redaction_status": "PASS",
            "passed": exc.reason == "forbidden_raw_content",
        }
    return {"runtime_execution_allowed": False, "passed": False, "redaction_status": "FAIL"}


def _evaluate(
    envelope: dict[str, Any],
    *,
    human_authorization: dict[str, Any] | None = None,
    approval_gate: dict[str, Any] | None = None,
    kill_switch: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return V9AgentExecutorSafetyGate().evaluate(
        envelope=envelope,
        human_authorization=human_authorization,
        approval_gate=approval_gate,
        kill_switch=kill_switch if kill_switch is not None else build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()


def _expect_decision(decision: dict[str, Any], *, expected: str, denial_reason: str | None) -> dict[str, Any]:
    return {
        "observed_decision": decision["decision"],
        "observed_denial_reason": decision["denial_reason"],
        "runtime_execution_allowed": decision["runtime_execution_allowed"],
        "redaction_status": decision["evidence"]["redaction_status"],
        "capability_decision_ref": decision["capability_decision_ref"],
        "passed": decision["decision"] == expected and decision["denial_reason"] == denial_reason and decision["runtime_execution_allowed"] is False,
    }


def _scenario_passed(result: dict[str, Any]) -> bool:
    return result.get("passed") is True and result.get("runtime_execution_allowed") is False and result.get("redaction_status") == "PASS"


def _make_envelope(
    *,
    operation: str = "workflow.instance.start",
    source: str = "product_console",
    actor_type: str = "human_user",
    user_confirmed: bool = True,
    human_authorization_ref: str | None = None,
    target_refs: dict[str, str] | None = None,
    payload_refs: list[str] | None = None,
) -> dict[str, Any]:
    refs = target_refs or _target_refs_for(operation)
    return {
        "schema_version": "v9.0",
        "execution_envelope_id": f"env-{operation.replace('.', '-')}-{source}",
        "operation": operation,
        "source": source,
        "actor_type": actor_type,
        "actor_id": "user-v9-1",
        "agent_id": "agent-v9-1",
        "station_id": refs.get("station_id", "station-v9-1"),
        "tenant_id": "tenant-v9",
        "workspace_id": "workspace-v9",
        "project_id": "project-v9",
        "app_id": "app-v9",
        "workflow_instance_id": refs.get("workflow_instance_id", "workflow-v9"),
        "station_run_id": refs.get("station_run_id", "station-run-v9"),
        "target_refs": refs,
        "payload_refs": payload_refs or ["context_ref:v9-1"],
        "user_confirmed": user_confirmed,
        "human_authorization_ref": human_authorization_ref,
        "capability_decision_ref": "capability-ref-pending",
        "approval_gate_ref": "approval://v9-1/default" if operation in {"artifact.write", "quality.evaluation.create"} else None,
        "idempotency_key": "idem-v9-1",
        "timeout_policy_ref": "timeout://v9-1/default",
        "kill_switch_policy_ref": "kill-switch://v9-1/default",
        "rollback_descriptor_ref": "rollback://v9-1/default",
        "correlation_id": "corr-v9-1",
        "request_id": "req-v9-1",
        "audit_ref": "audit://v9-1/envelope",
        "created_at": "2026-06-05T00:00:00Z",
    }


def _target_refs_for(operation: str) -> dict[str, str]:
    if operation == "workflow.instance.start":
        return {"workflow_instance_id": "workflow-v9"}
    if operation == "station.rerun":
        return {"station_id": "station-v9-1", "station_run_id": "station-run-v9"}
    if operation == "artifact.write":
        return {"artifact_id": "artifact-v9"}
    if operation == "quality.evaluation.create":
        return {"quality_evaluation_id": "quality-v9"}
    raise ValueError(f"unexpected operation: {operation}")


def _report_summary(path: Path) -> dict[str, Any]:
    data = read_json(path)
    return {
        "path": str(path),
        "status": data.get("status"),
        "runtime_evidence": data.get("runtime_evidence"),
        "violations": data.get("violations", []),
        "created_at": data.get("created_at"),
    }


def _summary_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# V9-1 Safety Gate Implementation Evidence",
        "",
        "```text",
        f"status: {data['status']}",
        "evidence_scope: real_code_policy_validation",
        "runtime_execution_allowed: false",
        "runtime_executor_route_created: false",
        "runtime_worker_created: false",
        "source_agent_durable_mutation_allowed: false",
        "agent_executor_ready: false",
        "```",
        "",
        "## Scenarios",
        "",
    ]
    for scenario in data["scenarios"]:
        lines.append(f"- {scenario['scenario_id']}: {scenario['status']}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This evidence package validates V9-1 Safety Gate policy behavior only. It does not implement runtime executor routes, runtime workers, controlled executor action execution, V9-2/V9-3/V9-4 runtime, or Agent executor readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def _html(data: dict[str, Any]) -> str:
    scenario_cards = []
    for scenario in data["scenarios"]:
        scenario_cards.append(
            f"""
            <section class="card">
              <h2>{html.escape(scenario['scenario_id'])}</h2>
              <p class="status {html.escape(scenario['status'].lower())}">{html.escape(scenario['status'])}</p>
              <p>{html.escape(scenario.get('title', ''))}</p>
              <p>runtime_execution_allowed: {html.escape(str(scenario.get('runtime_execution_allowed')))}</p>
              <p>redaction_status: {html.escape(str(scenario.get('redaction_status')))}</p>
              <pre>{html.escape(json.dumps({k: v for k, v in scenario.items() if k not in {'title'}}, ensure_ascii=False, indent=2))}</pre>
            </section>
            """
        )
    reports = "".join(
        f"<li>{html.escape(name)}: {html.escape(str(report['status']))} ({html.escape(report['path'])})</li>"
        for name, report in data["reports"].items()
    )
    blocked_flags = "".join(f"<li>{html.escape(name)}: {html.escape(str(value))}</li>" for name, value in data["blocked_capability_claim_flags"].items())
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>V9-1 Safety Gate Implementation Evidence</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f8fafc; color: #111827; }}
    header {{ background: #111827; color: #fff; padding: 28px 40px; }}
    main {{ padding: 28px 40px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }}
    .card {{ background: #fff; border: 1px solid #d1d5db; border-radius: 8px; padding: 16px; }}
    .status {{ display: inline-block; padding: 4px 10px; border-radius: 999px; font-weight: 700; }}
    .pass {{ background: #dcfce7; color: #166534; }}
    .fail {{ background: #fee2e2; color: #991b1b; }}
    .warning {{ border-left: 6px solid #dc2626; background: #fef2f2; padding: 16px 18px; margin: 20px 0; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #f3f4f6; padding: 10px; border-radius: 6px; font-size: 12px; }}
    ul {{ line-height: 1.7; }}
  </style>
</head>
<body>
  <header>
    <h1>V9-1 Agent Executor Safety Gate 实现证据</h1>
    <p>status: {html.escape(data['status'])} / evidence_scope: real_code_policy_validation / runtime_execution_allowed: false</p>
  </header>
  <main>
    <section class="warning">
      <strong>关键边界：</strong>本页只证明 Safety Gate validator / CapabilityResolver deny-by-default / contract checks 可运行；没有 runtime executor route、没有 runtime worker、没有 source=agent durable mutation。
    </section>
    <h2>全局运行时边界</h2>
    <ul>
      <li>runtime_executor_route_created: {html.escape(str(data['runtime_executor_route_created']))}</li>
      <li>runtime_worker_created: {html.escape(str(data['runtime_worker_created']))}</li>
      <li>controlled_executor_action_execution: {html.escape(str(data['controlled_executor_action_execution']))}</li>
      <li>source_agent_durable_mutation_allowed: {html.escape(str(data['source_agent_durable_mutation_allowed']))}</li>
      <li>agent_executor_ready: {html.escape(str(data['agent_executor_ready']))}</li>
    </ul>
    <h2>阻断能力标志</h2>
    <ul>{blocked_flags}</ul>
    <h2>场景证据</h2>
    <div class="grid">{''.join(scenario_cards)}</div>
    <h2>扫描与合同报告</h2>
    <ul>{reports}</ul>
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
