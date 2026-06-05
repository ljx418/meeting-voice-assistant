from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from tools.v9.common import V9_ROOT, utc_now


OUT_DIR = V9_ROOT / "evidence" / "v9-1-readiness"
REPORTS = {
    "contract_validation": V9_ROOT / "reports" / "v9_1_contract_validation_report.json",
    "negative_tests": V9_ROOT / "reports" / "v9_1_negative_test_results.json",
    "no_false_green": V9_ROOT / "reports" / "v9_1_no_false_green_scan.json",
    "redaction": V9_ROOT / "reports" / "v9_1_redaction_scan.json",
    "safety_gate_implementation": V9_ROOT / "evidence" / "v9-1-safety-gate-implementation" / "acceptance-data.json",
    "v9_2_pre_implementation": V9_ROOT / "evidence" / "v9-2-controlled-executor-pre-implementation" / "pre-implementation-data.json",
    "v9_2_limited_runtime_slice": V9_ROOT / "evidence" / "v9-2-controlled-executor-runtime" / "acceptance-data.json",
}
DECISIONS = {
    "external_audit_decision": V9_ROOT / "decisions" / "v9_1_external_audit_decision.md",
    "high_risk_human_decision": V9_ROOT / "decisions" / "v9_1_high_risk_human_decision.json",
}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": "v9_1.readiness_dashboard.v1",
        "stage_id": "V9-1",
        "created_at": utc_now(),
        "status": "PASS",
        "runtime_implementation_allowed": False,
        "limited_safety_gate_implementation_complete": True,
        "internal_independent_audit_closed": True,
        "v9_2_pre_implementation_closed": True,
        "v9_2_limited_runtime_slice_complete": True,
        "v9_2_limited_runtime_slice_ready_for_review": True,
        "v9_3_runtime_implementation_allowed": False,
        "v9_4_runtime_implementation_allowed": False,
        "external_audit_deferred": True,
        "allowed_next_work": [
            "V9 front-stage readiness audit",
            "V9-1 external implementation-readiness audit",
            "V9-1 limited safety gate implementation review",
            "V9-2 implementation-readiness closure review",
            "V9-2 limited controlled runtime slice review",
            "readiness validator tooling review",
        ],
        "blocked_work": [
            "V9-1 runtime executor route",
            "V9-1 runtime worker",
            "source=agent durable mutation",
            "V9-3 runtime implementation",
            "V9-4 runtime implementation",
            "V9-8 final acceptance",
        ],
        "reports": {name: _read_report(path) for name, path in REPORTS.items()},
        "decisions": {name: str(path) for name, path in DECISIONS.items()},
        "source_refs": [
            "docs/design/V9.x/v9_front_stage_development_readiness_audit.md",
            "docs/design/V9.x/v9_development_and_acceptance_plan.md",
            "docs/design/V9.x/v9_acceptance_gate_matrix.md",
            "docs/design/V9.x/v9_current_gap_analysis.drawio",
        ],
    }
    if any(report.get("status") != "PASS" for report in data["reports"].values()):
        data["status"] = "FAIL"

    (OUT_DIR / "readiness-dashboard-data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT_DIR / "result-summary.md").write_text(_summary_markdown(data), encoding="utf-8")
    (OUT_DIR / "index.html").write_text(_html(data), encoding="utf-8")
    print(json.dumps({"status": data["status"], "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0 if data["status"] == "PASS" else 1


def _read_report(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "path": str(path),
        "status": data.get("status"),
        "runtime_evidence": data.get("runtime_evidence"),
        "created_at": data.get("created_at"),
    }


def _summary_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# V9-1 Readiness Dashboard Result",
        "",
        "```text",
        f"status: {data['status']}",
        "runtime_implementation_allowed: false",
        "proceed_to_v9_1_external_implementation_readiness_audit: true",
        "proceed_to_v9_1_implementation_planning: true",
        "proceed_to_v9_1_runtime_implementation: false",
        "v9_2_limited_runtime_slice_complete: true",
        "proceed_to_v9_3_runtime_implementation: false",
        "proceed_to_v9_4_runtime_implementation: false",
        "```",
        "",
        "## Reports",
        "",
    ]
    for name, report in data["reports"].items():
        lines.append(f"- {name}: {report['status']} ({report['path']})")
    lines.extend(
        [
            "",
            "## Runtime Boundary",
            "",
        "This package includes V9-1 readiness evidence and V9-2 limited runtime slice evidence. It does not approve runtime executor routes, runtime workers, source=agent durable mutation, multi-Agent orchestration runtime, or autonomous coding workflow runtime.",
            "",
        ]
    )
    return "\n".join(lines)


def _html(data: dict[str, Any]) -> str:
    cards = []
    for name, report in data["reports"].items():
        cards.append(
            f"""
            <section class="card">
              <h2>{html.escape(name)}</h2>
              <p class="status {html.escape(str(report['status']).lower())}">{html.escape(str(report['status']))}</p>
              <p>runtime_evidence: {html.escape(str(report['runtime_evidence']))}</p>
              <p class="path">{html.escape(report['path'])}</p>
            </section>
            """
        )
    blocked = "".join(f"<li>{html.escape(item)}</li>" for item in data["blocked_work"])
    allowed = "".join(f"<li>{html.escape(item)}</li>" for item in data["allowed_next_work"])
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>V9-1 Readiness Dashboard</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f8fafc; color: #111827; }}
    header {{ background: #111827; color: white; padding: 28px 40px; }}
    main {{ padding: 28px 40px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
    .card {{ background: white; border: 1px solid #d1d5db; border-radius: 8px; padding: 18px; }}
    .status {{ display: inline-block; padding: 4px 10px; border-radius: 999px; font-weight: 700; }}
    .pass {{ background: #dcfce7; color: #166534; }}
    .fail {{ background: #fee2e2; color: #991b1b; }}
    .path {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; color: #4b5563; overflow-wrap: anywhere; }}
    .warning {{ border-left: 6px solid #dc2626; background: #fef2f2; padding: 16px 18px; margin: 20px 0; }}
    ul {{ line-height: 1.7; }}
  </style>
</head>
<body>
  <header>
    <h1>V9-1 Readiness Dashboard</h1>
    <p>status: {html.escape(data['status'])} / limited_safety_gate_implementation_complete: true / v9_2_limited_runtime_slice_complete: true / runtime_implementation_allowed: false</p>
  </header>
  <main>
    <section class="warning">
      <strong>边界：</strong>本看板证明 V9-1 readiness tooling 与 V9-2 有限 runtime slice 证据通过，不批准 runtime executor route、runtime worker、V9-3 编排运行时、V9-4 代码工作流运行时或 source=agent durable mutation。
    </section>
    <h2>Reports</h2>
    <div class="grid">{''.join(cards)}</div>
    <h2>Allowed Next Work</h2>
    <ul>{allowed}</ul>
    <h2>Blocked Work</h2>
    <ul>{blocked}</ul>
    <h2>Decision Files</h2>
    <ul>
      <li>{html.escape(data['decisions']['external_audit_decision'])}</li>
      <li>{html.escape(data['decisions']['high_risk_human_decision'])}</li>
    </ul>
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
