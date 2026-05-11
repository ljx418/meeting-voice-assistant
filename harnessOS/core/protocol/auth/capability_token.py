"""Local HMAC capability tokens for V3.5 external transport auth.

Token issuance helpers are for CLI/local admin/internal tests only. This module
does not expose or imply a public external token issuance API.
"""

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

from core.apps.profiles import AppProfile
from core.protocol.schemas.errors import ProtocolError


TOKEN_AUDIENCE = "harnessos"
TOKEN_ISSUER = "harnessos-local"


@dataclass(frozen=True)
class CapabilityTokenClaims:
    """Verified local capability token claims."""

    token_id: str
    issued_at: str
    expires_at: str
    app_id: str
    project_id: Optional[str]
    workspace_id: Optional[str]
    capabilities: tuple[str, ...]
    allowed_origins: tuple[str, ...]
    embed_policy: dict[str, Any]
    audience: str = TOKEN_AUDIENCE
    issuer: str = TOKEN_ISSUER

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "CapabilityTokenClaims":
        return cls(
            token_id=_require_str(payload, "token_id"),
            issued_at=_require_str(payload, "issued_at"),
            expires_at=_require_str(payload, "expires_at"),
            app_id=_require_str(payload, "app_id"),
            project_id=_optional_str(payload.get("project_id")),
            workspace_id=_optional_str(payload.get("workspace_id")),
            capabilities=tuple(_str_list(payload.get("capabilities"), "capabilities")),
            allowed_origins=tuple(_str_list(payload.get("allowed_origins"), "allowed_origins")),
            embed_policy=dict(payload.get("embed_policy") or {}),
            audience=_require_str(payload, "audience"),
            issuer=_require_str(payload, "issuer"),
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "token_id": self.token_id,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "app_id": self.app_id,
            "project_id": self.project_id,
            "workspace_id": self.workspace_id,
            "capabilities": list(self.capabilities),
            "allowed_origins": list(self.allowed_origins),
            "embed_policy": dict(self.embed_policy),
            "audience": self.audience,
            "issuer": self.issuer,
        }


def issue_capability_token(
    *,
    app_profile: AppProfile,
    project_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    capabilities: Optional[Iterable[str]] = None,
    allowed_origins: Optional[Iterable[str]] = None,
    embed_policy: Optional[dict[str, Any]] = None,
    ttl_seconds: int = 3600,
    secret: Optional[str] = None,
) -> str:
    """Issue a local capability token for CLI/local admin/internal tests only."""
    resolved_secret = _resolve_secret(secret)
    now = datetime.now(timezone.utc)
    requested_origins = tuple(allowed_origins if allowed_origins is not None else app_profile.allowed_origins)
    requested_capabilities = tuple(capabilities if capabilities is not None else app_profile.default_capabilities)
    _ensure_subset(
        requested_origins,
        app_profile.allowed_origins,
        code="AUTH_FORBIDDEN",
        reason="origin_exceeds_app_profile",
    )
    _ensure_subset(
        requested_capabilities,
        app_profile.default_capabilities,
        code="CAPABILITY_DENIED",
        reason="capability_exceeds_app_profile",
    )
    claims = CapabilityTokenClaims(
        token_id=f"cap_{uuid4().hex}",
        issued_at=now.isoformat(),
        expires_at=(now + timedelta(seconds=ttl_seconds)).isoformat(),
        app_id=app_profile.app_id,
        project_id=project_id if project_id is not None else app_profile.default_project_id,
        workspace_id=workspace_id if workspace_id is not None else app_profile.default_workspace_id,
        capabilities=tuple(sorted(set(requested_capabilities))),
        allowed_origins=tuple(sorted(set(requested_origins))),
        embed_policy=dict(embed_policy if embed_policy is not None else app_profile.embed_policy),
    )
    payload = _json(claims.to_payload())
    signature = _sign(payload, resolved_secret)
    return f"{_b64(payload)}.{_b64(signature)}"


def verify_capability_token(token: str, *, secret: Optional[str] = None) -> CapabilityTokenClaims:
    """Verify a local HMAC capability token."""
    resolved_secret = _resolve_secret(secret)
    try:
        payload_part, signature_part = token.split(".", 1)
        payload = _unb64(payload_part)
        signature = _unb64(signature_part)
    except Exception as exc:
        raise ProtocolError("AUTH_INVALID", "Invalid capability token.", {"reason": "malformed_token"}) from exc
    expected = _sign(payload, resolved_secret)
    if not hmac.compare_digest(signature, expected):
        raise ProtocolError("AUTH_INVALID", "Invalid capability token.", {"reason": "invalid_signature"})
    try:
        claims = CapabilityTokenClaims.from_payload(json.loads(payload.decode("utf-8")))
    except Exception as exc:
        raise ProtocolError("AUTH_INVALID", "Invalid capability token.", {"reason": "invalid_payload"}) from exc
    if claims.audience != TOKEN_AUDIENCE or claims.issuer != TOKEN_ISSUER:
        raise ProtocolError("AUTH_INVALID", "Invalid capability token.", {"reason": "invalid_audience"})
    try:
        expires_at = datetime.fromisoformat(claims.expires_at)
    except ValueError as exc:
        raise ProtocolError("AUTH_INVALID", "Invalid capability token.", {"reason": "invalid_expiry"}) from exc
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        raise ProtocolError("AUTH_INVALID", "Capability token expired.", {"reason": "expired"})
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
        raise ValueError("optional string value must be a string")
    return value


def _str_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list")
    if not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{label} entries must be non-empty strings")
    return list(value)


def _ensure_subset(values: Iterable[str], allowed: Iterable[str], *, code: str, reason: str) -> None:
    value_set = set(values)
    allowed_set = set(allowed)
    if not value_set <= allowed_set:
        raise ProtocolError(code, "Capability token exceeds app profile bounds.", {"reason": reason})
