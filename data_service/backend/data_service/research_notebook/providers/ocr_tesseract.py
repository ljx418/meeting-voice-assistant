"""Local Tesseract OCR provider for ResearchNotebook V2.5."""

from __future__ import annotations

import csv
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from .errors import provider_error


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".pbm", ".pgm", ".ppm"}
PDF_SUFFIXES = {".pdf"}


def tesseract_available() -> bool:
    return shutil.which("tesseract") is not None


def pdftoppm_available() -> bool:
    return shutil.which("pdftoppm") is not None


def pdftotext_available() -> bool:
    return shutil.which("pdftotext") is not None


def tesseract_version() -> str:
    return _tool_version("tesseract", ["tesseract", "--version"])


def pdftoppm_version() -> str:
    return _tool_version("pdftoppm", ["pdftoppm", "-v"])


def pdftotext_version() -> str:
    return _tool_version("pdftotext", ["pdftotext", "-v"])


def pdf_embedded_text_probe(source_path: Path, *, threshold_chars: int = 16) -> dict[str, Any]:
    source_path = Path(source_path)
    if not pdftotext_available():
        return {
            "available": False,
            "tool": "pdftotext",
            "version": "",
            "text_length": None,
            "threshold_chars": threshold_chars,
            "has_embedded_text": None,
            "error": provider_error("PROVIDER_NOT_CONFIGURED", "PDF text probe tool is not available."),
        }
    try:
        process = subprocess.run(
            ["pdftotext", str(source_path), "-"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {
            "available": True,
            "tool": "pdftotext",
            "version": pdftotext_version(),
            "text_length": None,
            "threshold_chars": threshold_chars,
            "has_embedded_text": None,
            "error": provider_error("PROVIDER_EXECUTION_FAILED", "PDF text probe failed."),
        }
    text = " ".join(str(process.stdout or "").split())
    return {
        "available": True,
        "tool": "pdftotext",
        "version": pdftotext_version(),
        "text_length": len(text),
        "threshold_chars": threshold_chars,
        "has_embedded_text": len(text) > threshold_chars,
        "error": None if process.returncode == 0 else provider_error("PROVIDER_BAD_RESPONSE", "PDF text probe returned a non-zero exit code."),
    }


def run_tesseract_ocr(source_path: Path, *, language: str = "eng") -> dict[str, Any]:
    started = time.monotonic()
    source_path = Path(source_path)
    suffix = source_path.suffix.lower()
    if not tesseract_available():
        return _error_result("PROVIDER_NOT_CONFIGURED", "Tesseract executable is not available.")
    if suffix in IMAGE_SUFFIXES:
        pages = [_ocr_image(source_path, page_index=0, language=language)]
        return _ready_result(pages, started, rasterizer="none")
    if suffix in PDF_SUFFIXES:
        embedded_text_probe = pdf_embedded_text_probe(source_path)
        if not pdftoppm_available():
            return _error_result("PDF_RASTERIZER_UNAVAILABLE", "PDF rasterizer is unavailable.", embedded_text_probe=embedded_text_probe)
        with tempfile.TemporaryDirectory(prefix="rn-ocr-") as temp_dir:
            prefix = Path(temp_dir) / "page"
            command = ["pdftoppm", "-png", "-r", "200", str(source_path), str(prefix)]
            process = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
            if process.returncode != 0:
                return _error_result("PDF_RASTERIZER_UNAVAILABLE", "PDF rasterizer failed.", embedded_text_probe=embedded_text_probe)
            image_paths = sorted(Path(temp_dir).glob("page-*.png"))
            if not image_paths:
                return _error_result("PDF_RASTERIZER_UNAVAILABLE", "PDF rasterizer produced no page images.", embedded_text_probe=embedded_text_probe)
            pages = [_ocr_image(path, page_index=index, language=language) for index, path in enumerate(image_paths)]
        return _ready_result(pages, started, rasterizer="pdftoppm", embedded_text_probe=embedded_text_probe)
    return _error_result("PROVIDER_UNSUPPORTED", f"OCR source suffix '{suffix or 'unknown'}' is not supported.")


def _ocr_image(image_path: Path, *, page_index: int, language: str) -> dict[str, Any]:
    command = ["tesseract", str(image_path), "stdout", "-l", language, "--psm", "6", "tsv"]
    process = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
    if process.returncode != 0:
        raise RuntimeError("Tesseract OCR execution failed.")
    blocks = _blocks_from_tsv(process.stdout, page_index=page_index)
    if not blocks:
        text_command = ["tesseract", str(image_path), "stdout", "-l", language, "--psm", "6"]
        text_process = subprocess.run(text_command, capture_output=True, text=True, timeout=30, check=False)
        text = " ".join(str(text_process.stdout or "").split())
        if text:
            blocks = [_block(page_index=page_index, block_index=0, text=text, confidence=0.5, bbox=None)]
    return {"page_index": page_index, "blocks": blocks}


def _blocks_from_tsv(tsv: str, *, page_index: int) -> list[dict[str, Any]]:
    words: list[str] = []
    confidences: list[float] = []
    boxes: list[tuple[int, int, int, int]] = []
    reader = csv.DictReader(tsv.splitlines(), delimiter="\t")
    for row in reader:
        text = str(row.get("text") or "").strip()
        if not text:
            continue
        try:
            conf = float(row.get("conf") or -1)
        except ValueError:
            conf = -1
        if conf < 0:
            continue
        words.append(text)
        confidences.append(max(0.0, min(conf / 100.0, 1.0)))
        try:
            left = int(float(row.get("left") or 0))
            top = int(float(row.get("top") or 0))
            width = int(float(row.get("width") or 0))
            height = int(float(row.get("height") or 0))
            boxes.append((left, top, left + width, top + height))
        except ValueError:
            pass
    if not words:
        return []
    confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return [_block(page_index=page_index, block_index=0, text=" ".join(words), confidence=confidence, bbox=_merge_boxes(boxes))]


def _block(*, page_index: int, block_index: int, text: str, confidence: float, bbox: list[int] | None) -> dict[str, Any]:
    return {
        "block_id": f"p{page_index}_b{block_index}",
        "text": text,
        "confidence": round(float(confidence), 4),
        "confidence_band": _confidence_band(confidence),
        "locator": {
            "page": page_index + 1,
            "block_index": block_index,
            **({"bbox": bbox} if bbox else {}),
        },
    }


def _ready_result(pages: list[dict[str, Any]], started: float, *, rasterizer: str, embedded_text_probe: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "ok": True,
        "status": "ready",
        "provider": {
            "name": "tesseract",
            "kind": "local",
            "version": tesseract_version(),
        },
        "rasterizer": {"name": rasterizer, "version": pdftoppm_version() if rasterizer == "pdftoppm" else None},
        "pages": pages,
        "duration_ms": int((time.monotonic() - started) * 1000),
    }
    if embedded_text_probe is not None:
        payload["embedded_text_probe"] = embedded_text_probe
    return payload


def _error_result(code: str, message: str, *, embedded_text_probe: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "ok": False,
        "status": "unavailable",
        "error": provider_error(code, message),
        "provider": {
            "name": "tesseract",
            "kind": "local",
            "version": tesseract_version() if tesseract_available() else None,
        },
    }
    if embedded_text_probe is not None:
        payload["embedded_text_probe"] = embedded_text_probe
    return payload


def _tool_version(tool: str, command: list[str]) -> str:
    if shutil.which(tool) is None:
        return ""
    try:
        process = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    output = (process.stdout or process.stderr or "").splitlines()
    return output[0].strip() if output else ""


def _merge_boxes(boxes: list[tuple[int, int, int, int]]) -> list[int] | None:
    if not boxes:
        return None
    left = min(item[0] for item in boxes)
    top = min(item[1] for item in boxes)
    right = max(item[2] for item in boxes)
    bottom = max(item[3] for item in boxes)
    return [left, top, right, bottom]


def _confidence_band(confidence: float) -> str:
    if confidence >= 0.8:
        return "high"
    if confidence >= 0.5:
        return "medium"
    return "low"
