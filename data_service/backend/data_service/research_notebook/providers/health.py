"""Provider health contracts for ResearchNotebook backend features."""

from __future__ import annotations

import os
import shutil
from typing import Any

from .errors import provider_error
from .redaction import redact_public_value


SUPPORTED_OCR_PROVIDERS = {"tesseract", "azure", "google"}
SUPPORTED_TTS_PROVIDERS = {"azure", "google", "elevenlabs", "local", "minimax"}
SUPPORTED_PPTX_EXPORTERS = {"python-pptx", "local"}


def provider_health(kind: str) -> dict[str, Any]:
    normalized = str(kind or "").strip().lower()
    if normalized == "ocr":
        local_available = {"tesseract"} if shutil.which("tesseract") else set()
        return _health_from_env(
            capability="ocr",
            provider_env="OCR_PROVIDER",
            key_env="OCR_API_KEY",
            endpoint_env="OCR_ENDPOINT",
            simulate_env="OCR_SIMULATE_ERROR",
            supported=SUPPORTED_OCR_PROVIDERS,
            local_without_key=local_available,
            unavailable_local={"tesseract"} - local_available,
            not_configured_code="PROVIDER_NOT_CONFIGURED",
            not_configured_reason="no_provider_configured",
            extra={"supported_languages": ["eng", "chi_sim", "chi_tra", "jpn", "kor"]},
        )
    if normalized == "tts":
        voices = _env_list("TTS_VOICES") or ["default"]
        local_available = {"local"} if shutil.which("espeak-ng") else set()
        return _health_from_env(
            capability="tts",
            provider_env="TTS_PROVIDER",
            key_env="TTS_API_KEY",
            endpoint_env="TTS_ENDPOINT",
            simulate_env="TTS_SIMULATE_ERROR",
            supported=SUPPORTED_TTS_PROVIDERS,
            local_without_key=local_available,
            unavailable_local={"local"} - local_available,
            not_configured_code="PROVIDER_NOT_CONFIGURED",
            not_configured_reason="no_provider_configured",
            alternate_key_envs=("MINIMAX_API_KEY", "DATA_SERVICE_AI_API_KEY"),
            alternate_endpoint_envs=("MINIMAX_TTS_ENDPOINT", "MINIMAX_ENDPOINT", "DATA_SERVICE_AI_BASE_URL"),
            extra={
                "voices": voices,
                "default_voice": os.getenv("TTS_DEFAULT_VOICE", voices[0]),
                "supported_languages": _env_list("TTS_LANGUAGES"),
            },
        )
    if normalized in {"pptx", "pptx_export"}:
        health = _health_from_env(
            capability="pptx_export",
            provider_env="PPTX_PROVIDER",
            key_env=None,
            endpoint_env=None,
            simulate_env="PPTX_SIMULATE_ERROR",
            supported=SUPPORTED_PPTX_EXPORTERS,
            local_without_key=SUPPORTED_PPTX_EXPORTERS,
            not_configured_code="EXPORTER_NOT_CONFIGURED",
            not_configured_reason="exporter_not_configured",
            unsupported_code="EXPORTER_UNSUPPORTED",
            extra={"supported_formats": ["pptx"]},
        )
        if health.get("available") and os.getenv("PPTX_EXPORTER_ENABLED", "").strip().lower() not in {"1", "true", "yes"}:
            return _public_health(
                capability="pptx_export",
                provider_name=str(health.get("provider") or "local"),
                provider_kind="exporter",
                available=False,
                status="unavailable",
                unsupported_reason="exporter_not_configured",
                error=provider_error("EXPORTER_NOT_CONFIGURED"),
                extra={"supported_formats": ["pptx"]},
            )
        return health
    error = provider_error("PROVIDER_UNSUPPORTED", f"Provider capability '{normalized}' is not supported.")
    return _public_health(
        capability=normalized or "unknown",
        provider_name=None,
        provider_kind="unsupported",
        available=False,
        status="unavailable",
        unsupported_reason="unsupported_provider_kind",
        error=error,
    )


def capability_flags() -> dict[str, bool]:
    ocr = bool(provider_health("ocr").get("available"))
    tts = bool(provider_health("tts").get("available"))
    pptx = bool(provider_health("pptx_export").get("available"))
    return {
        "ocr": ocr,
        "scanned_pdf_ocr": ocr,
        "tts": tts,
        "audio_overview": tts,
        "slides": True,
        "slide_outline": True,
        "pptx_export": pptx,
        "mindmap": True,
        "compare": True,
    }


def _health_from_env(
    *,
    capability: str,
    provider_env: str,
    key_env: str | None,
    endpoint_env: str | None,
    simulate_env: str,
    supported: set[str],
    local_without_key: set[str],
    unavailable_local: set[str] | None = None,
    not_configured_code: str,
    not_configured_reason: str,
    unsupported_code: str = "PROVIDER_UNSUPPORTED",
    extra: dict[str, Any] | None = None,
    alternate_key_envs: tuple[str, ...] = (),
    alternate_endpoint_envs: tuple[str, ...] = (),
) -> dict[str, Any]:
    provider_name = os.getenv(provider_env, "").strip()
    key = _first_env_value((key_env,) if key_env else (), alternate_key_envs)
    endpoint = _first_env_value((endpoint_env,) if endpoint_env else (), alternate_endpoint_envs)
    if not provider_name:
        return _public_health(
            capability=capability,
            provider_name=None,
            provider_kind="not_configured",
            available=False,
            status="unavailable",
            unsupported_reason=not_configured_reason,
            error=provider_error(not_configured_code),
            extra=extra,
        )

    normalized_provider = provider_name.strip().lower()
    if normalized_provider not in supported:
        return _public_health(
            capability=capability,
            provider_name=provider_name,
            provider_kind=_provider_kind(normalized_provider, local_without_key),
            available=False,
            status="unavailable",
            unsupported_reason="unsupported_provider",
            error=provider_error(unsupported_code),
            endpoint_configured=bool(endpoint),
            extra=extra,
        )

    if normalized_provider in (unavailable_local or set()):
        return _public_health(
            capability=capability,
            provider_name=provider_name,
            provider_kind=_provider_kind(normalized_provider, local_without_key | (unavailable_local or set())),
            available=False,
            status="unavailable",
            unsupported_reason="local_provider_unavailable",
            error=provider_error("PROVIDER_NOT_CONFIGURED"),
            endpoint_configured=bool(endpoint),
            extra=extra,
        )

    simulated = _simulated_error(os.getenv(simulate_env, "").strip())
    if simulated:
        return _public_health(
            capability=capability,
            provider_name=provider_name,
            provider_kind=_provider_kind(normalized_provider, local_without_key),
            available=False,
            status="unavailable",
            unsupported_reason=simulated["reason"],
            error=provider_error(simulated["code"]),
            endpoint_configured=bool(endpoint),
            extra=extra,
        )

    if normalized_provider not in local_without_key and not key:
        return _public_health(
            capability=capability,
            provider_name=provider_name,
            provider_kind=_provider_kind(normalized_provider, local_without_key),
            available=False,
            status="unavailable",
            unsupported_reason="missing_api_key",
            error=provider_error("PROVIDER_MISSING_CREDENTIAL"),
            endpoint_configured=bool(endpoint),
            extra=extra,
        )

    return _public_health(
        capability=capability,
        provider_name=provider_name,
        provider_kind=_provider_kind(normalized_provider, local_without_key),
        available=True,
        status="available",
        unsupported_reason=None,
        error=None,
        endpoint_configured=bool(endpoint),
        extra=extra,
    )


def _public_health(
    *,
    capability: str,
    provider_name: str | None,
    provider_kind: str,
    available: bool,
    status: str,
    unsupported_reason: str | None,
    error: dict[str, Any] | None,
    endpoint_configured: bool = False,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "available": available,
        "status": status,
        "capability": capability,
        "provider": provider_name,
        "provider_detail": {
            "name": provider_name,
            "kind": provider_kind,
            "available": available,
        },
        "latency_ms": None,
        "unsupported_reason": unsupported_reason,
        "error": error,
        "warnings": [] if available else [unsupported_reason or (error or {}).get("code") or "provider_unavailable"],
        "next_actions": [] if available else ["configure_provider"],
        "endpoint_configured": endpoint_configured,
    }
    if extra:
        payload.update(extra)
    return redact_public_value(payload)


def _provider_kind(provider_name: str, local_without_key: set[str]) -> str:
    return "local" if provider_name in local_without_key else "external"


def _simulated_error(value: str) -> dict[str, str] | None:
    if not value:
        return None
    normalized = value.strip().lower()
    return {
        "auth_failed": {"code": "PROVIDER_AUTH_FAILED", "reason": "auth_failed"},
        "timeout": {"code": "PROVIDER_TIMEOUT", "reason": "timeout"},
        "quota_exceeded": {"code": "PROVIDER_QUOTA_EXCEEDED", "reason": "quota_exceeded"},
        "bad_response": {"code": "PROVIDER_BAD_RESPONSE", "reason": "bad_response"},
        "execution_failed": {"code": "PROVIDER_EXECUTION_FAILED", "reason": "execution_failed"},
        "output_invalid": {"code": "PROVIDER_OUTPUT_INVALID", "reason": "output_invalid"},
        "unavailable": {"code": "PROVIDER_UNAVAILABLE", "reason": "provider_unavailable"},
    }.get(normalized)


def _env_list(name: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, "").split(",") if item.strip()]


def _first_env_value(primary: tuple[str, ...], alternate: tuple[str, ...]) -> str:
    for name in (*primary, *alternate):
        value = os.getenv(name or "", "").strip()
        if value:
            return value
    return ""
