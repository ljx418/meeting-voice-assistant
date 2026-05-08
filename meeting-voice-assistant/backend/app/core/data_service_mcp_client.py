"""MCP client adapter for the external Data Service.

The meeting app must not import Data Service internals.  This module talks to
the external MCP stdio server as a process boundary and returns degraded
payloads when the service is unavailable.
"""

from __future__ import annotations

import asyncio
import json
import os
import shlex
from pathlib import Path
from typing import Any

from app.config import config
from app.utils.logger import setup_logger

logger = setup_logger("data_service_mcp")


TERMINAL_SESSION_BUILD_STATUSES = {"succeeded", "failed", "blocked", "cancelled", "disposed"}


class DataServiceMcpUnavailable(RuntimeError):
    """Raised when the optional MCP client dependency or server is unavailable."""


class DataServiceMcpClient:
    """Small per-call MCP stdio client for Data Service tools."""

    def __init__(self) -> None:
        self.settings = config.knowledge_service

    @property
    def enabled(self) -> bool:
        return bool(self.settings.mcp_enabled)

    async def ingest_meeting_session(
        self,
        *,
        meeting_id: str,
        title: str,
        segments: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not self.enabled:
            return {
                "status": "disabled",
                "warnings": ["Data Service MCP is disabled"],
                "workspace_id": self.settings.mcp_workspace_id,
                "external_id": meeting_id,
                "session_id": None,
                "source_id": None,
                "operation_id": None,
                "session_graph": None,
                "speaker_summaries": [],
                "communities": [],
            }

        warnings: list[str] = []
        workspace_id = self.settings.mcp_workspace_id
        try:
            await self._ensure_workspace()
            created = await self.call_tool(
                "knowledge_session_create",
                {
                    "workspace_id": workspace_id,
                    "external_id": meeting_id,
                    "session_type": "meeting",
                    "title": title or meeting_id,
                    "ephemeral": bool(self.settings.mcp_session_ephemeral),
                    "ttl_seconds": int(self.settings.mcp_session_ttl_seconds),
                    "metadata": {"meeting_id": meeting_id, **dict(metadata or {})},
                },
            )
            session = (created.get("data") or {}).get("session") or {}
            data_service_session_id = session.get("session_id")
            if not data_service_session_id:
                warning_text = "; ".join(str(item) for item in (created.get("warnings") or []))
                raise DataServiceMcpUnavailable(warning_text or "knowledge_session_create did not return session_id")

            records = self._segments_to_records(segments)
            ingested = await self.call_tool(
                "knowledge_session_ingest",
                {
                    "workspace_id": workspace_id,
                    "session_id": data_service_session_id,
                    "source_type": "transcript",
                    "content_format": "turns",
                    "title": f"{title or meeting_id} 转写",
                    "records": records,
                    "metadata": {"meeting_id": meeting_id, "source": "meeting-voice-assistant", **dict(metadata or {})},
                    "auto_link": True,
                },
            )
            source = (ingested.get("data") or {}).get("source") or {}

            started = await self.call_tool(
                "knowledge_session_build_start",
                {"workspace_id": workspace_id, "session_id": data_service_session_id, "mode": "full", "sync": True},
            )
            operation_id = started.get("operation_id")
            build_status = started
            if build_status.get("status") not in TERMINAL_SESSION_BUILD_STATUSES:
                build_status = await self._poll_build(data_service_session_id, str(operation_id or ""))
            if build_status.get("status") != "succeeded":
                warnings.append(f"Data Service session build ended with status={build_status.get('status')}")

            snapshot = await self.call_tool(
                "knowledge_graph_snapshot",
                {
                    "workspace_id": workspace_id,
                    "scope": "session",
                    "session_id": data_service_session_id,
                    "max_nodes": 300,
                    "include_communities": True,
                    "include_source_refs": True,
                    "node_types": ["actor", "unit", "topic", "entity", "source"],
                },
            )
            graph = snapshot.get("data") or {}
            speaker_summaries = await self._speaker_summaries(data_service_session_id, records)

            return {
                "status": "ok" if not warnings else "degraded",
                "warnings": warnings,
                "workspace_id": workspace_id,
                "external_id": meeting_id,
                "session_id": data_service_session_id,
                "source_id": source.get("source_id"),
                "operation_id": operation_id,
                "build_status": build_status.get("status"),
                "session_graph": graph,
                "speaker_summaries": speaker_summaries,
                "communities": graph.get("communities", []),
            }
        except Exception as exc:
            logger.warning("[DataServiceMCP] meeting ingestion degraded: %s", exc)
            return {
                "status": "degraded",
                "warnings": [str(exc)],
                "workspace_id": workspace_id,
                "external_id": meeting_id,
                "session_id": None,
                "source_id": None,
                "operation_id": None,
                "session_graph": None,
                "speaker_summaries": [],
                "communities": [],
            }

    async def close_meeting_session(self, knowledge_session: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {"status": "disabled", "warnings": ["Data Service MCP is disabled"]}
        workspace_id = knowledge_session.get("workspace_id") or self.settings.mcp_workspace_id
        session_id = knowledge_session.get("session_id")
        if not session_id:
            return {"status": "skipped", "warnings": ["No Data Service session_id recorded"]}
        warnings: list[str] = []
        try:
            closed = await self.call_tool(
                "knowledge_session_close",
                {"workspace_id": workspace_id, "session_id": session_id},
            )
            status = closed.get("status", "closed")
            if bool(self.settings.mcp_delete_on_close):
                deleted = await self.call_tool(
                    "knowledge_session_delete",
                    {"workspace_id": workspace_id, "session_id": session_id},
                )
                status = deleted.get("status", "disposed")
                warnings.extend(deleted.get("warnings") or [])
            warnings.extend(closed.get("warnings") or [])
            return {"status": status, "warnings": warnings, "session_id": session_id, "workspace_id": workspace_id}
        except Exception as exc:
            logger.warning("[DataServiceMCP] close degraded: %s", exc)
            return {"status": "degraded", "warnings": [str(exc)], "session_id": session_id, "workspace_id": workspace_id}

    async def query_meeting_session(
        self,
        *,
        knowledge_session: dict[str, Any],
        query: str,
        top_k: int = 8,
        include_workspace_context: bool = True,
    ) -> dict[str, Any]:
        if not self.enabled:
            return {"status": "disabled", "warnings": ["Data Service MCP is disabled"], "hits": []}
        workspace_id = knowledge_session.get("workspace_id") or self.settings.mcp_workspace_id
        session_id = knowledge_session.get("session_id")
        if not session_id:
            return {"status": "skipped", "warnings": ["No Data Service session_id recorded"], "hits": []}
        try:
            result = await self.call_tool(
                "knowledge_session_query",
                {
                    "workspace_id": workspace_id,
                    "session_id": session_id,
                    "query": query,
                    "top_k": top_k,
                    "include_workspace_context": include_workspace_context,
                },
            )
            payload = result.get("data") or result
            return {
                "status": result.get("status") or payload.get("status") or "ok",
                "warnings": result.get("warnings") or payload.get("warnings") or [],
                **payload,
            }
        except Exception as exc:
            logger.warning("[DataServiceMCP] query degraded: %s", exc)
            return {"status": "degraded", "warnings": [str(exc)], "session_id": session_id, "workspace_id": workspace_id, "hits": []}

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            from mcp import ClientSession
            from mcp.client.stdio import StdioServerParameters, stdio_client
        except ModuleNotFoundError as exc:
            raise DataServiceMcpUnavailable("Python package `mcp` is not installed") from exc

        command_parts = shlex.split(str(self.settings.mcp_command or "").strip())
        if not command_parts:
            raise DataServiceMcpUnavailable("KNOWLEDGE_SERVICE_MCP_COMMAND is empty")

        env = os.environ.copy()
        cwd = self._backend_path()
        if cwd:
            existing_pythonpath = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = str(cwd) + (os.pathsep + existing_pythonpath if existing_pythonpath else "")

        server = StdioServerParameters(
            command=command_parts[0],
            args=command_parts[1:],
            env=env,
            cwd=str(cwd) if cwd else None,
        )

        async def _invoke() -> dict[str, Any]:
            async with stdio_client(server) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool(name, arguments)
                    return self._parse_tool_result(result)

        return await asyncio.wait_for(_invoke(), timeout=float(self.settings.request_timeout))

    async def _ensure_workspace(self) -> None:
        await self.call_tool(
            "knowledge_workspace_create",
            {
                "name": self.settings.mcp_workspace_id or self.settings.mcp_workspace_name,
                "tags": ["meeting", "session"],
            },
        )

    async def _poll_build(self, session_id: str, operation_id: str) -> dict[str, Any]:
        deadline = asyncio.get_running_loop().time() + float(self.settings.mcp_build_timeout)
        latest: dict[str, Any] = {}
        while asyncio.get_running_loop().time() < deadline:
            latest = await self.call_tool(
                "knowledge_session_build_status",
                {
                    "workspace_id": self.settings.mcp_workspace_id,
                    "session_id": session_id,
                    "operation_id": operation_id,
                },
            )
            if latest.get("status") in TERMINAL_SESSION_BUILD_STATUSES:
                return latest
            await asyncio.sleep(float(self.settings.mcp_build_poll_interval))
        return {"status": "timeout", "operation_id": operation_id, "warnings": ["Data Service session build timed out"], "data": latest}

    async def _speaker_summaries(self, session_id: str, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        summaries: list[dict[str, Any]] = []
        actor_ids = list(dict.fromkeys(str(record.get("actor_id")) for record in records if record.get("actor_id")))
        for actor_id in actor_ids:
            try:
                summary = await self.call_tool(
                    "knowledge_actor_summary",
                    {
                        "workspace_id": self.settings.mcp_workspace_id,
                        "session_id": session_id,
                        "actor_id": actor_id,
                        "include_units": True,
                        "unit_types": ["statement", "decision", "task", "risk", "question"],
                    },
                )
                summaries.append(summary.get("data") or summary)
            except Exception as exc:
                summaries.append({"actor": {"actor_id": actor_id, "label": actor_id}, "summary": "", "warnings": [str(exc)]})
        return summaries

    def _backend_path(self) -> Path | None:
        configured = self.settings.mcp_backend_path
        if configured:
            return Path(configured).expanduser().resolve()
        candidate = Path(__file__).resolve().parents[4] / "data_service" / "backend"
        return candidate if candidate.exists() else None

    @staticmethod
    def _segments_to_records(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        records = []
        for index, segment in enumerate(segments):
            text = str(segment.get("text") or "").strip()
            if not text:
                continue
            speaker = str(segment.get("speaker") or "unknown")
            records.append(
                {
                    "record_id": f"turn-{index + 1:04d}",
                    "actor_id": speaker,
                    "actor_label": speaker,
                    "role": "speaker",
                    "start_time": segment.get("start_time"),
                    "end_time": segment.get("end_time"),
                    "text": text,
                    "metadata": {},
                }
            )
        return records

    @staticmethod
    def _parse_tool_result(result: Any) -> dict[str, Any]:
        content = getattr(result, "content", None) or []
        if not content:
            return {}
        text = getattr(content[0], "text", None)
        if text is None and isinstance(content[0], dict):
            text = content[0].get("text")
        if not text:
            return {}
        if bool(getattr(result, "isError", False)):
            return {"status": "blocked", "warnings": [str(text)], "data": {"error": {"message": str(text), "retryable": False}}}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"status": "blocked", "warnings": [str(text)], "data": {"raw": str(text)}}
