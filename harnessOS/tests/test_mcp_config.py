from __future__ import annotations

from pathlib import Path

from core.config import FunASRMcpConfig


def test_funasr_mcp_defaults_prefer_voice_service_python(monkeypatch):
    voice_python = "/Users/Zhuanz/Desktop/workspace/voice_service/.venv/bin/python"
    monkeypatch.delenv("HARNESS_FUNASR_MCP_COMMAND", raising=False)

    original_exists = Path.exists

    def fake_exists(path: Path) -> bool:
        if str(path) == voice_python:
            return True
        return original_exists(path)

    monkeypatch.setattr(Path, "exists", fake_exists)

    config = FunASRMcpConfig()

    assert config.cwd == "/Users/Zhuanz/Desktop/workspace/voice_service"
    assert config.command == voice_python
    assert config.args == "-m funasr_service.mcp_stdio"
