"""MCP server for the local knowledge governance service.

The server name remains `data_service` for compatibility with existing MCP
clients. The service boundary is MCP-first and workspace-scoped.
"""

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

from .security import validate_workspace_path
from .mcp_build_runtime import BuildRuntime
from .mcp_dispatcher import MCPToolDispatcher
from .mcp_resources import RESOURCE_SPECS, canonical_resource_uri, read_resource_payload
from .mcp_tool_registry import all_tool_specs
from .mcp_workspace_runtime import WorkspaceRuntime


if Server is None:  # pragma: no cover - environment dependent
    raise RuntimeError("The `mcp` package is required to run data_service.mcp_stdio") from _MCP_IMPORT_ERROR

server = Server("data_service")
_workspace = validate_workspace_path(os.getenv("DATA_SERVICE_WORKSPACE", Path.cwd()))
_workspace_runtime = WorkspaceRuntime(_workspace)
_build_runtime = BuildRuntime(_workspace_runtime)
_dispatcher = MCPToolDispatcher(
    default_workspace=_workspace,
    workspace_runtime=_workspace_runtime,
    build_runtime=_build_runtime,
)


def _json_content(payload: dict) -> List[TextContent]:
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]


@server.list_resources()
async def list_resources() -> List[Resource]:
    return [Resource(**spec) for spec in RESOURCE_SPECS]


@server.read_resource()
async def read_resource(uri: str) -> TextResourceContents:
    mime_type, text = read_resource_payload(
        uri,
        service=_dispatcher.service(),
        layout_payload=_workspace_runtime.layout_payload,
    )
    return TextResourceContents(uri=canonical_resource_uri(uri), mimeType=mime_type, text=text)


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [Tool(**spec) for spec in all_tool_specs()]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    return _json_content(await _dispatcher.call_tool(name, arguments))


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
