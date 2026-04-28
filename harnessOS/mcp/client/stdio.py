from __future__ import annotations
async def stdio_client(server_params, **kwargs):
    class StubTransport:
        async def __aenter__(self):
            return (type('obj', (object,), {})(), type('obj', (object,), {})())
        async def __aexit__(self, *args): pass
    return StubTransport()
__all__ = ["stdio_client"]
