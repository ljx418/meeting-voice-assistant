from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


OUTPUT_DIR = REPO_ROOT / "docs" / "design" / "V5.x" / "evidence" / "v5-8e-final-acceptance"
FORBIDDEN_CLAIMS = [
    "distributed multi-Agent runtime ready",
    "full multi-Agent orchestration ready",
    "Agent executor ready",
    "production controlled executor ready",
    "production-ready external app support",
    "complete Workflow Studio ready",
    "autonomous workflow editing ready",
]
SAFE_CONTEXT = (
    "Forbidden",
    "No False Green",
    "forbidden",
    "禁止",
    "不得",
    "不能",
    "does not prove",
    "not ",
    "not_",
    "Stop",
    "Do not claim",
)


def build_acceptance() -> dict[str, Any]:
    stage_refs = [
        _read_status("V5-8A", "docs/design/V5.x/evidence/v5-8a-planning-gate/real-data-readiness.json", "status"),
        _read_status("V5-8B", "docs/design/V5.x/evidence/v5-8b-distributed-coordination/coordination-evidence.json", "status"),
        _read_status("V5-8C", "docs/design/V5.x/evidence/v5-8c-lineage-recovery/lineage-recovery-evidence.json", "status"),
        _read_status("V5-8D", "docs/design/V5.x/evidence/v5-8d-policy-observability/policy-observability-evidence.json", "status"),
    ]
    scenario_refs = [
        _read_summary_status("UX-08", "docs/design/V4.x/evidence/real-multi-agent/UX-08-serial-video/result-summary.md"),
        _read_summary_status("UX-09", "docs/design/V4.x/evidence/real-multi-agent/UX-09-parallel-deliberation/result-summary.md"),
        _read_summary_status("UX-10", "docs/design/V4.x/evidence/real-multi-agent/UX-10-engineering-workflow/result-summary.md"),
    ]
    claim_violations = _scan_claims()
    status = "PASS" if all(item["status"] == "PASS" for item in stage_refs + scenario_refs) and not claim_violations else "FAIL"
    return {
        "schema_version": "v5_8e.final_acceptance.v1",
        "stage": "V5-8E Distributed Runtime Acceptance Package",
        "status": status,
        "allowed_claim": "V5-8 complete: distributed multi-Agent runtime slice ready for review.",
        "stage_refs": stage_refs,
        "scenario_refs": scenario_refs,
        "claim_violations": claim_violations,
        "distributed_runtime_slice_ready_for_review": status == "PASS",
        "full_multi_agent_orchestration_ready": False,
        "agent_executor_ready": False,
        "production_controlled_executor_ready": False,
        "production_ready_external_app_support": False,
        "complete_workflow_studio_ready": False,
        "source_agent_can_mutate": False,
        "production_routes_added": False,
        "production_workers_started": False,
        "evidence_scope": "provider_backed_devlocal_scenario_evidence_plus_in_memory_distributed_runtime_slice",
        "redaction_status": "redacted",
    }


def write_acceptance(data: dict[str, Any], output_dir: Path = OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "final-acceptance-data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(render_summary(data), encoding="utf-8")
    (output_dir / "claims-scan.md").write_text(render_claims_scan(data), encoding="utf-8")
    (output_dir / "index.html").write_text(render_html(data), encoding="utf-8")


def render_summary(data: dict[str, Any]) -> str:
    lines = [
        "# V5-8E Final Acceptance Summary",
        "",
        f"status: {data['status']}",
        f"stage: {data['stage']}",
        f"allowed_claim: {data['allowed_claim']}",
        f"evidence_scope: {data['evidence_scope']}",
        f"distributed_runtime_slice_ready_for_review: {str(data['distributed_runtime_slice_ready_for_review']).lower()}",
        f"full_multi_agent_orchestration_ready: {str(data['full_multi_agent_orchestration_ready']).lower()}",
        f"agent_executor_ready: {str(data['agent_executor_ready']).lower()}",
        f"production_controlled_executor_ready: {str(data['production_controlled_executor_ready']).lower()}",
        f"source_agent_can_mutate: {str(data['source_agent_can_mutate']).lower()}",
        "stage_results:",
    ]
    lines.extend(f"- {item['id']}: {item['status']} {item['ref']}" for item in data["stage_refs"])
    lines.append("scenario_results:")
    lines.extend(f"- {item['id']}: {item['status']} {item['ref']}" for item in data["scenario_refs"])
    lines.extend(
        [
            "claim_violations:",
            "- none" if not data["claim_violations"] else "\n".join(f"- {violation}" for violation in data["claim_violations"]),
            "",
            "No False Green: V5-8 proves only a bounded distributed runtime slice ready for review. It does not prove full multi-Agent orchestration ready, Agent executor ready, production controlled executor ready, production-ready external app support, or complete Workflow Studio ready.",
            "",
        ]
    )
    return "\n".join(lines)


def render_claims_scan(data: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# V5-8E Claim Scan",
            "",
            f"status: {'PASS' if not data['claim_violations'] else 'FAIL'}",
            "violations:",
            "- none" if not data["claim_violations"] else "\n".join(f"- {violation}" for violation in data["claim_violations"]),
            "",
        ]
    )


def render_html(data: dict[str, Any]) -> str:
    stage_rows = "".join(f"<tr><td>{html.escape(item['id'])}</td><td>{html.escape(item['status'])}</td><td>{html.escape(item['ref'])}</td></tr>" for item in data["stage_refs"])
    scenario_rows = "".join(f"<tr><td>{html.escape(item['id'])}</td><td>{html.escape(item['status'])}</td><td>{html.escape(item['ref'])}</td></tr>" for item in data["scenario_refs"])
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V5-8E Final Acceptance</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #0f172a; background: #f8fafc; }}
    .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin-bottom: 18px; }}
    .pass {{ color: #15803d; font-weight: 700; }}
    .warn {{ color: #b45309; font-weight: 700; }}
    table {{ border-collapse: collapse; width: 100%; background: white; margin-top: 10px; }}
    th, td {{ border: 1px solid #e2e8f0; padding: 10px; text-align: left; }}
    th {{ background: #f1f5f9; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>V5-8E 最终验收包</h1>
    <p>Status: <span class="pass">{html.escape(data["status"])}</span></p>
    <p>Allowed claim: {html.escape(data["allowed_claim"])}</p>
    <p class="warn">No False Green: 本验收不证明 full multi-Agent orchestration ready、Agent executor ready 或 production controlled executor ready。</p>
  </div>
  <div class="card">
    <h2>V5-8 Stage Evidence</h2>
    <table><thead><tr><th>Stage</th><th>Status</th><th>Evidence</th></tr></thead><tbody>{stage_rows}</tbody></table>
  </div>
  <div class="card">
    <h2>Real Provider-backed Scenario Evidence</h2>
    <table><thead><tr><th>UX</th><th>Status</th><th>Evidence</th></tr></thead><tbody>{scenario_rows}</tbody></table>
  </div>
  <div class="card">
    <h2>Boundary</h2>
    <ul>
      <li>source_agent_can_mutate=false</li>
      <li>production_routes_added=false</li>
      <li>production_workers_started=false</li>
      <li>full_multi_agent_orchestration_ready=false</li>
      <li>production_controlled_executor_ready=false</li>
    </ul>
  </div>
  <div class="card">
    <h2>Raw Data</h2>
    <p><a href="final-acceptance-data.json">final-acceptance-data.json</a></p>
    <p><a href="result-summary.md">result-summary.md</a></p>
    <p><a href="claims-scan.md">claims-scan.md</a></p>
  </div>
</body>
</html>
"""


def _read_status(stage_id: str, ref: str, status_key: str) -> dict[str, str]:
    path = REPO_ROOT / ref
    data = json.loads(path.read_text(encoding="utf-8"))
    return {"id": stage_id, "status": data.get(status_key, "MISSING"), "ref": ref}


def _read_summary_status(stage_id: str, ref: str) -> dict[str, str]:
    text = (REPO_ROOT / ref).read_text(encoding="utf-8")
    status = "PASS" if "\nstatus: PASS" in text else "FAIL"
    return {"id": stage_id, "status": status, "ref": ref}


def _scan_claims() -> list[str]:
    docs = [
        REPO_ROOT / "docs" / "design" / "V5.x" / "00_README.md",
        REPO_ROOT / "docs" / "design" / "V5.x" / "v5_current_gap_analysis.md",
        REPO_ROOT / "docs" / "design" / "V5.x" / "v5_development_and_acceptance_plan.md",
        REPO_ROOT / "docs" / "design" / "V5.x" / "v5_8_entry_gate_plan.md",
        REPO_ROOT / "docs" / "design" / "V5.x" / "v5_8_pre_implementation_audit.md",
    ]
    violations: list[str] = []
    for doc in docs:
        lines = doc.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, start=1):
            context = "\n".join(lines[max(0, line_no - 18) : min(len(lines), line_no + 2)])
            for claim in FORBIDDEN_CLAIMS:
                if claim in line and not any(marker in context for marker in SAFE_CONTEXT):
                    violations.append(f"{doc.relative_to(REPO_ROOT)}:{line_no}:{claim}")
    return violations


def main() -> int:
    data = build_acceptance()
    write_acceptance(data)
    print(json.dumps({"status": data["status"], "output_dir": str(OUTPUT_DIR.relative_to(REPO_ROOT))}, ensure_ascii=False, indent=2))
    return 0 if data["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
