"""harnessOS SDK client wrapper for the BFF template."""

from __future__ import annotations

from harnessos_client import HarnessOSClient, Scope

from .settings import BffSettings


def create_harnessos_client(settings: BffSettings, scope: Scope) -> HarnessOSClient:
    return HarnessOSClient(
        base_url=settings.harnessos_base_url,
        capability_token=settings.harnessos_capability_token,
        scope=scope,
    )
