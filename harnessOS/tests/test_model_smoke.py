from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.smoke_model
def test_headless_cli_real_model_smoke():
    if os.getenv("HARNESSOS_RUN_MODEL_SMOKE") != "1":
        pytest.skip("Set HARNESSOS_RUN_MODEL_SMOKE=1 to run real model smoke tests.")

    process = subprocess.run(
        [sys.executable, "-m", "cli.main", "run", "你好"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )

    assert process.returncode == 0
    assert process.stdout.strip()
