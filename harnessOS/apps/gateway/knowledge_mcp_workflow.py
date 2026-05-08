"""Knowledge workflow runner backed by the Data Service MCP connector."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from apps.gateway.connector_execution import ConnectorExecutionRuntime, McpStdioSession


DATA_SERVICE_CONNECTOR_ID = "data_service_mcp"
TERMINAL_STATUSES = {"completed", "failed", "blocked", "cancelled"}


@dataclass(frozen=True)
class KnowledgeMcpWorkflowResult:
    """Result for one external Data Service MCP acceptance workflow."""

    status: str
    workspace_id: Optional[str]
    operation_id: Optional[str]
    steps: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "workspace_id": self.workspace_id,
            "operation_id": self.operation_id,
            "steps": list(self.steps),
            "warnings": list(self.warnings),
        }


class KnowledgeMcpWorkflowRunner:
    """Run the external Data Service MCP lifecycle through connector jobs."""

    def __init__(self, connector_runtime: ConnectorExecutionRuntime) -> None:
        self.connector_runtime = connector_runtime

    def run_acceptance(
        self,
        *,
        name: str,
        query: str,
        texts: Optional[list[dict[str, Any]]] = None,
        paths: Optional[list[str]] = None,
        owner: str = "harness",
        build_mode: str = "full",
        session_id: Optional[str] = None,
        turn_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        parent_artifact_ids: Optional[list[str]] = None,
        poll_interval: float = 0.2,
        max_polls: int = 120,
    ) -> KnowledgeMcpWorkflowResult:
        """Run create/import/build/poll/query/feedback/rules/review/plan/archive."""
        steps: list[dict[str, Any]] = []
        warnings: list[str] = []
        connector = self.connector_runtime.connector_registry.get_connector(DATA_SERVICE_CONNECTOR_ID)
        session: Optional[McpStdioSession] = None

        if connector.get("metadata", {}).get("execution") == "mcp_stdio":
            session = McpStdioSession(connector)

        context = session if session is not None else _NullMcpSession()
        with context as mcp_session:
            active_session = mcp_session if isinstance(mcp_session, McpStdioSession) else None
            return self._run_acceptance_steps(
                name=name,
                query=query,
                texts=texts,
                paths=paths,
                owner=owner,
                build_mode=build_mode,
                session_id=session_id,
                turn_id=turn_id,
                trace_id=trace_id,
                parent_artifact_ids=parent_artifact_ids or [],
                poll_interval=poll_interval,
                max_polls=max_polls,
                steps=steps,
                warnings=warnings,
                mcp_session=active_session,
            )

    def _run_acceptance_steps(
        self,
        *,
        name: str,
        query: str,
        texts: Optional[list[dict[str, Any]]],
        paths: Optional[list[str]],
        owner: str,
        build_mode: str,
        session_id: Optional[str],
        turn_id: Optional[str],
        trace_id: Optional[str],
        parent_artifact_ids: list[str],
        poll_interval: float,
        max_polls: int,
        steps: list[dict[str, Any]],
        warnings: list[str],
        mcp_session: Optional[McpStdioSession],
    ) -> KnowledgeMcpWorkflowResult:
        create = self._call(
            "knowledge_workspace_create",
            {"name": name, "owner": owner, "tags": ["harnessos-e2e"]},
            session_id=session_id,
            turn_id=turn_id,
            trace_id=trace_id,
            steps=steps,
            mcp_session=mcp_session,
            parent_artifact_ids=[],
        )
        workspace_id = _require_workspace_id(create)

        self._call(
            "knowledge_source_import",
            {
                "workspace_id": workspace_id,
                "paths": list(paths or []),
                "texts": list(texts or []),
                "metadata": {"owner": owner, "workflow": "harnessos_external_mcp_acceptance"},
            },
            session_id=session_id,
            turn_id=turn_id,
            trace_id=trace_id,
            steps=steps,
            mcp_session=mcp_session,
            parent_artifact_ids=parent_artifact_ids,
        )

        build = self._call(
            "knowledge_build_start",
            {"workspace_id": workspace_id, "mode": build_mode},
            session_id=session_id,
            turn_id=turn_id,
            trace_id=trace_id,
            steps=steps,
            mcp_session=mcp_session,
            parent_artifact_ids=_latest_artifact_ids(steps),
        )
        operation_id = build.get("operation_id")

        status = build.get("status")
        for _ in range(max_polls):
            if status in TERMINAL_STATUSES:
                break
            time.sleep(poll_interval)
            polled = self._call(
                "knowledge_build_status",
                {"workspace_id": workspace_id, "operation_id": operation_id},
                session_id=session_id,
                turn_id=turn_id,
                trace_id=trace_id,
                steps=steps,
                mcp_session=mcp_session,
                parent_artifact_ids=_latest_artifact_ids(steps),
            )
            status = polled.get("status")
        if status not in TERMINAL_STATUSES:
            warnings.append("build polling exceeded max_polls")
        if status != "completed":
            return KnowledgeMcpWorkflowResult(
                status=str(status or "failed"),
                workspace_id=workspace_id,
                operation_id=str(operation_id) if operation_id else None,
                steps=tuple(steps),
                warnings=tuple(warnings),
            )

        self._call(
            "knowledge_query_v2",
            {"workspace_id": workspace_id, "query": query, "mode": "hybrid", "top_k": 8},
            session_id=session_id,
            turn_id=turn_id,
            trace_id=trace_id,
            steps=steps,
            mcp_session=mcp_session,
            parent_artifact_ids=_latest_artifact_ids(steps),
        )
        self._call(
            "knowledge_quality_feedback_v2",
            {
                "workspace_id": workspace_id,
                "target_type": "query",
                "target_id": query,
                "action": "needs_review",
                "reason": "harnessOS external MCP acceptance feedback",
                "metadata": {"source": "harnessos"},
            },
            session_id=session_id,
            turn_id=turn_id,
            trace_id=trace_id,
            steps=steps,
            mcp_session=mcp_session,
            parent_artifact_ids=_latest_artifact_ids(steps),
        )
        rules = self._call(
            "knowledge_correction_rules_v2",
            {"workspace_id": workspace_id, "status": "draft", "limit": 20},
            session_id=session_id,
            turn_id=turn_id,
            trace_id=trace_id,
            steps=steps,
            mcp_session=mcp_session,
            parent_artifact_ids=_latest_artifact_ids(steps),
        )
        rule_id = _first_rule_id(rules)
        if rule_id:
            self._call(
                "knowledge_review_correction_rule_v2",
                {
                    "workspace_id": workspace_id,
                    "rule_id": rule_id,
                    "status": "approved",
                    "reviewer": "harnessos",
                    "note": "External MCP acceptance review.",
                },
                session_id=session_id,
                turn_id=turn_id,
                trace_id=trace_id,
                steps=steps,
                mcp_session=mcp_session,
                parent_artifact_ids=_latest_artifact_ids(steps),
            )
        else:
            warnings.append("no draft correction rule returned; review step skipped")

        self._call(
            "knowledge_correction_plan_v2",
            {"workspace_id": workspace_id, "rebuild": False},
            session_id=session_id,
            turn_id=turn_id,
            trace_id=trace_id,
            steps=steps,
            mcp_session=mcp_session,
            parent_artifact_ids=_latest_artifact_ids(steps),
        )
        archive = self._call(
            "knowledge_workspace_archive",
            {"workspace_id": workspace_id, "reason": "harnessOS external MCP acceptance completed"},
            session_id=session_id,
            turn_id=turn_id,
            trace_id=trace_id,
            steps=steps,
            mcp_session=mcp_session,
            parent_artifact_ids=_latest_artifact_ids(steps),
        )

        return KnowledgeMcpWorkflowResult(
            status=str(archive.get("status") or "ok"),
            workspace_id=workspace_id,
            operation_id=str(operation_id) if operation_id else None,
            steps=tuple(steps),
            warnings=tuple(warnings),
        )

    def _call(
        self,
        tool: str,
        payload: dict[str, Any],
        *,
        session_id: Optional[str],
        turn_id: Optional[str],
        trace_id: Optional[str],
        steps: list[dict[str, Any]],
        mcp_session: Optional[McpStdioSession] = None,
        parent_artifact_ids: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        if mcp_session is not None:
            return self._call_with_session(
                tool,
                payload,
                session_id=session_id,
                turn_id=turn_id,
                trace_id=trace_id,
                steps=steps,
                mcp_session=mcp_session,
                parent_artifact_ids=parent_artifact_ids,
            )
        submitted = self.connector_runtime.submit(
            connector_id=DATA_SERVICE_CONNECTOR_ID,
            tool=tool,
            payload=payload,
            session_id=session_id,
            turn_id=turn_id,
            trace_id=trace_id,
            parent_artifact_ids=parent_artifact_ids or [],
        )
        envelope = _extract_connector_envelope(submitted)
        steps.append({
            "tool": tool,
            "job_id": submitted["job"]["job_id"],
            "job_status": submitted["job"]["status"],
            "artifact_id": submitted.get("artifact", {}).get("artifact_id"),
            "envelope": envelope,
        })
        if submitted["job"]["status"] != "completed":
            raise RuntimeError(f"{tool} connector job did not complete: {submitted['job']['status']}")
        return envelope

    def _call_with_session(
        self,
        tool: str,
        payload: dict[str, Any],
        *,
        session_id: Optional[str],
        turn_id: Optional[str],
        trace_id: Optional[str],
        steps: list[dict[str, Any]],
        mcp_session: McpStdioSession,
        parent_artifact_ids: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        connector = self.connector_runtime.connector_registry.get_connector(DATA_SERVICE_CONNECTOR_ID)
        if tool not in set(connector.get("capabilities", {}).get("tools", [])):
            raise ValueError(f"Connector {DATA_SERVICE_CONNECTOR_ID} does not expose tool: {tool}")

        job = self.connector_runtime.core_service.create_job(
            workflow_id=f"connector.{DATA_SERVICE_CONNECTOR_ID}.{tool}",
            domain=connector.get("domain"),
            session_id=session_id,
            turn_id=turn_id,
            trace_id=trace_id,
            metadata={
                "connector_execution": {
                    "connector_id": DATA_SERVICE_CONNECTOR_ID,
                    "tool": tool,
                    "payload": dict(payload),
                    "mode": "mcp_stdio_session",
                }
            },
        )
        running = self.connector_runtime.core_service.update_job(
            job_id=job.job_id,
            status="running",
            progress=0.1,
            metadata={"message": f"connector {DATA_SERVICE_CONNECTOR_ID}.{tool} started"},
        )
        try:
            result = mcp_session.call_tool(tool, payload)
            artifact = self.connector_runtime._write_and_register_result_artifact(
                connector=connector,
                job_id=running.job_id,
                tool=tool,
                payload=payload,
                session_id=session_id,
                turn_id=turn_id,
                result=result,
                stubbed=False,
                parent_artifact_ids=parent_artifact_ids or [],
            )
            completed = self.connector_runtime.core_service.update_job(
                job_id=running.job_id,
                status="completed",
                progress=1.0,
                artifact_ids=[artifact["artifact_id"]],
                metadata={
                    "message": f"connector {DATA_SERVICE_CONNECTOR_ID}.{tool} completed",
                    "connector_execution": {
                        "connector_id": DATA_SERVICE_CONNECTOR_ID,
                        "tool": tool,
                        "status": "completed",
                        "artifact_id": artifact["artifact_id"],
                        "mode": "mcp_stdio_session",
                    },
                },
            )
        except Exception as exc:
            failure_context = {
                "type": "connector_execution_failed",
                "retryable": True,
                "message": str(exc),
            }
            failed = self.connector_runtime.core_service.update_job(
                job_id=running.job_id,
                status="failed",
                progress=1.0,
                failure_context=failure_context,
                metadata={
                    "message": f"connector {DATA_SERVICE_CONNECTOR_ID}.{tool} failed: {exc}",
                    "connector_execution": {
                        "connector_id": DATA_SERVICE_CONNECTOR_ID,
                        "tool": tool,
                        "status": "failed",
                        "error": str(exc),
                        "mode": "mcp_stdio_session",
                    },
                    "failure_context": failure_context,
                },
            )
            submitted = self.connector_runtime._job_payload(failed)
            steps.append({
                "tool": tool,
                "job_id": submitted["job"]["job_id"],
                "job_status": submitted["job"]["status"],
                "artifact_id": None,
                "envelope": {},
            })
            raise RuntimeError(f"{tool} connector job failed: {exc}") from exc

        submitted = {
            **self.connector_runtime._job_payload(completed),
            "artifact": artifact,
        }
        envelope = _extract_connector_envelope(submitted)
        steps.append({
            "tool": tool,
            "job_id": submitted["job"]["job_id"],
            "job_status": submitted["job"]["status"],
            "artifact_id": artifact["artifact_id"],
            "envelope": envelope,
        })
        return envelope


class _NullMcpSession:
    def __enter__(self) -> "_NullMcpSession":
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        return None


def _extract_connector_envelope(submitted: dict[str, Any]) -> dict[str, Any]:
    artifact = submitted.get("artifact") or {}
    path = artifact.get("path")
    if not path:
        raise RuntimeError("connector submission did not return an artifact path")
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    content = payload.get("result", {}).get("content")
    if isinstance(content, list) and content and isinstance(content[0], dict):
        return dict(content[0])
    result = payload.get("result")
    if isinstance(result, dict) and {"workspace_id", "status", "data"}.issubset(result):
        return dict(result)
    raise RuntimeError("connector result did not contain a Data Service envelope")


def _require_workspace_id(envelope: dict[str, Any]) -> str:
    workspace_id = envelope.get("workspace_id")
    if not isinstance(workspace_id, str) or not workspace_id:
        raise RuntimeError("Data Service envelope did not return workspace_id")
    return workspace_id


def _first_rule_id(envelope: dict[str, Any]) -> Optional[str]:
    data = envelope.get("data")
    if not isinstance(data, dict):
        return None
    candidates = data.get("rules") or data.get("items") or data.get("correction_rules") or []
    if not isinstance(candidates, list) or not candidates:
        return None
    first = candidates[0]
    if not isinstance(first, dict):
        return None
    value = first.get("rule_id") or first.get("id")
    return str(value) if value else None


def _latest_artifact_ids(steps: list[dict[str, Any]]) -> list[str]:
    for step in reversed(steps):
        artifact_id = step.get("artifact_id")
        if isinstance(artifact_id, str) and artifact_id:
            return [artifact_id]
    return []
