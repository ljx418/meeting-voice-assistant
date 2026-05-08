"""Connector execution runtime for gateway-managed connector jobs."""

from __future__ import annotations

import json
import os
import hashlib
from pathlib import Path
import subprocess
import threading
from typing import Any, Optional
from urllib.parse import urlparse

from apps.gateway.approvals import APPROVAL_APPROVED, ApprovalStore
from apps.gateway.artifacts import ArtifactRegistry
from apps.gateway.connectors import ConnectorRegistry
from apps.gateway.persistence import atomic_write_text
from apps.gateway.traces import TraceStore
from core.apps import ScopeContext
from core.services import CoreAppService


TERMINAL_JOB_STATUSES = {"completed", "failed", "cancelled"}


class ConnectorExecutionRuntime:
    """Minimal submit/poll/cancel/collect runtime for connector jobs."""

    def __init__(
        self,
        *,
        connector_registry: ConnectorRegistry,
        core_service: CoreAppService,
        artifact_registry: ArtifactRegistry,
        trace_store: Optional[TraceStore] = None,
        approval_store: Optional[ApprovalStore] = None,
    ) -> None:
        self.connector_registry = connector_registry
        self.core_service = core_service
        self.artifact_registry = artifact_registry
        self.trace_store = trace_store or TraceStore()
        self.approval_store = approval_store or ApprovalStore()

    def submit(
        self,
        *,
        connector_id: str,
        tool: str,
        payload: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        scope: Optional[ScopeContext] = None,
        defer: bool = False,
        parent_artifact_ids: Optional[list[str]] = None,
        approval_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Submit one connector operation as a Core job."""
        connector = self.connector_registry.get_connector(connector_id)
        resolved_scope = scope or ScopeContext()
        self._ensure_executable(connector)
        if tool not in set(connector.get("capabilities", {}).get("tools", [])):
            raise ValueError(f"Connector {connector_id} does not expose tool: {tool}")

        approved_ids: list[str] = []
        job = None
        if "external_call" in set(connector.get("requires_approval_for") or []):
            approval_context = _approval_context(
                connector_id=connector_id,
                tool=tool,
                payload=dict(payload or {}),
                session_id=session_id,
                turn_id=turn_id,
                scope=resolved_scope,
            )
            if approval_id is None:
                job = self.core_service.create_job(
                    workflow_id=f"connector.{connector_id}.{tool}",
                    domain=connector.get("domain"),
                    session_id=session_id,
                    turn_id=turn_id,
                    trace_id=trace_id,
                    scope=resolved_scope,
                    metadata={
                        "connector_execution": {
                            "connector_id": connector_id,
                            "tool": tool,
                            "payload": dict(payload or {}),
                            "mode": "deferred" if defer else "sync_stub",
                        }
                    },
                )
                approval = self.approval_store.request(
                    action="connector.submit",
                    request_summary=f"Approve connector execution {connector_id}.{tool}",
                    trace_id=trace_id,
                    session_id=session_id,
                    turn_id=turn_id,
                    app_id=resolved_scope.app_id,
                    project_id=resolved_scope.project_id,
                    workspace_id=resolved_scope.workspace_id,
                    risk_level="high",
                    metadata={"approval_context": approval_context, "job_id": job.job_id},
                )
                self.core_service.record_gateway_approval(approval)
                self._record_connector_trace(
                    connector=connector,
                    tool=tool,
                    job_id=job.job_id,
                    trace_id=trace_id,
                    session_id=session_id,
                    turn_id=turn_id,
                    scope=resolved_scope,
                    status="approval_required",
                    approval_ids=[str(approval["approval_id"])],
                    metadata={"requirement": "external_call", "approval_context": approval_context},
                )
                return {
                    **self._job_payload(job),
                    "approval_required": True,
                    "approval": approval,
                    "retry_context": {
                        "connector_id": connector_id,
                        "tool": tool,
                        "input": dict(payload or {}),
                        "session_id": session_id,
                        "turn_id": turn_id,
                        "approval_id": approval["approval_id"],
                    },
                }
            approval = self._validated_connector_approval(approval_id, approval_context)
            approved_ids = [str(approval["approval_id"])]
            stored_job_id = approval.get("metadata", {}).get("job_id")
            if not isinstance(stored_job_id, str) or not stored_job_id:
                raise ValueError(f"approval is missing connector job binding: {approval_id}")
            job = self.core_service.get_job(stored_job_id)
            if job.status in TERMINAL_JOB_STATUSES:
                return self._job_payload(job)
            session_id = job.session_id
            turn_id = job.turn_id
            trace_id = trace_id or job.trace_id
            resolved_scope = ScopeContext(
                app_id=job.app_id,
                project_id=job.project_id,
                workspace_id=job.workspace_id,
            )
        if job is None:
            job = self.core_service.create_job(
                workflow_id=f"connector.{connector_id}.{tool}",
                domain=connector.get("domain"),
                session_id=session_id,
                turn_id=turn_id,
                trace_id=trace_id,
                scope=resolved_scope,
                metadata={
                    "connector_execution": {
                        "connector_id": connector_id,
                        "tool": tool,
                        "payload": dict(payload or {}),
                        "mode": "deferred" if defer else "sync_stub",
                    }
                },
            )
        running = self.core_service.update_job(
            job_id=job.job_id,
            status="running",
            progress=0.1,
            metadata={"message": f"connector {connector_id}.{tool} started"},
        )
        self._record_connector_trace(
            connector=connector,
            tool=tool,
            job_id=running.job_id,
            trace_id=trace_id,
            session_id=session_id,
            turn_id=turn_id,
            scope=resolved_scope,
            status="running",
            approval_ids=approved_ids,
            metadata={"defer": defer, "parent_artifact_ids": list(parent_artifact_ids or [])},
        )
        if defer:
            worker = threading.Thread(
                target=self._run_deferred_job,
                kwargs={
                    "connector": connector,
                    "job_id": running.job_id,
                    "tool": tool,
                    "payload": dict(payload or {}),
                    "session_id": session_id,
                    "turn_id": turn_id,
                    "trace_id": trace_id,
                    "scope": resolved_scope,
                    "parent_artifact_ids": list(parent_artifact_ids or []),
                    "approval_ids": approved_ids,
                },
                daemon=True,
            )
            worker.start()
            return self._job_payload(running)

        return self._execute_job(
            connector=connector,
            job_id=running.job_id,
            tool=tool,
            payload=dict(payload or {}),
            session_id=session_id,
            turn_id=turn_id,
            trace_id=trace_id,
            scope=resolved_scope,
            parent_artifact_ids=list(parent_artifact_ids or []),
            approval_ids=approved_ids,
        )

    def _run_deferred_job(
        self,
        *,
        connector: dict[str, Any],
        job_id: str,
        tool: str,
        payload: dict[str, Any],
        session_id: Optional[str],
        turn_id: Optional[str],
        trace_id: Optional[str],
        scope: ScopeContext,
        parent_artifact_ids: list[str],
        approval_ids: list[str],
    ) -> None:
        try:
            self._execute_job(
                connector=connector,
                job_id=job_id,
                tool=tool,
                payload=payload,
                session_id=session_id,
                turn_id=turn_id,
                trace_id=trace_id,
                scope=scope,
                parent_artifact_ids=parent_artifact_ids,
                approval_ids=approval_ids,
            )
        except Exception:
            return

    def _execute_job(
        self,
        *,
        connector: dict[str, Any],
        job_id: str,
        tool: str,
        payload: dict[str, Any],
        session_id: Optional[str],
        turn_id: Optional[str],
        trace_id: Optional[str],
        scope: ScopeContext,
        parent_artifact_ids: list[str],
        approval_ids: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        connector_id = str(connector["connector_id"])
        resolved_approval_ids = list(approval_ids or [])
        try:
            job = self.core_service.get_job(job_id)
            if job.status == "cancelled":
                return self._job_payload(job)
            self._enforce_security_policy(connector, payload)
            if connector.get("metadata", {}).get("execution") == "mcp_stdio":
                result = _McpStdioClient(connector).call_tool(tool, payload)
                artifact = self._write_and_register_result_artifact(
                    connector=connector,
                    job_id=job_id,
                    tool=tool,
                    payload=payload,
                    session_id=session_id,
                    turn_id=turn_id,
                    scope=scope,
                    result=result,
                    stubbed=False,
                    parent_artifact_ids=parent_artifact_ids,
                )
            else:
                artifact = self._write_and_register_result_artifact(
                    connector=connector,
                    job_id=job_id,
                    tool=tool,
                    payload=payload,
                    session_id=session_id,
                    turn_id=turn_id,
                    scope=scope,
                    parent_artifact_ids=parent_artifact_ids,
                )
            current = self.core_service.get_job(job_id)
            if current.status == "cancelled":
                return self._job_payload(current)
            completed = self.core_service.update_job(
                job_id=job_id,
                status="completed",
                progress=1.0,
                artifact_ids=[artifact["artifact_id"]],
                metadata={
                    "message": f"connector {connector_id}.{tool} completed",
                    "connector_execution": {
                        "connector_id": connector_id,
                        "tool": tool,
                        "status": "completed",
                        "artifact_id": artifact["artifact_id"],
                    },
                },
            )
            self._record_connector_trace(
                connector=connector,
                tool=tool,
                job_id=job_id,
                trace_id=trace_id,
                session_id=session_id,
                turn_id=turn_id,
                scope=scope,
                status="completed",
                artifact_ids=[artifact["artifact_id"]],
                approval_ids=resolved_approval_ids,
                metadata={"artifact_id": artifact["artifact_id"]},
            )
            return {
                **self._job_payload(completed),
                "artifact": artifact,
            }
        except Exception as exc:
            failed = self.core_service.update_job(
                job_id=job_id,
                status="failed",
                progress=1.0,
                metadata={
                    "message": f"connector {connector_id}.{tool} failed: {exc}",
                    "connector_execution": {
                        "connector_id": connector_id,
                        "tool": tool,
                        "status": "failed",
                        "error": str(exc),
                    },
                    "failure_context": {
                        "type": "connector_execution_failed",
                        "retryable": True,
                        "message": str(exc),
                    },
                },
                failure_context={
                    "type": "connector_execution_failed",
                    "retryable": True,
                    "message": str(exc),
                },
            )
            self._record_connector_trace(
                connector=connector,
                tool=tool,
                job_id=job_id,
                trace_id=trace_id,
                session_id=session_id,
                turn_id=turn_id,
                scope=scope,
                status="failed",
                approval_ids=resolved_approval_ids,
                metadata={"failure_context": failed.failure_context},
            )
            return self._job_payload(failed)

    def _validated_connector_approval(
        self,
        approval_id: str,
        approval_context: dict[str, Any],
    ) -> dict[str, Any]:
        approval = self.approval_store.get_approval(approval_id)
        if approval.get("status") != APPROVAL_APPROVED:
            raise ValueError(f"approval is not approved: {approval_id}")
        if approval.get("action") != "connector.submit":
            raise ValueError(f"approval is not valid for connector.submit: {approval_id}")
        stored_context = approval.get("metadata", {}).get("approval_context")
        if not isinstance(stored_context, dict):
            raise ValueError(f"approval does not match connector submission: {approval_id}")
        expected_context = dict(approval_context)
        stored_comparable = dict(stored_context)
        expected_context.pop("turn_id", None)
        stored_comparable.pop("turn_id", None)
        if stored_comparable != expected_context:
            raise ValueError(f"approval does not match connector submission: {approval_id}")
        return approval

    def poll(self, *, job_id: str) -> dict[str, Any]:
        """Return one connector job plus lifecycle events."""
        job = self.core_service.get_job(job_id)
        return self._job_payload(job)

    def cancel(self, *, job_id: str, reason: Optional[str] = None) -> dict[str, Any]:
        """Cancel a queued or running connector job."""
        job = self.core_service.cancel_job(job_id, reason=reason)
        self._record_connector_trace(
            connector=None,
            tool=None,
            job_id=job_id,
            trace_id=job.trace_id,
            session_id=job.session_id,
            turn_id=job.turn_id,
            scope=ScopeContext(app_id=job.app_id, project_id=job.project_id, workspace_id=job.workspace_id),
            status="cancelled",
            metadata={"reason": reason},
        )
        return self._job_payload(job)

    def collect(self, *, job_id: str) -> dict[str, Any]:
        """Collect artifacts for a connector job."""
        job = self.core_service.get_job(job_id)
        artifacts = [
            self.core_service.get_artifact(artifact_id).model_dump(mode="json")
            for artifact_id in job.artifact_ids
        ]
        lineage = self.core_service.artifact_lineage(
            owner_session_id=job.session_id,
            owner_turn_id=job.turn_id,
            domain=job.domain,
        )
        self._record_connector_trace(
            connector=None,
            tool=None,
            job_id=job_id,
            trace_id=job.trace_id,
            session_id=job.session_id,
            turn_id=job.turn_id,
            scope=ScopeContext(app_id=job.app_id, project_id=job.project_id, workspace_id=job.workspace_id),
            status="collected",
            artifact_ids=list(job.artifact_ids),
            metadata={"artifact_count": len(artifacts)},
        )
        return {
            **self._job_payload(job),
            "artifacts": artifacts,
            "artifact_lineage": lineage,
        }

    def _ensure_executable(self, connector: dict[str, Any]) -> None:
        health = connector.get("health")
        capabilities = connector.get("capabilities", {})
        if health in {"available", "configured", "contract_stub"}:
            return
        if capabilities.get("contract_only"):
            return
        raise RuntimeError(f"Connector {connector.get('connector_id')} is not executable: {health}")

    def _record_connector_trace(
        self,
        *,
        connector: Optional[dict[str, Any]],
        tool: Optional[str],
        job_id: str,
        trace_id: Optional[str],
        session_id: Optional[str],
        turn_id: Optional[str],
        scope: ScopeContext,
        status: str,
        artifact_ids: Optional[list[str]] = None,
        approval_ids: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        connector_id = str(connector.get("connector_id")) if connector else None
        workflow_id = f"connector.{connector_id}.{tool}" if connector_id and tool else None
        record = {
            "trace_id": trace_id or self.trace_store.new_trace_id(),
            "session_id": session_id,
            "turn_id": turn_id,
            "app_id": scope.app_id,
            "project_id": scope.project_id,
            "workspace_id": scope.workspace_id,
            "event_type": "connector.execution",
            "status": status,
            "workflow_id": workflow_id,
            "artifact_ids": artifact_ids or [],
            "approval_ids": approval_ids or [],
            "input_summary": f"{connector_id or 'connector'} {tool or ''}".strip(),
            "metadata": {
                "job_id": job_id,
                "connector_id": connector_id,
                "tool": tool,
                **(metadata or {}),
            },
        }
        self.core_service.record_gateway_trace(record)

    def _enforce_security_policy(self, connector: dict[str, Any], payload: dict[str, Any]) -> None:
        execution_mode = str(
            connector.get("execution_mode")
            or connector.get("metadata", {}).get("execution")
            or connector.get("capabilities", {}).get("transport")
            or "stub"
        )
        metadata = connector.get("metadata", {})
        allowed_commands = {str(value) for value in connector.get("allowed_commands", []) if value}
        allowed_paths = [
            Path(str(value)).expanduser().resolve()
            for value in connector.get("allowed_paths", [])
            if value
        ]
        network_policy = str(connector.get("network_policy") or "none")
        allowed_network_hosts = {
            str(value) for value in connector.get("allowed_network_hosts", []) if value
        }

        if execution_mode in {"stdio", "mcp_stdio"}:
            command = str(metadata.get("command") or "")
            if not command:
                raise RuntimeError("connector_security_blocked: missing stdio command")
            command_path = Path(command).expanduser()
            command_candidates = {command}
            if command_path.exists():
                command_candidates.add(str(command_path.resolve()))
                command_candidates.add(command_path.name)
            if allowed_commands and command_candidates.isdisjoint(allowed_commands):
                raise RuntimeError(
                    f"connector_security_blocked: command {command} is not allowlisted for {connector.get('connector_id')}"
                )
            for required_path in _connector_payload_paths(payload, metadata):
                if not _path_allowed(required_path, allowed_paths):
                    raise RuntimeError(
                        f"connector_security_blocked: path {required_path} is not allowlisted for {connector.get('connector_id')}"
                    )
            return

        if execution_mode in {"http", "sse"}:
            if network_policy == "none":
                raise RuntimeError(
                    f"connector_security_blocked: network policy forbids {execution_mode} execution for {connector.get('connector_id')}"
                )
            endpoint = str(metadata.get("base_url") or metadata.get("endpoint") or "")
            host = urlparse(endpoint).netloc if endpoint else ""
            if network_policy == "allowlist" and (not host or host not in allowed_network_hosts):
                raise RuntimeError(
                    f"connector_security_blocked: host {host or '<missing>'} is not allowlisted for {connector.get('connector_id')}"
                )

    def _write_and_register_result_artifact(
        self,
        *,
        connector: dict[str, Any],
        job_id: str,
        tool: str,
        payload: dict[str, Any],
        session_id: Optional[str],
        turn_id: Optional[str],
        scope: Optional[ScopeContext] = None,
        result: Optional[dict[str, Any]] = None,
        stubbed: Optional[bool] = None,
        parent_artifact_ids: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        connector_id = str(connector["connector_id"])
        resolved_scope = scope or ScopeContext()
        output_path = self._result_path(job_id, connector_id, tool)
        is_stubbed = connector.get("health") == "contract_stub" if stubbed is None else stubbed
        result_payload = {
            "connector_id": connector_id,
            "tool": tool,
            "job_id": job_id,
            "status": "stubbed" if is_stubbed else "completed",
            "execution_deferred": is_stubbed,
            "input": payload,
            "result": result or {
                "message": f"{connector_id}.{tool} connector execution recorded.",
                "contract_only": bool(connector.get("capabilities", {}).get("contract_only")),
            },
        }
        atomic_write_text(
            output_path,
            json.dumps(result_payload, ensure_ascii=False, indent=2) + "\n",
        )
        artifact = self.artifact_registry.register_file(
            str(output_path),
            session_id=session_id,
            turn_id=turn_id,
            app_id=resolved_scope.app_id,
            project_id=resolved_scope.project_id,
            workspace_id=resolved_scope.workspace_id,
            domain=connector.get("domain"),
            kind="connector_result",
            metadata={
                "connector_id": connector_id,
                "tool": tool,
                "job_id": job_id,
                "stubbed": is_stubbed,
                "parent_artifact_ids": list(parent_artifact_ids or []),
                "execution_mode": connector.get("metadata", {}).get("execution"),
            },
        )
        artifact["app_id"] = resolved_scope.app_id
        artifact["project_id"] = resolved_scope.project_id
        artifact["workspace_id"] = resolved_scope.workspace_id
        self.core_service.record_gateway_artifact(artifact)
        return artifact

    def _result_path(self, job_id: str, connector_id: str, tool: str) -> Path:
        safe_name = f"{job_id}_{connector_id}_{tool}.json".replace("/", "_")
        output_dir = self.artifact_registry.root / "connector_execution"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / safe_name

    def _job_payload(self, job: Any) -> dict[str, Any]:
        events = self.core_service.list_job_events(job_id=job.job_id)
        return {
            "job": job.model_dump(mode="json"),
            "events": [event.model_dump(mode="json") for event in events],
            "terminal": job.status in TERMINAL_JOB_STATUSES,
        }


class McpStdioSession:
    """Persistent JSON-RPC stdio session for local MCP servers."""

    def __init__(self, connector: dict[str, Any]) -> None:
        metadata = connector.get("metadata", {})
        self.connector_id = str(connector.get("connector_id"))
        self.cwd = Path(str(metadata.get("cwd") or ".")).expanduser()
        self.command = str(metadata.get("command") or "python3")
        self.args = list(metadata.get("args") or [])
        self.timeout = int(metadata.get("request_timeout") or 3600)
        self.extra_env = {
            str(key): str(value)
            for key, value in (metadata.get("env") or {}).items()
            if value is not None
        }
        self._process: Optional[subprocess.Popen] = None
        self._stderr_lines: list[str] = []
        self._request_seq = 0

    def __enter__(self) -> "McpStdioSession":
        self.open()
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.close()

    def open(self) -> None:
        if self._process is not None and self._process.poll() is None:
            return
        env = dict(os.environ)
        env.update(self.extra_env)
        self._process = subprocess.Popen(
            [self.command, *self.args],
            cwd=str(self.cwd),
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        stderr_thread = threading.Thread(
            target=_read_stderr,
            args=(self._process, self._stderr_lines),
            daemon=True,
        )
        stderr_thread.start()
        initialize = self._request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "harnessOS", "version": "0.1.0"},
            },
            "init",
        )
        if initialize.get("error"):
            raise RuntimeError(f"MCP initialize failed: {initialize['error']}")

    def close(self) -> None:
        process = self._process
        self._process = None
        if process is None:
            return
        if process.stdin:
            process.stdin.close()
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=1)

    def call_tool(self, tool: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.open()
        response = self._request(
            "tools/call",
            {"name": tool, "arguments": payload},
            self._next_request_id("call"),
        )
        if response.get("error"):
            raise RuntimeError(f"MCP tool call failed: {response['error']}")
        result = response.get("result") or {}
        if bool(result.get("isError", False)):
            decoded = _decode_mcp_content(result.get("content", []))
            raise RuntimeError(decoded or f"MCP tool call returned isError=true for {tool}")
        return {
            "mcp_result": result,
            "content": _decode_mcp_content(result.get("content", [])),
            "is_error": bool(result.get("isError", False)),
            "server": self.connector_id,
        }

    def _request(
        self,
        method: str,
        params: dict[str, Any],
        request_id: str,
    ) -> dict[str, Any]:
        process = self._process
        if process is None:
            raise RuntimeError("MCP process is not started")
        if process.stdin is None or process.stdout is None:
            raise RuntimeError("MCP process stdio is not available")
        process.stdin.write(json.dumps({
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }, ensure_ascii=False, separators=(",", ":")) + "\n")
        process.stdin.flush()
        line = _read_stdout_line(process, self.timeout)
        if not line:
            stderr_tail = "".join(self._stderr_lines[-20:]).strip()
            suffix = f": {stderr_tail}" if stderr_tail else ""
            raise RuntimeError(f"MCP process closed without a JSON-RPC response{suffix}")
        return json.loads(line)

    def _next_request_id(self, prefix: str) -> str:
        self._request_seq += 1
        return f"{prefix}-{self._request_seq}"


class _McpStdioClient:
    """Small one-shot JSON-RPC stdio client for local MCP servers."""

    def __init__(self, connector: dict[str, Any]) -> None:
        self._connector = connector

    def call_tool(self, tool: str, payload: dict[str, Any]) -> dict[str, Any]:
        with McpStdioSession(self._connector) as session:
            return session.call_tool(tool, payload)


def _read_stdout_line(process: subprocess.Popen, timeout: int) -> str:
    result: list[str] = []
    error_holder: list[BaseException] = []

    def target() -> None:
        try:
            if process.stdout is None:
                return
            result.append(process.stdout.readline())
        except BaseException as exc:  # pragma: no cover - defensive thread boundary
            error_holder.append(exc)

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        process.kill()
        raise TimeoutError(f"MCP stdio request timed out after {timeout}s")
    if error_holder:
        raise RuntimeError(str(error_holder[0]))
    return result[0] if result else ""


def _read_stderr(process: subprocess.Popen, lines: list[str]) -> None:
    if process.stderr is None:
        return
    for line in process.stderr:
        lines.append(line)


def _decode_mcp_content(content: list[Any]) -> list[Any]:
    decoded: list[Any] = []
    for item in content:
        if not isinstance(item, dict):
            decoded.append(item)
            continue
        text = item.get("text")
        if item.get("type") == "text" and isinstance(text, str):
            try:
                decoded.append(json.loads(text))
            except json.JSONDecodeError:
                decoded.append(text)
        else:
            decoded.append(item)
    return decoded


def _approval_context(
    *,
    connector_id: str,
    tool: str,
    payload: dict[str, Any],
    session_id: Optional[str],
    turn_id: Optional[str],
    scope: ScopeContext,
) -> dict[str, Any]:
    return {
        "connector_id": connector_id,
        "tool": tool,
        "payload_digest": _payload_digest(payload),
        "session_id": session_id,
        "turn_id": turn_id,
        "app_id": scope.app_id,
        "project_id": scope.project_id,
        "workspace_id": scope.workspace_id,
    }


def _payload_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _connector_payload_paths(payload: dict[str, Any], metadata: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for key in ("cwd", "module_path"):
        value = metadata.get(key)
        if isinstance(value, str) and value:
            paths.append(Path(value).expanduser().resolve())
    for value in _walk_payload_values(payload):
        if not isinstance(value, str):
            continue
        if not (value.startswith("/") or value.startswith("~")):
            continue
        paths.append(Path(value).expanduser().resolve())
    return paths


def _walk_payload_values(value: Any) -> list[Any]:
    if isinstance(value, dict):
        items: list[Any] = []
        for nested in value.values():
            items.extend(_walk_payload_values(nested))
        return items
    if isinstance(value, list):
        items: list[Any] = []
        for nested in value:
            items.extend(_walk_payload_values(nested))
        return items
    return [value]


def _path_allowed(candidate: Path, allowed_paths: list[Path]) -> bool:
    if not allowed_paths:
        return False
    for allowed in allowed_paths:
        try:
            candidate.relative_to(allowed)
            return True
        except ValueError:
            continue
    return False
