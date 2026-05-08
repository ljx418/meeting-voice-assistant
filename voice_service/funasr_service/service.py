"""Shared recognition service used by HTTP, CLI, and MCP entrypoints."""

from __future__ import annotations

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import BinaryIO

from pydantic import BaseModel

from funasr_service.model_loader import recognize_audio

logger = logging.getLogger("funasr_service.service")


class SentenceInfo(BaseModel):
    """Recognized sentence with speaker and timing metadata."""

    text: str
    spk: int
    start_time: float
    end_time: float


class RecognizeResponse(BaseModel):
    """Recognition response shared by every public transport."""

    success: bool
    text: str
    sentences: list[SentenceInfo]
    message: str | None = None


def recognize_file_path(file_path: Path) -> RecognizeResponse:
    """Recognize an existing audio file path."""
    return _recognize_from_path(file_path)


def recognize_upload(file_obj: BinaryIO, filename: str) -> RecognizeResponse:
    """Persist an uploaded file temporarily, then recognize it."""
    suffix = Path(filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = file_obj.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    logger.info("[VoiceService] Processing upload: %s, size=%s bytes", filename, len(content))
    try:
        return _recognize_from_path(tmp_path)
    finally:
        _unlink_silent(tmp_path)


def _recognize_from_path(file_path: Path) -> RecognizeResponse:
    wav_path = file_path
    converted = False
    try:
        if file_path.suffix.lower() == ".m4a":
            wav_path = file_path.with_suffix(file_path.suffix + ".wav")
            _convert_m4a_to_wav(file_path, wav_path)
            converted = True

        result = recognize_audio(str(wav_path))
        if not result:
            raise RuntimeError("No recognition result returned")

        return _parse_funasr_result(result[0])
    finally:
        if converted:
            _unlink_silent(wav_path)


def _convert_m4a_to_wav(source: Path, target: Path) -> None:
    logger.info("[VoiceService] Converting m4a to wav: %s", target)
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", str(source), "-ar", "16000", "-ac", "1", str(target)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"m4a conversion failed: {result.stderr}")


def _parse_funasr_result(result: dict) -> RecognizeResponse:
    sentences: list[SentenceInfo] = []
    full_text: list[str] = []
    cumulative_time = 0.0

    for sent in result.get("sentence_info", []):
        start_ts = sent.get("start_time", sent.get("start", 0.0))
        end_ts = sent.get("end_time", sent.get("end", 0.0))

        if start_ts <= 0 and end_ts <= 0:
            start_time = cumulative_time
            end_time = cumulative_time + 3.0
        else:
            start_time = start_ts / 1000.0 if start_ts > 0 else cumulative_time
            end_time = end_ts / 1000.0 if end_ts > 0 else start_time + 3.0
        cumulative_time = end_time

        text = sent.get("text", "")
        sentences.append(
            SentenceInfo(
                text=text,
                spk=sent.get("spk", 0),
                start_time=start_time,
                end_time=end_time,
            )
        )
        full_text.append(text)

    return RecognizeResponse(success=True, text="".join(full_text), sentences=sentences)


def _unlink_silent(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass
    except Exception:
        logger.debug("[VoiceService] Failed to remove temp file: %s", path, exc_info=True)
