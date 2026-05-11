"""Python SDK value objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

from .errors import ScopeMismatchError


@dataclass(frozen=True)
class Scope:
    """Application scope passed to harnessOS protocol calls."""

    app_id: str = "default"
    project_id: Optional[str] = None
    workspace_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_id": self.app_id,
            "project_id": self.project_id,
            "workspace_id": self.workspace_id,
        }

    @classmethod
    def from_value(cls, value: "Scope | dict[str, Any] | None") -> "Scope | None":
        if value is None:
            return None
        if isinstance(value, Scope):
            return value
        if isinstance(value, dict):
            return cls(
                app_id=str(value.get("app_id") or "default"),
                project_id=_optional_text(value.get("project_id")),
                workspace_id=_optional_text(value.get("workspace_id")),
            )
        raise TypeError("scope must be Scope or dict")

    def ensure_compatible(self, override: "Scope") -> None:
        for field in ("app_id", "project_id", "workspace_id"):
            current = getattr(self, field)
            requested = getattr(override, field)
            if current is not None and requested is not None and current != requested:
                raise ScopeMismatchError(
                    "SCOPE_MISMATCH",
                    f"scope override conflicts with default scope: {field}",
                    {"field": field},
                )


@dataclass(frozen=True)
class CapabilityToken:
    """Opaque capability token accepted by the SDK."""

    value: str

    def __repr__(self) -> str:
        return "CapabilityToken(value='[REDACTED]')"

    __str__ = __repr__


@dataclass(frozen=True)
class EventSubscription:
    """Descriptor returned by events.subscribe."""

    subscription_id: str
    transport: str
    eventsource_url: str
    subscription_token: str
    replay_cursor: str
    expires_at: Optional[str] = None
    allowed_channels: tuple[str, ...] = ()

    @classmethod
    def from_result(cls, result: dict[str, Any], *, base_url: str) -> "EventSubscription":
        raw_url = str(result.get("eventsource_url") or "")
        return cls(
            subscription_id=str(result.get("subscription_id") or ""),
            transport=str(result.get("transport") or "eventsource"),
            eventsource_url=_absolute_url(base_url, raw_url),
            subscription_token=str(result.get("subscription_token") or ""),
            replay_cursor=str(result.get("replay_cursor") or ""),
            expires_at=_optional_text(result.get("expires_at")),
            allowed_channels=tuple(str(item) for item in result.get("allowed_channels") or ()),
        )

    def __repr__(self) -> str:
        return (
            "EventSubscription("
            f"subscription_id={self.subscription_id!r}, "
            f"transport={self.transport!r}, "
            f"eventsource_url={_redacted_url(self.eventsource_url)!r}, "
            "subscription_token='[REDACTED]', "
            f"replay_cursor={self.replay_cursor!r}, "
            f"expires_at={self.expires_at!r}, "
            f"allowed_channels={self.allowed_channels!r})"
        )


def _absolute_url(base_url: str, raw_url: str) -> str:
    parsed = urlsplit(raw_url)
    if parsed.scheme and parsed.netloc:
        return raw_url
    return urljoin(base_url.rstrip("/") + "/", raw_url.lstrip("/"))


def _redacted_url(raw_url: str) -> str:
    parsed = urlsplit(raw_url)
    query = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if "token" in key.lower():
            query.append((key, "[REDACTED]"))
        else:
            query.append((key, value))
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))


def _optional_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
