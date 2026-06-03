"""V6.5 governed Agent execution intent pilot slice.

This module implements only Agent intent, capability decision, and handoff
governance. It does not grant Agent executor authority, expose production
executor routes, start runtime workers, call connectors, or execute
source=agent durable mutations.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping, Protocol
from uuid import uuid4

import requests
from dotenv import dotenv_values

from apps.gateway.secrets import mask_value
from core.auth.tenant_boundary import IdentityContext
from core.policies.v6_controlled_executor_runtime import (
    INITIAL_ACTION_SET,
    MEDIUM_RISK_ACTIONS,
    V6ControlledExecutionRequest,
    V6ExecutionScope,
    V6HumanAuthorization,
    V6LimitedProductionControlledExecutorRuntime,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_AGENT_INTENT_OPERATIONS = {
    "business.event.emit",
    "context.update",
    "workflow.template.publish",
    "approval.respond",
    "connector.call",
    "external_llm.call",
    "credential.rotate",
    "credential.revoke",
    "audit.export.mutate",
}
SENSITIVE_TEXT = (
    "capability_token",
    "subscription_token",
    "authorization:",
    "bearer ",
    "secret",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw prompt",
    "upstream signed url",
    "sk-",
)
THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


class V6AgentGovernanceError(ValueError):
    """Stable V6-5 Agent governance denial."""

    def __init__(self, code: str, message: str, *, reason: str, resource: str | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
        self.resource = resource

    def to_error(self) -> dict[str, Any]:
        data: dict[str, Any] = {"reason": self.reason}
        if self.resource is not None:
            data["resource"] = self.resource
        return {"code": self.code, "message": str(self), "data": data}


@dataclass(frozen=True)
class V6MiniMaxIntentProviderConfig:
    """Redacted MiniMax config for V6-5 intent generation."""

    provider: str
    model_ref: str
    base_url: str
    api_key: str
    provider_config_source: str

    def redacted(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model_ref": self.model_ref,
            "base_url_ref": "env://MINIMAX_BASE_URL",
            "credential_ref": "env://MINIMAX_API_KEY",
            "provider_config_source": self.provider_config_source,
            "api_key_configured": bool(self.api_key),
            "redaction_status": "redacted",
        }


@dataclass(frozen=True)
class MiniMaxIntentInvocationEvidence:
    """Redacted evidence for one MiniMax intent-generation call."""

    invocation_id: str
    provider: str
    model_ref: str
    provider_config_source: str
    credential_ref: str
    prompt_template_ref: str
    input_runtime_snapshot_ref: str
    output_intent_ref: str
    redaction_status: str
    correlation_id: str
    created_at: str = field(default_factory=lambda: _now())
    token_usage_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class AgentExecutionIntent:
    """Agent-produced intent read model. It is not executable by itself."""

    intent_id: str
    agent_id: str
    session_id: str
    source: str
    operation: str
    target_refs: dict[str, str]
    requested_action_summary: str
    rationale_ref: str
    prompt_template_ref: str
    provider_invocation_ref: str
    created_at: str
    correlation_id: str
    redaction_status: str

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class AgentCapabilityDecision:
    """Policy/capability decision for one Agent intent."""

    decision_id: str
    intent_id: str
    policy_decision: str
    capability_decision: str
    risk_flags: tuple[str, ...]
    requires_user_confirmation: bool
    requires_approval_gate: bool
    denial_reason: str | None
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["risk_flags"] = list(self.risk_flags)
        return mask_value(data)


@dataclass(frozen=True)
class AgentExecutionHandoff:
    """Human-confirmation handoff for one Agent intent."""

    handoff_id: str
    intent_id: str
    operation: str
    target_refs: dict[str, str]
    status: str
    requires_human_authorization: bool
    human_authorization_ref: str | None
    approval_gate_decision_ref: str | None
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class AgentIntentRequest:
    """Input to the V6-5 Agent intent generator."""

    operation: str
    target_refs: dict[str, str]
    requested_action_summary: str
    redacted_runtime_status_ref: str
    redacted_failure_summary_ref: str
    policy_context_ref: str
    prompt_template_ref: str
    payload_refs: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentGovernanceResult:
    """End-to-end V6-5 intent decision and handoff result."""

    status: str
    intent: AgentExecutionIntent | None
    decision: AgentCapabilityDecision | None
    handoff: AgentExecutionHandoff | None
    minimax_evidence: MiniMaxIntentInvocationEvidence | None
    blocked_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return mask_value(
            {
                "status": self.status,
                "intent": self.intent.to_dict() if self.intent else None,
                "decision": self.decision.to_dict() if self.decision else None,
                "handoff": self.handoff.to_dict() if self.handoff else None,
                "minimax_evidence": self.minimax_evidence.to_dict() if self.minimax_evidence else None,
                "blocked_reason": self.blocked_reason,
                "agent_executor_ready": False,
                "production_controlled_executor_ready": False,
                "autonomous_workflow_editing_ready": False,
            }
        )


class IntentProvider(Protocol):
    """Provider protocol for Agent intent generation."""

    def generate_intent(self, context: IdentityContext, request: AgentIntentRequest) -> tuple[dict[str, Any], MiniMaxIntentInvocationEvidence]:
        """Generate a JSON-like intent and redacted provider evidence."""


class MiniMaxIntentProvider:
    """MiniMax chat completion adapter for V6-5 intent generation."""

    def __init__(self, config: V6MiniMaxIntentProviderConfig) -> None:
        self.config = config

    def generate_intent(self, context: IdentityContext, request: AgentIntentRequest) -> tuple[dict[str, Any], MiniMaxIntentInvocationEvidence]:
        if not self.config.api_key:
            raise V6AgentGovernanceError("V6_5_MINIMAX_KEY_MISSING", "MiniMax API key is required for V6-5 PASS.", reason="minimax_key_missing")
        _assert_no_sensitive_payload(asdict(request))
        prompt = _build_intent_prompt(request)
        response = requests.post(
            f"{self.config.base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {self.config.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.config.model_ref,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是 HarnessOS Agent intent 生成器。只输出一个 JSON object，不要 Markdown，不要代码块，不执行动作，不输出推理过程。",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "max_tokens": 700,
            },
            timeout=60,
        )
        if not response.ok:
            raise V6AgentGovernanceError("V6_5_MINIMAX_ERROR", "MiniMax provider request failed.", reason="minimax_provider_error", resource=str(response.status_code))
        payload = response.json()
        content = str(payload.get("choices", [{}])[0].get("message", {}).get("content", ""))
        intent = _parse_provider_intent(content)
        evidence = MiniMaxIntentInvocationEvidence(
            invocation_id=f"minimax-intent-{uuid4().hex[:12]}",
            provider="minimax",
            model_ref=self.config.model_ref,
            provider_config_source=self.config.provider_config_source,
            credential_ref="env://MINIMAX_API_KEY",
            prompt_template_ref=request.prompt_template_ref,
            input_runtime_snapshot_ref=request.redacted_runtime_status_ref,
            output_intent_ref=f"agent-intent-output://{uuid4().hex[:12]}",
            redaction_status="redacted",
            correlation_id=context.correlation_id,
            token_usage_ref="token-usage://v6-5/redacted" if payload.get("usage") else None,
        )
        _assert_no_sensitive_payload(evidence.to_dict())
        return intent, evidence


class FakeMiniMaxIntentProvider:
    """Deterministic MiniMax-shaped provider for tests."""

    def __init__(self, *, operation_override: str | None = None, malformed: bool = False) -> None:
        self.operation_override = operation_override
        self.malformed = malformed
        self.invocation_count = 0

    def generate_intent(self, context: IdentityContext, request: AgentIntentRequest) -> tuple[dict[str, Any], MiniMaxIntentInvocationEvidence]:
        self.invocation_count += 1
        if self.malformed:
            raise V6AgentGovernanceError("V6_5_INTENT_PARSE_FAILED", "MiniMax intent output could not be parsed.", reason="intent_parse_failed")
        intent = {
            "operation": self.operation_override or request.operation,
            "target_refs": request.target_refs,
            "requested_action_summary": request.requested_action_summary,
            "rationale_ref": f"rationale://v6-5/fake/{self.invocation_count}",
        }
        evidence = MiniMaxIntentInvocationEvidence(
            invocation_id=f"minimax-intent-fake-{self.invocation_count}",
            provider="minimax",
            model_ref="MiniMax-M2.1",
            provider_config_source="test",
            credential_ref="env://MINIMAX_API_KEY",
            prompt_template_ref=request.prompt_template_ref,
            input_runtime_snapshot_ref=request.redacted_runtime_status_ref,
            output_intent_ref=f"agent-intent-output://fake/{self.invocation_count}",
            redaction_status="redacted",
            correlation_id=context.correlation_id,
        )
        return intent, evidence


class V6GovernedAgentExecutionIntentRuntime:
    """Governed V6-5 Agent intent and handoff runtime slice."""

    def __init__(self, provider: IntentProvider | None = None) -> None:
        self.provider = provider or MiniMaxIntentProvider(load_v6_5_minimax_config())
        self.intents: list[AgentExecutionIntent] = []
        self.decisions: list[AgentCapabilityDecision] = []
        self.handoffs: list[AgentExecutionHandoff] = []
        self.minimax_evidence: list[MiniMaxIntentInvocationEvidence] = []

    def propose(self, context: IdentityContext, request: AgentIntentRequest) -> AgentGovernanceResult:
        try:
            self._validate_agent_context(context)
            _assert_no_sensitive_payload(asdict(request))
            provider_intent, evidence = self.provider.generate_intent(context, request)
            intent = self._build_intent(context, request, provider_intent, evidence)
            decision = self.decide(intent)
            handoff = self.create_handoff(intent, decision)
        except V6AgentGovernanceError as exc:
            return AgentGovernanceResult(status="blocked", intent=None, decision=None, handoff=None, minimax_evidence=None, blocked_reason=exc.reason)
        self.intents.append(intent)
        self.decisions.append(decision)
        if handoff:
            self.handoffs.append(handoff)
        self.minimax_evidence.append(evidence)
        return AgentGovernanceResult(
            status="handoff_ready" if handoff else "blocked",
            intent=intent,
            decision=decision,
            handoff=handoff,
            minimax_evidence=evidence,
            blocked_reason=decision.denial_reason,
        )

    def decide(self, intent: AgentExecutionIntent) -> AgentCapabilityDecision:
        risk_flags: list[str] = []
        denial_reason: str | None = None
        policy_decision = "allow_handoff"
        if intent.operation in EXCLUDED_AGENT_INTENT_OPERATIONS or intent.operation not in INITIAL_ACTION_SET:
            policy_decision = "deny"
            denial_reason = "agent_excluded_operation_denied"
            risk_flags.append("excluded_operation")
        if _target_ref_missing(intent.operation, intent.target_refs):
            policy_decision = "deny"
            denial_reason = "agent_missing_target_refs"
            risk_flags.append("missing_target_refs")
        if intent.operation in MEDIUM_RISK_ACTIONS:
            risk_flags.append("approval_gate_required")
        if intent.source != "agent":
            policy_decision = "deny"
            denial_reason = "invalid_intent_source"
            risk_flags.append("invalid_source")
        return AgentCapabilityDecision(
            decision_id=f"agent-decision-{uuid4().hex[:12]}",
            intent_id=intent.intent_id,
            policy_decision=policy_decision,
            capability_decision="allow_governed_handoff" if policy_decision == "allow_handoff" else "deny",
            risk_flags=tuple(risk_flags),
            requires_user_confirmation=True,
            requires_approval_gate=intent.operation in MEDIUM_RISK_ACTIONS,
            denial_reason=denial_reason,
        )

    def create_handoff(self, intent: AgentExecutionIntent, decision: AgentCapabilityDecision) -> AgentExecutionHandoff | None:
        if decision.policy_decision != "allow_handoff":
            return None
        return AgentExecutionHandoff(
            handoff_id=f"agent-handoff-{uuid4().hex[:12]}",
            intent_id=intent.intent_id,
            operation=intent.operation,
            target_refs=dict(intent.target_refs),
            status="awaiting_human_confirmation",
            requires_human_authorization=True,
            human_authorization_ref=None,
            approval_gate_decision_ref=None,
        )

    def confirm_handoff(
        self,
        context: IdentityContext,
        handoff: AgentExecutionHandoff,
        *,
        human_authorization: V6HumanAuthorization,
        approval_gate_decision_ref: str | None = None,
        idempotency_key: str | None = None,
    ) -> V6ControlledExecutionRequest:
        if context.actor_type != "human_user":
            raise V6AgentGovernanceError("V6_5_HUMAN_CONFIRMATION_DENIED", "Handoff confirmation requires a human user.", reason="missing_human_user")
        if handoff.status != "awaiting_human_confirmation":
            raise V6AgentGovernanceError("V6_5_HANDOFF_STATUS_DENIED", "Handoff is not awaiting confirmation.", reason="handoff_not_awaiting_confirmation")
        if human_authorization.human_authorization_ref == "":
            raise V6AgentGovernanceError("V6_5_HUMAN_AUTHORIZATION_REQUIRED", "Human authorization is required.", reason="missing_human_authorization")
        return V6ControlledExecutionRequest(
            operation=handoff.operation,
            source="product_console",
            actor_type="human_user",
            target_refs=dict(handoff.target_refs),
            user_confirmed=True,
            human_authorization=human_authorization,
            target_scope=V6ExecutionScope.from_context(context),
            idempotency_key=idempotency_key or f"v6-5-handoff-{handoff.handoff_id}",
            correlation_id=context.correlation_id,
            request_id=context.request_id,
            approval_gate_decision_ref=approval_gate_decision_ref,
        )

    def execute_confirmed_handoff(
        self,
        context: IdentityContext,
        handoff: AgentExecutionHandoff,
        *,
        human_authorization: V6HumanAuthorization,
        controlled_runtime: V6LimitedProductionControlledExecutorRuntime,
        approval_gate_decision_ref: str | None = None,
        idempotency_key: str | None = None,
    ) -> Any:
        request = self.confirm_handoff(
            context,
            handoff,
            human_authorization=human_authorization,
            approval_gate_decision_ref=approval_gate_decision_ref,
            idempotency_key=idempotency_key,
        )
        return controlled_runtime.execute(context, request)

    def _validate_agent_context(self, context: IdentityContext) -> None:
        if context.actor_type != "agent" or not context.agent_id or not context.session_id:
            raise V6AgentGovernanceError("V6_5_AGENT_CONTEXT_REQUIRED", "Agent intent generation requires an Agent context.", reason="missing_agent_context")

    def _build_intent(
        self,
        context: IdentityContext,
        request: AgentIntentRequest,
        provider_intent: Mapping[str, Any],
        evidence: MiniMaxIntentInvocationEvidence,
    ) -> AgentExecutionIntent:
        operation = _text(provider_intent.get("operation")) or request.operation
        target_refs = _string_mapping(provider_intent.get("target_refs")) or request.target_refs
        summary = _text(provider_intent.get("requested_action_summary")) or request.requested_action_summary
        rationale_ref = _text(provider_intent.get("rationale_ref")) or f"rationale://v6-5/{uuid4().hex[:12]}"
        data = {
            "intent_id": f"agent-intent-{uuid4().hex[:12]}",
            "agent_id": context.agent_id or "",
            "session_id": context.session_id or "",
            "source": "agent",
            "operation": operation,
            "target_refs": target_refs,
            "requested_action_summary": summary,
            "rationale_ref": rationale_ref,
            "prompt_template_ref": request.prompt_template_ref,
            "provider_invocation_ref": evidence.invocation_id,
            "created_at": _now(),
            "correlation_id": context.correlation_id,
            "redaction_status": "redacted",
        }
        _assert_no_sensitive_payload(data)
        return AgentExecutionIntent(**data)


def load_v6_5_minimax_config(env_files: tuple[str, ...] = (".env", ".env.local")) -> V6MiniMaxIntentProviderConfig:
    """Resolve V6-5 MiniMax config from dotenv and environment."""
    merged: dict[str, str] = {}
    source = "environment"
    for env_file in env_files:
        path = REPO_ROOT / env_file
        if path.exists():
            values = {key: value for key, value in dotenv_values(path).items() if value is not None}
            if values:
                merged.update(values)
                source = env_file
    merged.update({key: value for key, value in os.environ.items() if key.startswith(("V6_5_", "V5_", "V4_U5E_", "MINIMAX_", "LLM_"))})
    model_ref = (merged.get("V6_5_LLM_MODEL") or merged.get("V5_LLM_MODEL") or merged.get("V4_U5E_LLM_MODEL") or merged.get("LLM_MODEL") or "").strip()
    if not model_ref or model_ref.startswith("your-"):
        model_ref = "MiniMax-M2.1"
    api_key = (merged.get("MINIMAX_API_KEY") or "").strip()
    base_url = (merged.get("MINIMAX_BASE_URL") or "https://api.minimax.chat/v1").strip()
    return V6MiniMaxIntentProviderConfig(
        provider="minimax",
        model_ref=model_ref,
        base_url=base_url,
        api_key="" if _looks_placeholder(api_key) else api_key,
        provider_config_source=source,
    )


def _build_intent_prompt(request: AgentIntentRequest) -> str:
    return json.dumps(
        {
            "instruction": "Return only one JSON object for an AgentExecutionIntent. Do not execute anything. Do not wrap in markdown.",
            "operation": request.operation,
            "target_refs": request.target_refs,
            "requested_action_summary": request.requested_action_summary,
            "redacted_runtime_status_ref": request.redacted_runtime_status_ref,
            "redacted_failure_summary_ref": request.redacted_failure_summary_ref,
            "policy_context_ref": request.policy_context_ref,
            "allowed_operations": sorted(INITIAL_ACTION_SET),
            "output_schema": {
                "operation": "string",
                "target_refs": "object of string refs",
                "requested_action_summary": "string",
                "rationale_ref": "redacted ref",
            },
            "example_output": {
                "operation": request.operation,
                "target_refs": request.target_refs,
                "requested_action_summary": request.requested_action_summary,
                "rationale_ref": "rationale://v6-5/minimax/redacted",
            },
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def _parse_provider_intent(content: str) -> dict[str, Any]:
    stripped = THINK_RE.sub("", content).strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped).strip()
        stripped = re.sub(r"```$", "", stripped).strip()
    if "{" in stripped and "}" in stripped:
        stripped = stripped[stripped.find("{") : stripped.rfind("}") + 1]
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise V6AgentGovernanceError("V6_5_INTENT_PARSE_FAILED", "MiniMax intent output could not be parsed.", reason="intent_parse_failed") from exc
    if not isinstance(parsed, dict):
        raise V6AgentGovernanceError("V6_5_INTENT_PARSE_FAILED", "MiniMax intent output must be a JSON object.", reason="intent_parse_failed")
    return parsed


def _target_ref_missing(operation: str, refs: Mapping[str, str]) -> bool:
    if operation == "workflow.instance.start":
        return not refs.get("workflow_instance_id")
    if operation == "station.rerun":
        return not (refs.get("workflow_instance_id") and refs.get("station_id") and refs.get("station_run_id"))
    if operation == "artifact.write":
        return not (refs.get("artifact_id") or refs.get("output_artifact_target_id"))
    if operation == "quality.evaluation.create":
        return not (refs.get("quality_evaluation_id") or refs.get("station_id") or refs.get("artifact_id"))
    return False


def _assert_no_sensitive_payload(data: Mapping[str, Any]) -> None:
    dumped = json.dumps(data, ensure_ascii=False).lower()
    for term in SENSITIVE_TEXT:
        if term in dumped:
            raise V6AgentGovernanceError("V6_5_REDACTION_FAILED", "Sensitive text is not allowed in V6-5 DTOs.", reason="redaction_failed", resource=term)


def _text(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _string_mapping(value: Any) -> dict[str, str] | None:
    if not isinstance(value, Mapping):
        return None
    result = {str(key): str(item) for key, item in value.items() if str(item).strip()}
    return result or None


def _looks_placeholder(value: str) -> bool:
    lowered = value.strip().lower()
    return lowered in {"", "your-minimax-api-key-here", "<your-local-minimax-key>", "your-key"} or lowered.startswith("your-")


def _now() -> str:
    return datetime.now(UTC).isoformat()
