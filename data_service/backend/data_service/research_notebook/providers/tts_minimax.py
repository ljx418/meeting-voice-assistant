"""Minimax TTS provider adapter for ResearchNotebook V2.5 Phase 39."""

from __future__ import annotations

import base64
import json
import os
import ssl
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from .errors import provider_error


DEFAULT_MINIMAX_TTS_ENDPOINT = "https://api.minimax.io/v1/t2a_v2"
DEFAULT_MINIMAX_TTS_MODEL = "speech-2.8-hd"
DEFAULT_MINIMAX_TTS_VOICE = "Wise_Woman"


def synthesize_minimax_tts(text: str, output_path: Path, *, voice: str | None = None) -> dict[str, Any]:
    spoken = " ".join(str(text or "").split()).strip()
    if not spoken:
        return _error_result("PROVIDER_OUTPUT_INVALID", "TTS script is empty.")
    config = minimax_tts_config()
    if not config["api_key"]:
        return _error_result("PROVIDER_MISSING_CREDENTIAL", "Minimax TTS credential is missing.", config=config)
    body = {
        "model": config["model"],
        "text": spoken,
        "stream": False,
        "voice_setting": {
            "voice_id": voice or config["voice_id"],
            "speed": 1.0,
            "vol": 1.0,
            "pitch": 0,
        },
        "audio_setting": {
            "sample_rate": 32000,
            "bitrate": 128000,
            "format": "wav",
            "channel": 1,
        },
    }
    request = urllib.request.Request(
        config["endpoint"],
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=config["timeout_seconds"], context=_ssl_context()) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return _http_error_result(exc.code, config=config)
    except urllib.error.URLError as exc:
        reason = str(getattr(exc, "reason", "") or "")
        code = "PROVIDER_TIMEOUT" if "timed out" in reason.lower() else "PROVIDER_UNAVAILABLE"
        return _error_result(code, "Minimax TTS provider is unavailable.", config=config)
    except TimeoutError:
        return _error_result("PROVIDER_TIMEOUT", "Minimax TTS provider timed out.", config=config)
    except (json.JSONDecodeError, OSError):
        return _error_result("PROVIDER_BAD_RESPONSE", "Minimax TTS provider returned an invalid response.", config=config)

    audio_bytes = _audio_bytes_from_payload(payload)
    if not audio_bytes or len(audio_bytes) <= 44:
        return _error_result("PROVIDER_OUTPUT_INVALID", "Minimax TTS provider returned invalid audio.", config=config)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(audio_bytes)
    return {
        "ok": True,
        "status": "ready",
        "provider": {
            "name": "minimax",
            "kind": "external",
            "model": config["model"],
            "voice_id": voice or config["voice_id"],
            "audio_format": "wav",
        },
        "duration_ms": int((time.monotonic() - started) * 1000),
    }


def minimax_tts_config() -> dict[str, Any]:
    endpoint = _first_env("TTS_ENDPOINT", "MINIMAX_TTS_ENDPOINT", "MINIMAX_ENDPOINT")
    if not endpoint:
        endpoint = _endpoint_from_base_url(_first_env("DATA_SERVICE_AI_BASE_URL")) or DEFAULT_MINIMAX_TTS_ENDPOINT
    return {
        "api_key": _first_env("TTS_API_KEY", "MINIMAX_API_KEY", "DATA_SERVICE_AI_API_KEY"),
        "endpoint": endpoint,
        "model": _first_env("MINIMAX_TTS_MODEL", "TTS_MODEL") or DEFAULT_MINIMAX_TTS_MODEL,
        "voice_id": _first_env("MINIMAX_TTS_VOICE_ID", "TTS_VOICE_ID", "TTS_DEFAULT_VOICE") or DEFAULT_MINIMAX_TTS_VOICE,
        "timeout_seconds": _timeout_seconds(),
    }


def _audio_bytes_from_payload(payload: dict[str, Any]) -> bytes | None:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    candidate = data.get("audio") or data.get("audio_file") or payload.get("audio")
    if not isinstance(candidate, str) or not candidate.strip():
        return None
    value = candidate.strip()
    try:
        return bytes.fromhex(value)
    except ValueError:
        try:
            return base64.b64decode(value, validate=True)
        except (ValueError, base64.binascii.Error):
            return None


def _http_error_result(status_code: int, *, config: dict[str, Any]) -> dict[str, Any]:
    if status_code in {401, 403}:
        return _error_result("PROVIDER_AUTH_FAILED", "Minimax TTS authentication failed.", config=config)
    if status_code == 429:
        return _error_result("PROVIDER_QUOTA_EXCEEDED", "Minimax TTS quota was exceeded.", config=config)
    if status_code in {408, 504}:
        return _error_result("PROVIDER_TIMEOUT", "Minimax TTS provider timed out.", config=config)
    if status_code >= 500:
        return _error_result("PROVIDER_UNAVAILABLE", "Minimax TTS provider is unavailable.", config=config)
    return _error_result("PROVIDER_BAD_RESPONSE", "Minimax TTS provider returned an error.", config=config)


def _error_result(code: str, message: str, *, config: dict[str, Any] | None = None) -> dict[str, Any]:
    provider: dict[str, Any] = {
        "name": "minimax",
        "kind": "external",
    }
    if config:
        provider.update(
            {
                "model": config.get("model"),
                "voice_id": config.get("voice_id"),
                "endpoint_configured": bool(config.get("endpoint")),
            }
        )
    return {
        "ok": False,
        "status": "unavailable",
        "error": provider_error(code, message),
        "provider": provider,
    }


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _endpoint_from_base_url(base_url: str) -> str:
    value = str(base_url or "").strip()
    if not value:
        return ""
    if value.rstrip("/").endswith("/t2a_v2"):
        return value
    return urljoin(value.rstrip("/") + "/", "t2a_v2")


def _timeout_seconds() -> float:
    raw = _first_env("MINIMAX_TTS_TIMEOUT_SECONDS", "TTS_TIMEOUT_SECONDS")
    if not raw:
        raw_ms = _first_env("DATA_SERVICE_AI_TIMEOUT_MS")
        if raw_ms:
            try:
                return max(1.0, float(raw_ms) / 1000.0)
            except ValueError:
                return 60.0
        return 60.0
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 60.0


def _ssl_context() -> ssl.SSLContext | None:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return None
