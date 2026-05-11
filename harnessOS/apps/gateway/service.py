"""Local JSON-RPC style gateway service for harnessOS."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Optional

from apps.gateway.approvals import APPROVAL_APPROVED, APPROVAL_REJECTED, ApprovalConflictError, ApprovalStore
from apps.gateway.artifacts import ArtifactReadBlockedError, ArtifactRegistry
from apps.gateway.persistence import atomic_write_text
from apps.gateway.connector_execution import ConnectorExecutionRuntime
from apps.gateway.connectors import ConnectorRegistry, MEETING_VOICE_MCP_CONNECTOR_ID
from apps.gateway.policies import PolicyEvaluator
from apps.gateway.protocol import GatewayEvent, RpcError, RpcRequest, RpcResponse
from apps.gateway.retries import RETRY_PENDING_APPROVAL, RETRY_RETRIED, RetryStore
from apps.gateway.rpc_router import RpcRouter
from apps.gateway.runtime import GatewayRuntimePool
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
from core.protocol.event_bridge import ensure_channel_capabilities, make_event_cursor, normalize_event_channels
from core.protocol.schemas import ProtocolError, get_method_schema, list_method_schemas
from packs.meeting.connector import MeetingGatewayService
from packs.meeting.workflow import MeetingWorkflow


class GatewayService:
    """Project-owned control-plane facade over runtime sessions."""

    def __init__(
        self,
        runtime_pool: Optional[GatewayRuntimePool] = None,
        meeting_service: Optional[MeetingGatewayService] = None,
        artifact_registry: Optional[ArtifactRegistry] = None,
        trace_store: Optional[TraceStore] = None,
        approval_store: Optional[ApprovalStore] = None,
        policy_evaluator: Optional[PolicyEvaluator] = None,
        retry_store: Optional[RetryStore] = None,
        app_registry: Optional[AppRegistry] = None,
    ) -> None:
        resolved_app_registry = app_registry or getattr(runtime_pool, "app_registry", None) or build_default_app_registry()
        resolved_meeting_service = meeting_service or MeetingGatewayService()
        self.trace_store = trace_store or getattr(runtime_pool, "trace_store", None) or TraceStore()
        self.approval_store = approval_store or getattr(runtime_pool, "approval_store", None) or ApprovalStore()
        self.policy_evaluator = policy_evaluator or getattr(runtime_pool, "policy_evaluator", None) or PolicyEvaluator()
        self.retry_store = retry_store or getattr(runtime_pool, "retry_store", None) or RetryStore()
        meeting_workflow = None
        if runtime_pool is None and meeting_service is not None:
            meeting_workflow = MeetingWorkflow(
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
        self.meeting_service = resolved_meeting_service
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
        closed = await self.runtime_pool.close_session(session_id)
        return {"session_id": session_id, "closed": closed}

    async def session_resume(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resume a session from its local snapshot."""
        session_id = _require_str(params, "session_id")
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
        return {"memory": _dump_core_record(memory)}

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
        self._ensure_record_in_scope(
            self.approval_store.get_approval(approval_id),
            self._resolve_request_scope(params),
            params,
            label="approval",
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
        self._ensure_record_in_scope(
            self.approval_store.get_approval(approval_id),
            self._resolve_request_scope(params),
            params,
            label="approval",
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
        if idempotent:
            return {
                "approval": approval,
                "status": approval.get("status"),
                "trace_id": approval.get("trace_id"),
                "idempotent": True,
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
            raise ValueError("session does not belong to the requested scope")

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
        if not self._record_matches_scope(record, scope):
            raise ValueError(f"{label} does not belong to the requested scope")

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
    for entry in METHOD_INVENTORY:
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
