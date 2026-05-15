from __future__ import annotations

"""PhaseA frozen explicit real-audio acceptance baseline."""

import asyncio
import os
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from core.config import get_meeting_mcp_config


EXPECTED_KINDS = {"transcript", "analysis", "result", "minutes"}


def _preferred_acceptance_audio(audio_dir: Path) -> Path:
    audio_files = [
        path for path in sorted(audio_dir.iterdir())
        if path.is_file() and path.suffix.lower() in {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4"}
    ]
    assert audio_files, f"no acceptance audio files found in: {audio_dir}"
    preferred = os.environ.get("HARNESS_MEETING_ACCEPTANCE_AUDIO_FILE")
    if preferred:
        preferred_path = Path(preferred).expanduser().resolve()
        assert preferred_path.exists(), f"configured acceptance audio file does not exist: {preferred_path}"
        return preferred_path
    return min(audio_files, key=lambda path: path.stat().st_size)


def _require_real_audio_dir() -> Path:
    configured = os.environ.get("HARNESS_MEETING_MCP_AUDIO_DIR")
    if not configured:
        pytest.skip("real audio acceptance requires HARNESS_MEETING_MCP_AUDIO_DIR")
    audio_dir = Path(configured).expanduser().resolve()
    if not audio_dir.exists() or not audio_dir.is_dir():
        pytest.skip(f"real audio acceptance directory does not exist: {audio_dir}")
    return audio_dir


def _artifact_path(value) -> Path:
    if isinstance(value, dict):
        path = value.get("path") or (value.get("record") or {}).get("path")
    else:
        path = value
    assert isinstance(path, str) and path, f"artifact path missing from: {value!r}"
    return Path(path)


async def _approve_and_retry_if_required(service: GatewayService, result: dict) -> dict:
    if not result.get("approval_required"):
        return result
    approval = result.get("approval") or {}
    approval_id = approval.get("approval_id")
    session_id = result.get("gateway_session_id") or approval.get("session_id")
    assert isinstance(approval_id, str) and approval_id
    assert isinstance(session_id, str) and session_id
    approved = await service.handle_rpc(
        RpcRequest(
            id="acceptance-approve",
            method="approval.approve",
            params={
                "approval_id": approval_id,
                "reason": "Explicit real audio acceptance.",
                "scope": {
                    "app_id": approval.get("app_id"),
                    "project_id": approval.get("project_id"),
                    "workspace_id": approval.get("workspace_id"),
                },
            },
        )
    )
    assert approved.error is None, approved.error
    retried = await service.handle_rpc(
        RpcRequest(
            id="acceptance-retry",
            method="turn.retry",
            params={
                "session_id": session_id,
                "approval_id": approval_id,
                "scope": {
                    "app_id": approval.get("app_id"),
                    "project_id": approval.get("project_id"),
                    "workspace_id": approval.get("workspace_id"),
                },
            },
        )
    )
    assert retried.error is None, retried.error
    final_event = (retried.result.get("events") or [{}])[-1]
    assert final_event.get("type") == "turn.completed"
    meeting = final_event.get("data", {}).get("meeting") or {}
    meeting["gateway_session_id"] = session_id
    return meeting


def test_phase1_meeting_acceptance_uses_workspace_audio_dir():
    """PhaseA frozen acceptance must process env-configured real audio."""
    config = get_meeting_mcp_config()
    audio_dir = _require_real_audio_dir()
    audio_file = _preferred_acceptance_audio(audio_dir)

    async def run():
        service = GatewayService()
        response = await service.handle_rpc(
            RpcRequest(
                id="acceptance",
                method="meeting.process_recording",
                params={
                    "path": str(audio_file),
                    "engine": config.default_engine,
                    "language": config.default_language,
                    "title": audio_file.stem,
                },
            )
        )
        assert response.error is None, response.error
        result = await _approve_and_retry_if_required(service, response.result or {})
        assert result["source_path"] == str(audio_file)
        assert result["transcript_chars"] > 0
        assert result["segment_count"] >= 0
        assert result["analysis"]["theme"]
        assert result["minutes_path"]
        assert Path(result["minutes_path"]).exists()
        artifacts = result["artifacts"]
        assert EXPECTED_KINDS.issubset(set(artifacts))
        for artifact in artifacts.values():
            assert _artifact_path(artifact).exists()
        lineage = await service.handle_rpc(
            RpcRequest(
                id="acceptance-lineage",
                method="artifact.lineage",
                params={
                    "session_id": result["gateway_session_id"],
                    "domain": "meeting",
                    "scope": {"app_id": "meeting"},
                },
            )
        )
        assert lineage.error is None, lineage.error
        observed_kinds = {item["kind"] for item in lineage.result["artifacts"]}
        assert EXPECTED_KINDS.issubset(observed_kinds)

    asyncio.run(run())
