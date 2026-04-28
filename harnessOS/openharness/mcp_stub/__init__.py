"""Minimal stub for the mcp package (requires Python >=3.10)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional

import mcp_stub.client
import mcp_stub.client.stdio
import mcp_stub.client.streamable_http
import mcp_stub.types


@dataclass
class StdioServerParameters:
    command: str = ""
    args: list = field(default_factory=list)
    env: Optional[dict] = None
    cwd: Optional[str] = None


class ClientSession:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def initialize(self):
        pass

    async def list_tools(self):
        return type('obj', (object,), {'tools': []})()

    async def call_tool(self, name, arguments):
        return type('obj', (object,), {'content': []})()

    async def list_resources(self):
        return type('obj', (object,), {'resources': []})()

    async def read_resource(self, uri):
        return type('obj', (object,), {'contents': []})()


class Tool:
    name: str = ""
    description: str = ""
    inputSchema: dict = {}


class Types:
    @staticmethod
    def Tool(**kwargs):
        return Tool()


types = Types()

__all__ = ["ClientSession", "StdioServerParameters", "Tool", "types"]
