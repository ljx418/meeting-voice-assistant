from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

from tools.v9.common import ROOT, V9_ROOT, read_json, utc_now, write_json


OUT_DIR = V9_ROOT / "evidence" / "v9-1-internal-independent-audit"
SUMMARY_PATH = V9_ROOT / "v9_1_internal_independent_audit_closure.md"
SAFETY_MODULE = ROOT / "core" / "policies" / "v9_agent_executor_safety.py"
ACCEPTANCE_PATH = V9_ROOT / "evidence" / "v9-1-safety-gate-implementation" / "acceptance-data.json"
READINESS_PATH = V9_ROOT / "evidence" / "v9-1-readiness" / "readiness-dashboard-data.json"
DECISION_PATH = V9_ROOT / "decisions" / "v9_1_high_risk_human_decision.json"

REPORT_PATHS = {
    "contract_validation": V9_ROOT / "reports" / "v9_1_contract_validation_report.json",
    "negative_tests": V9_ROOT / "reports" / "v9_1_negative_test_results.json",
    "no_false_green": V9_ROOT / "reports" / "v9_1_no_false_green_scan.json",
    "redaction": V9_ROOT / "reports" / "v9_1_redaction_scan.json",
}

BLOCKED_WORK_REQUIRED = {
    "runtime_executor_route",
    "runtime_worker",
    "source_agent_durable_mutation",
    "controlled_executor_action_execution",
    "multi_agent_orchestration_runtime",
    "autonomous_coding_workflow_runtime",
    "v9_8_final_acceptance",
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = _build_audit()
    write_json(OUT_DIR / "internal-audit-data.json", data)
    (OUT_DIR / "index.html").write_text(_html(data), encoding="utf-8")
    (OUT_DIR / "result-summary.md").write_text(_summary(data), encoding="utf-8")
    SUMMARY_PATH.write_text(_summary(data), encoding="utf-8")
    print(json.dumps({"status": data["status"], "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0 if data["status"] == "PASS" else 1


def _build_audit() -> dict[str, Any]:
    acceptance = read_json(ACCEPTANCE_PATH)
    readiness = read_json(READINESS_PATH)
    decision = read_json(DECISION_PATH)
    reports = {name: read_json(path) for name, path in REPORT_PATHS.items()}
    checks = [
        _check("safety_gate_acceptance_pass", acceptance.get("status") == "PASS", "V9-1 Safety Gate implementation evidence status is PASS."),
        _check("all_scenarios_pass", all(item.get("status") == "PASS" for item in acceptance.get("scenarios", [])), "All real-code policy validation scenarios pass."),
        _check("runtime_execution_still_blocked", acceptance.get("runtime_execution_allowed") is False, "Safety Gate never allows runtime execution."),
        _check("runtime_route_not_created", acceptance.get("runtime_executor_route_created") is False, "No runtime executor route was created."),
        _check("runtime_worker_not_created", acceptance.get("runtime_worker_created") is False, "No runtime worker was created."),
        _check("source_agent_mutation_denied", acceptance.get("source_agent_durable_mutation_allowed") is False, "source=agent durable mutation remains denied."),
        _check("controlled_action_execution_blocked", acceptance.get("controlled_executor_action_execution") is False, "Controlled executor action execution remains out of scope."),
        _check("capability_claim_flags_false", _all_claim_flags_false(acceptance), "Blocked capability claim flags remain false."),
        _check("readiness_status_pass", readiness.get("status") == "PASS", "Readiness dashboard status is PASS."),
        _check("readiness_runtime_implementation_blocked", readiness.get("runtime_implementation_allowed") is False, "Readiness dashboard keeps runtime implementation blocked."),
        _check("readiness_v9_2_limited_runtime_slice_complete", readiness.get("v9_2_limited_runtime_slice_complete") is True, "Readiness dashboard includes V9-2 limited runtime slice evidence."),
        _check("human_decision_limited_scope", decision.get("decision") == "GO_FOR_IMPLEMENTATION" and "Safety Gate implementation only" in decision.get("scope", ""), "Human decision approves only limited V9-1 Safety Gate implementation."),
        _check("human_decision_blocks_runtime_work", BLOCKED_WORK_REQUIRED.issubset(set(decision.get("blocked_work", []))), "Human decision explicitly blocks runtime work."),
        _check("reports_pass", all(report.get("status") == "PASS" for report in reports.values()), "Contract, negative fixture, No False Green and redaction reports pass."),
        _check("safety_module_has_no_route_or_worker_constructs", not _safety_module_has_runtime_constructs(), "Safety module has no route, server, subprocess, worker, or runtime dispatch constructs."),
        _check("no_false_green_violations_zero", reports["no_false_green"].get("violations") == [], "No False Green scan has zero violations."),
        _check("redaction_violations_zero", reports["redaction"].get("violations") == [], "Redaction scan has zero violations."),
    ]
    status = "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL"
    return {
        "schema_version": "v9_1.internal_independent_audit.v1",
        "stage_id": "V9-1",
        "created_at": utc_now(),
        "status": status,
        "audit_type": "internal_independent_closure",
        "conclusion": "V9-1 limited Safety Gate implementation remains internally closed; V9-2 limited runtime slice evidence is now tracked separately and external audit is deferred until later V9 development packages are available." if status == "PASS" else "V9-1 internal audit failed; do not proceed.",
        "runtime_implementation_allowed": False,
        "v9_2_limited_runtime_slice_complete": True,
        "v9_2_runtime_implementation_allowed": True,
        "v9_3_runtime_implementation_allowed": False,
        "v9_4_runtime_implementation_allowed": False,
        "external_audit_deferred": True,
        "checks": checks,
        "evidence_refs": [
            str(ACCEPTANCE_PATH),
            str(READINESS_PATH),
            str(DECISION_PATH),
            *(str(path) for path in REPORT_PATHS.values()),
            str(SAFETY_MODULE),
        ],
        "remaining_blockers": [
            "V9-3 orchestration runtime remains blocked until V9-2 runtime evidence exists.",
            "V9-4 autonomous coding workflow remains blocked until V9-2/V9-3 evidence exists.",
            "V9-8 final acceptance remains blocked until V9-0 through V9-7 evidence packages exist.",
        ],
    }


def _check(check_id: str, condition: bool, details: str) -> dict[str, Any]:
    return {"check_id": check_id, "status": "PASS" if condition else "FAIL", "details": details}


def _all_claim_flags_false(data: dict[str, Any]) -> bool:
    flags = data.get("blocked_capability_claim_flags", {})
    return bool(flags) and all(value is False for value in flags.values())


def _safety_module_has_runtime_constructs() -> bool:
    text = SAFETY_MODULE.read_text(encoding="utf-8", errors="ignore")
    patterns = (
        r"\bAPIRouter\b",
        r"\bFastAPI\b",
        r"@\w+\.(get|post|put|delete|patch)\b",
        r"\buvicorn\b",
        r"\bsubprocess\b",
        r"\bthreading\b",
        r"\basyncio\.create_task\b",
        r"\brequests\.",
        r"\bhttpx\.",
        r"\bWorkflowStore\b",
        r"\bStationRun\b",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def _summary(data: dict[str, Any]) -> str:
    lines = [
        "# V9-1 Internal Independent Audit Closure",
        "",
        "Document status: internal audit closure / V9-1 only / external audit deferred.",
        "",
        "```text",
        f"status: {data['status']}",
        "runtime_implementation_allowed: false",
        "v9_2_limited_runtime_slice_complete: true",
        "v9_2_runtime_implementation_allowed: true",
        "v9_3_runtime_implementation_allowed: false",
        "v9_4_runtime_implementation_allowed: false",
        "external_audit_deferred: true",
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
    lines.extend(["", "## Remaining Blockers", ""])
    for blocker in data["remaining_blockers"]:
        lines.append(f"- {blocker}")
    lines.extend(
        [
            "",
            "## No False Green Boundary",
            "",
            "This closure does not claim Agent executor ready, controlled executor ready, production controlled executor ready, full multi-Agent orchestration ready, autonomous coding workflow ready, complete Workflow Studio ready, or production ready.",
            "",
        ]
    )
    return "\n".join(lines)


def _html(data: dict[str, Any]) -> str:
    checks = "".join(
        f"<tr><td>{html.escape(item['check_id'])}</td><td class='{html.escape(item['status'].lower())}'>{html.escape(item['status'])}</td><td>{html.escape(item['details'])}</td></tr>"
        for item in data["checks"]
    )
    blockers = "".join(f"<li>{html.escape(item)}</li>" for item in data["remaining_blockers"])
    refs = "".join(f"<li>{html.escape(ref)}</li>" for ref in data["evidence_refs"])
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>V9-1 Internal Independent Audit Closure</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f8fafc; color: #111827; }}
    header {{ background: #111827; color: white; padding: 28px 40px; }}
    main {{ padding: 28px 40px; }}
    .notice {{ border-left: 6px solid #2563eb; background: #eff6ff; padding: 16px 18px; margin: 20px 0; }}
    table {{ border-collapse: collapse; width: 100%; background: white; }}
    th, td {{ border: 1px solid #d1d5db; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f3f4f6; }}
    .pass {{ color: #166534; font-weight: 700; }}
    .fail {{ color: #991b1b; font-weight: 700; }}
    li {{ line-height: 1.7; overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <header>
    <h1>V9-1 内部独立审计闭环</h1>
    <p>status: {html.escape(data['status'])} / runtime_implementation_allowed: false / external_audit_deferred: true</p>
  </header>
  <main>
    <section class="notice">
      <strong>结论：</strong>{html.escape(data['conclusion'])}
    </section>
    <h2>审计检查</h2>
    <table>
      <thead><tr><th>check_id</th><th>status</th><th>details</th></tr></thead>
      <tbody>{checks}</tbody>
    </table>
    <h2>剩余阻断项</h2>
    <ul>{blockers}</ul>
    <h2>证据引用</h2>
    <ul>{refs}</ul>
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
