"""EventSource proxy for the V3.5-F BFF template."""

from __future__ import annotations

import urllib.request
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .security import redact


def upstream_eventsource_url(raw_url: str, *, last_event_id: str | None = None, cursor: str | None = None) -> str:
    """Forward Last-Event-ID as cursor without rewriting upstream event ids."""
    selected_cursor = last_event_id or cursor
    if not selected_cursor:
        return raw_url
    parsed = urlsplit(raw_url)
    query = [(key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True) if key not in {"cursor", "last_event_id"}]
    query.append(("cursor", selected_cursor))
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


def open_upstream_eventsource(url: str) -> Any:
    return urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "text/event-stream"}), timeout=30)


def proxy_sse_frames(upstream: Iterable[bytes]) -> Iterable[bytes]:
    try:
        for frame in upstream:
            yield str(redact(frame.decode("utf-8", errors="replace"))).encode("utf-8")
    finally:
        close = getattr(upstream, "close", None)
        if callable(close):
            close()
