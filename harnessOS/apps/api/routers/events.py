"""Browser-friendly V3.5 Event Bridge endpoints."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from apps.api.auth import add_dev_warning, authorize_http_request, http_error_response
from apps.api.dependencies import get_gateway_service
from apps.gateway.service import GatewayService
from core.apps.scope import ScopeContext
from core.protocol.auth import verify_subscription_token
from core.protocol.event_bridge import (
    collect_event_envelopes,
    ensure_channel_capabilities,
    heartbeat_frame,
    normalize_event_channels,
    read_event_cursor,
    sse_frame,
)
from core.protocol.schemas.errors import ProtocolError

router = APIRouter()

SENSITIVE_KEY_PARTS = (
    "token",
    "authorization",
    "secret",
    "raw_trace_payload",
    "raw_artifact_content",
    "raw_connector_payload",
)


@router.get("/events/subscribe")
async def subscribe_events(
    request: Request,
    gateway: GatewayService = Depends(get_gateway_service),
) -> Any:
    """Subscribe to replayable local events through SSE."""
    params = dict(request.query_params)
    try:
        channels = normalize_event_channels(params.get("channels"))
        auth = None
        subscription_token = params.get("subscription_token")
        if subscription_token:
            claims = verify_subscription_token(subscription_token)
            origin = request.headers.get("origin")
            if origin and claims.allowed_origins and origin not in set(claims.allowed_origins):
                raise ProtocolError(
                    "AUTH_FORBIDDEN",
                    "Origin is not allowed for this event subscription.",
                    {"reason": "subscription_origin_mismatch"},
                )
            requested_scope = _scope_from_params(params)
            if requested_scope is not None and requested_scope != claims.scope:
                raise ProtocolError(
                    "SUBSCRIPTION_TOKEN_SCOPE_MISMATCH",
                    "Subscription token scope does not match the request.",
                    {"reason": "subscription_scope_mismatch"},
                )
            denied = sorted(set(channels) - set(claims.channels))
            if denied:
                raise ProtocolError(
                    "SUBSCRIPTION_TOKEN_CHANNEL_DENIED",
                    "Subscription token cannot access the requested channel.",
                    {"channels": denied},
                )
            scope = claims.scope
            capabilities = claims.capabilities
        else:
            auth_params = dict(params)
            auth = await authorize_http_request(request, gateway=gateway, params=auth_params, capability="events")
            scope = auth.scope
            capabilities = tuple(auth_params.get("_auth_capabilities") or ())
        ensure_channel_capabilities(channels, capabilities)
        cursor = request.headers.get("last-event-id") or params.get("cursor") or params.get("last_event_id")
        start_sequence = read_event_cursor(cursor, scope)
    except ProtocolError as exc:
        return http_error_response(exc)

    filters = {
        key: params.get(key)
        for key in ("session_id", "turn_id", "job_id", "artifact_id", "approval_id", "trace_id", "workflow_instance_id", "workflow_patch_id")
        if params.get(key)
    }
    follow = _truthy(params.get("follow"))
    heartbeat_interval = _float_param(params.get("heartbeat_interval"), default=15.0)
    max_heartbeats = _int_param(params.get("max_heartbeats"))

    async def event_source():
        last_sequence = start_sequence
        sent_keys: set[tuple[str, str]] = set()
        events, last_sequence = _collect_unsent_events(
            gateway,
            scope=scope,
            channels=channels,
            filters=filters,
            last_sequence=last_sequence,
            sent_keys=sent_keys,
        )
        for event in events:
            yield sse_frame(_redact(event))
        if not follow:
            return
        sent_heartbeats = 0
        while True:
            await asyncio.sleep(max(heartbeat_interval, 0.01))
            events, last_sequence = _collect_unsent_events(
                gateway,
                scope=scope,
                channels=channels,
                filters=filters,
                last_sequence=last_sequence,
                sent_keys=sent_keys,
            )
            if events:
                for event in events:
                    yield sse_frame(_redact(event))
                continue
            yield heartbeat_frame()
            sent_heartbeats += 1
            if max_heartbeats is not None and sent_heartbeats >= max_heartbeats:
                return

    response = StreamingResponse(event_source(), media_type="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    if auth is not None:
        add_dev_warning(response, auth)
    return response


def _collect_unsent_events(
    gateway: GatewayService,
    *,
    scope: ScopeContext,
    channels: list[str],
    filters: dict[str, Any],
    last_sequence: int,
    sent_keys: set[tuple[str, str]],
) -> tuple[list[dict[str, Any]], int]:
    """Return replay/follow events newer than the last emitted cursor."""
    events: list[dict[str, Any]] = []
    current_sequence = last_sequence
    for event in collect_event_envelopes(gateway, scope=scope, channels=channels, filters=filters):
        sequence = read_event_cursor(event["cursor"], scope)
        key = (str(event.get("channel") or ""), str(event.get("event_id") or ""))
        if sequence > current_sequence and key not in sent_keys:
            events.append(event)
            current_sequence = max(current_sequence, sequence)
            sent_keys.add(key)
    return events, current_sequence


def _scope_from_params(params: dict[str, Any]) -> ScopeContext | None:
    raw_scope = params.get("scope")
    has_top_level = any(key in params for key in ("app_id", "project_id", "workspace_id"))
    if raw_scope is None and not has_top_level:
        return None
    scope = raw_scope if isinstance(raw_scope, dict) else {}
    return ScopeContext(
        app_id=str(scope.get("app_id") or params.get("app_id") or "default"),
        project_id=_optional_text(scope.get("project_id") or params.get("project_id")),
        workspace_id=_optional_text(scope.get("workspace_id") or params.get("workspace_id")),
    )


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).strip() or None


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            lower = str(key).lower()
            if any(part in lower for part in SENSITIVE_KEY_PARTS):
                continue
            redacted[key] = _redact(item)
        return redacted
    if isinstance(value, list):
        return [_redact(item) for item in value]
    if isinstance(value, str) and ("Bearer " in value or "subscription_token" in value or "capability_token" in value):
        return "[redacted]"
    return value


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _float_param(value: Any, *, default: float) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ProtocolError("INVALID_PARAMS", "heartbeat_interval must be numeric.", {"field": "heartbeat_interval"}) from exc


def _int_param(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ProtocolError("INVALID_PARAMS", "max_heartbeats must be an integer.", {"field": "max_heartbeats"}) from exc
