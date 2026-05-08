"""Preflight check for real MCP / real-audio acceptance."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import (  # noqa: E402
    get_data_service_mcp_config,
    get_funasr_mcp_config,
    get_meeting_mcp_config,
)


EXPECTED_AUDIO_SUFFIXES = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4"}
HARNESS_VENV = PROJECT_ROOT / ".venv" / "bin" / "python"


def main() -> int:
    payload = build_report()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] in {"ok", "integration_disabled"} else 1


def build_report() -> dict[str, Any]:
    meeting = get_meeting_mcp_config()
    funasr = get_funasr_mcp_config()
    data_service = get_data_service_mcp_config()
    configured_audio_dir = os.environ.get("HARNESS_MEETING_MCP_AUDIO_DIR")
    audio_dir = Path(configured_audio_dir or meeting.audio_dir).expanduser().resolve()
    audio_files = []
    if audio_dir.exists() and audio_dir.is_dir():
        audio_files = [
            path.name for path in sorted(audio_dir.iterdir())
            if path.is_file() and path.suffix.lower() in EXPECTED_AUDIO_SUFFIXES
        ]
    configured_audio_file = os.environ.get("HARNESS_MEETING_ACCEPTANCE_AUDIO_FILE")
    preferred_audio = (
        Path(configured_audio_file).expanduser().resolve()
        if configured_audio_file
        else _preferred_audio_file(audio_dir)
    )

    checks = {
        "harness_python": _python_check(HARNESS_VENV, imports=("pytest",)),
        "meeting_mcp_python": _python_check(Path(meeting.command), imports=("mcp", "aiohttp"), cwd=meeting.cwd),
        "funasr_mcp_python": _python_check(
            Path(funasr.command),
            imports=("mcp", "funasr_service.mcp_stdio"),
            cwd=funasr.cwd,
        ),
        "data_service_mcp_python": _python_check(Path(data_service.command), imports=("mcp",), cwd=data_service.cwd),
        "meeting_http_health": _http_check("http://127.0.0.1:8000/api/v1/health") if configured_audio_dir else _disabled_check("HARNESS_MEETING_MCP_AUDIO_DIR is not set"),
        "funasr_http_health": _http_check("http://127.0.0.1:8001/health") if configured_audio_dir else _disabled_check("HARNESS_MEETING_MCP_AUDIO_DIR is not set"),
        "audio_dir": {
            "enabled": bool(configured_audio_dir),
            "ok": bool(configured_audio_dir) and audio_dir.exists() and audio_dir.is_dir(),
            "path": str(audio_dir),
            "preferred_audio": str(preferred_audio),
            "preferred_exists": preferred_audio.exists(),
            "file_count": len(audio_files),
            "sample_files": audio_files[:5],
        },
        "resolved_commands": {
            "meeting_mcp_command": meeting.command,
            "funasr_mcp_command": funasr.command,
            "data_service_mcp_command": data_service.command,
        },
        "env_overrides": {
            "HARNESS_MEETING_MCP_COMMAND": os.environ.get("HARNESS_MEETING_MCP_COMMAND"),
            "HARNESS_FUNASR_MCP_COMMAND": os.environ.get("HARNESS_FUNASR_MCP_COMMAND"),
            "HARNESS_DATA_SERVICE_MCP_COMMAND": os.environ.get("HARNESS_DATA_SERVICE_MCP_COMMAND"),
            "HARNESS_FUNASR_MCP_EXECUTION": os.environ.get("HARNESS_FUNASR_MCP_EXECUTION"),
            "HARNESS_DATA_SERVICE_MCP_EXECUTION": os.environ.get("HARNESS_DATA_SERVICE_MCP_EXECUTION"),
            "HARNESS_MEETING_MCP_AUDIO_DIR": configured_audio_dir,
            "HARNESS_MEETING_ACCEPTANCE_AUDIO_FILE": configured_audio_file,
        },
    }

    if not configured_audio_dir:
        return {
            "status": "integration_disabled",
            "reason": "HARNESS_MEETING_MCP_AUDIO_DIR is not set; explicit real-audio acceptance is disabled.",
            "checks": checks,
        }

    failures = []
    for key in ("harness_python", "meeting_mcp_python", "funasr_mcp_python", "data_service_mcp_python"):
        if not checks[key]["ok"]:
            failures.append(key)
    if not checks["audio_dir"]["ok"] or checks["audio_dir"]["file_count"] == 0:
        failures.append("audio_dir")
    if not checks["meeting_http_health"]["ok"]:
        failures.append("meeting_http_health")
    if not checks["funasr_http_health"]["ok"]:
        failures.append("funasr_http_health")

    return {
        "status": "ok" if not failures else "blocked",
        "failures": failures,
        "checks": checks,
    }


def _python_check(path: Path, *, imports: tuple[str, ...], cwd: str | None = None) -> dict[str, Any]:
    path = path.expanduser()
    if not path.exists():
        return {"ok": False, "path": str(path), "reason": "missing"}
    resolved_cwd = Path(cwd).expanduser() if cwd else None
    env = os.environ.copy()
    if resolved_cwd is not None:
        env["PYTHONPATH"] = f"{resolved_cwd}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
    command = [
        str(path),
        "-c",
        "import json, sys; "
        + "; ".join(f"import {module}" for module in imports)
        + "; print(json.dumps({'executable': sys.executable}))",
    ]
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=str(resolved_cwd) if resolved_cwd and resolved_cwd.exists() else None,
            env=env,
            timeout=15,
        )
        output = completed.stdout.strip()
        details = json.loads(output) if output else {}
        return {
            "ok": True,
            "path": str(path),
            "imports": list(imports),
            "cwd": str(resolved_cwd) if resolved_cwd else None,
            "details": details,
        }
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "path": str(path),
            "imports": list(imports),
            "cwd": str(resolved_cwd) if resolved_cwd else None,
            "reason": str(exc),
        }


def _http_check(url: str) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["curl", "-sS", "--max-time", "5", url],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return {
            "ok": True,
            "url": url,
            "status": 200,
            "body": completed.stdout[:300],
        }
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        return {
            "ok": False,
            "url": url,
            "reason": str(exc),
            "stderr": getattr(exc, "stderr", None),
        }


def _disabled_check(reason: str) -> dict[str, Any]:
    return {
        "ok": False,
        "disabled": True,
        "reason": reason,
    }


def _preferred_audio_file(audio_dir: Path) -> Path:
    if not audio_dir.exists() or not audio_dir.is_dir():
        return audio_dir / "<missing-audio>"
    candidates = [
        path for path in audio_dir.iterdir()
        if path.is_file() and path.suffix.lower() in EXPECTED_AUDIO_SUFFIXES
    ]
    if not candidates:
        return audio_dir / "<missing-audio>"
    return min(candidates, key=lambda path: path.stat().st_size)


if __name__ == "__main__":
    raise SystemExit(main())
