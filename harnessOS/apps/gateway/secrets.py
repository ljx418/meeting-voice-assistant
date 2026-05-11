"""Secret masking helpers for gateway persistence boundaries."""

from __future__ import annotations

import re
from typing import Any


MASK = "[REDACTED]"

_SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_\-]{8,}\b"),
    re.compile(r"\b([A-Za-z0-9_-]*token|sk|api[_-]?key|secret|password)\s*[:=]\s*['\"]?[^'\"\s,;]+", re.IGNORECASE),
    re.compile(r"\bAuthorization\s*:\s*Bearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE),
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{8,}\b", re.IGNORECASE),
]


def mask_text(text: str) -> str:
    """Mask common API keys, bearer tokens, and credential assignments."""
    masked = text
    for pattern in _SECRET_PATTERNS:
        masked = pattern.sub(_mask_match, masked)
    return masked


def mask_value(value: Any) -> Any:
    """Recursively mask strings in JSON-like values."""
    if isinstance(value, str):
        return mask_text(value)
    if isinstance(value, list):
        return [mask_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(mask_value(item) for item in value)
    if isinstance(value, dict):
        masked: dict[Any, Any] = {}
        for key, item in value.items():
            if isinstance(key, str) and _is_secret_key(key):
                masked[key] = MASK
            else:
                masked[key] = mask_value(item)
        return masked
    return value


def _mask_match(match: re.Match[str]) -> str:
    text = match.group(0)
    if ":" in text:
        return f"{text.split(':', 1)[0]}: {MASK}"
    if "=" in text:
        return f"{text.split('=', 1)[0]}={MASK}"
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return f"{parts[0]} {MASK}"
    return MASK


def _is_secret_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return normalized in {
        "api_key",
        "apikey",
        "authorization",
        "access_token",
        "refresh_token",
        "token",
        "secret",
        "password",
    } or normalized.endswith("_token") or normalized.endswith("_secret")
