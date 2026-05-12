"""Secret hygiene helpers for the V3.5-F FastAPI BFF template."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


SECRET_KEYS = ("token", "authorization", "secret", "credential")


def redact(value: Any) -> Any:
    """Redact secrets from strings and nested JSON-compatible values."""
    if isinstance(value, dict):
        return {key: ("[REDACTED]" if _is_secret_key(key) else redact(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)
    if not isinstance(value, str):
        return value
    text = _redact_url(value)
    text = re.sub(r"(?i)(authorization:\s*bearer\s+)[^\s,;]+", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)(bearer\s+)[^\s,;]+", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)(subscription_token=)[^&\s]+", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)(capability_token=)[^&\s]+", r"\1[REDACTED]", text)
    return text


def _redact_url(value: str) -> str:
    try:
        parsed = urlsplit(value)
    except Exception:
        return value
    if not parsed.query:
        return value
    query = []
    changed = False
    for key, item in parse_qsl(parsed.query, keep_blank_values=True):
        if _is_secret_key(key):
            query.append((key, "[REDACTED]"))
            changed = True
        else:
            query.append((key, item))
    if not changed:
        return value
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


def _is_secret_key(key: Any) -> bool:
    lowered = str(key).lower()
    return any(secret in lowered for secret in SECRET_KEYS)
