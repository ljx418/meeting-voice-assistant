"""Local JSON-RPC style gateway service for harnessOS."""

from __future__ import annotations

from typing import Any, Dict, Optional

from apps.gateway.approvals import APPROVAL_APPROVED, ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.meeting import MeetingGatewayService
from apps.gateway.policies import PolicyEvaluator
from apps.gateway.protocol import GatewayEvent, RpcError, RpcRequest, RpcResponse
from apps.gateway.retries import RETRY_RETRIED, RetryStore
from apps.gateway.runtime import GatewayRuntimePool
from apps.gateway.traces import TraceStore


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
    ) -> None:
        self.trace_store = trace_store or getattr(runtime_pool, "trace_store", None) or TraceStore()
        self.approval_store = approval_store or getattr(runtime_pool, "approval_store", None) or ApprovalStore()
        self.policy_evaluator = policy_evaluator or getattr(runtime_pool, "policy_evaluator", None) or PolicyEvaluator()
        self.retry_store = retry_store or getattr(runtime_pool, "retry_store", None) or RetryStore()
        self.runtime_pool = runtime_pool or GatewayRuntimePool(
            artifact_registry=artifact_registry,
            trace_store=self.trace_store,
            approval_store=self.approval_store,
            policy_evaluator=self.policy_evaluator,
            retry_store=self.retry_store,
        )
        self.artifact_registry = artifact_registry or self.runtime_pool.artifact_registry
        self.trace_store = trace_store or self.runtime_pool.trace_store
        self.approval_store = approval_store or self.runtime_pool.approval_store
        self.policy_evaluator = policy_evaluator or self.runtime_pool.policy_evaluator
        self.retry_store = retry_store or self.runtime_pool.retry_store
        self.core_store = self.runtime_pool.core_store
        self.core_service = self.runtime_pool.core_service
        self.meeting_service = meeting_service or MeetingGatewayService()
        self.initialized = False

    async def initialize(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Initialize the gateway protocol session."""
        self.initialized = True
        return {
            "protocol_version": "v1alpha",
            "server": "harnessOS gateway",
            "capabilities": {
                "sessions": True,
                "session_list": True,
                "session_read": True,
                "transcript": True,
                "turns": True,
                "resume": True,
                "interrupt": True,
                "stream_events": True,
                "headless": True,
                "rpc": True,
                "stdio_jsonl": True,
                "meeting": True,
                "artifacts": True,
                "workflows": True,
                "packs": True,
                "traces": True,
                "approvals": True,
                "policies": True,
                "retry": True,
                "jobs": True,
            },
        }

    async def health_ping(self) -> Dict[str, Any]:
        """Return a compact health snapshot."""
        return {
            "status": "ok",
            "active_sessions": self.runtime_pool.active_sessions,
            "initialized": self.initialized,
        }

    async def session_start(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a runtime-backed session."""
        params = params or {}
        session = await self.runtime_pool.start_session(model=params.get("model"))
        return {
            "session_id": session.session_id,
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

    async def session_list(self) -> Dict[str, Any]:
        """Return persisted session snapshots."""
        return {"sessions": self.runtime_pool.list_sessions()}

    async def session_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one persisted session snapshot."""
        session_id = _require_str(params, "session_id")
        return {"session": self.runtime_pool.read_session(session_id)}

    async def core_session_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one Core v1.5 session record."""
        session_id = _require_str(params, "session_id")
        return {"session": _dump_core_record(self.core_service.get_session(session_id))}

    async def core_thread_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 thread records."""
        session_id = _optional_str(params, "session_id")
        threads = self.core_service.list_threads(session_id=session_id)
        return {"threads": [_dump_core_record(thread) for thread in threads], "count": len(threads)}

    async def core_turn_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one Core v1.5 turn record."""
        turn_id = _require_str(params, "turn_id")
        return {"turn": _dump_core_record(self.core_service.get_turn(turn_id))}

    async def core_turn_items(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 item records for a turn."""
        turn_id = _require_str(params, "turn_id")
        items = self.core_service.list_items(turn_id=turn_id)
        return {"items": [_dump_core_record(item) for item in items], "count": len(items)}

    async def core_trace_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 trace records."""
        trace_id = _optional_str(params, "trace_id")
        session_id = _optional_str(params, "session_id")
        turn_id = _optional_str(params, "turn_id")
        event_type = _optional_str(params, "event_type")
        traces = self.core_service.list_trace_records(
            trace_id=trace_id,
            session_id=session_id,
            turn_id=turn_id,
            event_type=event_type,
        )
        return {"traces": [_dump_core_record(trace) for trace in traces], "count": len(traces)}

    async def core_approval_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 approval records."""
        decision = _optional_str(params, "decision")
        target_type = _optional_str(params, "target_type")
        target_id = _optional_str(params, "target_id")
        approvals = self.core_service.list_approvals(
            decision=decision,
            target_type=target_type,
            target_id=target_id,
        )
        return {"approvals": [_dump_core_record(approval) for approval in approvals], "count": len(approvals)}

    async def core_retry_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 retry records."""
        session_id = _optional_str(params, "session_id")
        approval_id = _optional_str(params, "approval_id")
        status = _optional_str(params, "status")
        retries = self.core_service.list_retries(
            session_id=session_id,
            approval_id=approval_id,
            status=status,
        )
        return {"retries": [_dump_core_record(retry) for retry in retries], "count": len(retries)}

    async def core_artifact_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 artifact records."""
        owner_thread_id = _optional_str(params, "owner_thread_id")
        domain = _optional_str(params, "domain")
        kind = _optional_str(params, "kind")
        artifacts = self.core_service.list_artifacts(
            owner_thread_id=owner_thread_id,
            domain=domain,
            kind=kind,
        )
        return {"artifacts": [_dump_core_record(artifact) for artifact in artifacts], "count": len(artifacts)}

    async def core_job_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core v1.5 job records."""
        thread_id = _optional_str(params, "thread_id")
        session_id = _optional_str(params, "session_id")
        turn_id = _optional_str(params, "turn_id")
        domain = _optional_str(params, "domain")
        status = _optional_str(params, "status")
        jobs = self.core_service.list_jobs(
            thread_id=thread_id,
            session_id=session_id,
            turn_id=turn_id,
            domain=domain,
            status=status,
        )
        return {"jobs": [_dump_core_record(job) for job in jobs], "count": len(jobs)}

    async def job_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List Core job records."""
        return await self.core_job_list(params)

    async def job_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one Core job record."""
        job_id = _require_str(params, "job_id")
        return {"job": _dump_core_record(self.core_service.get_job(job_id))}

    async def job_cancel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel one Core job record."""
        job_id = _require_str(params, "job_id")
        reason = _optional_str(params, "reason")
        return {"job": _dump_core_record(self.core_service.cancel_job(job_id, reason=reason))}

    async def session_transcript(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return a transcript rebuilt from persisted events."""
        session_id = _require_str(params, "session_id")
        return {
            "session_id": session_id,
            "transcript": self.runtime_pool.read_transcript(session_id),
        }

    async def session_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return persisted protocol events for a session."""
        session_id = _require_str(params, "session_id")
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
        result = await self.runtime_pool.run_turn(
            session_id=session_id,
            user_input=user_input,
            domain=domain,
        )
        payload = result.model_dump(mode="json")
        payload["trace_id"] = _trace_id_from_events(payload.get("events", []))
        return payload

    async def turn_continue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Continue a pending turn when available."""
        session_id = _require_str(params, "session_id")
        result = await self.runtime_pool.continue_turn(session_id=session_id)
        return result.model_dump(mode="json")

    async def turn_retry(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retry a previously saved turn context."""
        session_id = _require_str(params, "session_id")
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
        resolved_approval_id = str(context.get("approval_id") or approval_id or "")
        if resolved_approval_id:
            approval = self.approval_store.get_approval(resolved_approval_id)
            if approval.get("status") != APPROVAL_APPROVED:
                raise ValueError(
                    f"approval is not approved: {approval.get('status')}"
                )
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
        async for event in self.runtime_pool.stream_turn(
            session_id=session_id,
            user_input=user_input,
            domain=domain,
        ):
            yield event

    async def meeting_capabilities(self) -> Dict[str, Any]:
        """Return configured Meeting MCP capabilities."""
        return await self.meeting_service.capabilities()

    async def meeting_analyze_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text through the Meeting MCP workflow."""
        text = _require_str(params, "text")
        title = params.get("title")
        if title is not None and not isinstance(title, str):
            raise ValueError("title must be a string when provided")
        return await self.meeting_service.analyze_text(text, title=title)

    async def meeting_process_recording(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process one real meeting recording through the Meeting MCP workflow."""
        path = _require_str(params, "path")
        engine = params.get("engine")
        language = params.get("language")
        title = params.get("title")
        for key, value in {"engine": engine, "language": language, "title": title}.items():
            if value is not None and not isinstance(value, str):
                raise ValueError(f"{key} must be a string when provided")
        return await self.meeting_service.process_recording(
            path,
            engine=engine,
            language=language,
            title=title,
        )

    async def meeting_process_audio_dir(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process all supported recordings under the configured audio acceptance directory."""
        audio_dir = params.get("audio_dir")
        engine = params.get("engine")
        language = params.get("language")
        for key, value in {"audio_dir": audio_dir, "engine": engine, "language": language}.items():
            if value is not None and not isinstance(value, str):
                raise ValueError(f"{key} must be a string when provided")
        return await self.meeting_service.process_audio_dir(
            audio_dir,
            engine=engine,
            language=language,
        )

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
        artifact = self.artifact_registry.register_file(
            path,
            session_id=session_id,
            turn_id=turn_id,
            domain=domain,
            kind=kind,
            metadata=merged_metadata,
        )
        self.core_service.record_gateway_artifact(artifact)
        trace_record = self.trace_store.record_artifact_operation(
            operation="register",
            artifact=artifact,
            trace_id=trace_id,
            metadata={"domain": domain, "kind": kind},
        )
        self.core_service.record_gateway_trace(trace_record)
        return {"artifact": artifact, "trace_id": trace_record["trace_id"]}

    async def artifact_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List registered artifacts."""
        session_id = _optional_str(params, "session_id")
        domain = _optional_str(params, "domain")
        kind = _optional_str(params, "kind")
        artifacts = self.artifact_registry.list_artifacts(session_id=session_id, domain=domain, kind=kind)
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
        trace_record = self.trace_store.record_artifact_operation(operation="get", artifact=artifact)
        self.core_service.record_gateway_trace(trace_record)
        return {"artifact": artifact, "trace_id": trace_record["trace_id"]}

    async def artifact_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read artifact content."""
        artifact_id = _require_str(params, "artifact_id")
        payload = self.artifact_registry.read_artifact(artifact_id)
        trace_record = self.trace_store.record_artifact_operation(operation="read", artifact=payload["artifact"])
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
        records = self.trace_store.list_records(
            trace_id=trace_id,
            session_id=session_id,
            turn_id=turn_id,
            artifact_id=artifact_id,
            event_type=event_type,
        )
        return {"traces": records, "count": len(records)}

    async def trace_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return records for one trace id."""
        trace_id = _require_str(params, "trace_id")
        return self.trace_store.get_trace(trace_id)

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
        approval = self.approval_store.request(
            action=action,
            request_summary=request_summary,
            trace_id=trace_id,
            session_id=session_id,
            turn_id=turn_id,
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
        approvals = self.approval_store.list_approvals(
            status=status,
            session_id=session_id,
            trace_id=trace_id,
        )
        return {"approvals": approvals, "count": len(approvals)}

    async def approval_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Return one approval request."""
        approval_id = _require_str(params, "approval_id")
        return {"approval": self.approval_store.get_approval(approval_id)}

    async def approval_approve(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Approve one pending approval request."""
        approval_id = _require_str(params, "approval_id")
        reason = _optional_str(params, "reason")
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
        packs = self.runtime_pool.pack_registry.list_packs(
            domain=_optional_str(params, "domain"),
            status=_optional_str(params, "status"),
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
        return {"pack": pack.to_dict()}

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
                ),
            )

    async def _dispatch(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if method == "initialize":
            return await self.initialize(params)
        if method == "health.ping":
            return await self.health_ping()
        if method == "session.start":
            return await self.session_start(params)
        if method == "session.resume":
            return await self.session_resume(params)
        if method == "session.list":
            return await self.session_list()
        if method == "session.get":
            return await self.core_session_get(params)
        if method == "session.read":
            return await self.session_read(params)
        if method == "thread.list":
            return await self.core_thread_list(params)
        if method == "turn.get":
            return await self.core_turn_get(params)
        if method == "turn.items":
            return await self.core_turn_items(params)
        if method == "core.trace.list":
            return await self.core_trace_list(params)
        if method == "core.approval.list":
            return await self.core_approval_list(params)
        if method == "core.retry.list":
            return await self.core_retry_list(params)
        if method == "core.artifact.list":
            return await self.core_artifact_list(params)
        if method == "core.job.list":
            return await self.core_job_list(params)
        if method == "job.list":
            return await self.job_list(params)
        if method == "job.get":
            return await self.job_get(params)
        if method == "job.cancel":
            return await self.job_cancel(params)
        if method == "session.transcript":
            return await self.session_transcript(params)
        if method == "session.events":
            return await self.session_events(params)
        if method == "session.close":
            return await self.session_close(params)
        if method == "turn.start":
            return await self.turn_start(params)
        if method == "turn.continue":
            return await self.turn_continue(params)
        if method == "turn.retry":
            return await self.turn_retry(params)
        if method == "turn.interrupt":
            return await self.turn_interrupt(params)
        if method == "meeting.capabilities":
            return await self.meeting_capabilities()
        if method == "meeting.analyze_text":
            return await self.meeting_analyze_text(params)
        if method == "meeting.process_recording":
            return await self.meeting_process_recording(params)
        if method == "meeting.process_audio_dir":
            return await self.meeting_process_audio_dir(params)
        if method == "artifact.register":
            return await self.artifact_register(params)
        if method == "artifact.list":
            return await self.artifact_list(params)
        if method == "artifact.get":
            return await self.artifact_get(params)
        if method == "artifact.read":
            return await self.artifact_read(params)
        if method == "trace.list":
            return await self.trace_list(params)
        if method == "trace.get":
            return await self.trace_get(params)
        if method == "approval.request":
            return await self.approval_request(params)
        if method == "approval.list":
            return await self.approval_list(params)
        if method == "approval.get":
            return await self.approval_get(params)
        if method == "approval.approve":
            return await self.approval_approve(params)
        if method == "approval.reject":
            return await self.approval_reject(params)
        if method == "policy.evaluate":
            return await self.policy_evaluate(params)
        if method == "workflow.list":
            return await self.workflow_list()
        if method == "pack.list":
            return await self.pack_list(params)
        if method == "pack.get":
            return await self.pack_get(params)
        raise LookupError(f"Unsupported method: {method}")


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
    return value


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


def _dump_core_record(record: Any) -> Dict[str, Any]:
    if hasattr(record, "model_dump"):
        return record.model_dump(mode="json")
    return dict(record)


def _error_code(exc: Exception) -> str:
    if isinstance(exc, KeyError):
        return "SESSION_NOT_FOUND"
    if isinstance(exc, ValueError):
        return "INVALID_PARAMS"
    if isinstance(exc, LookupError):
        return "METHOD_NOT_FOUND"
    return "RUNTIME_ERROR"
