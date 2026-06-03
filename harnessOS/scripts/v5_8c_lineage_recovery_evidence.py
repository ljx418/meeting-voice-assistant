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
    DistributedWorkerDescriptor,
    build_runtime_report_projection,
    read_v4_multi_agent_evidence_summary,
    seed_workers_for_stations,
)
from tests.v5_3_observability_support import make_context
from tests.v5_7b_runtime_support import make_human_authorization


OUTPUT_DIR = REPO_ROOT / "docs" / "design" / "V5.x" / "evidence" / "v5-8c-lineage-recovery"


def build_evidence() -> dict[str, Any]:
    context = make_context()
    summary = read_v4_multi_agent_evidence_summary("UX-10-engineering-workflow")
    station_ids = summary["station_ids"][:4]
    recovery_station = station_ids[2]
    registry = AgentWorkerRegistry()
    seed_workers_for_stations(context, registry, station_ids)
    replacement_worker_id = f"worker_{recovery_station}_replacement"
    registry.register(
        DistributedWorkerDescriptor.from_context(
            context,
            worker_id=replacement_worker_id,
            station_id=recovery_station,
            credential_decision_ref=f"credential-decision://v5-8c/{recovery_station}/replacement",
        )
    )
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
        idempotency_key="v5-8c-lineage-start",
        correlation_id=context.correlation_id,
        request_id=context.request_id,
    )
    started = coordinator.start_run(context, request)
    recovered = coordinator.recover_lost_worker(
        started.distributed_run_id or "",
        station_id=recovery_station,
        replacement_worker_id=replacement_worker_id,
    )
    state = coordinator.store.load(recovered.distributed_run_id or "")
    attempts = AttemptHistoryStore()
    lineage = ArtifactLineageService()
    attempts.ingest_state(state)
    lineage.ingest_state(state)
    report = build_runtime_report_projection(state, attempts, lineage)
    attempt_history = attempts.to_dict()
    artifact_lineage = lineage.to_dict()
    recovered_records = [
        record
        for record in artifact_lineage.values()
        if record["station_id"] == recovery_station and record["lineage_status"] == "recovered"
    ]
    status = "PASS" if recovered_records and report["readonly"] is True and report["report_actions"] == ["view", "export"] else "FAIL"
    return {
        "schema_version": "v5_8c.lineage_recovery_evidence.v1",
        "stage": "V5-8C Artifact Lineage And Attempt Recovery Slice",
        "status": status,
        "evidence_scope": "real_provider_backed_source_evidence_plus_in_memory_lineage_recovery",
        "source_evidence": {
            "scenario": summary["scenario"],
            "provider": summary["provider"],
            "model_ref": summary["model_ref"],
            "provider_invocation_count": summary["provider_invocation_count"],
            "real_provider_backed": summary["real_provider_backed"],
            "result_path": summary["result_path"],
            "summary_path": summary["summary_path"],
        },
        "recovery_station": recovery_station,
        "attempt_history": attempt_history,
        "artifact_lineage": artifact_lineage,
        "runtime_report": report,
        "distributed_runtime_complete": False,
        "production_ready": False,
        "source_agent_can_mutate": False,
        "redaction_status": "redacted",
    }


def write_evidence(evidence: dict[str, Any], output_dir: Path = OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "lineage-recovery-evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "runtime-report-projection.json").write_text(json.dumps(evidence["runtime_report"], ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(render_summary(evidence), encoding="utf-8")
    (output_dir / "index.html").write_text(render_html(evidence), encoding="utf-8")


def render_summary(evidence: dict[str, Any]) -> str:
    source = evidence["source_evidence"]
    return "\n".join(
        [
            "# V5-8C Lineage Recovery Evidence Summary",
            "",
            f"status: {evidence['status']}",
            f"stage: {evidence['stage']}",
            f"evidence_scope: {evidence['evidence_scope']}",
            f"provider: {source['provider']}",
            f"model_ref: {source['model_ref']}",
            f"provider_invocation_count: {source['provider_invocation_count']}",
            f"recovery_station: {evidence['recovery_station']}",
            f"distributed_runtime_complete: {str(evidence['distributed_runtime_complete']).lower()}",
            f"production_ready: {str(evidence['production_ready']).lower()}",
            f"source_agent_can_mutate: {str(evidence['source_agent_can_mutate']).lower()}",
            "runtime_report_readonly: true",
            "report_actions: view, export",
            "missing_evidence:",
            "- none" if evidence["status"] == "PASS" else "- lineage recovery evidence",
            "",
            "No False Green: this proves only artifact lineage and attempt recovery projection. It does not prove complete distributed runtime readiness.",
            "",
        ]
    )


def render_html(evidence: dict[str, Any]) -> str:
    source = evidence["source_evidence"]
    lineage_rows = "".join(
        "<tr>"
        f"<td>{html.escape(record['artifact_ref'])}</td>"
        f"<td>{html.escape(record['station_id'])}</td>"
        f"<td>{html.escape(record['producer_attempt_id'])}</td>"
        f"<td>{html.escape(str(record.get('previous_attempt_id') or ''))}</td>"
        f"<td>{html.escape(record['lineage_status'])}</td>"
        "</tr>"
        for record in evidence["artifact_lineage"].values()
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V5-8C Lineage Recovery Evidence</title>
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
    <h1>V5-8C 产物血缘与尝试恢复证据</h1>
    <p>Status: <span class="pass">{html.escape(evidence["status"])}</span></p>
    <p>Source evidence: <code>{html.escape(source["scenario"])}</code>, provider <code>{html.escape(str(source["provider"]))}</code>, model <code>{html.escape(str(source["model_ref"]))}</code></p>
    <p class="warn">No False Green: 本证据不证明完整分布式多 Agent 运行时。</p>
  </div>
  <div class="card">
    <h2>Artifact Lineage</h2>
    <table>
      <thead><tr><th>Artifact</th><th>Station</th><th>Producer Attempt</th><th>Previous Attempt</th><th>Status</th></tr></thead>
      <tbody>{lineage_rows}</tbody>
    </table>
  </div>
  <div class="card">
    <h2>Runtime Report Boundary</h2>
    <ul>
      <li>readonly=true</li>
      <li>report_actions=view/export</li>
      <li>production_ready=false</li>
      <li>source_agent_can_mutate=false</li>
    </ul>
  </div>
  <div class="card">
    <h2>Raw Data</h2>
    <p><a href="lineage-recovery-evidence.json">lineage-recovery-evidence.json</a></p>
    <p><a href="runtime-report-projection.json">runtime-report-projection.json</a></p>
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
