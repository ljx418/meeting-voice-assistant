#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 - "$@" <<'PY'
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from apps.gateway.protocol import RpcRequest
from apps.gateway.service import GatewayService
from core.config import get_meeting_mcp_config


AUDIO_SUFFIXES = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4"}
EXPECTED_KINDS = ["transcript", "analysis", "result", "minutes"]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="scripts/e2e_meeting_validation.sh",
        description="Run the user-state Meeting artifact lineage acceptance path.",
    )
    parser.add_argument(
        "audio",
        nargs="?",
        help="Audio file to analyze. Defaults to fixtures/audio_samples/sample_ted_talk.mp3, then HARNESS_MEETING_MCP_AUDIO_DIR.",
    )
    parser.add_argument("--engine", default=None, help="Meeting ASR engine hint.")
    parser.add_argument("--language", default=None, help="Meeting language hint.")
    return parser.parse_args()


def _find_audio(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.exists():
            raise SystemExit(f"Audio file not found: {path}")
        return path

    fixture = Path("fixtures/audio_samples/sample_ted_talk.mp3").resolve()
    if fixture.exists():
        return fixture

    config = get_meeting_mcp_config()
    audio_dir = Path(config.audio_dir).expanduser().resolve()
    if audio_dir.exists():
        files = sorted(
            path for path in audio_dir.iterdir()
            if path.is_file() and path.suffix.lower() in AUDIO_SUFFIXES
        )
        preferred = audio_dir / "TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3"
        if preferred.exists():
            return preferred
        if files:
            return files[0]

    raise SystemExit(
        "No acceptance audio found. Provide a file path, add "
        "fixtures/audio_samples/sample_ted_talk.mp3, or set HARNESS_MEETING_MCP_AUDIO_DIR."
    )


def _artifact_kind_map(lineage: dict) -> dict[str, dict]:
    artifacts = lineage.get("artifacts") or []
    by_kind = {str(item.get("kind")): item for item in artifacts}
    missing = [kind for kind in EXPECTED_KINDS if kind not in by_kind]
    if missing:
        raise AssertionError(f"Missing meeting artifact kinds: {missing}")
    return by_kind


def _assert_meeting_lineage(lineage: dict) -> dict[str, dict]:
    by_kind = _artifact_kind_map(lineage)
    expected_edges = [
        (by_kind["transcript"]["artifact_id"], by_kind["analysis"]["artifact_id"]),
        (by_kind["analysis"]["artifact_id"], by_kind["result"]["artifact_id"]),
        (by_kind["result"]["artifact_id"], by_kind["minutes"]["artifact_id"]),
    ]
    actual_edges = [
        (edge.get("source_artifact_id"), edge.get("target_artifact_id"))
        for edge in lineage.get("edges") or []
    ]
    if actual_edges != expected_edges:
        raise AssertionError(
            "Unexpected meeting lineage edges: "
            f"expected={expected_edges}, actual={actual_edges}"
        )
    if lineage.get("roots") != [by_kind["transcript"]["artifact_id"]]:
        raise AssertionError(f"Unexpected roots: {lineage.get('roots')}")
    if lineage.get("leaves") != [by_kind["minutes"]["artifact_id"]]:
        raise AssertionError(f"Unexpected leaves: {lineage.get('leaves')}")
    return by_kind


async def _rpc(service: GatewayService, request: RpcRequest) -> dict:
    response = await service.handle_rpc(request)
    if response.error is not None:
        raise RuntimeError(response.error.model_dump())
    return response.result or {}


async def _run() -> int:
    args = _parse_args()
    audio = _find_audio(args.audio)
    config = get_meeting_mcp_config()
    engine = args.engine or config.default_engine
    language = args.language or config.default_language

    service = GatewayService()
    await service.initialize({})
    started = await _rpc(service, RpcRequest(id="session", method="session.start"))
    session_id = str(started["session_id"])
    prompt = f"请分析 {audio}，生成会议纪要"

    try:
        turn = await _rpc(
            service,
            RpcRequest(
                id="turn",
                method="turn.start",
                params={
                    "session_id": session_id,
                    "domain": "meeting",
                    "input": prompt,
                    "engine": engine,
                    "language": language,
                },
            ),
        )
        lineage = await _rpc(
            service,
            RpcRequest(
                id="lineage",
                method="artifact.lineage",
                params={"session_id": session_id, "domain": "meeting"},
            ),
        )
        artifacts_by_kind = _assert_meeting_lineage(lineage)
        jobs = await _rpc(
            service,
            RpcRequest(
                id="jobs",
                method="job.list",
                params={"session_id": session_id, "domain": "meeting"},
            ),
        )
    finally:
        await service.session_close({"session_id": session_id})

    summary = {
        "status": "passed",
        "domain": "meeting",
        "audio": str(audio),
        "session_id": session_id,
        "turn_id": turn.get("turn_id"),
        "job_ids": [job.get("job_id") for job in jobs.get("jobs", [])],
        "artifacts": {
            kind: artifacts_by_kind[kind]["artifact_id"]
            for kind in EXPECTED_KINDS
        },
        "lineage": {
            "roots": lineage.get("roots"),
            "leaves": lineage.get("leaves"),
            "edges": lineage.get("edges"),
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(_run()))
    except Exception as exc:
        print(f"Meeting lineage acceptance failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
PY
