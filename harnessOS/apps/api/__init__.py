"""
harnessOS API Application.

FastAPI-based API gateway for the harnessOS multi-agent framework.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.gateway.service import GatewayService
from core.config import get_server_config, get_app_config


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup
    config = get_app_config()
    if not hasattr(app.state, "gateway_service"):
        app.state.gateway_service = GatewayService()
    print(f"Starting harnessOS API on {config.server.host}:{config.server.port}")

    yield

    # Shutdown
    print("Shutting down harnessOS API")


def create_app(gateway_service: Optional[GatewayService] = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    config = get_server_config()

    app = FastAPI(
        title="harnessOS API",
        description="""
harnessOS - Multi-functional AI framework based on Deep Agents/LangGraph.

## Features

- **Intent Routing**: Intelligent request routing to specialized agents
- **Meeting Assistant**: Voice meeting transcription and analysis
- **Interview Coach**: Interview preparation and coaching
- **Knowledge Base**: Graph-based knowledge management
- **Video Production**: Media orchestration and rendering

## Architecture

Built on Deep Agents/LangGraph with modular agent system.
        """,
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    if gateway_service is not None:
        app.state.gateway_service = gateway_service

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    from apps.api.routers import bff, bff_v41, bff_v42, bff_v43, bff_v44, bff_v45, bff_v46, health, agents, events, routing, runs

    app.include_router(health.router, tags=["health"])
    app.include_router(bff.router, prefix="/bff", tags=["bff"])
    app.include_router(bff_v41.router, prefix="/bff/v4_1", tags=["bff-v4.1"])
    app.include_router(bff_v42.router, prefix="/bff/v4_2", tags=["bff-v4.2"])
    app.include_router(bff_v43.router, prefix="/bff/v4_3", tags=["bff-v4.3"])
    app.include_router(bff_v44.router, prefix="/bff/v4_4", tags=["bff-v4.4"])
    app.include_router(bff_v45.router, prefix="/bff/v4_5", tags=["bff-v4.5"])
    app.include_router(bff_v46.router, prefix="/bff/v4_6", tags=["bff-v4.6"])
    app.include_router(runs.router, prefix="/v1", tags=["runs"])
    app.include_router(events.router, prefix="/v1", tags=["events"])
    app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
    app.include_router(routing.router, prefix="/api/routing", tags=["routing"])

    return app


# Create app instance
app = create_app()
