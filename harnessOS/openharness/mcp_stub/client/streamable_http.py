"""Stub for mcp.client.streamable_http module."""
from typing import Any, AsyncIterator, Tuple

class streamable_http_client:
    """Stub streamable_http_client context manager."""
    def __init__(self, url: str, **kwargs: Any):
        self.url = url
        self.kwargs = kwargs

    async def __aenter__(self) -> Tuple[AsyncIterator[str], AsyncIterator[str], Any]:
        # Return mock read/write streams and session_id getter
        async def read_stream() -> str:
            yield ""
        async def write_stream(msg: str) -> None:
            pass
        def get_session_id() -> str:
            return "stub-session-id"
        return read_stream, write_stream, get_session_id

    async def __aexit__(self, *args: Any) -> None:
        pass


__all__ = ["streamable_http_client"]
