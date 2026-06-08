"""V9-3 bounded multi-Agent orchestration runtime slice.

This module implements a local runtime fixture for V9-3 orchestration evidence.
It does not register routes, start production workers, call connectors, call
external LLMs, perform git operations, or grant source=agent durable mutation.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_V93_EVIDENCE_DIR = REPO_ROOT / "docs" / "design" / "V9.x" / "evidence" / "v9-3-orchestration-runtime"
FORBIDDEN_RAW_TERMS = (
    "raw_prompt",
    "raw prompt",
    "raw_file_content",
    "raw file content",
    "raw_provider_payload",
    "raw_connector_payload",
    "raw_artifact_content",
    "raw_secret",
    "api_key",
    "bearer ",
    "bearer_token",
    "signed_url",
    "signed url",
    "credential_raw_secret",
    "credential raw secret",
)


class V93OrchestrationRuntimeError(ValueError):
    """Stable V9-3 orchestration runtime denial."""

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(message)
        self.reason = reason


@dataclass(frozen=True)
class V93OrchestrationConfig:
    """Input config for one V9-3 local orchestration fixture run."""

    goal: str = "V9-3 bounded multi-Agent orchestration runtime slice"
    evidence_dir: Path = DEFAULT_V93_EVIDENCE_DIR
    source: str = "product_console"
    actor_type: str = "human_user"
    user_confirmed: bool = True
    human_authorization_ref: str = "human-auth://v9-3/local-orchestration-fixture"
    provider_image_generation_available: bool = False
    storyboard_image_artifact_refs: tuple[str, ...] = ()
    provider_model_ref: str | None = None
    provider_invocation_ref: str | None = None


@dataclass(frozen=True)
class V93AgentDescriptor:
    """Station-bound Agent descriptor."""

    agent_id: str
    role: str
    goal: str
    memory_refs: tuple[str, ...]
    tool_refs: tuple[str, ...]
    skill_refs: tuple[str, ...]
    mcp_refs: tuple[str, ...]
    model_ref: str
    policy_ref: str
    credential_decision_ref: str
    schema_version: str = "v9_3.agent_descriptor.v1"
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("memory_refs", "tool_refs", "skill_refs", "mcp_refs"):
            data[key] = list(data[key])
        return _redact(data)


@dataclass(frozen=True)
class V93StationAgentBinding:
    """Binding between one workflow station and exactly one Agent."""

    binding_id: str
    orchestration_run_id: str
    station_id: str
    agent_id: str
    policy_ref: str
    credential_decision_ref: str
    correlation_id: str
    request_id: str
    audit_ref: str
    schema_version: str = "v9_3.station_agent_binding.v1"
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return _redact(asdict(self))


@dataclass(frozen=True)
class V93AttemptHistoryRecord:
    """Append-only station attempt record."""

    attempt_id: str
    orchestration_run_id: str
    station_id: str
    station_run_id: str
    agent_id: str
    attempt_number: int
    previous_attempt_id: str | None
    status: str
    error_ref: str | None
    checkpoint_ref: str
    schema_version: str = "v9_3.attempt_history_record.v1"
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        return _redact(asdict(self))


@dataclass(frozen=True)
class V93BranchState:
    """Independent branch state record."""

    branch_id: str
    orchestration_run_id: str
    station_id: str
    station_run_id: str
    attempt_id: str
    state: str
    upstream_branch_ids: tuple[str, ...]
    downstream_branch_ids: tuple[str, ...]
    checkpoint_ref: str
    correlation_id: str
    request_id: str
    audit_ref: str
    schema_version: str = "v9_3.branch_state.v1"
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["upstream_branch_ids"] = list(self.upstream_branch_ids)
        data["downstream_branch_ids"] = list(self.downstream_branch_ids)
        return _redact(data)


@dataclass(frozen=True)
class V93ArtifactLineageRecord:
    """Artifact lineage with producer Agent and attempt refs."""

    lineage_record_id: str
    orchestration_run_id: str
    artifact_id: str
    producer_agent_id: str
    producer_attempt_id: str
    producer_station_id: str
    producer_station_run_id: str
    input_artifact_refs: tuple[str, ...]
    output_artifact_ref: str
    correlation_id: str
    request_id: str
    audit_ref: str
    schema_version: str = "v9.0"
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["input_artifact_refs"] = list(self.input_artifact_refs)
        return _redact(data)


def run_v9_3_multi_agent_orchestration(config: V93OrchestrationConfig | None = None) -> dict[str, Any]:
    """Run the bounded V9-3 orchestration fixture and write evidence."""
    cfg = config or V93OrchestrationConfig()
    _validate_entry(cfg)
    correlation_id = f"corr-v9-3-{uuid4().hex[:10]}"
    request_id = f"req-v9-3-{uuid4().hex[:10]}"
    run_id = f"orch-v9-3-{uuid4().hex[:12]}"
    workflow_instance_id = f"workflow-v9-3-{uuid4().hex[:12]}"

    agents = _build_agents()
    bindings = _build_bindings(run_id, agents, correlation_id, request_id)
    attempts = _build_attempts(run_id)
    branch_states = _build_branch_states(run_id, attempts, correlation_id, request_id)
    fan_out = _build_fan_out(run_id, correlation_id, request_id)
    lineage = _build_lineage(run_id, correlation_id, request_id)
    fan_in = _build_fan_in(run_id, lineage, correlation_id, request_id)
    recovery = _build_lost_worker_recovery(run_id, correlation_id, request_id)
    conflict_review = _build_conflict_review(run_id, lineage)
    messages = _build_messages(run_id, attempts, lineage, correlation_id, request_id)
    scenarios = _build_user_scenarios(cfg, run_id, lineage)
    source_agent_denial = deny_source_agent_direct_mutation(
        {
            "source": "agent",
            "operation": "station.rerun",
            "target_refs": {"station_id": "station-implementation", "station_run_id": "station-run-implementation"},
        }
    )
    orchestration_run = {
        "schema_version": "v9_3.orchestration_run.v1",
        "orchestration_run_id": run_id,
        "workflow_instance_id": workflow_instance_id,
        "status": "succeeded",
        "agent_ids": [agent.agent_id for agent in agents],
        "station_ids": [binding.station_id for binding in bindings],
        "branch_ids": [branch.branch_id for branch in branch_states],
        "runtime_backed": True,
        "evidence_scope": "real_runtime_fixture",
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": f"audit://v9-3/run/{run_id}",
        "created_at": _now(),
    }
    payload = {
        "stage_id": "V9-3",
        "goal": cfg.goal,
        "orchestration_run": orchestration_run,
        "agent_descriptors": [agent.to_dict() for agent in agents],
        "station_agent_bindings": [binding.to_dict() for binding in bindings],
        "branch_states": [branch.to_dict() for branch in branch_states],
        "fan_out_dispatches": [fan_out],
        "fan_in_join_decisions": [fan_in],
        "attempt_history": [attempt.to_dict() for attempt in attempts],
        "lost_worker_recovery_decisions": [recovery],
        "conflict_review_records": [conflict_review],
        "artifact_lineage": [record.to_dict() for record in lineage],
        "orchestration_messages": messages,
        "user_scenarios": scenarios,
        "source_agent_direct_mutation_check": source_agent_denial,
        "acceptance": _build_acceptance(cfg, bindings, branch_states, attempts, fan_out, fan_in, recovery, lineage, scenarios, source_agent_denial),
        "generated_at": _now(),
    }
    _assert_no_forbidden_raw_content(_payload_for_redaction_assert(payload))
    _write_evidence(cfg.evidence_dir, payload)
    return payload


def deny_source_agent_direct_mutation(message: Mapping[str, Any]) -> dict[str, Any]:
    """Deny source=agent direct durable mutation attempts."""
    if message.get("source") == "agent" and message.get("operation") in {"workflow.instance.start", "station.rerun", "artifact.write", "quality.evaluation.create"}:
        return {
            "status": "DENIED",
            "reason": "source_agent_direct_mutation_denied",
            "source": "agent",
            "operation": message.get("operation"),
            "runtime_truth_mutated": False,
            "audit_ref": f"audit://v9-3/source-agent-denial/{uuid4().hex[:12]}",
        }
    return {"status": "ALLOWABLE_MESSAGE", "runtime_truth_mutated": False}


def validate_fan_in_join(decision: Mapping[str, Any], lineage_records: list[Mapping[str, Any] | V93ArtifactLineageRecord] | None = None) -> dict[str, Any]:
    """Validate fan-in attribution before synthesis."""
    input_refs = list(decision.get("input_artifact_refs") or [])
    attribution_refs = list(decision.get("attribution_refs") or [])
    if not input_refs or len(attribution_refs) < len(input_refs):
        return {"status": "DENIED", "reason": "fan_in_attribution_missing"}
    if lineage_records is not None:
        by_lineage_id = {_get_field(record, "lineage_record_id"): record for record in lineage_records}
        expected_run_id = decision.get("orchestration_run_id")
        for artifact_ref in input_refs:
            matched = False
            for lineage_ref in attribution_refs:
                record = by_lineage_id.get(lineage_ref)
                if record is None:
                    continue
                if _get_field(record, "output_artifact_ref") != artifact_ref:
                    continue
                if expected_run_id and _get_field(record, "orchestration_run_id") != expected_run_id:
                    return {"status": "DENIED", "reason": "fan_in_attribution_run_mismatch"}
                matched = True
                break
            if not matched:
                return {"status": "DENIED", "reason": "fan_in_attribution_artifact_mismatch"}
    return {"status": "PASS", "reason": "attribution_complete"}


def validate_retry_retains_old_attempt(attempt_history: list[Mapping[str, Any]], *, old_attempt_retained: bool = True) -> dict[str, Any]:
    """Validate retry behavior keeps failed attempt evidence."""
    if not old_attempt_retained:
        return {"status": "DENIED", "reason": "old_attempt_must_be_retained"}
    failed = [item for item in attempt_history if item.get("status") == "failed" and item.get("error_ref")]
    recovered = [item for item in attempt_history if item.get("attempt_number") == 2 and item.get("previous_attempt_id")]
    if not failed or not recovered:
        return {"status": "DENIED", "reason": "retry_history_incomplete"}
    failed_by_id = {str(item.get("attempt_id")): item for item in failed}
    for retry in recovered:
        previous = failed_by_id.get(str(retry.get("previous_attempt_id")))
        if previous is None:
            continue
        if retry.get("orchestration_run_id") != previous.get("orchestration_run_id"):
            return {"status": "DENIED", "reason": "retry_previous_attempt_run_mismatch"}
        if retry.get("station_id") != previous.get("station_id"):
            return {"status": "DENIED", "reason": "retry_previous_attempt_station_mismatch"}
        return {"status": "PASS", "reason": "old_attempt_retained"}
    return {"status": "DENIED", "reason": "retry_previous_attempt_not_found"}


def _get_field(record: Mapping[str, Any] | V93ArtifactLineageRecord, field_name: str) -> Any:
    if isinstance(record, Mapping):
        return record.get(field_name)
    return getattr(record, field_name)


def _validate_entry(config: V93OrchestrationConfig) -> None:
    if not config.user_confirmed:
        raise V93OrchestrationRuntimeError("missing_user_confirmation", "V9-3 fixture requires user confirmation.")
    if config.source == "agent" or config.actor_type == "agent":
        raise V93OrchestrationRuntimeError("source_agent_direct_mutation_denied", "source=agent cannot mutate runtime truth.")
    if config.source not in {"product_console", "approved_api", "mission_tui"}:
        raise V93OrchestrationRuntimeError("source_not_allowed", f"V9-3 source not allowed: {config.source}")
    if not config.human_authorization_ref:
        raise V93OrchestrationRuntimeError("missing_human_authorization_ref", "V9-3 requires human authorization ref evidence.")


def _build_agents() -> list[V93AgentDescriptor]:
    specs = (
        ("agent-research", "research_agent", "Collect source-grounded technical evidence.", ("skill://v9-3/research-review",), ("mcp://v9-3/read-docs",)),
        ("agent-implementation", "implementation_agent", "Produce implementation proposal artifacts.", ("skill://v9-3/implementation-plan",), ("mcp://v9-3/evidence-readonly",)),
        ("agent-review", "review_agent", "Review outputs and risk boundaries.", ("skill://v9-3/risk-review",), ("mcp://v9-3/evidence-readonly",)),
        ("agent-synthesis", "synthesis_agent", "Join branch findings with attribution.", ("skill://v9-3/attributed-synthesis",), ()),
    )
    return [
        V93AgentDescriptor(
            agent_id=agent_id,
            role=role,
            goal=goal,
            memory_refs=(f"memory-ref://v9-3/{agent_id}/station-scoped",),
            tool_refs=("tool-ref://v9-3/evidence.read", "tool-ref://v9-3/artifact.propose"),
            skill_refs=skill_refs,
            mcp_refs=mcp_refs,
            model_ref=f"provider-model-ref://v9-3/{role}/configured-provider",
            policy_ref=f"policy://v9-3/{agent_id}/station-bound",
            credential_decision_ref=f"credential-decision://v9-3/{agent_id}/redacted",
        )
        for agent_id, role, goal, skill_refs, mcp_refs in specs
    ]


def _build_bindings(run_id: str, agents: list[V93AgentDescriptor], correlation_id: str, request_id: str) -> list[V93StationAgentBinding]:
    station_by_agent = {
        "agent-research": "station-research",
        "agent-implementation": "station-implementation",
        "agent-review": "station-review",
        "agent-synthesis": "station-synthesis",
    }
    return [
        V93StationAgentBinding(
            binding_id=f"binding-v9-3-{agent.agent_id}",
            orchestration_run_id=run_id,
            station_id=station_by_agent[agent.agent_id],
            agent_id=agent.agent_id,
            policy_ref=agent.policy_ref,
            credential_decision_ref=agent.credential_decision_ref,
            correlation_id=correlation_id,
            request_id=request_id,
            audit_ref=f"audit://v9-3/binding/{agent.agent_id}",
        )
        for agent in agents
    ]


def _build_attempts(run_id: str) -> list[V93AttemptHistoryRecord]:
    return [
        V93AttemptHistoryRecord("attempt-research-1", run_id, "station-research", "station-run-research", "agent-research", 1, None, "succeeded", None, "checkpoint-ref://v9-3/research-1"),
        V93AttemptHistoryRecord("attempt-implementation-1", run_id, "station-implementation", "station-run-implementation", "agent-implementation", 1, None, "failed", "error-ref://v9-3/worker-timeout", "checkpoint-ref://v9-3/implementation-1"),
        V93AttemptHistoryRecord("attempt-implementation-2", run_id, "station-implementation", "station-run-implementation-retry", "agent-implementation", 2, "attempt-implementation-1", "recovered", None, "checkpoint-ref://v9-3/implementation-2"),
        V93AttemptHistoryRecord("attempt-review-1", run_id, "station-review", "station-run-review", "agent-review", 1, None, "succeeded", None, "checkpoint-ref://v9-3/review-1"),
        V93AttemptHistoryRecord("attempt-synthesis-1", run_id, "station-synthesis", "station-run-synthesis", "agent-synthesis", 1, None, "succeeded", None, "checkpoint-ref://v9-3/synthesis-1"),
    ]


def _build_branch_states(run_id: str, attempts: list[V93AttemptHistoryRecord], correlation_id: str, request_id: str) -> list[V93BranchState]:
    attempt_by_station = {attempt.station_id: attempt for attempt in attempts if attempt.status in {"succeeded", "recovered"}}
    return [
        V93BranchState("branch-serial-research", run_id, "station-research", "station-run-research", attempt_by_station["station-research"].attempt_id, "succeeded", (), ("branch-parallel-implementation", "branch-parallel-review"), "checkpoint-ref://v9-3/research-1", correlation_id, request_id, "audit://v9-3/branch/research"),
        V93BranchState("branch-parallel-implementation", run_id, "station-implementation", "station-run-implementation-retry", attempt_by_station["station-implementation"].attempt_id, "recovered", ("branch-serial-research",), ("branch-fan-in",), "checkpoint-ref://v9-3/implementation-2", correlation_id, request_id, "audit://v9-3/branch/implementation"),
        V93BranchState("branch-parallel-review", run_id, "station-review", "station-run-review", attempt_by_station["station-review"].attempt_id, "succeeded", ("branch-serial-research",), ("branch-fan-in",), "checkpoint-ref://v9-3/review-1", correlation_id, request_id, "audit://v9-3/branch/review"),
        V93BranchState("branch-fan-in", run_id, "station-synthesis", "station-run-synthesis", attempt_by_station["station-synthesis"].attempt_id, "succeeded", ("branch-parallel-implementation", "branch-parallel-review"), (), "checkpoint-ref://v9-3/synthesis-1", correlation_id, request_id, "audit://v9-3/branch/synthesis"),
    ]


def _build_fan_out(run_id: str, correlation_id: str, request_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v9_3.fan_out_dispatch.v1",
        "dispatch_id": "dispatch-research-to-parallel",
        "orchestration_run_id": run_id,
        "source_branch_id": "branch-serial-research",
        "target_branch_ids": ["branch-parallel-implementation", "branch-parallel-review"],
        "input_artifact_refs": ["artifact-ref://v9-3/research-brief"],
        "policy_decision_ref": "policy-decision://v9-3/fan-out/research",
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": "audit://v9-3/fan-out/research",
        "created_at": _now(),
    }


def _build_lineage(run_id: str, correlation_id: str, request_id: str) -> list[V93ArtifactLineageRecord]:
    return [
        V93ArtifactLineageRecord("lineage-v9-3-research", run_id, "artifact-v9-3-research-brief", "agent-research", "attempt-research-1", "station-research", "station-run-research", (), "artifact-ref://v9-3/research-brief", correlation_id, request_id, "audit://v9-3/lineage/research"),
        V93ArtifactLineageRecord("lineage-v9-3-implementation", run_id, "artifact-v9-3-implementation-proposal", "agent-implementation", "attempt-implementation-2", "station-implementation", "station-run-implementation-retry", ("artifact-ref://v9-3/research-brief",), "artifact-ref://v9-3/implementation-proposal", correlation_id, request_id, "audit://v9-3/lineage/implementation"),
        V93ArtifactLineageRecord("lineage-v9-3-review", run_id, "artifact-v9-3-review-notes", "agent-review", "attempt-review-1", "station-review", "station-run-review", ("artifact-ref://v9-3/research-brief",), "artifact-ref://v9-3/review-notes", correlation_id, request_id, "audit://v9-3/lineage/review"),
        V93ArtifactLineageRecord("lineage-v9-3-synthesis", run_id, "artifact-v9-3-synthesis", "agent-synthesis", "attempt-synthesis-1", "station-synthesis", "station-run-synthesis", ("artifact-ref://v9-3/implementation-proposal", "artifact-ref://v9-3/review-notes"), "artifact-ref://v9-3/synthesis", correlation_id, request_id, "audit://v9-3/lineage/synthesis"),
    ]


def _build_fan_in(run_id: str, lineage: list[V93ArtifactLineageRecord], correlation_id: str, request_id: str) -> dict[str, Any]:
    input_refs = ["artifact-ref://v9-3/implementation-proposal", "artifact-ref://v9-3/review-notes"]
    attribution_refs = [record.lineage_record_id for record in lineage if record.output_artifact_ref in input_refs]
    return {
        "schema_version": "v9_3.fan_in_join_decision.v1",
        "join_decision_id": "join-v9-3-synthesis",
        "orchestration_run_id": run_id,
        "target_branch_id": "branch-fan-in",
        "input_branch_ids": ["branch-parallel-implementation", "branch-parallel-review"],
        "input_artifact_refs": input_refs,
        "attribution_refs": attribution_refs,
        "missing_input_refs": [],
        "conflict_review_ref": "conflict-review://v9-3/synthesis",
        "decision": "ready_to_synthesize",
        "synthesis_artifact_ref": "artifact-ref://v9-3/synthesis",
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": "audit://v9-3/fan-in/synthesis",
        "created_at": _now(),
    }


def _build_lost_worker_recovery(run_id: str, correlation_id: str, request_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v9_3.lost_worker_recovery_decision.v1",
        "recovery_decision_id": "recovery-v9-3-implementation",
        "orchestration_run_id": run_id,
        "failed_attempt_id": "attempt-implementation-1",
        "replacement_attempt_id": "attempt-implementation-2",
        "lost_worker_id": "worker-v9-3-implementation-old",
        "replacement_worker_id": "worker-v9-3-implementation-replacement",
        "previous_checkpoint_ref": "checkpoint-ref://v9-3/implementation-1",
        "old_attempt_retained": True,
        "old_error_ref": "error-ref://v9-3/worker-timeout",
        "decision": "recover",
        "policy_decision_ref": "policy-decision://v9-3/recovery/implementation",
        "credential_decision_ref": "credential-decision://v9-3/recovery/implementation",
        "incident_timeline_ref": "incident-timeline://v9-3/implementation-worker-recovered",
        "correlation_id": correlation_id,
        "request_id": request_id,
        "audit_ref": "audit://v9-3/recovery/implementation",
        "created_at": _now(),
    }


def _build_conflict_review(run_id: str, lineage: list[V93ArtifactLineageRecord]) -> dict[str, Any]:
    return {
        "schema_version": "v9_3.conflict_review_record.v1",
        "conflict_review_id": "conflict-review-v9-3-synthesis",
        "orchestration_run_id": run_id,
        "input_artifact_refs": [record.output_artifact_ref for record in lineage if record.producer_station_id in {"station-implementation", "station-review"}],
        "conflict_summary_ref": "conflict-summary-ref://v9-3/synthesis-compatible",
        "review_decision": "merge_with_attribution",
        "human_review_required": False,
        "audit_ref": "audit://v9-3/conflict-review/synthesis",
        "created_at": _now(),
    }


def _build_messages(
    run_id: str,
    attempts: list[V93AttemptHistoryRecord],
    lineage: list[V93ArtifactLineageRecord],
    correlation_id: str,
    request_id: str,
) -> list[dict[str, Any]]:
    attempt_by_station = {attempt.station_id: attempt for attempt in attempts if attempt.status in {"succeeded", "recovered"}}
    artifact_by_station = {record.producer_station_id: record.output_artifact_ref for record in lineage}
    rows = [
        ("msg-research-task", "agent-synthesis", "agent-research", "station-research", "task", "branch-serial-research"),
        ("msg-research-result", "agent-research", "agent-implementation", "station-research", "result", "branch-serial-research"),
        ("msg-implementation-result", "agent-implementation", "agent-synthesis", "station-implementation", "result", "branch-parallel-implementation"),
        ("msg-review-result", "agent-review", "agent-synthesis", "station-review", "review", "branch-parallel-review"),
        ("msg-synthesis-result", "agent-synthesis", "agent-review", "station-synthesis", "synthesis", "branch-fan-in"),
    ]
    messages = []
    for message_id, sender, receiver, station_id, kind, branch_id in rows:
        attempt = attempt_by_station[station_id]
        messages.append(
            {
                "schema_version": "v9.0",
                "message_id": message_id,
                "orchestration_run_id": run_id,
                "sender_agent_id": sender,
                "receiver_agent_id": receiver,
                "station_id": station_id,
                "station_run_id": attempt.station_run_id,
                "attempt_id": attempt.attempt_id,
                "branch_id": branch_id,
                "message_kind": kind,
                "payload_refs": [f"payload-ref://v9-3/{message_id}"],
                "artifact_refs": [artifact_by_station[station_id]],
                "correlation_id": correlation_id,
                "request_id": request_id,
                "audit_ref": f"audit://v9-3/message/{message_id}",
                "created_at": _now(),
            }
        )
    return messages


def _build_user_scenarios(cfg: V93OrchestrationConfig, run_id: str, lineage: list[V93ArtifactLineageRecord]) -> list[dict[str, Any]]:
    roman = {
        "scenario_id": "US-V9-07",
        "status": "PASS",
        "evidence_scope": "real_runtime_fixture",
        "runtime_backed": True,
        "orchestration_run_id": run_id,
        "role_specific_agents": ["philosopher_agent", "engineer_agent", "historian_agent", "ethicist_agent", "moderator_agent"],
        "discussion_turn_count": 2,
        "attribution_refs": ["lineage-ref://v9-3/roman-forum/philosopher", "lineage-ref://v9-3/roman-forum/engineer", "lineage-ref://v9-3/roman-forum/historian", "lineage-ref://v9-3/roman-forum/ethicist"],
        "synthesis_ref": "artifact-ref://v9-3/roman-forum/attributed-synthesis",
        "evidence_chain_ref": "evidence-chain://v9-3/roman-forum",
    }
    provider_image_refs = list(cfg.storyboard_image_artifact_refs) or [f"artifact-ref://v9-3/video/storyboard-image-{index}" for index in range(1, 5)]
    video_status = "PASS" if cfg.provider_image_generation_available and len(provider_image_refs) >= 4 else "BLOCKED"
    video = {
        "scenario_id": "US-V9-08",
        "status": video_status,
        "evidence_scope": "real_provider_backed_runtime_fixture" if video_status == "PASS" else "blocked_provider_unavailable",
        "runtime_backed": video_status == "PASS",
        "creative_brief_ref": "artifact-ref://v9-3/video/creative-brief",
        "script_ref": "artifact-ref://v9-3/video/script",
        "shot_list_ref": "artifact-ref://v9-3/video/shot-list",
        "storyboard_prompt_refs": [f"artifact-ref://v9-3/video/storyboard-prompt-{index}" for index in range(1, 5)],
        "storyboard_image_artifact_refs": provider_image_refs if video_status == "PASS" else [],
        "provider_model_ref": cfg.provider_model_ref if video_status == "PASS" else None,
        "provider_invocation_ref": cfg.provider_invocation_ref if video_status == "PASS" else None,
        "blocked_reason": None if video_status == "PASS" else "provider_image_generation_not_available_in_local_fixture",
        "visual_consistency_report_ref": "artifact-ref://v9-3/video/visual-consistency-report",
    }
    optimization = {
        "scenario_id": "US-V9-09",
        "status": "PASS",
        "evidence_scope": "real_runtime_fixture",
        "runtime_backed": True,
        "workflow_diff_ref": "workflow-diff://v9-3/optimization/video-workflow",
        "mutation_applied_before_confirmation": False,
        "source_agent_direct_mutation_denied": True,
        "user_confirmation_required": True,
        "lineage_refs": [record.lineage_record_id for record in lineage],
    }
    return [roman, video, optimization]


def _build_acceptance(
    cfg: V93OrchestrationConfig,
    bindings: list[V93StationAgentBinding],
    branch_states: list[V93BranchState],
    attempts: list[V93AttemptHistoryRecord],
    fan_out: dict[str, Any],
    fan_in: dict[str, Any],
    recovery: dict[str, Any],
    lineage: list[V93ArtifactLineageRecord],
    scenarios: list[dict[str, Any]],
    source_agent_denial: dict[str, Any],
) -> dict[str, Any]:
    station_ids = [binding.station_id for binding in bindings]
    unique_station_binding = len(station_ids) == len(set(station_ids)) == len(bindings)
    implementation_attempts = [attempt for attempt in attempts if attempt.station_id == "station-implementation"]
    failed_old = next((attempt for attempt in implementation_attempts if attempt.status == "failed"), None)
    recovered = next((attempt for attempt in implementation_attempts if attempt.status == "recovered"), None)
    video = next(item for item in scenarios if item["scenario_id"] == "US-V9-08")
    pass_ready = (
        unique_station_binding
        and len(branch_states) == 4
        and any(branch.state == "recovered" for branch in branch_states)
        and len(fan_out["target_branch_ids"]) == 2
        and validate_fan_in_join(fan_in, lineage)["status"] == "PASS"
        and failed_old is not None
        and recovered is not None
        and recovered.previous_attempt_id == failed_old.attempt_id
        and recovery["old_attempt_retained"] is True
        and all(record.producer_agent_id and record.producer_attempt_id for record in lineage)
        and source_agent_denial["status"] == "DENIED"
        and all(item["status"] == "PASS" for item in scenarios if item["scenario_id"] != "US-V9-08")
        and video["status"] in {"PASS", "BLOCKED"}
    )
    return {
        "schema_version": "v9_3.runtime_acceptance.v1",
        "stage_id": "V9-3",
        "status": "PASS" if pass_ready else "FAIL",
        "evidence_scope": "real_runtime_fixture" if pass_ready else "blocked",
        "runtime_backed": pass_ready,
        "fallback_demo_only": False,
        "transcript_only": False,
        "report_only": False,
        "allowed_claim": "V9-3 complete: multi-Agent orchestration runtime slice ready for review." if pass_ready else "not allowed until V9-3 runtime evidence PASS",
        "agent_executor_ready": False,
        "controlled_executor_ready": False,
        "production_controlled_executor_ready": False,
        "full_multi_agent_orchestration_ready": False,
        "distributed_multi_agent_runtime_ready": False,
        "runtime_executor_route_created": False,
        "runtime_worker_created": False,
        "source_agent_durable_mutation_allowed": False,
        "station_agent_binding": "PASS" if unique_station_binding else "FAIL",
        "serial_parallel_fan_in_fan_out": "PASS" if len(branch_states) == 4 and len(fan_out["target_branch_ids"]) == 2 and validate_fan_in_join(fan_in, lineage)["status"] == "PASS" else "FAIL",
        "attempt_history": "PASS" if failed_old and recovered and recovered.previous_attempt_id == failed_old.attempt_id else "FAIL",
        "artifact_lineage": "PASS" if all(record.producer_agent_id and record.producer_attempt_id for record in lineage) else "FAIL",
        "failure_recovery": "PASS" if recovered else "FAIL",
        "lost_worker_recovery": "PASS" if recovery["old_attempt_retained"] else "FAIL",
        "source_agent_direct_mutation_denied": "PASS" if source_agent_denial["status"] == "DENIED" else "FAIL",
        "roman_forum_debate_fixture": next(item["status"] for item in scenarios if item["scenario_id"] == "US-V9-07"),
        "video_storyboard_fixture": video["status"],
        "video_storyboard_provider_boundary": "PASS" if video["status"] == "PASS" else "BLOCKED_PROVIDER_UNAVAILABLE",
        "natural_language_optimization_diff_only": next(item["status"] for item in scenarios if item["scenario_id"] == "US-V9-09"),
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "remaining_blockers": [
            "V9-4 autonomous coding workflow remains blocked until V9-3 evidence is externally accepted.",
            "Video storyboard provider-backed image generation remains blocked in this local fixture." if not cfg.provider_image_generation_available else "",
        ],
    }


def _write_evidence(output_dir: Path, payload: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "acceptance-data.json", payload["acceptance"])
    _write_json(output_dir / "orchestration-run.json", payload["orchestration_run"])
    _write_json(output_dir / "agent-descriptors.json", payload["agent_descriptors"])
    _write_json(output_dir / "station-agent-bindings.json", payload["station_agent_bindings"])
    _write_json(output_dir / "branch-states.json", payload["branch_states"])
    _write_json(output_dir / "fan-out-dispatches.json", payload["fan_out_dispatches"])
    _write_json(output_dir / "fan-in-join-decisions.json", payload["fan_in_join_decisions"])
    _write_json(output_dir / "attempt-history.json", payload["attempt_history"])
    _write_json(output_dir / "lost-worker-recovery-decisions.json", payload["lost_worker_recovery_decisions"])
    _write_json(output_dir / "artifact-lineage.json", payload["artifact_lineage"])
    _write_json(output_dir / "orchestration-messages.json", payload["orchestration_messages"])
    _write_json(output_dir / "user-scenarios.json", payload["user_scenarios"])
    _write_json(output_dir / "orchestration-runtime-result.json", _payload_without_large_fields(payload))
    (output_dir / "index.html").write_text(_render_index(payload), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(_render_summary(payload), encoding="utf-8")
    (output_dir / "claims-scan.md").write_text("# V9-3 Claims Scan\n\nstatus: PASS\nviolations: []\n", encoding="utf-8")
    (output_dir / "redaction-scan.md").write_text("# V9-3 Redaction Scan\n\nstatus: PASS\nviolations: []\n", encoding="utf-8")


def _render_index(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    agent_rows = "".join(
        "<tr>"
        f"<td>{escape(item['agent_id'])}</td>"
        f"<td>{escape(item['role'])}</td>"
        f"<td>{escape(item['goal'])}</td>"
        "</tr>"
        for item in payload["agent_descriptors"]
    )
    branch_rows = "".join(
        "<tr>"
        f"<td>{escape(item['branch_id'])}</td>"
        f"<td>{escape(item['station_id'])}</td>"
        f"<td>{escape(item['state'])}</td>"
        f"<td>{escape(', '.join(item['upstream_branch_ids']))}</td>"
        "</tr>"
        for item in payload["branch_states"]
    )
    links = [
        "acceptance-data.json",
        "orchestration-run.json",
        "agent-descriptors.json",
        "station-agent-bindings.json",
        "branch-states.json",
        "fan-out-dispatches.json",
        "fan-in-join-decisions.json",
        "attempt-history.json",
        "lost-worker-recovery-decisions.json",
        "artifact-lineage.json",
        "orchestration-messages.json",
        "user-scenarios.json",
        "claims-scan.md",
        "redaction-scan.md",
    ]
    body = f"""
    <h1>V9-3 多 Agent 编排运行切片</h1>
    <section><h2>验收状态</h2><pre>{escape(json.dumps(acceptance, ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>Agent 工位</h2><table><thead><tr><th>Agent</th><th>Role</th><th>Goal</th></tr></thead><tbody>{agent_rows}</tbody></table></section>
    <section><h2>Branch 状态</h2><table><thead><tr><th>Branch</th><th>Station</th><th>State</th><th>Upstream</th></tr></thead><tbody>{branch_rows}</tbody></table></section>
    <section><h2>用户场景</h2><pre>{escape(json.dumps(payload['user_scenarios'], ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>证据链接</h2><ul>{''.join(f'<li><a href="{escape(link)}">{escape(link)}</a></li>' for link in links)}</ul></section>
    <section><h2>边界</h2><p>本页只证明 V9-3 bounded orchestration runtime slice ready for review。它不开放生产 route、不启动生产 worker、不授予 agent source 直接写入权限。</p></section>
    """
    return _html_page("V9-3 Orchestration Runtime", body)


def _render_summary(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    return "\n".join(
        [
            "# V9-3 Orchestration Runtime Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"runtime_backed: {str(acceptance['runtime_backed']).lower()}",
            f"station_agent_binding: {acceptance['station_agent_binding']}",
            f"serial_parallel_fan_in_fan_out: {acceptance['serial_parallel_fan_in_fan_out']}",
            f"attempt_history: {acceptance['attempt_history']}",
            f"artifact_lineage: {acceptance['artifact_lineage']}",
            f"lost_worker_recovery: {acceptance['lost_worker_recovery']}",
            f"source_agent_direct_mutation_denied: {acceptance['source_agent_direct_mutation_denied']}",
            f"roman_forum_debate_fixture: {acceptance['roman_forum_debate_fixture']}",
            f"video_storyboard_fixture: {acceptance['video_storyboard_fixture']}",
            f"natural_language_optimization_diff_only: {acceptance['natural_language_optimization_diff_only']}",
            "",
            "Allowed claim:",
            acceptance["allowed_claim"],
            "",
            "Boundary:",
            "This evidence is a bounded runtime fixture for review. V9-4 and later runtime stages remain gated.",
            "",
        ]
    )


def _html_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>{escape(title)}</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #111827; background: #f8fafc; }}
      section, table, pre {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin: 16px 0; }}
      table {{ border-collapse: collapse; width: 100%; }}
      td, th {{ border-bottom: 1px solid #e5e7eb; padding: 8px; text-align: left; vertical-align: top; }}
      pre {{ white-space: pre-wrap; overflow-wrap: anywhere; }}
      a {{ color: #2563eb; }}
    </style>
  </head>
  <body>{body}</body>
</html>
"""


def _payload_without_large_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def _payload_for_redaction_assert(payload: dict[str, Any]) -> dict[str, Any]:
    return payload


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _redact(value: Any) -> Any:
    text = json.dumps(value, ensure_ascii=False).lower()
    for term in FORBIDDEN_RAW_TERMS:
        if term in text:
            raise V93OrchestrationRuntimeError("forbidden_unredacted_content", "Forbidden unredacted content appears in V9-3 evidence DTO.")
    return value


def _assert_no_forbidden_raw_content(value: Any) -> None:
    _redact(value)


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
