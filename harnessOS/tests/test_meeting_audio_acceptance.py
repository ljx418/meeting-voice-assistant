from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from core.config import get_meeting_mcp_config


def test_phase1_meeting_acceptance_uses_workspace_audio_dir():
    """Phase1 acceptance must process real audio from workspace/音频资料."""
    config = get_meeting_mcp_config()
    audio_dir = Path(os.environ.get("HARNESS_MEETING_MCP_AUDIO_DIR", config.audio_dir)).expanduser().resolve()
    assert audio_dir == Path("/Users/Zhuanz/Desktop/workspace/音频资料")
    assert audio_dir.exists(), f"required acceptance audio directory does not exist: {audio_dir}"

    audio_files = [
        path for path in sorted(audio_dir.iterdir())
        if path.is_file() and path.suffix.lower() in {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4"}
    ]
    assert audio_files, f"no acceptance audio files found in: {audio_dir}"

    async def run():
        service = GatewayService()
        response = await service.handle_rpc(
            RpcRequest(
                id="acceptance",
                method="meeting.process_recording",
                params={
                    "path": str(audio_files[0]),
                    "engine": config.default_engine,
                    "language": config.default_language,
                    "title": audio_files[0].stem,
                },
            )
        )
        assert response.error is None, response.error
        result = response.result or {}
        assert result["source_path"] == str(audio_files[0])
        assert result["transcript_chars"] > 0
        assert result["segment_count"] > 0
        assert result["analysis"]["theme"]
        assert result["minutes_path"]
        assert Path(result["minutes_path"]).exists()
        artifacts = result["artifacts"]
        assert {"transcript", "analysis", "result", "minutes"}.issubset(set(artifacts))
        for path in artifacts.values():
            assert Path(path).exists()

    asyncio.run(run())
