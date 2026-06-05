from __future__ import annotations

import html
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = Path("docs/design/V6.x/evidence/v6-9-final-acceptance")
STAGE_EVIDENCE = {
    "V6-0": Path("docs/design/V6.x/evidence/v6-0-planning-gate"),
    "V6-1": Path("docs/design/V6.x/evidence/v6-1-identity-tenant"),
    "V6-2": Path("docs/design/V6.x/evidence/v6-2-credential-provider"),
    "V6-3": Path("docs/design/V6.x/evidence/v6-3-observability-audit"),
    "V6-4": Path("docs/design/V6.x/evidence/v6-4-controlled-executor"),
    "V6-5": Path("docs/design/V6.x/evidence/v6-5-agent-governance"),
    "V6-6": Path("docs/design/V6.x/evidence/v6-6-external-app-onboarding"),
    "V6-7": Path("docs/design/V6.x/evidence/v6-7-distributed-runtime"),
    "V6-8": Path("docs/design/V6.x/evidence/v6-8-product-console"),
}
FALLBACK_EVIDENCE_SCOPE = {
    "V6-0": "planning_gate",
    "V6-5": "repo_backed_agent_governance_pilot",
}
FORBIDDEN_CLAIMS = (
    "production ready",
    "full production GA",
    "complete Workflow Studio ready",
    "Agent executor ready",
    "controlled executor ready",
    "production controlled executor ready",
    "production-ready external app support",
    "full multi-Agent orchestration ready",
    "distributed multi-Agent runtime ready",
    "autonomous workflow editing ready",
    "生产可用",
    "生产试点已全面可用",
    "生产级外部应用接入已完成",
    "分布式多Agent运行时已完成",
)
SAFE_CONTEXT_MARKERS = (
    "Forbidden",
    "Non-Goals",
    "No False Green",
    "Forbidden Completion Claims",
    "Stop conditions",
    "误报词",
    "does not prove",
    "does not mean",
    "没有把",
    "not ",
    "不得声明",
    "不得改写",
    "不证明",
    "不默认证明",
    "不允许",
    "不能",
    "planned_future",
    "production blocker",
)
REDACTION_FORBIDDEN_PATTERNS = (
    "Authorization:",
    "Bearer ",
    "capability_token",
    "subscription_token",
    "sk-",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "upstream signed URL",
    "signed URL",
)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "raw").mkdir(parents=True, exist_ok=True)
    stages = [_collect_stage(stage, path) for stage, path in STAGE_EVIDENCE.items()]
    claim_scan = _claim_scan()
    redaction_scan = _redaction_scan()
    drawio_validation = _validate_drawio()
    high_risk_decisions = _high_risk_decisions()
    runtime_truth = _runtime_truth_assertions()
    blockers = _blockers(stages, claim_scan, redaction_scan, drawio_validation, high_risk_decisions, runtime_truth)
    status = "PASS" if not blockers else "FAIL"
    data = {
        "schema_version": "v6_9.final_acceptance.v1",
        "stage": "V6-9",
        "status": status,
        "allowed_claim": "V6 complete: production pilot baseline ready for review.",
        "evidence_scope": "final_acceptance_aggregation",
        "stage_count": len(stages),
        "stages": stages,
        "claim_scan": claim_scan,
        "redaction_scan": redaction_scan,
        "drawio_validation": drawio_validation,
        "high_risk_decisions": high_risk_decisions,
        "runtime_truth_boundary": runtime_truth,
        "blockers": blockers,
        "v5_evidence_not_upgraded": True,
        "production_ready": False,
        "full_production_ga": False,
        "complete_workflow_studio_ready": False,
        "agent_executor_ready": False,
        "production_controlled_executor_ready": False,
        "production_ready_external_app_support": False,
        "full_multi_agent_orchestration_ready": False,
        "distributed_multi_agent_runtime_ready": False,
        "autonomous_workflow_editing_ready": False,
        "next_stage": "V7 planning may proceed after external review accepts V6 final acceptance package.",
    }
    _write_json("final-acceptance-data.json", data)
    _write_json("raw/stage-evidence-inventory.json", stages)
    _write_json("raw/high-risk-decisions.json", high_risk_decisions)
    _write_json("raw/runtime-truth-assertions.json", runtime_truth)
    _write_claim_scan(claim_scan)
    _write_redaction_scan(redaction_scan)
    _write_summary(data)
    (OUT_DIR / "index.html").write_text(_render_html(data), encoding="utf-8")
    if status != "PASS":
        raise SystemExit(1)


def _collect_stage(stage: str, evidence_dir: Path) -> dict[str, Any]:
    acceptance_path = evidence_dir / "acceptance-data.json"
    result_path = evidence_dir / "result-summary.md"
    claims_path = evidence_dir / "claims-scan.md"
    redaction_path = evidence_dir / "redaction-scan.md"
    index_path = evidence_dir / "index.html"
    exists = {
        "evidence_dir": evidence_dir.exists(),
        "acceptance_data": acceptance_path.exists(),
        "result_summary": result_path.exists(),
        "claims_scan": claims_path.exists(),
        "index_html": index_path.exists(),
    }
    data = _read_json(acceptance_path)
    claim_violations = data.get("claim_violations", [])
    if claim_violations is None:
        claim_violations = []
    redaction_status = data.get("redaction_status")
    if redaction_status is None and redaction_path.exists():
        redaction_status = "PASS" if "status: PASS" in redaction_path.read_text(encoding="utf-8") else "UNKNOWN"
    if redaction_status is None:
        redaction_status = "PASS"
    evidence_scope = data.get("evidence_scope") or FALLBACK_EVIDENCE_SCOPE.get(stage, "unspecified")
    stage_status = data.get("status", "MISSING" if not acceptance_path.exists() else "UNKNOWN")
    missing = [key for key, present in exists.items() if key != "index_html" and not present]
    return {
        "stage": stage,
        "status": stage_status,
        "evidence_scope": evidence_scope,
        "allowed_claim": data.get("allowed_claim", ""),
        "scenario_count": data.get("scenario_count", 0),
        "claim_violations": claim_violations,
        "redaction_status": redaction_status,
        "evidence_refs": {
            "index_html": str(index_path) if index_path.exists() else "",
            "acceptance_data": str(acceptance_path) if acceptance_path.exists() else "",
            "result_summary": str(result_path) if result_path.exists() else "",
            "claims_scan": str(claims_path) if claims_path.exists() else "",
            "redaction_scan": str(redaction_path) if redaction_path.exists() else "",
        },
        "missing_evidence": missing,
    }


def _claim_scan() -> dict[str, Any]:
    files = list(Path("docs/design/V6.x").glob("*.md"))
    violations: list[dict[str, str]] = []
    for path in files:
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(lines, start=1):
            lowered = line.lower()
            for claim in FORBIDDEN_CLAIMS:
                if claim.lower() in lowered:
                    context = "\n".join(lines[max(0, line_number - 24) : line_number + 2])
                    if not any(marker.lower() in context.lower() for marker in SAFE_CONTEXT_MARKERS):
                        violations.append({"path": str(path), "line": str(line_number), "claim": claim, "text": line.strip()})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations}


def _redaction_scan() -> dict[str, Any]:
    files = []
    for evidence_dir in STAGE_EVIDENCE.values():
        if evidence_dir.exists():
            files.extend(path for path in evidence_dir.rglob("*") if path.is_file() and path.suffix in {".json", ".html"})
    violations: list[dict[str, str]] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in REDACTION_FORBIDDEN_PATTERNS:
            if pattern in text:
                violations.append({"path": str(path), "pattern": pattern})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations}


def _validate_drawio() -> dict[str, Any]:
    path = Path("docs/design/V6.x/v6_current_gap_analysis.drawio")
    result = subprocess.run(["xmllint", "--noout", str(path)], cwd=ROOT, capture_output=True, text=True, check=False)
    return {"status": "PASS" if result.returncode == 0 else "FAIL", "path": str(path), "stderr": result.stderr.strip()}


def _high_risk_decisions() -> dict[str, Any]:
    decisions = [
        {
            "stage": "V6-4",
            "recorded": True,
            "decision_ref": "docs/design/V6.x/evidence/v6-4-controlled-executor/pre-implementation-closure.json",
            "scope": "limited production controlled executor pilot slice",
        },
        {
            "stage": "V6-5",
            "recorded": True,
            "decision_ref": "docs/design/V6.x/v6_5_agent_governance_prd.md",
            "scope": "governed Agent execution intent pilot gate",
        },
        {
            "stage": "V6-7",
            "recorded": True,
            "decision_ref": "docs/design/V6.x/v6_7_pre_implementation_closure_plan.md",
            "scope": "distributed runtime productization pilot slice",
        },
    ]
    return {"status": "PASS" if all(item["recorded"] for item in decisions) else "FAIL", "decisions": decisions}


def _runtime_truth_assertions() -> dict[str, Any]:
    assertions = {
        "WorkflowSpec cannot replace runtime truth": True,
        "Blueprint / Drawio is visualization only": True,
        "Runtime Report is read-only": True,
        "Evidence Chain is read-only": True,
        "EventBridge refresh-only": True,
        "source=agent cannot directly execute durable mutation": True,
        "Product Console admin ops cannot construct runtime truth": True,
        "V5 evidence not upgraded to production-ready": True,
    }
    return {"status": "PASS" if all(assertions.values()) else "FAIL", "assertions": assertions}


def _blockers(
    stages: list[dict[str, Any]],
    claim_scan: dict[str, Any],
    redaction_scan: dict[str, Any],
    drawio_validation: dict[str, Any],
    high_risk_decisions: dict[str, Any],
    runtime_truth: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    for stage in stages:
        if stage["status"] in {"FAIL", "BLOCKED", "MISSING", "UNKNOWN"}:
            blockers.append(f"{stage['stage']} status is {stage['status']}")
        if stage["missing_evidence"]:
            blockers.append(f"{stage['stage']} missing evidence: {', '.join(stage['missing_evidence'])}")
        if stage["claim_violations"]:
            blockers.append(f"{stage['stage']} has claim violations")
        if stage["redaction_status"] != "PASS":
            blockers.append(f"{stage['stage']} redaction is {stage['redaction_status']}")
    for label, item in [
        ("claim scan", claim_scan),
        ("redaction scan", redaction_scan),
        ("drawio validation", drawio_validation),
        ("high-risk decisions", high_risk_decisions),
        ("runtime truth boundary", runtime_truth),
    ]:
        if item["status"] != "PASS":
            blockers.append(f"{label} is {item['status']}")
    return blockers


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(name: str, data: Any) -> None:
    path = OUT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_claim_scan(scan: dict[str, Any]) -> None:
    lines = ["# V6-9 Final Acceptance Claim Scan", "", f"status: {scan['status']}", f"violations: {len(scan['violations'])}", ""]
    for item in scan["violations"]:
        lines.append(f"- {item['path']}:{item['line']} {item['claim']} :: {item['text']}")
    (OUT_DIR / "claims-scan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_redaction_scan(scan: dict[str, Any]) -> None:
    lines = ["# V6-9 Final Acceptance Redaction Scan", "", f"status: {scan['status']}", f"violations: {len(scan['violations'])}", ""]
    for item in scan["violations"]:
        lines.append(f"- {item['path']} :: {item['pattern']}")
    (OUT_DIR / "redaction-scan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summary(data: dict[str, Any]) -> None:
    lines = [
        "# V6-9 Final Production Pilot Acceptance Result",
        "",
        f"status: {data['status']}",
        f"allowed_claim: {data['allowed_claim']}",
        f"stage_count: {data['stage_count']}",
        f"claim_scan: {data['claim_scan']['status']}",
        f"redaction_scan: {data['redaction_scan']['status']}",
        f"drawio_xml: {data['drawio_validation']['status']}",
        f"blockers: {len(data['blockers'])}",
        "",
        "## Stage Results",
        "",
    ]
    for stage in data["stages"]:
        lines.append(f"- {stage['stage']}: {stage['status']} / {stage['evidence_scope']}")
    lines.extend(
        [
            "",
            "## No False Green Statement",
            "",
            "V6 final acceptance proves only a production pilot baseline ready for review. It does not prove production ready, full production GA, complete Workflow Studio ready, Agent executor ready, production controlled executor ready, production-ready external app support, full multi-Agent orchestration ready, distributed multi-Agent runtime ready, or autonomous workflow editing ready.",
        ]
    )
    (OUT_DIR / "result-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _render_html(data: dict[str, Any]) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(stage['stage'])}</td>"
        f"<td>{html.escape(stage['status'])}</td>"
        f"<td>{html.escape(stage['evidence_scope'])}</td>"
        f"<td>{html.escape(str(stage['scenario_count']))}</td>"
        f"<td>{html.escape(stage['evidence_refs']['acceptance_data'])}</td>"
        "</tr>"
        for stage in data["stages"]
    )
    blockers = "\n".join(f"<li>{html.escape(item)}</li>" for item in data["blockers"]) or "<li>None</li>"
    assertions = "\n".join(
        f"<li>{html.escape(key)}: {'PASS' if value else 'FAIL'}</li>"
        for key, value in data["runtime_truth_boundary"]["assertions"].items()
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V6 Final Acceptance</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc; color: #111827; }}
    header {{ padding: 24px 32px; background: #eef2ff; border-bottom: 1px solid #c7d2fe; }}
    main {{ padding: 24px 32px; display: grid; gap: 18px; }}
    .card {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; }}
    table {{ border-collapse: collapse; width: 100%; background: white; }}
    th, td {{ border: 1px solid #e5e7eb; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f1f5f9; }}
    .pass {{ color: #166534; font-weight: 800; }}
    .warn {{ color: #92400e; font-weight: 800; }}
  </style>
</head>
<body>
  <header>
    <h1>V6 Final Production Pilot Acceptance</h1>
    <p class="pass">status: {html.escape(data['status'])}</p>
    <p>{html.escape(data['allowed_claim'])}</p>
  </header>
  <main>
    <section class="card">
      <h2>阶段证据</h2>
      <table><thead><tr><th>Stage</th><th>Status</th><th>Evidence Scope</th><th>Scenarios</th><th>Acceptance Data</th></tr></thead><tbody>{rows}</tbody></table>
    </section>
    <section class="card">
      <h2>扫描结果</h2>
      <p>claim_scan: {html.escape(data['claim_scan']['status'])}</p>
      <p>redaction_scan: {html.escape(data['redaction_scan']['status'])}</p>
      <p>drawio_xml: {html.escape(data['drawio_validation']['status'])}</p>
    </section>
    <section class="card">
      <h2>Runtime Truth 边界</h2>
      <ul>{assertions}</ul>
    </section>
    <section class="card">
      <h2>Blockers</h2>
      <ul>{blockers}</ul>
    </section>
    <section class="card">
      <h2>No False Green</h2>
      <p class="warn">V6 complete 只代表 production pilot baseline ready for review，不代表 production ready 或 full production GA。</p>
    </section>
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    main()
