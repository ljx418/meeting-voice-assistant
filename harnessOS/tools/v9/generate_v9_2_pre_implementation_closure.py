from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

from tools.v9.common import ROOT, V9_ROOT, read_json, utc_now, write_json


OUT_DIR = V9_ROOT / "evidence" / "v9-2-controlled-executor-pre-implementation"
SUMMARY_PATH = V9_ROOT / "v9_2_pre_implementation_audit_closure.md"
FIXTURE_DIR = V9_ROOT / "fixtures" / "v9-2-controlled-executor"
V9_1_INTERNAL_AUDIT = V9_ROOT / "evidence" / "v9-1-internal-independent-audit" / "internal-audit-data.json"
V9_1_SAFETY_GATE = V9_ROOT / "evidence" / "v9-1-safety-gate-implementation" / "acceptance-data.json"
V9_2_DECISION = V9_ROOT / "decisions" / "v9_2_high_risk_human_decision.json"
V9_2_PLAN = V9_ROOT / "v9_2_pre_implementation_development_and_acceptance_plan.md"
V9_2_ENGINEERING = V9_ROOT / "v9_2_controlled_executor_engineering_design.md"
V9_2_SPEC = V9_ROOT / "v9_2_controlled_executor_implementation_spec.md"

REQUIRED_FIXTURES = {
    "workflow_instance_start_with_human_authorization_ref.json",
    "station_rerun_with_user_confirmed.json",
    "artifact_write_append_only_with_approval_gate.json",
    "quality_evaluation_append_only_with_approval_gate.json",
    "source_agent_durable_mutation_denied.json",
    "expired_human_authorization_ref_denied.json",
    "idempotency_duplicate_returns_prior_ref.json",
    "kill_switch_denied_blocks_action.json",
}
ALLOWLIST = {
    "workflow.instance.start",
    "station.rerun",
    "artifact.write",
    "quality.evaluation.create",
}
EXCLUDED_ACTIONS = {
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
    data = _build_closure()
    write_json(OUT_DIR / "pre-implementation-data.json", data)
    (OUT_DIR / "index.html").write_text(_html(data), encoding="utf-8")
    (OUT_DIR / "result-summary.md").write_text(_summary(data), encoding="utf-8")
    SUMMARY_PATH.write_text(_summary(data), encoding="utf-8")
    print(json.dumps({"status": data["status"], "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0 if data["status"] == "PASS" else 1


def _build_closure() -> dict[str, Any]:
    v9_1_audit = read_json(V9_1_INTERNAL_AUDIT)
    v9_1_safety_gate = read_json(V9_1_SAFETY_GATE)
    decision = read_json(V9_2_DECISION)
    fixtures = [_read_fixture(path) for path in sorted(FIXTURE_DIR.glob("*.json"))]
    fixture_names = {item["path"].name for item in fixtures}
    fixture_checks = _fixture_checks(fixtures)
    doc_checks = _document_checks()
    checks = [
        _check("v9_1_internal_audit_pass", v9_1_audit.get("status") == "PASS", "V9-1 internal audit must pass before V9-2 planning closure."),
        _check("v9_1_safety_gate_pass", v9_1_safety_gate.get("status") == "PASS", "V9-1 Safety Gate implementation evidence must pass."),
        _check("v9_1_runtime_still_blocked", v9_1_safety_gate.get("runtime_execution_allowed") is False, "V9-1 evidence still blocks runtime execution."),
        _check("v9_2_high_risk_decision_recorded", decision.get("decision") == "GO_FOR_IMPLEMENTATION", "V9-2 limited runtime implementation has scoped human high-risk approval."),
        _check("v9_2_decision_blocks_forbidden_work", _decision_blocks_runtime(decision), "V9-2 decision blocks routes, workers, excluded actions, source=agent mutation and overclaim."),
        _check("required_fixture_set_present", REQUIRED_FIXTURES.issubset(fixture_names), "V9-2 pre-implementation fixture set is present."),
        *fixture_checks,
        *doc_checks,
        _check("no_v9_2_forbidden_route_or_worker_detected", not _forbidden_route_or_worker_detected(), "No V9-2 runtime route or worker implementation is present."),
    ]
    status = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    return {
        "schema_version": "v9_2.pre_implementation_closure.v1",
        "stage_id": "V9-2",
        "created_at": utc_now(),
        "status": status,
        "audit_type": "implementation_readiness_closure",
        "conclusion": "V9-2 implementation-readiness closure is complete and scoped human approval is recorded; only the limited runtime slice is allowed." if status == "PASS" else "V9-2 implementation-readiness closure failed.",
        "v9_2_runtime_implementation_allowed": True,
        "runtime_executor_route_created": False,
        "runtime_worker_created": False,
        "controlled_executor_action_execution": False,
        "source_agent_durable_mutation_allowed": False,
        "requires_human_high_risk_decision": False,
        "external_audit_deferred": True,
        "fixtures": [_fixture_summary(item) for item in fixtures],
        "checks": checks,
        "evidence_refs": [
            str(V9_1_INTERNAL_AUDIT),
            str(V9_1_SAFETY_GATE),
            str(V9_2_DECISION),
            str(V9_2_PLAN),
            str(V9_2_ENGINEERING),
            str(V9_2_SPEC),
            *(str(FIXTURE_DIR / name) for name in sorted(REQUIRED_FIXTURES)),
        ],
        "next_human_decision_required": {
            "stage_id": "V9-2",
            "decision_needed": "Recorded: V9-2 limited controlled Agent executor runtime implementation is approved.",
            "impact_if_approved": "Allows implementation of the four allowlisted actions only, still denying source=agent durable mutation and excluded actions.",
            "impact_if_rejected": "Not applicable to the current recorded decision; revocation would block V9-2 and downstream V9-3/V9-4 runtime.",
        },
        "remaining_blockers": [
            "V9-2 runtime evidence must prove only the four allowlisted actions.",
            "V9-3 remains blocked until V9-2 runtime evidence exists.",
            "V9-4 remains blocked until V9-2 and V9-3 runtime evidence exists.",
            "V9-8 final acceptance remains blocked.",
        ],
    }


def _read_fixture(path: Path) -> dict[str, Any]:
    data = read_json(path)
    return {"path": path, "data": data}


def _fixture_checks(fixtures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for item in fixtures:
        name = item["path"].name
        data = item["data"]
        checks.append(_check(f"{name}_stage_id", data.get("stage_id") == "V9-2", "Fixture is scoped to V9-2."))
        checks.append(_check(f"{name}_redaction_pass", data.get("redaction_status") == "PASS", "Fixture carries redaction_status=PASS."))
        checks.append(_check(f"{name}_runtime_not_allowed_now", data.get("runtime_execution_allowed_now") is False, "Fixture does not approve current runtime execution."))
        operation = data.get("operation")
        checks.append(_check(f"{name}_operation_in_allowlist", operation in ALLOWLIST, "Fixture operation is in the V9-2 candidate allowlist."))
        if data.get("source") == "agent":
            checks.append(_check(f"{name}_source_agent_denied", data.get("expected_decision") == "deny", "source=agent fixture must be denied."))
        if operation in {"artifact.write", "quality.evaluation.create"}:
            checks.append(_check(f"{name}_approval_gate_required", data.get("approval_gate_required") is True, "Medium-risk write/evaluation fixtures require approval gate."))
            checks.append(_check(f"{name}_append_only_required", data.get("append_only_required") is True, "Write/evaluation fixtures are append-only."))
        if data.get("expected_runtime_status") == "planned_only_not_executed":
            checks.append(_check(f"{name}_requires_human_decision", data.get("requires_human_high_risk_decision") is True, "Planned allow fixtures require human high-risk decision."))
    return checks


def _document_checks() -> list[dict[str, Any]]:
    engineering = V9_2_ENGINEERING.read_text(encoding="utf-8")
    spec = V9_2_SPEC.read_text(encoding="utf-8")
    plan = V9_2_PLAN.read_text(encoding="utf-8")
    combined = "\n".join((engineering, spec, plan))
    return [
        _check("allowlist_documented", all(action in combined for action in ALLOWLIST), "All four candidate actions are documented."),
        _check("excluded_actions_documented", all(action in combined for action in EXCLUDED_ACTIONS), "Excluded actions are documented as hard-denied."),
        _check("durable_mutation_invariant_documented", "user_confirmed=true OR valid human_authorization_ref" in combined, "Durable mutation invariant uses valid human_authorization_ref."),
        _check("source_agent_denial_documented", "source=agent" in combined and "denied" in combined.lower(), "source=agent default durable mutation denial is documented."),
        _check("append_only_documented", "append" in combined.lower() and "overwrite" in combined.lower(), "Append-only and overwrite denial are documented."),
    ]


def _decision_blocks_runtime(decision: dict[str, Any]) -> bool:
    blocked = set(decision.get("blocked_work", []))
    return {
        "runtime_executor_route",
        "runtime_worker",
        "source_agent_durable_mutation",
        "connector_call",
        "external_llm_call",
        "business_event_emit",
        "context_update",
        "workflow_template_publish",
        "approval_respond",
        "git_commit",
        "git_push",
        "production_deploy",
        "v9_3_runtime_implementation",
        "v9_4_runtime_implementation",
        "v9_8_final_acceptance",
    }.issubset(blocked)


def _forbidden_route_or_worker_detected() -> bool:
    paths = list((ROOT / "core").glob("**/*.py"))
    runtime_patterns = (
        r"@.*\.(post|put|patch)\(",
        r"\bAPIRouter\b",
        r"\bFastAPI\b",
        r"\buvicorn\b",
        r"\bsubprocess\b",
        r"\bthreading\b",
        r"\basyncio\.create_task\b",
    )
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "V9-2" not in text and "v9_2" not in str(path):
            continue
        if any(re.search(pattern, text) for pattern in runtime_patterns):
            return True
    return False


def _fixture_summary(item: dict[str, Any]) -> dict[str, Any]:
    data = item["data"]
    return {
        "path": str(item["path"]),
        "fixture_id": data.get("fixture_id"),
        "operation": data.get("operation"),
        "expected_runtime_status": data.get("expected_runtime_status"),
        "expected_decision": data.get("expected_decision"),
        "runtime_execution_allowed_now": data.get("runtime_execution_allowed_now"),
    }


def _check(check_id: str, condition: bool, details: str) -> dict[str, Any]:
    return {"check_id": check_id, "status": "PASS" if condition else "FAIL", "details": details}


def _summary(data: dict[str, Any]) -> str:
    lines = [
        "# V9-2 Pre-Implementation Audit Closure",
        "",
        "Document status: internal readiness closure / limited runtime implementation approved.",
        "",
        "```text",
        f"status: {data['status']}",
        f"v9_2_runtime_implementation_allowed: {str(data['v9_2_runtime_implementation_allowed']).lower()}",
        "runtime_executor_route_created: false",
        "runtime_worker_created: false",
        "controlled_executor_action_execution: limited_to_allowlisted_runtime_slice",
        "source_agent_durable_mutation_allowed: false",
        f"requires_human_high_risk_decision: {str(data['requires_human_high_risk_decision']).lower()}",
        "```",
        "",
        "## Conclusion",
        "",
        data["conclusion"],
        "",
        "## Checks",
        "",
    ]
    for check in data["checks"]:
        lines.append(f"- {check['check_id']}: {check['status']} - {check['details']}")
    lines.extend(["", "## Human Decision Required", ""])
    for key, value in data["next_human_decision_required"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Remaining Blockers", ""])
    for blocker in data["remaining_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "## No False Green Boundary",
            "",
            "This closure does not claim Agent executor ready, controlled executor ready, production controlled executor ready, V9-2 runtime PASS, V9-3 runtime PASS, or V9-4 runtime PASS.",
            "",
        ]
    )
    return "\n".join(lines)


def _html(data: dict[str, Any]) -> str:
    checks = "".join(
        f"<tr><td>{html.escape(item['check_id'])}</td><td class='{html.escape(item['status'].lower())}'>{html.escape(item['status'])}</td><td>{html.escape(item['details'])}</td></tr>"
        for item in data["checks"]
    )
    fixtures = "".join(
        f"<tr><td>{html.escape(item['fixture_id'] or '')}</td><td>{html.escape(item['operation'] or '')}</td><td>{html.escape(item['expected_decision'] or '')}</td><td>{html.escape(str(item['runtime_execution_allowed_now']))}</td></tr>"
        for item in data["fixtures"]
    )
    blockers = "".join(f"<li>{html.escape(item)}</li>" for item in data["remaining_blockers"])
    decision = "".join(f"<li>{html.escape(key)}: {html.escape(str(value))}</li>" for key, value in data["next_human_decision_required"].items())
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>V9-2 Pre-Implementation Audit Closure</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f8fafc; color: #111827; }}
    header {{ background: #111827; color: white; padding: 28px 40px; }}
    main {{ padding: 28px 40px; }}
    .warning {{ border-left: 6px solid #dc2626; background: #fef2f2; padding: 16px 18px; margin: 20px 0; }}
    table {{ border-collapse: collapse; width: 100%; background: white; margin: 16px 0; }}
    th, td {{ border: 1px solid #d1d5db; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    .pass {{ color: #166534; font-weight: 700; }}
    .fail {{ color: #991b1b; font-weight: 700; }}
    li {{ line-height: 1.7; overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <header>
    <h1>V9-2 受控执行器实现前闭环</h1>
    <p>status: {html.escape(data['status'])} / v9_2_runtime_implementation_allowed: {html.escape(str(data['v9_2_runtime_implementation_allowed']))}</p>
  </header>
  <main>
    <section class="warning">
      <strong>高风险边界：</strong>V9-2 limited runtime slice 已获窄授权；本页仍阻断 route、worker、source=agent mutation 和 excluded actions。
    </section>
    <h2>审计检查</h2>
    <table><thead><tr><th>check_id</th><th>status</th><th>details</th></tr></thead><tbody>{checks}</tbody></table>
    <h2>V9-2 夹具</h2>
    <table><thead><tr><th>fixture</th><th>operation</th><th>expected_decision</th><th>runtime_now</th></tr></thead><tbody>{fixtures}</tbody></table>
    <h2>需要人类处理的高风险决策</h2>
    <ul>{decision}</ul>
    <h2>剩余阻断</h2>
    <ul>{blockers}</ul>
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
