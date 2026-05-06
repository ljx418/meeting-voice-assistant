import json

import pytest


@pytest.mark.asyncio
async def test_funasr_mcp_lists_tools_and_capabilities(monkeypatch, tmp_path):
    monkeypatch.setenv("HARNESS_FUNASR_AUDIO_ROOTS", str(tmp_path))
    from funasr_service import mcp_stdio

    tools = await mcp_stdio.list_tools()
    names = {tool.name for tool in tools}

    assert {"funasr_health", "funasr_recognize_file"}.issubset(names)

    resource = await mcp_stdio.read_resource("funasr://capabilities")
    payload = json.loads(resource.text)
    assert payload["service"] == "funasr"
    assert str(tmp_path.resolve()) in payload["audio_roots"]


@pytest.mark.asyncio
async def test_funasr_mcp_recognize_file_uses_http_proxy(monkeypatch, tmp_path):
    monkeypatch.setenv("HARNESS_FUNASR_AUDIO_ROOTS", str(tmp_path))
    from funasr_service import mcp_stdio

    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"RIFFdemo")

    def fake_request_json(method, url, body, headers):
        assert method == "POST"
        assert url.endswith("/recognize")
        assert b"sample.wav" in body
        assert headers["Content-Type"].startswith("multipart/form-data")
        return {
            "success": True,
            "text": "hello",
            "sentences": [
                {"text": "hello", "spk": 0, "start_time": 0.0, "end_time": 1.5}
            ],
        }

    monkeypatch.setattr(mcp_stdio, "_request_json", fake_request_json)

    content = await mcp_stdio.call_tool("funasr_recognize_file", {"path": str(audio)})
    payload = json.loads(content[0].text)

    assert payload["status"] == "ok"
    assert payload["data"]["text"] == "hello"
    assert payload["data"]["duration"] == 1.5
    assert payload["data"]["source_path"] == str(audio.resolve())


@pytest.mark.asyncio
async def test_funasr_mcp_rejects_disallowed_path(monkeypatch, tmp_path):
    allowed = tmp_path / "allowed"
    blocked = tmp_path / "blocked"
    allowed.mkdir()
    blocked.mkdir()
    audio = blocked / "sample.wav"
    audio.write_bytes(b"RIFFdemo")
    monkeypatch.setenv("HARNESS_FUNASR_AUDIO_ROOTS", str(allowed))

    from funasr_service import mcp_stdio

    response = await mcp_stdio.handle_jsonrpc_request({
        "jsonrpc": "2.0",
        "id": "call",
        "method": "tools/call",
        "params": {
            "name": "funasr_recognize_file",
            "arguments": {"path": str(audio)},
        },
    })

    assert response["error"]["code"] == -32000
    assert "outside allowed roots" in response["error"]["message"]


@pytest.mark.asyncio
async def test_funasr_mcp_jsonrpc_fallback_lists_tools():
    from funasr_service import mcp_stdio

    response = await mcp_stdio.handle_jsonrpc_request({
        "jsonrpc": "2.0",
        "id": "tools",
        "method": "tools/list",
    })

    assert response.get("error") is None
    names = {tool["name"] for tool in response["result"]["tools"]}
    assert "funasr_recognize_file" in names
