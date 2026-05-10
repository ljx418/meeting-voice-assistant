from __future__ import annotations

from pathlib import Path

from apps.gateway.connectors import ConnectorRegistry
from core.config import FunASRMcpConfig, MeetingMcpConfig
from core.services import CoreAppService
from core.stores import CoreSQLiteStore


def test_meeting_connectors_declare_phase_d_capabilities(tmp_path):
    registry = ConnectorRegistry(
        core_service=CoreAppService(CoreSQLiteStore(tmp_path / "core.sqlite3")),
        meeting_config=MeetingMcpConfig(cwd=str(tmp_path), command="python3", args="-m missing.meeting"),
        funasr_config=FunASRMcpConfig(cwd=str(tmp_path), command="python3", args="-m missing.funasr", execution="stdio"),
    )

    meeting = registry.get_connector("meeting_voice_mcp")
    funasr = registry.get_connector("funasr_mcp")

    assert meeting["domain"] == "meeting"
    assert meeting["execution_mode"] == "stdio"
    assert meeting["app_scope"] == ["meeting"]
    assert {"meeting.analyze", "minutes.generate"} <= set(meeting["capabilities"]["capabilities"])
    assert {"meeting_analyze_text", "meeting_build_minutes"} <= set(meeting["capabilities"]["tools"])
    assert {"audio.transcribe"} <= set(funasr["capabilities"]["capabilities"])
    assert {"funasr_recognize_file"} <= set(funasr["capabilities"]["tools"])


def test_meeting_connector_missing_stdio_path_is_explainable(tmp_path):
    missing = tmp_path / "missing-cwd"
    registry = ConnectorRegistry(
        core_service=CoreAppService(CoreSQLiteStore(tmp_path / "core.sqlite3")),
        meeting_config=MeetingMcpConfig(cwd=str(missing), command="python3", args="-m missing.meeting"),
    )

    health = registry.refresh_health("meeting_voice_mcp")["health"]

    assert health["status"] == "missing_dependency"
    assert "cwd does not exist" in health["message"]
    assert health["details"]["cwd"] == str(Path(missing))
