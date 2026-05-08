"""Compatibility proxy for the external Knowledge Governance Service.

The meeting application no longer owns the knowledge governance runtime.
Its `/api/v1/knowledge/*` routes are kept only as a local compatibility
boundary for the frontend and existing clients; requests are forwarded to
the standalone data_service HTTP API.
"""

from __future__ import annotations

import os
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response

from app.api.v1.auth import api_key_header, verify_api_key


async def verify_knowledge_access(api_key: Optional[str] = Depends(api_key_header)) -> str:
    require_api_key = os.getenv("DATA_SERVICE_REQUIRE_API_KEY", "false").lower() not in {
        "0",
        "false",
        "no",
        "off",
    }
    if require_api_key:
        return await verify_api_key(api_key)
    return "local-dev"


router = APIRouter(
    prefix="/knowledge",
    tags=["Knowledge Governance Proxy"],
    dependencies=[Depends(verify_knowledge_access)],
)


def _upstream_base_url() -> str:
    return os.getenv(
        "DATA_SERVICE_HTTP_BASE_URL",
        "http://127.0.0.1:8003/api/v1/knowledge",
    ).rstrip("/")


def _proxy_timeout() -> float:
    try:
        return float(os.getenv("DATA_SERVICE_PROXY_TIMEOUT", "120"))
    except ValueError:
        return 120.0


def _headers_for_upstream(request: Request) -> dict[str, str]:
    headers: dict[str, str] = {}
    for key in ("accept", "content-type", "authorization", "x-api-key"):
        value = request.headers.get(key)
        if value:
            headers[key] = value

    service_api_key = os.getenv("DATA_SERVICE_API_KEY", "").strip()
    if service_api_key and "x-api-key" not in headers:
        headers["x-api-key"] = service_api_key
    return headers


def _headers_for_downstream(upstream: httpx.Response) -> dict[str, str]:
    excluded = {
        "connection",
        "content-encoding",
        "content-length",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    }
    return {
        key: value
        for key, value in upstream.headers.items()
        if key.lower() not in excluded
    }


async def _proxy(request: Request, path: str = "") -> Response:
    base_url = _upstream_base_url()
    upstream_url = f"{base_url}/{path}" if path else base_url
    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=_proxy_timeout()) as client:
            upstream = await client.request(
                request.method,
                upstream_url,
                params=list(request.query_params.multi_items()),
                content=body if body else None,
                headers=_headers_for_upstream(request),
            )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Knowledge Governance Service is unavailable",
                "upstream": base_url,
                "error": str(exc),
            },
        ) from exc

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=_headers_for_downstream(upstream),
        media_type=upstream.headers.get("content-type"),
    )


@router.api_route("", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_knowledge_root(request: Request) -> Response:
    return await _proxy(request)


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_knowledge_path(path: str, request: Request) -> Response:
    return await _proxy(request, path)
