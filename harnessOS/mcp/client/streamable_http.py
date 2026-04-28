from __future__ import annotations
async def streamable_http_client(url, headers=None, **kwargs):
    class StubTransport:
        async def __aenter__(self):
            return (type('obj', (object,), {})(), type('obj', (object,), {})())
        async def __aexit__(self, *args): pass
    return StubTransport()
__all__ = ["streamable_http_client"]
