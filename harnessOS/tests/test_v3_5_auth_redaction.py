"""V3.5-B auth secret redaction tests."""

from __future__ import annotations

from apps.api.auth import protocol_error_response
from core.protocol.schemas.errors import ProtocolError


def test_protocol_auth_error_redacts_token_like_data() -> None:
    payload = protocol_error_response(
        ProtocolError(
            "AUTH_INVALID",
            "Invalid token.",
            {
                "authorization": "Bearer secret-token",
                "subscription_token": "secret-subscription",
                "reason": "invalid_signature",
            },
        ),
        request_id="redact",
    )
    text = str(payload)
    assert "secret-token" not in text
    assert "secret-subscription" not in text
    assert payload["error"]["data"]["authorization"] == "[REDACTED]"
    assert payload["error"]["data"]["subscription_token"] == "[REDACTED]"
    assert payload["error"]["data"]["reason"] == "invalid_signature"
