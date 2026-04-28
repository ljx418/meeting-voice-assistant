"""
Health check endpoints for harnessOS API.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Service health status information.
    """
    return {"status": "healthy", "service": "harness-os-api"}