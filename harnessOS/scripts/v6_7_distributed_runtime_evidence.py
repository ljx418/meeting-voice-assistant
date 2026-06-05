from __future__ import annotations

import html
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.auth.tenant_boundary import IdentityContext
from core.policies.v6_controlled_executor_runtime import V6ExecutionScope, V6HumanAuthorization
from core.workflows.v6_7_distributed_runtime import (
    V67AgentWorkerRegistry,
    V67DistributedRunCoordinator,
    V67DistributedRunRequest,
    V67WorkerDescriptor,
    build_v67_observability_package,
    build_v67_runtime_report,
    seed_v67_workers,
)


OUT_DIR = Path("docs/design/V6.x/evidence/v6-7-distributed-runtime")
FORBIDDEN_CLAIMS = (
    "distributed multi-Agent runtime ready",
    "full multi-Agent orchestration ready",
    "Agent executor ready",
    "production controlled executor ready",
    "autonomous workflow editing ready",
    "complete Workflow Studio ready",
    "production-ready external app support",
    "分布式多Agent运行时已完成",
    "生产级Agent执行器已完成",
)
SAFE_CONTEXT_MARKERS = (
    "Forbidden",
    "Non-Goals",
    "No False Green",
    "Stop Conditions",
    "禁止",
    "不得声明",
    "不证明",
    "不能",
    "not ",
    "does not prove",
)
SENSITIVE_TERMS = (
    "capability_token",
    "subscription_token",
    "Authorization",
    "Bearer",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw prompt",
    "upstream signed URL",
    "sk-",
)


def context(*, actor_type: str = "human_user", tenant_id: str = "tenant_v6_7", actor_id: str = "user_v6_7") -> IdentityContext:
    return IdentityContext(
        tenant_id=tenant_id,
        workspace_id="workspace_v6_7",
        project_id="project_v6_7",
        app_id="app_v6_7",
        actor_type=actor_type,
        actor_id=actor_id,
        user_id=actor_id if actor_type == "human_user" else None,
        service_account_id=actor_id if actor_type == "service_account" else None,
        agent_id=actor_id if actor_type == "agent" else None,
        session_id="session_v6_7" if actor_type == "agent" else None,
        request_id=f"request_{actor_id}",
        correlation_id=f"correlation_{actor_id}",
    )


def authorization(ctx: IdentityContext) -> V6HumanAuthorization:
    return V6HumanAuthorization(
        human_authorization_ref="human-auth://v6-7/evidence",
        authorization_subject_actor_id=ctx.actor_id,
        authorization_created_at="2026-06-03T00:00:00+00:00",
        authorization_expires_at="2999-01-01T00:00:00+00:00",
        allowed_operations=("workflow.instance.start",),
        tenant_id=ctx.tenant_id,
        workspace_id=ctx.workspace_id,
        authorizing_human_user_id=ctx.user_id or "user_v6_7",
        audit_ref="audit://v6-7/human-authorization",
    )


def request(
    ctx: IdentityContext,
    *,
    branch_station_ids: dict[str, tuple[str, ...]] | None = None,
    station_dependencies: dict[str, tuple[str, ...]] | None = None,
    completed_station_ids: tuple[str, ...] = (),
    source: str = "product_console",
    user_confirmed: bool = True,
    idempotency_key: str = "v6-7-evidence-start",
) -> V67DistributedRunRequest:
    return V67DistributedRunRequest(
        workflow_instance_id="workflow-instance-v6-7-evidence",
        source=source,
        actor_type=ctx.actor_type,
        target_scope=V6ExecutionScope.from_context(ctx),
        user_confirmed=user_confirmed,
        human_authorization=authorization(ctx),
        branch_station_ids=branch_station_ids or {"branch-script": ("writer",), "branch-review": ("reviewer",)},
        evidence_source_refs=(
            "docs/design/V6.x/evidence/v6-6-external-app-onboarding/acceptance-data.json",
            "docs/design/V6.x/evidence/v6-5-agent-governance/acceptance-data.json",
        ),
        idempotency_key=idempotency_key,
        correlation_id=ctx.correlation_id,
        request_id=ctx.request_id,
        completed_station_ids=completed_station_ids,
        station_dependencies=station_dependencies or {},
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "raw").mkdir(parents=True, exist_ok=True)
    ctx = context()
    registry = V67AgentWorkerRegistry()
    seed_v67_workers(ctx, registry, 8)
    coordinator = V67DistributedRunCoordinator(registry=registry)
    scenarios: list[dict[str, Any]] = []

    started = coordinator.start_run(ctx, request(ctx, branch_station_ids={"branch-a": ("writer", "storyboard"), "branch-b": ("reviewer", "publisher")})) 
    scenarios.append(_scenario("distributed_run_start", started.status == "started", started.evidence))
    assert started.distributed_run_id is not None

    serial = coordinator.start_run(
        ctx,
        request(
            ctx,
            branch_station_ids={"serial": ("upstream", "downstream")},
            station_dependencies={"downstream": ("upstream",)},
            idempotency_key="v6-7-serial",
        ),
    )
    scenarios.append(_scenario("serial_station_dependency_blocks_downstream", serial.run_state is not None and serial.run_state["branch_states"]["serial"] == "waiting_dependency", serial.run_state))

    source_agent = coordinator.start_run(ctx, request(ctx, source="agent", idempotency_key="v6-7-agent-denied"))
    scenarios.append(_scenario("source_agent_worker_assignment_denied", source_agent.blocked_reason == "source_agent_durable_mutation_denied", source_agent.__dict__))

    wrong_ctx = context(tenant_id="tenant_other", actor_id="user_other")
    wrong_tenant = coordinator.start_run(wrong_ctx, request(wrong_ctx, idempotency_key="v6-7-wrong-tenant"))
    scenarios.append(_scenario("worker_wrong_tenant_denied", wrong_tenant.blocked_reason == "worker_not_available_or_scope_denied", wrong_tenant.__dict__))

    recovered = coordinator.recover_worker(
        ctx,
        started.distributed_run_id,
        station_id="writer",
        failure_type="timeout",
        replacement_worker_id="worker_v6_7_5",
        recovery_strategy="retry_replacement_worker",
        idempotency_key="v6-7-recover-writer",
    )
    scenarios.append(_scenario("timeout_retry_keeps_old_error", _has_recovered_attempt(recovered.run_state, "writer"), recovered.evidence))
    replay = coordinator.recover_worker(
        ctx,
        started.distributed_run_id,
        station_id="writer",
        failure_type="timeout",
        replacement_worker_id="worker_v6_7_5",
        recovery_strategy="retry_replacement_worker",
        idempotency_key="v6-7-recover-writer",
    )
    scenarios.append(_scenario("idempotent_retry_returns_prior_recovery_ref", replay.status == "idempotent_recovery_replay" and replay.evidence == recovered.evidence, replay.evidence))

    state = coordinator.store.load(started.distributed_run_id)
    report = build_v67_runtime_report(state)
    package = build_v67_observability_package(state)
    scenarios.append(_scenario("artifact_lineage_preserves_producer_attempt_id", _lineage_has_producer_attempt(report), report))
    scenarios.append(_scenario("incident_timeline_records_assignment_timeout_retry_recovery", _timeline_has_recovery(report), report))
    scenarios.append(_scenario("runtime_report_readonly", report["readonly"] is True and report["report_actions"] == ["view", "export"], report))

    claims = _claim_scan()
    redaction = _redaction_scan({"started": started.run_state, "serial": serial.run_state, "report": report, "package": package})
    scenarios.append(_scenario("distributed_runtime_no_false_green", claims["status"] == "PASS", claims))

    data = {
        "schema_version": "v6_7.distributed_runtime.acceptance.v1",
        "stage": "V6-7",
        "status": "PASS" if all(item["status"] == "PASS" for item in scenarios) and claims["status"] == "PASS" and redaction["status"] == "PASS" else "FAIL",
        "allowed_claim": "V6-7 complete: distributed multi-Agent runtime productization pilot slice ready for review.",
        "evidence_scope": "repo_backed_pilot_runtime_slice",
        "distributed_multi_agent_runtime_ready": False,
        "full_multi_agent_orchestration_ready": False,
        "agent_executor_ready": False,
        "production_controlled_executor_ready": False,
        "autonomous_workflow_editing_ready": False,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "claim_violations": claims["violations"],
        "redaction_status": redaction["status"],
        "next_stage": "V6-8 Product Console And Studio Gate",
        "next_stage_entry_decision": "V6-8 may proceed only as Product Console / Thin Web Console scope; Full Workflow Studio still requires a separate PRD.",
    }
    raw = {
        "started": started.run_state,
        "serial_dependency": serial.run_state,
        "source_agent_denied": source_agent.__dict__,
        "wrong_tenant_denied": wrong_tenant.__dict__,
        "recovered": recovered.run_state,
        "runtime_report": report,
        "observability_package": package,
    }
    _write_json("acceptance-data.json", data)
    _write_json("raw/runtime-results.json", raw)
    _write_json("raw/worker-assignments.json", report["assignments"])
    _write_json("raw/attempt-history.json", report["attempt_history"])
    _write_json("raw/artifact-lineage.json", report["artifact_lineage"])
    _write_json("raw/incident-timeline.json", report["incident_timeline"])
    _write_summary(data)
    _write_claim_scan(claims)
    _write_redaction_scan(redaction)
    _write_html(data)


def _scenario(scenario_id: str, passed: bool, evidence: Any) -> dict[str, Any]:
    audit_ref = evidence.get("audit_ref") if isinstance(evidence, dict) else None
    return {
        "scenario_id": scenario_id,
        "status": "PASS" if passed else "FAIL",
        "evidence_scope": "repo_backed_pilot_runtime_slice",
        "audit_ref": audit_ref,
    }


def _has_recovered_attempt(state: dict[str, Any] | None, station_id: str) -> bool:
    if not state:
        return False
    attempts = state["station_attempts"][station_id]
    return len(attempts) == 2 and attempts[0]["status"] == "failed" and attempts[0]["error_ref"] and attempts[1]["previous_attempt_id"] == attempts[0]["attempt_id"]


def _lineage_has_producer_attempt(report: dict[str, Any]) -> bool:
    return all(item.get("producer_attempt_id") for item in report["artifact_lineage"].values())


def _timeline_has_recovery(report: dict[str, Any]) -> bool:
    event_types = {item["event_type"] for item in report["incident_timeline"]}
    return {"worker_timeout", "retry_scheduled", "attempt_recovered", "artifact_lineage_recorded"}.issubset(event_types)


def _claim_scan() -> dict[str, Any]:
    files = [
        Path("docs/design/V6.x/00_README.md"),
        Path("docs/design/V6.x/v6_development_and_acceptance_plan.md"),
        Path("docs/design/V6.x/v6_remaining_development_and_acceptance_plan.md"),
        Path("docs/design/V6.x/v6_7_distributed_runtime_development_and_acceptance_plan.md"),
        Path("docs/design/V6.x/v6_7_no_false_green_guard.md"),
    ]
    violations: list[dict[str, str]] = []
    for path in files:
        if not path.exists():
            continue
        safe_context = False
        current_heading = ""
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.startswith("#"):
                current_heading = line
                safe_context = False
            if any(marker.lower() in line.lower() for marker in SAFE_CONTEXT_MARKERS):
                safe_context = True
            for claim in FORBIDDEN_CLAIMS:
                context_blob = f"{current_heading}\n{line}"
                if claim.lower() in line.lower() and not safe_context and not any(marker.lower() in context_blob.lower() for marker in SAFE_CONTEXT_MARKERS):
                    violations.append({"path": str(path), "line": str(lineno), "claim": claim, "text": line.strip()})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations}


def _redaction_scan(data: Any) -> dict[str, Any]:
    serialized = json.dumps(data, ensure_ascii=False)
    violations = [term for term in SENSITIVE_TERMS if term.lower() in serialized.lower()]
    return {"status": "PASS" if not violations else "FAIL", "violations": violations}


def _write_json(name: str, data: Any) -> None:
    path = OUT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_summary(data: dict[str, Any]) -> None:
    text = f"""# V6-7 Distributed Runtime Acceptance Result

## Result

```text
status: {data["status"]}
evidence_scope: {data["evidence_scope"]}
distributed_multi_agent_runtime_ready: false
full_multi_agent_orchestration_ready: false
agent_executor_ready: false
production_controlled_executor_ready: false
scenario_count: {data["scenario_count"]}
```

## Allowed Claim

```text
{data["allowed_claim"]}
```

## Evidence

```text
docs/design/V6.x/evidence/v6-7-distributed-runtime/index.html
docs/design/V6.x/evidence/v6-7-distributed-runtime/acceptance-data.json
docs/design/V6.x/evidence/v6-7-distributed-runtime/raw/runtime-results.json
docs/design/V6.x/evidence/v6-7-distributed-runtime/raw/worker-assignments.json
docs/design/V6.x/evidence/v6-7-distributed-runtime/raw/attempt-history.json
docs/design/V6.x/evidence/v6-7-distributed-runtime/raw/artifact-lineage.json
docs/design/V6.x/evidence/v6-7-distributed-runtime/raw/incident-timeline.json
docs/design/V6.x/evidence/v6-7-distributed-runtime/claims-scan.md
docs/design/V6.x/evidence/v6-7-distributed-runtime/redaction-scan.md
```

## No False Green Statement

V6-7 proves only a distributed multi-Agent runtime productization pilot slice ready for review. It does not prove distributed multi-Agent runtime ready, full multi-Agent orchestration ready, Agent executor ready, production controlled executor ready, autonomous workflow editing ready, production-ready external app support, or complete Workflow Studio ready.
"""
    (OUT_DIR / "result-summary.md").write_text(text, encoding="utf-8")


def _write_claim_scan(claims: dict[str, Any]) -> None:
    lines = ["# V6-7 Claim Scan", "", f"status: {claims['status']}", "", "violations:"]
    if claims["violations"]:
        lines.extend(f"- {item['path']}:{item['line']} {item['claim']} :: {item['text']}" for item in claims["violations"])
    else:
        lines.append("- none")
    lines.append("")
    lines.append("Forbidden claims remain forbidden outside No False Green / Non-Goals / Forbidden Claims contexts.")
    (OUT_DIR / "claims-scan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_redaction_scan(redaction: dict[str, Any]) -> None:
    lines = ["# V6-7 Redaction Scan", "", f"status: {redaction['status']}", "", "violations:"]
    lines.extend(f"- {item}" for item in redaction["violations"]) if redaction["violations"] else lines.append("- none")
    (OUT_DIR / "redaction-scan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_html(data: dict[str, Any]) -> None:
    cards = "\n".join(
        f"<section class='card'><h2>{html.escape(item['scenario_id'])}</h2><p class='{item['status'].lower()}'>{item['status']}</p><p>{html.escape(item['evidence_scope'])}</p></section>"
        for item in data["scenarios"]
    )
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V6-7 Distributed Runtime Acceptance</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; background: #f8fafc; color: #0f172a; }}
    header {{ background: #dbeafe; border: 1px solid #2563eb; border-radius: 8px; padding: 20px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-top: 24px; }}
    .card {{ background: #fff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px; }}
    .pass {{ color: #15803d; font-weight: 700; }}
    .fail {{ color: #b91c1c; font-weight: 700; }}
    .warn {{ background: #fef3c7; border: 1px solid #d97706; border-radius: 8px; padding: 16px; margin-top: 16px; }}
  </style>
</head>
<body>
  <header>
    <h1>V6-7 分布式运行时产品化验收</h1>
    <p>状态：{html.escape(data['status'])}</p>
    <p>Allowed claim: {html.escape(data['allowed_claim'])}</p>
  </header>
  <section class="warn">
    <strong>No False Green:</strong>
    本报告只证明 pilot slice ready for review，不证明 distributed runtime ready、full multi-Agent orchestration ready、Agent executor ready 或 production controlled executor ready。
  </section>
  <main class="grid">{cards}</main>
  <section class="card">
    <h2>Raw Data</h2>
    <ul>
      <li><a href="acceptance-data.json">acceptance-data.json</a></li>
      <li><a href="raw/runtime-results.json">raw/runtime-results.json</a></li>
      <li><a href="claims-scan.md">claims-scan.md</a></li>
      <li><a href="redaction-scan.md">redaction-scan.md</a></li>
    </ul>
  </section>
</body>
</html>
"""
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
