"""Transport abstractions for the Python SDK."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Protocol

from .errors import TransportError


class JsonRpcTransport(Protocol):
    """Synchronous JSON-RPC transport protocol."""

    def request(self, payload: dict[str, Any], *, headers: dict[str, str], timeout: float) -> dict[str, Any]:
        ...


class UrllibJsonRpcTransport:
    """Small stdlib HTTP transport for /v1/rpc."""

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    def request(self, payload: dict[str, Any], *, headers: dict[str, str], timeout: float) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                **headers,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
        except (TimeoutError, urllib.error.URLError, OSError) as exc:
            raise TransportError(f"transport request failed: {type(exc).__name__}") from exc
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TransportError("transport returned non JSON response") from exc
        if not isinstance(decoded, dict):
            raise TransportError("transport returned malformed JSON-RPC response")
        return decoded
