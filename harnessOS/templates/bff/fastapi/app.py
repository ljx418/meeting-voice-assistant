"""Copyable FastAPI BFF template for V3.5-F."""

from __future__ import annotations

from typing import Any, Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from .capability_policy import CapabilityPolicy
from .errors import BffError, ErrorSanitizer
from .event_proxy import open_upstream_eventsource, proxy_sse_frames, upstream_eventsource_url
from .harnessos import create_harnessos_client
from .identity import DemoIdentityProvider, Identity
from .rpc_proxy import assert_rpc_allowed
from .scope_binding import ScopeResolver, query_scope
from .settings import BffSettings, load_settings

DEFAULT_EMBED_ACTIONS = [
    "session.start",
    "turn.start",
    "events.subscribe",
    "approval.respond",
    "artifact.read_metadata",
    "artifact.lineage",
    "job.get",
    "pack.get",
    "connector.health",
]
DEFAULT_EMBED_CHANNELS = ["chat", "job", "artifact", "approval"]


def create_app(
    *,
    config: dict[str, Any] | None = None,
    sdk_client: Any | None = None,
    upstream_opener: Callable[[str], Any] | None = None,
    settings: BffSettings | None = None,
) -> FastAPI:
    """Create a copyable BFF app.

    Pass `sdk_client` and `upstream_opener` in tests. In real usage, the app
    creates a harnessOS Python SDK client from server-side configuration.
    """
    resolved_settings = settings or load_settings(config)
    sanitizer = ErrorSanitizer()
    identity_provider = DemoIdentityProvider(default_scope=resolved_settings.identity_scope, capabilities=resolved_settings.demo_capabilities)
    scope_resolver = ScopeResolver()
    capability_policy = CapabilityPolicy()
    open_events = upstream_opener or open_upstream_eventsource

    app = FastAPI(title="harnessOS Full BFF Template")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(resolved_settings.allowed_origins),
        allow_credentials=resolved_settings.allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def demo_warning_header(request: Request, call_next: Callable[[Request], Any]) -> Any:
        response = await call_next(request)
        if resolved_settings.warning_header:
            response.headers["X-HarnessOS-BFF-Warning"] = resolved_settings.warning_header
        return response

    @app.get("/bff/health")
    async def health() -> dict[str, Any]:
        return {
            "status": "ok" if not resolved_settings.config_error else "degraded",
            "app_id": resolved_settings.identity_scope.app_id,
            "config_error": bool(resolved_settings.config_error),
        }

    @app.post("/bff/rpc")
    async def rpc_proxy(request: Request) -> Any:
        try:
            payload, identity, scope = await _context(request, resolved_settings, identity_provider, scope_resolver)
            method = str(payload.get("method") or "")
            params = dict(payload.get("params") or {})
            assert_rpc_allowed(method, params, identity=identity, capability_policy=capability_policy)
            params.setdefault("scope", scope.to_dict())
            return _call(lambda: _client(resolved_settings, scope, sdk_client).rpc(method, params), sanitizer)
        except Exception as exc:
            return sanitizer.response(exc)

    @app.post("/bff/sessions")
    async def sessions(request: Request) -> Any:
        return await _structured(request, resolved_settings, identity_provider, scope_resolver, capability_policy, sdk_client, sanitizer, "session.start")

    @app.post("/bff/turns")
    async def turns(request: Request) -> Any:
        return await _structured(request, resolved_settings, identity_provider, scope_resolver, capability_policy, sdk_client, sanitizer, "turn.start")

    @app.get("/bff/artifacts")
    async def artifact_list(request: Request) -> Any:
        return await _structured(request, resolved_settings, identity_provider, scope_resolver, capability_policy, sdk_client, sanitizer, "artifact.list")

    @app.post("/bff/artifacts/external")
    async def artifact_register_external(request: Request) -> Any:
        return await _structured(request, resolved_settings, identity_provider, scope_resolver, capability_policy, sdk_client, sanitizer, "artifact.register_external")

    @app.get("/bff/artifacts/{artifact_id}/metadata")
    async def artifact_metadata(artifact_id: str, request: Request) -> Any:
        return await _structured(
            request,
            resolved_settings,
            identity_provider,
            scope_resolver,
            capability_policy,
            sdk_client,
            sanitizer,
            "artifact.read_metadata",
            path_params={"artifact_id": artifact_id},
        )

    @app.get("/bff/artifacts/{artifact_id}/lineage")
    async def artifact_lineage(artifact_id: str, request: Request) -> Any:
        return await _structured(
            request,
            resolved_settings,
            identity_provider,
            scope_resolver,
            capability_policy,
            sdk_client,
            sanitizer,
            "artifact.lineage",
            path_params={"artifact_id": artifact_id},
        )

    @app.get("/bff/jobs")
    async def job_list(request: Request) -> Any:
        return await _structured(request, resolved_settings, identity_provider, scope_resolver, capability_policy, sdk_client, sanitizer, "job.list")

    @app.get("/bff/jobs/{job_id}")
    async def job_get(job_id: str, request: Request) -> Any:
        return await _structured(
            request,
            resolved_settings,
            identity_provider,
            scope_resolver,
            capability_policy,
            sdk_client,
            sanitizer,
            "job.get",
            path_params={"job_id": job_id},
        )

    @app.post("/bff/approvals/{approval_id}/respond")
    async def approval_respond(approval_id: str, request: Request) -> Any:
        return await _structured(
            request,
            resolved_settings,
            identity_provider,
            scope_resolver,
            capability_policy,
            sdk_client,
            sanitizer,
            "approval.respond",
            path_params={"approval_id": approval_id},
        )

    @app.get("/bff/packs")
    async def pack_list(request: Request) -> Any:
        return await _structured(request, resolved_settings, identity_provider, scope_resolver, capability_policy, sdk_client, sanitizer, "pack.list")

    @app.get("/bff/packs/{pack_id}")
    async def pack_get(pack_id: str, request: Request) -> Any:
        return await _structured(
            request,
            resolved_settings,
            identity_provider,
            scope_resolver,
            capability_policy,
            sdk_client,
            sanitizer,
            "pack.get",
            path_params={"pack_id": pack_id},
        )

    @app.get("/bff/connectors/{connector_id}/health")
    async def connector_health(connector_id: str, request: Request) -> Any:
        return await _structured(
            request,
            resolved_settings,
            identity_provider,
            scope_resolver,
            capability_policy,
            sdk_client,
            sanitizer,
            "connector.health",
            path_params={"connector_id": connector_id},
        )

    @app.get("/bff/embed/bootstrap")
    async def embed_bootstrap(request: Request) -> Any:
        try:
            _require_configured(resolved_settings)
            identity = identity_provider.resolve(request.headers)
            route_scope = query_scope(request.query_params)
            scope = scope_resolver.resolve(identity=identity, route_scope=route_scope)
            requested_channels = _channels(request.query_params.get("channels")) or list(DEFAULT_EMBED_CHANNELS)
            channels = _embed_channels(identity, requested_channels)
            for action in ("events.subscribe",):
                capability_policy.require(identity, action)
            session = None
            if request.query_params.get("create_session") == "true":
                capability_policy.require(identity, "session.start")
                session = _client(resolved_settings, scope, sdk_client).session_start(scope=scope)
            subscription = _client(resolved_settings, scope, sdk_client).events_subscribe(channels=channels, scope=scope)
            return {
                "embedDefinition": {
                    "schemaVersion": "1",
                    "embedId": str(request.query_params.get("embed_id") or "reference_app_embed"),
                    "appId": scope.app_id,
                    "defaultProjectId": scope.project_id,
                    "defaultWorkspaceId": scope.workspace_id,
                    "capabilityMode": "bff",
                    "transportMode": "bff_proxy",
                    "allowedEventChannels": channels,
                    "allowedActions": _allowed_embed_actions(identity, capability_policy),
                    "initialView": str(request.query_params.get("initial_view") or "chat"),
                    "artifactPreviewPolicy": {"mode": "metadata_only"},
                    "approvalPolicy": {"method": "approval.respond"},
                    "tracePolicy": {"enabled": "trace" in channels},
                    "theme": {},
                    "metadata": {"template": "fastapi"},
                },
                "session": session,
                "thread": None,
                "eventSubscription": {
                    "eventsourceUrl": _bff_eventsource_url(channels, subscription.replay_cursor),
                    "replayCursor": subscription.replay_cursor,
                    "allowedChannels": channels,
                    "expiresAt": subscription.expires_at,
                },
            }
        except Exception as exc:
            return sanitizer.response(exc)

    @app.get("/bff/events/subscribe")
    async def events_subscribe(request: Request) -> Any:
        try:
            _require_configured(resolved_settings)
            identity = identity_provider.resolve(request.headers)
            capability_policy.require(identity, "events.subscribe")
            scope = scope_resolver.resolve(identity=identity, route_scope=query_scope(request.query_params))
            channels = _channels(request.query_params.get("channels"))
            subscription = _client(resolved_settings, scope, sdk_client).events_subscribe(channels=channels, scope=scope)
            upstream_url = upstream_eventsource_url(
                subscription.eventsource_url,
                last_event_id=request.headers.get("last-event-id"),
                cursor=request.query_params.get("cursor"),
            )
            upstream = open_events(upstream_url)
            response = StreamingResponse(proxy_sse_frames(upstream), media_type="text/event-stream")
            response.headers["Cache-Control"] = "no-cache"
            return response
        except Exception as exc:
            return sanitizer.response(exc)

    return app


async def _structured(
    request: Request,
    settings: BffSettings,
    identity_provider: DemoIdentityProvider,
    scope_resolver: ScopeResolver,
    capability_policy: CapabilityPolicy,
    sdk_client: Any | None,
    sanitizer: ErrorSanitizer,
    method: str,
    *,
    path_params: dict[str, Any] | None = None,
) -> Any:
    try:
        payload, identity, scope = await _context(request, settings, identity_provider, scope_resolver)
        capability_policy.require(identity, method)
        params = _method_params(method, {**payload, **(path_params or {})}, request)
        params["scope"] = scope.to_dict()
        return _call(lambda: _invoke(_client(settings, scope, sdk_client), method, params), sanitizer)
    except Exception as exc:
        return sanitizer.response(exc)


async def _context(
    request: Request,
    settings: BffSettings,
    identity_provider: DemoIdentityProvider,
    scope_resolver: ScopeResolver,
) -> tuple[dict[str, Any], Identity, Any]:
    _require_configured(settings)
    payload = await _payload(request)
    identity = identity_provider.resolve(request.headers)
    scope = scope_resolver.resolve(
        identity=identity,
        route_scope=query_scope(request.query_params),
        body_scope=payload.get("scope"),
        scope_mode=payload.get("scope_mode") or request.query_params.get("scope_mode"),
    )
    return payload, identity, scope


def _require_configured(settings: BffSettings) -> None:
    if settings.config_error:
        raise BffError("AUTH_NOT_CONFIGURED", settings.config_error, status_code=401)


def _client(settings: BffSettings, scope: Any, sdk_client: Any | None) -> Any:
    return sdk_client or create_harnessos_client(settings, scope)


async def _payload(request: Request) -> dict[str, Any]:
    if request.method.upper() == "GET":
        return {}
    try:
        data = await request.json()
    except Exception:
        data = {}
    return data if isinstance(data, dict) else {}


def _call(fn: Callable[[], dict[str, Any]], sanitizer: ErrorSanitizer) -> Any:
    try:
        return fn()
    except Exception as exc:
        return sanitizer.response(exc)


def _invoke(client: Any, method: str, params: dict[str, Any]) -> dict[str, Any]:
    if method == "session.start":
        return client.session_start(model=params.get("model"), scope=params["scope"])
    if method == "turn.start":
        return client.turn_start(input=str(params.get("input") or ""), session_id=params.get("session_id"), domain=params.get("domain"), scope=params["scope"])
    if method == "artifact.list":
        return client.artifact_list(session_id=params.get("session_id"), kind=params.get("kind"), scope=params["scope"])
    if method == "artifact.register_external":
        return client.artifact_register_external(kind=str(params.get("kind") or ""), external_asset_uri=str(params.get("external_asset_uri") or ""), scope=params["scope"])
    if method == "artifact.read_metadata":
        return client.artifact_read_metadata(artifact_id=str(params.get("artifact_id") or ""), scope=params["scope"])
    if method == "artifact.lineage":
        return client.artifact_lineage(artifact_id=params.get("artifact_id"), session_id=params.get("session_id"), scope=params["scope"])
    if method == "job.list":
        return client.job_list(session_id=params.get("session_id"), status=params.get("status"), scope=params["scope"])
    if method == "job.get":
        return client.job_get(job_id=str(params.get("job_id") or ""), scope=params["scope"])
    if method == "approval.respond":
        return client.approval_respond(approval_id=str(params.get("approval_id") or ""), decision=str(params.get("decision") or ""), reason=params.get("reason"), scope=params["scope"])
    if method == "pack.list":
        return client.pack_list()
    if method == "pack.get":
        return client.pack_get(app_id=params.get("app_id"), pack_id=params.get("pack_id"))
    if method == "connector.health":
        return client.connector_health(connector_id=str(params.get("connector_id") or ""))
    return client.rpc(method, params)


def _method_params(method: str, payload: dict[str, Any], request: Request) -> dict[str, Any]:
    params = dict(payload)
    if method in {"artifact.list", "artifact.lineage", "job.list", "pack.get"}:
        for key in ("session_id", "kind", "status", "app_id"):
            if request.query_params.get(key) is not None:
                params[key] = request.query_params.get(key)
    return params


def _channels(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [part.strip() for part in value.split(",") if part.strip()]


def _embed_channels(identity: Identity, requested: list[str]) -> list[str]:
    allowed = []
    for channel in requested:
        if channel == "trace" and not ({"traces.read", "debug"} & set(identity.capabilities)):
            raise BffError("CAPABILITY_DENIED", "Trace channel requires traces.read/debug capability.", status_code=403)
        if channel not in {"chat", "job", "artifact", "approval", "trace", "business"}:
            raise BffError("INVALID_PARAMS", f"Unsupported embed event channel: {channel}", status_code=400)
        allowed.append(channel)
    return allowed


def _allowed_embed_actions(identity: Identity, capability_policy: CapabilityPolicy) -> list[str]:
    allowed: list[str] = []
    for action in DEFAULT_EMBED_ACTIONS:
        try:
            capability_policy.require(identity, action)
        except BffError:
            continue
        allowed.append(action)
    return allowed


def _bff_eventsource_url(channels: list[str], replay_cursor: str | None) -> str:
    query = f"channels={','.join(channels)}"
    if replay_cursor:
        query = f"{query}&cursor={replay_cursor}"
    return f"/bff/events/subscribe?{query}"


app = create_app()
