"""V3.5-B local capability token tests."""

from __future__ import annotations

from core.apps.profiles import AppProfile, build_default_app_registry
from core.protocol.auth import get_method_capability, issue_capability_token, verify_capability_token
from core.protocol.contracts.method_inventory import METHOD_INVENTORY
from core.protocol.schemas.errors import ProtocolError
from core.protocol.schemas.methods import METHOD_SCHEMAS


SECRET = "phase-b-test-secret"


def test_capability_token_sign_verify_and_missing_secret(monkeypatch) -> None:
    profile = build_default_app_registry().get("meeting")
    token = issue_capability_token(app_profile=profile, capabilities=("sessions",), allowed_origins=("http://localhost:5173",), secret=SECRET)
    claims = verify_capability_token(token, secret=SECRET)
    assert claims.app_id == "meeting"
    assert claims.capabilities == ("sessions",)
    assert claims.allowed_origins == ("http://localhost:5173",)

    try:
        verify_capability_token(token, secret="wrong")
    except ProtocolError as exc:
        assert exc.code == "AUTH_INVALID"
        assert exc.data["reason"] == "invalid_signature"
    else:
        raise AssertionError("invalid signature was accepted")

    monkeypatch.delenv("HARNESS_CAPABILITY_TOKEN_SECRET", raising=False)
    try:
        verify_capability_token(token)
    except ProtocolError as exc:
        assert exc.code == "AUTH_INVALID"
        assert exc.data["reason"] == "auth_not_configured"
    else:
        raise AssertionError("missing secret was accepted")

    try:
        issue_capability_token(app_profile=profile)
    except ProtocolError as exc:
        assert exc.code == "AUTH_INVALID"
        assert exc.data["reason"] == "auth_not_configured"
    else:
        raise AssertionError("missing secret was accepted for issue")


def test_capability_token_rejects_expired_and_malformed_tokens() -> None:
    profile = build_default_app_registry().get("meeting")
    expired = issue_capability_token(app_profile=profile, ttl_seconds=-1, secret=SECRET)
    try:
        verify_capability_token(expired, secret=SECRET)
    except ProtocolError as exc:
        assert exc.code == "AUTH_INVALID"
        assert exc.data["reason"] == "expired"
    else:
        raise AssertionError("expired token was accepted")

    try:
        verify_capability_token("not-a-token", secret=SECRET)
    except ProtocolError as exc:
        assert exc.code == "AUTH_INVALID"
        assert exc.data["reason"] == "malformed_token"
    else:
        raise AssertionError("malformed token was accepted")


def test_token_cannot_broaden_app_profile_permissions() -> None:
    profile = AppProfile(
        app_id="demo",
        display_name="Demo",
        domain="demo",
        default_pack="demo",
        allowed_origins=("http://localhost:5173",),
        default_capabilities=("sessions",),
    )
    try:
        issue_capability_token(app_profile=profile, allowed_origins=("http://evil.example",), secret=SECRET)
    except ProtocolError as exc:
        assert exc.code == "AUTH_FORBIDDEN"
        assert exc.data["reason"] == "origin_exceeds_app_profile"
    else:
        raise AssertionError("token broadened profile origins")

    try:
        issue_capability_token(app_profile=profile, capabilities=("sessions", "turns"), secret=SECRET)
    except ProtocolError as exc:
        assert exc.code == "CAPABILITY_DENIED"
        assert exc.data["reason"] == "capability_exceeds_app_profile"
    else:
        raise AssertionError("token broadened profile capabilities")


def test_method_capability_resolver_covers_sdk_default_methods() -> None:
    default_methods = {entry["method"] for entry in METHOD_INVENTORY if entry["surface"] == "default"}
    schema_default = {entry["method"] for entry in METHOD_SCHEMAS if entry["sdk_exposure"] == "default"}
    assert default_methods <= schema_default
    for method in default_methods:
        assert get_method_capability(method), method
    assert get_method_capability("approval.respond") == "approvals"
    assert get_method_capability("connector.health") == "connectors.read"
    assert get_method_capability("pack.list") == "packs.read"
    assert get_method_capability("pack.get") == "packs.read"
