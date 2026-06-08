"""Local espeak-ng TTS provider for ResearchNotebook V2.5."""

from __future__ import annotations

import os
import shutil
import subprocess
import time
import tempfile
from pathlib import Path
from typing import Any

from .errors import provider_error


def espeak_available() -> bool:
    return shutil.which("espeak-ng") is not None


def espeak_version() -> str:
    if not espeak_available():
        return ""
    try:
        process = subprocess.run(["espeak-ng", "--version"], capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    output = (process.stdout or process.stderr or "").splitlines()
    return output[0].strip() if output else ""


def synthesize_wav(text: str, output_path: Path, *, voice: str = "en") -> dict[str, Any]:
    if not espeak_available():
        return _error_result("PROVIDER_NOT_CONFIGURED", "espeak-ng executable is not available.")
    spoken = " ".join(str(text or "").split()).strip()
    if not spoken:
        return _error_result("PROVIDER_OUTPUT_INVALID", "TTS script is empty.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_handle = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temporary_output = Path(temporary_handle.name)
    temporary_handle.close()
    if temporary_output.exists():
        temporary_output.unlink()
    started = time.monotonic()
    command = ["espeak-ng", "-v", voice or "en", "-w", str(temporary_output), spoken]
    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
    except subprocess.TimeoutExpired:
        if temporary_output.exists():
            temporary_output.unlink()
        return _error_result("PROVIDER_TIMEOUT", "espeak-ng synthesis timed out.")
    except OSError:
        if temporary_output.exists():
            temporary_output.unlink()
        return _error_result("PROVIDER_EXECUTION_FAILED", "espeak-ng synthesis failed.")
    if process.returncode != 0:
        if temporary_output.exists():
            temporary_output.unlink()
        return _error_result("PROVIDER_EXECUTION_FAILED", "espeak-ng synthesis failed.")
    if not temporary_output.exists() or temporary_output.stat().st_size <= 44:
        if temporary_output.exists():
            temporary_output.unlink()
        return _error_result("PROVIDER_OUTPUT_INVALID", "espeak-ng produced an invalid WAV file.")
    if output_path.exists():
        output_path.unlink()
    shutil.move(str(temporary_output), str(output_path))
    return {
        "ok": True,
        "status": "ready",
        "provider": {
            "name": "local",
            "kind": "local",
            "engine": "espeak-ng",
            "version": espeak_version(),
        },
        "duration_ms": int((time.monotonic() - started) * 1000),
    }


def _error_result(code: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "status": "unavailable",
        "error": provider_error(code, message),
        "provider": {
            "name": "local",
            "kind": "local",
            "engine": "espeak-ng",
            "version": espeak_version() if espeak_available() else None,
        },
    }
