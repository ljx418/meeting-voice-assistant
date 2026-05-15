"""Session runtime pool for the harnessOS gateway."""

from __future__ import annotations

import asyncio
import inspect
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Callable, Dict, Optional

from apps.gateway.approvals import ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.connector_execution import ConnectorExecutionRuntime
from apps.gateway.connectors import ConnectorRegistry
from apps.gateway.policies import PolicyEvaluator
from apps.gateway.retries import RetryStore
from apps.gateway.traces import TraceStore
from apps.gateway.workflows import LeadOrchestrator, WorkflowContext, build_default_orchestrator
from core.apps import AppRegistry, ScopeContext, build_default_app_registry
from core.packs import PackRegistry, build_default_pack_registry
from core.services import CoreAppService
from core.stores import CoreSQLiteStore
from core.runtime_adapter import (
    OpenHarnessRuntimeAdapter,
    RuntimeAdapter,
    RuntimeGovernanceContext,
    RuntimeHandle,
    SimpleRuntimeAdapter,
)
from tools import get_builtin_tools
from tools.policy_guard import tool_input_hash

from apps.gateway.protocol import GatewayEvent, TurnResult, new_id
from apps.gateway.storage import GatewaySessionStore


AgentFactory = Callable[[str], Any]
RuntimeBundleFactory = Callable[[str], Any]


@dataclass
class RuntimeSession:
    """Runtime state owned by one gateway session."""

    session_id: str
    model: str
    app_id: str = "default"
    project_id: Optional[str] = None
    workspace_id: Optional[str] = None
    agent: Any = None
    bundle: Any = None
    handle: Optional[RuntimeHandle] = None
    adapter: Optional[RuntimeAdapter] = None
    backend: str = "simple"
    created_at: datetime = field(default_factory=datetime.now)
    last_active_at: datetime = field(default_factory=datetime.now)
    state: str = "idle"
    interrupted: bool = False


@dataclass
class ActiveTurn:
    """Runtime task currently serving one session turn."""

    turn_id: str
    task: asyncio.Task[Any]
    cancel_requested: bool = False


class GatewayRuntimePool:
    """Maintain model runtimes by gateway session id."""

    def __init__(
        self,
        *,
        model: Optional[str] = None,
        agent_factory: Optional[AgentFactory] = None,
        runtime_factory: Optional[RuntimeBundleFactory] = None,
        runtime_backend: str = "auto",
        store: Optional[GatewaySessionStore] = None,
        meeting_workflow: Optional[Any] = None,
        artifact_registry: Optional[ArtifactRegistry] = None,
        trace_store: Optional[TraceStore] = None,
        approval_store: Optional[ApprovalStore] = None,
        policy_evaluator: Optional[PolicyEvaluator] = None,
        retry_store: Optional[RetryStore] = None,
        orchestrator: Optional[LeadOrchestrator] = None,
        pack_registry: Optional[PackRegistry] = None,
        app_registry: Optional[AppRegistry] = None,
        connector_registry: Optional[ConnectorRegistry] = None,
        core_store: Optional[CoreSQLiteStore] = None,
        core_service: Optional[CoreAppService] = None,
    ) -> None:
        self._model = model or _default_model()
        self._agent_factory = agent_factory or self._create_default_agent
        self._runtime_factory = runtime_factory
        self._runtime_backend = runtime_backend
        self._store = store or GatewaySessionStore()
        self._artifact_registry = artifact_registry or getattr(meeting_workflow, "artifact_registry", None) or ArtifactRegistry()
        self._trace_store = trace_store or TraceStore()
        self._approval_store = approval_store or ApprovalStore()
        self._policy_evaluator = policy_evaluator or PolicyEvaluator()
        self._retry_store = retry_store or RetryStore()
        self._app_registry = app_registry or build_default_app_registry()
        self._pack_registry = pack_registry or build_default_pack_registry(app_registry=self._app_registry)
        resolved_core_store = core_store
        if resolved_core_store is None and core_service is None and store is not None:
            resolved_core_store = CoreSQLiteStore(self._store.root / "core.sqlite3")
        self._core_service = core_service or CoreAppService(store=resolved_core_store)
        self._core_store = self._core_service.store
        self._connector_registry = connector_registry or ConnectorRegistry(core_service=self._core_service)
        self._connector_execution_runtime = ConnectorExecutionRuntime(
            connector_registry=self._connector_registry,
            core_service=self._core_service,
            artifact_registry=self._artifact_registry,
            trace_store=self._trace_store,
            approval_store=self._approval_store,
        )
        self._meeting_workflow = meeting_workflow or _build_default_meeting_workflow(
            artifact_registry=self._artifact_registry,
            connector_registry=self._connector_registry,
            connector_execution_runtime=self._connector_execution_runtime,
        )
        self._orchestrator = orchestrator or build_default_orchestrator(
            self._meeting_workflow,
            pack_registry=self._pack_registry,
            connector_registry=self._connector_registry,
            connector_execution_runtime=self._connector_execution_runtime,
            app_registry=self._app_registry,
        )
        self._sessions: Dict[str, RuntimeSession] = {}
        self._active_turns: Dict[str, ActiveTurn] = {}

    @property
    def active_sessions(self) -> int:
        """Return the number of open sessions."""
        return len(self._sessions)

    @property
    def artifact_registry(self) -> ArtifactRegistry:
        """Return the artifact registry used by runtime workflows."""
        return self._artifact_registry

    @property
    def trace_store(self) -> TraceStore:
        """Return the trace store used by runtime workflows."""
        return self._trace_store

    @property
    def approval_store(self) -> ApprovalStore:
        """Return the approval store used by runtime policy gates."""
        return self._approval_store

    @property
    def policy_evaluator(self) -> PolicyEvaluator:
        """Return the policy evaluator used by runtime policy gates."""
        return self._policy_evaluator

    @property
    def retry_store(self) -> RetryStore:
        """Return the retry context store used by runtime retry/resume."""
        return self._retry_store

    @property
    def orchestrator(self) -> LeadOrchestrator:
        """Return the lead orchestrator used for domain workflows."""
        return self._orchestrator

    @property
    def pack_registry(self) -> PackRegistry:
        """Return the Domain Pack registry used by the gateway."""
        return self._pack_registry

    @property
    def app_registry(self) -> AppRegistry:
        """Return the app profile registry used by the gateway."""
        return self._app_registry

    @property
    def core_store(self) -> CoreSQLiteStore:
        """Return the Core v1.5 SQLite store written through CoreAppService."""
        return self._core_store

    @property
    def core_service(self) -> CoreAppService:
        """Return the Core v1.5 application service facade."""
        return self._core_service

    @property
    def connector_registry(self) -> ConnectorRegistry:
        """Return the connector registry used by domain workflows."""
        return self._connector_registry

    @property
    def connector_execution_runtime(self) -> ConnectorExecutionRuntime:
        """Return the connector execution runtime used by domain workflows."""
        return self._connector_execution_runtime

    async def start_session(
        self,
        *,
        model: Optional[str] = None,
        session_id: Optional[str] = None,
        agent_messages: Optional[list[Dict[str, str]]] = None,
        backend: Optional[str] = None,
        scope: Optional[ScopeContext] = None,
    ) -> RuntimeSession:
        """Create and store a new runtime session."""
        resolved_scope = scope or ScopeContext()
        resolved_model = model or self._model
        resolved_session_id = session_id or new_id("sess")
        resolved_backend = backend or self._runtime_backend
        if resolved_backend == "auto":
            resolved_backend = "openharness" if _has_runtime_api_key() else "simple"
        handle: Optional[RuntimeHandle] = None
        adapter: Optional[RuntimeAdapter] = None
        if resolved_backend == "openharness":
            try:
                adapter = OpenHarnessRuntimeAdapter(runtime_factory=self._runtime_factory)
                handle = await adapter.start(
                    model=resolved_model,
                    restore_messages=agent_messages or [],
                )
            except Exception:
                resolved_backend = "simple"
                adapter = None
                handle = None
        if handle is None:
            adapter = SimpleRuntimeAdapter(agent_factory=self._agent_factory)
            handle = await adapter.start(
                model=resolved_model,
                restore_messages=agent_messages,
            )
        session = RuntimeSession(
            session_id=resolved_session_id,
            model=resolved_model,
            app_id=resolved_scope.app_id,
            project_id=resolved_scope.project_id,
            workspace_id=resolved_scope.workspace_id,
            agent=handle.agent,
            bundle=handle.bundle,
            handle=handle,
            adapter=adapter,
            backend=resolved_backend,
        )
        self._sessions[resolved_session_id] = session
        self._store.save_snapshot(session)
        self._core_service.record_runtime_session(session)
        return session

    async def resume_session(self, session_id: str) -> RuntimeSession:
        """Restore a session from its persisted snapshot."""
        existing = self._sessions.get(session_id)
        if existing is not None:
            return existing
        snapshot = self._store.load_snapshot(session_id)
        messages = snapshot.get("agent_messages")
        if not isinstance(messages, list):
            messages = []
        return await self.start_session(
            model=snapshot.get("model") or self._model,
            session_id=session_id,
            agent_messages=messages,
            backend=snapshot.get("backend"),
            scope=ScopeContext(
                app_id=str(snapshot.get("app_id") or "default"),
                project_id=snapshot.get("project_id") if isinstance(snapshot.get("project_id"), str) else None,
                workspace_id=snapshot.get("workspace_id") if isinstance(snapshot.get("workspace_id"), str) else None,
            ),
        )

    def get_session(self, session_id: str) -> RuntimeSession:
        """Return a session or raise a protocol-friendly KeyError."""
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise KeyError(f"Unknown session_id: {session_id}") from exc

    async def close_session(self, session_id: str) -> bool:
        """Close a session if present."""
        session = self._sessions.pop(session_id, None)
        if session is None:
            return False
        active_turn = self._active_turns.pop(session_id, None)
        if active_turn is not None and not active_turn.task.done():
            active_turn.cancel_requested = True
            active_turn.task.cancel()
        session.state = "closed"
        if session.adapter is not None and session.handle is not None:
            await session.adapter.close(session.handle)
        elif session.bundle is not None:
            await self._close_runtime_bundle(session.bundle)
        self._store.save_snapshot(session)
        self._core_service.record_runtime_session(session)
        return True

    def interrupt_session(self, session_id: str) -> RuntimeSession:
        """Interrupt an active turn or mark an idle session as interrupted."""
        session = self.get_session(session_id)
        active_turn = self._active_turns.get(session_id)
        if active_turn is not None and not active_turn.task.done():
            active_turn.cancel_requested = True
            active_turn.task.cancel()
            session.interrupted = True
            session.state = "interrupted"
            session.last_active_at = datetime.now()
            self._store.save_snapshot(session)
        else:
            self._mark_interrupted(session, turn_id=None)
        return session

    def _mark_interrupted(self, session: RuntimeSession, *, turn_id: Optional[str]) -> GatewayEvent:
        session.interrupted = True
        session.state = "interrupted"
        session.last_active_at = datetime.now()
        event = GatewayEvent(
            type="turn.interrupted",
            session_id=session.session_id,
            turn_id=turn_id,
            app_id=session.app_id,
            project_id=session.project_id,
            workspace_id=session.workspace_id,
            data={"message": "Turn interrupted.", "interrupted": True},
        )
        self._append_event(event)
        self._store.save_snapshot(session)
        self._core_service.record_runtime_session(session)
        return event

    def read_events(self, session_id: str) -> list[Dict[str, Any]]:
        """Read persisted protocol events for a session."""
        try:
            return self._core_service.read_session_events(session_id)
        except KeyError:
            return self._store.read_events(session_id)

    def list_sessions(self) -> list[Dict[str, Any]]:
        """List persisted session snapshots."""
        sessions = self._core_service.list_session_snapshots()
        if sessions:
            return sessions
        return self._store.list_snapshots()

    def read_session(self, session_id: str) -> Dict[str, Any]:
        """Read one persisted session snapshot."""
        try:
            return self._core_service.read_session_snapshot(session_id)
        except KeyError:
            return self._store.load_snapshot(session_id)

    def read_transcript(self, session_id: str) -> list[Dict[str, Any]]:
        """Read a transcript rebuilt from persisted events."""
        try:
            return self._core_service.read_session_transcript(session_id)
        except KeyError:
            return self._store.read_transcript(session_id)

    async def stream_turn(
        self,
        *,
        session_id: str,
        user_input: str,
        domain: Optional[str] = None,
        scope: Optional[ScopeContext] = None,
        skip_policy: bool = False,
        retry_of_turn_id: Optional[str] = None,
        approval_id: Optional[str] = None,
        source_turn_id: Optional[str] = None,
    ) -> AsyncIterator[GatewayEvent]:
        """Submit a user turn and yield normalized gateway events."""
        session = self.get_session(session_id)
        resolved_scope = scope or ScopeContext(
            app_id=session.app_id,
            project_id=session.project_id,
            workspace_id=session.workspace_id,
        )
        turn_id = new_id("turn")
        trace_id = self._trace_store.new_trace_id()
        session.state = "running"
        session.last_active_at = datetime.now()
        current_task = asyncio.current_task()
        if current_task is not None:
            self._active_turns[session_id] = ActiveTurn(turn_id=turn_id, task=current_task)
        started_data: Dict[str, Any] = {
            "input": user_input,
            "domain": domain,
            "model": session.model,
            "trace_id": trace_id,
            "app_id": resolved_scope.app_id,
            "project_id": resolved_scope.project_id,
            "workspace_id": resolved_scope.workspace_id,
        }
        if retry_of_turn_id:
            started_data["retry_of_turn_id"] = retry_of_turn_id
        if approval_id:
            started_data["approval_id"] = approval_id
        started_event = GatewayEvent(
            type="turn.started",
            session_id=session_id,
            turn_id=turn_id,
            app_id=resolved_scope.app_id,
            project_id=resolved_scope.project_id,
            workspace_id=resolved_scope.workspace_id,
            data=started_data,
        )
        self._append_event(started_event)
        yield started_event
        turn_thread_id: Optional[str] = None
        try:
            turn_thread_id = self._core_service.get_turn(turn_id).thread_id
        except KeyError:
            turn_thread_id = None
        memory_context = self._core_service.memory_context_for_turn(
            session_id=session_id,
            thread_id=turn_thread_id,
            domain=domain,
            trace_id=trace_id,
            app_id=resolved_scope.app_id,
            project_id=resolved_scope.project_id,
            workspace_id=resolved_scope.workspace_id,
        )
        runtime_input = (
            user_input
            if retry_of_turn_id or approval_id
            else _with_memory_context(user_input, memory_context)
        )

        try:
            policy_decision = self._policy_evaluator.evaluate_user_input(user_input, domain=domain)
            if policy_decision.requires_approval and not skip_policy:
                approval = self._approval_store.request(
                    action=policy_decision.action,
                    request_summary=user_input,
                    trace_id=trace_id,
                    session_id=session_id,
                    turn_id=turn_id,
                    app_id=resolved_scope.app_id,
                    project_id=resolved_scope.project_id,
                    workspace_id=resolved_scope.workspace_id,
                    risk_level=policy_decision.risk_level,
                    metadata={"policy": policy_decision.model_dump()},
                )
                self._core_service.record_gateway_approval(approval)
                trace_record = self._trace_store.record_approval_operation(
                    operation="request",
                    approval=approval,
                    status="pending",
                    metadata={"policy": policy_decision.model_dump()},
                )
                self._core_service.record_gateway_trace(trace_record)
                retry_context = self._retry_store.create_policy_context(
                    session_id=session_id,
                    turn_id=turn_id,
                    user_input=user_input,
                    domain=domain,
                    trace_id=trace_id,
                    approval_id=approval["approval_id"],
                    app_id=resolved_scope.app_id,
                    project_id=resolved_scope.project_id,
                    workspace_id=resolved_scope.workspace_id,
                    policy=policy_decision.model_dump(),
                )
                self._core_service.record_gateway_retry(retry_context)
                async for event in self._emit_simple_result(
                    session=session,
                    turn_id=turn_id,
                    trace_id=trace_id,
                    scope=resolved_scope,
                    result={
                        "status": "success",
                        "content": f"操作需要审批。Approval ID: {approval['approval_id']}",
                        "approval_required": True,
                        "approval": approval,
                        "retry_context": retry_context,
                        "policy": policy_decision.model_dump(),
                    },
                ):
                    yield event
                return

            workflow_context = WorkflowContext(
                session_id=session.session_id,
                turn_id=turn_id,
                domain=domain,
                scope=resolved_scope,
                artifact_registry=self._artifact_registry,
                approval_id=approval_id,
            )
            blocked_pack_for_domain = getattr(self._orchestrator.registry, "blocked_pack_for_domain", None)
            blocked_pack = blocked_pack_for_domain(domain) if callable(blocked_pack_for_domain) else None
            if blocked_pack is not None:
                raise RuntimeError(
                    "Pack assembly blocked for domain "
                    f"{blocked_pack.domain}: {blocked_pack.disabled_reason} "
                    f"Missing dependencies: {', '.join(blocked_pack.missing_dependencies)}"
                )
            workflow = self._orchestrator.registry.select(user_input, workflow_context)
            if workflow is not None:
                thread = self._core_service.ensure_thread(
                    session_id=session.session_id,
                    domain=workflow.domain,
                    scope=resolved_scope,
                )
                job = self._core_service.start_job(
                    workflow_id=workflow.workflow_id,
                    domain=workflow.domain,
                    session_id=session.session_id,
                    thread_id=thread.thread_id,
                    turn_id=turn_id,
                    trace_id=trace_id,
                    scope=resolved_scope,
                    metadata={
                        "input": user_input,
                        "pack": _workflow_pack_metadata(self._pack_registry, workflow.workflow_id),
                    },
                )
                try:
                    result = await workflow.run(user_input, workflow_context)
                except Exception as exc:
                    failure_context = {
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                        "workflow_id": workflow.workflow_id,
                        "domain": workflow.domain,
                    }
                    self._core_service.update_job(
                        job_id=job.job_id,
                        status="failed",
                        progress=1.0,
                        failure_context=failure_context,
                        metadata={
                            "error": str(exc),
                            "failure_context": failure_context,
                        },
                    )
                    raise
                result.setdefault("domain", workflow.domain)
                result.setdefault("workflow_id", workflow.workflow_id)
                self._persist_workflow_approval_retry_context(
                    result=result,
                    session_id=session.session_id,
                    turn_id=turn_id,
                    user_input=user_input,
                    domain=workflow.domain,
                    trace_id=trace_id,
                    scope=resolved_scope,
                )
                artifact_ids = _artifact_ids_from_workflow_result(result)
                job_status = "failed" if str(result.get("status", "success")) == "error" else "completed"
                completed_job = self._core_service.update_job(
                    job_id=job.job_id,
                    status=job_status,
                    progress=1.0,
                    artifact_ids=artifact_ids,
                    metadata={"artifact_ids": artifact_ids},
                )
                result["job"] = completed_job.model_dump(mode="json")
                result["job_id"] = completed_job.job_id
                async for event in self._emit_simple_result(
                    session=session,
                    turn_id=turn_id,
                    trace_id=trace_id,
                    scope=resolved_scope,
                    result=result,
                ):
                    yield event
                return
            if session.backend == "openharness" and session.adapter is not None and session.handle is not None:
                async for event in self._stream_adapter_turn(
                    session=session,
                    turn_id=turn_id,
                    trace_id=trace_id,
                    user_input=runtime_input,
                    scope=resolved_scope,
                    original_user_input=user_input,
                    approval_id=approval_id,
                    source_turn_id=retry_of_turn_id,
                ):
                    yield event
                self._store.save_snapshot(session)
                return
            if session.adapter is not None and session.handle is not None:
                result = await session.adapter.invoke(
                    session.handle,
                    runtime_input,
                    governance=self._governance_context(
                        session_id=session.session_id,
                        turn_id=turn_id,
                        trace_id=trace_id,
                        scope=resolved_scope,
                        user_input=user_input,
                        approval_id=approval_id,
                        source_turn_id=retry_of_turn_id,
                    ),
                )
            else:
                result = session.agent.invoke(runtime_input)
        except asyncio.CancelledError:
            active_turn = self._active_turns.get(session_id)
            interrupted_event = self._mark_interrupted(session, turn_id=turn_id)
            if active_turn is not None and active_turn.cancel_requested:
                yield interrupted_event
                return
            raise
        except Exception as exc:
            session.state = "idle"
            failed_event = GatewayEvent(
                type="turn.failed",
                session_id=session_id,
                turn_id=turn_id,
                app_id=resolved_scope.app_id,
                project_id=resolved_scope.project_id,
                workspace_id=resolved_scope.workspace_id,
                data={"message": str(exc), "recoverable": True, "trace_id": trace_id},
            )
            self._append_event(failed_event, trace_id=trace_id)
            self._store.save_snapshot(session)
            yield failed_event
            return
        finally:
            active_turn = self._active_turns.get(session_id)
            if active_turn is not None and active_turn.turn_id == turn_id:
                self._active_turns.pop(session_id, None)

        async for event in self._emit_simple_result(
            session=session,
            turn_id=turn_id,
            trace_id=trace_id,
            scope=resolved_scope,
            result=result,
        ):
            yield event

    async def _emit_simple_result(
        self,
        *,
        session: RuntimeSession,
        turn_id: str,
        trace_id: str,
        scope: ScopeContext,
        result: Any,
    ) -> AsyncIterator[GatewayEvent]:
        status = "success"
        content = ""
        metadata: Dict[str, Any] = {}
        if isinstance(result, dict):
            status = str(result.get("status", "success"))
            content = str(result.get("content", ""))
            metadata = {
                key: value
                for key, value in result.items()
                if key not in {"status", "content"}
            }
        else:
            content = str(result)

        if status == "error":
            session.state = "idle"
            failed_event = GatewayEvent(
                type="turn.failed",
                session_id=session.session_id,
                turn_id=turn_id,
                app_id=scope.app_id,
                project_id=scope.project_id,
                workspace_id=scope.workspace_id,
                data={"message": content, "recoverable": True, "trace_id": trace_id, **metadata},
            )
            self._append_event(failed_event)
            self._store.save_snapshot(session)
            yield failed_event
            return

        if content:
            delta_event = GatewayEvent(
                type="item.delta",
                session_id=session.session_id,
                turn_id=turn_id,
                app_id=scope.app_id,
                project_id=scope.project_id,
                workspace_id=scope.workspace_id,
                data={"text": content, "trace_id": trace_id},
            )
            self._append_event(delta_event)
            yield delta_event

        if session.state != "interrupted":
            session.state = "idle"
        completed_event = GatewayEvent(
            type="turn.completed",
            session_id=session.session_id,
            turn_id=turn_id,
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            data={
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": content}],
                },
                "usage": metadata.get("usage", {}),
                "model": metadata.get("model", session.model),
                **metadata,
                "trace_id": trace_id,
            },
        )
        self._append_event(completed_event)
        summary_thread_id: Optional[str] = None
        try:
            summary_thread_id = self._core_service.get_turn(turn_id).thread_id
        except KeyError:
            summary_thread_id = None
        self._core_service.build_session_summary(
            session_id=session.session_id,
            thread_id=summary_thread_id,
            trace_id=trace_id,
            scope_context=scope,
        )
        self._store.save_snapshot(session)
        yield completed_event

    async def continue_turn(self, *, session_id: str) -> TurnResult:
        """Continue a pending turn when supported by the runtime."""
        session = self.get_session(session_id)
        turn_id = new_id("turn")
        trace_id = self._trace_store.new_trace_id()
        if session.backend == "openharness" and session.adapter is not None and session.handle is not None:
            events: list[GatewayEvent] = []
            text_parts: list[str] = []
            try:
                async for runtime_event in session.adapter.continue_pending(
                    session.handle,
                    governance=self._governance_context(
                        session_id=session_id,
                        turn_id=turn_id,
                        trace_id=trace_id,
                        scope=ScopeContext(
                            app_id=session.app_id,
                            project_id=session.project_id,
                            workspace_id=session.workspace_id,
                        ),
                    ),
                ):
                    event = normalize_runtime_event(
                        runtime_event,
                        session_id=session_id,
                        turn_id=turn_id,
                    )
                    event.app_id = session.app_id
                    event.project_id = session.project_id
                    event.workspace_id = session.workspace_id
                    self._append_event(event, trace_id=trace_id)
                    events.append(event)
                    if event.type == "item.delta":
                        text_parts.append(str(event.data.get("text", "")))
            except Exception as exc:
                failed = GatewayEvent(
                    type="turn.failed",
                    session_id=session_id,
                    turn_id=turn_id,
                    app_id=session.app_id,
                    project_id=session.project_id,
                    workspace_id=session.workspace_id,
                    data={"message": str(exc), "recoverable": True, "trace_id": trace_id},
                )
                self._append_event(failed)
                events.append(failed)
            if events:
                self._store.save_snapshot(session)
                return TurnResult(
                    session_id=session_id,
                    turn_id=turn_id,
                    final_text="".join(text_parts),
                    app_id=session.app_id,
                    project_id=session.project_id,
                    workspace_id=session.workspace_id,
                    events=events,
                )
        event = GatewayEvent(
            type="item.status",
            session_id=session_id,
            turn_id=turn_id,
            app_id=session.app_id,
            project_id=session.project_id,
            workspace_id=session.workspace_id,
            data={
                "message": "No pending continuation for the current simple runtime.",
                "continued": False,
                "state": session.state,
            },
        )
        self._append_event(event)
        return TurnResult(
            session_id=session_id,
            turn_id=turn_id,
            final_text="",
            app_id=session.app_id,
            project_id=session.project_id,
            workspace_id=session.workspace_id,
            events=[event],
        )

    async def run_turn(
        self,
        *,
        session_id: str,
        user_input: str,
        domain: Optional[str] = None,
        scope: Optional[ScopeContext] = None,
        skip_policy: bool = False,
        retry_of_turn_id: Optional[str] = None,
        approval_id: Optional[str] = None,
    ) -> TurnResult:
        """Run a turn and aggregate text for headless clients."""
        session = self.get_session(session_id)
        resolved_scope = scope or ScopeContext(
            app_id=session.app_id,
            project_id=session.project_id,
            workspace_id=session.workspace_id,
        )
        events: list[GatewayEvent] = []
        text_parts: list[str] = []
        failure_text = ""
        turn_id = ""
        async for event in self.stream_turn(
            session_id=session_id,
            user_input=user_input,
            domain=domain,
            scope=scope,
            skip_policy=skip_policy,
            retry_of_turn_id=retry_of_turn_id,
            approval_id=approval_id,
        ):
            events.append(event)
            if event.turn_id:
                turn_id = event.turn_id
            if event.type == "item.delta":
                text_parts.append(str(event.data.get("text", "")))
            elif event.type == "turn.failed" and not failure_text:
                failure_text = str(event.data.get("message", "") or "")
        return TurnResult(
            session_id=session_id,
            turn_id=turn_id,
            final_text="".join(text_parts) or failure_text,
            app_id=resolved_scope.app_id,
            project_id=resolved_scope.project_id,
            workspace_id=resolved_scope.workspace_id,
            events=events,
        )

    def _create_default_agent(self, model: str) -> Any:
        adapter = SimpleRuntimeAdapter(
            tools=get_builtin_tools(
                policy_evaluator=self._policy_evaluator,
                approval_checker=self._is_approval_approved,
            )
        )
        return adapter._create_agent(model)

    def _is_approval_approved(self, approval_id: str, expected: Optional[Dict[str, Any]] = None) -> bool:
        try:
            approval = self._approval_store.get_approval(approval_id)
        except Exception:
            return False
        if approval.get("status") != "approved":
            return False
        if not expected:
            return True
        metadata = approval.get("metadata") if isinstance(approval.get("metadata"), dict) else {}
        binding = metadata.get("binding") if isinstance(metadata.get("binding"), dict) else {}
        if not binding:
            return False
        checks = {
            "session_id": expected.get("session_id"),
            "turn_id": expected.get("source_turn_id") or expected.get("turn_id"),
            "tool_name": expected.get("tool_name"),
            "action": expected.get("action"),
            "tool_input_hash": expected.get("tool_input_hash"),
        }
        for key, binding_value in binding.items():
            if key in checks and binding_value and checks.get(key) != binding_value:
                return False
        return all(binding.get(key) == value for key, value in checks.items() if value)

    def _persist_workflow_approval_retry_context(
        self,
        *,
        result: dict[str, Any],
        session_id: str,
        turn_id: str,
        user_input: str,
        domain: Optional[str],
        trace_id: str,
        scope: ScopeContext,
    ) -> None:
        """Persist retry context for workflow-level approval gates."""
        if not result.get("approval_required"):
            return
        approval = result.get("approval")
        if not isinstance(approval, dict):
            return
        approval_id = approval.get("approval_id")
        if not isinstance(approval_id, str) or not approval_id:
            return
        try:
            self._retry_store.get_by_approval(approval_id)
            return
        except KeyError:
            pass
        retry_context = self._retry_store.create_policy_context(
            session_id=session_id,
            turn_id=turn_id,
            user_input=user_input,
            domain=domain,
            trace_id=trace_id,
            approval_id=approval_id,
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            policy={
                "action": "connector.submit",
                "source": "workflow",
                "workflow_id": result.get("workflow_id"),
            },
        )
        self._core_service.record_gateway_retry(retry_context)
        result["retry_context"] = retry_context

    def _append_event(self, event: GatewayEvent, *, trace_id: Optional[str] = None) -> None:
        """Persist one event and write its Core trace/item records."""
        if trace_id and "trace_id" not in event.data:
            event.data["trace_id"] = trace_id
        event.data.setdefault("app_id", event.app_id)
        event.data.setdefault("project_id", event.project_id)
        event.data.setdefault("workspace_id", event.workspace_id)
        self._store.append_event(event)
        trace_record = self._trace_store.record_event(event)
        self._core_service.record_gateway_trace(trace_record)
        self._core_service.record_gateway_event(event)

    async def _create_runtime_bundle(
        self,
        model: str,
        restore_messages: list[Dict[str, Any]],
    ) -> Any:
        if self._runtime_factory is not None:
            created = self._runtime_factory(model)
            if inspect.isawaitable(created):
                return await created
            return created
        from cli.tui.runtime import build_runtime, start_runtime

        bundle = await build_runtime(
            model=model,
            restore_messages=restore_messages,
            enforce_max_turns=False,
        )
        await start_runtime(bundle)
        return bundle

    async def _close_runtime_bundle(self, bundle: Any) -> None:
        from cli.tui.runtime import close_runtime

        await close_runtime(bundle)

    async def _stream_runtime_bundle_turn(
        self,
        *,
        session: RuntimeSession,
        turn_id: str,
        trace_id: str,
        user_input: str,
        original_user_input: Optional[str] = None,
        approval_id: Optional[str] = None,
        source_turn_id: Optional[str] = None,
    ) -> AsyncIterator[GatewayEvent]:
        session.state = "running"
        text_parts: list[str] = []
        try:
            async for runtime_event in session.bundle.engine.submit_message(user_input):
                event = normalize_runtime_event(
                    runtime_event,
                    session_id=session.session_id,
                    turn_id=turn_id,
                )
                event.app_id = session.app_id
                event.project_id = session.project_id
                event.workspace_id = session.workspace_id
                self._append_event(event, trace_id=trace_id)
                if event.type == "item.delta":
                    text_parts.append(str(event.data.get("text", "")))
                yield event
        except Exception as exc:
            failed_event = GatewayEvent(
                type="turn.failed",
                session_id=session.session_id,
                turn_id=turn_id,
                app_id=session.app_id,
                project_id=session.project_id,
                workspace_id=session.workspace_id,
                data={"message": str(exc), "recoverable": True, "trace_id": trace_id},
            )
            self._append_event(failed_event)
            yield failed_event
            return
        finally:
            if session.state != "interrupted":
                session.state = "idle"
            session.last_active_at = datetime.now()

        if text_parts:
            return

    async def _stream_adapter_turn(
        self,
        *,
        session: RuntimeSession,
        turn_id: str,
        trace_id: str,
        user_input: str,
        scope: ScopeContext,
        original_user_input: Optional[str] = None,
        approval_id: Optional[str] = None,
        source_turn_id: Optional[str] = None,
    ) -> AsyncIterator[GatewayEvent]:
        session.state = "running"
        text_parts: list[str] = []
        if session.adapter is None or session.handle is None:
            raise RuntimeError("Runtime adapter is not available for this session")
        try:
            async for runtime_event in session.adapter.stream(
                session.handle,
                user_input,
                governance=self._governance_context(
                    session_id=session.session_id,
                    turn_id=turn_id,
                    trace_id=trace_id,
                    scope=scope,
                    user_input=original_user_input or user_input,
                    approval_id=approval_id,
                    source_turn_id=source_turn_id,
                ),
            ):
                event = normalize_runtime_event(
                    runtime_event,
                    session_id=session.session_id,
                    turn_id=turn_id,
                )
                event.app_id = scope.app_id
                event.project_id = scope.project_id
                event.workspace_id = scope.workspace_id
                self._append_event(event, trace_id=trace_id)
                if event.type == "item.delta":
                    text_parts.append(str(event.data.get("text", "")))
                yield event
        except Exception as exc:
            failed_event = GatewayEvent(
                type="turn.failed",
                session_id=session.session_id,
                turn_id=turn_id,
                app_id=scope.app_id,
                project_id=scope.project_id,
                workspace_id=scope.workspace_id,
                data={"message": str(exc), "recoverable": True, "trace_id": trace_id},
            )
            self._append_event(failed_event)
            yield failed_event
            return
        finally:
            if session.state != "interrupted":
                session.state = "idle"
            session.last_active_at = datetime.now()

        if text_parts:
            return

    def _governance_context(
        self,
        *,
        session_id: str,
        turn_id: str,
        trace_id: str,
        scope: Optional[ScopeContext] = None,
        user_input: str = "",
        approval_id: Optional[str] = None,
        source_turn_id: Optional[str] = None,
    ) -> RuntimeGovernanceContext:
        resolved_scope = scope or ScopeContext()
        return RuntimeGovernanceContext(
            session_id=session_id,
            turn_id=turn_id,
            trace_id=trace_id,
            app_id=resolved_scope.app_id,
            project_id=resolved_scope.project_id,
            workspace_id=resolved_scope.workspace_id,
            user_input=user_input,
            approval_id=approval_id,
            source_turn_id=source_turn_id,
            policy_evaluator=self._policy_evaluator,
            approval_checker=self._is_approval_approved,
            approval_requester=lambda tool_name, tool_input, decision: self._request_tool_approval(
                session_id=session_id,
                turn_id=turn_id,
                trace_id=trace_id,
                user_input=user_input,
                tool_name=tool_name,
                tool_input=tool_input,
                decision=decision,
            ),
        )

    def _request_tool_approval(
        self,
        *,
        session_id: str,
        turn_id: str,
        trace_id: str,
        user_input: str,
        tool_name: str,
        tool_input: Any,
        decision: Dict[str, Any],
    ) -> Dict[str, Any]:
        session = self.get_session(session_id)
        approval = self._approval_store.request(
            action=str(decision.get("action") or f"tool.{tool_name}"),
            request_summary=f"Tool {tool_name} requires approval",
            trace_id=trace_id,
            session_id=session_id,
            turn_id=turn_id,
            app_id=session.app_id,
            project_id=session.project_id,
            workspace_id=session.workspace_id,
            risk_level=str(decision.get("risk_level") or "medium"),
            metadata={
                "policy": decision,
                "tool_name": tool_name,
                "tool_input": tool_input,
                "binding": {
                    "session_id": session_id,
                    "turn_id": turn_id,
                    "trace_id": trace_id,
                    "tool_name": tool_name,
                    "action": str(decision.get("action") or f"tool.{tool_name}"),
                    "tool_input_hash": tool_input_hash(tool_input),
                },
            },
        )
        self._core_service.record_gateway_approval(approval)
        trace_record = self._trace_store.record_approval_operation(
            operation="request",
            approval=approval,
            status="pending",
            metadata={"policy": decision, "tool_name": tool_name},
        )
        self._core_service.record_gateway_trace(trace_record)
        retry_context = self._retry_store.create_policy_context(
            session_id=session_id,
            turn_id=turn_id,
            user_input=user_input,
            domain=None,
            trace_id=trace_id,
            approval_id=approval["approval_id"],
            app_id=session.app_id,
            project_id=session.project_id,
            workspace_id=session.workspace_id,
            policy={
                **decision,
                "tool_name": tool_name,
                "tool_input": tool_input,
            },
        )
        self._core_service.record_gateway_retry(retry_context)
        return {"approval": approval, "retry_context": retry_context}


def normalize_runtime_event(
    event: Any,
    *,
    session_id: str,
    turn_id: str,
) -> GatewayEvent:
    """Convert OpenHarness-like stream events into project protocol events.

    This intentionally uses class names and attributes instead of isinstance
    checks so migrated ``openharness.*`` and ``harnessOS.openharness.*`` modules
    cannot split event identity.
    """
    event_name = type(event).__name__
    if event_name == "AssistantTextDelta":
        return GatewayEvent(
            type="item.delta",
            session_id=session_id,
            turn_id=turn_id,
            data={"text": getattr(event, "text", "")},
        )
    if event_name == "AssistantTurnComplete":
        message = getattr(event, "message", None)
        usage = getattr(event, "usage", None)
        return GatewayEvent(
            type="turn.completed",
            session_id=session_id,
            turn_id=turn_id,
            data={
                "message": _message_to_payload(message),
                "usage": _usage_to_payload(usage),
            },
        )
    if event_name == "ToolExecutionStarted":
        return GatewayEvent(
            type="tool.started",
            session_id=session_id,
            turn_id=turn_id,
            data={
                "tool_name": getattr(event, "tool_name", ""),
                "tool_input": getattr(event, "tool_input", {}),
            },
        )
    if event_name == "ToolExecutionCompleted":
        return GatewayEvent(
            type="tool.completed",
            session_id=session_id,
            turn_id=turn_id,
            data={
                "tool_name": getattr(event, "tool_name", ""),
                "output": getattr(event, "output", ""),
                "is_error": bool(getattr(event, "is_error", False)),
            },
        )
    if event_name == "StatusEvent":
        return GatewayEvent(
            type="item.status",
            session_id=session_id,
            turn_id=turn_id,
            data={"message": getattr(event, "message", "")},
        )
    if event_name == "ErrorEvent":
        return GatewayEvent(
            type="turn.failed",
            session_id=session_id,
            turn_id=turn_id,
            data={
                "message": getattr(event, "message", ""),
                "recoverable": bool(getattr(event, "recoverable", True)),
            },
        )
    if event_name == "CompactProgressEvent":
        return GatewayEvent(
            type="item.status",
            session_id=session_id,
            turn_id=turn_id,
            data={
                "message": getattr(event, "message", "") or "Compacting context",
                "phase": getattr(event, "phase", ""),
                "trigger": getattr(event, "trigger", ""),
                "attempt": getattr(event, "attempt", None),
            },
        )
    return GatewayEvent(
        type="item.status",
        session_id=session_id,
        turn_id=turn_id,
        data={"message": f"Unhandled runtime event: {event_name}"},
    )


def _default_model() -> str:
    return (
        os.getenv("LLM_MODEL")
        or os.getenv("DEEP_AGENTS_MODEL")
        or os.getenv("OPENHARNESS_MODEL")
        or "deepseek-chat"
    )


def _build_default_meeting_workflow(
    *,
    artifact_registry: ArtifactRegistry,
    connector_registry: ConnectorRegistry,
    connector_execution_runtime: ConnectorExecutionRuntime,
) -> Any | None:
    try:
        from packs.meeting.workflow import MeetingWorkflow
    except Exception:
        return None
    return MeetingWorkflow(
        artifact_registry=artifact_registry,
        connector_registry=connector_registry,
        connector_execution_runtime=connector_execution_runtime,
    )


def _has_runtime_api_key() -> bool:
    return any(
        os.getenv(name)
        for name in (
            "OPENHARNESS_API_KEY",
            "DEEPSEEK_API_KEY",
            "MINIMAX_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
        )
    )


def _workflow_pack_metadata(pack_registry: Any, workflow_id: str) -> Optional[Dict[str, str]]:
    pack = pack_registry.get_workflow_pack(workflow_id)
    if pack is None:
        return None
    return {"name": pack.name, "version": pack.version, "status": pack.status}


def _with_memory_context(user_input: str, memory_context: Dict[str, Any]) -> str:
    prompt = memory_context.get("prompt") if isinstance(memory_context, dict) else ""
    if not isinstance(prompt, str) or not prompt.strip():
        return user_input
    return f"{prompt.strip()}\n\nUser request:\n{user_input}"


def _artifact_ids_from_workflow_result(result: Dict[str, Any]) -> list[str]:
    records = result.get("artifact_records")
    if not isinstance(records, dict):
        meeting = result.get("meeting")
        records = meeting.get("artifact_records") if isinstance(meeting, dict) else None
    if not isinstance(records, dict):
        return []
    artifact_ids: list[str] = []
    for record in records.values():
        if isinstance(record, dict) and isinstance(record.get("artifact_id"), str):
            artifact_ids.append(record["artifact_id"])
    return sorted(set(artifact_ids))


def _message_to_payload(message: Any) -> Dict[str, Any]:
    if message is None:
        return {"role": "assistant", "content": []}
    if hasattr(message, "model_dump"):
        return message.model_dump(mode="json")
    return {
        "role": getattr(message, "role", "assistant"),
        "content": [{"type": "text", "text": getattr(message, "text", str(message))}],
    }


def _usage_to_payload(usage: Any) -> Dict[str, Any]:
    if usage is None:
        return {}
    if hasattr(usage, "model_dump"):
        return usage.model_dump(mode="json")
    return {
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
        "total_tokens": int(getattr(usage, "total_tokens", 0) or 0),
    }
