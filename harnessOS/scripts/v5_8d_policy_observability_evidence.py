from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.policies.production_controlled_executor_runtime import ExecutionScope
from core.workflows.v5_8_distributed_runtime import (
    AgentWorkerRegistry,
    ArtifactLineageService,
    AttemptHistoryStore,
    DistributedRunCoordinator,
    DistributedRunRequest,
    build_distributed_observability_package,
    build_policy_credential_decision,
    build_runtime_report_projection,
    read_v4_multi_agent_evidence_summary,
    seed_workers_for_stations,
)
from tests.v5_3_observability_support import make_context
from tests.v5_7b_runtime_support import make_human_authorization


OUTPUT_DIR = REPO_ROOT / "docs" / "design" / "V5.x" / "evidence" / "v5-8d-policy-observability"


def build_evidence() -> dict[str, Any]:
    context = make_context()
    summary = read_v4_multi_agent_evidence_summary("UX-09-parallel-deliberation")
    station_ids = summary["station_ids"][:4]
    registry = AgentWorkerRegistry()
    seed_workers_for_stations(context, registry, station_ids)
    coordinator = DistributedRunCoordinator(registry=registry)
    request = DistributedRunRequest(
        workflow_instance_id=summary["workflow_instance_id"],
        source="product_console",
        actor_type=context.actor_type,
        target_scope=ExecutionScope.from_context(context),
        user_confirmed=True,
        human_authorization=make_human_authorization(context, operations=("workflow.instance.start",)),
        station_ids=station_ids,
        evidence_source_refs=(summary["result_path"], summary["summary_path"]),
        idempotency_key="v5-8d-policy-start",
        correlation_id=context.correlation_id,
        request_id=context.request_id,
    )
    started = coordinator.start_run(context, request)
    state = coordinator.store.load(started.distributed_run_id or "")
    attempts = AttemptHistoryStore()
    lineage = ArtifactLineageService()
    attempts.ingest_state(state)
    lineage.ingest_state(state)
    report = build_runtime_report_projection(state, attempts, lineage)
    decision = build_policy_credential_decision(state, registry)
    package = build_distributed_observability_package(state, report, decision)
    status = "PASS" if package["readonly"] is True and package["policy_credential_decision"]["worker_credential_refs"] else "FAIL"
    return {
        "schema_version": "v5_8d.policy_observability_evidence.v1",
        "stage": "V5-8D Policy Credential Observability Slice",
        "status": status,
        "evidence_scope": "real_provider_backed_source_evidence_plus_in_memory_policy_observability_projection",
        "source_evidence": {
            "scenario": summary["scenario"],
            "provider": summary["provider"],
            "model_ref": summary["model_ref"],
            "provider_invocation_count": summary["provider_invocation_count"],
            "real_provider_backed": summary["real_provider_backed"],
            "result_path": summary["result_path"],
            "summary_path": summary["summary_path"],
        },
        "policy_credential_decision": decision.to_dict(),
        "observability_package": package,
        "distributed_runtime_complete": False,
        "production_ready": False,
        "source_agent_can_mutate": False,
        "redaction_status": "redacted",
    }


def write_evidence(evidence: dict[str, Any], output_dir: Path = OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "policy-observability-evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "audit-export-projection.json").write_text(json.dumps(evidence["observability_package"], ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(render_summary(evidence), encoding="utf-8")
    (output_dir / "index.html").write_text(render_html(evidence), encoding="utf-8")


def render_summary(evidence: dict[str, Any]) -> str:
    source = evidence["source_evidence"]
    package = evidence["observability_package"]
    return "\n".join(
        [
            "# V5-8D Policy Observability Evidence Summary",
            "",
            f"status: {evidence['status']}",
            f"stage: {evidence['stage']}",
            f"evidence_scope: {evidence['evidence_scope']}",
            f"provider: {source['provider']}",
            f"model_ref: {source['model_ref']}",
            f"provider_invocation_count: {source['provider_invocation_count']}",
            f"audit_event_count: {len(package['audit_events'])}",
            f"worker_credential_ref_count: {len(package['policy_credential_decision']['worker_credential_refs'])}",
            f"distributed_runtime_complete: {str(evidence['distributed_runtime_complete']).lower()}",
            f"production_ready: {str(evidence['production_ready']).lower()}",
            f"source_agent_can_mutate: {str(evidence['source_agent_can_mutate']).lower()}",
            "missing_evidence:",
            "- none" if evidence["status"] == "PASS" else "- policy / observability projection evidence",
            "",
            "No False Green: this proves only policy / credential / observability projection. It does not prove complete distributed runtime readiness.",
            "",
        ]
    )


def render_html(evidence: dict[str, Any]) -> str:
    package = evidence["observability_package"]
    source = evidence["source_evidence"]
    event_rows = "".join(
        "<tr>"
        f"<td>{html.escape(event['event_type'])}</td>"
        f"<td>{html.escape(str(event.get('policy_decision_ref', '')))}</td>"
        f"<td>{html.escape(str(event.get('redaction_status', '')))}</td>"
        "</tr>"
        for event in package["audit_events"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V5-8D Policy Observability Evidence</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #0f172a; background: #f8fafc; }}
    .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin-bottom: 18px; }}
    .pass {{ color: #15803d; font-weight: 700; }}
    .warn {{ color: #b45309; font-weight: 700; }}
    table {{ border-collapse: collapse; width: 100%; background: white; }}
    th, td {{ border: 1px solid #e2e8f0; padding: 10px; text-align: left; }}
    th {{ background: #f1f5f9; }}
    code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>V5-8D 策略 / 凭证 / 可观测性证据</h1>
    <p>Status: <span class="pass">{html.escape(evidence["status"])}</span></p>
    <p>Source evidence: <code>{html.escape(source["scenario"])}</code>, provider <code>{html.escape(str(source["provider"]))}</code>, model <code>{html.escape(str(source["model_ref"]))}</code></p>
    <p class="warn">No False Green: 本证据不证明完整分布式多 Agent 运行时。</p>
  </div>
  <div class="card">
    <h2>Audit Events</h2>
    <table>
      <thead><tr><th>Event Type</th><th>Policy Decision Ref</th><th>Redaction</th></tr></thead>
      <tbody>{event_rows}</tbody>
    </table>
  </div>
  <div class="card">
    <h2>Boundary</h2>
    <ul>
      <li>readonly=true</li>
      <li>report_actions=view/export</li>
      <li>production_ready=false</li>
      <li>source_agent_can_mutate=false</li>
      <li>unrestricted connector / external LLM call=false</li>
    </ul>
  </div>
  <div class="card">
    <h2>Raw Data</h2>
    <p><a href="policy-observability-evidence.json">policy-observability-evidence.json</a></p>
    <p><a href="audit-export-projection.json">audit-export-projection.json</a></p>
    <p><a href="result-summary.md">result-summary.md</a></p>
  </div>
</body>
</html>
"""


def main() -> int:
    evidence = build_evidence()
    write_evidence(evidence)
    print(json.dumps({"status": evidence["status"], "output_dir": str(OUTPUT_DIR.relative_to(REPO_ROOT))}, ensure_ascii=False, indent=2))
    return 0 if evidence["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
