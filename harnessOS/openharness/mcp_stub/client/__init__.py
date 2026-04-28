"""Stub for mcp.client module."""
# Note: ClientSession and StdioServerParameters are defined in mcp_stub/__init__.py
# and re-exported here for compatibility

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


class StdioServerParameters:
    def __init__(self, command="", args=None, env=None, cwd=None):
        self.command = command
        self.args = args or []
        self.env = env
        self.cwd = cwd


stdio_client = None
streamable_http_client = None

__all__ = ["ClientSession", "StdioServerParameters", "stdio_client", "streamable_http_client"]
