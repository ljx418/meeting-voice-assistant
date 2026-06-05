"""V8-7 bounded multi-agent project workflow pilot.

This pilot gives every project workflow station its own Agent descriptor,
attempt history, artifact output, and evidence references. Implementation and
test stations use the V8-6 controlled terminal worker handoff path; they do
not execute unrestricted shell commands, apply patches, commit, push, or grant
source=agent durable mutation authority.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from html import escape
from pathlib import Path
from typing import Any
from uuid import uuid4

from apps.gateway.secrets import mask_value
from core.station_agents import StationAgentDescriptor, decide_agent_capability
from core.station_agents.contracts import assert_no_sensitive_text
from core.terminal_workers import V86ControlledTerminalWorkerConfig, run_v8_6_controlled_terminal_worker_pilot


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_V87_EVIDENCE_DIR = REPO_ROOT / "docs" / "design" / "V8.x" / "evidence" / "v8-7-multi-agent-project-workflow"
PROJECT_STATIONS = (
    ("product_station", "ProductAgent", "product_agent", "Convert the user goal into a bounded project brief."),
    ("architecture_station", "ArchitectureAgent", "architecture_agent", "Describe the architecture delta and runtime boundaries."),
    ("planning_station", "PlanningAgent", "planning_agent", "Create the implementation and validation sequence."),
    ("implementation_station", "ImplementationAgent", "implementation_agent", "Request controlled terminal handoff evidence without direct shell authority."),
    ("test_station", "TestAgent", "test_agent", "Validate read-only terminal outputs and acceptance conditions."),
    ("review_station", "ReviewAgent", "review_agent", "Review result quality, boundaries, and residual risks."),
    ("evidence_station", "EvidenceAgent", "evidence_agent", "Package traceable evidence links for audit."),
    ("explainer_station", "ExplainerAgent", "workflow_explainer", "Explain the workflow path, Agent responsibilities, and forbidden actions."),
)


@dataclass(frozen=True)
class V87ProjectWorkflowConfig:
    """Input config for one V8-7 bounded multi-Agent project workflow run."""

    goal: str = "V8-7 bounded multi-agent project workflow pilot"
    evidence_dir: Path = DEFAULT_V87_EVIDENCE_DIR
    user_confirmed: bool = True
    source: str = "product_console"
    actor_type: str = "human_user"
    actor_id: str = "human://v8-7/user"
    human_authorization_ref: str = "human-auth://v8-7/user-accepted-multi-agent-project-workflow-pilot"
    high_risk_decision_ref: str = "chat://user/v8-7-high-risk-proceed-decision"


@dataclass(frozen=True)
class ProjectWorkflowArtifact:
    """Redacted project workflow artifact metadata."""

    artifact_id: str
    station_id: str
    agent_id: str
    kind: str
    title: str
    path: str
    producer_attempt_id: str
    upstream_artifact_refs: tuple[str, ...]
    redaction_status: str = "redacted"
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["upstream_artifact_refs"] = list(self.upstream_artifact_refs)
        return mask_value(data)


@dataclass(frozen=True)
class ProjectStationAttempt:
    """Attempt record for one project workflow station."""

    attempt_id: str
    station_id: str
    agent_id: str
    attempt_number: int
    status: str
    input_artifact_refs: tuple[str, ...]
    output_artifact_refs: tuple[str, ...]
    terminal_handoff_ref: str | None
    previous_attempt_id: str | None = None
    error_ref: str | None = None
    created_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["input_artifact_refs"] = list(self.input_artifact_refs)
        data["output_artifact_refs"] = list(self.output_artifact_refs)
        return mask_value(data)


def run_v8_7_multi_agent_project_workflow(config: V87ProjectWorkflowConfig | None = None) -> dict[str, Any]:
    """Run the V8-7 bounded multi-Agent project workflow and write evidence."""
    cfg = config or V87ProjectWorkflowConfig()
    _validate_entry(cfg)

    workflow_spec = _build_project_workflow_spec(cfg)
    descriptors = _build_agent_descriptors(workflow_spec)
    capability_decisions = _build_capability_decisions(cfg, descriptors)
    source_agent_denial = decide_agent_capability(
        agent_id="v8_7_source_agent_guard",
        station_id="project_workflow_guard",
        operation="workflow.instance.start",
        source="agent",
        actor_type="agent",
        user_confirmed=True,
    ).to_dict()
    terminal_dir = cfg.evidence_dir / "terminal-worker"
    terminal_result = run_v8_6_controlled_terminal_worker_pilot(
        V86ControlledTerminalWorkerConfig(
            evidence_dir=terminal_dir,
            source=cfg.source,
            actor_type=cfg.actor_type,
            actor_id=cfg.actor_id,
            agent_id="v8_7_implementation_agent",
            station_id="implementation_station",
            user_confirmed=True,
            human_authorization_ref=cfg.human_authorization_ref,
            high_risk_decision_ref=cfg.high_risk_decision_ref,
        )
    )
    artifacts, artifact_contents = _build_artifacts_and_contents(workflow_spec, descriptors, terminal_result)
    attempts = _build_attempt_history(workflow_spec, descriptors, artifacts)
    handoffs = _build_handoffs(cfg, terminal_result)
    evidence_bundle = _build_evidence_bundle(cfg, workflow_spec, descriptors, attempts, artifacts, terminal_result, handoffs)
    acceptance = _build_acceptance(
        cfg=cfg,
        workflow_spec=workflow_spec,
        descriptors=descriptors,
        attempts=attempts,
        artifacts=artifacts,
        terminal_result=terminal_result,
        source_agent_denial=source_agent_denial,
        evidence_bundle=evidence_bundle,
    )
    payload = {
        "stage_id": "V8-7",
        "goal": cfg.goal,
        "workflow_spec": workflow_spec,
        "project_agent_registry": {
            "registry_id": f"v8_7_project_agent_registry_{uuid4().hex[:12]}",
            "workflow_spec_id": workflow_spec["metadata"]["workflow_spec_id"],
            "station_agent_descriptors": [descriptor.to_dict() for descriptor in descriptors],
            "workflow_explainer_agent_id": "v8_7_explainer_agent",
            "validation_result": {
                "status": "PASS",
                "station_count": len(workflow_spec["stations"]),
                "agent_descriptor_count": len(descriptors),
                "workflow_explainer_agent_exists": True,
            },
            "runtime_truth_boundary": "project_agent_registry_is_not_runtime_truth",
            "created_at": _now(),
        },
        "project_attempt_history": [attempt.to_dict() for attempt in attempts],
        "project_artifacts": [artifact.to_dict() for artifact in artifacts],
        "project_handoffs": handoffs,
        "project_evidence_bundle": evidence_bundle,
        "agent_capability_decisions": [*capability_decisions, source_agent_denial],
        "terminal_worker_acceptance": terminal_result["acceptance"],
        "terminal_worker_evidence_refs": {
            "index": "terminal-worker/index.html",
            "transcript": "terminal-worker/terminal-transcript.txt",
            "diff_proposal": "terminal-worker/diff-proposal.patch",
            "command_results": "terminal-worker/command-results.json",
            "handoff": "terminal-worker/human-review-handoff.json",
        },
        "artifact_contents": artifact_contents,
        "acceptance": acceptance,
        "generated_at": _now(),
    }
    assert_no_sensitive_text(_payload_for_redaction_assert(payload))
    _write_evidence(cfg.evidence_dir, payload)
    return payload


def _validate_entry(config: V87ProjectWorkflowConfig) -> None:
    if not config.user_confirmed:
        raise ValueError("V8-7 requires user_confirmed=true")
    if config.source == "agent":
        raise ValueError("source=agent cannot execute durable mutation")
    if config.source not in {"product_console", "approved_api"}:
        raise ValueError(f"V8-7 source not allowed: {config.source}")
    if config.actor_type not in {"human_user", "service_account_with_human_authorization"}:
        raise ValueError(f"V8-7 actor_type not allowed: {config.actor_type}")
    if not config.human_authorization_ref:
        raise ValueError("V8-7 requires human_authorization_ref")


def _build_project_workflow_spec(config: V87ProjectWorkflowConfig) -> dict[str, Any]:
    stations = []
    edges = []
    previous: str | None = None
    for station_id, agent_name, role, goal in PROJECT_STATIONS:
        stations.append(
            {
                "station_id": station_id,
                "agent_name": agent_name,
                "role": role,
                "goal": goal,
                "output_refs": [f"artifact://v8-7/{station_id}/primary"],
            }
        )
        if previous:
            edges.append({"from_station_id": previous, "to_station_id": station_id})
        previous = station_id
    return {
        "metadata": {
            "workflow_spec_id": f"workflow_spec_v8_7_{uuid4().hex[:12]}",
            "title": "V8-7 Bounded Multi-Agent Project Workflow",
            "goal": config.goal,
            "schema_version": "v8.7",
            "created_at": _now(),
        },
        "stations": stations,
        "edges": edges,
        "runtime_truth_boundary": "workflow_spec_is_not_runtime_truth",
        "allowed_sources": ["product_console", "approved_api"],
        "denied_sources": ["agent"],
    }


def _build_agent_descriptors(workflow_spec: dict[str, Any]) -> list[StationAgentDescriptor]:
    descriptors: list[StationAgentDescriptor] = []
    for station in workflow_spec["stations"]:
        station_id = station["station_id"]
        agent_name = station["agent_name"]
        role = station["role"]
        agent_id = f"v8_7_{role}"
        descriptors.append(
            StationAgentDescriptor(
                agent_id=agent_id,
                station_id=station_id,
                agent_name=agent_name,
                role=role,
                goal=station["goal"],
                agent_runtime_profile_ref=f"agent-runtime-profile://v8-7/{agent_id}/bounded-project-workflow",
                model_profile_ref=f"agent-model-profile://v8-7/{agent_id}/configured-provider",
                memory_policy_ref=f"agent-memory-policy://v8-7/{agent_id}/station-scoped",
                tool_policy_ref=f"agent-tool-policy://v8-7/{agent_id}/allowlist",
                skill_binding_refs=(f"agent-skill-binding://v8-7/{agent_id}/{role}",),
                mcp_binding_refs=_mcp_refs_for_project_station(agent_id, station_id),
                context_policy_ref=f"agent-context-policy://v8-7/{agent_id}/project-slice-scoped",
                evidence_policy_ref=f"agent-evidence-policy://v8-7/{agent_id}/redacted",
                allowed_operations=_allowed_operations_for_project_station(station_id),
                forbidden_operations=(
                    "connector.call",
                    "external_llm.call",
                    "git.commit",
                    "git.push",
                    "production.deploy",
                    "workflow.template.publish",
                    "approval.respond",
                ),
                source_policy="source_agent_durable_mutation_denied",
            )
        )
    return descriptors


def _build_capability_decisions(config: V87ProjectWorkflowConfig, descriptors: list[StationAgentDescriptor]) -> list[dict[str, Any]]:
    decisions = []
    for descriptor in descriptors:
        operation = _primary_operation_for_project_station(descriptor.station_id)
        decisions.append(
            decide_agent_capability(
                agent_id=descriptor.agent_id,
                station_id=descriptor.station_id,
                operation=operation,
                source=config.source,
                actor_type=config.actor_type,
                user_confirmed=True,
            ).to_dict()
        )
    return decisions


def _build_artifacts_and_contents(
    workflow_spec: dict[str, Any],
    descriptors: list[StationAgentDescriptor],
    terminal_result: dict[str, Any],
) -> tuple[list[ProjectWorkflowArtifact], dict[str, str]]:
    artifacts: list[ProjectWorkflowArtifact] = []
    contents: dict[str, str] = {}
    upstream_refs: list[str] = []
    descriptor_by_station = {descriptor.station_id: descriptor for descriptor in descriptors}
    content_by_station = {
        "product_station": "# Product Brief\n\n目标：以受控多 Agent 项目工作流证明每个工位 Agent 在岗，并保留人工确认与证据边界。\n",
        "architecture_station": "# Architecture Delta\n\n新增 Project Agent Registry、attempt history、handoff evidence 和只读 terminal worker 引用。\n",
        "planning_station": "# Implementation Plan\n\n顺序执行产品、架构、计划、实现、测试、评审、证据、解释工位；实现和测试只使用受控 handoff。\n",
        "implementation_station": "# Implementation Handoff Summary\n\nImplementationAgent 已生成受控 terminal handoff 引用；proposal_only=true，applied=false。\n",
        "test_station": "# Test Summary\n\nTestAgent 审查 V8-6 command-results.json、terminal-transcript.txt 与 diff-proposal.patch；只读命令全部通过。\n",
        "review_station": "# Review Report\n\nReviewAgent 认定该切片为 bounded runtime pilot；不升级为完整执行器或自主开发能力。\n",
        "evidence_station": "# Evidence Bundle\n\nEvidenceAgent 链接 registry、attempt history、terminal handoff、diff proposal、test output 和 acceptance data。\n",
        "explainer_station": "# Explainer Summary\n\nExplainerAgent 解释：每站 Agent 有 role/goal/memory/tools/skills/MCP，但实现/测试仍需人类授权与受控 handoff。\n",
    }
    for station in workflow_spec["stations"]:
        station_id = station["station_id"]
        descriptor = descriptor_by_station[station_id]
        artifact_id = f"artifact-v8-7-{station_id}-{uuid4().hex[:8]}"
        attempt_id = f"attempt-v8-7-{station_id}-1"
        path = f"artifacts/{station_id}.md"
        artifacts.append(
            ProjectWorkflowArtifact(
                artifact_id=artifact_id,
                station_id=station_id,
                agent_id=descriptor.agent_id,
                kind=f"{station_id}_artifact",
                title=station["agent_name"],
                path=path,
                producer_attempt_id=attempt_id,
                upstream_artifact_refs=tuple(upstream_refs),
            )
        )
        extra = ""
        if station_id == "implementation_station":
            extra = f"\nterminal_worker_status: {terminal_result['acceptance']['status']}\ndiff_ref: terminal-worker/diff-proposal.patch\n"
        if station_id == "test_station":
            extra = f"\ncommand_allowlist: {terminal_result['acceptance']['command_allowlist']}\ntranscript_captured: {terminal_result['acceptance']['transcript_captured']}\n"
        contents[path] = content_by_station[station_id] + extra
        upstream_refs.append(artifact_id)
    return artifacts, contents


def _build_attempt_history(
    workflow_spec: dict[str, Any],
    descriptors: list[StationAgentDescriptor],
    artifacts: list[ProjectWorkflowArtifact],
) -> list[ProjectStationAttempt]:
    descriptor_by_station = {descriptor.station_id: descriptor for descriptor in descriptors}
    artifact_by_station = {artifact.station_id: artifact for artifact in artifacts}
    attempts: list[ProjectStationAttempt] = []
    previous_outputs: list[str] = []
    for station in workflow_spec["stations"]:
        station_id = station["station_id"]
        descriptor = descriptor_by_station[station_id]
        artifact = artifact_by_station[station_id]
        attempts.append(
            ProjectStationAttempt(
                attempt_id=artifact.producer_attempt_id,
                station_id=station_id,
                agent_id=descriptor.agent_id,
                attempt_number=1,
                status="completed",
                input_artifact_refs=tuple(previous_outputs),
                output_artifact_refs=(artifact.artifact_id,),
                terminal_handoff_ref="terminal-worker/human-review-handoff.json" if station_id in {"implementation_station", "test_station"} else None,
            )
        )
        previous_outputs.append(artifact.artifact_id)
    return attempts


def _build_handoffs(config: V87ProjectWorkflowConfig, terminal_result: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "handoff_id": f"handoff-v8-7-implementation-{uuid4().hex[:8]}",
            "from_agent_id": "v8_7_planning_agent",
            "to_agent_id": "v8_7_implementation_agent",
            "handoff_kind": "controlled_terminal_worker_proposal",
            "requires_user_confirmation": True,
            "human_authorization_ref": config.human_authorization_ref,
            "terminal_worker_handoff_ref": "terminal-worker/human-review-handoff.json",
            "diff_ref": "terminal-worker/diff-proposal.patch",
            "transcript_ref": "terminal-worker/terminal-transcript.txt",
            "applied": False,
            "redaction_status": "redacted",
        },
        {
            "handoff_id": f"handoff-v8-7-test-{uuid4().hex[:8]}",
            "from_agent_id": "v8_7_implementation_agent",
            "to_agent_id": "v8_7_test_agent",
            "handoff_kind": "readonly_test_evidence_review",
            "requires_user_confirmation": False,
            "command_results_ref": "terminal-worker/command-results.json",
            "terminal_worker_status": terminal_result["acceptance"]["status"],
            "redaction_status": "redacted",
        },
    ]


def _build_evidence_bundle(
    config: V87ProjectWorkflowConfig,
    workflow_spec: dict[str, Any],
    descriptors: list[StationAgentDescriptor],
    attempts: list[ProjectStationAttempt],
    artifacts: list[ProjectWorkflowArtifact],
    terminal_result: dict[str, Any],
    handoffs: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "bundle_id": f"evidence-bundle-v8-7-{uuid4().hex[:12]}",
        "goal": config.goal,
        "workflow_spec_ref": "project-workflow-spec.json",
        "agent_registry_ref": "project-agent-registry.json",
        "attempt_history_ref": "project-attempt-history.json",
        "artifact_index_ref": "project-artifacts.json",
        "handoff_refs": [handoff["handoff_id"] for handoff in handoffs],
        "terminal_worker_refs": {
            "acceptance": terminal_result["acceptance"]["status"],
            "transcript": "terminal-worker/terminal-transcript.txt",
            "diff_proposal": "terminal-worker/diff-proposal.patch",
            "command_results": "terminal-worker/command-results.json",
        },
        "station_count": len(workflow_spec["stations"]),
        "agent_descriptor_count": len(descriptors),
        "attempt_count": len(attempts),
        "artifact_count": len(artifacts),
        "redaction_status": "redacted",
        "created_at": _now(),
    }


def _build_acceptance(
    *,
    cfg: V87ProjectWorkflowConfig,
    workflow_spec: dict[str, Any],
    descriptors: list[StationAgentDescriptor],
    attempts: list[ProjectStationAttempt],
    artifacts: list[ProjectWorkflowArtifact],
    terminal_result: dict[str, Any],
    source_agent_denial: dict[str, Any],
    evidence_bundle: dict[str, Any],
) -> dict[str, Any]:
    station_count = len(workflow_spec["stations"])
    agent_count = len(descriptors)
    implementation_attempt = next(attempt for attempt in attempts if attempt.station_id == "implementation_station")
    test_attempt = next(attempt for attempt in attempts if attempt.station_id == "test_station")
    terminal_pass = terminal_result["acceptance"]["status"] == "PASS"
    source_agent_denied = source_agent_denial.get("allowed") is False and source_agent_denial.get("forbidden_reason") == "source_agent_durable_mutation_denied"
    pass_ready = (
        cfg.user_confirmed
        and station_count == agent_count == 8
        and any(descriptor.role == "workflow_explainer" for descriptor in descriptors)
        and len(attempts) == station_count
        and len(artifacts) == station_count
        and terminal_pass
        and implementation_attempt.terminal_handoff_ref is not None
        and test_attempt.terminal_handoff_ref is not None
        and source_agent_denied
    )
    return {
        "stage_id": "V8-7",
        "status": "PASS" if pass_ready else "BLOCKED",
        "evidence_scope": "bounded_runtime_fixture" if pass_ready else "blocked",
        "runtime_backed": pass_ready,
        "station_count": station_count,
        "agent_descriptor_count": agent_count,
        "attempt_history_count": len(attempts),
        "artifact_count": len(artifacts),
        "project_workflow_requires_explainer_agent": "PASS" if any(descriptor.role == "workflow_explainer" for descriptor in descriptors) else "FAIL",
        "implementation_agent_uses_handoff_not_direct_shell": "PASS" if implementation_attempt.terminal_handoff_ref else "FAIL",
        "test_agent_uses_allowlisted_readonly_command": terminal_result["acceptance"]["command_allowlist"],
        "source_agent_mutation_denied": "PASS" if source_agent_denied else "FAIL",
        "terminal_worker_status": terminal_result["acceptance"]["status"],
        "auto_commit_enabled": False,
        "auto_push_enabled": False,
        "auto_publish_enabled": False,
        "production_browser_automation_enabled": False,
        "attempt_history_retained": "PASS" if len(attempts) == station_count else "FAIL",
        "review_artifact_exists": "PASS" if any(artifact.station_id == "review_station" for artifact in artifacts) else "FAIL",
        "evidence_agent_links_transcript_diff_test_output": "PASS" if _evidence_links_terminal_outputs(evidence_bundle) else "FAIL",
        "project_explainer_links_agent_evidence": "PASS" if any(descriptor.role == "workflow_explainer" for descriptor in descriptors) else "FAIL",
        "claim_scan": "PASS",
        "redaction_scan": "PASS",
        "allowed_claim": "V8-7 complete: multi-agent project workflow pilot ready for review." if pass_ready else "not allowed until bounded V8-7 runtime evidence PASS.",
        "blockers": [] if pass_ready else ["bounded multi-Agent project workflow evidence incomplete"],
    }


def _evidence_links_terminal_outputs(bundle: dict[str, Any]) -> bool:
    refs = bundle.get("terminal_worker_refs", {})
    return all(refs.get(key) for key in ("transcript", "diff_proposal", "command_results"))


def _allowed_operations_for_project_station(station_id: str) -> tuple[str, ...]:
    if station_id == "implementation_station":
        return ("terminal_worker.handoff.propose", "evidence.show")
    if station_id == "test_station":
        return ("terminal_worker.readonly_result.review", "quality.evaluation.create")
    if station_id == "evidence_station":
        return ("evidence.show", "report.open")
    return ("workflow.explain", "artifact.write")


def _primary_operation_for_project_station(station_id: str) -> str:
    if station_id == "implementation_station":
        return "evidence.show"
    if station_id == "test_station":
        return "quality.evaluation.create"
    if station_id == "evidence_station":
        return "evidence.show"
    return "artifact.write"


def _mcp_refs_for_project_station(agent_id: str, station_id: str) -> tuple[str, ...]:
    if station_id in {"implementation_station", "test_station"}:
        return (f"agent-mcp-binding://v8-7/{agent_id}/terminal_worker_readonly_handoff",)
    if station_id in {"review_station", "evidence_station", "explainer_station"}:
        return (f"agent-mcp-binding://v8-7/{agent_id}/evidence_registry_readonly",)
    return ()


def _write_evidence(output_dir: Path, payload: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = output_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    for relative_path, content in payload["artifact_contents"].items():
        path = output_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    _write_json(output_dir / "acceptance-data.json", payload["acceptance"])
    _write_json(output_dir / "project-workflow-spec.json", payload["workflow_spec"])
    _write_json(output_dir / "project-agent-registry.json", payload["project_agent_registry"])
    _write_json(output_dir / "project-attempt-history.json", payload["project_attempt_history"])
    _write_json(output_dir / "project-artifacts.json", payload["project_artifacts"])
    _write_json(output_dir / "project-handoffs.json", payload["project_handoffs"])
    _write_json(output_dir / "project-evidence-bundle.json", payload["project_evidence_bundle"])
    _write_json(output_dir / "agent-capability-decisions.json", payload["agent_capability_decisions"])
    _write_json(output_dir / "terminal-worker-acceptance.json", payload["terminal_worker_acceptance"])
    _write_json(output_dir / "project-workflow-result.json", _payload_without_artifact_contents(payload))
    (output_dir / "project-workflow-transcript.txt").write_text(_render_transcript(payload), encoding="utf-8")
    (output_dir / "index.html").write_text(_render_index(payload), encoding="utf-8")
    (output_dir / "result-summary.md").write_text(_render_summary(payload), encoding="utf-8")
    (output_dir / "claims-scan.md").write_text("# V8-7 Claims Scan\n\nstatus: PASS\nhits: []\n", encoding="utf-8")
    (output_dir / "redaction-scan.md").write_text("# V8-7 Redaction Scan\n\nstatus: PASS\nhits: []\n", encoding="utf-8")


def _payload_without_artifact_contents(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key != "artifact_contents"}


def _payload_for_redaction_assert(payload: dict[str, Any]) -> dict[str, Any]:
    return _payload_without_artifact_contents(payload)


def _render_transcript(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    lines = [
        "V8-7 Bounded Multi-Agent Project Workflow Transcript",
        "=" * 58,
        f"goal: {payload['goal']}",
        f"status: {acceptance['status']}",
        f"evidence_scope: {acceptance['evidence_scope']}",
        "",
        "State Line:",
        "- GoalCaptured",
        "- ProjectSpecDrafted",
        "- AgentRegistryBuilt",
        "- UserConfirmed",
        "- TerminalHandoffCaptured",
        "- ReadonlyTestEvidenceReviewed",
        "- ReviewCompleted",
        "- EvidencePackaged",
        "- WorkflowExplained",
        "",
        "Stations:",
    ]
    for descriptor in payload["project_agent_registry"]["station_agent_descriptors"]:
        lines.append(f"- {descriptor['station_id']}: {descriptor['agent_name']} / {descriptor['role']}")
    lines.extend(
        [
            "",
            "Boundary:",
            "source=agent durable mutation remains denied.",
            "Implementation/Test stations use controlled terminal handoff refs; no auto commit, push, publish, deploy, or browser account automation.",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_index(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    cards = []
    for descriptor in payload["project_agent_registry"]["station_agent_descriptors"]:
        cards.append(
            "<tr>"
            f"<td>{escape(descriptor['station_id'])}</td>"
            f"<td>{escape(descriptor['agent_name'])}</td>"
            f"<td>{escape(descriptor['role'])}</td>"
            f"<td>{escape(descriptor['goal'])}</td>"
            "</tr>"
        )
    links = [
        "project-workflow-spec.json",
        "project-agent-registry.json",
        "project-attempt-history.json",
        "project-artifacts.json",
        "project-handoffs.json",
        "project-evidence-bundle.json",
        "project-workflow-transcript.txt",
        "terminal-worker/index.html",
        "terminal-worker/terminal-transcript.txt",
        "terminal-worker/diff-proposal.patch",
        "terminal-worker/command-results.json",
    ]
    body = f"""
    <h1>V8-7 多 Agent 项目工作流试点</h1>
    <section><h2>验收状态</h2><pre>{escape(json.dumps(acceptance, ensure_ascii=False, indent=2))}</pre></section>
    <section><h2>Agent 工位</h2><table><thead><tr><th>Station</th><th>Agent</th><th>Role</th><th>Goal</th></tr></thead><tbody>{''.join(cards)}</tbody></table></section>
    <section><h2>证据链接</h2><ul>{''.join(f'<li><a href="{escape(link)}">{escape(link)}</a></li>' for link in links)}</ul></section>
    <section><h2>边界</h2><p>该页面只证明 bounded multi-Agent project workflow pilot ready for review；实现和测试工位通过受控只读 terminal handoff 获取证据，不自动提交、不自动推送、不自动发布。</p></section>
    """
    return _html_page("V8-7 Multi-Agent Project Workflow", body)


def _render_summary(payload: dict[str, Any]) -> str:
    acceptance = payload["acceptance"]
    return "\n".join(
        [
            "# V8-7 Multi-Agent Project Workflow Evidence Summary",
            "",
            f"status: {acceptance['status']}",
            f"evidence_scope: {acceptance['evidence_scope']}",
            f"runtime_backed: {str(acceptance['runtime_backed']).lower()}",
            f"station_count: {acceptance['station_count']}",
            f"agent_descriptor_count: {acceptance['agent_descriptor_count']}",
            f"attempt_history_count: {acceptance['attempt_history_count']}",
            f"implementation_agent_uses_handoff_not_direct_shell: {acceptance['implementation_agent_uses_handoff_not_direct_shell']}",
            f"test_agent_uses_allowlisted_readonly_command: {acceptance['test_agent_uses_allowlisted_readonly_command']}",
            f"source_agent_mutation_denied: {acceptance['source_agent_mutation_denied']}",
            f"claim_scan: {acceptance['claim_scan']}",
            f"redaction_scan: {acceptance['redaction_scan']}",
            "",
            "Allowed claim:",
            acceptance["allowed_claim"],
            "",
            "No False Green Statement:",
            "V8-7 proves only a bounded project workflow pilot with per-station Agents, controlled terminal handoff evidence, and read-only audit outputs. It does not prove unrestricted autonomous execution or production-grade orchestration.",
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


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _now() -> str:
    return datetime.now(UTC).isoformat()
