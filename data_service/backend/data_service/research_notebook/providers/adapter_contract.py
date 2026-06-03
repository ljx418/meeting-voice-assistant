"""Provider execution contracts for ResearchNotebook provider-backed artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .errors import provider_error
from .health import (
    SUPPORTED_OCR_PROVIDERS,
    SUPPORTED_PPTX_EXPORTERS,
    SUPPORTED_TTS_PROVIDERS,
    provider_health,
)
from .redaction import redact_public_value


EXECUTION_SUPPORTED_PROVIDERS = {
    ("ocr", "tesseract"),
    ("tts", "local"),
    ("tts", "minimax"),
    ("pptx_export", "local"),
    ("pptx_export", "python-pptx"),
}

KNOWN_PROVIDERS_BY_CAPABILITY = {
    "ocr": SUPPORTED_OCR_PROVIDERS | {"minimax"},
    "tts": SUPPORTED_TTS_PROVIDERS | {"minimax"},
    "pptx_export": SUPPORTED_PPTX_EXPORTERS,
}


class ProviderExecutionAdapter(Protocol):
    """Execution adapter boundary for real provider implementations."""

    capability: str
    provider_name: str

    def execute(self, request: "ProviderExecutionRequest") -> "ProviderExecutionResult":
        """Execute provider work and return the shared public result shape."""


@dataclass(frozen=True)
class ProviderExecutionRequest:
    capability: str
    provider_name: str | None = None
    workspace_id: str | None = None
    source_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderCapability:
    capability: str
    provider_name: str | None
    provider_kind: str
    health_known: bool
    health_available: bool
    execution_supported: bool
    unsupported_reason: str | None = None

    def to_public(self) -> dict[str, Any]:
        return redact_public_value(
            {
                "capability": self.capability,
                "provider": {
                    "name": self.provider_name,
                    "kind": self.provider_kind,
                    "health_known": self.health_known,
                    "health_available": self.health_available,
                    "execution_supported": self.execution_supported,
                },
                "unsupported_reason": self.unsupported_reason,
            }
        )


@dataclass(frozen=True)
class ArtifactWriteResult:
    ok: bool
    status: str
    artifact_id: str | None = None
    artifact: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)

    def to_public(self) -> dict[str, Any]:
        return redact_public_value(
            {
                "ok": self.ok,
                "status": self.status,
                "artifact_id": self.artifact_id,
                "artifact": self.artifact,
                "error": self.error,
                "warnings": self.warnings,
                "redacted": True,
            }
        )


@dataclass(frozen=True)
class ProviderExecutionResult:
    ok: bool
    capability: str
    provider: ProviderCapability
    status: str
    artifact: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)

    def to_public(self) -> dict[str, Any]:
        return redact_public_value(
            {
                "ok": self.ok,
                "status": self.status,
                "capability": self.capability,
                "provider": self.provider.to_public()["provider"],
                "artifact": self.artifact,
                "error": self.error,
                "warnings": self.warnings,
                "redacted": True,
            }
        )


def provider_execution_capability(
    capability: str,
    provider_name: str | None = None,
    *,
    health_payload: dict[str, Any] | None = None,
) -> ProviderCapability:
    normalized_capability = _normalize_capability(capability)
    health = health_payload or provider_health(normalized_capability)
    resolved_provider = _normalize_provider(provider_name or health.get("provider"))
    provider_detail = health.get("provider_detail") if isinstance(health.get("provider_detail"), dict) else {}
    provider_kind = str(provider_detail.get("kind") or _provider_kind(normalized_capability, resolved_provider))
    health_known = _health_known(normalized_capability, resolved_provider)
    health_available = bool(health.get("available")) and bool(resolved_provider)
    execution_supported = (
        health_available
        and bool(resolved_provider)
        and (normalized_capability, resolved_provider) in EXECUTION_SUPPORTED_PROVIDERS
    )
    unsupported_reason = None
    if not resolved_provider:
        unsupported_reason = str(health.get("unsupported_reason") or "no_provider_configured")
    elif not health_known:
        unsupported_reason = "unsupported_provider"
    elif not execution_supported:
        unsupported_reason = "execution_adapter_unavailable"
    return ProviderCapability(
        capability=normalized_capability,
        provider_name=resolved_provider,
        provider_kind=provider_kind,
        health_known=health_known,
        health_available=health_available,
        execution_supported=execution_supported,
        unsupported_reason=unsupported_reason,
    )


def unsupported_execution_result(
    capability: str,
    provider_name: str | None = None,
    *,
    health_payload: dict[str, Any] | None = None,
    message: str | None = None,
) -> ProviderExecutionResult:
    provider = provider_execution_capability(capability, provider_name, health_payload=health_payload)
    provider_label = provider.provider_name or "not_configured"
    return ProviderExecutionResult(
        ok=False,
        capability=provider.capability,
        provider=provider,
        status="unavailable",
        artifact=None,
        error=provider_error(
            "PROVIDER_UNSUPPORTED",
            message or f"Provider '{provider_label}' has no execution adapter for {provider.capability}.",
        ),
        warnings=[provider.unsupported_reason or "execution_adapter_unavailable"],
    )


def provider_execution_status(capability: str, provider_name: str | None = None) -> dict[str, Any]:
    provider = provider_execution_capability(capability, provider_name)
    if provider.execution_supported:
        return ProviderExecutionResult(
            ok=True,
            capability=provider.capability,
            provider=provider,
            status="available",
            artifact=None,
            error=None,
            warnings=[],
        ).to_public()
    return unsupported_execution_result(provider.capability, provider.provider_name).to_public()


def _normalize_capability(capability: str) -> str:
    normalized = str(capability or "").strip().lower()
    if normalized in {"pptx", "pptx_export"}:
        return "pptx_export"
    return normalized


def _normalize_provider(provider_name: str | None) -> str | None:
    normalized = str(provider_name or "").strip().lower()
    return normalized or None


def _health_known(capability: str, provider_name: str | None) -> bool:
    if not provider_name:
        return False
    return provider_name in KNOWN_PROVIDERS_BY_CAPABILITY.get(capability, set())


def _provider_kind(capability: str, provider_name: str | None) -> str:
    if not provider_name:
        return "not_configured"
    if (capability, provider_name) in {
        ("ocr", "tesseract"),
        ("tts", "local"),
        ("tts", "minimax"),
        ("pptx_export", "local"),
        ("pptx_export", "python-pptx"),
    }:
        return "local"
    return "external"
