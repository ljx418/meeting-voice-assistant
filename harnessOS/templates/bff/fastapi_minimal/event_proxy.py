"""EventSource proxy helpers for the V3.5-D2 Minimal BFF Smoke."""

from __future__ import annotations

import urllib.request
from typing import Any, Iterable, Protocol
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


class UpstreamEventStream(Protocol):
    def __iter__(self) -> Iterable[bytes | str]:
        ...

    def close(self) -> None:
        ...


def open_upstream_eventsource(url: str) -> Any:
    """Open an upstream EventSource URL.

    The signed URL already contains the short-lived upstream subscription token.
    """
    return urllib.request.urlopen(url, timeout=30)


def proxy_sse_frames(upstream: Any):
    """Yield upstream SSE frames and close upstream when downstream ends."""
    try:
        for chunk in upstream:
            if isinstance(chunk, bytes):
                yield _redact_chunk(chunk.decode("utf-8", errors="replace")).encode("utf-8")
            else:
                yield _redact_chunk(str(chunk)).encode("utf-8")
    finally:
        close = getattr(upstream, "close", None)
        if callable(close):
            close()


def _redact_chunk(value: str) -> str:
    if "subscription_token=" not in value:
        return value
    lines = []
    for line in value.splitlines(keepends=True):
        if "subscription_token=" not in line:
            lines.append(line)
            continue
        if "?" in line:
            parsed = urlsplit(line.strip())
            query = urlencode(
                [
                    (key, "[REDACTED]" if key == "subscription_token" else item)
                    for key, item in parse_qsl(parsed.query, keep_blank_values=True)
                ]
            )
            redacted = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, query, parsed.fragment))
            suffix = "\n" if line.endswith("\n") else ""
            lines.append(redacted + suffix)
        else:
            lines.append(line.split("subscription_token=", 1)[0] + "subscription_token=[REDACTED]\n")
    return "".join(lines)
