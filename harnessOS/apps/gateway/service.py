"""Local JSON-RPC style gateway service for harnessOS."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Optional
from uuid import uuid4

from apps.gateway.approvals import (
    APPROVAL_APPROVED,
    APPROVAL_PENDING,
    APPROVAL_REJECTED,
    ApprovalConflictError,
    ApprovalStore,
)
from apps.gateway.artifacts import ArtifactReadBlockedError, ArtifactRegistry
from apps.gateway.persistence import atomic_write_text
from apps.gateway.connector_execution import ConnectorExecutionRuntime
from apps.gateway.connectors import ConnectorRegistry, MEETING_VOICE_MCP_CONNECTOR_ID
from apps.gateway.policies import PolicyEvaluator
from apps.gateway.protocol import GatewayEvent, RpcError, RpcRequest, RpcResponse
from apps.gateway.retries import RETRY_PENDING_APPROVAL, RETRY_RETRIED, RetryStore
from apps.gateway.rpc_router import RpcRouter
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.secrets import mask_value
from apps.gateway.traces import TraceStore
from apps.gateway.workflows import (
    AVAILABLE_POLICY_BUNDLES,
    COMPATIBLE_PACK_SCHEMA_VERSIONS,
    build_pack_assembly_inputs,
    _supported_workflow_ids,
)
from core.apps import AppRegistry, build_default_app_registry, resolve_scope_context
from core.packs import build_pack_execution_plan, execute_pack_stub
from core.protocol.auth import issue_subscription_token
from core.protocol.contracts.method_inventory import METHOD_INVENTORY
from core.protocol.contracts.workflow_method_inventory import WORKFLOW_METHOD_INVENTORY
from core.protocol.event_bridge import ensure_channel_capabilities, make_event_cursor, normalize_event_channels
from core.protocol.schemas import ProtocolError, get_method_schema, list_method_schemas
from core.workflows.models import (
    BusinessEvent,
    BusinessEventBinding,
    EvaluatorType,
    QualityEvaluation,
    StationRun,
    StationRunStatus,
    WorkflowContext,
    WorkflowInstance,
    WorkflowInstanceStatus,
    WorkflowPatch,
    WorkflowPatchActorType,
    WorkflowPatchOperation,
    WorkflowPatchStatus,
    WorkflowTemplate,
)
from core.workflows.store import InMemoryWorkflowStore, WorkflowRepository, WorkflowStore


class GatewayService:
    """Project-owned control-plane facade over runtime sessions."""

    def __init__(
        self,
        runtime_pool: Optional[GatewayRuntimePool] = None,
        meeting_service: Optional[Any] = None,
        artifact_registry: Optional[ArtifactRegistry] = None,
        trace_store: Optional[TraceStore] = None,
        approval_store: Optional[ApprovalStore] = None,
        policy_evaluator: Optional[PolicyEvaluator] = None,
        retry_store: Optional[RetryStore] = None,
        app_registry: Optional[AppRegistry] = None,
        workflow_store: Optional[WorkflowStore] = None,
        workflow_repository: Optional[WorkflowRepository] = None,
    ) -> None:
        resolved_app_registry = app_registry or getattr(runtime_pool, "app_registry", None) or build_default_app_registry()
        resolved_meeting_service = meeting_service
        self.trace_store = trace_store or getattr(runtime_pool, "trace_store", None) or TraceStore()
        self.approval_store = approval_store or getattr(runtime_pool, "approval_store", None) or ApprovalStore()
        self.policy_evaluator = policy_evaluator or getattr(runtime_pool, "policy_evaluator", None) or PolicyEvaluator()
        self.retry_store = retry_store or getattr(runtime_pool, "retry_store", None) or RetryStore()
        meeting_workflow = None
        if runtime_pool is None and meeting_service is not None:
            meeting_workflow = _build_meeting_workflow(
                service=resolved_meeting_service,
                artifact_registry=artifact_registry,
            )
        self.runtime_pool = runtime_pool or GatewayRuntimePool(
            artifact_registry=artifact_registry,
            meeting_workflow=meeting_workflow,
            trace_store=self.trace_store,
            approval_store=self.approval_store,
            policy_evaluator=self.policy_evaluator,
            retry_store=self.retry_store,
            app_registry=resolved_app_registry,
        )
        self.artifact_registry = artifact_registry or self.runtime_pool.artifact_registry
        self.trace_store = trace_store or self.runtime_pool.trace_store
        self.approval_store = approval_store or self.runtime_pool.approval_store
        self.policy_evaluator = policy_evaluator or self.runtime_pool.policy_evaluator
        self.retry_store = retry_store or self.runtime_pool.retry_store
        self.core_store = self.runtime_pool.core_store
        self.core_service = self.runtime_pool.core_service
        self.app_registry = resolved_app_registry
        self.workflow_repository = workflow_repository or WorkflowRepository(workflow_store or InMemoryWorkflowStore())
        self._meeting_service = resolved_meeting_service
        self.connector_registry = (
            ConnectorRegistry(core_service=self.core_service, meeting_config=self.meeting_service.config)
            if meeting_service is not None
            else self.runtime_pool.connector_registry
        )
        runtime_connector_execution = getattr(self.runtime_pool, "connector_execution_runtime", None)
        self.connector_execution_runtime = runtime_connector_execution or ConnectorExecutionRuntime(
            connector_registry=self.connector_registry,
            core_service=self.core_service,
            artifact_registry=self.artifact_registry,
            trace_store=self.trace_store,
            approval_store=self.approval_store,
        )
        self.rpc_router = RpcRouter()
        self._register_rpc_methods()
        self.initialized = False

    @property
    def meeting_service(self) -> Any:
        """Lazily initialize the legacy Meeting facade only when called."""
        if self._meeting_service is None:
            self._meeting_service = _build_meeting_gateway_service()
        return self._meeting_service

    @meeting_service.setter
    def meeting_service(self, service: Any) -> None:
        self._meeting_service = service

    async def initialize(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Initialize the gateway protocol session."""
        self.initialized = True
        capabilities = self.rpc_router.capabilities()
        capabilities.update({"headless": True, "stdio_jsonl": True})
        method_payload = await self.method_list({})
        return {
            "protocol_version": "v1alpha",
            "server": "harnessOS gateway",
            "capabilities": capabilities,
            "methods": method_payload["methods"],
        }

    async def health_ping(self) -> Dict[str, Any]:
        """Return a compact health snapshot."""
        return {
            "status": "ok",
            "active_sessions": self.runtime_pool.active_sessions,
            "initialized": self.initialized,
        }

    async def app_list(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List app profiles that can share the Core runtime."""
        del params
        profiles = self.app_registry.list_profiles()
        return {"apps": profiles, "count": len(profiles)}

    async def app_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one app profile."""
        return {"app": self.app_registry.get(_require_str(params, "app_id")).to_dict()}

    async def session_start(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a runtime-backed session."""
        params = params or {}
        scope = self._resolve_request_scope(params)
        session = await self.runtime_pool.start_session(model=params.get("model"), scope=scope)
        return {
            "session_id": session.session_id,
            "app_id": session.app_id,
            "project_id": session.project_id,
            "workspace_id": session.workspace_id,
            "model": session.model,
            "state": session.state,
            "backend": session.backend,
            "created_at": session.created_at.isoformat(),
        }

    async def session_close(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Close a session."""
        session_id = _require_str(params, "session_id")
        session = self.runtime_pool.read_session(session_id)
        self._ensure_session_in_scope(session, self._resolve_request_scope(params), params)
        closed = await self.runtime_pool.close_session(session_id)
        return {"session_id": session_id, "closed": closed}

    async def session_resume(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resume a session from its local snapshot."""
        session_id = _require_str(params, "session_id")
        existing = self.runtime_pool.read_session(session_id)
        self._ensure_session_in_scope(existing, self._resolve_request_scope(params), params)
        session = await self.runtime_pool.resume_session(session_id)
        return {
            "session_id": session.session_id,
            "model": session.model,
            "state": session.state,
            "backend": session.backend,
            "created_at": session.created_at.isoformat(),
            "last_active_at": session.last_active_at.isoformat(),
        }

    async def session_list(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return persisted session snapshots."""
        params = params or {}
        scope = self._resolve_request_scope(params)
        sessions = self.core_service.list_session_snapshots(
            app_id=_scope_filter(params, "app_id", scope.app_id),
            project_id=_scope_filter(params, "project_id", scope.project_id),
            workspace_id=_scope_filter(params, "workspace_id", scope.workspace_id),
        )
        if sessions:
            return {"sessions": sessions}
        records = self.runtime_pool.list_sessions()
        if params.get("scope_mode") == "all":
            return {"sessions": records}
        filtered = [record for record in records if self._session_matches_scope(record, scope)]
        return {"sessions": filtered}

    async def session_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one persisted session snapshot."""
        session_id = _require_str(params, "session_id")
        session = self.runtime_pool.read_session(session_id)
        self._ensure_session_in_scope(session, self._resolve_request_scope(params), params)
        return {"session": session}

    async def core_session_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one Core v1.5 session record."""
        session_id = _require_str(params, "session_id")
        return {"session": _dump_core_record(self.core_service.get_session(session_id))}

    async def core_thread_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 thread records."""
        session_id = _optional_str(params, "session_id")
        scope = self._resolve_request_scope(params)
        threads = self.core_service.list_threads(
            session_id=session_id,
            app_id=_scope_filter(params, "app_id", scope.app_id),
            project_id=_scope_filter(params, "project_id", scope.project_id),
            workspace_id=_scope_filter(params, "workspace_id", scope.workspace_id),
        )
        return {"threads": [_dump_core_record(thread) for thread in threads], "count": len(threads)}

    async def core_turn_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one Core v1.5 turn record."""
        turn_id = _require_str(params, "turn_id")
        return {"turn": _dump_core_record(self.core_service.get_turn(turn_id))}

    async def core_turn_items(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 item records for a turn."""
        turn_id = _require_str(params, "turn_id")
        scope = self._resolve_request_scope(params)
        items = self.core_service.list_items(
            turn_id=turn_id,
            app_id=_scope_filter(params, "app_id", scope.app_id),
            project_id=_scope_filter(params, "project_id", scope.project_id),
            workspace_id=_scope_filter(params, "workspace_id", scope.workspace_id),
        )
        return {"items": [_dump_core_record(item) for item in items], "count": len(items)}

    async def core_trace_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 trace records."""
        trace_id = _optional_str(params, "trace_id")
        session_id = _optional_str(params, "session_id")
        turn_id = _optional_str(params, "turn_id")
        event_type = _optional_str(params, "event_type")
        scope = self._resolve_request_scope(params)
        traces = self.core_service.list_trace_records(
            trace_id=trace_id,
            session_id=session_id,
            turn_id=turn_id,
            event_type=event_type,
            app_id=_scope_filter(params, "app_id", scope.app_id),
            project_id=_scope_filter(params, "project_id", scope.project_id),
            workspace_id=_scope_filter(params, "workspace_id", scope.workspace_id),
        )
        return {"traces": [_dump_core_record(trace) for trace in traces], "count": len(traces)}

    async def core_approval_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 approval records."""
        decision = _optional_str(params, "decision")
        target_type = _optional_str(params, "target_type")
        target_id = _optional_str(params, "target_id")
        scope = self._resolve_request_scope(params)
        approvals = self.core_service.list_approvals(
            decision=decision,
            target_type=target_type,
            target_id=target_id,
            app_id=_scope_filter(params, "app_id", scope.app_id),
            project_id=_scope_filter(params, "project_id", scope.project_id),
            workspace_id=_scope_filter(params, "workspace_id", scope.workspace_id),
        )
        return {"approvals": [_dump_core_record(approval) for approval in approvals], "count": len(approvals)}

    async def core_retry_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 retry records."""
        session_id = _optional_str(params, "session_id")
        approval_id = _optional_str(params, "approval_id")
        status = _optional_str(params, "status")
        scope = self._resolve_request_scope(params)
        retries = self.core_service.list_retries(
            session_id=session_id,
            approval_id=approval_id,
            status=status,
            app_id=_scope_filter(params, "app_id", scope.app_id),
            project_id=_scope_filter(params, "project_id", scope.project_id),
            workspace_id=_scope_filter(params, "workspace_id", scope.workspace_id),
        )
        return {"retries": [_dump_core_record(retry) for retry in retries], "count": len(retries)}

    async def core_memory_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core memory records."""
        scope = self._resolve_request_scope(params)
        memories = self.core_service.list_memory_records(
            session_id=_optional_str(params, "session_id"),
            thread_id=_optional_str(params, "thread_id"),
            kind=_optional_str(params, "kind"),
            source_artifact_id=_optional_str(params, "source_artifact_id"),
            status=_optional_str(params, "status") or "active",
            trace_id=_optional_str(params, "trace_id"),
            app_id=_scope_filter(params, "app_id", scope.app_id),
            project_id=_scope_filter(params, "project_id", scope.project_id),
            workspace_id=_scope_filter(params, "workspace_id", scope.workspace_id),
        )
        return {"memories": [_dump_core_record(memory) for memory in memories], "count": len(memories)}

    async def core_artifact_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 artifact records."""
        owner_thread_id = _optional_str(params, "owner_thread_id")
        owner_session_id = _optional_str(params, "owner_session_id")
        owner_turn_id = _optional_str(params, "owner_turn_id")
        session_id = _optional_str(params, "session_id")
        turn_id = _optional_str(params, "turn_id")
        domain = _optional_str(params, "domain")
        kind = _optional_str(params, "kind")
        scope = self._resolve_request_scope(params)
        artifacts = self.core_service.list_artifacts(
            owner_thread_id=owner_thread_id,
            owner_session_id=owner_session_id or session_id,
            owner_turn_id=owner_turn_id or turn_id,
            domain=domain,
            kind=kind,
            app_id=_scope_filter(params, "app_id", scope.app_id),
            project_id=_scope_filter(params, "project_id", scope.project_id),
            workspace_id=_scope_filter(params, "workspace_id", scope.workspace_id),
        )
        return {"artifacts": [_dump_core_record(artifact) for artifact in artifacts], "count": len(artifacts)}

    async def core_artifact_lineage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return a Core artifact lineage graph."""
        scope = self._resolve_request_scope(params)
        artifact_id = _optional_str(params, "artifact_id")
        if artifact_id is not None:
            anchor = self.core_service.get_artifact(artifact_id)
            self._ensure_record_in_scope(_dump_core_record(anchor), scope, params, label="artifact")
        return self.core_service.artifact_lineage(
            artifact_id=artifact_id,
            owner_session_id=_optional_str(params, "owner_session_id") or _optional_str(params, "session_id"),
            owner_turn_id=_optional_str(params, "owner_turn_id") or _optional_str(params, "turn_id"),
            domain=_optional_str(params, "domain"),
            kind=_optional_str(params, "kind"),
            app_id=_scope_filter(params, "app_id", scope.app_id),
            project_id=_scope_filter(params, "project_id", scope.project_id),
            workspace_id=_scope_filter(params, "workspace_id", scope.workspace_id),
        )

    async def artifact_lineage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return artifact lineage and record a governance trace."""
        result = await self.core_artifact_lineage(params)
        scope = self._resolve_request_scope(params)
        trace_id = _optional_str(params, "trace_id") or self.trace_store.new_trace_id()
        artifact_ids = [
            artifact["artifact_id"]
            for artifact in result.get("artifacts", [])
            if isinstance(artifact, dict) and isinstance(artifact.get("artifact_id"), str)
        ]
        trace_record = {
            "trace_id": trace_id,
            "session_id": _optional_str(params, "owner_session_id") or _optional_str(params, "session_id"),
            "turn_id": _optional_str(params, "owner_turn_id") or _optional_str(params, "turn_id"),
            "app_id": scope.app_id,
            "project_id": scope.project_id,
            "workspace_id": scope.workspace_id,
            "event_type": "artifact.lineage",
            "status": "success",
            "artifact_ids": artifact_ids,
            "approval_ids": [],
            "input_summary": str(_optional_str(params, "artifact_id") or "artifact.lineage"),
            "metadata": {
                "filters": {
                    "artifact_id": _optional_str(params, "artifact_id"),
                    "domain": _optional_str(params, "domain"),
                    "kind": _optional_str(params, "kind"),
                },
                "count": result.get("count"),
            },
        }
        self.core_service.record_gateway_trace(trace_record)
        result["trace_id"] = trace_id
        return result

    async def core_job_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 job records."""
        thread_id = _optional_str(params, "thread_id")
        session_id = _optional_str(params, "session_id")
        turn_id = _optional_str(params, "turn_id")
        domain = _optional_str(params, "domain")
        status = _optional_str(params, "status")
        scope = self._resolve_request_scope(params)
        jobs = self.core_service.list_jobs(
            thread_id=thread_id,
            session_id=session_id,
            turn_id=turn_id,
            domain=domain,
            status=status,
            app_id=_scope_filter(params, "app_id", scope.app_id),
            project_id=_scope_filter(params, "project_id", scope.project_id),
            workspace_id=_scope_filter(params, "workspace_id", scope.workspace_id),
        )
        return {"jobs": [_dump_core_record(job) for job in jobs], "count": len(jobs)}

    async def job_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core job records."""
        return await self.core_job_list(params)

    async def job_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a queued Core job record."""
        workflow_id = _require_str(params, "workflow_id")
        scope = self._resolve_request_scope(params)
        job = self.core_service.create_job(
            workflow_id=workflow_id,
            domain=_optional_str(params, "domain"),
            session_id=_optional_str(params, "session_id"),
            thread_id=_optional_str(params, "thread_id"),
            turn_id=_optional_str(params, "turn_id"),
            trace_id=_optional_str(params, "trace_id"),
            scope=scope,
            external_job_ref=_optional_str(params, "external_job_ref"),
            parent_job_id=_optional_str(params, "parent_job_id"),
            metadata=_optional_dict(params, "metadata"),
        )
        return {"job": _dump_core_record(job)}

    async def job_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one Core job record."""
        job_id = _require_str(params, "job_id")
        job = self.core_service.get_job(job_id)
        self._ensure_record_in_scope(
            _dump_core_record(job),
            self._resolve_request_scope(params),
            params,
            label="job",
        )
        return {"job": _dump_core_record(job)}

    async def job_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return Core job lifecycle events."""
        job_id = _optional_str(params, "job_id")
        event_type = _optional_str(params, "event_type")
        status = _optional_str(params, "status")
        scope = self._resolve_request_scope(params)
        if job_id is not None:
            self._ensure_record_in_scope(
                _dump_core_record(self.core_service.get_job(job_id)),
                scope,
                params,
                label="job",
            )
        events = self.core_service.list_job_events(job_id=job_id, event_type=event_type, status=status)
        records = [_dump_core_record(event) for event in events]
        if params.get("scope_mode") != "all":
            records = [record for record in records if self._record_matches_scope(record, scope)]
        return {"events": records, "count": len(records)}

    async def job_cancel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel one Core job record."""
        job_id = _require_str(params, "job_id")
        reason = _optional_str(params, "reason")
        self._ensure_record_in_scope(
            _dump_core_record(self.core_service.get_job(job_id)),
            self._resolve_request_scope(params),
            params,
            label="job",
        )
        return {"job": _dump_core_record(self.core_service.cancel_job(job_id, reason=reason))}

    async def memory_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List session or thread memory records."""
        return await self.core_memory_list(params)

    async def memory_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one memory record."""
        memory = self.core_service.get_memory(
            _require_str(params, "memory_id"),
            trace_id=_optional_str(params, "trace_id"),
        )
        record = _dump_core_record(memory)
        self._ensure_record_in_scope(record, self._resolve_request_scope(params), params, label="memory")
        return {"memory": record}

    async def memory_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Build and persist a deterministic session summary."""
        memory = self.core_service.build_session_summary(
            session_id=_require_str(params, "session_id"),
            thread_id=_optional_str(params, "thread_id"),
            trace_id=_optional_str(params, "trace_id"),
        )
        return {"memory": _dump_core_record(memory)}

    async def memory_extract_from_artifacts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create artifact-backed memory refs for existing Core artifacts."""
        memories = self.core_service.extract_artifact_memory_refs(
            session_id=_optional_str(params, "session_id"),
            turn_id=_optional_str(params, "turn_id"),
            domain=_optional_str(params, "domain"),
            trace_id=_optional_str(params, "trace_id"),
        )
        return {"memories": [_dump_core_record(memory) for memory in memories], "count": len(memories)}

    async def session_transcript(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return a transcript rebuilt from persisted events."""
        session_id = _require_str(params, "session_id")
        session = self.runtime_pool.read_session(session_id)
        self._ensure_session_in_scope(session, self._resolve_request_scope(params), params)
        return {
            "session_id": session_id,
            "transcript": self.runtime_pool.read_transcript(session_id),
        }

    async def session_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return persisted protocol events for a session."""
        session_id = _require_str(params, "session_id")
        session = self.runtime_pool.read_session(session_id)
        self._ensure_session_in_scope(session, self._resolve_request_scope(params), params)
        return {
            "session_id": session_id,
            "events": self.runtime_pool.read_events(session_id),
        }

    async def turn_start(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run one turn and return normalized events plus final text."""
        session_id = _require_str(params, "session_id")
        user_input = _require_str(params, "input")
        domain = params.get("domain")
        if domain is not None and not isinstance(domain, str):
            raise ValueError("domain must be a string when provided")
        session = self.runtime_pool.read_session(session_id)
        scope = (
            self._resolve_request_scope(params)
            if _params_include_scope(params)
            else self._resolve_request_scope(
                params,
                app_id=_optional_text_value(session.get("app_id")),
                project_id=_optional_text_value(session.get("project_id")),
                workspace_id=_optional_text_value(session.get("workspace_id")),
            )
        )
        result = await self.runtime_pool.run_turn(
            session_id=session_id,
            user_input=user_input,
            domain=domain,
            scope=scope,
        )
        payload = result.model_dump(mode="json")
        payload["trace_id"] = _trace_id_from_events(payload.get("events", []))
        return payload

    async def turn_continue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Continue a pending turn when available."""
        session_id = _require_str(params, "session_id")
        session = self.runtime_pool.read_session(session_id)
        self._ensure_session_in_scope(session, self._resolve_request_scope(params), params)
        result = await self.runtime_pool.continue_turn(session_id=session_id)
        return result.model_dump(mode="json")

    async def turn_retry(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retry a previously saved turn context."""
        session_id = _require_str(params, "session_id")
        session = self.runtime_pool.read_session(session_id)
        self._ensure_session_in_scope(session, self._resolve_request_scope(params), params)
        approval_id = _optional_str(params, "approval_id")
        turn_id = _optional_str(params, "turn_id")
        if approval_id is None and turn_id is None:
            raise ValueError("approval_id or turn_id is required")
        context = (
            self.retry_store.get_by_approval(approval_id)
            if approval_id is not None
            else self.retry_store.get_by_turn(session_id, turn_id or "")
        )
        if context.get("session_id") != session_id:
            raise ValueError("retry context does not belong to the provided session_id")
        if context.get("status") == RETRY_RETRIED:
            raise ValueError(f"retry context already retried: {context.get('retry_id')}")
        if context.get("status") != RETRY_PENDING_APPROVAL:
            raise ValueError(f"retry context is not pending: {context.get('retry_id')}")
        resolved_approval_id = str(context.get("approval_id") or approval_id or "")
        if resolved_approval_id:
            approval = self.approval_store.get_approval(resolved_approval_id)
            if approval.get("status") != APPROVAL_APPROVED:
                raise ValueError(
                    f"approval is not approved: {approval.get('status')}"
                )
        reserved_context = self.retry_store.mark_retrying(str(context["retry_id"]))
        self.core_service.record_gateway_retry(reserved_context)
        result = await self.runtime_pool.run_turn(
            session_id=session_id,
            user_input=str(context.get("input") or ""),
            domain=context.get("domain") if isinstance(context.get("domain"), str) else None,
            skip_policy=True,
            retry_of_turn_id=str(context.get("source_turn_id") or ""),
            approval_id=resolved_approval_id or None,
        )
        payload = result.model_dump(mode="json")
        payload["trace_id"] = _trace_id_from_events(payload.get("events", []))
        updated_context = self.retry_store.mark_retried(
            str(context["retry_id"]),
            retry_turn_id=result.turn_id,
            retry_trace_id=payload["trace_id"],
        )
        self.core_service.record_gateway_retry(updated_context)
        payload["retry_context"] = updated_context
        return payload

    async def turn_interrupt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Interrupt or mark a session as interrupted."""
        session_id = _require_str(params, "session_id")
        session = self.runtime_pool.read_session(session_id)
        self._ensure_session_in_scope(session, self._resolve_request_scope(params), params)
        session = self.runtime_pool.interrupt_session(session_id)
        return {
            "session_id": session.session_id,
            "state": session.state,
            "interrupted": session.interrupted,
        }

    async def turn_stream(self, params: Dict[str, Any]):
        """Yield normalized events for one turn."""
        session_id = _require_str(params, "session_id")
        user_input = _require_str(params, "input")
        domain = params.get("domain")
        if domain is not None and not isinstance(domain, str):
            raise ValueError("domain must be a string when provided")
        session = self.runtime_pool.read_session(session_id)
        scope = (
            self._resolve_request_scope(params)
            if _params_include_scope(params)
            else self._resolve_request_scope(
                params,
                app_id=_optional_text_value(session.get("app_id")),
                project_id=_optional_text_value(session.get("project_id")),
                workspace_id=_optional_text_value(session.get("workspace_id")),
            )
        )
        async for event in self.runtime_pool.stream_turn(
            session_id=session_id,
            user_input=user_input,
            domain=domain,
            scope=scope,
        ):
            yield event

    async def meeting_capabilities(self) -> Dict[str, Any]:
        """Return configured Meeting MCP capabilities."""
        self.connector_registry.require_available(MEETING_VOICE_MCP_CONNECTOR_ID)
        return await self.meeting_service.capabilities()

    async def meeting_analyze_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text through the Meeting MCP workflow."""
        text = _require_str(params, "text")
        title = params.get("title")
        if title is not None and not isinstance(title, str):
            raise ValueError("title must be a string when provided")
        self.connector_registry.require_available(MEETING_VOICE_MCP_CONNECTOR_ID)
        return await self.meeting_service.analyze_text(text, title=title)

    async def meeting_process_recording(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compatibility facade for processing one real meeting recording."""
        path = _require_str(params, "path")
        engine = params.get("engine")
        language = params.get("language")
        title = params.get("title")
        session_id = _optional_str(params, "session_id")
        turn_id = _optional_str(params, "turn_id")
        for key, value in {"engine": engine, "language": language, "title": title}.items():
            if value is not None and not isinstance(value, str):
                raise ValueError(f"{key} must be a string when provided")
        scope = self._resolve_request_scope(params, app_id="meeting")
        warning = _meeting_legacy_deprecation_warning()
        trace_record = self.trace_store.record_event(
            GatewayEvent(
                type=warning["trace_event"],
                session_id=session_id,
                turn_id=turn_id,
                app_id=scope.app_id,
                project_id=scope.project_id,
                workspace_id=scope.workspace_id,
                data=warning,
            )
        )
        self.core_service.record_gateway_trace(trace_record)
        session = await self._ensure_legacy_meeting_session(session_id=session_id, scope=scope)
        turn = await self.runtime_pool.run_turn(
            session_id=session.session_id,
            user_input=f"请分析 {path}",
            domain="meeting",
            scope=scope,
        )
        turn_payload = turn.model_dump(mode="json")
        final_event = (turn_payload.get("events") or [{}])[-1]
        final_data = final_event.get("data") if isinstance(final_event, dict) else {}
        if final_event.get("type") == "turn.failed":
            raise RuntimeError(str(final_data.get("message") or "meeting workflow failed"))
        meeting = dict(final_data.get("meeting") or {})
        meeting["legacy_facade"] = True
        meeting["deprecation_warning"] = warning
        meeting["workflow_id"] = "meeting.workflow"
        meeting["gateway_session_id"] = session.session_id
        meeting["turn_id"] = turn.turn_id
        meeting["trace_id"] = turn_payload.get("trace_id")
        if isinstance(final_data.get("job"), dict):
            meeting["job"] = final_data["job"]
        if isinstance(final_data.get("job_id"), str):
            meeting["job_id"] = final_data["job_id"]
        for key in ("approval_required", "approval", "retry_context", "policy"):
            if key in final_data:
                meeting[key] = final_data[key]
        if engine is not None:
            meeting["engine"] = engine
        if language is not None:
            meeting["language"] = language
        if title is not None:
            meeting["title"] = title
        return meeting

    async def meeting_process_audio_dir(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process all supported recordings under the configured audio acceptance directory."""
        audio_dir = params.get("audio_dir")
        engine = params.get("engine")
        language = params.get("language")
        for key, value in {"audio_dir": audio_dir, "engine": engine, "language": language}.items():
            if value is not None and not isinstance(value, str):
                raise ValueError(f"{key} must be a string when provided")
        self.connector_registry.require_available(MEETING_VOICE_MCP_CONNECTOR_ID)
        return await self.meeting_service.process_audio_dir(
            audio_dir,
            engine=engine,
            language=language,
        )

    async def connector_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return registered connector descriptors."""
        domain = _optional_str(params, "domain")
        kind = _optional_str(params, "kind")
        health = _optional_str(params, "health")
        connectors = self.connector_registry.list_connectors(domain=domain, kind=kind, health=health)
        return {"connectors": connectors, "count": len(connectors)}

    async def connector_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one connector descriptor."""
        connector_id = _require_str(params, "connector_id")
        return {"connector": self.connector_registry.get_connector(connector_id)}

    async def connector_health(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh and return one connector health result."""
        connector_id = _require_str(params, "connector_id")
        return self.connector_registry.refresh_health(connector_id)

    async def connector_submit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Submit one connector execution job."""
        session_id = _optional_str(params, "session_id")
        return self.connector_execution_runtime.submit(
            connector_id=_require_str(params, "connector_id"),
            tool=_require_str(params, "tool"),
            payload=_optional_dict(params, "input"),
            session_id=session_id,
            turn_id=_optional_str(params, "turn_id"),
            trace_id=_optional_str(params, "trace_id"),
            scope=self._resolve_request_scope_for_session(params, session_id),
            defer=_optional_bool(params, "defer"),
            parent_artifact_ids=_optional_str_list(params, "parent_artifact_ids"),
            approval_id=_optional_str(params, "approval_id"),
        )

    async def connector_poll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Poll one connector execution job."""
        job_id = _require_str(params, "job_id")
        self._ensure_record_in_scope(
            _dump_core_record(self.core_service.get_job(job_id)),
            self._resolve_request_scope(params),
            params,
            label="job",
        )
        return self.connector_execution_runtime.poll(job_id=job_id)

    async def connector_cancel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel one connector execution job."""
        job_id = _require_str(params, "job_id")
        self._ensure_record_in_scope(
            _dump_core_record(self.core_service.get_job(job_id)),
            self._resolve_request_scope(params),
            params,
            label="job",
        )
        return self.connector_execution_runtime.cancel(
            job_id=job_id,
            reason=_optional_str(params, "reason"),
        )

    async def connector_collect(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Collect artifacts for one connector execution job."""
        job_id = _require_str(params, "job_id")
        self._ensure_record_in_scope(
            _dump_core_record(self.core_service.get_job(job_id)),
            self._resolve_request_scope(params),
            params,
            label="job",
        )
        return self.connector_execution_runtime.collect(job_id=job_id)

    async def artifact_register(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Register an existing local file as a harnessOS artifact."""
        path = _require_str(params, "path")
        session_id = _optional_str(params, "session_id")
        turn_id = _optional_str(params, "turn_id")
        domain = _optional_str(params, "domain")
        kind = _optional_str(params, "kind")
        metadata = params.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("metadata must be an object when provided")
        trace_id = _optional_str(params, "trace_id")
        merged_metadata = dict(metadata or {})
        if trace_id:
            merged_metadata["trace_id"] = trace_id
        scope = self._resolve_request_scope(params)
        artifact = self.artifact_registry.register_file(
            path,
            session_id=session_id,
            turn_id=turn_id,
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            domain=domain,
            kind=kind,
            metadata=merged_metadata,
        )
        artifact["app_id"] = scope.app_id
        artifact["project_id"] = scope.project_id
        artifact["workspace_id"] = scope.workspace_id
        self.core_service.record_gateway_artifact(artifact)
        trace_record = self.trace_store.record_artifact_operation(
            operation="register",
            artifact=artifact,
            trace_id=trace_id,
            metadata={"domain": domain, "kind": kind},
        )
        self.core_service.record_gateway_trace(trace_record)
        return {"artifact": artifact, "trace_id": trace_record["trace_id"]}

    async def artifact_register_external(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Register an external asset as metadata-only artifact."""
        scope = self._resolve_request_scope(params)
        artifact = self.artifact_registry.register_external(
            external_asset_uri=_require_str(params, "external_asset_uri"),
            session_id=_optional_str(params, "session_id"),
            turn_id=_optional_str(params, "turn_id"),
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            domain=_optional_str(params, "domain"),
            kind=_optional_str(params, "kind") or "external_asset",
            name=_optional_str(params, "name") or "",
            mime=_optional_str(params, "mime") or "application/octet-stream",
            preview_uri=_optional_str(params, "preview_uri"),
            thumbnail_uri=_optional_str(params, "thumbnail_uri"),
            metadata=_optional_dict(params, "metadata"),
        )
        artifact["app_id"] = scope.app_id
        artifact["project_id"] = scope.project_id
        artifact["workspace_id"] = scope.workspace_id
        self.core_service.record_gateway_artifact(artifact)
        trace_record = self.trace_store.record_artifact_operation(
            operation="register_external",
            artifact=artifact,
            trace_id=_optional_str(params, "trace_id"),
            metadata={"domain": artifact.get("domain"), "kind": artifact.get("kind")},
        )
        self.core_service.record_gateway_trace(trace_record)
        return {"artifact": artifact, "trace_id": trace_record["trace_id"]}

    async def artifact_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List registered artifacts."""
        session_id = _optional_str(params, "session_id")
        domain = _optional_str(params, "domain")
        kind = _optional_str(params, "kind")
        scope = self._resolve_request_scope(params)
        artifacts = self.artifact_registry.list_artifacts(
            session_id=session_id,
            domain=domain,
            kind=kind,
            app_id=_scope_filter(params, "app_id", scope.app_id),
            project_id=_scope_filter(params, "project_id", scope.project_id),
            workspace_id=_scope_filter(params, "workspace_id", scope.workspace_id),
        )
        trace_id = self.trace_store.new_trace_id()
        for artifact in artifacts:
            trace_record = self.trace_store.record_artifact_operation(
                operation="list",
                artifact=artifact,
                trace_id=trace_id,
                status="success",
                metadata={"filters": {"session_id": session_id, "domain": domain, "kind": kind}},
            )
            self.core_service.record_gateway_trace(trace_record)
        return {"artifacts": artifacts, "count": len(artifacts), "trace_id": trace_id}

    async def artifact_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return artifact metadata."""
        artifact_id = _require_str(params, "artifact_id")
        artifact = self.artifact_registry.get_artifact(artifact_id)
        self._ensure_record_in_scope(
            artifact,
            self._resolve_request_scope(params),
            params,
            label="artifact",
        )
        trace_record = self.trace_store.record_artifact_operation(operation="get", artifact=artifact)
        self.core_service.record_gateway_trace(trace_record)
        return {"artifact": artifact, "trace_id": trace_record["trace_id"]}

    async def artifact_read_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return artifact metadata without reading content."""
        payload = self.artifact_registry.read_metadata(_require_str(params, "artifact_id"))
        self._ensure_record_in_scope(
            payload["artifact"],
            self._resolve_request_scope(params),
            params,
            label="artifact",
        )
        trace_record = self.trace_store.record_artifact_operation(
            operation="read_metadata",
            artifact=payload["artifact"],
            trace_id=_optional_str(params, "trace_id"),
        )
        self.core_service.record_gateway_trace(trace_record)
        payload["trace_id"] = trace_record["trace_id"]
        return payload

    async def artifact_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read artifact content."""
        artifact_id = _require_str(params, "artifact_id")
        metadata_payload = self.artifact_registry.read_metadata(artifact_id)
        self._ensure_record_in_scope(
            metadata_payload["artifact"],
            self._resolve_request_scope(params),
            params,
            label="artifact",
        )
        try:
            payload = self.artifact_registry.read_artifact(artifact_id)
        except ArtifactReadBlockedError as exc:
            trace_record = self.trace_store.record_artifact_operation(
                operation="read",
                artifact=metadata_payload["artifact"],
                trace_id=_optional_str(params, "trace_id"),
                status="blocked",
                metadata={
                    "blocked_reason": exc.reason,
                    "suggested_method": "artifact.read_metadata",
                },
            )
            self.core_service.record_gateway_trace(trace_record)
            exc.trace_id = trace_record["trace_id"]
            raise
        except Exception:
            trace_record = self.trace_store.record_artifact_operation(
                operation="read",
                artifact=metadata_payload["artifact"],
                trace_id=_optional_str(params, "trace_id"),
                status="failed",
            )
            self.core_service.record_gateway_trace(trace_record)
            raise
        trace_record = self.trace_store.record_artifact_operation(
            operation="read",
            artifact=payload["artifact"],
            trace_id=_optional_str(params, "trace_id"),
        )
        self.core_service.record_gateway_trace(trace_record)
        payload["trace_id"] = trace_record["trace_id"]
        return payload

    async def trace_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List trace records."""
        trace_id = _optional_str(params, "trace_id")
        session_id = _optional_str(params, "session_id")
        turn_id = _optional_str(params, "turn_id")
        artifact_id = _optional_str(params, "artifact_id")
        event_type = _optional_str(params, "event_type")
        scope = self._resolve_request_scope(params)
        records = self.trace_store.list_records(
            trace_id=trace_id,
            session_id=session_id,
            turn_id=turn_id,
            artifact_id=artifact_id,
            event_type=event_type,
            app_id=_scope_filter(params, "app_id", scope.app_id),
            project_id=_scope_filter(params, "project_id", scope.project_id),
            workspace_id=_scope_filter(params, "workspace_id", scope.workspace_id),
        )
        return {"traces": records, "count": len(records)}

    async def trace_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return records for one trace id."""
        trace_id = _require_str(params, "trace_id")
        scope = self._resolve_request_scope(params)
        payload = self.trace_store.get_trace(trace_id)
        if params.get("scope_mode") == "all":
            return payload
        records = [record for record in payload["records"] if self._record_matches_scope(record, scope)]
        if not records:
            raise ValueError("trace does not belong to the requested scope")
        return {
            "trace_id": trace_id,
            "records": records,
            "count": len(records),
        }

    async def approval_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a pending approval request."""
        action = _require_str(params, "action")
        request_summary = _require_str(params, "request_summary")
        trace_id = _optional_str(params, "trace_id")
        session_id = _optional_str(params, "session_id")
        turn_id = _optional_str(params, "turn_id")
        risk_level = _optional_str(params, "risk_level") or "medium"
        metadata = params.get("metadata")
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("metadata must be an object when provided")
        scope = self._resolve_request_scope(params)
        approval = self.approval_store.request(
            action=action,
            request_summary=request_summary,
            trace_id=trace_id,
            session_id=session_id,
            turn_id=turn_id,
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            risk_level=risk_level,
            metadata=metadata,
        )
        self.core_service.record_gateway_approval(approval)
        trace_record = self.trace_store.record_approval_operation(
            operation="request",
            approval=approval,
            status="pending",
        )
        self.core_service.record_gateway_trace(trace_record)
        return {"approval": approval, "trace_id": trace_record["trace_id"]}

    async def approval_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List approval requests."""
        status = _optional_str(params, "status")
        session_id = _optional_str(params, "session_id")
        trace_id = _optional_str(params, "trace_id")
        scope = self._resolve_request_scope(params)
        approvals = self.approval_store.list_approvals(
            status=status,
            session_id=session_id,
            trace_id=trace_id,
            app_id=_scope_filter(params, "app_id", scope.app_id),
            project_id=_scope_filter(params, "project_id", scope.project_id),
            workspace_id=_scope_filter(params, "workspace_id", scope.workspace_id),
        )
        return {"approvals": approvals, "count": len(approvals)}

    async def approval_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one approval request."""
        approval_id = _require_str(params, "approval_id")
        approval = self.approval_store.get_approval(approval_id)
        self._ensure_record_in_scope(
            approval,
            self._resolve_request_scope(params),
            params,
            label="approval",
        )
        return {"approval": approval}

    async def approval_approve(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Approve one pending approval request."""
        approval_id = _require_str(params, "approval_id")
        reason = _optional_str(params, "reason")
        existing = self.approval_store.get_approval(approval_id)
        self._ensure_record_in_scope(
            existing,
            self._resolve_request_scope(params),
            params,
            label="approval",
        )
        if _workflow_binding_from_approval(existing):
            raise ProtocolError(
                "WORKFLOW_ACTION_FORBIDDEN",
                "Workflow-bound approvals must use approval.respond.",
                {"approval_id": approval_id, "replacement": "approval.respond", "legacy_method": "approval.approve"},
            )
        approval = self.approval_store.approve(approval_id, reason=reason)
        self.core_service.record_gateway_approval(approval)
        trace_record = self.trace_store.record_approval_operation(
            operation="approve",
            approval=approval,
            status="approved",
            metadata={"reason": reason},
        )
        self.core_service.record_gateway_trace(trace_record)
        return {"approval": approval, "trace_id": trace_record["trace_id"]}

    async def approval_reject(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reject one pending approval request."""
        approval_id = _require_str(params, "approval_id")
        reason = _optional_str(params, "reason")
        existing = self.approval_store.get_approval(approval_id)
        self._ensure_record_in_scope(
            existing,
            self._resolve_request_scope(params),
            params,
            label="approval",
        )
        if _workflow_binding_from_approval(existing):
            raise ProtocolError(
                "WORKFLOW_ACTION_FORBIDDEN",
                "Workflow-bound approvals must use approval.respond.",
                {"approval_id": approval_id, "replacement": "approval.respond", "legacy_method": "approval.reject"},
            )
        approval = self.approval_store.reject(approval_id, reason=reason)
        self.core_service.record_gateway_approval(approval)
        trace_record = self.trace_store.record_approval_operation(
            operation="reject",
            approval=approval,
            status="rejected",
            metadata={"reason": reason},
        )
        self.core_service.record_gateway_trace(trace_record)
        return {"approval": approval, "trace_id": trace_record["trace_id"]}

    async def approval_respond(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Approve or reject one approval request through the V3.5 unified method."""
        approval_id_value = params.get("approval_id")
        if not isinstance(approval_id_value, str) or not approval_id_value.strip():
            raise ProtocolError("INVALID_PARAMS", "approval_id is required", {"field": "approval_id"})
        approval_id = approval_id_value.strip()
        decision = params.get("decision")
        if decision == "approve":
            status = APPROVAL_APPROVED
        elif decision == "reject":
            status = APPROVAL_REJECTED
        else:
            raise ProtocolError(
                "APPROVAL_INVALID_DECISION",
                "decision must be approve or reject",
                {"approval_id": approval_id, "decision": decision},
            )
        reason = _optional_str(params, "reason")
        try:
            current = self.approval_store.get_approval(approval_id)
        except KeyError as exc:
            raise ProtocolError("APPROVAL_NOT_FOUND", f"Approval not found: {approval_id}", {"approval_id": approval_id}) from exc
        scope = self._resolve_request_scope(params)
        if not self._record_matches_scope(current, scope):
            trace_record = self.trace_store.record_approval_operation(
                operation="respond",
                approval=current,
                status="blocked",
                metadata={"error_code": "SCOPE_MISMATCH", "decision": decision},
            )
            self.core_service.record_gateway_trace(trace_record)
            raise ProtocolError(
                "SCOPE_MISMATCH",
                "approval does not belong to the requested scope",
                {"approval_id": approval_id, "trace_id": trace_record["trace_id"]},
            )
        current_binding = _workflow_binding_from_approval(current)
        if current_binding and current_binding.get("active") is False:
            raise ProtocolError(
                "WORKFLOW_APPROVAL_INACTIVE",
                "Workflow-bound approval is inactive.",
                {
                    "approval_id": approval_id,
                    "workflow_instance_id": current_binding.get("workflow_instance_id"),
                    "station_run_id": current_binding.get("station_run_id"),
                    "inactive_reason": current_binding.get("inactive_reason"),
                },
            )
        try:
            approval, idempotent = self.approval_store.respond(approval_id, status=status, reason=reason)
        except KeyError as exc:
            raise ProtocolError("APPROVAL_NOT_FOUND", f"Approval not found: {approval_id}", {"approval_id": approval_id}) from exc
        except ApprovalConflictError as exc:
            current_status = exc.current_status
            if current_status is None:
                try:
                    current_status = str(self.approval_store.get_approval(approval_id).get("status") or "")
                except KeyError:
                    current_status = None
            raise ProtocolError(
                "APPROVAL_CONFLICT",
                str(exc),
                {"approval_id": approval_id, "decision": decision, "current_status": current_status},
            ) from exc
        workflow_side_effect = None
        binding = _workflow_binding_from_approval(approval)
        if binding:
            workflow_side_effect = self._apply_workflow_approval_side_effect(
                approval,
                binding=binding,
                decision=decision,
                was_idempotent=idempotent,
                scope=scope,
            )
            approval = self.approval_store.get_approval(approval_id)
        if idempotent:
            return {
                "approval": approval,
                "status": approval.get("status"),
                "trace_id": approval.get("trace_id"),
                "idempotent": True,
                "workflow_side_effect": workflow_side_effect,
            }
        self.core_service.record_gateway_approval(approval)
        trace_record = self.trace_store.record_approval_operation(
            operation="respond",
            approval=approval,
            status=str(approval.get("status") or status),
            metadata={"decision": decision, "reason": reason},
        )
        self.core_service.record_gateway_trace(trace_record)
        return {
            "approval": approval,
            "status": approval.get("status"),
            "trace_id": trace_record["trace_id"],
            "idempotent": False,
            "workflow_side_effect": workflow_side_effect,
        }

    async def policy_evaluate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a user input or tool operation without executing it."""
        user_input = _optional_str(params, "input")
        tool_name = _optional_str(params, "tool_name")
        if user_input is None and tool_name is None:
            raise ValueError("input or tool_name is required")
        if tool_name is not None:
            decision = self.policy_evaluator.evaluate_tool(tool_name, params.get("tool_input"))
        else:
            decision = self.policy_evaluator.evaluate_user_input(
                user_input or "",
                domain=_optional_str(params, "domain"),
            )
        return {"decision": decision.model_dump()}

    async def workflow_list(self) -> Dict[str, Any]:
        """List registered domain workflows."""
        workflows = self.runtime_pool.orchestrator.registry.list_workflows()
        return {"workflows": workflows, "count": len(workflows)}

    async def pack_list(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List registered Domain Packs."""
        params = params or {}
        assembly_inputs = build_pack_assembly_inputs(
            connector_registry=self.connector_registry,
            app_registry=self.app_registry,
        )
        packs = self.runtime_pool.pack_registry.list_packs_with_assembly(
            domain=_optional_str(params, "domain"),
            status=_optional_str(params, "status"),
            supported_workflows=_supported_workflow_ids(self.runtime_pool.pack_registry),
            available_connectors=assembly_inputs["available_connectors"],
            app_enabled_connectors_by_domain=assembly_inputs["app_enabled_connectors_by_domain"],
            available_connector_capabilities=assembly_inputs["available_connector_capabilities"],
            available_policy_bundles=AVAILABLE_POLICY_BUNDLES,
            compatible_manifest_schema_versions=COMPATIBLE_PACK_SCHEMA_VERSIONS,
        )
        return {"packs": packs, "count": len(packs)}

    async def pack_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one Domain Pack manifest."""
        name = _optional_str(params, "name")
        domain = _optional_str(params, "domain")
        if name is None and domain is None:
            raise ValueError("name or domain is required")
        pack = self.runtime_pool.pack_registry.get_pack(name or domain or "")
        if pack is None:
            raise LookupError(f"Pack not found: {name or domain}")
        assembly_inputs = build_pack_assembly_inputs(
            connector_registry=self.connector_registry,
            app_registry=self.app_registry,
        )
        assembly = self.runtime_pool.pack_registry.evaluate_assembly(
            pack.name,
            supported_workflows=_supported_workflow_ids(self.runtime_pool.pack_registry),
            available_connectors=assembly_inputs["available_connectors"],
            app_enabled_connectors_by_domain=assembly_inputs["app_enabled_connectors_by_domain"],
            available_connector_capabilities=assembly_inputs["available_connector_capabilities"],
            available_policy_bundles=AVAILABLE_POLICY_BUNDLES,
            compatible_manifest_schema_versions=COMPATIBLE_PACK_SCHEMA_VERSIONS,
        )
        return {"pack": {**pack.to_dict(), "assembly": assembly.to_dict()}}

    async def pack_agents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return agent contracts for one Domain Pack."""
        name = _optional_str(params, "name")
        domain = _optional_str(params, "domain")
        if name is None and domain is None:
            raise ValueError("name or domain is required")
        pack = self.runtime_pool.pack_registry.get_pack(name or domain or "")
        if pack is None:
            raise LookupError(f"Pack not found: {name or domain}")
        agents = self.runtime_pool.pack_registry.list_agents(pack_name=pack.name)
        return {"agents": agents, "count": len(agents)}

    async def pack_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Build a Pack workflow template execution plan."""
        pack = self._pack_from_params(params)
        plan = build_pack_execution_plan(pack, template_id=_optional_str(params, "template_id"))
        return {"plan": plan.to_dict()}

    async def workflow_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Build a workflow template execution plan by workflow or domain."""
        pack = self._pack_from_workflow_params(params)
        plan = build_pack_execution_plan(pack, template_id=_optional_str(params, "template_id"))
        return {"plan": plan.to_dict()}

    async def pack_execute_stub(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a deterministic Pack workflow template stub execution."""
        pack = self._pack_from_params(params)
        result = execute_pack_stub(
            pack,
            template_id=_optional_str(params, "template_id"),
            inputs=_optional_dict(params, "inputs"),
        )
        payload = result.to_dict()
        if result.status != "stubbed":
            return payload
        payload.update(self._register_stub_artifacts(result, params))
        return payload

    async def workflow_execute_stub(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a deterministic workflow template stub execution by workflow or domain."""
        pack = self._pack_from_workflow_params(params)
        result = execute_pack_stub(
            pack,
            template_id=_optional_str(params, "template_id"),
            inputs=_optional_dict(params, "inputs"),
        )
        payload = result.to_dict()
        if result.status != "stubbed":
            return payload
        payload.update(self._register_stub_artifacts(result, params))
        return payload

    async def agent_list(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List registered Domain Pack agent contracts."""
        params = params or {}
        agents = self.runtime_pool.pack_registry.list_agents(
            pack_name=_optional_str(params, "pack_name"),
            domain=_optional_str(params, "domain"),
        )
        return {"agents": agents, "count": len(agents)}

    async def agent_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one Domain Pack agent contract."""
        agent_id = _require_str(params, "agent_id")
        agent = self.runtime_pool.pack_registry.get_agent(agent_id)
        if agent is None:
            raise LookupError(f"Agent not found: {agent_id}")
        return {"agent": agent}

    def _pack_from_params(self, params: Dict[str, Any]):
        name = _optional_str(params, "name")
        domain = _optional_str(params, "domain")
        if name is None and domain is None:
            raise ValueError("name or domain is required")
        pack = self.runtime_pool.pack_registry.get_pack(name or domain or "")
        if pack is None:
            raise LookupError(f"Pack not found: {name or domain}")
        return pack

    def _pack_from_workflow_params(self, params: Dict[str, Any]):
        workflow_id = _optional_str(params, "workflow_id")
        if workflow_id is not None:
            pack = self.runtime_pool.pack_registry.get_workflow_pack(workflow_id)
            if pack is None:
                raise LookupError(f"Workflow not found: {workflow_id}")
            return pack
        return self._pack_from_params(params)

    def _register_stub_artifacts(self, result: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        session_id = _optional_str(params, "session_id")
        turn_id = _optional_str(params, "turn_id")
        artifact_records = []
        artifact_by_kind: Dict[str, Dict[str, Any]] = {}
        for request in result.artifact_requests:
            kind = str(request["kind"])
            parent_ids = [
                artifact_by_kind[parent_kind]["artifact_id"]
                for parent_kind in request.get("parent_kinds", [])
                if parent_kind in artifact_by_kind
            ]
            artifact_path = self._write_stub_artifact_file(request)
            artifact = self.artifact_registry.register_file(
                str(artifact_path),
                session_id=session_id,
                turn_id=turn_id,
                domain=result.plan.domain,
                kind=kind,
                metadata={
                    "parent_artifact_ids": parent_ids,
                    "pack_name": result.plan.pack_name,
                    "template_id": result.plan.template_id,
                    "node_id": request.get("node_id"),
                    "stubbed": True,
                },
            )
            self.core_service.record_gateway_artifact(artifact)
            artifact_by_kind[kind] = artifact
            artifact_records.append(artifact)
        return {
            "artifact_records": artifact_records,
            "artifact_lineage": self.core_service.artifact_lineage(
                owner_session_id=session_id,
                owner_turn_id=turn_id,
                domain=result.plan.domain,
            ) if session_id or turn_id else {
                "artifacts": artifact_records,
                "edges": _artifact_edges_from_records(artifact_records),
                "roots": [
                    artifact["artifact_id"]
                    for artifact in artifact_records
                    if not artifact.get("metadata", {}).get("parent_ids")
                ],
                "leaves": _artifact_leaves_from_records(artifact_records),
                "count": len(artifact_records),
            },
        }

    def _write_stub_artifact_file(self, request: Dict[str, Any]) -> Path:
        output_dir = self.artifact_registry.root / "pack_stub"
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = str(request["name"]).replace("/", "_")
        path = output_dir / safe_name
        atomic_write_text(
            path,
            json.dumps(request.get("content", {}), ensure_ascii=False, indent=2) + "\n",
        )
        return path

    async def method_list(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return registered RPC methods and their public metadata."""
        params = params or {}
        include_planned = _optional_bool(params, "include_planned")
        include_forbidden = _optional_bool(params, "include_forbidden")
        methods = []
        for method in self.rpc_router.list_methods():
            contract = _method_contract(str(method.get("method")))
            surface = str(contract.get("surface") or "optional")
            if surface == "forbidden_by_default" and not include_forbidden:
                continue
            method.update(_method_discovery_metadata(str(method.get("method")), contract, runtime_handler=True))
            methods.append(method)
        for method in methods:
            try:
                schema = get_method_schema(str(method.get("method")))
            except KeyError:
                continue
            method.update(
                {
                    "schema_ref": schema["schema_ref"],
                    "sdk_exposure": schema["sdk_exposure"],
                    "stability": schema["stability"],
                    "runtime_handler": schema["runtime_handler"],
                }
            )
        if include_planned:
            existing = {method["method"] for method in methods}
            for schema in list_method_schemas(include_planned=True):
                if schema["runtime_handler"] or schema["method"] in existing:
                    continue
                contract = _method_contract(str(schema["method"]))
                methods.append(
                    {
                        "method": schema["method"],
                        "capability": schema["capability"],
                        **_method_discovery_metadata(str(schema["method"]), contract, runtime_handler=False),
                        "schema_ref": schema["schema_ref"],
                        "sdk_exposure": schema["sdk_exposure"],
                        "stability": schema["stability"],
                        "runtime_handler": False,
                    }
                )
            methods = sorted(methods, key=lambda item: item["method"])
        capabilities = {
            str(method["capability"]): True
            for method in methods
            if isinstance(method.get("capability"), str) and method.get("capability")
        }
        return {
            "methods": methods,
            "count": len(methods),
            "capabilities": dict(sorted(capabilities.items())),
        }

    async def events_subscribe(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a short-lived browser event subscription descriptor."""
        params = params or {}
        capabilities = params.get("_auth_capabilities")
        if not isinstance(capabilities, list) or not all(isinstance(item, str) for item in capabilities):
            raise ProtocolError(
                "AUTH_REQUIRED",
                "events.subscribe requires an external capability token.",
                {"reason": "missing_auth_context"},
            )
        channels = normalize_event_channels(params.get("channels"))
        ensure_channel_capabilities(channels, capabilities)
        scope = self._resolve_request_scope(params)
        ttl_seconds = _optional_int(params, "ttl_seconds", default=300)
        token, claims = issue_subscription_token(
            scope=scope,
            channels=channels,
            capabilities=capabilities,
            allowed_origins=params.get("_auth_allowed_origins") if isinstance(params.get("_auth_allowed_origins"), list) else (),
            ttl_seconds=ttl_seconds,
        )
        replay_cursor = make_event_cursor(scope, -1)
        query_channels = ",".join(channels)
        eventsource_url = f"/v1/events/subscribe?subscription_token={token}&channels={query_channels}"
        return {
            "subscription_id": claims.subscription_id,
            "transport": "eventsource",
            "eventsource_url": eventsource_url,
            "subscription_token": token,
            "replay_cursor": replay_cursor,
            "expires_at": claims.expires_at,
            "allowed_channels": list(channels),
        }

    async def workflow_template_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a workflow template and its initial editable draft."""
        scope = self._resolve_request_scope(params)
        template, draft = self.workflow_repository.create_template(_require_dict(params, "template"), scope=scope)
        trace_record = self._record_workflow_trace(
            "workflow.template.created",
            scope=scope,
            template=template.model_dump(mode="json"),
            metadata={"workflow_template_id": template.workflow_template_id, "draft_id": draft.workflow_draft_id},
        )
        return {
            "template": template.model_dump(mode="json"),
            "draft": draft.model_dump(mode="json"),
            "trace_id": trace_record["trace_id"],
        }

    async def workflow_template_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one workflow template in the requested scope."""
        scope = self._resolve_request_scope(params)
        template = self.workflow_repository.get_template(_require_str(params, "workflow_template_id"), scope=scope)
        return {"template": template.model_dump(mode="json")}

    async def workflow_template_list(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List workflow templates in scope."""
        params = params or {}
        scope = self._resolve_request_scope(params)
        templates = self.workflow_repository.list_templates(scope=scope, include_archived=_optional_bool(params, "include_archived"))
        payload = [template.model_dump(mode="json") for template in templates]
        return {"templates": payload, "count": len(payload)}

    async def workflow_template_update_draft(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update the latest draft for a workflow template, forking after publish."""
        scope = self._resolve_request_scope(params)
        draft, forked = self.workflow_repository.update_latest_draft(
            _require_str(params, "workflow_template_id"),
            _require_dict(params, "draft"),
            scope=scope,
            expected_revision=_optional_revision(params),
        )
        trace_record = self._record_workflow_trace(
            "workflow.template.draft_updated",
            scope=scope,
            template={"workflow_template_id": draft.workflow_template_id},
            metadata={
                "workflow_template_id": draft.workflow_template_id,
                "draft_id": draft.workflow_draft_id,
                "revision": draft.revision,
                "forked": forked,
                "base_version_id": draft.base_version_id,
            },
        )
        return {
            "draft": draft.model_dump(mode="json"),
            "draft_id": draft.workflow_draft_id,
            "forked": forked,
            "base_version_id": draft.base_version_id,
            "trace_id": trace_record["trace_id"],
        }

    async def workflow_draft_save(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Save a specific workflow draft by id."""
        scope = self._resolve_request_scope(params)
        draft = self.workflow_repository.save_draft(
            _require_str(params, "workflow_draft_id"),
            _require_dict(params, "draft"),
            scope=scope,
            expected_revision=_optional_revision(params),
        )
        trace_record = self._record_workflow_trace(
            "workflow.draft.saved",
            scope=scope,
            template={"workflow_template_id": draft.workflow_template_id},
            metadata={"workflow_template_id": draft.workflow_template_id, "draft_id": draft.workflow_draft_id, "revision": draft.revision},
        )
        return {"draft": draft.model_dump(mode="json"), "trace_id": trace_record["trace_id"]}

    async def workflow_template_publish(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Publish the latest editable draft as an immutable workflow version."""
        scope = self._resolve_request_scope(params)
        template, draft, version = self.workflow_repository.publish_template(
            _require_str(params, "workflow_template_id"),
            version=_require_str(params, "version"),
            scope=scope,
            expected_revision=_optional_revision(params),
        )
        trace_record = self._record_workflow_trace(
            "workflow.template.published",
            scope=scope,
            template=template.model_dump(mode="json"),
            metadata={
                "workflow_template_id": template.workflow_template_id,
                "draft_id": draft.workflow_draft_id,
                "workflow_version_id": version.workflow_version_id,
                "version": version.version,
            },
        )
        return {
            "template": template.model_dump(mode="json"),
            "draft": draft.model_dump(mode="json"),
            "version": version.model_dump(mode="json"),
            "trace_id": trace_record["trace_id"],
        }

    async def workflow_template_archive(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Archive a workflow template without deleting draft/version history."""
        scope = self._resolve_request_scope(params)
        before = self.workflow_repository.get_template(_require_str(params, "workflow_template_id"), scope=scope)
        template = self.workflow_repository.archive_template(before.workflow_template_id, scope=scope)
        idempotent = before.status == "archived"
        trace_record = self._record_workflow_trace(
            "workflow.template.archived",
            scope=scope,
            template=template.model_dump(mode="json"),
            metadata={"workflow_template_id": template.workflow_template_id, "idempotent": idempotent},
        )
        return {"template": template.model_dump(mode="json"), "idempotent": idempotent, "trace_id": trace_record["trace_id"]}

    async def workflow_version_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one immutable workflow version."""
        scope = self._resolve_request_scope(params)
        version = self.workflow_repository.get_version(_require_str(params, "workflow_version_id"), scope=scope)
        return {"version": version.model_dump(mode="json")}

    async def workflow_version_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List immutable workflow versions for a template."""
        scope = self._resolve_request_scope(params)
        versions = self.workflow_repository.list_versions(_require_str(params, "workflow_template_id"), scope=scope)
        payload = [version.model_dump(mode="json") for version in versions]
        return {"versions": payload, "count": len(payload)}

    async def workflow_instance_start(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start a deterministic dev/local workflow instance from an immutable version snapshot."""
        scope = self._resolve_request_scope(params)
        version = self._resolve_workflow_version_for_start(params, scope)
        template = self._template_from_version_snapshot(version.snapshot)
        ordered_stations = _linear_station_order(template)
        max_steps = _optional_positive_int(params, "max_steps")
        initial_artifact_ids = _optional_str_list(params, "input_artifact_ids")
        instance = WorkflowInstance(
            workflow_instance_id=_new_workflow_id("wfi"),
            workflow_template_id=version.workflow_template_id,
            workflow_version=version.version,
            workflow_version_id=version.workflow_version_id,
            session_id=_optional_str(params, "session_id"),
            thread_id=_optional_str(params, "thread_id"),
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            status=WorkflowInstanceStatus.CREATED,
            trace_id=self.trace_store.new_trace_id(),
            metadata={
                "input": _optional_dict(params, "input"),
                "source": "workflow_version_snapshot",
                "station_order": [station["station_id"] for station in ordered_stations],
                "execution_mode": "auto" if max_steps is None else "step",
                "max_steps": max_steps,
                "initial_artifact_ids": initial_artifact_ids,
            },
        )
        instance = self.workflow_repository.create_instance(instance, scope=scope)
        executed = self._execute_workflow_steps(
            instance,
            version_snapshot=version.snapshot,
            max_steps=max_steps,
            scope=scope,
        )
        instance = self.workflow_repository.get_instance(instance.workflow_instance_id, scope=scope)
        self._record_workflow_runtime_trace(
            "workflow.instance.started",
            scope=scope,
            workflow_instance=instance,
            metadata={
                "workflow_version_id": version.workflow_version_id,
                "version": version.version,
                "max_steps": params.get("max_steps"),
            },
        )
        return {
            "workflow_instance": instance.model_dump(mode="json"),
            "station_runs": [run.model_dump(mode="json") for run in executed],
            "resolved_version": {
                "workflow_template_id": version.workflow_template_id,
                "workflow_version_id": version.workflow_version_id,
                "version": version.version,
            },
        }

    async def workflow_instance_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one workflow instance."""
        scope = self._resolve_request_scope(params)
        instance = self.workflow_repository.get_instance(_require_str(params, "workflow_instance_id"), scope=scope)
        return {"workflow_instance": instance.model_dump(mode="json")}

    async def workflow_instance_list(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List workflow instances in scope."""
        params = params or {}
        scope = self._resolve_request_scope(params)
        instances = self.workflow_repository.list_instances(scope=scope, status=_optional_str(params, "status"))
        payload = [instance.model_dump(mode="json") for instance in instances]
        return {"workflow_instances": payload, "count": len(payload)}

    async def workflow_instance_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return a compact workflow instance status view."""
        scope = self._resolve_request_scope(params)
        instance = self.workflow_repository.get_instance(_require_str(params, "workflow_instance_id"), scope=scope)
        runs = self.workflow_repository.list_station_runs(instance.workflow_instance_id, scope=scope)
        quality = self.workflow_repository.list_quality_evaluations(scope=scope, workflow_instance_id=instance.workflow_instance_id)
        jobs = [self._job_summary_in_scope(job_id, scope=scope) for job_id in instance.job_ids]
        return {
            "status": {
                "workflow_instance_id": instance.workflow_instance_id,
                "status": _enum_value(instance.status),
                "current_station_ids": list(instance.current_station_ids),
                "job_ids": list(instance.job_ids),
                "artifact_ids": list(instance.artifact_ids),
                "station_run_count": len(runs),
                "station_run_status_counts": _status_counts([str(run.status) for run in runs]),
                "job_status_counts": _status_counts([str(job.get("status") or "") for job in jobs]),
                "artifact_count": len(instance.artifact_ids),
                "quality_evaluation_count": len(quality),
            }
        }

    async def station_output_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return output artifact summaries for one station run."""
        scope = self._resolve_request_scope(params)
        station_run = self.workflow_repository.get_station_run(_require_str(params, "station_run_id"), scope=scope)
        artifacts = [self._artifact_summary(artifact_id, scope=scope) for artifact_id in station_run.output_artifact_ids]
        return {
            "station_run_id": station_run.station_run_id,
            "artifacts": artifacts,
            "count": len(artifacts),
        }

    async def workflow_board_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return a redacted board summary for one workflow instance."""
        scope = self._resolve_request_scope(params)
        instance = self.workflow_repository.get_instance(_require_str(params, "workflow_instance_id"), scope=scope)
        runs = self.workflow_repository.list_station_runs(instance.workflow_instance_id, scope=scope)
        run_by_station: dict[str, list[StationRun]] = {}
        for run in runs:
            run_by_station.setdefault(run.station_id, []).append(run)
        version = self.workflow_repository.get_version(_instance_version_id(instance), scope=scope)
        template = self._template_from_version_snapshot(version.snapshot)
        station_entries = []
        all_artifact_ids: list[str] = []
        all_job_ids: list[str] = []
        all_quality_ids: list[str] = []
        approvals = self._workflow_approval_summaries(instance, scope=scope)
        for station in template.stations:
            station_runs = run_by_station.get(station.station_id, [])
            station_artifact_ids = _dedupe_stable(
                [artifact_id for run in station_runs for artifact_id in list(run.input_artifact_ids) + list(run.output_artifact_ids)]
            )
            station_quality_ids = _dedupe_stable(
                [evaluation_id for run in station_runs for evaluation_id in list(run.quality_evaluation_ids)]
            )
            station_job_ids = _dedupe_stable([run.job_id for run in station_runs if isinstance(run.job_id, str) and run.job_id])
            all_artifact_ids.extend(station_artifact_ids)
            all_job_ids.extend(station_job_ids)
            all_quality_ids.extend(station_quality_ids)
            station_entries.append(
                {
                    "station": _station_summary(station.model_dump(mode="json")),
                    "runs": [self._station_run_summary(run, scope=scope) for run in station_runs],
                    "status": _latest_station_status(station_runs),
                    "input_artifacts": [
                        self._artifact_summary(artifact_id, scope=scope)
                        for artifact_id in _dedupe_stable([artifact_id for run in station_runs for artifact_id in run.input_artifact_ids])
                    ],
                    "output_artifacts": [
                        self._artifact_summary(artifact_id, scope=scope)
                        for artifact_id in _dedupe_stable([artifact_id for run in station_runs for artifact_id in run.output_artifact_ids])
                    ],
                    "approvals": [
                        approval
                        for approval in approvals
                        if approval.get("workflow_binding", {}).get("station_id") == station.station_id
                    ],
                    "quality": [
                        self._quality_summary(evaluation_id, scope=scope)
                        for evaluation_id in station_quality_ids
                    ],
                    "trace_summary": self._workflow_trace_summary(instance, scope=scope, station_id=station.station_id),
                }
            )
        all_artifact_ids = _dedupe_stable(all_artifact_ids)
        all_job_ids = _dedupe_stable(all_job_ids + list(instance.job_ids))
        all_quality_ids = _dedupe_stable(all_quality_ids)
        board = {
            "workflow_instance": self._workflow_instance_summary(instance),
            "stations": station_entries,
            "current_station_ids": list(instance.current_station_ids),
            "jobs": [self._job_summary_in_scope(job_id, scope=scope) for job_id in all_job_ids],
            "artifacts": [self._artifact_summary(artifact_id, scope=scope) for artifact_id in all_artifact_ids],
            "approvals": approvals,
            "quality_evaluations": [self._quality_summary(evaluation_id, scope=scope) for evaluation_id in all_quality_ids],
            "trace_summary": self._workflow_trace_summary(instance, scope=scope),
        }
        return {"board": _sanitize_board_payload(board)}

    async def workflow_context_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one workflow context."""
        scope = self._resolve_request_scope(params)
        workflow_instance_id = _require_str(params, "workflow_instance_id")
        self.workflow_repository.get_instance(workflow_instance_id, scope=scope)
        context = self.workflow_repository.get_or_create_context(workflow_instance_id, scope=scope)
        return {"context": _sanitize_workflow_context(context)}

    async def workflow_context_update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update context.business using shallow merge or path set semantics."""
        scope = self._resolve_request_scope(params)
        workflow_instance_id = _require_str(params, "workflow_instance_id")
        self.workflow_repository.get_instance(workflow_instance_id, scope=scope)
        current = self.workflow_repository.get_or_create_context(workflow_instance_id, scope=scope)
        business = _updated_business_context(current.business, params)
        updated = current.model_copy(update={"business": business})
        context = self.workflow_repository.update_context(
            updated,
            scope=scope,
            expected_revision=_optional_revision(params, "expected_revision"),
        )
        trace_record = self._record_workflow_context_trace(
            "workflow.context.updated",
            scope=scope,
            context=context,
            metadata={
                "workflow_instance_id": workflow_instance_id,
                "context_revision": context.revision,
                "source": "workflow.context.update",
            },
        )
        return {"context": _sanitize_workflow_context(context), "trace_id": trace_record["trace_id"]}

    async def business_event_bind(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Bind a concrete business event to a context.business path set."""
        scope = self._resolve_request_scope(params)
        payload = params.get("binding") if isinstance(params.get("binding"), dict) else dict(params)
        payload = dict(payload)
        payload.setdefault("binding_id", f"beb_{uuid4().hex[:12]}")
        payload["workflow_instance_id"] = str(payload.get("workflow_instance_id") or _require_str(params, "workflow_instance_id"))
        payload.setdefault("event_type", params.get("event_type"))
        payload.setdefault("target_path", params.get("target_path"))
        payload.setdefault("payload_path", params.get("payload_path"))
        payload.setdefault("mode", params.get("mode") or "set")
        for key in ("scope", "app_id", "project_id", "workspace_id", "_auth_capabilities", "_auth_external"):
            payload.pop(key, None)
        try:
            binding = BusinessEventBinding.model_validate(payload)
        except Exception as exc:
            raise ProtocolError("BUSINESS_EVENT_BINDING_INVALID", str(exc), {"reason": "schema_validation_failed"}) from exc
        self.workflow_repository.get_instance(binding.workflow_instance_id, scope=scope)
        binding = self.workflow_repository.create_business_event_binding(binding, scope=scope)
        trace_record = self._record_workflow_context_trace(
            "business.event.binding.created",
            scope=scope,
            context=self.workflow_repository.get_or_create_context(binding.workflow_instance_id, scope=scope),
            metadata={
                "workflow_instance_id": binding.workflow_instance_id,
                "binding": binding.model_dump(mode="json"),
            },
        )
        return {"binding": _sanitize_board_payload(binding.model_dump(mode="json")), "trace_id": trace_record["trace_id"]}

    async def business_event_emit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Emit one business.* event and apply matching context bindings once."""
        scope = self._resolve_request_scope(params)
        payload = params.get("event")
        if not isinstance(payload, dict):
            raise ProtocolError("BUSINESS_EVENT_INVALID", "event must be an object.", {"field": "event"})
        payload = dict(payload)
        payload.setdefault("scope", scope.to_dict())
        try:
            event = BusinessEvent.model_validate(payload)
        except Exception as exc:
            raise ProtocolError("BUSINESS_EVENT_INVALID", str(exc), {"reason": "schema_validation_failed"}) from exc
        if event.workflow_instance_id is None:
            raise ProtocolError("BUSINESS_EVENT_INVALID", "workflow_instance_id is required.", {"field": "workflow_instance_id"})
        if event.scope and _scope_dict(event.scope) != scope.to_dict():
            raise ProtocolError("SCOPE_MISMATCH", "Business event scope does not match requested scope.", {"resource": "business_event"})
        self.workflow_repository.get_instance(event.workflow_instance_id, scope=scope)
        bindings = [
            binding
            for binding in self.workflow_repository.list_business_event_bindings(
                scope=scope,
                workflow_instance_id=event.workflow_instance_id,
                event_type=event.type,
            )
            if binding.enabled
        ]
        if not bindings:
            raise ProtocolError("BUSINESS_EVENT_UNBOUND", "No enabled binding for business event.", {"event_type": event.type})
        context = self.workflow_repository.get_or_create_context(event.workflow_instance_id, scope=scope)
        business = dict(context.business)
        applied_bindings = []
        for binding in bindings:
            value = _value_from_business_event(event, binding.payload_path)
            business = _set_context_business_path(business, binding.target_path, value)
            applied_bindings.append(binding.binding_id)
        event_key = event.event_id or event.idempotency_key
        if event_key:
            context, applied = self.workflow_repository.apply_business_event_context(
                event_key,
                context.model_copy(update={"business": business}),
                scope=scope,
            )
            if not applied:
                return {
                    "event": _sanitize_business_event(event),
                    "context": _sanitize_workflow_context(context),
                    "idempotent": True,
                    "trace_id": context.trace_id,
                }
        else:
            context = self.workflow_repository.update_context(context.model_copy(update={"business": business}), scope=scope)
        received_trace = self._record_workflow_context_trace(
            "business.event.received",
            scope=scope,
            context=context,
            metadata={
                "workflow_instance_id": event.workflow_instance_id,
                "context_revision": context.revision,
                "event": _sanitize_business_event(event),
                "applied_bindings": applied_bindings,
            },
        )
        self._record_workflow_context_trace(
            "workflow.context.updated",
            scope=scope,
            context=context,
            metadata={
                "workflow_instance_id": event.workflow_instance_id,
                "context_revision": context.revision,
                "source": "business.event.emit",
                "event_type": event.type,
                "applied_bindings": applied_bindings,
            },
        )
        return {
            "event": _sanitize_business_event(event),
            "context": _sanitize_workflow_context(context),
            "idempotent": False,
            "trace_id": received_trace["trace_id"],
        }

    async def workflow_patch_propose(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create one draft-only workflow patch proposal."""
        scope = self._resolve_request_scope(params)
        workflow_template_id = _require_str(params, "workflow_template_id")
        template = self.workflow_repository.get_template(workflow_template_id, scope=scope)
        patch_payload = params.get("patch")
        if not isinstance(patch_payload, dict):
            raise ProtocolError("WORKFLOW_PATCH_INVALID", "patch must be an object.", {"field": "patch"})
        draft_id = str(patch_payload.get("workflow_draft_id") or template.latest_draft_id or "")
        if not draft_id:
            raise ProtocolError("WORKFLOW_DRAFT_NOT_FOUND", "Workflow draft not found.", {"workflow_template_id": workflow_template_id})
        draft = self.workflow_repository.get_draft(draft_id, scope=scope)
        operation = _patch_operation(patch_payload)
        payload = _patch_payload(patch_payload)
        actor_type = _patch_actor_type(patch_payload)
        actor_id = str(patch_payload.get("actor_id") or patch_payload.get("proposed_by") or "unknown")
        risk_flags = _patch_risk_flags(operation, payload)
        workflow_patch_id = str(patch_payload.get("workflow_patch_id") or f"wfp_{uuid4().hex[:12]}")
        base_revision = int(patch_payload.get("base_revision") or draft.revision)
        patch = WorkflowPatch(
            workflow_patch_id=workflow_patch_id,
            workflow_template_id=workflow_template_id,
            workflow_draft_id=draft.workflow_draft_id,
            base_revision=base_revision,
            base_version_id=patch_payload.get("base_version_id") or draft.base_version_id or template.latest_published_version_id,
            operation=operation,
            payload=payload,
            diff=_build_patch_diff(
                workflow_patch_id=workflow_patch_id,
                workflow_draft_id=draft.workflow_draft_id,
                base_revision=base_revision,
                operation=operation,
                payload=payload,
                draft_payload=draft.draft,
                risk_flags=risk_flags,
            ),
            proposed_by=str(patch_payload.get("proposed_by") or actor_id),
            actor_type=actor_type,
            actor_id=actor_id,
            risk_flags=risk_flags,
            requires_approval=bool(risk_flags),
            metadata=_sanitize_board_payload(patch_payload.get("metadata") if isinstance(patch_payload.get("metadata"), dict) else {}),
        )
        patch = self.workflow_repository.propose_patch(patch, scope=scope)
        trace_record = self._record_workflow_patch_trace("workflow.patch.proposed", scope=scope, patch=patch, metadata={"idempotent": False})
        return {"patch": _sanitize_workflow_patch(patch), "trace_id": trace_record["trace_id"]}

    async def workflow_patch_diff(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return a redacted patch diff summary."""
        scope = self._resolve_request_scope(params)
        patch = self.workflow_repository.get_patch(_require_str(params, "workflow_patch_id"), scope=scope)
        return {"diff": _sanitize_board_payload(patch.diff)}

    async def workflow_patch_apply(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply one proposed patch to its draft."""
        scope = self._resolve_request_scope(params)
        actor_type = _patch_actor_type(params)
        patch = self.workflow_repository.get_patch(_require_str(params, "workflow_patch_id"), scope=scope)
        if patch.requires_approval and patch.status != WorkflowPatchStatus.APPLIED:
            trace_record = self._record_workflow_patch_trace(
                "workflow.patch.apply_blocked",
                scope=scope,
                patch=patch,
                metadata={"error_code": "WORKFLOW_ACTION_FORBIDDEN", "reason": "requires_approval"},
            )
            raise ProtocolError(
                "WORKFLOW_ACTION_FORBIDDEN",
                "High-risk workflow patches require an explicit approval flow before apply.",
                {
                    "workflow_patch_id": patch.workflow_patch_id,
                    "requires_approval": True,
                    "risk_flags": list(patch.risk_flags),
                    "trace_id": trace_record["trace_id"],
                },
            )
        patch, draft, idempotent = self.workflow_repository.apply_patch(
            patch.workflow_patch_id,
            scope=scope,
            actor_type=actor_type,
        )
        trace_record = self._record_workflow_patch_trace(
            "workflow.patch.applied",
            scope=scope,
            patch=patch,
            metadata={"idempotent": idempotent},
        )
        return {
            "patch": _sanitize_workflow_patch(patch),
            "draft": _sanitize_board_payload(draft.model_dump(mode="json")),
            "idempotent": idempotent,
            "trace_id": trace_record["trace_id"],
        }

    async def workflow_patch_reject(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Reject one proposed patch."""
        scope = self._resolve_request_scope(params)
        patch, idempotent = self.workflow_repository.reject_patch(
            _require_str(params, "workflow_patch_id"),
            scope=scope,
            reason=params.get("reason") if isinstance(params.get("reason"), str) else None,
        )
        trace_record = self._record_workflow_patch_trace(
            "workflow.patch.rejected",
            scope=scope,
            patch=patch,
            metadata={"idempotent": idempotent},
        )
        return {"patch": _sanitize_workflow_patch(patch), "idempotent": idempotent, "trace_id": trace_record["trace_id"]}

    async def workflow_instance_pause(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Pause a running workflow instance."""
        scope = self._resolve_request_scope(params)
        instance = self.workflow_repository.get_instance(_require_str(params, "workflow_instance_id"), scope=scope)
        if instance.status != WorkflowInstanceStatus.RUNNING:
            raise ProtocolError("WORKFLOW_INVALID_STATE", "Only running workflow instances can be paused.", {"status": instance.status})
        instance = instance.model_copy(update={"status": WorkflowInstanceStatus.PAUSED})
        instance = self.workflow_repository.update_instance(instance, scope=scope)
        self._record_workflow_runtime_trace("workflow.instance.paused", scope=scope, workflow_instance=instance, metadata={})
        return {"workflow_instance": instance.model_dump(mode="json")}

    async def workflow_instance_resume(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resume a paused workflow instance."""
        scope = self._resolve_request_scope(params)
        instance = self.workflow_repository.get_instance(_require_str(params, "workflow_instance_id"), scope=scope)
        if instance.status == WorkflowInstanceStatus.WAITING_APPROVAL:
            raise ProtocolError(
                "WORKFLOW_APPROVAL_REQUIRED",
                "Workflow instance is waiting for approval.respond.",
                {"workflow_instance_id": instance.workflow_instance_id},
            )
        if instance.status != WorkflowInstanceStatus.PAUSED:
            raise ProtocolError("WORKFLOW_INVALID_STATE", "Only paused workflow instances can be resumed.", {"status": instance.status})
        version_id = _instance_version_id(instance)
        version = self.workflow_repository.get_version(version_id, scope=scope)
        max_steps = _optional_positive_int(params, "max_steps")
        metadata = dict(instance.metadata or {})
        metadata["execution_mode"] = "auto" if max_steps is None else "step"
        metadata["max_steps"] = max_steps
        instance = self.workflow_repository.update_instance(
            instance.model_copy(update={"status": WorkflowInstanceStatus.RUNNING, "metadata": metadata}),
            scope=scope,
        )
        executed = self._execute_workflow_steps(
            instance,
            version_snapshot=version.snapshot,
            max_steps=max_steps,
            scope=scope,
        )
        instance = self.workflow_repository.get_instance(instance.workflow_instance_id, scope=scope)
        self._record_workflow_runtime_trace("workflow.instance.resumed", scope=scope, workflow_instance=instance, metadata={"max_steps": params.get("max_steps")})
        return {
            "workflow_instance": instance.model_dump(mode="json"),
            "station_runs": [run.model_dump(mode="json") for run in executed],
        }

    async def workflow_instance_cancel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a workflow instance without executing more stations."""
        scope = self._resolve_request_scope(params)
        instance = self.workflow_repository.get_instance(_require_str(params, "workflow_instance_id"), scope=scope)
        if instance.status == WorkflowInstanceStatus.CANCELLED:
            return {"workflow_instance": instance.model_dump(mode="json"), "idempotent": True}
        if instance.status not in {WorkflowInstanceStatus.CREATED, WorkflowInstanceStatus.RUNNING, WorkflowInstanceStatus.PAUSED, WorkflowInstanceStatus.WAITING_APPROVAL}:
            raise ProtocolError("WORKFLOW_INVALID_STATE", "Workflow instance cannot be cancelled from its current state.", {"status": instance.status})
        if instance.status == WorkflowInstanceStatus.WAITING_APPROVAL:
            for run in self.workflow_repository.list_station_runs(instance.workflow_instance_id, scope=scope):
                if run.status != StationRunStatus.WAITING_APPROVAL:
                    continue
                metadata = dict(run.metadata or {})
                approval_id = metadata.get("approval_id")
                if isinstance(approval_id, str) and approval_id:
                    self.approval_store.deactivate_workflow_binding(approval_id, reason="workflow_cancelled")
                cancelled_run = run.model_copy(
                    update={
                        "status": StationRunStatus.CANCELLED,
                        "completed_at": datetime.now(timezone.utc),
                        "failure_context": {"reason": "workflow_cancelled"},
                    }
                )
                self.workflow_repository.update_station_run(cancelled_run, scope=scope)
        instance = self.workflow_repository.update_instance(instance.model_copy(update={"status": WorkflowInstanceStatus.CANCELLED}), scope=scope)
        self._record_workflow_runtime_trace("workflow.instance.cancelled", scope=scope, workflow_instance=instance, metadata={"reason": _optional_str(params, "reason")})
        return {"workflow_instance": instance.model_dump(mode="json"), "idempotent": False}

    async def workflow_instance_retry(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retry the last failed station run for a failed or cancelled instance."""
        scope = self._resolve_request_scope(params)
        instance = self.workflow_repository.get_instance(_require_str(params, "workflow_instance_id"), scope=scope)
        if instance.status not in {WorkflowInstanceStatus.FAILED, WorkflowInstanceStatus.CANCELLED}:
            raise ProtocolError("WORKFLOW_INVALID_STATE", "Only failed or cancelled workflow instances can be retried.", {"status": instance.status})
        failed_runs = [
            run for run in self.workflow_repository.list_station_runs(instance.workflow_instance_id, scope=scope)
            if run.status == StationRunStatus.FAILED
        ]
        if not failed_runs:
            raise ProtocolError("WORKFLOW_INVALID_STATE", "Workflow instance has no failed station run to retry.", {"status": instance.status})
        rerun = self._rerun_station(failed_runs[-1], scope=scope)
        instance = self.workflow_repository.update_instance(instance.model_copy(update={"status": WorkflowInstanceStatus.RUNNING}), scope=scope)
        return {"workflow_instance": instance.model_dump(mode="json"), "station_run": rerun.model_dump(mode="json")}

    async def station_run_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one station run."""
        scope = self._resolve_request_scope(params)
        station_run = self.workflow_repository.get_station_run(_require_str(params, "station_run_id"), scope=scope)
        return {"station_run": station_run.model_dump(mode="json")}

    async def station_run_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List station runs for one workflow instance."""
        scope = self._resolve_request_scope(params)
        runs = self.workflow_repository.list_station_runs(_require_str(params, "workflow_instance_id"), scope=scope)
        payload = [run.model_dump(mode="json") for run in runs]
        return {"station_runs": payload, "count": len(payload)}

    async def station_rerun(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rerun one station run without overwriting its history."""
        scope = self._resolve_request_scope(params)
        old_run = self.workflow_repository.get_station_run(_require_str(params, "station_run_id"), scope=scope)
        rerun = self._rerun_station(old_run, scope=scope)
        return {"station_run": rerun.model_dump(mode="json")}

    async def quality_evaluation_create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a V3.6-F quality evaluation record."""
        scope = self._resolve_request_scope(params)
        payload = _require_dict(params, "evaluation")
        evaluation = self._build_quality_evaluation(payload, scope=scope)
        evaluation = self.workflow_repository.create_quality_evaluation(evaluation, scope=scope)
        attached = False
        if _optional_bool(params, "auto_attach"):
            attach_result = self._attach_quality_evaluation(
                evaluation,
                workflow_instance_id=evaluation.workflow_instance_id,
                station_run_id=evaluation.station_run_id,
                artifact_id=evaluation.artifact_id,
                allow_input_artifact=bool(payload.get("allow_input_artifact")),
                scope=scope,
            )
            evaluation = attach_result["evaluation"]
            attached = bool(attach_result["attached"])
        trace_record = self._record_quality_trace(
            "quality.evaluation.created",
            scope=scope,
            evaluation=evaluation,
            metadata={"attached": attached},
        )
        return {
            "evaluation": evaluation.model_dump(mode="json"),
            "attached": attached,
            "trace_id": trace_record["trace_id"],
        }

    async def quality_evaluation_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one quality evaluation."""
        scope = self._resolve_request_scope(params)
        evaluation = self.workflow_repository.get_quality_evaluation(_require_str(params, "evaluation_id"), scope=scope)
        return {"evaluation": evaluation.model_dump(mode="json")}

    async def quality_evaluation_list(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List quality evaluations in scope."""
        params = params or {}
        scope = self._resolve_request_scope(params)
        workflow_instance_id = _optional_str(params, "workflow_instance_id")
        station_run_id = _optional_str(params, "station_run_id")
        if workflow_instance_id is not None:
            self.workflow_repository.get_instance(workflow_instance_id, scope=scope)
        if station_run_id is not None:
            station_run = self.workflow_repository.get_station_run(station_run_id, scope=scope)
            if workflow_instance_id is not None and station_run.workflow_instance_id != workflow_instance_id:
                raise ProtocolError(
                    "QUALITY_EVALUATION_INVALID",
                    "Station run does not belong to the workflow instance.",
                    {"workflow_instance_id": workflow_instance_id, "station_run_id": station_run_id},
                )
        evaluations = self.workflow_repository.list_quality_evaluations(
            scope=scope,
            workflow_instance_id=workflow_instance_id,
            station_run_id=station_run_id,
        )
        payload = [evaluation.model_dump(mode="json") for evaluation in evaluations]
        return {"evaluations": payload, "count": len(payload)}

    async def quality_evaluation_attach(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Attach an existing quality evaluation to one station run artifact."""
        scope = self._resolve_request_scope(params)
        evaluation = self.workflow_repository.get_quality_evaluation(_require_str(params, "evaluation_id"), scope=scope)
        attach_result = self._attach_quality_evaluation(
            evaluation,
            workflow_instance_id=_optional_str(params, "workflow_instance_id") or evaluation.workflow_instance_id,
            station_run_id=_optional_str(params, "station_run_id") or evaluation.station_run_id,
            artifact_id=_optional_str(params, "artifact_id") or evaluation.artifact_id,
            allow_input_artifact=_optional_bool(params, "allow_input_artifact"),
            scope=scope,
        )
        evaluation = attach_result["evaluation"]
        trace_record = self._record_quality_trace(
            "quality.evaluation.attached",
            scope=scope,
            evaluation=evaluation,
            metadata={"idempotent": attach_result["idempotent"]},
        )
        return {
            "evaluation": evaluation.model_dump(mode="json"),
            "idempotent": attach_result["idempotent"],
            "trace_id": trace_record["trace_id"],
        }

    def _build_quality_evaluation(self, payload: Dict[str, Any], *, scope) -> QualityEvaluation:
        workflow_instance_id = _require_str(payload, "workflow_instance_id")
        station_run_id = _require_str(payload, "station_run_id")
        artifact_id = _optional_str(payload, "artifact_id")
        evaluator_type = _optional_str(payload, "evaluator_type") or EvaluatorType.RULE
        if evaluator_type not in {EvaluatorType.RULE, EvaluatorType.MANUAL, EvaluatorType.LLM_PLACEHOLDER}:
            raise ProtocolError("QUALITY_EVALUATION_UNSUPPORTED", "Quality evaluator type is unsupported.", {"evaluator_type": evaluator_type})
        instance, station_run = self._validate_quality_target(
            workflow_instance_id=workflow_instance_id,
            station_run_id=station_run_id,
            artifact_id=artifact_id,
            allow_input_artifact=bool(payload.get("allow_input_artifact")),
            scope=scope,
        )
        rubric_id = _optional_str(payload, "rubric_id")
        score = _optional_score(payload, "score")
        issues = _sanitize_quality_payload(_optional_dict_list(payload, "issues"))
        suggestions = _sanitize_quality_payload(_optional_dict_list(payload, "suggestions"))
        metadata = _sanitize_quality_payload(_optional_dict(payload, "metadata"))
        evaluator = _optional_str(payload, "evaluator")
        quality_contract = self._quality_contract_for_evaluation(instance, rubric_id=rubric_id, evaluator_type=str(evaluator_type), scope=scope)
        if quality_contract is not None:
            rubric_id = str(quality_contract["rubric_id"])
        if evaluator_type == EvaluatorType.LLM_PLACEHOLDER and not rubric_id:
            rubric_id = "llm_placeholder"
        if not rubric_id:
            raise ProtocolError("QUALITY_EVALUATION_INVALID", "Quality evaluation rubric_id is required.", {"field": "rubric_id"})
        status = self._resolve_quality_status(
            evaluator_type=str(evaluator_type),
            supplied_status=_optional_str(payload, "status"),
            score=score,
            issues=issues,
            quality_contract=quality_contract,
        )
        return QualityEvaluation(
            evaluation_id=_new_workflow_id("qe"),
            workflow_instance_id=workflow_instance_id,
            station_run_id=station_run.station_run_id,
            artifact_id=artifact_id,
            rubric_id=rubric_id,
            evaluator_type=evaluator_type,
            score=score,
            status=status,
            issues=issues,
            suggestions=suggestions,
            evaluator=evaluator or str(evaluator_type),
            metadata={
                **metadata,
                "binding": {
                    "attached": False,
                    "workflow_instance_id": workflow_instance_id,
                    "station_run_id": station_run.station_run_id,
                    "artifact_id": artifact_id,
                },
            },
        )

    def _validate_quality_target(
        self,
        *,
        workflow_instance_id: str,
        station_run_id: str,
        artifact_id: str | None,
        allow_input_artifact: bool,
        scope,
    ) -> tuple[WorkflowInstance, StationRun]:
        instance = self.workflow_repository.get_instance(workflow_instance_id, scope=scope)
        station_run = self.workflow_repository.get_station_run(station_run_id, scope=scope)
        if station_run.workflow_instance_id != instance.workflow_instance_id:
            raise ProtocolError(
                "QUALITY_EVALUATION_INVALID",
                "Station run does not belong to the workflow instance.",
                {"workflow_instance_id": workflow_instance_id, "station_run_id": station_run_id},
            )
        if artifact_id is not None:
            self._ensure_artifact_in_scope(artifact_id, scope=scope)
            valid_outputs = set(station_run.output_artifact_ids)
            valid_inputs = set(station_run.input_artifact_ids)
            if artifact_id not in valid_outputs and not (allow_input_artifact and artifact_id in valid_inputs):
                raise ProtocolError(
                    "QUALITY_EVALUATION_INVALID",
                    "Quality evaluation artifact must belong to the station run output artifacts.",
                    {
                        "artifact_id": artifact_id,
                        "station_run_id": station_run_id,
                        "allow_input_artifact": allow_input_artifact,
                    },
                )
        return instance, station_run

    def _quality_contract_for_evaluation(
        self,
        instance: WorkflowInstance,
        *,
        rubric_id: str | None,
        evaluator_type: str,
        scope,
    ) -> Dict[str, Any] | None:
        if evaluator_type == EvaluatorType.MANUAL:
            return None
        if evaluator_type == EvaluatorType.LLM_PLACEHOLDER:
            return None
        version = self.workflow_repository.get_version(_instance_version_id(instance), scope=scope)
        template = self._template_from_version_snapshot(version.snapshot)
        contracts = [
            contract.model_dump(mode="json") if hasattr(contract, "model_dump") else dict(contract)
            for contract in template.quality_contracts
        ]
        if rubric_id:
            for contract in contracts:
                if contract.get("rubric_id") == rubric_id:
                    return contract
            raise ProtocolError("QUALITY_EVALUATION_INVALID", "Rule evaluator rubric was not found.", {"rubric_id": rubric_id})
        if len(contracts) == 1:
            return contracts[0]
        raise ProtocolError("QUALITY_EVALUATION_INVALID", "Rule evaluator requires a matching quality contract rubric.", {"rubric_id": rubric_id})

    def _resolve_quality_status(
        self,
        *,
        evaluator_type: str,
        supplied_status: str | None,
        score: float | None,
        issues: list[dict[str, Any]],
        quality_contract: Dict[str, Any] | None,
    ) -> str:
        allowed = {"passed", "warning", "failed", "manual_required"}
        if supplied_status is not None and supplied_status not in allowed:
            raise ProtocolError("QUALITY_EVALUATION_INVALID", "Quality evaluation status is invalid.", {"status": supplied_status})
        if evaluator_type == EvaluatorType.MANUAL:
            return supplied_status or ("manual_required" if score is None else ("passed" if score >= 0.5 else "failed"))
        if evaluator_type == EvaluatorType.LLM_PLACEHOLDER:
            return "manual_required"
        threshold = quality_contract.get("threshold") if isinstance(quality_contract, dict) else None
        if score is None:
            return "failed" if issues else "manual_required"
        if isinstance(threshold, (int, float)):
            return "passed" if score >= float(threshold) else "failed"
        return supplied_status or ("passed" if score >= 0.5 else "failed")

    def _attach_quality_evaluation(
        self,
        evaluation: QualityEvaluation,
        *,
        workflow_instance_id: str,
        station_run_id: str,
        artifact_id: str | None,
        allow_input_artifact: bool,
        scope,
    ) -> Dict[str, Any]:
        _, station_run = self._validate_quality_target(
            workflow_instance_id=workflow_instance_id,
            station_run_id=station_run_id,
            artifact_id=artifact_id,
            allow_input_artifact=allow_input_artifact,
            scope=scope,
        )
        metadata = dict(evaluation.metadata or {})
        binding = metadata.get("binding") if isinstance(metadata.get("binding"), dict) else {}
        requested = {
            "workflow_instance_id": workflow_instance_id,
            "station_run_id": station_run_id,
            "artifact_id": artifact_id,
        }
        if binding.get("attached") is True:
            current = {
                "workflow_instance_id": binding.get("workflow_instance_id"),
                "station_run_id": binding.get("station_run_id"),
                "artifact_id": binding.get("artifact_id"),
            }
            if current != requested:
                raise ProtocolError(
                    "QUALITY_EVALUATION_ALREADY_ATTACHED",
                    "Quality evaluation is already attached to a different target.",
                    {"evaluation_id": evaluation.evaluation_id},
                )
            return {"evaluation": evaluation, "attached": False, "idempotent": True}
        metadata["binding"] = {**requested, "attached": True}
        updated = evaluation.model_copy(
            update={
                "workflow_instance_id": workflow_instance_id,
                "station_run_id": station_run_id,
                "artifact_id": artifact_id,
                "metadata": _sanitize_quality_payload(metadata),
            }
        )
        updated = self.workflow_repository.update_quality_evaluation(updated, scope=scope)
        quality_ids = _unique(list(station_run.quality_evaluation_ids) + [updated.evaluation_id])
        self.workflow_repository.update_station_run(station_run.model_copy(update={"quality_evaluation_ids": quality_ids}), scope=scope)
        return {"evaluation": updated, "attached": True, "idempotent": False}

    def _record_quality_trace(
        self,
        event_type: str,
        *,
        scope,
        evaluation: QualityEvaluation,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        event = GatewayEvent(
            type=event_type,
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            data=mask_value(
                {
                    "trace_id": self.trace_store.new_trace_id(),
                    "evaluation_id": evaluation.evaluation_id,
                    "workflow_instance_id": evaluation.workflow_instance_id,
                    "station_run_id": evaluation.station_run_id,
                    "artifact_id": evaluation.artifact_id,
                    "rubric_id": evaluation.rubric_id,
                    "evaluator_type": evaluation.evaluator_type,
                    "score": evaluation.score,
                    "status": evaluation.status,
                    **metadata,
                }
            ),
        )
        trace_record = self.trace_store.record_event(event)
        self.core_service.record_gateway_trace(trace_record)
        return trace_record

    def _workflow_instance_summary(self, instance: WorkflowInstance) -> Dict[str, Any]:
        return {
            "workflow_instance_id": instance.workflow_instance_id,
            "workflow_template_id": instance.workflow_template_id,
            "workflow_version": instance.workflow_version,
            "workflow_version_id": instance.workflow_version_id,
            "session_id": instance.session_id,
            "thread_id": instance.thread_id,
            "app_id": instance.app_id,
            "project_id": instance.project_id,
            "workspace_id": instance.workspace_id,
            "status": _enum_value(instance.status),
            "current_station_ids": list(instance.current_station_ids),
            "job_ids": list(instance.job_ids),
            "artifact_ids": list(instance.artifact_ids),
            "trace_id": instance.trace_id,
        }

    def _station_run_summary(self, station_run: StationRun, *, scope) -> Dict[str, Any]:
        return {
            "station_run_id": station_run.station_run_id,
            "workflow_instance_id": station_run.workflow_instance_id,
            "station_id": station_run.station_id,
            "status": _enum_value(station_run.status),
            "attempt": station_run.attempt,
            "rerun_of_station_run_id": station_run.rerun_of_station_run_id,
            "job_id": station_run.job_id,
            "input_artifact_ids": list(station_run.input_artifact_ids),
            "output_artifact_ids": list(station_run.output_artifact_ids),
            "input_bindings": dict(station_run.input_bindings),
            "output_bindings": dict(station_run.output_bindings),
            "quality_evaluation_ids": list(station_run.quality_evaluation_ids),
            "failure_context": _sanitize_board_payload(station_run.failure_context),
            "trace_id": station_run.trace_id,
            "started_at": station_run.started_at.isoformat() if station_run.started_at else None,
            "completed_at": station_run.completed_at.isoformat() if station_run.completed_at else None,
        }

    def _job_summary_in_scope(self, job_id: str, *, scope) -> Dict[str, Any]:
        job = _dump_core_record(self.core_service.get_job(job_id))
        self._ensure_record_in_scope(job, scope, {}, label="job")
        return _job_summary(job)

    def _artifact_summary(self, artifact_id: str, *, scope) -> Dict[str, Any]:
        artifact = self._ensure_artifact_in_scope(artifact_id, scope=scope)
        metadata = artifact.get("metadata") if isinstance(artifact.get("metadata"), dict) else {}
        return _sanitize_board_payload(
            {
                "artifact_id": artifact.get("artifact_id"),
                "session_id": artifact.get("session_id"),
                "turn_id": artifact.get("turn_id"),
                "app_id": artifact.get("app_id"),
                "project_id": artifact.get("project_id"),
                "workspace_id": artifact.get("workspace_id"),
                "domain": artifact.get("domain"),
                "kind": artifact.get("kind"),
                "name": artifact.get("name"),
                "mime": artifact.get("mime"),
                "size": artifact.get("size"),
                "uri": artifact.get("uri") or artifact.get("external_asset_uri"),
                "preview_uri": artifact.get("preview_uri"),
                "thumbnail_uri": artifact.get("thumbnail_uri"),
                "parent_ids": _artifact_parent_ids_from_gateway_record(artifact),
                "metadata": {
                    "workflow": metadata.get("workflow") if isinstance(metadata.get("workflow"), dict) else {},
                    "artifact_contract": metadata.get("artifact_contract") if isinstance(metadata.get("artifact_contract"), dict) else {},
                    "lineage": metadata.get("lineage") if isinstance(metadata.get("lineage"), dict) else {},
                    "quality": metadata.get("quality") if isinstance(metadata.get("quality"), dict) else {},
                },
            }
        )

    def _quality_summary(self, evaluation_id: str, *, scope) -> Dict[str, Any]:
        evaluation = self.workflow_repository.get_quality_evaluation(evaluation_id, scope=scope)
        return _sanitize_board_payload(
            {
                "evaluation_id": evaluation.evaluation_id,
                "workflow_instance_id": evaluation.workflow_instance_id,
                "station_run_id": evaluation.station_run_id,
                "artifact_id": evaluation.artifact_id,
                "rubric_id": evaluation.rubric_id,
                "evaluator_type": evaluation.evaluator_type,
                "score": evaluation.score,
                "status": evaluation.status,
                "issues": evaluation.issues,
                "suggestions": evaluation.suggestions,
                "evaluator": evaluation.evaluator,
                "created_at": evaluation.created_at.isoformat(),
            }
        )

    def _workflow_approval_summaries(self, instance: WorkflowInstance, *, scope) -> list[Dict[str, Any]]:
        approvals = self.approval_store.list_approvals(
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
        )
        summaries: list[Dict[str, Any]] = []
        for approval in approvals:
            binding = _workflow_binding_from_approval(approval)
            if not binding or binding.get("workflow_instance_id") != instance.workflow_instance_id:
                continue
            summaries.append(
                _sanitize_board_payload(
                    {
                        "approval_id": approval.get("approval_id"),
                        "trace_id": approval.get("trace_id"),
                        "action": approval.get("action"),
                        "status": approval.get("status"),
                        "risk_level": approval.get("risk_level"),
                        "request_summary": approval.get("request_summary"),
                        "created_at": approval.get("created_at"),
                        "decided_at": approval.get("decided_at"),
                        "workflow_binding": binding,
                    }
                )
            )
        return summaries

    def _workflow_trace_summary(
        self,
        instance: WorkflowInstance,
        *,
        scope,
        station_id: str | None = None,
    ) -> Dict[str, Any]:
        records = self.trace_store.list_records(
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
        )
        selected: list[dict[str, Any]] = []
        for record in records:
            metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
            event = metadata.get("event") if isinstance(metadata.get("event"), dict) else {}
            data = event.get("data") if isinstance(event.get("data"), dict) else {}
            if data.get("workflow_instance_id") != instance.workflow_instance_id:
                continue
            if station_id is not None and data.get("station_id") != station_id:
                continue
            selected.append(record)
        event_types = _dedupe_stable([str(record.get("event_type") or "") for record in selected])
        return {
            "count": len(selected),
            "event_types": event_types,
            "records": [_trace_record_summary(record) for record in selected[-10:]],
        }

    def _resolve_workflow_version_for_start(self, params: Dict[str, Any], scope):
        version_id = _optional_str(params, "workflow_version_id")
        if version_id is not None:
            return self.workflow_repository.get_version(version_id, scope=scope)
        workflow_template_id = _require_str(params, "workflow_template_id")
        workflow_version = _require_str(params, "workflow_version")
        return self.workflow_repository.get_version_by_template(workflow_template_id, workflow_version, scope=scope)

    def _execute_workflow_steps(
        self,
        instance: WorkflowInstance,
        *,
        version_snapshot: Dict[str, Any],
        max_steps: int | None,
        scope,
    ) -> list[StationRun]:
        template = self._template_from_version_snapshot(version_snapshot)
        ordered_stations = _linear_station_order(template)
        existing_runs = self.workflow_repository.list_station_runs(instance.workflow_instance_id, scope=scope)
        waiting_runs = [run for run in existing_runs if run.status == StationRunStatus.WAITING_APPROVAL]
        if waiting_runs:
            waiting = waiting_runs[-1]
            self.workflow_repository.update_instance(
                instance.model_copy(
                    update={
                        "status": WorkflowInstanceStatus.WAITING_APPROVAL,
                        "current_station_ids": [waiting.station_id],
                        "job_ids": _unique([job_id for run in existing_runs for job_id in ([run.job_id] if run.job_id else [])]),
                        "artifact_ids": _unique([artifact_id for run in existing_runs for artifact_id in run.output_artifact_ids]),
                    }
                ),
                scope=scope,
            )
            return []
        completed_station_ids = [run.station_id for run in existing_runs if run.status == StationRunStatus.COMPLETED]
        next_stations = [station for station in ordered_stations if station["station_id"] not in completed_station_ids]
        steps_to_run = len(next_stations) if max_steps is None else max_steps
        if steps_to_run <= 0:
            return []
        executed: list[StationRun] = []
        prior_outputs = _latest_outputs_by_station(existing_runs)
        if not prior_outputs:
            metadata = instance.metadata if isinstance(instance.metadata, dict) else {}
            raw_initial = metadata.get("initial_artifact_ids")
            if isinstance(raw_initial, list):
                prior_outputs = [item for item in raw_initial if isinstance(item, str) and item]
        instance = self.workflow_repository.update_instance(
            instance.model_copy(update={"status": WorkflowInstanceStatus.RUNNING, "current_station_ids": [next_stations[0]["station_id"]] if next_stations else []}),
            scope=scope,
        )
        steps_executed = 0
        for station in next_stations:
            if steps_executed >= steps_to_run:
                break
            if bool(station.get("approval_required")):
                waiting = self._create_workflow_approval_gate(
                    instance,
                    station=station,
                    input_artifact_ids=list(prior_outputs),
                    version_snapshot=version_snapshot,
                    scope=scope,
                )
                executed.append(waiting)
                return executed
            try:
                station_run = self._execute_station(instance, station=station, input_artifact_ids=list(prior_outputs), scope=scope)
            except Exception:
                self.workflow_repository.update_instance(
                    instance.model_copy(update={"status": WorkflowInstanceStatus.FAILED, "current_station_ids": [str(station["station_id"])]}),
                    scope=scope,
                )
                raise
            executed.append(station_run)
            prior_outputs = list(station_run.output_artifact_ids)
            steps_executed += 1
        latest_runs = self.workflow_repository.list_station_runs(instance.workflow_instance_id, scope=scope)
        all_done = len([run for run in latest_runs if run.status == StationRunStatus.COMPLETED and run.rerun_of_station_run_id is None]) >= len(ordered_stations)
        status = WorkflowInstanceStatus.COMPLETED if all_done else WorkflowInstanceStatus.RUNNING
        remaining_station_ids = []
        if not all_done:
            completed = {run.station_id for run in latest_runs if run.status == StationRunStatus.COMPLETED}
            remaining_station_ids = [station["station_id"] for station in ordered_stations if station["station_id"] not in completed][:1]
        updated = instance.model_copy(
            update={
                "status": status,
                "current_station_ids": remaining_station_ids,
                "job_ids": _unique([job_id for run in latest_runs for job_id in ([run.job_id] if run.job_id else [])]),
                "artifact_ids": _unique([artifact_id for run in latest_runs for artifact_id in run.output_artifact_ids]),
            }
        )
        self.workflow_repository.update_instance(updated, scope=scope)
        if status == WorkflowInstanceStatus.COMPLETED:
            self._record_workflow_runtime_trace("workflow.instance.completed", scope=scope, workflow_instance=updated, metadata={})
        return executed

    def _execute_station(self, instance: WorkflowInstance, *, station: Dict[str, Any], input_artifact_ids: list[str], scope) -> StationRun:
        station_id = str(station["station_id"])
        trace_id = self.trace_store.new_trace_id()
        input_bindings = self._resolve_station_input_bindings(station, input_artifact_ids=input_artifact_ids, scope=scope)
        flattened_inputs = _flatten_bindings(input_bindings)
        station_run = StationRun(
            station_run_id=_new_workflow_id("sr"),
            workflow_instance_id=instance.workflow_instance_id,
            station_id=station_id,
            status=StationRunStatus.RUNNING,
            input_artifact_ids=flattened_inputs,
            input_bindings=input_bindings,
            trace_id=trace_id,
            started_at=datetime.now(timezone.utc),
            metadata={
                "station_name": station.get("name"),
                "workflow_version_id": instance.workflow_version_id,
                "station_contracts": _station_contract_snapshot(station),
            },
        )
        station_run = self.workflow_repository.create_station_run(station_run, scope=scope)
        return self._complete_station_run(instance, station=station, station_run=station_run, scope=scope)

    def _complete_station_run(
        self,
        instance: WorkflowInstance,
        *,
        station: Dict[str, Any],
        station_run: StationRun,
        scope,
    ) -> StationRun:
        station_id = str(station["station_id"])
        trace_id = station_run.trace_id or self.trace_store.new_trace_id()
        output_contracts = _station_output_contracts(station, station_id=station_id)
        parent_artifact_ids = _dedupe_stable(station_run.input_artifact_ids)
        try:
            self._ensure_artifacts_in_scope(parent_artifact_ids, scope=scope)
        except ProtocolError as exc:
            failed = station_run.model_copy(
                update={
                    "status": StationRunStatus.FAILED,
                    "failure_context": {"error_code": exc.code, **dict(exc.data)},
                    "completed_at": datetime.now(timezone.utc),
                }
            )
            self.workflow_repository.update_station_run(failed, scope=scope)
            raise
        if station_run.status != StationRunStatus.RUNNING:
            station_run = station_run.model_copy(
                update={
                    "status": StationRunStatus.RUNNING,
                    "started_at": station_run.started_at or datetime.now(timezone.utc),
                    "trace_id": trace_id,
                }
            )
            station_run = self.workflow_repository.update_station_run(station_run, scope=scope)
        job = self.core_service.create_job(
            workflow_id=f"workflow.station.{station_id}",
            domain="workflow_runtime",
            session_id=instance.session_id,
            thread_id=instance.thread_id,
            trace_id=trace_id,
            scope=scope,
            metadata={
                "workflow_instance_id": instance.workflow_instance_id,
                "station_run_id": station_run.station_run_id,
                "station_id": station_id,
                "workflow_version_id": instance.workflow_version_id,
            },
        )
        output_bindings: dict[str, list[str]] = {}
        output_artifact_ids: list[str] = []
        try:
            for contract in output_contracts:
                artifact = self.artifact_registry.register_external(
                    external_asset_uri=f"harnessos://workflow/{instance.workflow_instance_id}/{station_run.station_run_id}/{contract['contract_id']}",
                    session_id=instance.session_id,
                    app_id=scope.app_id,
                    project_id=scope.project_id,
                    workspace_id=scope.workspace_id,
                    domain="workflow_runtime",
                    kind=str(contract["artifact_kind"]),
                    name=f"{station_id}-{contract['contract_id']}.json",
                    mime="application/json",
                    metadata=_workflow_artifact_metadata(
                        instance=instance,
                        station_run=station_run,
                        station=station,
                        contract=contract,
                        parent_artifact_ids=parent_artifact_ids,
                    ),
                )
                self.core_service.record_gateway_artifact(artifact)
                output_bindings.setdefault(str(contract["contract_id"]), []).append(artifact["artifact_id"])
                output_artifact_ids.append(artifact["artifact_id"])
            self.core_service.update_job(
                job_id=job.job_id,
                status="completed",
                progress=1.0,
                artifact_ids=output_artifact_ids,
                metadata={
                    "workflow_instance_id": instance.workflow_instance_id,
                    "station_run_id": station_run.station_run_id,
                    "station_id": station_id,
                    "message": "station completed",
                },
            )
            station_run = station_run.model_copy(
                update={
                    "status": StationRunStatus.COMPLETED,
                    "job_id": job.job_id,
                    "output_artifact_ids": output_artifact_ids,
                    "output_bindings": output_bindings,
                    "completed_at": datetime.now(timezone.utc),
                }
            )
            station_run = self.workflow_repository.update_station_run(station_run, scope=scope)
        except Exception as exc:
            failure_context = mask_value({"reason": "artifact_registration_failed", "error": str(exc)})
            failed = station_run.model_copy(
                update={
                    "status": StationRunStatus.FAILED,
                    "job_id": job.job_id,
                    "failure_context": failure_context,
                    "completed_at": datetime.now(timezone.utc),
                }
            )
            self.workflow_repository.update_station_run(failed, scope=scope)
            self.core_service.update_job(
                job_id=job.job_id,
                status="failed",
                progress=0.0,
                failure_context=failure_context,
                metadata={
                    "workflow_instance_id": instance.workflow_instance_id,
                    "station_run_id": station_run.station_run_id,
                    "station_id": station_id,
                },
            )
            raise ProtocolError(
                "WORKFLOW_ARTIFACT_REGISTRATION_FAILED",
                "Workflow artifact registration failed.",
                {
                    "workflow_instance_id": instance.workflow_instance_id,
                    "station_run_id": station_run.station_run_id,
                    "station_id": station_id,
                    "failure_context": failure_context,
                },
            ) from exc
        self._record_workflow_runtime_trace(
            "station.run.completed",
            scope=scope,
            workflow_instance=instance,
            metadata={
                "station_run_id": station_run.station_run_id,
                "station_id": station_id,
                "job_id": job.job_id,
                "artifact_ids": output_artifact_ids,
            },
        )
        return station_run

    def _resolve_station_input_bindings(
        self,
        station: Dict[str, Any],
        *,
        input_artifact_ids: list[str],
        scope,
    ) -> dict[str, list[str]]:
        contracts = _station_input_contracts(station)
        candidate_ids = _dedupe_stable(input_artifact_ids)
        for artifact_id in candidate_ids:
            self._ensure_artifact_in_scope(artifact_id, scope=scope)
        if not contracts:
            return {"__default_input__": candidate_ids} if candidate_ids else {}
        bindings: dict[str, list[str]] = {}
        remaining = list(candidate_ids)
        for contract in contracts:
            matched = []
            for artifact_id in list(remaining):
                artifact = self.artifact_registry.get_artifact(artifact_id)
                if _artifact_matches_contract(artifact, contract):
                    matched.append(artifact_id)
                    if contract.get("cardinality") == "one":
                        break
            if not matched and contract.get("required", True) and candidate_ids:
                first = self.artifact_registry.get_artifact(candidate_ids[0])
                raise ProtocolError(
                    "WORKFLOW_ARTIFACT_KIND_MISMATCH",
                    "Input artifact kind does not match station input contract.",
                    {
                        "station_id": station.get("station_id"),
                        "contract_id": contract.get("contract_id"),
                        "artifact_id": candidate_ids[0],
                        "artifact_kind": first.get("kind"),
                    },
                )
            if not matched and contract.get("required", True):
                raise ProtocolError(
                    "WORKFLOW_ARTIFACT_INPUT_MISSING",
                    "Required workflow input artifact is missing.",
                    {"station_id": station.get("station_id"), "contract_id": contract.get("contract_id")},
                )
            if contract.get("cardinality") == "one" and len(matched) > 1:
                raise ProtocolError(
                    "WORKFLOW_ARTIFACT_CONTRACT_INVALID",
                    "Workflow artifact contract cardinality was violated.",
                    {"station_id": station.get("station_id"), "contract_id": contract.get("contract_id")},
                )
            bindings[str(contract["contract_id"])] = matched
            remaining = [artifact_id for artifact_id in remaining if artifact_id not in matched]
        if candidate_ids and not any(candidate_id in _flatten_bindings(bindings) for candidate_id in candidate_ids):
            artifact_id = candidate_ids[0]
            artifact = self.artifact_registry.get_artifact(artifact_id)
            raise ProtocolError(
                "WORKFLOW_ARTIFACT_KIND_MISMATCH",
                "Input artifact kind does not match station input contracts.",
                {"station_id": station.get("station_id"), "artifact_id": artifact_id, "artifact_kind": artifact.get("kind")},
            )
        return bindings

    def _ensure_artifacts_in_scope(self, artifact_ids: list[str], *, scope) -> None:
        for artifact_id in artifact_ids:
            self._ensure_artifact_in_scope(artifact_id, scope=scope)

    def _ensure_artifact_in_scope(self, artifact_id: str, *, scope) -> dict[str, Any]:
        try:
            artifact = self.artifact_registry.get_artifact(artifact_id)
        except KeyError as exc:
            raise ProtocolError(
                "WORKFLOW_ARTIFACT_INPUT_MISSING",
                "Workflow input artifact was not found.",
                {"artifact_id": artifact_id},
            ) from exc
        if not self._record_matches_scope(artifact, scope):
            raise ProtocolError(
                "SCOPE_MISMATCH",
                "Workflow input artifact does not belong to the requested scope.",
                {"artifact_id": artifact_id},
            )
        return artifact

    def _create_workflow_approval_gate(
        self,
        instance: WorkflowInstance,
        *,
        station: Dict[str, Any],
        input_artifact_ids: list[str],
        version_snapshot: Dict[str, Any],
        scope,
    ) -> StationRun:
        station_id = str(station["station_id"])
        trace_id = self.trace_store.new_trace_id()
        input_bindings = self._resolve_station_input_bindings(station, input_artifact_ids=input_artifact_ids, scope=scope)
        flattened_inputs = _flatten_bindings(input_bindings)
        station_run = StationRun(
            station_run_id=_new_workflow_id("sr"),
            workflow_instance_id=instance.workflow_instance_id,
            station_id=station_id,
            status=StationRunStatus.WAITING_APPROVAL,
            input_artifact_ids=flattened_inputs,
            input_bindings=input_bindings,
            trace_id=trace_id,
            metadata={
                "station_name": station.get("name"),
                "workflow_version_id": instance.workflow_version_id,
                "station_contracts": _station_contract_snapshot(station),
            },
        )
        station_run = self.workflow_repository.create_station_run(station_run, scope=scope)
        workflow_binding = {
            "workflow_instance_id": instance.workflow_instance_id,
            "station_run_id": station_run.station_run_id,
            "station_id": station_id,
            "workflow_template_id": instance.workflow_template_id,
            "workflow_version_id": instance.workflow_version_id,
            "resume_strategy": "execute_station_then_continue",
            "reject_strategy": "block_workflow",
            "active": True,
            "inactive_reason": None,
            "workflow_side_effect_status": "pending",
            "workflow_side_effect_error": None,
        }
        approval = self.approval_store.request(
            action="workflow.station.approval",
            request_summary=f"Approve workflow station {station_id}",
            trace_id=trace_id,
            session_id=instance.session_id,
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            risk_level="medium",
            metadata={"workflow_binding": workflow_binding},
        )
        self.core_service.record_gateway_approval(approval)
        station_run = station_run.model_copy(update={"metadata": {**dict(station_run.metadata or {}), "approval_id": approval["approval_id"]}})
        station_run = self.workflow_repository.update_station_run(station_run, scope=scope)
        instance_metadata = dict(instance.metadata or {})
        instance_metadata["pending_approval_id"] = approval["approval_id"]
        updated = instance.model_copy(
            update={
                "status": WorkflowInstanceStatus.WAITING_APPROVAL,
                "current_station_ids": [station_id],
                "job_ids": _unique(list(instance.job_ids)),
                "artifact_ids": _unique(list(instance.artifact_ids)),
                "metadata": instance_metadata,
            }
        )
        updated = self.workflow_repository.update_instance(updated, scope=scope)
        trace_record = self.trace_store.record_approval_operation(
            operation="request",
            approval=approval,
            status="pending",
            metadata={"workflow_binding": workflow_binding},
        )
        self.core_service.record_gateway_trace(trace_record)
        self._record_workflow_runtime_trace(
            "station.run.waiting_approval",
            scope=scope,
            workflow_instance=updated,
            metadata={
                "station_run_id": station_run.station_run_id,
                "station_id": station_id,
                "approval_id": approval["approval_id"],
            },
        )
        return station_run

    def _apply_workflow_approval_side_effect(
        self,
        approval: Dict[str, Any],
        *,
        binding: Dict[str, Any],
        decision: str,
        was_idempotent: bool,
        scope,
    ) -> Dict[str, Any]:
        approval_id = str(approval["approval_id"])
        current_binding = _workflow_binding_from_approval(approval)
        if current_binding and current_binding.get("active") is False:
            raise ProtocolError(
                "WORKFLOW_APPROVAL_INACTIVE",
                "Workflow-bound approval is inactive.",
                {
                    "approval_id": approval_id,
                    "workflow_instance_id": current_binding.get("workflow_instance_id"),
                    "station_run_id": current_binding.get("station_run_id"),
                    "inactive_reason": current_binding.get("inactive_reason"),
                },
            )
        reserved_approval, marker = self.approval_store.begin_workflow_side_effect(approval_id)
        reserved_binding = _workflow_binding_from_approval(reserved_approval) or binding
        if marker == "applied":
            return {
                "status": "applied",
                "replayed": True,
                "workflow_instance_id": reserved_binding.get("workflow_instance_id"),
                "station_run_id": reserved_binding.get("station_run_id"),
            }
        if marker == "inactive":
            raise ProtocolError(
                "WORKFLOW_APPROVAL_INACTIVE",
                "Workflow-bound approval is inactive.",
                {
                    "approval_id": approval_id,
                    "workflow_instance_id": reserved_binding.get("workflow_instance_id"),
                    "station_run_id": reserved_binding.get("station_run_id"),
                    "inactive_reason": reserved_binding.get("inactive_reason"),
                },
            )
        if marker == "applying":
            raise ProtocolError(
                "WORKFLOW_APPROVAL_SIDE_EFFECT_FAILED",
                "Workflow approval side effect is already applying.",
                {
                    "approval_id": approval_id,
                    "workflow_instance_id": reserved_binding.get("workflow_instance_id"),
                    "station_run_id": reserved_binding.get("station_run_id"),
                    "recoverable": True,
                    "reason": "side_effect_in_progress",
                },
            )
        if marker == "none":
            return {
                "status": "applied",
                "replayed": False,
                "workflow_instance_id": None,
                "station_run_id": None,
            }
        try:
            if decision == "approve":
                result = self._resume_workflow_from_approval(reserved_binding, scope=scope)
            else:
                result = self._reject_workflow_from_approval(reserved_binding, scope=scope)
            self.approval_store.mark_workflow_side_effect(approval_id, status="applied")
            return {
                "status": "recovered" if was_idempotent else "applied",
                "replayed": False,
                **result,
            }
        except ProtocolError as exc:
            self.approval_store.mark_workflow_side_effect(approval_id, status="failed", error=str(exc))
            raise
        except Exception as exc:
            self.approval_store.mark_workflow_side_effect(approval_id, status="failed", error=str(exc))
            raise ProtocolError(
                "WORKFLOW_APPROVAL_SIDE_EFFECT_FAILED",
                "Workflow approval side effect failed.",
                {
                    "approval_id": approval_id,
                    "workflow_instance_id": reserved_binding.get("workflow_instance_id"),
                    "station_run_id": reserved_binding.get("station_run_id"),
                    "recoverable": True,
                },
            ) from exc

    def _resume_workflow_from_approval(self, binding: Dict[str, Any], *, scope) -> Dict[str, Any]:
        instance = self.workflow_repository.get_instance(str(binding["workflow_instance_id"]), scope=scope)
        station_run = self.workflow_repository.get_station_run(str(binding["station_run_id"]), scope=scope)
        if instance.status == WorkflowInstanceStatus.CANCELLED or station_run.status == StationRunStatus.CANCELLED:
            raise ProtocolError(
                "WORKFLOW_APPROVAL_INACTIVE",
                "Workflow approval cannot resume a cancelled workflow.",
                {
                    "workflow_instance_id": instance.workflow_instance_id,
                    "station_run_id": station_run.station_run_id,
                    "inactive_reason": "workflow_cancelled",
                },
            )
        if instance.status != WorkflowInstanceStatus.WAITING_APPROVAL or station_run.status != StationRunStatus.WAITING_APPROVAL:
            raise ProtocolError(
                "WORKFLOW_INVALID_STATE",
                "Workflow is not waiting on this approval.",
                {"workflow_instance_id": instance.workflow_instance_id, "station_run_id": station_run.station_run_id, "status": instance.status},
            )
        version = self.workflow_repository.get_version(_instance_version_id(instance), scope=scope)
        template = self._template_from_version_snapshot(version.snapshot)
        station = _station_by_id(template, station_run.station_id)
        station_run = self._complete_station_run(instance, station=station, station_run=station_run, scope=scope)
        latest_runs = self.workflow_repository.list_station_runs(instance.workflow_instance_id, scope=scope)
        metadata = dict(instance.metadata or {})
        metadata.pop("pending_approval_id", None)
        instance = self.workflow_repository.update_instance(
            instance.model_copy(
                update={
                    "status": WorkflowInstanceStatus.RUNNING,
                    "job_ids": _unique([job_id for run in latest_runs for job_id in ([run.job_id] if run.job_id else [])]),
                    "artifact_ids": _unique([artifact_id for run in latest_runs for artifact_id in run.output_artifact_ids]),
                    "metadata": metadata,
                }
            ),
            scope=scope,
        )
        max_steps = metadata.get("max_steps") if metadata.get("execution_mode") == "step" else None
        if max_steps is None:
            self._execute_workflow_steps(instance, version_snapshot=version.snapshot, max_steps=None, scope=scope)
            self._refresh_workflow_instance_progress(instance, version_snapshot=version.snapshot, scope=scope)
        else:
            self._refresh_workflow_instance_progress(instance, version_snapshot=version.snapshot, scope=scope)
        return {"workflow_instance_id": instance.workflow_instance_id, "station_run_id": station_run.station_run_id}

    def _reject_workflow_from_approval(self, binding: Dict[str, Any], *, scope) -> Dict[str, Any]:
        instance = self.workflow_repository.get_instance(str(binding["workflow_instance_id"]), scope=scope)
        station_run = self.workflow_repository.get_station_run(str(binding["station_run_id"]), scope=scope)
        if instance.status == WorkflowInstanceStatus.CANCELLED or station_run.status == StationRunStatus.CANCELLED:
            raise ProtocolError(
                "WORKFLOW_APPROVAL_INACTIVE",
                "Workflow approval cannot reject a cancelled workflow.",
                {
                    "workflow_instance_id": instance.workflow_instance_id,
                    "station_run_id": station_run.station_run_id,
                    "inactive_reason": "workflow_cancelled",
                },
            )
        station_run = station_run.model_copy(
            update={
                "status": StationRunStatus.FAILED,
                "failure_context": {"reason": "approval_rejected"},
                "completed_at": datetime.now(timezone.utc),
            }
        )
        self.workflow_repository.update_station_run(station_run, scope=scope)
        metadata = dict(instance.metadata or {})
        metadata.pop("pending_approval_id", None)
        instance = self.workflow_repository.update_instance(
            instance.model_copy(
                update={
                    "status": WorkflowInstanceStatus.BLOCKED,
                    "current_station_ids": [station_run.station_id],
                    "metadata": metadata,
                }
            ),
            scope=scope,
        )
        self._record_workflow_runtime_trace(
            "workflow.instance.blocked",
            scope=scope,
            workflow_instance=instance,
            metadata={"station_run_id": station_run.station_run_id, "reason": "approval_rejected"},
        )
        return {"workflow_instance_id": instance.workflow_instance_id, "station_run_id": station_run.station_run_id}

    def _refresh_workflow_instance_progress(self, instance: WorkflowInstance, *, version_snapshot: Dict[str, Any], scope) -> WorkflowInstance:
        template = self._template_from_version_snapshot(version_snapshot)
        ordered_stations = _linear_station_order(template)
        latest_runs = self.workflow_repository.list_station_runs(instance.workflow_instance_id, scope=scope)
        completed = {run.station_id for run in latest_runs if run.status == StationRunStatus.COMPLETED and run.rerun_of_station_run_id is None}
        waiting = [run for run in latest_runs if run.status == StationRunStatus.WAITING_APPROVAL]
        all_done = len(completed) >= len(ordered_stations)
        if waiting:
            status = WorkflowInstanceStatus.WAITING_APPROVAL
            current_station_ids = [waiting[-1].station_id]
        elif all_done:
            status = WorkflowInstanceStatus.COMPLETED
            current_station_ids = []
        else:
            status = WorkflowInstanceStatus.RUNNING
            current_station_ids = [station["station_id"] for station in ordered_stations if station["station_id"] not in completed][:1]
        updated = instance.model_copy(
            update={
                "status": status,
                "current_station_ids": current_station_ids,
                "job_ids": _unique([job_id for run in latest_runs for job_id in ([run.job_id] if run.job_id else [])]),
                "artifact_ids": _unique([artifact_id for run in latest_runs for artifact_id in run.output_artifact_ids]),
            }
        )
        updated = self.workflow_repository.update_instance(updated, scope=scope)
        if status == WorkflowInstanceStatus.COMPLETED:
            self._record_workflow_runtime_trace("workflow.instance.completed", scope=scope, workflow_instance=updated, metadata={})
        return updated

    def _rerun_station(self, old_run: StationRun, *, scope) -> StationRun:
        instance = self.workflow_repository.get_instance(old_run.workflow_instance_id, scope=scope)
        metadata = old_run.metadata if isinstance(old_run.metadata, dict) else {}
        contracts = metadata.get("station_contracts") if isinstance(metadata.get("station_contracts"), dict) else {}
        station = {
            "station_id": old_run.station_id,
            "name": metadata.get("station_name") if isinstance(metadata.get("station_name"), str) else old_run.station_id,
            "input_contracts": contracts.get("input_contracts") if isinstance(contracts.get("input_contracts"), list) else [],
            "output_contracts": contracts.get("output_contracts") if isinstance(contracts.get("output_contracts"), list) else [],
            "metadata": {},
        }
        trace_id = self.trace_store.new_trace_id()
        rerun = StationRun(
            station_run_id=_new_workflow_id("sr"),
            workflow_instance_id=instance.workflow_instance_id,
            station_id=old_run.station_id,
            status=StationRunStatus.RUNNING,
            attempt=old_run.attempt + 1,
            rerun_of_station_run_id=old_run.station_run_id,
            input_artifact_ids=list(old_run.input_artifact_ids),
            input_bindings=dict(old_run.input_bindings),
            trace_id=trace_id,
            started_at=datetime.now(timezone.utc),
            metadata={"station_name": station["name"], "workflow_version_id": instance.workflow_version_id, "station_contracts": _station_contract_snapshot(station)},
        )
        rerun = self.workflow_repository.create_station_run(rerun, scope=scope)
        rerun = self._complete_station_run(instance, station=station, station_run=rerun, scope=scope)
        self._record_workflow_runtime_trace(
            "station.run.rerun_requested",
            scope=scope,
            workflow_instance=instance,
            metadata={
                "station_run_id": rerun.station_run_id,
                "rerun_of_station_run_id": old_run.station_run_id,
                "attempt": rerun.attempt,
            },
        )
        return rerun

    def _template_from_version_snapshot(self, snapshot: Dict[str, Any]) -> WorkflowTemplate:
        try:
            return WorkflowTemplate.model_validate(snapshot)
        except Exception as exc:
            raise ProtocolError("WORKFLOW_SCHEMA_INVALID", "Workflow version snapshot is invalid.", {"reason": "snapshot_validation_failed"}) from exc

    def _record_workflow_runtime_trace(self, event_type: str, *, scope, workflow_instance: WorkflowInstance, metadata: Dict[str, Any]) -> Dict[str, Any]:
        event = GatewayEvent(
            type=event_type,
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            data={
                "trace_id": self.trace_store.new_trace_id(),
                "workflow_id": workflow_instance.workflow_template_id,
                "workflow_instance_id": workflow_instance.workflow_instance_id,
                **metadata,
            },
        )
        trace_record = self.trace_store.record_event(event)
        self.core_service.record_gateway_trace(trace_record)
        return trace_record

    def _record_workflow_trace(self, event_type: str, *, scope, template: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        event = GatewayEvent(
            type=event_type,
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            data={
                "trace_id": self.trace_store.new_trace_id(),
                "workflow_id": template.get("workflow_template_id"),
                **metadata,
            },
        )
        trace_record = self.trace_store.record_event(event)
        self.core_service.record_gateway_trace(trace_record)
        return trace_record

    def _record_workflow_context_trace(self, event_type: str, *, scope, context: WorkflowContext, metadata: Dict[str, Any]) -> Dict[str, Any]:
        event = GatewayEvent(
            type=event_type,
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            data={
                "trace_id": self.trace_store.new_trace_id(),
                "workflow_instance_id": context.workflow_instance_id,
                "context_revision": context.revision,
                **_sanitize_board_payload(metadata),
            },
        )
        trace_record = self.trace_store.record_event(event)
        self.core_service.record_gateway_trace(trace_record)
        return trace_record

    def _record_workflow_patch_trace(self, event_type: str, *, scope, patch: WorkflowPatch, metadata: Dict[str, Any]) -> Dict[str, Any]:
        event = GatewayEvent(
            type=event_type,
            app_id=scope.app_id,
            project_id=scope.project_id,
            workspace_id=scope.workspace_id,
            data={
                "trace_id": self.trace_store.new_trace_id(),
                "workflow_template_id": patch.workflow_template_id,
                "workflow_draft_id": patch.workflow_draft_id,
                "workflow_patch_id": patch.workflow_patch_id,
                "operation": _enum_value(patch.operation),
                "status": _enum_value(patch.status),
                "base_revision": patch.base_revision,
                "resulting_draft_revision": patch.resulting_draft_revision,
                "risk_flags": list(patch.risk_flags),
                **_sanitize_board_payload(metadata),
            },
        )
        trace_record = self.trace_store.record_event(event)
        self.core_service.record_gateway_trace(trace_record)
        return trace_record

    async def handle_rpc(self, request: RpcRequest) -> RpcResponse:
        """Handle one JSON-RPC style request."""
        try:
            result = await self._dispatch(request.method, request.params)
            return RpcResponse(id=request.id, result=result)
        except Exception as exc:
            return RpcResponse(
                id=request.id,
                error=RpcError(
                    code=_error_code(exc),
                    message=str(exc),
                    data=_error_data(exc),
                ),
            )

    async def _dispatch(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return await self.rpc_router.dispatch(method, params)

    def _register_rpc_methods(self) -> None:
        router = self.rpc_router
        router.register("initialize", self.initialize, capability="rpc", description="Initialize protocol state")
        router.register("health.ping", _without_params(self.health_ping), capability="health", description="Gateway health")
        router.register("method.list", self.method_list, capability="rpc", description="List registered RPC methods")
        router.register("events.subscribe", self.events_subscribe, capability="events", description="Create browser event subscription")
        router.register("app.list", self.app_list, capability="apps", description="List app profiles")
        router.register("app.get", self.app_get, capability="apps", description="Get app profile")

        router.register("session.start", self.session_start, capability="sessions")
        router.register("session.resume", self.session_resume, capability="resume")
        router.register("session.list", self.session_list, capability="session_list")
        router.register("session.get", self.core_session_get, capability="sessions", alias_of="core.session.get")
        router.register("session.read", self.session_read, capability="session_read")
        router.register("session.transcript", self.session_transcript, capability="transcript")
        router.register("session.events", self.session_events, capability="stream_events")
        router.register("session.close", self.session_close, capability="sessions")

        router.register("thread.list", self.core_thread_list, capability="sessions")
        router.register("turn.get", self.core_turn_get, capability="turns")
        router.register("turn.items", self.core_turn_items, capability="turns")
        router.register("turn.start", self.turn_start, capability="turns")
        router.register("turn.continue", self.turn_continue, capability="resume")
        router.register("turn.retry", self.turn_retry, capability="retry")
        router.register("turn.interrupt", self.turn_interrupt, capability="interrupt")

        router.register("core.trace.list", self.core_trace_list, capability="traces")
        router.register("core.approval.list", self.core_approval_list, capability="approvals")
        router.register("core.retry.list", self.core_retry_list, capability="retry")
        router.register("core.memory.list", self.core_memory_list, capability="memory")
        router.register("core.artifact.list", self.core_artifact_list, capability="artifacts")
        router.register("core.artifact.lineage", self.core_artifact_lineage, capability="artifact_lineage")
        router.register("core.job.list", self.core_job_list, capability="jobs")

        router.register("connector.list", self.connector_list, capability="connectors")
        router.register("connector.get", self.connector_get, capability="connectors")
        router.register("connector.health", self.connector_health, capability="connectors")
        router.register("connector.submit", self.connector_submit, capability="connector_execution")
        router.register("connector.poll", self.connector_poll, capability="connector_execution")
        router.register("connector.cancel", self.connector_cancel, capability="connector_execution")
        router.register("connector.collect", self.connector_collect, capability="connector_execution")

        router.register("job.list", self.job_list, capability="jobs")
        router.register("job.create", self.job_create, capability="jobs")
        router.register("job.get", self.job_get, capability="jobs")
        router.register("job.events", self.job_events, capability="job_events")
        router.register("job.cancel", self.job_cancel, capability="jobs")
        router.register("memory.list", self.memory_list, capability="memory")
        router.register("memory.get", self.memory_get, capability="memory")
        router.register("memory.summary", self.memory_summary, capability="memory")
        router.register("memory.extract_from_artifacts", self.memory_extract_from_artifacts, capability="memory")

        router.register("meeting.capabilities", _without_params(self.meeting_capabilities), capability="meeting")
        router.register("meeting.analyze_text", self.meeting_analyze_text, capability="meeting")
        router.register("meeting.process_recording", self.meeting_process_recording, capability="meeting")
        router.register("meeting.process_audio_dir", self.meeting_process_audio_dir, capability="meeting")

        router.register("artifact.register", self.artifact_register, capability="artifacts")
        router.register("artifact.register_external", self.artifact_register_external, capability="artifacts")
        router.register("artifact.list", self.artifact_list, capability="artifacts")
        router.register("artifact.get", self.artifact_get, capability="artifacts")
        router.register("artifact.read_metadata", self.artifact_read_metadata, capability="artifacts")
        router.register("artifact.read", self.artifact_read, capability="artifacts")
        router.register(
            "artifact.lineage",
            self.artifact_lineage,
            capability="artifact_lineage",
            alias_of="core.artifact.lineage",
        )

        router.register("trace.list", self.trace_list, capability="traces")
        router.register("trace.get", self.trace_get, capability="traces")
        router.register("approval.request", self.approval_request, capability="approvals")
        router.register("approval.list", self.approval_list, capability="approvals")
        router.register("approval.get", self.approval_get, capability="approvals")
        router.register("approval.respond", self.approval_respond, capability="approvals")
        router.register("approval.approve", self.approval_approve, capability="approvals")
        router.register("approval.reject", self.approval_reject, capability="approvals")
        router.register("policy.evaluate", self.policy_evaluate, capability="policies")
        router.register("workflow.list", _without_params(self.workflow_list), capability="workflows")
        router.register("workflow.template.create", self.workflow_template_create, capability="workflows.write")
        router.register("workflow.template.get", self.workflow_template_get, capability="workflows.read")
        router.register("workflow.template.list", self.workflow_template_list, capability="workflows.read")
        router.register("workflow.template.update_draft", self.workflow_template_update_draft, capability="workflows.write")
        router.register("workflow.draft.save", self.workflow_draft_save, capability="workflows.write")
        router.register("workflow.template.publish", self.workflow_template_publish, capability="workflow_versions.publish")
        router.register("workflow.template.archive", self.workflow_template_archive, capability="workflows.write")
        router.register("workflow.version.get", self.workflow_version_get, capability="workflows.read")
        router.register("workflow.version.list", self.workflow_version_list, capability="workflows.read")
        router.register("workflow.instance.start", self.workflow_instance_start, capability="workflows.execute")
        router.register("workflow.instance.get", self.workflow_instance_get, capability="workflows.read")
        router.register("workflow.instance.list", self.workflow_instance_list, capability="workflows.read")
        router.register("workflow.instance.status", self.workflow_instance_status, capability="workflows.read")
        router.register("workflow.instance.pause", self.workflow_instance_pause, capability="workflows.execute")
        router.register("workflow.instance.resume", self.workflow_instance_resume, capability="workflows.execute")
        router.register("workflow.instance.cancel", self.workflow_instance_cancel, capability="workflows.execute")
        router.register("workflow.instance.retry", self.workflow_instance_retry, capability="workflows.execute")
        router.register("station.run.get", self.station_run_get, capability="stations.read")
        router.register("station.run.list", self.station_run_list, capability="stations.read")
        router.register("station.rerun", self.station_rerun, capability="stations.execute")
        router.register("station.output.list", self.station_output_list, capability="stations.read")
        router.register("quality.evaluation.create", self.quality_evaluation_create, capability="quality.write")
        router.register("quality.evaluation.get", self.quality_evaluation_get, capability="quality.read")
        router.register("quality.evaluation.list", self.quality_evaluation_list, capability="quality.read")
        router.register("quality.evaluation.attach", self.quality_evaluation_attach, capability="quality.write")
        router.register("workflow.board.get", self.workflow_board_get, capability="board.read")
        router.register("workflow.context.get", self.workflow_context_get, capability="workflow_context.read")
        router.register("workflow.context.update", self.workflow_context_update, capability="workflow_context.write")
        router.register("business.event.bind", self.business_event_bind, capability="workflow_context.write")
        router.register("business.event.emit", self.business_event_emit, capability="business_events.write")
        router.register("workflow.patch.propose", self.workflow_patch_propose, capability="workflow_patches.write")
        router.register("workflow.patch.diff", self.workflow_patch_diff, capability="workflow_patches.read")
        router.register("workflow.patch.apply", self.workflow_patch_apply, capability="workflow_patches.write")
        router.register("workflow.patch.reject", self.workflow_patch_reject, capability="workflow_patches.write")
        router.register("pack.list", self.pack_list, capability="packs")
        router.register("pack.get", self.pack_get, capability="packs")
        router.register("pack.plan", self.pack_plan, capability="pack_execution")
        router.register("pack.execute_stub", self.pack_execute_stub, capability="pack_execution")
        router.register("workflow.plan", self.workflow_plan, capability="pack_execution")
        router.register("workflow.execute_stub", self.workflow_execute_stub, capability="pack_execution")
        router.register("pack.agents", self.pack_agents, capability="agents")
        router.register("agent.list", self.agent_list, capability="agents")
        router.register("agent.get", self.agent_get, capability="agents")

    def _resolve_request_scope(
        self,
        params: Optional[Dict[str, Any]] = None,
        *,
        app_id: Optional[str] = None,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ):
        return resolve_scope_context(
            params,
            app_registry=self.app_registry,
            app_id=app_id,
            project_id=project_id,
            workspace_id=workspace_id,
        )

    def _resolve_request_scope_for_session(self, params: Dict[str, Any], session_id: Optional[str]):
        if _params_include_scope(params) or session_id is None:
            return self._resolve_request_scope(params)
        try:
            session = self.runtime_pool.read_session(session_id)
        except Exception:
            return self._resolve_request_scope(params)
        return self._resolve_request_scope(
            params,
            app_id=_optional_text_value(session.get("app_id")),
            project_id=_optional_text_value(session.get("project_id")),
            workspace_id=_optional_text_value(session.get("workspace_id")),
        )

    def _ensure_session_in_scope(self, session: Dict[str, Any], scope, params: Dict[str, Any]) -> None:
        if params.get("scope_mode") == "all":
            return
        if not self._record_matches_scope(session, scope):
            raise ProtocolError("SCOPE_MISMATCH", "session does not belong to the requested scope", {"resource": "session_id"})

    def _session_matches_scope(self, session: Dict[str, Any], scope) -> bool:
        return self._record_matches_scope(session, scope)

    def _record_matches_scope(self, record: Dict[str, Any], scope) -> bool:
        return (
            _optional_text_value(record.get("app_id")) == scope.app_id
            and _optional_text_value(record.get("project_id")) == scope.project_id
            and _optional_text_value(record.get("workspace_id")) == scope.workspace_id
        )

    def _ensure_record_in_scope(self, record: Dict[str, Any], scope, params: Dict[str, Any], *, label: str) -> None:
        if params.get("scope_mode") == "all":
            return
        if _optional_text_value(record.get("app_id")) is None and not _auth_has_admin_capability(params):
            raise ProtocolError(
                "SCOPE_REQUIRED",
                f"{label} record does not include scope.",
                {"resource": label, "reason": "legacy_scope_required"},
            )
        if not self._record_matches_scope(record, scope):
            raise ProtocolError("SCOPE_MISMATCH", f"{label} does not belong to the requested scope", {"resource": label})

    async def _ensure_legacy_meeting_session(self, *, session_id: Optional[str], scope):
        if session_id is not None:
            try:
                session = self.runtime_pool.get_session(session_id)
                self._ensure_session_in_scope(
                    {
                        "app_id": session.app_id,
                        "project_id": session.project_id,
                        "workspace_id": session.workspace_id,
                    },
                    scope,
                    {},
                )
                return session
            except KeyError:
                try:
                    snapshot = self.runtime_pool.read_session(session_id)
                except KeyError:
                    pass
                else:
                    self._ensure_session_in_scope(snapshot, scope, {})
                    return await self.runtime_pool.resume_session(str(snapshot["session_id"]))
        return await self.runtime_pool.start_session(session_id=session_id, scope=scope)


def event_to_json(event: GatewayEvent) -> str:
    """Serialize a gateway event as one JSON line."""
    return event.model_dump_json()


def _require_str(params: Dict[str, Any], key: str) -> str:
    value = params.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} is required")
    return value


def _optional_str(params: Dict[str, Any], key: str) -> Optional[str]:
    value = params.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string when provided")
    return value.strip() or None


def _optional_dict(params: Dict[str, Any], key: str) -> Dict[str, Any]:
    value = params.get(key)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object when provided")
    return value


def _optional_dict_list(params: Dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = params.get(key)
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ProtocolError("QUALITY_EVALUATION_INVALID", f"{key} must be an object list when provided", {"field": key})
    return [dict(item) for item in value]


def _require_dict(params: Dict[str, Any], key: str) -> Dict[str, Any]:
    value = params.get(key)
    if not isinstance(value, dict):
        raise ProtocolError("INVALID_PARAMS", f"{key} must be an object", {"field": key})
    return value


def _optional_bool(params: Dict[str, Any], key: str) -> bool:
    value = params.get(key)
    if value is None:
        return False
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean when provided")
    return value


def _optional_int(params: Dict[str, Any], key: str, *, default: int) -> int:
    value = params.get(key)
    if value is None:
        return default
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer when provided")
    return value


def _optional_positive_int(params: Dict[str, Any], key: str) -> Optional[int]:
    value = params.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or value < 1:
        raise ProtocolError("INVALID_PARAMS", f"{key} must be a positive integer when provided", {"field": key})
    return value


def _optional_revision(params: Dict[str, Any], key: str = "expected_revision") -> Optional[int]:
    value = params.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or value < 1:
        raise ProtocolError("INVALID_PARAMS", f"{key} must be a positive integer", {"field": key})
    return value


def _optional_score(params: Dict[str, Any], key: str) -> Optional[float]:
    value = params.get(key)
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ProtocolError("QUALITY_EVALUATION_INVALID", "Quality evaluation score must be a number.", {"field": key})
    score = float(value)
    if score < 0.0 or score > 1.0:
        raise ProtocolError("QUALITY_EVALUATION_INVALID", "Quality evaluation score must be between 0.0 and 1.0.", {"field": key})
    return score


_QUALITY_RAW_PAYLOAD_KEYS = {
    "artifact_content",
    "connector_payload",
    "raw_artifact_content",
    "raw_connector_payload",
    "raw_trace_payload",
}

_QUALITY_SECRET_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "access_token",
    "refresh_token",
    "token",
    "secret",
    "password",
    "capability_token",
    "subscription_token",
}


def _sanitize_quality_payload(value: Any) -> Any:
    """Redact secrets and drop raw payload fields from quality records/traces."""
    masked = mask_value(value)
    if isinstance(masked, list):
        return [_sanitize_quality_payload(item) for item in masked]
    if isinstance(masked, tuple):
        return tuple(_sanitize_quality_payload(item) for item in masked)
    if isinstance(masked, dict):
        sanitized: dict[Any, Any] = {}
        for key, item in masked.items():
            normalized = str(key).lower().replace("-", "_")
            if (
                normalized in _QUALITY_RAW_PAYLOAD_KEYS
                or normalized in _QUALITY_SECRET_KEYS
                or normalized.endswith("_token")
                or normalized.endswith("_secret")
            ):
                continue
            sanitized[key] = _sanitize_quality_payload(item)
        return sanitized
    return masked


def _optional_str_list(params: Dict[str, Any], key: str) -> list[str]:
    value = params.get(key)
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{key} must be a string list when provided")
    return value


def _scope_filter(params: Dict[str, Any], key: str, value: Optional[str]) -> Optional[str]:
    if params.get("scope_mode") == "all":
        return None
    return value


def _params_include_scope(params: Dict[str, Any]) -> bool:
    if "scope" in params:
        return True
    return any(key in params for key in ("app_id", "project_id", "workspace_id"))


def _optional_text_value(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("scope values must be strings when provided")
    return value.strip() or None


def _trace_id_from_events(events: Any) -> Optional[str]:
    if not isinstance(events, list):
        return None
    for event in events:
        if not isinstance(event, dict):
            continue
        data = event.get("data") or {}
        if isinstance(data, dict) and isinstance(data.get("trace_id"), str):
            return data["trace_id"]
    return None


def _new_workflow_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _linear_station_order(template: WorkflowTemplate) -> list[Dict[str, Any]]:
    stations = [station.model_dump(mode="json") if hasattr(station, "model_dump") else dict(station) for station in template.stations]
    if not stations:
        raise ProtocolError("WORKFLOW_RUNTIME_UNSUPPORTED", "Workflow runtime requires at least one station.", {"reason": "empty_workflow"})
    if len(stations) == 1:
        return stations
    edges = [edge.model_dump(mode="json") if hasattr(edge, "model_dump") else dict(edge) for edge in template.edges]
    if len(edges) != len(stations) - 1:
        raise ProtocolError("WORKFLOW_RUNTIME_UNSUPPORTED", "V3.6-C supports only explicit linear workflows.", {"reason": "non_linear_edge_count"})
    station_by_id = {str(station["station_id"]): station for station in stations}
    outgoing: dict[str, list[str]] = {}
    incoming: dict[str, list[str]] = {}
    for edge in sorted(edges, key=lambda item: int(item.get("order") or 0)):
        if edge.get("condition"):
            raise ProtocolError("WORKFLOW_RUNTIME_UNSUPPORTED", "V3.6-C does not support conditional workflow edges.", {"reason": "conditional_edge"})
        source = str(edge["from_station_id"])
        target = str(edge["to_station_id"])
        outgoing.setdefault(source, []).append(target)
        incoming.setdefault(target, []).append(source)
    if any(len(targets) > 1 for targets in outgoing.values()) or any(len(sources) > 1 for sources in incoming.values()):
        raise ProtocolError("WORKFLOW_RUNTIME_UNSUPPORTED", "V3.6-C does not support parallel workflow branches.", {"reason": "branching_graph"})
    starts = [station_id for station_id in station_by_id if station_id not in incoming]
    if len(starts) != 1:
        raise ProtocolError("WORKFLOW_RUNTIME_UNSUPPORTED", "V3.6-C requires exactly one start station.", {"reason": "invalid_start_count"})
    ordered: list[Dict[str, Any]] = []
    visited: set[str] = set()
    current = starts[0]
    while current:
        if current in visited:
            raise ProtocolError("WORKFLOW_RUNTIME_UNSUPPORTED", "V3.6-C does not support workflow cycles.", {"reason": "cycle"})
        visited.add(current)
        ordered.append(station_by_id[current])
        next_nodes = outgoing.get(current, [])
        current = next_nodes[0] if next_nodes else ""
    if len(ordered) != len(stations):
        raise ProtocolError("WORKFLOW_RUNTIME_UNSUPPORTED", "Workflow graph is disconnected.", {"reason": "disconnected_graph"})
    return ordered


def _latest_outputs_by_station(runs: list[StationRun]) -> list[str]:
    completed = [run for run in runs if run.status == StationRunStatus.COMPLETED and run.output_artifact_ids]
    if not completed:
        return []
    return list(completed[-1].output_artifact_ids)


def _station_by_id(template: WorkflowTemplate, station_id: str) -> Dict[str, Any]:
    for station in template.stations:
        payload = station.model_dump(mode="json") if hasattr(station, "model_dump") else dict(station)
        if payload.get("station_id") == station_id:
            return payload
    raise ProtocolError("STATION_NOT_FOUND", f"Station not found: {station_id}", {"station_id": station_id})


def _station_input_contracts(station: Dict[str, Any]) -> list[Dict[str, Any]]:
    contracts = station.get("input_contracts")
    if not isinstance(contracts, list):
        return []
    return [_normalize_artifact_contract(contract, direction="input") for contract in contracts if isinstance(contract, dict)]


def _station_output_contracts(station: Dict[str, Any], *, station_id: str) -> list[Dict[str, Any]]:
    contracts = station.get("output_contracts")
    if isinstance(contracts, list) and contracts:
        return [_normalize_artifact_contract(contract, direction="output") for contract in contracts if isinstance(contract, dict)]
    return [
        {
            "contract_id": f"{station_id}.output",
            "artifact_kind": "workflow_station_output",
            "direction": "output",
            "required": True,
            "cardinality": "one",
            "kind_match_policy": "exact",
            "schema_ref": None,
            "metadata_schema": {},
            "preview_policy": {},
            "large_file_policy_ref": None,
            "metadata": {},
        }
    ]


def _normalize_artifact_contract(contract: Dict[str, Any], *, direction: str) -> Dict[str, Any]:
    contract_id = contract.get("contract_id")
    artifact_kind = contract.get("artifact_kind")
    if not isinstance(contract_id, str) or not contract_id:
        raise ProtocolError("WORKFLOW_ARTIFACT_CONTRACT_MISSING", "Artifact contract_id is required.", {"direction": direction})
    if not isinstance(artifact_kind, str) or not artifact_kind:
        raise ProtocolError("WORKFLOW_ARTIFACT_CONTRACT_INVALID", "Artifact contract artifact_kind is required.", {"contract_id": contract_id})
    return {
        "contract_id": contract_id,
        "artifact_kind": artifact_kind,
        "direction": str(contract.get("direction") or direction),
        "required": bool(contract.get("required", True)),
        "cardinality": str(contract.get("cardinality") or "one"),
        "kind_match_policy": str(contract.get("kind_match_policy") or "exact"),
        "schema_ref": contract.get("schema_ref") if isinstance(contract.get("schema_ref"), str) else None,
        "metadata_schema": contract.get("metadata_schema") if isinstance(contract.get("metadata_schema"), dict) else {},
        "preview_policy": contract.get("preview_policy") if isinstance(contract.get("preview_policy"), dict) else {},
        "large_file_policy_ref": contract.get("large_file_policy_ref") if isinstance(contract.get("large_file_policy_ref"), str) else None,
        "metadata": contract.get("metadata") if isinstance(contract.get("metadata"), dict) else {},
    }


def _artifact_matches_contract(artifact: Dict[str, Any], contract: Dict[str, Any]) -> bool:
    artifact_kind = str(artifact.get("kind") or "")
    expected_kind = str(contract.get("artifact_kind") or "")
    policy = str(contract.get("kind_match_policy") or "exact")
    if policy == "exact" and artifact_kind != expected_kind:
        return False
    if policy == "compatible" and artifact_kind != expected_kind:
        compatible = artifact.get("metadata", {}).get("artifact_contract", {}).get("compatible_kinds", [])
        if not isinstance(compatible, list) or expected_kind not in compatible:
            return False
    schema_ref = contract.get("schema_ref")
    if isinstance(schema_ref, str) and schema_ref:
        metadata = artifact.get("metadata") if isinstance(artifact.get("metadata"), dict) else {}
        artifact_contract = metadata.get("artifact_contract") if isinstance(metadata.get("artifact_contract"), dict) else {}
        if artifact_contract.get("schema_ref") not in {None, schema_ref}:
            return False
    return True


def _workflow_artifact_metadata(
    *,
    instance: WorkflowInstance,
    station_run: StationRun,
    station: Dict[str, Any],
    contract: Dict[str, Any],
    parent_artifact_ids: list[str],
) -> Dict[str, Any]:
    user_metadata = station.get("metadata") if isinstance(station.get("metadata"), dict) else {}
    return mask_value(
        {
            "workflow": {
                "workflow_instance_id": instance.workflow_instance_id,
                "workflow_template_id": instance.workflow_template_id,
                "workflow_version_id": instance.workflow_version_id,
                "station_run_id": station_run.station_run_id,
                "station_id": station_run.station_id,
                "attempt": station_run.attempt,
                "rerun_of_station_run_id": station_run.rerun_of_station_run_id,
            },
            "artifact_contract": {
                "contract_id": contract["contract_id"],
                "artifact_kind": contract["artifact_kind"],
                "direction": contract["direction"],
                "cardinality": contract["cardinality"],
                "kind_match_policy": contract["kind_match_policy"],
                "schema_ref": contract.get("schema_ref"),
            },
            "lineage": {
                "input_artifact_ids": list(station_run.input_artifact_ids),
                "parent_artifact_ids": _dedupe_stable(parent_artifact_ids),
            },
            "user": mask_value(user_metadata),
        }
    )


def _station_contract_snapshot(station: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "input_contracts": station.get("input_contracts") if isinstance(station.get("input_contracts"), list) else [],
        "output_contracts": station.get("output_contracts") if isinstance(station.get("output_contracts"), list) else [],
    }


def _flatten_bindings(bindings: dict[str, list[str]]) -> list[str]:
    return _dedupe_stable([artifact_id for ids in bindings.values() for artifact_id in ids])


def _dedupe_stable(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if isinstance(value, str) and value))


def _workflow_binding_from_approval(approval: Dict[str, Any]) -> Dict[str, Any] | None:
    metadata = approval.get("metadata")
    if not isinstance(metadata, dict):
        return None
    binding = metadata.get("workflow_binding")
    if not isinstance(binding, dict):
        return None
    required = ("workflow_instance_id", "station_run_id", "station_id", "workflow_template_id", "workflow_version_id")
    if not all(isinstance(binding.get(key), str) and binding.get(key) for key in required):
        return None
    return dict(binding)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _instance_version_id(instance: WorkflowInstance) -> str:
    if instance.workflow_version_id:
        return instance.workflow_version_id
    metadata = instance.metadata if isinstance(instance.metadata, dict) else {}
    value = metadata.get("workflow_version_id")
    if isinstance(value, str) and value:
        return value
    raise ProtocolError("WORKFLOW_VERSION_NOT_FOUND", "Workflow instance does not reference a workflow version.", {"workflow_instance_id": instance.workflow_instance_id})


def _meeting_legacy_deprecation_warning() -> Dict[str, str]:
    return {
        "legacy_method": "meeting.process_recording",
        "replacement": "turn.start / meeting.workflow",
        "sunset_stage": "stage_1_compat_facade",
        "message": "meeting.process_recording is deprecated; use the Meeting Pack workflow.",
        "trace_event": "legacy_facade.deprecation_warning",
    }


def _method_contract(method: str) -> Dict[str, Any]:
    exact: Dict[str, Any] | None = None
    wildcard: Dict[str, Any] | None = None
    for entry in list(METHOD_INVENTORY) + list(WORKFLOW_METHOD_INVENTORY):
        pattern = str(entry.get("method") or "")
        if pattern == method:
            exact = entry
            break
        if pattern.endswith(".*") and method.startswith(pattern[:-1]):
            wildcard = entry
    return exact or wildcard or {
        "surface": "optional",
        "status": "implemented",
        "stability": "legacy",
        "forbidden_reason": None,
    }


def _method_discovery_metadata(method: str, contract: Dict[str, Any], *, runtime_handler: bool) -> Dict[str, Any]:
    surface = str(contract.get("surface") or "optional")
    metadata: Dict[str, Any] = {
        "surface": surface,
        "status": str(contract.get("status") or "implemented"),
        "stability": str(contract.get("stability") or "legacy"),
        "runtime_handler": runtime_handler,
        "sdk_exposure": "forbidden" if surface == "forbidden_by_default" else surface,
    }
    forbidden_reason = contract.get("forbidden_reason")
    if isinstance(forbidden_reason, str) and forbidden_reason:
        metadata["forbidden_reason"] = forbidden_reason
    return metadata


def _station_summary(station: Dict[str, Any]) -> Dict[str, Any]:
    return _sanitize_board_payload(
        {
            "station_id": station.get("station_id"),
            "name": station.get("name"),
            "role": station.get("role"),
            "agent_ref": station.get("agent_ref"),
            "skill_refs": station.get("skill_refs") if isinstance(station.get("skill_refs"), list) else [],
            "connector_refs": station.get("connector_refs") if isinstance(station.get("connector_refs"), list) else [],
            "approval_required": bool(station.get("approval_required")),
            "input_contracts": station.get("input_contracts") if isinstance(station.get("input_contracts"), list) else [],
            "output_contracts": station.get("output_contracts") if isinstance(station.get("output_contracts"), list) else [],
            "quality_policy": station.get("quality_policy") if isinstance(station.get("quality_policy"), dict) else {},
        }
    )


def _latest_station_status(station_runs: list[StationRun]) -> str:
    if not station_runs:
        return "not_started"
    return _enum_value(station_runs[-1].status)


def _job_summary(job: Dict[str, Any]) -> Dict[str, Any]:
    return _sanitize_board_payload(
        {
            "job_id": job.get("job_id"),
            "workflow_id": job.get("workflow_id"),
            "domain": job.get("domain"),
            "session_id": job.get("session_id"),
            "thread_id": job.get("thread_id"),
            "turn_id": job.get("turn_id"),
            "app_id": job.get("app_id"),
            "project_id": job.get("project_id"),
            "workspace_id": job.get("workspace_id"),
            "status": job.get("status"),
            "progress": job.get("progress"),
            "trace_id": job.get("trace_id"),
            "artifact_ids": job.get("artifact_ids") if isinstance(job.get("artifact_ids"), list) else [],
            "external_job_ref": job.get("external_job_ref"),
            "parent_job_id": job.get("parent_job_id"),
            "failure_context": job.get("failure_context") if isinstance(job.get("failure_context"), dict) else {},
            "metadata": _board_metadata_subset(job.get("metadata") if isinstance(job.get("metadata"), dict) else {}),
        }
    )


def _trace_record_summary(record: Dict[str, Any]) -> Dict[str, Any]:
    return _sanitize_board_payload(
        {
            "trace_id": record.get("trace_id"),
            "event_type": record.get("event_type"),
            "status": record.get("status"),
            "workflow_id": record.get("workflow_id"),
            "artifact_ids": record.get("artifact_ids") if isinstance(record.get("artifact_ids"), list) else [],
            "approval_ids": record.get("approval_ids") if isinstance(record.get("approval_ids"), list) else [],
            "input_summary": record.get("input_summary"),
            "created_at": record.get("created_at"),
        }
    )


def _status_counts(statuses: list[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for status in statuses:
        normalized = _enum_value(status)
        if not normalized:
            continue
        counts[normalized] = counts.get(normalized, 0) + 1
    return counts


def _enum_value(value: Any) -> str:
    if hasattr(value, "value"):
        return str(value.value)
    text = str(value or "")
    if "." in text:
        return text.rsplit(".", 1)[-1].lower()
    return text


def _artifact_parent_ids_from_gateway_record(artifact: Dict[str, Any]) -> list[str]:
    metadata = artifact.get("metadata") if isinstance(artifact.get("metadata"), dict) else {}
    parent_ids = []
    lineage = metadata.get("lineage") if isinstance(metadata.get("lineage"), dict) else {}
    raw_parent_ids = lineage.get("parent_artifact_ids") if isinstance(lineage, dict) else None
    if isinstance(raw_parent_ids, list):
        parent_ids.extend(item for item in raw_parent_ids if isinstance(item, str) and item)
    raw_parent_ids = metadata.get("parent_artifact_ids")
    if isinstance(raw_parent_ids, list):
        parent_ids.extend(item for item in raw_parent_ids if isinstance(item, str) and item)
    return _dedupe_stable(parent_ids)


def _board_metadata_subset(metadata: Dict[str, Any]) -> Dict[str, Any]:
    allowed = {
        "workflow_instance_id",
        "station_run_id",
        "station_id",
        "workflow_template_id",
        "workflow_version_id",
        "message",
    }
    return {key: value for key, value in metadata.items() if key in allowed}


def _sanitize_board_payload(value: Any) -> Any:
    return _sanitize_quality_payload(value)


def _sanitize_workflow_context(context: WorkflowContext) -> Dict[str, Any]:
    return _sanitize_board_payload(context.model_dump(mode="json"))


def _sanitize_business_event(event: BusinessEvent) -> Dict[str, Any]:
    return _sanitize_board_payload(event.model_dump(mode="json"))


def _sanitize_workflow_patch(patch: WorkflowPatch) -> Dict[str, Any]:
    return _sanitize_board_payload(patch.model_dump(mode="json"))


def _patch_operation(params: Dict[str, Any]) -> WorkflowPatchOperation:
    value = params.get("operation")
    if not isinstance(value, str):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "operation is required.", {"field": "operation"})
    try:
        return WorkflowPatchOperation(value)
    except ValueError as exc:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "Unsupported workflow patch operation.", {"operation": value}) from exc


def _patch_payload(params: Dict[str, Any]) -> Dict[str, Any]:
    payload = params.get("payload")
    if not isinstance(payload, dict):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "payload must be an object.", {"field": "payload"})
    _reject_patch_payload_forbidden(payload)
    return _sanitize_board_payload(payload)


def _patch_actor_type(params: Dict[str, Any]) -> str:
    value = params.get("actor_type") or "user"
    if not isinstance(value, str):
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "actor_type must be a string.", {"field": "actor_type"})
    try:
        return WorkflowPatchActorType(value).value
    except ValueError as exc:
        raise ProtocolError("WORKFLOW_PATCH_INVALID", "actor_type must be agent, user, or system.", {"actor_type": value}) from exc


def _reject_patch_payload_forbidden(value: Any) -> None:
    forbidden = {
        "x",
        "y",
        "position",
        "canvas",
        "panel",
        "react_state",
        "component",
        "layout",
        "capability_token",
        "subscription_token",
        "authorization",
        "secret",
        "raw_trace_payload",
        "raw_connector_payload",
        "raw_artifact_content",
    }
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in forbidden or normalized.endswith("_token") or normalized.endswith("_secret"):
                raise ProtocolError("WORKFLOW_PATCH_INVALID", "Workflow patch payload contains forbidden field.", {"field": str(key)})
            _reject_patch_payload_forbidden(item)
    elif isinstance(value, list):
        for item in value:
            _reject_patch_payload_forbidden(item)


def _patch_risk_flags(operation: WorkflowPatchOperation, payload: Dict[str, Any]) -> list[str]:
    flags: list[str] = []
    if operation == WorkflowPatchOperation.UPDATE_CONNECTOR:
        flags.append("connector_change")
    if operation == WorkflowPatchOperation.UPDATE_APPROVAL_POINT and payload.get("approval_required") is False:
        flags.append("approval_removed")
    if operation == WorkflowPatchOperation.UPDATE_ARTIFACT_CONTRACT:
        patch = payload.get("contract_patch")
        if isinstance(patch, dict) and (patch.get("required") is False or patch.get("removed") is True):
            flags.append("artifact_contract_removed")
    if operation == WorkflowPatchOperation.UPDATE_QUALITY_RULE:
        patch = payload.get("quality_patch")
        if isinstance(patch, dict) and (patch.get("required") is False or patch.get("removed") is True or patch.get("blocking") is False):
            flags.append("quality_rule_removed")
    if operation in {WorkflowPatchOperation.UPDATE_EDGE, WorkflowPatchOperation.REMOVE_STATION}:
        flags.append("edge_removed" if operation == WorkflowPatchOperation.UPDATE_EDGE else "station_removed")
    return sorted(set(flags))


def _build_patch_diff_from_patch(patch: WorkflowPatch, draft_payload: Dict[str, Any]) -> Dict[str, Any]:
    return _build_patch_diff(
        workflow_patch_id=patch.workflow_patch_id,
        workflow_draft_id=patch.workflow_draft_id,
        base_revision=patch.base_revision,
        operation=WorkflowPatchOperation(_enum_value(patch.operation)),
        payload=patch.payload,
        draft_payload=draft_payload,
        risk_flags=list(patch.risk_flags),
    )


def _build_patch_diff(
    *,
    workflow_patch_id: str,
    workflow_draft_id: str,
    base_revision: int,
    operation: WorkflowPatchOperation,
    payload: Dict[str, Any],
    draft_payload: Dict[str, Any],
    risk_flags: list[str],
) -> Dict[str, Any]:
    target = _patch_target_summary(operation, payload)
    return _sanitize_board_payload(
        {
            "workflow_patch_id": workflow_patch_id,
            "workflow_draft_id": workflow_draft_id,
            "base_revision": base_revision,
            "operation": operation.value,
            "target": target,
            "before_summary": _patch_before_summary(operation, payload, draft_payload),
            "after_summary": _patch_after_summary(operation, payload),
            "risk_flags": list(risk_flags),
            "requires_approval": bool(risk_flags),
            "redacted": True,
        }
    )


def _patch_target_summary(operation: WorkflowPatchOperation, payload: Dict[str, Any]) -> Dict[str, Any]:
    if operation == WorkflowPatchOperation.ADD_STATION:
        station = payload.get("station") if isinstance(payload.get("station"), dict) else {}
        return {"type": "station", "station_id": station.get("station_id")}
    if "station_id" in payload:
        return {"type": "station", "station_id": payload.get("station_id")}
    if "edge_id" in payload:
        return {"type": "edge", "edge_id": payload.get("edge_id")}
    if "quality_contract_id" in payload:
        return {"type": "quality_contract", "quality_contract_id": payload.get("quality_contract_id")}
    return {"type": "workflow"}


def _patch_before_summary(operation: WorkflowPatchOperation, payload: Dict[str, Any], draft_payload: Dict[str, Any]) -> Dict[str, Any]:
    target = _patch_target_summary(operation, payload)
    if target.get("type") == "station":
        station_id = target.get("station_id")
        stations = draft_payload.get("stations") if isinstance(draft_payload.get("stations"), list) else []
        exists = any(isinstance(station, dict) and station.get("station_id") == station_id for station in stations)
        return {"exists": exists, "station_id": station_id}
    if target.get("type") == "edge":
        edge_id = target.get("edge_id")
        edges = draft_payload.get("edges") if isinstance(draft_payload.get("edges"), list) else []
        exists = any(isinstance(edge, dict) and edge.get("edge_id") == edge_id for edge in edges)
        return {"exists": exists, "edge_id": edge_id}
    return {"exists": True}


def _patch_after_summary(operation: WorkflowPatchOperation, payload: Dict[str, Any]) -> Dict[str, Any]:
    summary = {"operation": operation.value}
    target = _patch_target_summary(operation, payload)
    summary.update(target)
    if operation == WorkflowPatchOperation.ADD_STATION:
        station = payload.get("station") if isinstance(payload.get("station"), dict) else {}
        if isinstance(station.get("name"), str):
            summary["station_name"] = station["name"]
    if operation == WorkflowPatchOperation.UPDATE_APPROVAL_POINT and "approval_required" in payload:
        summary["approval_required"] = payload["approval_required"]
    if operation == WorkflowPatchOperation.UPDATE_CONNECTOR and "connector_refs" in payload:
        summary["connector_ref_count"] = len(payload["connector_refs"]) if isinstance(payload["connector_refs"], list) else None
    return summary


def _updated_business_context(current: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    business = _sanitize_board_payload(dict(current))
    if "system" in params or "runtime" in params or "status" in params:
        raise ProtocolError("WORKFLOW_CONTEXT_SCOPE_MISMATCH", "Only context.business can be updated externally.", {"allowed": "context.business"})
    if params.get("path") is not None:
        path = _require_str(params, "path")
        if "value" not in params:
            raise ProtocolError("INVALID_PARAMS", "value is required when path is provided.", {"field": "value"})
        return _set_context_business_path(business, path, params.get("value"))
    raw_business = params.get("business") if isinstance(params.get("business"), dict) else None
    raw_values = params.get("values") if isinstance(params.get("values"), dict) else None
    if raw_business is None and raw_values is None:
        raise ProtocolError("INVALID_PARAMS", "business, values, or path is required.", {"field": "business"})
    update = raw_business if raw_business is not None else raw_values
    _reject_context_reserved_keys(update)
    merged = dict(business)
    merged.update(_sanitize_board_payload(update))
    return merged


def _set_context_business_path(current: Dict[str, Any], target_path: str, value: Any) -> Dict[str, Any]:
    if target_path.startswith("business."):
        parts = target_path.split(".")[1:]
    elif target_path.startswith("context.business."):
        parts = target_path.split(".")[2:]
    else:
        raise ProtocolError("BUSINESS_EVENT_BINDING_INVALID", "target_path must be under context.business.*", {"target_path": target_path})
    if not parts or any(not part for part in parts):
        raise ProtocolError("BUSINESS_EVENT_BINDING_INVALID", "target_path must include a concrete business key.", {"target_path": target_path})
    business = _sanitize_board_payload(dict(current))
    cursor = business
    for part in parts[:-1]:
        existing = cursor.get(part)
        if not isinstance(existing, dict):
            existing = {}
            cursor[part] = existing
        cursor = existing
    cursor[parts[-1]] = _sanitize_board_payload(value)
    return business


def _value_from_business_event(event: BusinessEvent, payload_path: str) -> Any:
    if not payload_path.startswith("event.payload."):
        raise ProtocolError("BUSINESS_EVENT_BINDING_INVALID", "payload_path must start with event.payload.", {"payload_path": payload_path})
    parts = payload_path.split(".")[2:]
    value: Any = event.payload
    for part in parts:
        if not isinstance(value, dict) or part not in value:
            raise ProtocolError("BUSINESS_EVENT_INVALID", "payload_path does not exist in event payload.", {"payload_path": payload_path})
        value = value[part]
    return value


def _reject_context_reserved_keys(value: Dict[str, Any]) -> None:
    forbidden = {
        "system",
        "runtime",
        "status",
        "workflow_instance",
        "workflow_instance_status",
        "station_run_status",
        "approval_status",
        "template",
        "draft",
        "version",
    }
    for key, item in value.items():
        normalized = str(key).lower()
        if normalized in forbidden:
            raise ProtocolError("WORKFLOW_CONTEXT_SCOPE_MISMATCH", "Context update cannot modify workflow runtime state.", {"field": key})
        if isinstance(item, dict):
            _reject_context_reserved_keys(item)


def _scope_dict(value: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "app_id": str(value.get("app_id") or "default"),
        "project_id": value.get("project_id"),
        "workspace_id": value.get("workspace_id"),
    }


def _dump_core_record(record: Any) -> Dict[str, Any]:
    if hasattr(record, "model_dump"):
        return record.model_dump(mode="json")
    return dict(record)


def _artifact_edges_from_records(records: list[Dict[str, Any]]) -> list[Dict[str, str]]:
    artifact_ids = {record["artifact_id"] for record in records}
    edges = []
    for record in records:
        metadata = record.get("metadata", {}) if isinstance(record.get("metadata"), dict) else {}
        for parent_id in metadata.get("parent_artifact_ids", []):
            if parent_id in artifact_ids:
                edges.append(
                    {
                        "source_artifact_id": parent_id,
                        "target_artifact_id": record["artifact_id"],
                        "relation": "derived_from",
                    }
                )
    return edges


def _artifact_leaves_from_records(records: list[Dict[str, Any]]) -> list[str]:
    parent_ids = {
        parent_id
        for record in records
        for parent_id in (record.get("metadata", {}) or {}).get("parent_artifact_ids", [])
    }
    return [record["artifact_id"] for record in records if record["artifact_id"] not in parent_ids]


def _without_params(handler: Callable[[], Awaitable[Dict[str, Any]]]) -> Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]:
    async def wrapped(_: Dict[str, Any]) -> Dict[str, Any]:
        return await handler()

    return wrapped


def _auth_has_admin_capability(params: Dict[str, Any]) -> bool:
    capabilities = params.get("_auth_capabilities")
    if not isinstance(capabilities, list):
        return False
    return bool(set(str(item) for item in capabilities) & {"admin", "debug", "internal"})


def _build_meeting_gateway_service() -> Any:
    from packs.meeting.connector import MeetingGatewayService

    return MeetingGatewayService()


def _build_meeting_workflow(*, service: Any, artifact_registry: Optional[ArtifactRegistry]) -> Any:
    from packs.meeting.workflow import MeetingWorkflow

    return MeetingWorkflow(service=service, artifact_registry=artifact_registry)


def _error_code(exc: Exception) -> str:
    if isinstance(exc, ProtocolError):
        return exc.code
    if isinstance(exc, ArtifactReadBlockedError):
        return "ARTIFACT_READ_BLOCKED"
    if isinstance(exc, KeyError):
        return "SESSION_NOT_FOUND"
    if isinstance(exc, ValueError):
        return "INVALID_PARAMS"
    if isinstance(exc, LookupError):
        return "METHOD_NOT_FOUND"
    return "RUNTIME_ERROR"


def _error_data(exc: Exception) -> Dict[str, Any]:
    if isinstance(exc, ProtocolError):
        return dict(exc.data)
    if hasattr(exc, "to_error_data") and callable(getattr(exc, "to_error_data")):
        data = exc.to_error_data()
        return data if isinstance(data, dict) else {}
    return {}
