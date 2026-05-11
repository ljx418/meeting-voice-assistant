"""Platform-neutral Minimal FastAPI BFF Smoke for V3.5-D2."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

from harnessos_client import HarnessOSClient, MethodForbiddenError, Scope, ScopeMismatchError

from .denylist import BffForbiddenError, assert_allowed_rpc
from .event_proxy import open_upstream_eventsource, proxy_sse_frames
from .scope_binding import identity_from_headers, resolve_request_scope, scope_error


DEFAULT_CONFIG = {
    "harnessos_base_url": "http://127.0.0.1:8000",
    "harnessos_capability_token_env": "HARNESSOS_BFF_CAPABILITY_TOKEN",
    "identity_scope": {
        "app_id": "reference_app",
        "project_id": "demo",
        "workspace_id": "local",
    },
    "allowed_origins": ["http://localhost:5173"],
}


def create_app(
    *,
    config: Optional[dict[str, Any]] = None,
    sdk_client: Optional[Any] = None,
    upstream_opener: Optional[Callable[[str], Any]] = None,
) -> FastAPI:
    """Create the Minimal BFF Smoke app."""
    resolved_config = {**DEFAULT_CONFIG, **(config or {})}
    identity_scope = Scope.from_value(resolved_config["identity_scope"]) or Scope(app_id="reference_app")
    client = sdk_client or _default_client(resolved_config, identity_scope)
    open_events = upstream_opener or open_upstream_eventsource

    app = FastAPI(title="harnessOS Minimal BFF Smoke")

    @app.get("/bff/health")
    async def health() -> dict[str, Any]:
        return {"status": "ok", "app_id": identity_scope.app_id}

    @app.post("/bff/session/start")
    async def session_start(request: Request) -> Any:
        payload, scope_or_error = await _payload_and_scope(request, identity_scope)
        if isinstance(scope_or_error, JSONResponse):
            return scope_or_error
        return _call(lambda: client.session_start(model=payload.get("model"), scope=scope_or_error))

    @app.post("/bff/turn/start")
    async def turn_start(request: Request) -> Any:
        payload, scope_or_error = await _payload_and_scope(request, identity_scope)
        if isinstance(scope_or_error, JSONResponse):
            return scope_or_error
        return _call(
            lambda: client.turn_start(
                input=str(payload.get("input") or ""),
                session_id=payload.get("session_id"),
                domain=payload.get("domain"),
                scope=scope_or_error,
            )
        )

    @app.post("/bff/approval/respond")
    async def approval_respond(request: Request) -> Any:
        payload, scope_or_error = await _payload_and_scope(request, identity_scope)
        if isinstance(scope_or_error, JSONResponse):
            return scope_or_error
        return _call(
            lambda: client.approval_respond(
                approval_id=str(payload.get("approval_id") or ""),
                decision=str(payload.get("decision") or ""),
                reason=payload.get("reason"),
                scope=scope_or_error,
            )
        )

    @app.post("/bff/rpc")
    async def constrained_rpc(request: Request) -> Any:
        payload, scope_or_error = await _payload_and_scope(request, identity_scope)
        if isinstance(scope_or_error, JSONResponse):
            return scope_or_error
        method = str(payload.get("method") or "")
        params = dict(payload.get("params") or {})
        try:
            assert_allowed_rpc(method, params)
        except BffForbiddenError as exc:
            return _error("METHOD_FORBIDDEN", str(exc), status_code=403)
        params.setdefault("scope", scope_or_error.to_dict())
        return _call(lambda: client.rpc(method, params))

    @app.get("/bff/events/subscribe")
    async def events_subscribe(request: Request) -> Any:
        try:
            identity = identity_from_headers(request.headers, default_scope=identity_scope)
            scope = resolve_request_scope(
                identity_scope=identity.scope,
                route_scope=_query_scope(request),
                body_scope=None,
            )
        except ScopeMismatchError as exc:
            return JSONResponse(status_code=403, content=scope_error(str(exc)))
        channels = _channels(request.query_params.get("channels"))
        try:
            subscription = client.events_subscribe(channels=channels, scope=scope)
        except Exception as exc:
            return _exception_to_response(exc)
        try:
            upstream = open_events(subscription.eventsource_url)
        except Exception as exc:
            return _error("RUNTIME_ERROR", _redact(str(exc)), status_code=502)
        response = StreamingResponse(proxy_sse_frames(upstream), media_type="text/event-stream")
        response.headers["Cache-Control"] = "no-cache"
        return response

    return app


def load_config(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _default_client(config: dict[str, Any], scope: Scope) -> HarnessOSClient:
    token_env = str(config.get("harnessos_capability_token_env") or "HARNESSOS_BFF_CAPABILITY_TOKEN")
    token = os.getenv(token_env)
    return HarnessOSClient(
        base_url=str(config.get("harnessos_base_url") or "http://127.0.0.1:8000"),
        capability_token=token,
        scope=scope,
    )


async def _payload_and_scope(request: Request, identity_scope: Scope) -> tuple[dict[str, Any], Scope | JSONResponse]:
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    try:
        identity = identity_from_headers(request.headers, default_scope=identity_scope)
        scope = resolve_request_scope(
            identity_scope=identity.scope,
            route_scope=_query_scope(request),
            body_scope=payload.get("scope"),
        )
    except ScopeMismatchError as exc:
        return payload, JSONResponse(status_code=403, content=scope_error(str(exc)))
    if payload.get("scope_mode") == "all":
        return payload, _error("METHOD_FORBIDDEN", "scope_mode=all is not allowed through the BFF.", status_code=403)
    return payload, scope


def _query_scope(request: Request) -> dict[str, Any]:
    return {
        key: value
        for key, value in {
            "app_id": request.query_params.get("app_id"),
            "project_id": request.query_params.get("project_id"),
            "workspace_id": request.query_params.get("workspace_id"),
        }.items()
        if value is not None
    }


def _channels(value: Optional[str]) -> list[str] | None:
    if not value:
        return None
    return [part.strip() for part in value.split(",") if part.strip()]


def _call(fn: Callable[[], dict[str, Any]]) -> Any:
    try:
        return fn()
    except Exception as exc:
        return _exception_to_response(exc)


def _exception_to_response(exc: Exception) -> JSONResponse:
    code = getattr(exc, "code", "RUNTIME_ERROR")
    data = getattr(exc, "data", {})
    return _error(str(code), _redact(str(exc)), data=data if isinstance(data, dict) else {}, status_code=_status(str(code)))


def _error(code: str, message: str, *, data: Optional[dict[str, Any]] = None, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": _redact(message), "data": _redact_data(data or {})}},
    )


def _status(code: str) -> int:
    if code in {"AUTH_REQUIRED", "AUTH_INVALID"}:
        return 401
    if code in {"AUTH_FORBIDDEN", "CAPABILITY_DENIED", "METHOD_FORBIDDEN", "SCOPE_MISMATCH"}:
        return 403
    if code.endswith("_NOT_FOUND"):
        return 404
    return 400


def _redact_data(data: dict[str, Any]) -> dict[str, Any]:
    return {key: ("[REDACTED]" if "token" in str(key).lower() else _redact(value) if isinstance(value, str) else value) for key, value in data.items()}


def _redact(value: str) -> str:
    cleaned = value.replace("Authorization", "[REDACTED]")
    if "subscription_token=" in cleaned:
        cleaned = cleaned.split("subscription_token=", 1)[0] + "subscription_token=[REDACTED]"
    parts = []
    redact_next = False
    for part in cleaned.split():
        if redact_next:
            parts.append("[REDACTED]")
            redact_next = False
            continue
        if part.lower() == "bearer":
            parts.append(part)
            redact_next = True
            continue
        parts.append("[REDACTED]" if len(part) > 48 and "." in part else part)
    return " ".join(parts)


app = create_app()
