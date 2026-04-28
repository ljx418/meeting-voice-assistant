from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _demo_env() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "DEEPSEEK_API_KEY": "",
            "MINIMAX_API_KEY": "",
            "OPENAI_API_KEY": "",
            "OPENHARNESS_API_KEY": "",
            "ANTHROPIC_API_KEY": "",
            "PYTHONPYCACHEPREFIX": "/tmp/harnessos-pycache",
        }
    )
    return env


def test_cli_run_text_demo():
    process = subprocess.run(
        [sys.executable, "-m", "cli.main", "run", "你好"],
        cwd=PROJECT_ROOT,
        env=_demo_env(),
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )

    assert process.returncode == 0
    assert "NotOpenSSLWarning" not in process.stderr
    assert "你好" in process.stdout
    assert "demo mode" in process.stdout


def test_cli_run_json_demo():
    process = subprocess.run(
        [sys.executable, "-m", "cli.main", "run", "--json", "你好"],
        cwd=PROJECT_ROOT,
        env=_demo_env(),
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )

    assert process.returncode == 0
    assert "NotOpenSSLWarning" not in process.stderr
    payload = json.loads(process.stdout)
    assert payload["session_id"].startswith("sess_")
    assert payload["turn_id"].startswith("turn_")
    assert "你好" in payload["final_text"]
    assert payload["events"][0]["type"] == "turn.started"
