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
    DistributedRunCoordinator,
    DistributedRunRequest,
    DistributedWorkerDescriptor,
    read_v4_multi_agent_evidence_summary,
    seed_workers_for_stations,
)
from tests.v5_3_observability_support import make_context
from tests.v5_7b_runtime_support import make_human_authorization


OUTPUT_DIR = REPO_ROOT / "docs" / "design" / "V5.x" / "evidence" / "v5-8b-distributed-coordination"
SCENARIOS = ("UX-08-serial-video", "UX-09-parallel-deliberation", "UX-10-engineering-workflow")


def build_evidence() -> dict[str, Any]:
    context = make_context()
    scenario_summaries = [read_v4_multi_agent_evidence_summary(scenario) for scenario in SCENARIOS]
    scenario_results = []
    all_pass = True
    for summary in scenario_summaries:
        station_ids = summary["station_ids"][:3]
        registry = AgentWorkerRegistry()
        seed_workers_for_stations(context, registry, station_ids)
        replacement_station = station_ids[1]
        replacement_worker_id = f"worker_{replacement_station}_replacement"
        registry.register(
            DistributedWorkerDescriptor.from_context(
                context,
                worker_id=replacement_worker_id,
                station_id=replacement_station,
                credential_decision_ref=f"credential-decision://v5-8b/{replacement_station}/replacement",
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
            idempotency_key=f"v5-8b-{summary['scenario']}",
            correlation_id=context.correlation_id,
            request_id=context.request_id,
        )
        started = coordinator.start_run(context, request)
        restarted = coordinator.recover_after_restart(started.distributed_run_id or "")
        recovered_worker = coordinator.recover_lost_worker(
            started.distributed_run_id or "",
            station_id=replacement_station,
            replacement_worker_id=replacement_worker_id,
        )
        scenario_pass = (
            started.status == "coordinated"
            and restarted.status == "recovered"
            and recovered_worker.status == "worker_recovered"
            and summary["real_provider_backed"] is True
            and bool(recovered_worker.run_state and recovered_worker.run_state["downstream_stale"])
        )
        all_pass = all_pass and scenario_pass
        scenario_results.append(
            {
                "scenario": summary["scenario"],
                "status": "PASS" if scenario_pass else "FAIL",
                "source_evidence": {
                    "result_path": summary["result_path"],
                    "summary_path": summary["summary_path"],
                    "provider": summary["provider"],
                    "model_ref": summary["model_ref"],
                    "provider_invocation_count": summary["provider_invocation_count"],
                    "real_provider_backed": summary["real_provider_backed"],
                },
                "started": started.run_state,
                "start_evidence": started.evidence,
                "restart_recovery": restarted.run_state,
                "worker_recovery": recovered_worker.run_state,
            }
        )
    return {
        "schema_version": "v5_8b.distributed_coordination_evidence.v1",
        "stage": "V5-8B Minimal Distributed Run Coordination Slice",
        "status": "PASS" if all_pass else "FAIL",
        "evidence_scope": "real_provider_backed_source_evidence_plus_in_memory_coordination",
        "runtime_backed": True,
        "real_provider_backed_source_count": len(scenario_summaries),
        "distributed_runtime_complete": False,
        "production_ready": False,
        "source_agent_can_mutate": False,
        "production_routes_added": False,
        "production_workers_started": False,
        "scenarios": scenario_results,
        "allowed_claim": "V5-8B complete: minimal distributed run coordination slice ready for review.",
        "forbidden_claims": [
            "distributed multi-Agent runtime ready",
            "full multi-Agent orchestration ready",
            "Agent executor ready",
            "production controlled executor ready",
            "production-ready external app support",
        ],
    }


def write_evidence(evidence: dict[str, Any], output_dir: Path = OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "coordination-evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(render_summary(evidence), encoding="utf-8")
    (output_dir / "index.html").write_text(render_html(evidence), encoding="utf-8")


def render_summary(evidence: dict[str, Any]) -> str:
    lines = [
        "# V5-8B Distributed Coordination Evidence Summary",
        "",
        f"status: {evidence['status']}",
        f"stage: {evidence['stage']}",
        f"evidence_scope: {evidence['evidence_scope']}",
        f"runtime_backed: {str(evidence['runtime_backed']).lower()}",
        f"distributed_runtime_complete: {str(evidence['distributed_runtime_complete']).lower()}",
        f"production_ready: {str(evidence['production_ready']).lower()}",
        f"source_agent_can_mutate: {str(evidence['source_agent_can_mutate']).lower()}",
        f"production_routes_added: {str(evidence['production_routes_added']).lower()}",
        f"production_workers_started: {str(evidence['production_workers_started']).lower()}",
        "scenario_results:",
    ]
    for scenario in evidence["scenarios"]:
        source = scenario["source_evidence"]
        lines.append(f"- {scenario['scenario']}: {scenario['status']} provider={source['provider']} model={source['model_ref']} invocations={source['provider_invocation_count']}")
    lines.extend(
        [
            "missing_evidence:",
            "- none" if evidence["status"] == "PASS" else "- failed coordination scenario",
            "",
            "No False Green: this proves only a minimal coordination slice. It does not prove distributed multi-Agent runtime ready or full multi-Agent orchestration ready.",
            "",
        ]
    )
    return "\n".join(lines)


def render_html(evidence: dict[str, Any]) -> str:
    rows = "".join(
        "<tr>"
        f"<td>{html.escape(scenario['scenario'])}</td>"
        f"<td>{html.escape(scenario['status'])}</td>"
        f"<td>{html.escape(str(scenario['source_evidence']['provider']))}</td>"
        f"<td>{html.escape(str(scenario['source_evidence']['model_ref']))}</td>"
        f"<td>{scenario['source_evidence']['provider_invocation_count']}</td>"
        f"<td>{len(scenario['started']['assignments'])}</td>"
        f"<td>{len(scenario['worker_recovery']['downstream_stale'])}</td>"
        "</tr>"
        for scenario in evidence["scenarios"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V5-8B Distributed Coordination Evidence</title>
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
    <h1>V5-8B 最小分布式协调切片证据</h1>
    <p>Status: <span class="pass">{html.escape(evidence["status"])}</span></p>
    <p>Evidence scope: <code>{html.escape(evidence["evidence_scope"])}</code></p>
    <p class="warn">No False Green: 本证据不证明完整分布式多 Agent 运行时，不证明 Agent executor 或 production controlled executor ready。</p>
  </div>
  <div class="card">
    <h2>Scenario Evidence</h2>
    <table>
      <thead><tr><th>Scenario</th><th>Status</th><th>Provider</th><th>Model</th><th>Provider Calls</th><th>Assignments</th><th>Stale Markers</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
  <div class="card">
    <h2>Boundary</h2>
    <ul>
      <li>production_routes_added=false</li>
      <li>production_workers_started=false</li>
      <li>source_agent_can_mutate=false</li>
      <li>distributed_runtime_complete=false</li>
    </ul>
  </div>
  <div class="card">
    <h2>Raw Data</h2>
    <p><a href="coordination-evidence.json">coordination-evidence.json</a></p>
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
