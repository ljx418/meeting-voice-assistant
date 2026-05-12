"""Stable BFF error responses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from fastapi.responses import JSONResponse

from .security import redact


@dataclass
class BffError(Exception):
    code: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    status_code: int = 400

    def __str__(self) -> str:
        return str(redact(self.message))


class ErrorSanitizer:
    """Replace with a product-specific sanitizer in real BFFs."""

    def response(self, exc: Exception) -> JSONResponse:
        if isinstance(exc, BffError):
            return self.error(exc.code, exc.message, data=exc.data, status_code=exc.status_code)
        code = str(getattr(exc, "code", "RUNTIME_ERROR"))
        data = getattr(exc, "data", {})
        return self.error(code, str(exc), data=data if isinstance(data, dict) else {}, status_code=self.status_for(code))

    def error(self, code: str, message: str, *, data: dict[str, Any] | None = None, status_code: int | None = None) -> JSONResponse:
        return JSONResponse(
            status_code=status_code or self.status_for(code),
            content={"error": {"code": code, "message": redact(message), "data": redact(data or {})}},
        )

    @staticmethod
    def status_for(code: str) -> int:
        if code in {"AUTH_REQUIRED", "AUTH_INVALID", "AUTH_NOT_CONFIGURED"}:
            return 401
        if code in {"AUTH_FORBIDDEN", "CAPABILITY_DENIED", "METHOD_FORBIDDEN", "SCOPE_MISMATCH"}:
            return 403
        if code.endswith("_NOT_FOUND"):
            return 404
        return 400
