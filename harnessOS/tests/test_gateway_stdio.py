from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_stdio_server_health_ping():
    process = subprocess.run(
        [sys.executable, "-m", "apps.gateway.stdio_server"],
        input='{"id":"req_1","method":"health.ping","params":{}}\n',
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
        timeout=10,
        check=False,
    )

    assert process.returncode == 0
    lines = [line for line in process.stdout.splitlines() if line.strip()]
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["id"] == "req_1"
    assert payload["error"] is None
    assert payload["result"]["status"] == "ok"
    assert "NotOpenSSLWarning" not in process.stderr


def test_stdio_server_workflow_list():
    process = subprocess.run(
        [sys.executable, "-m", "apps.gateway.stdio_server"],
        input='{"id":"w1","method":"workflow.list","params":{}}\n',
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
        timeout=10,
        check=False,
    )

    assert process.returncode == 0
    payload = json.loads(process.stdout)
    assert payload["id"] == "w1"
    assert payload["error"] is None
    assert {item["domain"] for item in payload["result"]["workflows"]} == {"meeting", "knowledge"}
    assert "NotOpenSSLWarning" not in process.stderr


def test_stdio_server_pack_list():
    process = subprocess.run(
        [sys.executable, "-m", "apps.gateway.stdio_server"],
        input='{"id":"p1","method":"pack.list","params":{}}\n',
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
        timeout=10,
        check=False,
    )

    assert process.returncode == 0
    payload = json.loads(process.stdout)
    assert payload["id"] == "p1"
    assert payload["error"] is None
    assert {item["name"] for item in payload["result"]["packs"]} == {
        "meeting",
        "knowledge",
        "investment",
        "interview",
        "video_studio",
    }
    assert "NotOpenSSLWarning" not in process.stderr


def test_stdio_server_job_list():
    process = subprocess.run(
        [sys.executable, "-m", "apps.gateway.stdio_server"],
        input='{"id":"j1","method":"job.list","params":{}}\n',
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
        timeout=10,
        check=False,
    )

    assert process.returncode == 0
    payload = json.loads(process.stdout)
    assert payload["id"] == "j1"
    assert payload["error"] is None
    assert "jobs" in payload["result"]
    assert "NotOpenSSLWarning" not in process.stderr


def test_stdio_server_approval_request():
    process = subprocess.run(
        [sys.executable, "-m", "apps.gateway.stdio_server"],
        input='{"id":"ap1","method":"approval.request","params":{"action":"workspace.write","request_summary":"Write file","trace_id":"trace_stdio"}}\n',
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
        timeout=10,
        check=False,
    )

    assert process.returncode == 0
    payload = json.loads(process.stdout)
    assert payload["id"] == "ap1"
    assert payload["error"] is None
    assert payload["result"]["approval"]["status"] == "pending"
    assert payload["result"]["approval"]["trace_id"] == "trace_stdio"
    assert payload["result"]["trace_id"] == "trace_stdio"
    assert "NotOpenSSLWarning" not in process.stderr


def test_stdio_server_parse_error():
    process = subprocess.run(
        [sys.executable, "-m", "apps.gateway.stdio_server"],
        input="{not-json}\n",
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
        timeout=10,
        check=False,
    )

    assert process.returncode == 0
    payload = json.loads(process.stdout)
    assert payload["error"]["code"] == "PARSE_ERROR"
