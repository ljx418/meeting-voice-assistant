"""Stub for mcp.client.stdio module."""
from typing import Any, AsyncIterator, Tuple

class stdio_client:
    """Stub stdio_client context manager."""
    def __init__(self, params: Any):
        self.params = params

    async def __aenter__(self) -> Tuple[AsyncIterator[str], AsyncIterator[str]]:
        # Return mock read/write streams
        async def read_stream() -> str:
            yield ""
        async def write_stream(msg: str) -> None:
            pass
        return read_stream, write_stream

    async def __aexit__(self, *args: Any) -> None:
        pass


__all__ = ["stdio_client"]
