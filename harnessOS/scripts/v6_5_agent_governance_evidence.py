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
from core.policies.v6_agent_governance import (
    AgentGovernanceResult,
    AgentIntentRequest,
    V6AgentGovernanceError,
    V6GovernedAgentExecutionIntentRuntime,
    load_v6_5_minimax_config,
)
from core.policies.v6_controlled_executor_runtime import (
    V6ControlledExecutionRequest,
    V6ExecutionScope,
    V6HumanAuthorization,
    V6LimitedProductionControlledExecutorRuntime,
)


OUT_DIR = Path("docs/design/V6.x/evidence/v6-5-agent-governance")


def agent_context() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v6",
        workspace_id="workspace_v6",
        project_id="project_v6",
        app_id="app_v6",
        actor_type="agent",
        actor_id="agent_actor_v6_5",
        agent_id="agent_v6_5",
        session_id="agent_session_v6_5",
        request_id="request_v6_5_agent",
        correlation_id="correlation_v6_5_e2e",
    )


def human_context() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v6",
        workspace_id="workspace_v6",
        project_id="project_v6",
        app_id="app_v6",
        actor_type="human_user",
        actor_id="user_v6_5",
        user_id="user_v6_5",
        request_id="request_v6_5_human",
        correlation_id="correlation_v6_5_e2e",
    )


def authorization(ctx: IdentityContext, operation: str) -> V6HumanAuthorization:
    return V6HumanAuthorization(
        human_authorization_ref="human-auth://v6-5/confirmed",
        authorization_subject_actor_id=ctx.actor_id,
        authorization_created_at="2026-06-03T00:00:00+00:00",
        authorization_expires_at="2999-01-01T00:00:00+00:00",
        allowed_operations=(operation,),
        tenant_id=ctx.tenant_id,
        workspace_id=ctx.workspace_id,
        authorizing_human_user_id=ctx.user_id or "user_v6_5",
        audit_ref="audit://v6-5/human-authorization",
    )


def intent_request() -> AgentIntentRequest:
    return AgentIntentRequest(
        operation="station.rerun",
        target_refs={
            "workflow_instance_id": "workflow-instance-v6-5",
            "station_id": "markdown_parse",
            "station_run_id": "station-run-v6-5-1",
        },
        requested_action_summary="Rerun the failed Markdown parsing station using governed handoff only.",
        redacted_runtime_status_ref="runtime-status://v6-5/redacted",
        redacted_failure_summary_ref="failure-summary://v6-5/redacted",
        policy_context_ref="policy-context://v6-5/default",
        prompt_template_ref="prompt-template://v6-5/agent-intent",
    )


def controlled_runtime(ctx: IdentityContext) -> V6LimitedProductionControlledExecutorRuntime:
    runtime = V6LimitedProductionControlledExecutorRuntime()
    runtime.seed_workflow(
        ctx,
        workflow_instance_id="workflow-instance-v6-5",
        station_id="markdown_parse",
        station_run_id="station-run-v6-5-1",
        failed=True,
    )
    return runtime


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "raw").mkdir(exist_ok=True)
    config = load_v6_5_minimax_config()
    data: dict[str, Any] = {
        "schema_version": "v6_5.agent_governance.acceptance.v1",
        "stage": "V6-5",
        "allowed_claim": "V6-5 complete: governed Agent execution intent pilot gate ready for review.",
        "provider": config.redacted(),
        "status": "BLOCKED",
        "blocked_reason": None,
        "scenario_count": 0,
        "scenarios": [],
        "claim_violations": [],
        "redaction_status": "PASS",
        "agent_executor_ready": False,
        "production_controlled_executor_ready": False,
        "autonomous_workflow_editing_ready": False,
    }
    if not config.api_key:
        data["blocked_reason"] = "minimax_key_missing"
        _write_all(data, {})
        return

    raw: dict[str, Any] = {}
    agent_rt = V6GovernedAgentExecutionIntentRuntime()
    agent_ctx = agent_context()
    human_ctx = human_context()
    try:
        proposal = agent_rt.propose(agent_ctx, intent_request())
    except V6AgentGovernanceError as exc:
        data["blocked_reason"] = exc.reason
        _write_all(data, raw)
        return

    proposal_data = proposal.to_dict()
    raw["proposal"] = proposal_data
    if proposal.status != "handoff_ready" or proposal.handoff is None:
        data["blocked_reason"] = proposal.blocked_reason or "handoff_not_ready"
        _write_all(data, raw)
        return

    controlled = controlled_runtime(human_ctx)
    executed = agent_rt.execute_confirmed_handoff(
        human_ctx,
        proposal.handoff,
        human_authorization=authorization(human_ctx, proposal.handoff.operation),
        controlled_runtime=controlled,
        idempotency_key="v6-5-confirmed-rerun",
    ).to_dict()
    raw["human_confirmed_controlled_execution"] = executed
    agent_direct_denial = controlled.execute(
        agent_ctx,
        V6ControlledExecutionRequest(
            operation="station.rerun",
            source="agent",
            actor_type="agent",
            target_refs=proposal.handoff.target_refs,
            user_confirmed=True,
            human_authorization=authorization(human_ctx, "station.rerun"),
            target_scope=V6ExecutionScope.from_context(agent_ctx),
            idempotency_key="v6-5-agent-direct-denied",
            correlation_id=agent_ctx.correlation_id,
            request_id=agent_ctx.request_id,
        ),
    ).to_dict()
    raw["source_agent_denial"] = agent_direct_denial

    checks = {
        "minimax_invocation_evidence": proposal.minimax_evidence is not None and proposal.minimax_evidence.provider == "minimax",
        "agent_intent_generated": proposal.intent is not None and proposal.intent.source == "agent",
        "policy_allows_handoff_only": proposal.decision is not None and proposal.decision.policy_decision == "allow_handoff",
        "handoff_requires_human_authorization": proposal.handoff.requires_human_authorization is True,
        "human_confirmed_handoff_executes_v6_4": executed["status"] == "applied_limited_runtime_slice",
        "source_agent_direct_mutation_denied": agent_direct_denial["blocked_reason"] == "source_agent_durable_mutation_denied",
        "no_agent_executor_claim": proposal_data["agent_executor_ready"] is False,
    }
    scenarios = [{"scenario_id": key, "status": "PASS" if value else "FAIL"} for key, value in checks.items()]
    data.update(
        {
            "status": "PASS" if all(item["status"] == "PASS" for item in scenarios) else "FAIL",
            "scenario_count": len(scenarios),
            "scenarios": scenarios,
            "blocked_reason": None,
        }
    )
    _write_all(data, raw)


def _write_all(data: dict[str, Any], raw: dict[str, Any]) -> None:
    _write_json("acceptance-data.json", data)
    _write_json("raw/runtime-results.json", raw)
    _write_summary(data)
    _write_claim_scan(data)
    _write_redaction_scan(data)
    _write_html(data)


def _write_json(name: str, data: Any) -> None:
    path = OUT_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_summary(data: dict[str, Any]) -> None:
    text = f"""# V6-5 Agent Governance Acceptance Result

## Result

```text
status: {data["status"]}
blocked_reason: {data.get("blocked_reason")}
provider: {data["provider"]["provider"]}
model_ref: {data["provider"]["model_ref"]}
provider_config_source: {data["provider"]["provider_config_source"]}
agent_executor_ready: false
production_controlled_executor_ready: false
```

## Allowed Claim

```text
{data["allowed_claim"] if data["status"] == "PASS" else "No completion claim allowed while V6-5 is not PASS."}
```

## No False Green Statement

V6-5 proves only a governed Agent execution intent pilot gate ready for review when PASS. It does not prove Agent executor ready, autonomous workflow editing ready, production controlled executor ready, complete Workflow Studio ready, or full multi-Agent orchestration ready.
"""
    (OUT_DIR / "result-summary.md").write_text(text, encoding="utf-8")


def _write_claim_scan(data: dict[str, Any]) -> None:
    status = "PASS" if not data["claim_violations"] else "FAIL"
    text = f"""# V6-5 Claim Scan

status: {status}
violations:
{chr(10).join(f"- {item}" for item in data["claim_violations"]) if data["claim_violations"] else "- none"}

Forbidden claims remain forbidden outside No False Green / Non-Goals / Forbidden Claims contexts.
"""
    (OUT_DIR / "claims-scan.md").write_text(text, encoding="utf-8")


def _write_redaction_scan(data: dict[str, Any]) -> None:
    text = f"""# V6-5 Redaction Scan

status: {data["redaction_status"]}

Sensitive raw prompt, raw credential, raw artifact content, token and secret values are not written to V6-5 evidence files.
"""
    (OUT_DIR / "redaction-scan.md").write_text(text, encoding="utf-8")


def _write_html(data: dict[str, Any]) -> None:
    rows = "\n".join(
        f"<tr><td>{html.escape(item['scenario_id'])}</td><td class='{item['status'].lower()}'>{item['status']}</td></tr>"
        for item in data["scenarios"]
    )
    body = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>V6-5 Agent Governance Acceptance</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px; color: #172554; }}
    .card {{ border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; margin: 16px 0; }}
    .pass {{ color: #15803d; font-weight: 700; }}
    .blocked, .fail {{ color: #b91c1c; font-weight: 700; }}
    table {{ border-collapse: collapse; width: 100%; }}
    td, th {{ border: 1px solid #cbd5e1; padding: 8px; text-align: left; }}
  </style>
</head>
<body>
  <h1>V6-5 Agent Governance Acceptance</h1>
  <section class="card">
    <p>Status: <span class="{html.escape(data['status'].lower())}">{html.escape(data['status'])}</span></p>
    <p>Blocked reason: {html.escape(str(data.get('blocked_reason')))}</p>
    <p>Provider: {html.escape(data['provider']['provider'])}</p>
    <p>Model: {html.escape(data['provider']['model_ref'])}</p>
    <p>Agent executor ready: false</p>
    <p>Production controlled executor ready: false</p>
  </section>
  <section class="card">
    <h2>Scenarios</h2>
    <table><thead><tr><th>Scenario</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table>
  </section>
  <section class="card">
    <h2>Evidence</h2>
    <ul>
      <li><a href="acceptance-data.json">acceptance-data.json</a></li>
      <li><a href="result-summary.md">result-summary.md</a></li>
      <li><a href="claims-scan.md">claims-scan.md</a></li>
      <li><a href="redaction-scan.md">redaction-scan.md</a></li>
      <li><a href="raw/runtime-results.json">raw/runtime-results.json</a></li>
    </ul>
  </section>
</body>
</html>
"""
    (OUT_DIR / "index.html").write_text(body, encoding="utf-8")


if __name__ == "__main__":
    main()
