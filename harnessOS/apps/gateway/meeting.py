"""Compatibility exports for the Meeting domain pack.

New code should import Meeting workflow and connector primitives from
``packs.meeting``. This module keeps existing Gateway RPC tests and external
imports stable during the pack-boundary migration.
"""

from __future__ import annotations

from packs.meeting.connector import (
    MEETING_MCP_STDIO_LIMIT,
    SUPPORTED_AUDIO_EXTENSIONS,
    MeetingGatewayService,
    MeetingMcpError,
    MeetingMcpJsonRpcClient,
    _compact_transcript_for_analysis,
)
from packs.meeting.workflow import (
    MeetingWorkflow,
    extract_audio_path,
    format_meeting_final_text,
    register_meeting_artifacts,
)

__all__ = [
    "MEETING_MCP_STDIO_LIMIT",
    "SUPPORTED_AUDIO_EXTENSIONS",
    "MeetingGatewayService",
    "MeetingMcpError",
    "MeetingMcpJsonRpcClient",
    "MeetingWorkflow",
    "_compact_transcript_for_analysis",
    "extract_audio_path",
    "format_meeting_final_text",
    "register_meeting_artifacts",
]
