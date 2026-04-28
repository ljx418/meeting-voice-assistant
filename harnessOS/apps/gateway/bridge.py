"""Small bridge helpers for harnessOS gateway clients."""

from __future__ import annotations

from typing import AsyncIterator

from apps.gateway.protocol import GatewayEvent
from apps.gateway.service import GatewayService


async def run_prompt_stream(
    service: GatewayService,
    prompt: str,
    *,
    model: str | None = None,
    domain: str | None = None,
) -> AsyncIterator[GatewayEvent]:
    """Create a temporary session and stream one prompt through it."""
    session = await service.session_start({"model": model} if model else {})
    session_id = str(session["session_id"])
    try:
        async for event in service.turn_stream(
            {
                "session_id": session_id,
                "input": prompt,
                "domain": domain,
            }
        ):
            yield event
    finally:
        await service.session_close({"session_id": session_id})


async def run_prompt_text(
    service: GatewayService,
    prompt: str,
    *,
    model: str | None = None,
    domain: str | None = None,
) -> str:
    """Run one prompt and aggregate assistant text."""
    text_parts: list[str] = []
    async for event in run_prompt_stream(
        service,
        prompt,
        model=model,
        domain=domain,
    ):
        if event.type == "item.delta":
            text_parts.append(str(event.data.get("text", "")))
    return "".join(text_parts)
