"""V4.x unified experience read-model helpers.

This module is intentionally read-only. It derives UX projections and action
availability from supplied state labels; it does not write workflow runtime
objects or execute operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


MUTATION_OPERATIONS = {
    "workflow.patch.apply",
    "workflow.template.publish",
    "workflow.instance.start",
    "station.rerun",
    "approval.respond",
    "context.update",
}

READ_ONLY_OPERATIONS = {"evidence.show", "report.open", "drawio.open"}

PROPOSAL_OPERATIONS = {"workflow.spec.generate", "workflow.patch.propose", "handoff.open"}

ALLOWED_OPERATIONS = MUTATION_OPERATIONS | READ_ONLY_OPERATIONS | PROPOSAL_OPERATIONS

WORKFLOW_TRANSITIONS = {
    "Idle": {"IntentCaptured"},
    "IntentCaptured": {"SpecDrafted"},
    "SpecDrafted": {"SchemaValidated"},
    "SchemaValidated": {"DiffReady"},
    "DiffReady": {"AwaitingConfirmation"},
    "AwaitingConfirmation": {"DraftApplied", "Published", "RunReady", "RerunRequested"},
    "DraftApplied": {"Published"},
    "Published": {"RunReady"},
    "RunReady": {"Running"},
    "Running": {"Completed", "Failed", "Blocked"},
    "Failed": {"Recoverable"},
    "Recoverable": {"RerunRequested"},
    "RerunRequested": {"Rerunning"},
    "Rerunning": {"Running", "Completed", "Failed"},
    "Completed": {"Reviewed"},
    "Reviewed": {"Archived"},
}

MISSION_CONSOLE_CREATE_FLOW = (
    "IntentCaptured",
    "SpecDrafted",
    "SchemaValidated",
    "DiffReady",
    "AwaitingConfirmation",
)


@dataclass(frozen=True)
class AvailableAction:
    """Read-model action visible to workflow heads."""

    action_id: str
    operation: str
    requires_user_confirmation: bool
    agent_executable: bool
    risk_flags: tuple[str, ...] = ()
    policy_decision: str = "read_only"

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "operation": self.operation,
            "requires_user_confirmation": self.requires_user_confirmation,
            "agent_executable": self.agent_executable,
            "risk_flags": list(self.risk_flags),
            "policy_decision": self.policy_decision,
        }


@dataclass(frozen=True)
class ExperienceStateProjection:
    """Shared UX projection for Mission Console, reports, review, and evidence."""

    workflow_state: str
    station_states: tuple[dict[str, Any], ...] = ()
    evidence_state: str = "NoEvidence"
    available_actions: tuple[AvailableAction, ...] = ()
    blocked_actions: tuple[str, ...] = ()
    source_refs: tuple[str, ...] = ()
    refresh_generation: int = 1
    stale_reasons: tuple[str, ...] = ()
    read_model_only: bool = True
    runtime_truth_boundary: str = (
        "ExperienceStateProjection is a UX read model and must not write "
        "WorkflowDraft, WorkflowVersion, WorkflowInstance, or StationRun."
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_state": self.workflow_state,
            "station_states": list(self.station_states),
            "evidence_state": self.evidence_state,
            "available_actions": [action.to_dict() for action in self.available_actions],
            "blocked_actions": list(self.blocked_actions),
            "source_refs": list(self.source_refs),
            "refresh_generation": self.refresh_generation,
            "stale_reasons": list(self.stale_reasons),
            "read_model_only": self.read_model_only,
            "runtime_truth_boundary": self.runtime_truth_boundary,
        }


def resolve_available_action(operation: str, *, source: str = "mission_console") -> AvailableAction:
    """Resolve operation policy for a visible action."""
    if operation not in ALLOWED_OPERATIONS:
        return AvailableAction(
            action_id=f"blocked:{operation}",
            operation=operation,
            requires_user_confirmation=False,
            agent_executable=False,
            risk_flags=("unknown_operation",),
            policy_decision="blocked",
        )

    if operation in MUTATION_OPERATIONS:
        return AvailableAction(
            action_id=f"confirm:{operation}",
            operation=operation,
            requires_user_confirmation=True,
            agent_executable=False,
            risk_flags=("durable_mutation",),
            policy_decision="blocked" if source == "agent" else "user_confirmed_only",
        )

    if operation in PROPOSAL_OPERATIONS:
        return AvailableAction(
            action_id=f"proposal:{operation}",
            operation=operation,
            requires_user_confirmation=False,
            agent_executable=True,
            risk_flags=(),
            policy_decision="proposal_only" if operation != "handoff.open" else "handoff_only",
        )

    return AvailableAction(
        action_id=f"read:{operation}",
        operation=operation,
        requires_user_confirmation=False,
        agent_executable=True,
        risk_flags=(),
        policy_decision="read_only",
    )


def validate_transition(current_state: str, next_state: str) -> bool:
    """Return whether a workflow-level UX transition is allowed."""
    return next_state in WORKFLOW_TRANSITIONS.get(current_state, set())


def build_experience_state_projection(
    *,
    workflow_state: str,
    station_states: list[dict[str, Any]] | None = None,
    evidence_state: str = "NoEvidence",
    operations: list[str] | None = None,
    source: str = "mission_console",
    source_refs: list[str] | None = None,
    refresh_generation: int = 1,
    stale_reasons: list[str] | None = None,
) -> ExperienceStateProjection:
    """Build a read-only UX projection from supplied DTO refs."""
    actions = tuple(resolve_available_action(operation, source=source) for operation in (operations or []))
    blocked = tuple(action.operation for action in actions if action.policy_decision == "blocked")
    return ExperienceStateProjection(
        workflow_state=workflow_state,
        station_states=tuple(station_states or ()),
        evidence_state=evidence_state,
        available_actions=actions,
        blocked_actions=blocked,
        source_refs=tuple(source_refs or ()),
        refresh_generation=refresh_generation,
        stale_reasons=tuple(stale_reasons or ()),
    )


def build_mission_console_projection(
    *,
    workflow_state: str = "AwaitingConfirmation",
    source_refs: list[str] | None = None,
    refresh_generation: int = 1,
    stale_reasons: list[str] | None = None,
) -> ExperienceStateProjection:
    """Build the shared projection used by the TUI Mission Console panel."""
    return build_experience_state_projection(
        workflow_state=workflow_state,
        evidence_state="EvidencePending" if workflow_state != "EvidenceReady" else "EvidenceReady",
        operations=[
            "workflow.patch.apply",
            "workflow.template.publish",
            "workflow.instance.start",
            "station.rerun",
            "evidence.show",
            "report.open",
            "drawio.open",
        ],
        source="mission_console",
        source_refs=source_refs
        or [
            "workflow_spec:v4_2_headless_local_markdown_summary",
            "report:workflow_board.html",
            "evidence:operation-evidence.json",
        ],
        refresh_generation=refresh_generation,
        stale_reasons=stale_reasons,
    )


def render_tui_state_timeline(projection: ExperienceStateProjection) -> str:
    """Render a compact text timeline for TUI/command-palette surfaces."""
    states = list(MISSION_CONSOLE_CREATE_FLOW)
    if projection.workflow_state not in states:
        states.append(projection.workflow_state)
    lines = [
        "Experience State Projection / 体验状态投影",
        f"current_state={projection.workflow_state}",
        f"refresh_generation={projection.refresh_generation}",
        f"read_model_only={str(projection.read_model_only).lower()}",
        "timeline:",
    ]
    for state in states:
        marker = "●" if state == projection.workflow_state else "○"
        lines.append(f"  {marker} {state}")
    if projection.stale_reasons:
        lines.append("stale_reasons:")
        lines.extend(f"  - {reason}" for reason in projection.stale_reasons)
    lines.append("available_actions:")
    for action in projection.available_actions:
        label = "requires_user_confirmation" if action.requires_user_confirmation else "read_or_proposal"
        lines.append(
            f"  - {action.operation} policy={action.policy_decision} "
            f"agent_executable={str(action.agent_executable).lower()} {label}"
        )
    if projection.source_refs:
        lines.append("source_refs:")
        lines.extend(f"  - {ref}" for ref in projection.source_refs)
    lines.append("runtime_truth_boundary=read_model_only")
    return "\n".join(lines) + "\n"


def build_review_action(
    *,
    operation: str,
    source: str,
    actor_type: str,
    risk_flags: list[str] | None = None,
) -> dict[str, Any]:
    """Build a Review Console action contract without executing it."""
    action = resolve_available_action(operation, source=source)
    return {
        "operation": operation,
        "source": source,
        "actor_type": actor_type,
        "requires_user_confirmation": action.requires_user_confirmation,
        "policy_decision": action.policy_decision,
        "risk_flags": risk_flags or list(action.risk_flags),
        "operation_executed": False,
    }
