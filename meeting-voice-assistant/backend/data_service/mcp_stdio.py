"""MCP server for data_service."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Resource, TextContent, TextResourceContents, Tool
    _MCP_IMPORT_ERROR = None
except ModuleNotFoundError as exc:  # pragma: no cover - environment dependent
    Server = None  # type: ignore[assignment]
    stdio_server = None  # type: ignore[assignment]
    Resource = TextContent = TextResourceContents = Tool = object  # type: ignore[assignment]
    _MCP_IMPORT_ERROR = exc

from .models import QueryMode
from .service import DataService


if Server is None:  # pragma: no cover - environment dependent
    raise RuntimeError("The `mcp` package is required to run data_service.mcp_stdio") from _MCP_IMPORT_ERROR

server = Server("data_service")
_workspace = Path(os.getenv("DATA_SERVICE_WORKSPACE", Path.cwd())).resolve()


def _service() -> DataService:
    return DataService(_workspace)


@server.list_resources()
async def list_resources() -> List[Resource]:
    return [
        Resource(
            uri="data_service://summary",
            name="Workspace Summary",
            description="Current data_service summary for the active workspace",
            mimeType="text/markdown",
        ),
        Resource(
            uri="data_service://layout",
            name="Workspace Layout",
            description="Artifact layout for row, llmwiki, graphrag, and summary layers",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> TextResourceContents:
    service = _service()
    if uri == "data_service://summary":
        plan = service.build_ingest_plan([])
        service.write_summary_files(plan)
        return TextResourceContents(uri=uri, mimeType="text/markdown", text=service.layout.summary_md.read_text(encoding="utf-8"))
    if uri == "data_service://layout":
        layout = service.layout
        payload = {
            "workspace": str(layout.workspace),
            "row_manifest": str(layout.row_manifest),
            "llmwiki": {
                "raw": str(layout.raw_dir),
                "readable": str(layout.readable_dir),
                "normalized": str(layout.normalized_dir),
                "pages": str(layout.llmwiki_pages_dir),
                "state": str(layout.llmwiki_state_dir),
            },
            "graphrag": {
                "input": str(layout.graphrag_input_dir),
                "cache": str(layout.graphrag_cache_dir),
                "state": str(layout.graphrag_state_dir),
            },
            "summary": str(layout.summary_dir),
        }
        return TextResourceContents(uri=uri, mimeType="application/json", text=json.dumps(payload, ensure_ascii=False, indent=2))
    raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="knowledge_ingest",
            description="Ingest files once and fan out to llmwiki and graphrag",
            inputSchema={
                "type": "object",
                "properties": {
                    "paths": {"type": "array", "items": {"type": "string"}},
                    "workspace": {"type": "string"},
                },
                "required": ["paths"],
            },
        ),
        Tool(
            name="knowledge_query",
            description="Query llmwiki, graphrag, or hybrid mode",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "mode": {"type": "string", "enum": [mode.value for mode in QueryMode]},
                    "top_k": {"type": "integer", "default": 8},
                    "workspace": {"type": "string"},
                },
                "required": ["query"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    global _workspace
    workspace = arguments.get("workspace")
    if workspace:
        _workspace = Path(workspace).resolve()
    service = _service()

    if name == "knowledge_ingest":
        paths = arguments.get("paths") or []
        plan = service.build_ingest_plan(paths)
        service.write_summary_files(plan)
        results = service.run_default_pipeline(plan)
        payload = {
            "workspace": str(service.workspace),
            "results": [
                {"engine": result.engine, "status": result.status, "meta": result.meta}
                for result in results
            ],
        }
        return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]

    if name == "knowledge_query":
        response = service.query(
            arguments.get("query", ""),
            mode=QueryMode(arguments.get("mode", QueryMode.HYBRID.value)),
            top_k=int(arguments.get("top_k", 8)),
        )
        payload = {
            "mode": response.mode.value,
            "query": response.query,
            "answer": response.answer,
            "hits": [
                {
                    "title": hit.title,
                    "snippet": hit.snippet,
                    "source": hit.source,
                    "score": hit.score,
                    "meta": hit.meta,
                }
                for hit in response.hits
            ],
            "engine_payloads": response.engine_payloads,
        }
        return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]

    raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
