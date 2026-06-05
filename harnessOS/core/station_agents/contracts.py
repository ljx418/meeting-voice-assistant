"""V8 station-agent contract helpers.

These contracts model a governed station-agent pilot. They intentionally do
not grant Agent executor authority or source=agent durable mutation rights.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from apps.gateway.secrets import mask_value


DURABLE_MUTATION_OPERATIONS = {
    "workflow.instance.start",
    "station.rerun",
    "artifact.write",
    "quality.evaluation.create",
}
DENIED_DEFAULT_OPERATIONS = {
    "connector.call",
    "external_llm.call",
    "business.event.emit",
    "context.update",
    "workflow.template.publish",
    "approval.respond",
    "git.commit",
    "git.push",
    "production.deploy",
}
SENSITIVE_TERMS = (
    "raw_prompt",
    "raw prompt",
    "raw_file_content",
    "raw file content",
    "raw_artifact_content",
    "raw_provider_payload",
    "raw_connector_payload",
    "api_key",
    "Bearer ",
    "signed_url",
    "MINIMAX_API_KEY",
    "DEEPSEEK_API_KEY",
)


def now_iso() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(UTC).isoformat()


@dataclass(frozen=True)
class AgentRuntimeProfile:
    """Runtime profile for one station Agent."""

    profile_id: str
    agent_id: str
    runtime_kind: str
    max_attempts: int
    timeout_policy_ref: str
    kill_switch_policy_ref: str
    requires_user_confirmation_for_mutation: bool
    high_risk_handoff_required: bool
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class StationAgentDescriptor:
    """Agent assigned to one workflow station."""

    agent_id: str
    station_id: str
    agent_name: str
    role: str
    goal: str
    agent_runtime_profile_ref: str
    model_profile_ref: str
    memory_policy_ref: str
    tool_policy_ref: str
    skill_binding_refs: tuple[str, ...]
    mcp_binding_refs: tuple[str, ...]
    context_policy_ref: str
    evidence_policy_ref: str
    allowed_operations: tuple[str, ...]
    forbidden_operations: tuple[str, ...]
    source_policy: str
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["skill_binding_refs"] = list(self.skill_binding_refs)
        data["mcp_binding_refs"] = list(self.mcp_binding_refs)
        data["allowed_operations"] = list(self.allowed_operations)
        data["forbidden_operations"] = list(self.forbidden_operations)
        return mask_value(data)


@dataclass(frozen=True)
class StationAgentRegistry:
    """Registry of station-to-Agent bindings for one workflow."""

    registry_id: str
    workflow_spec_id: str
    workflow_version_ref: str
    station_agent_descriptors: tuple[StationAgentDescriptor, ...]
    workflow_explainer_agent_id: str
    validation_result: dict[str, Any]
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return mask_value(
            {
                "registry_id": self.registry_id,
                "workflow_spec_id": self.workflow_spec_id,
                "workflow_version_ref": self.workflow_version_ref,
                "station_agent_descriptors": [descriptor.to_dict() for descriptor in self.station_agent_descriptors],
                "workflow_explainer_agent_id": self.workflow_explainer_agent_id,
                "validation_result": self.validation_result,
                "created_at": self.created_at,
                "runtime_truth_boundary": "station_agent_registry_is_not_runtime_truth",
            }
        )


@dataclass(frozen=True)
class StationAgentContextEnvelope:
    """Scoped context references provided to one station Agent."""

    context_envelope_id: str
    agent_id: str
    station_id: str
    workflow_context_refs: tuple[str, ...]
    upstream_artifact_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    memory_refs: tuple[str, ...]
    prompt_template_ref: str
    redaction_status: str
    context_scope: str
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("workflow_context_refs", "upstream_artifact_refs", "evidence_refs", "memory_refs"):
            data[key] = list(data[key])
        return mask_value(data)


@dataclass(frozen=True)
class AgentCapabilityDecision:
    """Capability decision for one Agent operation."""

    decision_id: str
    agent_id: str
    station_id: str
    operation: str
    source: str
    actor_type: str
    allowed: bool
    requires_user_confirmation: bool
    requires_handoff: bool
    risk_level: str
    policy_decision_ref: str
    forbidden_reason: str | None
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return mask_value(asdict(self))


@dataclass(frozen=True)
class AgentInvocationEvidence:
    """Redacted evidence for one station Agent invocation."""

    invocation_id: str
    agent_id: str
    station_id: str
    provider: str
    model_ref: str
    provider_config_source: str
    prompt_template_ref: str
    input_artifact_refs: tuple[str, ...]
    output_artifact_refs: tuple[str, ...]
    redaction_status: str
    correlation_id: str
    request_id: str
    invocation_kind: str
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["input_artifact_refs"] = list(self.input_artifact_refs)
        data["output_artifact_refs"] = list(self.output_artifact_refs)
        return mask_value(data)


@dataclass(frozen=True)
class StationAgentRunResult:
    """One station Agent run result."""

    run_result_id: str
    agent_id: str
    station_id: str
    station_run_id: str
    attempt_id: str
    status: str
    output_artifact_refs: tuple[str, ...]
    quality_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    llm_invocation_refs: tuple[str, ...]
    tool_call_refs: tuple[str, ...]
    mcp_call_refs: tuple[str, ...]
    capability_decision_refs: tuple[str, ...]
    redaction_status: str
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in (
            "output_artifact_refs",
            "quality_refs",
            "evidence_refs",
            "llm_invocation_refs",
            "tool_call_refs",
            "mcp_call_refs",
            "capability_decision_refs",
        ):
            data[key] = list(data[key])
        return mask_value(data)


def decide_agent_capability(
    *,
    agent_id: str,
    station_id: str,
    operation: str,
    source: str,
    actor_type: str,
    user_confirmed: bool = False,
) -> AgentCapabilityDecision:
    """Decide whether one Agent operation is allowed in the V8 pilot."""
    durable = operation in DURABLE_MUTATION_OPERATIONS
    denied_default = operation in DENIED_DEFAULT_OPERATIONS
    source_agent_mutation = source == "agent" and durable
    allowed = not denied_default and not source_agent_mutation and (not durable or user_confirmed)
    forbidden_reason: str | None = None
    if denied_default:
        forbidden_reason = "operation_requires_separate_stage_policy"
    elif source_agent_mutation:
        forbidden_reason = "source_agent_durable_mutation_denied"
    elif durable and not user_confirmed:
        forbidden_reason = "durable_mutation_requires_user_confirmation"
    risk_level = "high" if operation in DURABLE_MUTATION_OPERATIONS or operation in DENIED_DEFAULT_OPERATIONS else "low"
    return AgentCapabilityDecision(
        decision_id=f"agent_capability_{uuid4().hex[:12]}",
        agent_id=agent_id,
        station_id=station_id,
        operation=operation,
        source=source,
        actor_type=actor_type,
        allowed=allowed,
        requires_user_confirmation=durable,
        requires_handoff=durable or operation in DENIED_DEFAULT_OPERATIONS,
        risk_level=risk_level,
        policy_decision_ref=f"policy://v8/{'allow' if allowed else 'deny'}/{operation}",
        forbidden_reason=forbidden_reason,
    )


def build_local_document_station_agent_registry(workflow_spec: dict[str, Any]) -> StationAgentRegistry:
    """Build default station Agent bindings for the local document workflow."""
    station_map = {
        "folder_authorization": ("mission_agent", "MissionAgent", "mission_intake", "Capture and explain the authorized local document workflow goal."),
        "markdown_scan": ("scanner_agent", "ScannerAgent", "markdown_scanner", "Read authorized Markdown files through scoped read-only capability."),
        "per_folder_summary": ("folder_summary_agent", "FolderSummaryAgent", "folder_summarizer", "Generate per-folder technical summaries."),
        "overview_summary": ("overview_agent", "OverviewAgent", "overview_summarizer", "Generate the overall technical document summary."),
        "quality_check": ("quality_agent", "QualityAgent", "quality_reviewer", "Evaluate coverage, unsupported files and summary quality."),
        "runtime_report": ("report_agent", "ReportAgent", "runtime_reporter", "Render read-only Runtime Report and artifact links."),
        "evidence_record": ("workflow_explainer_agent", "WorkflowExplainerAgent", "workflow_explainer", "Explain the workflow result, boundaries, risk and evidence."),
    }
    descriptors: list[StationAgentDescriptor] = []
    for station in workflow_spec.get("stations", []):
        station_id = str(station["station_id"])
        agent_slug, agent_name, role, goal = station_map.get(
            station_id,
            (f"{station_id}_agent", f"{station_id.title()}Agent", "station_agent", f"Execute station {station_id} under V8 governance."),
        )
        agent_id = f"v8_{agent_slug}"
        descriptors.append(
            StationAgentDescriptor(
                agent_id=agent_id,
                station_id=station_id,
                agent_name=agent_name,
                role=role,
                goal=goal,
                agent_runtime_profile_ref=f"agent-runtime-profile://v8/{agent_id}",
                model_profile_ref=f"agent-model-profile://v8/{agent_id}",
                memory_policy_ref=f"agent-memory-policy://v8/{agent_id}/station-scoped",
                tool_policy_ref=f"agent-tool-policy://v8/{agent_id}/allowlist",
                skill_binding_refs=(f"agent-skill-binding://v8/{agent_id}/{role}",),
                mcp_binding_refs=_mcp_refs_for_station(agent_id, station_id),
                context_policy_ref=f"agent-context-policy://v8/{agent_id}/station-scoped",
                evidence_policy_ref=f"agent-evidence-policy://v8/{agent_id}/redacted",
                allowed_operations=_allowed_operations_for_station(station_id),
                forbidden_operations=tuple(sorted(DENIED_DEFAULT_OPERATIONS)),
                source_policy="source_agent_durable_mutation_denied",
            )
        )
    validation = validate_station_agent_registry(workflow_spec, descriptors)
    return StationAgentRegistry(
        registry_id=f"station_agent_registry_v8_{uuid4().hex[:12]}",
        workflow_spec_id=str(workflow_spec["metadata"]["workflow_spec_id"]),
        workflow_version_ref="workflow-version://v8/local-document-pilot",
        station_agent_descriptors=tuple(descriptors),
        workflow_explainer_agent_id="v8_workflow_explainer_agent",
        validation_result=validation,
    )


def validate_station_agent_registry(workflow_spec: dict[str, Any], descriptors: list[StationAgentDescriptor]) -> dict[str, Any]:
    """Validate station Agent coverage and required explainer Agent."""
    station_ids = {str(station["station_id"]) for station in workflow_spec.get("stations", [])}
    descriptor_station_ids = {descriptor.station_id for descriptor in descriptors}
    missing = sorted(station_ids - descriptor_station_ids)
    extra = sorted(descriptor_station_ids - station_ids)
    explainer = [descriptor for descriptor in descriptors if descriptor.role == "workflow_explainer"]
    status = "PASS" if not missing and not extra and explainer else "FAIL"
    return {
        "status": status,
        "station_count": len(station_ids),
        "agent_descriptor_count": len(descriptors),
        "missing_station_ids": missing,
        "extra_station_ids": extra,
        "workflow_explainer_agent_exists": bool(explainer),
        "source_agent_durable_mutation_denied": True,
    }


def create_agent_context_envelopes(
    registry: StationAgentRegistry,
    workflow_spec: dict[str, Any],
    runtime_result: dict[str, Any],
) -> list[StationAgentContextEnvelope]:
    """Create scoped context envelopes for all station Agents."""
    provider_ref = f"provider://{runtime_result.get('provider', {}).get('provider', 'unknown')}"
    workflow_ref = f"workflow-spec://{workflow_spec['metadata']['workflow_spec_id']}"
    envelopes: list[StationAgentContextEnvelope] = []
    for descriptor in registry.station_agent_descriptors:
        station = _station_by_id(workflow_spec, descriptor.station_id)
        envelopes.append(
            StationAgentContextEnvelope(
                context_envelope_id=f"context_envelope_v8_{uuid4().hex[:12]}",
                agent_id=descriptor.agent_id,
                station_id=descriptor.station_id,
                workflow_context_refs=(workflow_ref, provider_ref),
                upstream_artifact_refs=tuple(f"artifact-contract://{ref}" for ref in station.get("input_refs", [])),
                evidence_refs=(f"evidence://v8/{descriptor.station_id}",),
                memory_refs=(f"memory://v8/{descriptor.agent_id}/station-summary",),
                prompt_template_ref=f"prompt-template://v8/{descriptor.role}/v1",
                redaction_status="redacted",
                context_scope="station_scoped",
            )
        )
    return envelopes


def create_agent_invocation_evidence(
    registry: StationAgentRegistry,
    workflow_spec: dict[str, Any],
    runtime_result: dict[str, Any],
) -> list[AgentInvocationEvidence]:
    """Create redacted invocation evidence for all station Agents."""
    provider = runtime_result.get("provider", {})
    evidence: list[AgentInvocationEvidence] = []
    for descriptor in registry.station_agent_descriptors:
        station = _station_by_id(workflow_spec, descriptor.station_id)
        invocation_kind = "llm" if descriptor.station_id in {"per_folder_summary", "overview_summary"} else "tool_or_read_model"
        evidence.append(
            AgentInvocationEvidence(
                invocation_id=f"agent_invocation_v8_{uuid4().hex[:12]}",
                agent_id=descriptor.agent_id,
                station_id=descriptor.station_id,
                provider=str(provider.get("provider") or ("none" if invocation_kind != "llm" else "unknown")),
                model_ref=str(provider.get("model_ref") or ("not_llm" if invocation_kind != "llm" else "unknown")),
                provider_config_source=str(provider.get("provider_config_source") or "not_required"),
                prompt_template_ref=f"prompt-template://v8/{descriptor.role}/v1",
                input_artifact_refs=tuple(f"artifact-contract://{ref}" for ref in station.get("input_refs", [])),
                output_artifact_refs=tuple(f"artifact-contract://{ref}" for ref in station.get("output_refs", [])),
                redaction_status="redacted",
                correlation_id=f"corr_v8_{uuid4().hex[:12]}",
                request_id=f"req_v8_{uuid4().hex[:12]}",
                invocation_kind=invocation_kind,
            )
        )
    return evidence


def create_station_agent_run_results(
    registry: StationAgentRegistry,
    workflow_spec: dict[str, Any],
    runtime_result: dict[str, Any],
    invocation_evidence: list[AgentInvocationEvidence],
    capability_decisions: list[AgentCapabilityDecision],
) -> list[StationAgentRunResult]:
    """Create station Agent run results."""
    status = "PASS" if runtime_result.get("status") == "completed" else "BLOCKED"
    results: list[StationAgentRunResult] = []
    for descriptor in registry.station_agent_descriptors:
        station = _station_by_id(workflow_spec, descriptor.station_id)
        invocations = [item.invocation_id for item in invocation_evidence if item.station_id == descriptor.station_id]
        decisions = [item.decision_id for item in capability_decisions if item.station_id == descriptor.station_id]
        results.append(
            StationAgentRunResult(
                run_result_id=f"agent_run_result_v8_{uuid4().hex[:12]}",
                agent_id=descriptor.agent_id,
                station_id=descriptor.station_id,
                station_run_id=f"station-run-v8-{descriptor.station_id}",
                attempt_id=f"attempt-v8-{descriptor.station_id}-1",
                status=status,
                output_artifact_refs=tuple(f"artifact-contract://{ref}" for ref in station.get("output_refs", [])),
                quality_refs=("quality-report://v8/local-document",) if descriptor.station_id == "quality_check" else (),
                evidence_refs=(f"evidence://v8/{descriptor.station_id}",),
                llm_invocation_refs=tuple(invocations),
                tool_call_refs=(f"tool-call://v8/{descriptor.station_id}",),
                mcp_call_refs=(f"mcp-call://v8/{descriptor.station_id}",) if descriptor.mcp_binding_refs else (),
                capability_decision_refs=tuple(decisions),
                redaction_status="redacted",
            )
        )
    return results


def assert_no_sensitive_text(value: Any) -> None:
    """Fail if sensitive strings appear in evidence."""
    import json

    text = json.dumps(value, ensure_ascii=False)
    for term in SENSITIVE_TERMS:
        if term in text:
            raise AssertionError(f"sensitive term leaked: {term}")


def _allowed_operations_for_station(station_id: str) -> tuple[str, ...]:
    if station_id == "markdown_scan":
        return ("local_folder.read", "markdown.scan")
    if station_id in {"per_folder_summary", "overview_summary"}:
        return ("llm.summarize",)
    if station_id == "quality_check":
        return ("quality.evaluation.create",)
    if station_id == "runtime_report":
        return ("report.open",)
    if station_id == "evidence_record":
        return ("evidence.show",)
    return ("workflow.explain",)


def _mcp_refs_for_station(agent_id: str, station_id: str) -> tuple[str, ...]:
    if station_id == "markdown_scan":
        return (f"agent-mcp-binding://v8/{agent_id}/filesystem_readonly",)
    if station_id in {"quality_check", "runtime_report", "evidence_record"}:
        return (f"agent-mcp-binding://v8/{agent_id}/artifact_registry_readonly",)
    return ()


def _station_by_id(workflow_spec: dict[str, Any], station_id: str) -> dict[str, Any]:
    for station in workflow_spec.get("stations", []):
        if station.get("station_id") == station_id:
            return station
    return {"station_id": station_id, "input_refs": [], "output_refs": []}
