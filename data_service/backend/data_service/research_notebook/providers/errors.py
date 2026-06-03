"""Structured public provider errors."""

from __future__ import annotations

from dataclasses import dataclass


PROVIDER_ERROR_CODES = {
    "PROVIDER_NOT_CONFIGURED",
    "PROVIDER_UNSUPPORTED",
    "PROVIDER_MISSING_CREDENTIAL",
    "PROVIDER_AUTH_FAILED",
    "PROVIDER_TIMEOUT",
    "PROVIDER_QUOTA_EXCEEDED",
    "PROVIDER_UNAVAILABLE",
    "PROVIDER_BAD_RESPONSE",
    "PROVIDER_EXECUTION_FAILED",
    "PROVIDER_OUTPUT_INVALID",
    "EXPORTER_NOT_CONFIGURED",
    "EXPORTER_UNSUPPORTED",
    "PDF_RASTERIZER_UNAVAILABLE",
}

RETRYABLE_PROVIDER_ERRORS = {
    "PROVIDER_TIMEOUT",
    "PROVIDER_QUOTA_EXCEEDED",
    "PROVIDER_UNAVAILABLE",
    "PROVIDER_BAD_RESPONSE",
    "PROVIDER_EXECUTION_FAILED",
}


@dataclass(frozen=True)
class ProviderError:
    code: str
    message: str
    retryable: bool = False

    def to_public(self) -> dict:
        code = self.code if self.code in PROVIDER_ERROR_CODES else "PROVIDER_UNAVAILABLE"
        return {
            "code": code,
            "message": self.message,
            "retryable": bool(self.retryable or code in RETRYABLE_PROVIDER_ERRORS),
        }


def provider_error(code: str, message: str | None = None, *, retryable: bool | None = None) -> dict:
    normalized = code if code in PROVIDER_ERROR_CODES else "PROVIDER_UNAVAILABLE"
    text = message or _default_message(normalized)
    return ProviderError(
        code=normalized,
        message=text,
        retryable=normalized in RETRYABLE_PROVIDER_ERRORS if retryable is None else retryable,
    ).to_public()


def _default_message(code: str) -> str:
    return {
        "PROVIDER_NOT_CONFIGURED": "Provider is not configured.",
        "PROVIDER_UNSUPPORTED": "Provider is not supported.",
        "PROVIDER_MISSING_CREDENTIAL": "Provider credential is missing.",
        "PROVIDER_AUTH_FAILED": "Provider authentication failed.",
        "PROVIDER_TIMEOUT": "Provider request timed out.",
        "PROVIDER_QUOTA_EXCEEDED": "Provider quota was exceeded.",
        "PROVIDER_UNAVAILABLE": "Provider is unavailable.",
        "PROVIDER_BAD_RESPONSE": "Provider returned an invalid response.",
        "PROVIDER_EXECUTION_FAILED": "Provider execution failed.",
        "PROVIDER_OUTPUT_INVALID": "Provider output was invalid.",
        "EXPORTER_NOT_CONFIGURED": "Exporter is not configured.",
        "EXPORTER_UNSUPPORTED": "Exporter is not supported.",
        "PDF_RASTERIZER_UNAVAILABLE": "PDF rasterizer is unavailable.",
    }.get(code, "Provider is unavailable.")
