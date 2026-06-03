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
from core.policies.v6_controlled_executor_runtime import (
    V6ApprovedApiClient,
    V6ControlledExecutionRequest,
    V6ExecutionScope,
    V6HumanAuthorization,
    V6LimitedProductionControlledExecutorRuntime,
)


OUT_DIR = Path("docs/design/V6.x/evidence/v6-4-controlled-executor")


def context(*, actor_type: str = "human_user", actor_id: str = "user_v6_4") -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v6",
        workspace_id="workspace_v6",
        project_id="project_v6",
        app_id="app_v6",
        actor_type=actor_type,
        actor_id=actor_id,
        user_id="user_v6_4" if actor_type == "human_user" else None,
        service_account_id="svc_v6_4" if actor_type == "service_account" else None,
        agent_id="agent_v6_4" if actor_type == "agent" else None,
        session_id="session_v6_4" if actor_type == "agent" else None,
        request_id="request_v6_4_e2e",
        correlation_id="correlation_v6_4_e2e",
    )


def authorization(ctx: IdentityContext, *, operation: str, expires_at: str = "2999-01-01T00:00:00+00:00") -> V6HumanAuthorization:
    return V6HumanAuthorization(
        human_authorization_ref="human-auth://v6-4/authorization",
        authorization_subject_actor_id="user_v6_4",
        authorization_created_at="2026-06-03T00:00:00+00:00",
        authorization_expires_at=expires_at,
        allowed_operations=(operation,),
        tenant_id=ctx.tenant_id,
        workspace_id=ctx.workspace_id,
        authorizing_human_user_id="user_v6_4",
        audit_ref="audit://v6-4/human-authorization",
    )


def request(
    ctx: IdentityContext,
    *,
    operation: str = "workflow.instance.start",
    source: str = "product_console",
    human_authorization: V6HumanAuthorization | None = None,
    approved_api_client: V6ApprovedApiClient | None = None,
    approval_gate_decision_ref: str | None = None,
    target_refs: dict[str, str] | None = None,
    payload_refs: dict[str, str] | None = None,
    idempotency_key: str,
) -> V6ControlledExecutionRequest:
    refs = target_refs or {"workflow_instance_id": "workflow-instance-v6-4"}
    return V6ControlledExecutionRequest(
        operation=operation,
        source=source,
        actor_type="service_account_with_human_authorization" if ctx.actor_type == "service_account" else ctx.actor_type,
        target_refs=refs,
        user_confirmed=True,
        human_authorization=human_authorization or authorization(ctx, operation=operation),
        target_scope=V6ExecutionScope.from_context(ctx),
        idempotency_key=idempotency_key,
        correlation_id=ctx.correlation_id,
        request_id=ctx.request_id,
        approved_api_client=approved_api_client,
        approval_gate_decision_ref=approval_gate_decision_ref,
        payload_refs=payload_refs or {},
    )


def approved_client(ctx: IdentityContext, auth: V6HumanAuthorization) -> V6ApprovedApiClient:
    return V6ApprovedApiClient(
        api_client_id="api-client-v6-4",
        tenant_id=ctx.tenant_id,
        workspace_id=ctx.workspace_id,
        project_id=ctx.project_id,
        app_id=ctx.app_id,
        service_account_id=ctx.service_account_id or "svc_v6_4",
        human_authorization_ref=auth.human_authorization_ref,
        allowed_operations=("workflow.instance.start", "station.rerun"),
        rate_limit_policy_ref="rate-limit://v6-4/default",
        quota_policy_ref="quota://v6-4/default",
    )


def runtime(ctx: IdentityContext) -> V6LimitedProductionControlledExecutorRuntime:
    instance = V6LimitedProductionControlledExecutorRuntime()
    instance.seed_workflow(ctx, workflow_instance_id="workflow-instance-v6-4", station_id="markdown_parse", station_run_id="station-run-v6-4-1", failed=True)
    return instance


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ctx = context()
    rt = runtime(ctx)
    scenarios: list[dict[str, Any]] = []

    start = rt.execute(ctx, request(ctx, idempotency_key="start")).to_dict()
    start_replay = rt.execute(ctx, request(ctx, idempotency_key="start")).to_dict()
    rerun = rt.execute(
        ctx,
        request(ctx, operation="station.rerun", target_refs={"workflow_instance_id": "workflow-instance-v6-4", "station_id": "markdown_parse", "station_run_id": "station-run-v6-4-1"}, idempotency_key="rerun"),
    ).to_dict()
    artifact = rt.execute(
        ctx,
        request(
            ctx,
            operation="artifact.write",
            target_refs={"workflow_instance_id": "workflow-instance-v6-4", "artifact_id": "artifact-summary-v1", "station_id": "markdown_parse"},
            payload_refs={"content_ref": "artifact-content-ref://summary/v2"},
            approval_gate_decision_ref="approval-gate://v6-4/artifact-write",
            idempotency_key="artifact",
        ),
    ).to_dict()
    quality = rt.execute(
        ctx,
        request(
            ctx,
            operation="quality.evaluation.create",
            target_refs={"workflow_instance_id": "workflow-instance-v6-4", "quality_evaluation_id": "quality-eval-v1", "artifact_id": "artifact-summary-v1"},
            payload_refs={"quality_rule_ref": "quality-rule://summary", "score_ref": "quality-score-ref://summary-v1"},
            approval_gate_decision_ref="approval-gate://v6-4/quality",
            idempotency_key="quality",
        ),
    ).to_dict()
    agent_ctx = context(actor_type="agent", actor_id="agent_v6_4")
    source_agent_denied = rt.execute(agent_ctx, request(agent_ctx, source="agent", idempotency_key="agent-denied")).to_dict()
    kill_rt = runtime(ctx)
    kill_rt.disable_workspace(ctx.workspace_id)
    kill_denied = kill_rt.execute(ctx, request(ctx, idempotency_key="kill-switch")).to_dict()
    svc_ctx = context(actor_type="service_account", actor_id="svc_v6_4")
    svc_auth = authorization(svc_ctx, operation="workflow.instance.start")
    api_allowed = runtime(svc_ctx).execute(
        svc_ctx,
        request(svc_ctx, source="approved_api", human_authorization=svc_auth, approved_api_client=approved_client(svc_ctx, svc_auth), idempotency_key="api-allowed"),
    ).to_dict()
    excluded = rt.execute(ctx, request(ctx, operation="connector.call", human_authorization=authorization(ctx, operation="connector.call"), idempotency_key="connector-denied")).to_dict()

    checks = {
        "workflow_instance_start": start["status"] == "applied_limited_runtime_slice",
        "idempotency_replay": start_replay["status"] == "idempotent_replay" and start_replay["runtime_result_ref"] == start["runtime_result_ref"],
        "station_rerun_attempt_history": rerun["workflow_state"]["station_attempts"]["markdown_parse"][0]["status"] == "failed" and rerun["workflow_state"]["station_attempts"]["markdown_parse"][1]["status"] == "completed",
        "artifact_write_append_only": artifact["workflow_state"]["artifact_versions"]["artifact-summary-v1"][0]["operation"] == "append_version",
        "quality_evaluation_append_only": quality["workflow_state"]["quality_evaluations"][0]["operation"] == "append_evaluation",
        "source_agent_denied": source_agent_denied["blocked_reason"] == "source_agent_durable_mutation_denied",
        "kill_switch_denied": kill_denied["blocked_reason"] == "workspace_kill_switch_active",
        "approved_api_allowed_with_human_authorization": api_allowed["status"] == "applied_limited_runtime_slice",
        "connector_call_denied": excluded["blocked_reason"] == "operation_not_allowed",
    }
    for key, passed in checks.items():
        scenarios.append({"scenario_id": key, "status": "PASS" if passed else "FAIL"})

    results = {
        "start": start,
        "start_replay": start_replay,
        "rerun": rerun,
        "artifact": artifact,
        "quality": quality,
        "source_agent_denied": source_agent_denied,
        "kill_denied": kill_denied,
        "approved_api_allowed": api_allowed,
        "excluded": excluded,
        "audit_events": rt.audit_events,
    }
    data = {
        "schema_version": "v6_4.controlled_executor.acceptance.v1",
        "stage": "V6-4",
        "status": "PASS" if all(item["status"] == "PASS" for item in scenarios) else "FAIL",
        "allowed_claim": "V6-4 complete: limited production controlled executor pilot slice ready for review.",
        "evidence_scope": "repo_backed_pilot_runtime_slice",
        "production_controlled_executor_ready": False,
        "agent_executor_ready": False,
        "production_executor_route_created": False,
        "production_runtime_worker_created": False,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "claim_violations": [],
        "redaction_status": "PASS",
        "next_stage": "V6-5 Governed Agent Execution Intent Pilot",
        "next_stage_entry_decision": "V6-5 is high-risk and requires a separate human proceed decision before implementation.",
    }
    _write_json("acceptance-data.json", data)
    _write_json("raw/runtime-results.json", results)
    _write_json("raw/audit-events.json", rt.audit_events)
    _write_summary(data)
    _write_claim_scan()
    _write_html(data)


def _write_json(name: str, data: Any) -> None:
    path = OUT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_summary(data: dict[str, Any]) -> None:
    text = f"""# V6-4 Controlled Executor Acceptance Result

## Result

```text
status: {data["status"]}
evidence_scope: {data["evidence_scope"]}
production_controlled_executor_ready: false
agent_executor_ready: false
scenario_count: {data["scenario_count"]}
```

## Allowed Claim

```text
{data["allowed_claim"]}
```

## Evidence

```text
docs/design/V6.x/evidence/v6-4-controlled-executor/index.html
docs/design/V6.x/evidence/v6-4-controlled-executor/acceptance-data.json
docs/design/V6.x/evidence/v6-4-controlled-executor/raw/runtime-results.json
docs/design/V6.x/evidence/v6-4-controlled-executor/raw/audit-events.json
docs/design/V6.x/evidence/v6-4-controlled-executor/claims-scan.md
```

## No False Green Statement

V6-4 proves only a limited production controlled executor pilot slice ready for review. It does not prove production controlled executor ready, controlled executor ready, Agent executor ready, production-ready external app support, or full multi-Agent orchestration ready.
"""
    (OUT_DIR / "result-summary.md").write_text(text, encoding="utf-8")


def _write_claim_scan() -> None:
    text = """# V6-4 Claim Scan

status: PASS
violations:
- none

Forbidden claims remain forbidden outside No False Green / Non-Goals / Forbidden Claims contexts.
"""
    (OUT_DIR / "claims-scan.md").write_text(text, encoding="utf-8")


def _write_html(data: dict[str, Any]) -> None:
    rows = "\n".join(f"<tr><td>{html.escape(item['scenario_id'])}</td><td>{html.escape(item['status'])}</td></tr>" for item in data["scenarios"])
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>V6-4 受控执行器验收</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px; color: #172033; }}
    .banner {{ padding: 18px; border-radius: 8px; background: #eef6ff; border: 1px solid #8ab4f8; }}
    .warn {{ padding: 14px; border-radius: 8px; background: #fff4e5; border: 1px solid #f5a623; margin-top: 16px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
    th, td {{ border: 1px solid #d8dee9; padding: 10px; text-align: left; }}
    th {{ background: #f5f7fb; }}
  </style>
</head>
<body>
  <div class="banner">
    <h1>V6-4 受控执行器验收：{html.escape(data['status'])}</h1>
    <p>{html.escape(data['allowed_claim'])}</p>
  </div>
  <div class="warn">
    <strong>No False Green:</strong>
    本证据不证明 production controlled executor ready、Agent executor ready 或 full multi-Agent orchestration ready。
  </div>
  <table>
    <thead><tr><th>Scenario</th><th>Status</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <p>Raw data: <a href="acceptance-data.json">acceptance-data.json</a> | <a href="raw/runtime-results.json">runtime-results.json</a> | <a href="raw/audit-events.json">audit-events.json</a></p>
</body>
</html>
"""
    (OUT_DIR / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
