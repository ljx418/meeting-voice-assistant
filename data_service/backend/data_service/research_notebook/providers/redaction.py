"""Public payload redaction helpers for provider-backed artifacts."""

from __future__ import annotations

import re
from typing import Any


SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "token",
    "secret",
    "authorization",
    "credential",
    "credentials",
    "password",
    "endpoint_secret",
    "raw_traceback",
    "traceback",
    "raw_exception",
    "raw_response",
    "provider_raw_response",
}

SENSITIVE_TEXT_PATTERNS = [
    re.compile(r"file://[^\s`'\"，。；,;)]*"),
    re.compile(r"/Users/[^\s`'\"，。；,;)]*"),
    re.compile(r"/private/tmp/[^\s`'\"，。；,;)]*"),
    re.compile(r"/tmp/[^\s`'\"，。；,;)]*"),
    re.compile(r"[A-Za-z]:\\\\[^\s`'\"，。；,;)]*"),
    re.compile(r"(?i)(api[_-]?key|token|secret|authorization)\s*[:=]\s*[A-Za-z0-9._~+/=-]{6,}"),
]


def redact_public_value(value: Any) -> Any:
    if isinstance(value, list):
        return [redact_public_value(item) for item in value]
    if isinstance(value, dict):
        return {
            key: "[redacted]" if _is_sensitive_key(str(key)) else redact_public_value(item)
            for key, item in value.items()
        }
    if isinstance(value, str):
        return redact_public_text(value)
    return value


def redact_public_text(value: str) -> str:
    text = str(value or "")
    for pattern in SENSITIVE_TEXT_PATTERNS:
        text = pattern.sub("[redacted]", text)
    return text


def _is_sensitive_key(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", "_", key.strip().lower()).strip("_")
    return normalized in SENSITIVE_KEYS or any(fragment in normalized for fragment in ("api_key", "token", "secret", "authorization"))
