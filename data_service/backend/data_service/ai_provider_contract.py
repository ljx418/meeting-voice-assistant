"""ResearchNotebook V1.5 AI provider contract."""

from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class AIProviderContractError(RuntimeError):
    """Stable provider contract error."""

    def __init__(self, code: str, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.retryable = retryable


@dataclass(frozen=True)
class AIProviderConfig:
    provider: str
    provider_name: str
    base_url: str
    model: str
    timeout_ms: int
    max_tokens: int
    temperature: float
    api_key: str

    @classmethod
    def from_env(cls) -> "AIProviderConfig":
        provider = os.getenv("DATA_SERVICE_AI_PROVIDER", "").strip()
        provider_name = os.getenv("DATA_SERVICE_AI_PROVIDER_NAME", "").strip()
        base_url = os.getenv("DATA_SERVICE_AI_BASE_URL", "").strip()
        model = os.getenv("DATA_SERVICE_AI_MODEL", "").strip()
        api_key = os.getenv("DATA_SERVICE_AI_API_KEY", "").strip()

        missing = []
        if not provider:
            missing.append("DATA_SERVICE_AI_PROVIDER")
        if not provider_name:
            missing.append("DATA_SERVICE_AI_PROVIDER_NAME")
        if not base_url:
            missing.append("DATA_SERVICE_AI_BASE_URL")
        if not model:
            missing.append("DATA_SERVICE_AI_MODEL")
        if not api_key:
            raise AIProviderContractError("missing_api_key", "DATA_SERVICE_AI_API_KEY is not configured")
        if missing:
            raise AIProviderContractError("missing_provider_config", f"Missing provider config: {', '.join(missing)}")

        normalized_provider = provider.lower().replace("_", "-")
        if normalized_provider not in {"openai-compatible", "openai"}:
            raise AIProviderContractError("missing_provider_config", "DATA_SERVICE_AI_PROVIDER must be openai_compatible")

        return cls(
            provider="openai_compatible",
            provider_name=provider_name,
            base_url=base_url.rstrip("/"),
            model=model,
            timeout_ms=int(os.getenv("DATA_SERVICE_AI_TIMEOUT_MS", "30000")),
            max_tokens=int(os.getenv("DATA_SERVICE_AI_MAX_TOKENS", "1200")),
            temperature=float(os.getenv("DATA_SERVICE_AI_TEMPERATURE", "0.2")),
            api_key=api_key,
        )


def _provider_metadata(config: AIProviderConfig) -> dict[str, Any]:
    return {
        "provider": config.provider,
        "provider_name": config.provider_name,
        "model": config.model,
        "timeout_ms": config.timeout_ms,
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
        "api_key_configured": bool(config.api_key),
    }


def ai_provider_metadata() -> dict[str, Any]:
    """Return sanitized configured provider metadata without making a request."""

    return _provider_metadata(AIProviderConfig.from_env())


def _classify_http_error(exc: urllib.error.HTTPError) -> AIProviderContractError:
    if exc.code in {401, 403}:
        return AIProviderContractError("auth_failed", "AI provider authentication failed")
    if exc.code == 404:
        return AIProviderContractError("model_not_found", "AI provider model or endpoint was not found")
    if exc.code == 429:
        return AIProviderContractError("rate_limited", "AI provider rate limit exceeded", retryable=True)
    if exc.code in {408, 500, 502, 503, 504}:
        return AIProviderContractError("provider_unavailable", "AI provider is unavailable", retryable=True)
    return AIProviderContractError("provider_unavailable", f"AI provider returned HTTP {exc.code}", retryable=True)


def _chat_completion(config: AIProviderConfig, *, system_prompt: str, user_prompt: str) -> tuple[str, dict[str, Any], int]:
    payload = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
    }
    request = urllib.request.Request(
        f"{config.base_url}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}",
        },
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=config.timeout_ms / 1000, context=_ssl_context()) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except TimeoutError as exc:
        raise AIProviderContractError("provider_timeout", "AI provider request timed out", retryable=True) from exc
    except urllib.error.HTTPError as exc:
        raise _classify_http_error(exc) from exc
    except urllib.error.URLError as exc:
        reason = str(getattr(exc, "reason", exc))
        code = "provider_timeout" if "timed out" in reason.lower() else "provider_unavailable"
        raise AIProviderContractError(code, "AI provider request failed", retryable=True) from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise AIProviderContractError("response_schema_mismatch", "AI provider returned invalid JSON") from exc

    latency_ms = int((time.monotonic() - started) * 1000)
    try:
        text = raw["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AIProviderContractError("response_schema_mismatch", "AI provider response missing choices[0].message.content") from exc
    if not isinstance(text, str) or not text.strip():
        raise AIProviderContractError("response_schema_mismatch", "AI provider response content is empty")
    return text, raw, latency_ms


def _extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    candidates = [stripped]
    first = stripped.find("{")
    last = stripped.rfind("}")
    if first >= 0 and last > first:
        candidates.append(stripped[first : last + 1])
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise AIProviderContractError("response_schema_mismatch", "AI provider response is not a JSON object")


def ai_complete_json(*, system_prompt: str, user_prompt: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run a real provider JSON completion and return parsed JSON plus sanitized metadata."""

    config = AIProviderConfig.from_env()
    text, _raw, latency_ms = _chat_completion(config, system_prompt=system_prompt, user_prompt=user_prompt)
    parsed = _extract_json_object(text)
    metadata = {
        **_provider_metadata(config),
        "latency_ms": latency_ms,
        "response_schema": "openai_chat_completions",
        "response_text_chars": len(text.strip()),
    }
    return parsed, metadata


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi  # type: ignore

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def ai_provider_health_payload() -> dict[str, Any]:
    """Run a real OpenAI-compatible provider smoke and return sanitized metadata."""

    config = AIProviderConfig.from_env()
    text, raw, latency_ms = _chat_completion(
        config,
        system_prompt="You are a health probe. Reply with a short JSON object.",
        user_prompt='Return exactly this JSON shape with your own short value: {"status":"ok","message":"ready"}',
    )
    return {
        "provider_available": True,
        "provider": _provider_metadata(config),
        "latency_ms": latency_ms,
        "response_schema": "openai_chat_completions",
        "response_text_chars": len(text.strip()),
        "raw_response_keys": sorted(str(key) for key in raw.keys())[:20],
    }
