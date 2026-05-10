#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON:-$ROOT_DIR/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="${PYTHON:-python3}"
fi

export HARNESS_FUNASR_MCP_EXECUTION="${HARNESS_FUNASR_MCP_EXECUTION:-stdio}"
export HARNESS_FUNASR_MCP_ENDPOINT="${HARNESS_FUNASR_MCP_ENDPOINT:-http://127.0.0.1:8001}"
if [[ -n "${HARNESS_MEETING_E2E_AUDIO_DIR:-}" && -z "${HARNESS_MEETING_MCP_AUDIO_DIR:-}" ]]; then
  export HARNESS_MEETING_MCP_AUDIO_DIR="$HARNESS_MEETING_E2E_AUDIO_DIR"
fi
export HARNESS_FUNASR_MCP_AUDIO_ROOTS="${HARNESS_FUNASR_MCP_AUDIO_ROOTS:-${HARNESS_MEETING_E2E_AUDIO_DIR:-/Users/Zhuanz/Desktop/workspace/音频资料}:/tmp}"
export HARNESS_MEETING_ANALYSIS_TIMEOUT="${HARNESS_MEETING_ANALYSIS_TIMEOUT:-10}"

"$PYTHON_BIN" - "$@" <<'PY'
from __future__ import annotations

import argparse
import asyncio
import json
import os
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
        help="Audio file to analyze. Defaults to fixtures/audio_samples/sample_ted_talk.mp3, then HARNESS_MEETING_E2E_AUDIO_DIR/HARNESS_MEETING_MCP_AUDIO_DIR.",
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

    configured_audio_dir = (
        os.environ.get("HARNESS_MEETING_E2E_AUDIO_DIR")
        or os.environ.get("HARNESS_MEETING_MCP_AUDIO_DIR")
        or get_meeting_mcp_config().audio_dir
    )
    audio_dir = Path(configured_audio_dir).expanduser().resolve()
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
        "fixtures/audio_samples/sample_ted_talk.mp3, or set HARNESS_MEETING_E2E_AUDIO_DIR."
    )


def _artifact_kind_map(lineage: dict) -> dict[str, dict]:
    artifacts = lineage.get("artifacts") or []
    by_kind = {str(item.get("kind")): item for item in artifacts}
    missing = [kind for kind in EXPECTED_KINDS if kind not in by_kind]
    if missing:
        raise AssertionError(
            f"Missing meeting artifact kinds: {missing}; observed={sorted(by_kind)}"
        )
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
    missing_edges = [edge for edge in expected_edges if edge not in actual_edges]
    if missing_edges:
        raise AssertionError(
            "Unexpected meeting lineage edges: "
            f"missing={missing_edges}, actual={actual_edges}"
        )
    roots = lineage.get("roots") or []
    if by_kind["transcript"]["artifact_id"] not in roots:
        raise AssertionError(f"Unexpected roots: {lineage.get('roots')}")
    leaves = lineage.get("leaves") or []
    if by_kind["minutes"]["artifact_id"] not in leaves:
        raise AssertionError(f"Unexpected leaves: {lineage.get('leaves')}")
    return by_kind


def _fallback_reason_from_artifacts(by_kind: dict[str, dict]) -> str | None:
    for item in by_kind.values():
        metadata = item.get("metadata") if isinstance(item, dict) else None
        if isinstance(metadata, dict) and metadata.get("fallback_reason"):
            return str(metadata["fallback_reason"])
    return None


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
    strict = os.environ.get("HARNESS_MEETING_E2E_STRICT", "").strip().lower() in {"1", "true", "yes", "on", "strict"}

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
        completed = (turn.get("events") or [{}])[-1]
        completed_data = completed.get("data") if isinstance(completed, dict) else {}
        if isinstance(completed_data, dict) and completed_data.get("approval_required"):
            approval = completed_data.get("approval") or {}
            approval_id = approval.get("approval_id")
            if not isinstance(approval_id, str) or not approval_id:
                raise RuntimeError("Meeting approval response did not include approval_id")
            await _rpc(
                service,
                RpcRequest(
                    id="approve",
                    method="approval.approve",
                    params={"approval_id": approval_id},
                ),
            )
            turn = await _rpc(
                service,
                RpcRequest(
                    id="retry",
                    method="turn.retry",
                    params={"session_id": session_id, "approval_id": approval_id},
                ),
            )
        final_event = (turn.get("events") or [{}])[-1]
        final_data = final_event.get("data") if isinstance(final_event, dict) else {}
        if isinstance(final_data, dict) and final_event.get("type") == "turn.failed":
            raise RuntimeError(f"Meeting turn failed: {final_data.get('message')}")
        lineage = await _rpc(
            service,
            RpcRequest(
                id="lineage",
                method="artifact.lineage",
                params={"session_id": session_id, "domain": "meeting"},
            ),
        )
        artifacts_by_kind = _assert_meeting_lineage(lineage)
        fallback_reason = _fallback_reason_from_artifacts(artifacts_by_kind)
        if strict and fallback_reason:
            raise AssertionError(f"Strict mode forbids meeting fallback: {fallback_reason}")
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
        "strict": strict,
        "resilience_fallback_reason": fallback_reason,
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
