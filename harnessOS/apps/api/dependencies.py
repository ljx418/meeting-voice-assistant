"""FastAPI dependencies for shared application services."""

from __future__ import annotations

from fastapi import Request

from apps.gateway.service import GatewayService


def get_gateway_service(request: Request) -> GatewayService:
    """Return the app-scoped GatewayService."""
    service = getattr(request.app.state, "gateway_service", None)
    if not isinstance(service, GatewayService):
        service = GatewayService()
        request.app.state.gateway_service = service
    return service
