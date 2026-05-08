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
    assert {item["domain"] for item in payload["result"]["workflows"]} == {
        "meeting",
        "knowledge",
        "video_studio",
    }
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


def test_stdio_server_connector_list():
    process = subprocess.run(
        [sys.executable, "-m", "apps.gateway.stdio_server"],
        input='{"id":"c1","method":"connector.list","params":{}}\n',
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
        timeout=10,
        check=False,
    )

    assert process.returncode == 0
    payload = json.loads(process.stdout)
    assert payload["id"] == "c1"
    assert payload["error"] is None
    connectors = {item["connector_id"]: item for item in payload["result"]["connectors"]}
    assert connectors["meeting_voice_mcp"]["domain"] == "meeting"
    assert connectors["meeting_voice_mcp"]["config_ref"] == "HARNESS_MEETING_MCP_*"
    assert connectors["funasr_mcp"]["domain"] == "meeting"
    assert connectors["funasr_mcp"]["config_ref"] == "HARNESS_FUNASR_MCP_*"
    assert "funasr_recognize_file" in connectors["funasr_mcp"]["capabilities"]["tools"]
    assert connectors["data_service_mcp"]["domain"] == "knowledge"
    assert connectors["data_service_mcp"]["health"] == "contract_stub"
    assert "NotOpenSSLWarning" not in process.stderr


def test_stdio_server_connector_submit():
    process = subprocess.run(
        [sys.executable, "-m", "apps.gateway.stdio_server"],
        input='{"id":"cs1","method":"connector.submit","params":{"connector_id":"data_service_mcp","tool":"knowledge_query","input":{"query":"demo"}}}\n',
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
        timeout=10,
        check=False,
    )

    assert process.returncode == 0
    payload = json.loads(process.stdout)
    assert payload["id"] == "cs1"
    assert payload["error"] is None
    assert payload["result"]["approval_required"] is True
    assert payload["result"]["job"]["status"] == "queued"
    assert "artifact" not in payload["result"]
    assert "NotOpenSSLWarning" not in process.stderr


def test_stdio_server_agent_list():
    process = subprocess.run(
        [sys.executable, "-m", "apps.gateway.stdio_server"],
        input='{"id":"a1","method":"agent.list","params":{"domain":"knowledge"}}\n',
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
        timeout=10,
        check=False,
    )

    assert process.returncode == 0
    payload = json.loads(process.stdout)
    assert payload["id"] == "a1"
    assert payload["error"] is None
    assert [item["agent_id"] for item in payload["result"]["agents"]] == [
        "knowledge.curator",
        "knowledge.quality_reviewer",
    ]
    assert "NotOpenSSLWarning" not in process.stderr


def test_stdio_server_memory_summary():
    process = subprocess.run(
        [sys.executable, "-m", "apps.gateway.stdio_server"],
        input=(
            '{"id":"s1","method":"session.start","params":{}}\n'
            '{"id":"m1","method":"memory.summary","params":{"session_id":"sess_missing"}}\n'
        ),
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
        timeout=10,
        check=False,
    )

    assert process.returncode == 0
    payloads = [json.loads(line) for line in process.stdout.splitlines() if line.strip()]
    assert payloads[0]["id"] == "s1"
    assert payloads[0]["error"] is None
    assert payloads[1]["id"] == "m1"
    assert payloads[1]["error"] is not None
    assert payloads[1]["error"]["code"] == "SESSION_NOT_FOUND"
    assert "NotOpenSSLWarning" not in process.stderr


def test_stdio_server_pack_plan():
    process = subprocess.run(
        [sys.executable, "-m", "apps.gateway.stdio_server"],
        input='{"id":"pp1","method":"pack.plan","params":{"domain":"video_studio","template_id":"video.pipeline"}}\n',
        text=True,
        capture_output=True,
        cwd=PROJECT_ROOT,
        timeout=10,
        check=False,
    )

    assert process.returncode == 0
    payload = json.loads(process.stdout)
    assert payload["id"] == "pp1"
    assert payload["error"] is None
    assert payload["result"]["plan"]["status"] == "planned"
    assert payload["result"]["plan"]["execution_order"] == [
        "brief",
        "script",
        "direction",
        "storyboard",
        "render_manifest",
        "publish_review",
    ]
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
