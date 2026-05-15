"""Short-lived EventSource subscription tokens for V3.5 Event Bridge."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Optional
from uuid import uuid4

from core.apps.scope import ScopeContext
from core.protocol.schemas.errors import ProtocolError


TOKEN_AUDIENCE = "harnessos-events"
TOKEN_ISSUER = "harnessos-local"


@dataclass(frozen=True)
class SubscriptionTokenClaims:
    """Verified short-lived event subscription claims."""

    subscription_id: str
    issued_at: str
    expires_at: str
    app_id: str
    project_id: Optional[str]
    workspace_id: Optional[str]
    channels: tuple[str, ...]
    capabilities: tuple[str, ...]
    allowed_origins: tuple[str, ...] = ()
    audience: str = TOKEN_AUDIENCE
    issuer: str = TOKEN_ISSUER

    @property
    def scope(self) -> ScopeContext:
        return ScopeContext(app_id=self.app_id, project_id=self.project_id, workspace_id=self.workspace_id)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "SubscriptionTokenClaims":
        return cls(
            subscription_id=_require_str(payload, "subscription_id"),
            issued_at=_require_str(payload, "issued_at"),
            expires_at=_require_str(payload, "expires_at"),
            app_id=_require_str(payload, "app_id"),
            project_id=_optional_str(payload.get("project_id")),
            workspace_id=_optional_str(payload.get("workspace_id")),
            channels=tuple(_str_list(payload.get("channels"), "channels")),
            capabilities=tuple(_str_list(payload.get("capabilities"), "capabilities")),
            allowed_origins=tuple(_str_list(payload.get("allowed_origins") or [], "allowed_origins")),
            audience=_require_str(payload, "audience"),
            issuer=_require_str(payload, "issuer"),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "subscription_id": self.subscription_id,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "app_id": self.app_id,
            "project_id": self.project_id,
            "workspace_id": self.workspace_id,
            "channels": list(self.channels),
            "capabilities": list(self.capabilities),
            "allowed_origins": list(self.allowed_origins),
            "audience": self.audience,
            "issuer": self.issuer,
        }


def issue_subscription_token(
    *,
    scope: ScopeContext,
    channels: Iterable[str],
    capabilities: Iterable[str],
    allowed_origins: Iterable[str] = (),
    ttl_seconds: int = 300,
    secret: Optional[str] = None,
) -> tuple[str, SubscriptionTokenClaims]:
    """Issue a short-lived subscription token derived from an existing auth context."""
    resolved_secret = _resolve_secret(secret)
    now = datetime.now(timezone.utc)
    claims = SubscriptionTokenClaims(
        subscription_id=f"sub_{uuid4().hex}",
        issued_at=now.isoformat(),
        expires_at=(now + timedelta(seconds=ttl_seconds)).isoformat(),
        app_id=scope.app_id,
        project_id=scope.project_id,
        workspace_id=scope.workspace_id,
        channels=tuple(sorted(set(channels))),
        capabilities=tuple(sorted(set(capabilities))),
        allowed_origins=tuple(sorted(set(allowed_origins))),
    )
    payload = _json(claims.to_payload())
    signature = _sign(payload, resolved_secret)
    return f"{_b64(payload)}.{_b64(signature)}", claims


def verify_subscription_token(token: str, *, secret: Optional[str] = None) -> SubscriptionTokenClaims:
    """Verify a short-lived event subscription token."""
    resolved_secret = _resolve_secret(secret)
    try:
        payload_part, signature_part = token.split(".", 1)
        payload = _unb64(payload_part)
        signature = _unb64(signature_part)
    except Exception as exc:
        raise ProtocolError("SUBSCRIPTION_TOKEN_INVALID", "Invalid subscription token.", {"reason": "malformed_token"}) from exc
    expected = _sign(payload, resolved_secret)
    if not hmac.compare_digest(signature, expected):
        raise ProtocolError("SUBSCRIPTION_TOKEN_INVALID", "Invalid subscription token.", {"reason": "invalid_signature"}) from None
    try:
        claims = SubscriptionTokenClaims.from_payload(json.loads(payload.decode("utf-8")))
    except Exception as exc:
        raise ProtocolError("SUBSCRIPTION_TOKEN_INVALID", "Invalid subscription token.", {"reason": "invalid_payload"}) from exc
    if claims.audience != TOKEN_AUDIENCE or claims.issuer != TOKEN_ISSUER:
        raise ProtocolError("SUBSCRIPTION_TOKEN_INVALID", "Invalid subscription token.", {"reason": "invalid_audience"})
    try:
        expires_at = datetime.fromisoformat(claims.expires_at)
    except ValueError as exc:
        raise ProtocolError("SUBSCRIPTION_TOKEN_INVALID", "Invalid subscription token.", {"reason": "invalid_expiry"}) from exc
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        raise ProtocolError("SUBSCRIPTION_TOKEN_EXPIRED", "Subscription token expired.", {"reason": "expired"})
    return claims


def _resolve_secret(secret: Optional[str]) -> bytes:
    value = secret if secret is not None else os.getenv("HARNESS_CAPABILITY_TOKEN_SECRET")
    if not value:
        raise ProtocolError("AUTH_INVALID", "Capability token secret is not configured.", {"reason": "auth_not_configured"})
    return value.encode("utf-8")


def _json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sign(payload: bytes, secret: bytes) -> bytes:
    return hmac.new(secret, payload, hashlib.sha256).digest()


def _b64(payload: bytes) -> str:
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def _unb64(payload: str) -> bytes:
    return base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))


def _require_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} is required")
    return value


def _optional_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("optional value must be a string")
    return value


def _str_list(value: Any, key: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{key} must be a string list")
    return value
