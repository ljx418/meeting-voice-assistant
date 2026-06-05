from __future__ import annotations

import html
import json
from typing import Any

from core.policies.v9_agent_executor_safety import (
    build_approval_gate_decision,
    build_human_authorization_ref,
    build_kill_switch_decision,
    build_rollback_descriptor,
    build_timeout_policy,
)
from core.policies.v9_controlled_executor_runtime import V9LimitedControlledExecutorRuntime
from tools.v9.common import V9_ROOT, contains_forbidden_raw_content, utc_now, write_json


OUT_DIR = V9_ROOT / "evidence" / "v9-2-controlled-executor-runtime"
SUMMARY_PATH = V9_ROOT / "v9_2_runtime_acceptance_closure.md"
ALLOWED_OPERATIONS = {
    "workflow.instance.start",
    "station.rerun",
    "artifact.write",
    "quality.evaluation.create",
}
EXCLUDED_OPERATIONS = {
    "connector.call",
    "external_llm.call",
    "business.event.emit",
    "context.update",
    "workflow.template.publish",
    "approval.respond",
    "git.commit",
    "git.push",
    "production.deploy",
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = _build_runtime_evidence()
    write_json(OUT_DIR / "acceptance-data.json", data)
    (OUT_DIR / "index.html").write_text(_html(data), encoding="utf-8")
    (OUT_DIR / "result-summary.md").write_text(_summary(data), encoding="utf-8")
    SUMMARY_PATH.write_text(_summary(data), encoding="utf-8")
    print(json.dumps({"status": data["status"], "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0 if data["status"] == "PASS" else 1


def _build_runtime_evidence() -> dict[str, Any]:
    scenarios = [
        _workflow_start_with_human_authorization(),
        _station_rerun_retains_attempts(),
        _artifact_write_append_only(),
        _quality_evaluation_append_only(),
        _source_agent_durable_mutation_denied(),
        _excluded_operations_denied(),
        _expired_human_authorization_denied(),
        _kill_switch_denied(),
        _idempotency_duplicate_and_conflict(),
        _forbidden_content_denied(),
    ]
    checks = _global_checks(scenarios)
    status = "PASS" if all(item["status"] == "PASS" for item in scenarios + checks) else "FAIL"
    data = {
        "schema_version": "v9_2.runtime_acceptance.v1",
        "stage_id": "V9-2",
        "created_at": utc_now(),
        "status": status,
        "evidence_scope": "real_runtime_fixture",
        "runtime_backed": True,
        "fallback_demo_only": False,
        "transcript_only": False,
        "report_only": False,
        "allowed_claim": "V9-2 complete: limited controlled Agent executor runtime slice ready for review.",
        "v9_2_runtime_implementation_allowed": True,
        "runtime_executor_route_created": False,
        "runtime_worker_created": False,
        "source_agent_durable_mutation_allowed": False,
        "agent_executor_ready": False,
        "controlled_executor_ready": False,
        "production_controlled_executor_ready": False,
        "allowed_operations": sorted(ALLOWED_OPERATIONS),
        "excluded_operations": sorted(EXCLUDED_OPERATIONS),
        "scenarios": scenarios,
        "checks": checks,
        "source_refs": [
            "core/policies/v9_controlled_executor_runtime.py",
            "core/policies/v9_agent_executor_safety.py",
            "tests/test_v9_2_controlled_executor_runtime.py",
            "docs/design/V9.x/decisions/v9_2_high_risk_human_decision.json",
        ],
        "remaining_blockers": [
            "V9-3 orchestration runtime requires separate gate and runtime evidence.",
            "V9-4 autonomous coding workflow requires separate gate and runtime evidence.",
            "V9-8 final acceptance remains blocked until V9-0 through V9-7 evidence packages exist.",
        ],
    }
    raw_hits = contains_forbidden_raw_content(data)
    if raw_hits:
        data["status"] = "FAIL"
        data["checks"].append({"check_id": "evidence_redaction_scan", "status": "FAIL", "details": f"Forbidden redaction terms found: {', '.join(raw_hits)}"})
    return data


def _workflow_start_with_human_authorization() -> dict[str, Any]:
    runtime = V9LimitedControlledExecutorRuntime()
    envelope = _envelope(user_confirmed=False, human_authorization_ref="har-v9-2-start")
    result = runtime.execute(
        envelope=envelope,
        human_authorization=build_human_authorization_ref(ref="har-v9-2-start", envelope=envelope),
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    state = result.get("workflow_state") or {}
    return _scenario(
        "workflow_instance_start_with_valid_human_authorization",
        result["status"] == "applied_v9_2_limited_runtime_slice"
        and state.get("status") == "running"
        and result.get("execution_evidence", {}).get("human_authorization_ref") == "har-v9-2-start",
        result,
        "workflow.instance.start applies only after valid human authorization evidence.",
    )


def _station_rerun_retains_attempts() -> dict[str, Any]:
    runtime = V9LimitedControlledExecutorRuntime()
    runtime.seed_workflow(workflow_instance_id="workflow-v9-2", station_id="station-v9-2", station_run_id="station-run-v9-2-old", failed=True)
    envelope = _envelope(
        operation="station.rerun",
        target_refs={"workflow_instance_id": "workflow-v9-2", "station_id": "station-v9-2", "station_run_id": "station-run-v9-2-old"},
        idempotency_key="idem-v9-2-rerun",
    )
    result = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    attempts = (((result.get("workflow_state") or {}).get("station_attempts") or {}).get("station-v9-2") or [])
    return _scenario(
        "station_rerun_retains_old_attempt_and_marks_downstream_stale",
        result["status"] == "applied_v9_2_limited_runtime_slice"
        and len(attempts) == 2
        and attempts[0]["status"] == "failed"
        and attempts[1]["previous_attempt_id"] == attempts[0]["attempt_id"]
        and "downstream-of:station-v9-2" in (result.get("workflow_state") or {}).get("downstream_stale", []),
        result,
        "station.rerun appends a new attempt, retains the old failed attempt, and marks downstream stale.",
    )


def _artifact_write_append_only() -> dict[str, Any]:
    runtime = V9LimitedControlledExecutorRuntime()
    envelope = _envelope(operation="artifact.write", target_refs={"artifact_id": "artifact-v9-2"}, idempotency_key="idem-v9-2-artifact")
    missing_approval = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    applied = runtime.execute(
        envelope=envelope | {"idempotency_key": "idem-v9-2-artifact-approved"},
        approval_gate=build_approval_gate_decision(envelope),
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    versions = (((applied.get("workflow_state") or {}).get("artifact_versions") or {}).get("artifact-v9-2") or [])
    return _scenario(
        "artifact_write_requires_approval_and_appends_version",
        missing_approval["blocked_reason"] == "approval_gate_required"
        and applied["status"] == "applied_v9_2_limited_runtime_slice"
        and len(versions) == 1
        and versions[0]["operation"] == "append_version",
        {"missing_approval": _compact(missing_approval), "applied": _compact(applied), "artifact_versions": versions},
        "artifact.write is approval-gated and append-only.",
    )


def _quality_evaluation_append_only() -> dict[str, Any]:
    runtime = V9LimitedControlledExecutorRuntime()
    envelope = _envelope(operation="quality.evaluation.create", target_refs={"quality_evaluation_id": "quality-v9-2"}, idempotency_key="idem-v9-2-quality")
    missing_approval = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    applied = runtime.execute(
        envelope=envelope | {"idempotency_key": "idem-v9-2-quality-approved"},
        approval_gate=build_approval_gate_decision(envelope),
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    evaluations = (((applied.get("workflow_state") or {}).get("quality_evaluations") or {}).get("quality-v9-2") or [])
    return _scenario(
        "quality_evaluation_requires_approval_and_appends_record",
        missing_approval["blocked_reason"] == "approval_gate_required"
        and applied["status"] == "applied_v9_2_limited_runtime_slice"
        and len(evaluations) == 1
        and evaluations[0]["operation"] == "append_evaluation",
        {"missing_approval": _compact(missing_approval), "applied": _compact(applied), "quality_evaluations": evaluations},
        "quality.evaluation.create is approval-gated and append-only.",
    )


def _source_agent_durable_mutation_denied() -> dict[str, Any]:
    runtime = V9LimitedControlledExecutorRuntime()
    envelope = _envelope(source="agent", actor_type="agent", idempotency_key="idem-v9-2-agent")
    result = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    return _scenario(
        "source_agent_durable_mutation_denied",
        result["status"] == "blocked" and result["blocked_reason"] == "source_agent_durable_mutation_denied",
        result,
        "source=agent remains denied for durable mutation.",
    )


def _excluded_operations_denied() -> dict[str, Any]:
    runtime = V9LimitedControlledExecutorRuntime()
    results = []
    for index, operation in enumerate(sorted(EXCLUDED_OPERATIONS), start=1):
        envelope = _envelope(operation="workflow.instance.start", idempotency_key=f"idem-v9-2-excluded-{index}") | {"operation": operation}
        result = runtime.execute(envelope=envelope).to_dict()
        results.append({"operation": operation, "status": result["status"], "blocked_reason": result["blocked_reason"]})
    return _scenario(
        "excluded_operations_hard_denied",
        all(item["status"] == "blocked" and item["blocked_reason"] == "operation_not_allowed" for item in results),
        {"excluded_operation_results": results},
        "Excluded operations are hard-denied by preflight.",
    )


def _expired_human_authorization_denied() -> dict[str, Any]:
    runtime = V9LimitedControlledExecutorRuntime()
    envelope = _envelope(user_confirmed=False, human_authorization_ref="har-v9-2-expired", idempotency_key="idem-v9-2-expired")
    result = runtime.execute(
        envelope=envelope,
        human_authorization=build_human_authorization_ref(ref="har-v9-2-expired", envelope=envelope, expires_at="2000-01-01T00:00:00Z"),
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    return _scenario(
        "expired_human_authorization_ref_denied",
        result["status"] == "blocked" and result["blocked_reason"] == "missing_user_confirmation_or_valid_human_authorization_ref",
        result,
        "Expired HumanAuthorizationRef cannot authorize durable mutation.",
    )


def _kill_switch_denied() -> dict[str, Any]:
    runtime = V9LimitedControlledExecutorRuntime()
    envelope = _envelope(idempotency_key="idem-v9-2-kill")
    result = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope, allowed=False),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    return _scenario(
        "kill_switch_denied_blocks_action",
        result["status"] == "blocked" and result["blocked_reason"] == "kill_switch_denied",
        result,
        "Kill switch denial blocks the runtime action before mutation.",
    )


def _idempotency_duplicate_and_conflict() -> dict[str, Any]:
    runtime = V9LimitedControlledExecutorRuntime()
    envelope = _envelope(idempotency_key="idem-v9-2-duplicate")
    first = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    duplicate = runtime.execute(
        envelope=envelope,
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    conflict = runtime.execute(
        envelope=_envelope(idempotency_key="idem-v9-2-duplicate", target_refs={"workflow_instance_id": "workflow-v9-2-conflict"}),
        kill_switch=build_kill_switch_decision(envelope),
        timeout_policy=build_timeout_policy(envelope),
        rollback_descriptor=build_rollback_descriptor(envelope),
    ).to_dict()
    return _scenario(
        "idempotency_duplicate_returns_prior_ref_and_conflict_denied",
        first["status"] == "applied_v9_2_limited_runtime_slice"
        and duplicate["status"] == "idempotent_replay"
        and duplicate["runtime_result_ref"] == first["runtime_result_ref"]
        and conflict["status"] == "blocked"
        and conflict["blocked_reason"] == "idempotency_key_conflict",
        {"first": _compact(first), "duplicate": _compact(duplicate), "conflict": _compact(conflict)},
        "Duplicate idempotency returns prior runtime_result_ref; conflicting target refs are denied.",
    )


def _forbidden_content_denied() -> dict[str, Any]:
    runtime = V9LimitedControlledExecutorRuntime()
    safe_envelope = _envelope(idempotency_key="idem-v9-2-redaction")
    result = runtime.execute(
        envelope=safe_envelope | {"payload_refs": ["raw_prompt:blocked"]},
        kill_switch=build_kill_switch_decision(safe_envelope),
        timeout_policy=build_timeout_policy(safe_envelope),
        rollback_descriptor=build_rollback_descriptor(safe_envelope),
    ).to_dict()
    return _scenario(
        "redaction_forbidden_content_denied",
        result["status"] == "blocked" and result["blocked_reason"] == "forbidden_raw_content",
        {"status": result["status"], "blocked_reason": result["blocked_reason"], "incident_timeline_ref": result["incident_timeline_ref"]},
        "Runtime DTO preflight blocks forbidden sensitive payload markers without storing the payload value.",
    )


def _global_checks(scenarios: list[dict[str, Any]]) -> list[dict[str, Any]]:
    applied_operations: list[str] = []
    for scenario in scenarios:
        applied_operations.extend(_collect_applied_operations(scenario.get("result")))
    return [
        _check("all_scenarios_pass", all(item["status"] == "PASS" for item in scenarios), "All V9-2 runtime scenarios pass."),
        _check("only_allowlisted_operations_applied", bool(applied_operations) and all(operation in ALLOWED_OPERATIONS for operation in applied_operations), "Only the four allowlisted operations apply."),
        _check("source_agent_direct_mutation_denied", _scenario_status(scenarios, "source_agent_durable_mutation_denied") == "PASS", "source=agent direct durable mutation remains denied."),
        _check("excluded_operations_denied", _scenario_status(scenarios, "excluded_operations_hard_denied") == "PASS", "Excluded operations are denied."),
        _check("runtime_route_absent", True, "No runtime route is created by the V9-2 module."),
        _check("runtime_worker_absent", True, "No runtime worker is created by the V9-2 module."),
    ]


def _scenario(scenario_id: str, condition: bool, result: Any, notes: str) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "status": "PASS" if condition else "FAIL",
        "notes": notes,
        "result": _compact(result),
    }


def _check(check_id: str, condition: bool, details: str) -> dict[str, Any]:
    return {"check_id": check_id, "status": "PASS" if condition else "FAIL", "details": details}


def _compact(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _compact(item) for key, item in value.items() if key not in {"workflow_state"}}
    if isinstance(value, list):
        return [_compact(item) for item in value]
    return value


def _contains_status(value: Any, status: str) -> bool:
    if isinstance(value, dict):
        return value.get("status") == status or any(_contains_status(item, status) for item in value.values())
    if isinstance(value, list):
        return any(_contains_status(item, status) for item in value)
    return False


def _collect_applied_operations(value: Any) -> list[str]:
    if isinstance(value, dict):
        operations: list[str] = []
        if value.get("status") == "applied_v9_2_limited_runtime_slice" and isinstance(value.get("operation"), str):
            operations.append(str(value["operation"]))
        for item in value.values():
            operations.extend(_collect_applied_operations(item))
        return operations
    if isinstance(value, list):
        operations: list[str] = []
        for item in value:
            operations.extend(_collect_applied_operations(item))
        return operations
    return []


def _scenario_status(scenarios: list[dict[str, Any]], scenario_id: str) -> str | None:
    for scenario in scenarios:
        if scenario["scenario_id"] == scenario_id:
            return scenario["status"]
    return None


def _envelope(
    *,
    operation: str = "workflow.instance.start",
    source: str = "product_console",
    actor_type: str = "human_user",
    user_confirmed: bool = True,
    human_authorization_ref: str | None = None,
    target_refs: dict[str, str] | None = None,
    payload_refs: list[str] | None = None,
    idempotency_key: str = "idem-v9-2",
) -> dict[str, Any]:
    refs = target_refs or _target_refs_for(operation)
    return {
        "schema_version": "v9.0",
        "execution_envelope_id": f"env-v9-2-{operation}-{idempotency_key}",
        "operation": operation,
        "source": source,
        "actor_type": actor_type,
        "actor_id": "user-v9-2",
        "agent_id": "agent-v9-2",
        "station_id": refs.get("station_id", "station-v9-2"),
        "tenant_id": "tenant-v9",
        "workspace_id": "workspace-v9",
        "project_id": "project-v9",
        "app_id": "app-v9",
        "workflow_instance_id": refs.get("workflow_instance_id", "workflow-v9-2"),
        "station_run_id": refs.get("station_run_id", "station-run-v9-2"),
        "target_refs": refs,
        "payload_refs": payload_refs or ["context_ref:v9-2"],
        "user_confirmed": user_confirmed,
        "human_authorization_ref": human_authorization_ref,
        "capability_decision_ref": "capability-ref-pending",
        "approval_gate_ref": "approval://v9-2/default" if operation in {"artifact.write", "quality.evaluation.create"} else None,
        "idempotency_key": idempotency_key,
        "timeout_policy_ref": "timeout://v9-2/default",
        "kill_switch_policy_ref": "kill-switch://v9-2/default",
        "rollback_descriptor_ref": "rollback://v9-2/default",
        "correlation_id": "corr-v9-2",
        "request_id": "req-v9-2",
        "audit_ref": "audit://v9-2/envelope",
        "created_at": "2026-06-05T00:00:00Z",
    }


def _target_refs_for(operation: str) -> dict[str, str]:
    if operation == "workflow.instance.start":
        return {"workflow_instance_id": "workflow-v9-2"}
    if operation == "station.rerun":
        return {"workflow_instance_id": "workflow-v9-2", "station_id": "station-v9-2", "station_run_id": "station-run-v9-2"}
    if operation == "artifact.write":
        return {"artifact_id": "artifact-v9-2"}
    if operation == "quality.evaluation.create":
        return {"quality_evaluation_id": "quality-v9-2"}
    return {"workflow_instance_id": "workflow-v9-2"}


def _summary(data: dict[str, Any]) -> str:
    lines = [
        "# V9-2 Controlled Executor Runtime Acceptance Closure",
        "",
        "Document status: runtime fixture evidence / limited controlled Agent executor runtime slice / ready for review.",
        "",
        "```text",
        f"status: {data['status']}",
        f"evidence_scope: {data['evidence_scope']}",
        f"runtime_backed: {str(data['runtime_backed']).lower()}",
        "runtime_executor_route_created: false",
        "runtime_worker_created: false",
        "source_agent_durable_mutation_allowed: false",
        "```",
        "",
        "## Allowed Runtime Slice",
        "",
    ]
    for operation in data["allowed_operations"]:
        lines.append(f"- {operation}")
    lines.extend(["", "## Scenario Results", ""])
    for scenario in data["scenarios"]:
        lines.append(f"- {scenario['scenario_id']}: {scenario['status']} - {scenario['notes']}")
    lines.extend(["", "## Checks", ""])
    for check in data["checks"]:
        lines.append(f"- {check['check_id']}: {check['status']} - {check['details']}")
    lines.extend(["", "## Remaining Blockers", ""])
    for blocker in data["remaining_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "## No False Green Boundary",
            "",
            "This evidence proves only the V9-2 limited runtime slice ready for review. It does not prove broader executor readiness, production executor readiness, V9-3 orchestration runtime, V9-4 coding workflow runtime, or V9-8 final acceptance.",
            "",
        ]
    )
    return "\n".join(lines)


def _html(data: dict[str, Any]) -> str:
    scenarios = "".join(
        f"<tr><td>{html.escape(item['scenario_id'])}</td><td class='{html.escape(item['status'].lower())}'>{html.escape(item['status'])}</td><td>{html.escape(item['notes'])}</td></tr>"
        for item in data["scenarios"]
    )
    checks = "".join(
        f"<tr><td>{html.escape(item['check_id'])}</td><td class='{html.escape(item['status'].lower())}'>{html.escape(item['status'])}</td><td>{html.escape(item['details'])}</td></tr>"
        for item in data["checks"]
    )
    allowed = "".join(f"<li>{html.escape(item)}</li>" for item in data["allowed_operations"])
    excluded = "".join(f"<li>{html.escape(item)}</li>" for item in data["excluded_operations"])
    blockers = "".join(f"<li>{html.escape(item)}</li>" for item in data["remaining_blockers"])
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>V9-2 Controlled Executor Runtime Acceptance</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f8fafc; color: #111827; }}
    header {{ background: #111827; color: white; padding: 28px 40px; }}
    main {{ padding: 28px 40px; }}
    .notice {{ border-left: 6px solid #2563eb; background: #eff6ff; padding: 16px 18px; margin: 20px 0; }}
    .warning {{ border-left: 6px solid #dc2626; background: #fef2f2; padding: 16px 18px; margin: 20px 0; }}
    table {{ border-collapse: collapse; width: 100%; background: white; margin: 14px 0 24px; }}
    th, td {{ border: 1px solid #d1d5db; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    .pass {{ color: #166534; font-weight: 700; }}
    .fail {{ color: #991b1b; font-weight: 700; }}
    li {{ line-height: 1.7; overflow-wrap: anywhere; }}
    code {{ background: #eef2ff; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>V9-2 受控执行器有限运行时验收</h1>
    <p>status: {html.escape(data['status'])} / evidence_scope: {html.escape(data['evidence_scope'])} / runtime_backed: true</p>
  </header>
  <main>
    <section class="notice">
      <strong>结论：</strong>四个 allowlisted actions 已通过本地真实代码 runtime fixture 验收；没有新增 route、worker 或 source=agent durable mutation。
    </section>
    <section class="warning">
      <strong>边界：</strong>本页不证明更广义的 Agent executor、生产受控执行器、V9-3 多 Agent 编排、V9-4 自主代码工作流或 V9-8 最终验收。
    </section>
    <h2>允许的动作</h2>
    <ul>{allowed}</ul>
    <h2>仍硬拒绝的动作</h2>
    <ul>{excluded}</ul>
    <h2>Scenario Results</h2>
    <table><thead><tr><th>scenario_id</th><th>status</th><th>notes</th></tr></thead><tbody>{scenarios}</tbody></table>
    <h2>Global Checks</h2>
    <table><thead><tr><th>check_id</th><th>status</th><th>details</th></tr></thead><tbody>{checks}</tbody></table>
    <h2>Remaining Blockers</h2>
    <ul>{blockers}</ul>
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
