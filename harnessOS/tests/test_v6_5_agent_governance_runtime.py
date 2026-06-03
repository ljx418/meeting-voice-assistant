from __future__ import annotations

from core.auth.tenant_boundary import IdentityContext
from core.policies.v6_agent_governance import (
    AgentIntentRequest,
    FakeMiniMaxIntentProvider,
    V6GovernedAgentExecutionIntentRuntime,
    load_v6_5_minimax_config,
)
from core.policies.v6_controlled_executor_runtime import (
    V6ControlledExecutionRequest,
    V6ExecutionScope,
    V6HumanAuthorization,
    V6LimitedProductionControlledExecutorRuntime,
)


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
        request_id="request_v6_5",
        correlation_id="correlation_v6_5",
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
        correlation_id="correlation_v6_5",
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


def intent_request(*, operation: str = "station.rerun", target_refs: dict[str, str] | None = None, summary: str = "rerun failed Markdown station") -> AgentIntentRequest:
    return AgentIntentRequest(
        operation=operation,
        target_refs=target_refs
        or {
            "workflow_instance_id": "workflow-instance-v6-5",
            "station_id": "markdown_parse",
            "station_run_id": "station-run-v6-5-1",
        },
        requested_action_summary=summary,
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


def test_minimax_backed_agent_intent_creates_human_confirmed_handoff() -> None:
    runtime = V6GovernedAgentExecutionIntentRuntime(provider=FakeMiniMaxIntentProvider())

    result = runtime.propose(agent_context(), intent_request()).to_dict()

    assert result["status"] == "handoff_ready"
    assert result["intent"]["source"] == "agent"
    assert result["intent"]["operation"] == "station.rerun"
    assert result["decision"]["policy_decision"] == "allow_handoff"
    assert result["decision"]["requires_user_confirmation"] is True
    assert result["handoff"]["status"] == "awaiting_human_confirmation"
    assert result["handoff"]["requires_human_authorization"] is True
    assert result["minimax_evidence"]["provider"] == "minimax"
    assert result["agent_executor_ready"] is False


def test_human_confirmed_handoff_can_call_v6_4_controlled_executor() -> None:
    agent_runtime = V6GovernedAgentExecutionIntentRuntime(provider=FakeMiniMaxIntentProvider())
    proposed = agent_runtime.propose(agent_context(), intent_request())
    assert proposed.handoff is not None
    human = human_context()
    controlled = controlled_runtime(human)

    executed = agent_runtime.execute_confirmed_handoff(
        human,
        proposed.handoff,
        human_authorization=authorization(human, "station.rerun"),
        controlled_runtime=controlled,
        idempotency_key="v6-5-confirmed-rerun",
    ).to_dict()

    assert executed["status"] == "applied_limited_runtime_slice"
    assert executed["evidence"]["source"] == "product_console"
    assert executed["evidence"]["human_authorization_ref"] == "human-auth://v6-5/confirmed"
    assert executed["workflow_state"]["station_attempts"]["markdown_parse"][0]["status"] == "failed"
    assert executed["workflow_state"]["station_attempts"]["markdown_parse"][1]["status"] == "completed"


def test_source_agent_direct_controlled_executor_mutation_is_still_denied() -> None:
    agent = agent_context()
    controlled = controlled_runtime(human_context())
    request = V6ControlledExecutionRequest(
        operation="station.rerun",
        source="agent",
        actor_type="agent",
        target_refs={
            "workflow_instance_id": "workflow-instance-v6-5",
            "station_id": "markdown_parse",
            "station_run_id": "station-run-v6-5-1",
        },
        user_confirmed=True,
        human_authorization=authorization(human_context(), "station.rerun"),
        target_scope=V6ExecutionScope.from_context(agent),
        idempotency_key="agent-direct-denied",
        correlation_id=agent.correlation_id,
        request_id=agent.request_id,
    )

    result = controlled.execute(agent, request).to_dict()

    assert result["status"] == "blocked"
    assert result["blocked_reason"] == "source_agent_durable_mutation_denied"


def test_excluded_operation_intent_is_denied_before_handoff() -> None:
    runtime = V6GovernedAgentExecutionIntentRuntime(provider=FakeMiniMaxIntentProvider(operation_override="external_llm.call"))

    result = runtime.propose(agent_context(), intent_request(operation="station.rerun")).to_dict()

    assert result["status"] == "blocked"
    assert result["handoff"] is None
    assert result["decision"]["policy_decision"] == "deny"
    assert result["decision"]["denial_reason"] == "agent_excluded_operation_denied"


def test_artifact_write_intent_requires_approval_gate() -> None:
    runtime = V6GovernedAgentExecutionIntentRuntime(provider=FakeMiniMaxIntentProvider())
    request = intent_request(
        operation="artifact.write",
        target_refs={"workflow_instance_id": "workflow-instance-v6-5", "artifact_id": "artifact-v6-5", "station_id": "markdown_parse"},
        summary="append a corrected summary artifact",
    )

    result = runtime.propose(agent_context(), request).to_dict()

    assert result["status"] == "handoff_ready"
    assert result["decision"]["requires_approval_gate"] is True
    assert "approval_gate_required" in result["decision"]["risk_flags"]


def test_missing_minimax_key_blocks_default_provider(monkeypatch) -> None:
    monkeypatch.setenv("MINIMAX_API_KEY", "")
    config = load_v6_5_minimax_config(env_files=("missing.env",))
    runtime = V6GovernedAgentExecutionIntentRuntime()
    runtime.provider.config = config

    result = runtime.propose(agent_context(), intent_request()).to_dict()

    assert result["status"] == "blocked"
    assert result["blocked_reason"] == "minimax_key_missing"


def test_raw_artifact_content_in_agent_request_is_rejected() -> None:
    runtime = V6GovernedAgentExecutionIntentRuntime(provider=FakeMiniMaxIntentProvider())
    request = intent_request(summary="please use raw_artifact_content to rerun")

    result = runtime.propose(agent_context(), request).to_dict()

    assert result["status"] == "blocked"
    assert result["blocked_reason"] == "redaction_failed"

