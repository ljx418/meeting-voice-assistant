#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON:-$ROOT_DIR/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="${PYTHON:-python3}"
fi

export HARNESS_FUNASR_MCP_EXECUTION="${HARNESS_FUNASR_MCP_EXECUTION:-stdio}"
export HARNESS_FUNASR_MCP_ENDPOINT="${HARNESS_FUNASR_MCP_ENDPOINT:-http://127.0.0.1:8001}"

"$PYTHON_BIN" - <<'PY'
from __future__ import annotations

import json
import os
import shutil
import sys
import urllib.request
from pathlib import Path


def _status(status: str, **payload):
    print(json.dumps({"status": status, **payload}, ensure_ascii=False, indent=2))
    return 0 if status in {"ok", "integration_disabled"} else 1


audio_dir = os.getenv("HARNESS_MEETING_E2E_AUDIO_DIR") or os.getenv("HARNESS_MEETING_MCP_AUDIO_DIR")
if not audio_dir:
    raise SystemExit(_status("integration_disabled", reason="HARNESS_MEETING_E2E_AUDIO_DIR is not set"))

audio_root = Path(audio_dir).expanduser()
if not audio_root.exists() or not audio_root.is_dir():
    raise SystemExit(_status("failed", failure="audio_dir_missing", audio_dir=str(audio_root)))

if os.getenv("HARNESS_FUNASR_MCP_EXECUTION") != "stdio":
    raise SystemExit(_status("failed", failure="funasr_stdio_disabled"))

endpoint = os.getenv("HARNESS_FUNASR_MCP_ENDPOINT", "http://127.0.0.1:8001").rstrip("/")
try:
    with urllib.request.urlopen(f"{endpoint}/health", timeout=3) as response:
        funasr_health = json.loads(response.read().decode("utf-8"))
except Exception as exc:
    raise SystemExit(_status("failed", failure="funasr_http_unavailable", endpoint=endpoint, message=str(exc)))

command = os.getenv("HARNESS_FUNASR_MCP_COMMAND") or sys.executable
resolved_command = shutil.which(command) if "/" not in command else command
if not resolved_command or not Path(resolved_command).exists():
    raise SystemExit(_status("failed", failure="funasr_mcp_command_missing", command=command))

cwd = Path(os.getenv("HARNESS_FUNASR_MCP_CWD", "/Users/Zhuanz/Desktop/workspace/voice_service")).expanduser()
if not cwd.exists():
    raise SystemExit(_status("failed", failure="funasr_mcp_cwd_missing", cwd=str(cwd)))

raise SystemExit(
    _status(
        "ok",
        audio_dir=str(audio_root),
        funasr_endpoint=endpoint,
        funasr_health=funasr_health,
        funasr_mcp_command=str(resolved_command),
        funasr_mcp_cwd=str(cwd),
        strict=os.getenv("HARNESS_MEETING_E2E_STRICT", ""),
    )
)
PY
