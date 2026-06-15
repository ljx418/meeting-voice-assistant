"""Architecture source model builder for V2.25 Phase 91."""

from __future__ import annotations

import hashlib
import html
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json, write_json

from ..artifacts import read_jsonl, snapshot_files_path, write_jsonl
from .paths import (
    architecture_intent_diagram_cells_path,
    architecture_intent_source_artifact_refs,
    architecture_intent_source_blocks_path,
    architecture_intent_source_summary_path,
    architecture_intent_sources_path,
)


SCHEMA_VERSION = "v2.25"
MAX_TEXT_BYTES = 1_000_000
MAX_BLOCKS_PER_FILE = 200
MAX_DRAWIO_CELLS_PER_FILE = 500

TEXT_SUFFIXES = {
    ".md",
    ".markdown",
    ".mdx",
    ".drawio",
    ".mmd",
    ".puml",
    ".plantuml",
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".vue",
    ".rs",
    ".go",
    ".java",
    ".kt",
    ".swift",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
}

CODE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".vue", ".rs", ".go", ".java", ".kt", ".swift"}
CONFIG_SUFFIXES = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
MARKDOWN_SUFFIXES = {".md", ".markdown", ".mdx"}
PLANTUML_SUFFIXES = {".puml", ".plantuml"}
EXCLUDED_PARTS = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def build_architecture_source_model(
    *,
    workspace: Path,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    root: Path,
    files: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build and persist the Phase 91 architecture source model."""

    created_at = now()
    records = _candidate_records(workspace, codebase_id, snapshot_id, root, files)
    sources: list[dict[str, Any]] = []
    source_blocks: list[dict[str, Any]] = []
    diagram_cells: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    for record in records:
        rel = _clean_rel(record.get("path"))
        if not rel or _is_excluded(rel):
            continue
        source_type = classify_source_type(rel)
        if source_type == "unknown":
            continue
        path = root / rel
        source_id = stable_id("archsrc", snapshot_id, rel, source_type)
        authority_role, authority_level = classify_authority(rel)
        source = {
            "schema_version": SCHEMA_VERSION,
            "workspace_id": workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "source_id": source_id,
            "source_type": source_type,
            "path": rel,
            "authority_role": authority_role,
            "authority_level": authority_level,
            "phase_hint": phase_hint(rel),
            "version_hint": version_hint(rel),
            "stale_hint": stale_hint(rel),
            "supersedes": [],
            "superseded_by": [],
            "locator": {"path": rel, "line_range": record.get("line_range")},
            "evidence": [{"type": "source_file", "path": rel, "line_range": record.get("line_range"), "extractor": "architecture_intent_source_model"}],
            "confidence": authority_confidence(authority_level, source_type),
            "needs_review": [],
            "created_at": created_at,
        }
        if source_type == "runtime_descriptor":
            source["needs_review"].append({"code": "RUNTIME_DESCRIPTOR_ONLY", "reason": "Registered as runtime descriptor only; not runtime_observed evidence."})
        if not path.exists():
            source["needs_review"].append({"code": "SOURCE_FILE_MISSING", "reason": "Snapshot record exists but file is missing from the current repo checkout."})
            warnings.append({"code": "SOURCE_FILE_MISSING", "path": rel})
        sources.append(source)
        blocks, block_warnings = extract_source_blocks(path, rel, source_id, source_type, workspace_id, codebase_id, snapshot_id)
        cells, cell_warnings = extract_diagram_cells(path, rel, source_id, workspace_id, codebase_id, snapshot_id)
        source_blocks.extend(blocks)
        diagram_cells.extend(cells)
        warnings.extend(block_warnings)
        warnings.extend(cell_warnings)

    sources = sorted(_dedupe(sources, "source_id"), key=lambda item: (item["source_type"], item["path"]))
    source_blocks = sorted(_dedupe(source_blocks, "block_id"), key=lambda item: (item["path"], item.get("line_range") or [0, 0]))
    diagram_cells = sorted(_dedupe(diagram_cells, "cell_id"), key=lambda item: (item["path"], item.get("diagram_page") or "", item.get("raw_cell_id") or ""))
    summary = build_summary(workspace_id, codebase_id, snapshot_id, sources, source_blocks, diagram_cells, warnings, created_at)

    write_jsonl(architecture_intent_sources_path(workspace, codebase_id), sources)
    write_jsonl(architecture_intent_source_blocks_path(workspace, codebase_id), source_blocks)
    write_jsonl(architecture_intent_diagram_cells_path(workspace, codebase_id), diagram_cells)
    write_json(architecture_intent_source_summary_path(workspace, codebase_id), summary)

    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "sources": sources,
        "source_blocks": source_blocks,
        "diagram_cells": diagram_cells,
        "summary": summary,
        "artifact_refs": architecture_intent_source_artifact_refs(codebase_id),
    }


def read_architecture_source_model(*, workspace: Path, codebase_id: str) -> dict[str, Any]:
    summary = read_json(architecture_intent_source_summary_path(workspace, codebase_id), {})
    return {
        "schema_version": summary.get("schema_version", SCHEMA_VERSION),
        "workspace_id": summary.get("workspace_id"),
        "codebase_id": codebase_id,
        "snapshot_id": summary.get("snapshot_id"),
        "sources": read_jsonl(architecture_intent_sources_path(workspace, codebase_id)),
        "source_blocks": read_jsonl(architecture_intent_source_blocks_path(workspace, codebase_id)),
        "diagram_cells": read_jsonl(architecture_intent_diagram_cells_path(workspace, codebase_id)),
        "summary": summary,
        "artifact_refs": architecture_intent_source_artifact_refs(codebase_id),
    }


def classify_source_type(path: str) -> str:
    low = path.lower()
    suffix = Path(path).suffix.lower()
    name = Path(path).name.lower()
    if suffix == ".drawio":
        return "drawio"
    if suffix == ".mmd":
        return "mermaid"
    if suffix in PLANTUML_SUFFIXES:
        return "plantuml"
    if _looks_like_test(low):
        return "test"
    if _looks_like_runtime_descriptor(low) and suffix in CONFIG_SUFFIXES | MARKDOWN_SUFFIXES:
        return "runtime_descriptor"
    if suffix in MARKDOWN_SUFFIXES:
        return "markdown"
    if suffix in CODE_SUFFIXES:
        return "code"
    if suffix in CONFIG_SUFFIXES or name in {"package.json", "pyproject.toml", "tsconfig.json", "vite.config.ts", "requirements.txt"}:
        return "config"
    return "unknown"


def classify_authority(path: str) -> tuple[str, str]:
    low = path.lower()
    if any(part in low for part in ("/history/", "/archive/", "/legacy/", "superseded", "deprecated")):
        return "historical", "historical"
    if any(part in low for part in ("target_architecture", "target-architecture", "target_state", "target-state", "目标架构")):
        return "target", "primary"
    if any(part in low for part in ("prd", "product_requirements")):
        return "target", "primary"
    if any(part in low for part in ("development_plan", "implementation_package", "milestones", "roadmap", "开发计划")):
        return "plan", "supporting"
    if any(part in low for part in ("acceptance", "coverage_matrix", "e2e", "验收")):
        return "acceptance", "supporting"
    if any(part in low for part in ("audit", "review_report", "审计")):
        return "audit", "supporting"
    if classify_source_type(path) in {"code", "config", "test", "runtime_descriptor"}:
        return "implementation", "supporting"
    return "unknown", "weak"


def extract_source_blocks(
    path: Path,
    rel: str,
    source_id: str,
    source_type: str,
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if source_type not in {"markdown", "mermaid", "plantuml", "runtime_descriptor"}:
        return [], []
    text, warning = _read_small_text(path, rel)
    if warning:
        return [], [warning]
    lines = text.splitlines()
    blocks: list[dict[str, Any]] = []
    in_fence = False
    fence_lang = ""
    fence_start = 0
    fence_body: list[str] = []
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_fence:
                in_fence = True
                fence_lang = stripped.strip("`").strip().lower()
                fence_start = idx
                fence_body = []
            else:
                block_type = _fenced_block_type(fence_lang)
                if block_type:
                    blocks.append(_source_block(workspace_id, codebase_id, snapshot_id, source_id, rel, block_type, [fence_start, idx], "\n".join(fence_body)))
                in_fence = False
                fence_lang = ""
                fence_body = []
            continue
        if in_fence:
            fence_body.append(line)
            continue
        if source_type == "markdown":
            if stripped.startswith("#"):
                blocks.append(_source_block(workspace_id, codebase_id, snapshot_id, source_id, rel, "heading", [idx, idx], stripped.lstrip("#").strip()))
            elif re.match(r"^[-*+]\s+", stripped):
                blocks.append(_source_block(workspace_id, codebase_id, snapshot_id, source_id, rel, "bullet", [idx, idx], re.sub(r"^[-*+]\s+", "", stripped).strip()))
            elif re.match(r"^\d+[.)]\s+", stripped):
                blocks.append(_source_block(workspace_id, codebase_id, snapshot_id, source_id, rel, "numbered_item", [idx, idx], re.sub(r"^\d+[.)]\s+", "", stripped).strip()))
            elif stripped.startswith("|") and stripped.endswith("|"):
                blocks.append(_source_block(workspace_id, codebase_id, snapshot_id, source_id, rel, "table_row", [idx, idx], stripped))
        if len(blocks) >= MAX_BLOCKS_PER_FILE:
            blocks.append(_source_block(workspace_id, codebase_id, snapshot_id, source_id, rel, "truncated", [idx, idx], "Source block extraction truncated for large file."))
            break
    if source_type in {"mermaid", "plantuml"} and not blocks:
        blocks.append(_source_block(workspace_id, codebase_id, snapshot_id, source_id, rel, source_type, [1, max(1, len(lines))], text[:4000]))
    return blocks, []


def extract_diagram_cells(path: Path, rel: str, source_id: str, workspace_id: str, codebase_id: str, snapshot_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if Path(rel).suffix.lower() != ".drawio":
        return [], []
    text, warning = _read_small_text(path, rel)
    if warning:
        return [], [warning]
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return [], [{"code": "ARCHITECTURE_DIAGRAM_PARSE_UNSUPPORTED", "path": rel, "reason": f"drawio parse failed: {exc}"}]
    cells: list[dict[str, Any]] = []
    for diagram in root.findall(".//diagram"):
        page_id = diagram.attrib.get("id") or diagram.attrib.get("name") or rel
        page_name = diagram.attrib.get("name") or page_id
        for cell in diagram.findall(".//mxCell"):
            raw_id = cell.attrib.get("id") or ""
            value = _clean_label(cell.attrib.get("value", ""))
            if not value and cell.attrib.get("edge") != "1":
                continue
            cell_kind = "edge" if cell.attrib.get("edge") == "1" else "node" if cell.attrib.get("vertex") == "1" else "cell"
            cells.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "workspace_id": workspace_id,
                    "codebase_id": codebase_id,
                    "snapshot_id": snapshot_id,
                    "cell_id": stable_id("diagramcell", snapshot_id, rel, page_id, raw_id),
                    "source_id": source_id,
                    "path": rel,
                    "diagram_page": page_name,
                    "diagram_page_id": page_id,
                    "raw_cell_id": raw_id,
                    "raw_source": cell.attrib.get("source"),
                    "raw_target": cell.attrib.get("target"),
                    "cell_kind": cell_kind,
                    "label": redact_public_text(value)[:500],
                    "source_type": "drawio",
                    "locator": {"path": rel, "diagram_page": page_name, "cell_id": raw_id},
                    "evidence": [{"type": "diagram_cell", "path": rel, "diagram_page": page_name, "cell_id": raw_id, "extractor": "architecture_intent_source_model"}],
                    "confidence": 0.7 if value else 0.5,
                    "needs_review": [] if value else [{"code": "UNLABELED_DIAGRAM_EDGE", "reason": "Diagram edge has no label; relation semantics require later review."}],
                }
            )
            if len(cells) >= MAX_DRAWIO_CELLS_PER_FILE:
                return cells, [{"code": "DRAWIO_CELL_EXTRACTION_TRUNCATED", "path": rel, "reason": "Too many cells in one drawio file."}]
    return cells, []


def build_summary(
    workspace_id: str,
    codebase_id: str,
    snapshot_id: str,
    sources: list[dict[str, Any]],
    blocks: list[dict[str, Any]],
    cells: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    created_at: str,
) -> dict[str, Any]:
    source_types = Counter(str(row.get("source_type")) for row in sources)
    authority_roles = Counter(str(row.get("authority_role")) for row in sources)
    blockers: list[dict[str, Any]] = list(warnings)
    if source_types.get("drawio", 0) > 0 and not cells:
        blockers.append({"code": "DRAWIO_PRESENT_WITHOUT_CELLS", "reason": "Drawio sources exist but no diagram cells were extracted."})
    if source_types.get("markdown", 0) > 0 and not blocks:
        blockers.append({"code": "MARKDOWN_PRESENT_WITHOUT_BLOCKS", "reason": "Markdown sources exist but no source blocks were extracted."})
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "created_at": created_at,
        "source_count": len(sources),
        "source_block_count": len(blocks),
        "diagram_cell_count": len(cells),
        "source_type_counts": dict(sorted(source_types.items())),
        "authority_role_counts": dict(sorted(authority_roles.items())),
        "blockers": blockers,
        "artifact_refs": architecture_intent_source_artifact_refs(codebase_id),
    }


def _candidate_records(workspace: Path, codebase_id: str, snapshot_id: str, root: Path, files: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    records = files if files is not None else read_jsonl(snapshot_files_path(workspace, codebase_id, snapshot_id))
    result = [record for record in records if record.get("included", True)]
    if result:
        return result
    fallback: list[dict[str, Any]] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if _is_excluded(rel):
            continue
        fallback.append({"path": rel, "line_range": None, "included": True})
    return fallback


def _source_block(workspace_id: str, codebase_id: str, snapshot_id: str, source_id: str, rel: str, block_type: str, line_range: list[int], text: str) -> dict[str, Any]:
    if block_type in {"mermaid", "plantuml"}:
        text = redact_public_text((text or "").strip())
    else:
        text = redact_public_text(re.sub(r"\s+", " ", text or "").strip())
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "block_id": stable_id("srcblock", snapshot_id, rel, block_type, line_range[0], line_range[1], text[:120]),
        "source_id": source_id,
        "path": rel,
        "block_type": block_type,
        "line_range": line_range,
        "text": text[:1000],
        "locator": {"path": rel, "line_range": line_range},
        "evidence": [{"type": "source_block", "path": rel, "line_range": line_range, "extractor": "architecture_intent_source_model"}],
        "confidence": 0.8 if block_type not in {"truncated"} else 0.5,
        "needs_review": [] if block_type != "truncated" else [{"code": "SOURCE_BLOCK_TRUNCATED", "reason": "Large source block extraction was truncated."}],
    }


def _fenced_block_type(lang: str) -> str:
    if "mermaid" in lang:
        return "mermaid"
    if "plantuml" in lang or "puml" in lang:
        return "plantuml"
    return ""


def _read_small_text(path: Path, rel: str) -> tuple[str, dict[str, Any] | None]:
    try:
        if not path.exists():
            return "", {"code": "SOURCE_FILE_MISSING", "path": rel}
        if path.stat().st_size > MAX_TEXT_BYTES:
            return "", {"code": "SOURCE_FILE_TOO_LARGE", "path": rel, "reason": f"File exceeds {MAX_TEXT_BYTES} bytes."}
        return path.read_text(encoding="utf-8", errors="ignore"), None
    except OSError as exc:
        return "", {"code": "SOURCE_FILE_READ_FAILED", "path": rel, "reason": str(exc)}


def _clean_label(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<br\s*/?>", " | ", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def redact_public_text(value: str) -> str:
    """Redact local absolute paths from public source text snippets."""

    value = re.sub(r"/Users/[^`'\"\\s|)]+", "[REDACTED_LOCAL_PATH]", value)
    value = re.sub(r"(?<![A-Za-z0-9_.-])/Users/(?![A-Za-z0-9_.-])", "[REDACTED_LOCAL_PATH]/", value)
    value = re.sub(r"/private/tmp/[^`'\"\\s|)]+", "[REDACTED_LOCAL_PATH]", value)
    value = re.sub(r"(?<![A-Za-z0-9_.-])/private/tmp(?![A-Za-z0-9_.-])", "[REDACTED_LOCAL_PATH]", value)
    value = re.sub(r"/private/var/[^`'\"\\s|)]+", "[REDACTED_LOCAL_PATH]", value)
    value = re.sub(r"(?<![A-Za-z0-9_.-])/private/var(?![A-Za-z0-9_.-])", "[REDACTED_LOCAL_PATH]", value)
    value = re.sub(r"/var/folders/[^`'\"\\s|)]+", "[REDACTED_LOCAL_PATH]", value)
    value = re.sub(r"(?<![A-Za-z0-9_.-])/var/folders(?![A-Za-z0-9_.-])", "[REDACTED_LOCAL_PATH]", value)
    value = re.sub(r"[A-Za-z]:\\\\[^`'\"\\s|)]+", "[REDACTED_LOCAL_PATH]", value)
    return value


def _clean_rel(value: Any) -> str:
    raw = str(value or "")
    if Path(raw).is_absolute() or raw.startswith(("/", "\\")):
        return ""
    rel = raw.replace("\\", "/").lstrip("/")
    parts = [part for part in rel.split("/") if part not in {"", "."}]
    if any(part == ".." for part in parts):
        return ""
    return "/".join(parts)


def _is_excluded(path: str) -> bool:
    parts = set(Path(path).parts)
    return bool(parts & EXCLUDED_PARTS)


def _looks_like_test(low_path: str) -> bool:
    parts = set(Path(low_path).parts)
    name = Path(low_path).name
    return bool(parts & {"tests", "test", "fixtures", "fixture", "__tests__"}) or name.startswith("test_") or name.endswith("_test.py") or ".spec." in name or ".test." in name


def _looks_like_runtime_descriptor(low_path: str) -> bool:
    return any(hint in low_path for hint in ("runtime", "execution", "trace", "run", "evidence"))


def phase_hint(path: str) -> str:
    match = re.search(r"\b[Vv](\d+(?:[._]\d+)*)", path)
    if not match:
        return ""
    return "V" + match.group(1).replace("_", ".")


def version_hint(path: str) -> str:
    value = phase_hint(path)
    return value[1:] if value.startswith("V") else ""


def stale_hint(path: str) -> bool:
    low = path.lower()
    return any(part in low for part in ("/history/", "/archive/", "/legacy/", "superseded", "deprecated"))


def authority_confidence(authority_level: str, source_type: str) -> float:
    if authority_level == "primary":
        return 0.9
    if authority_level == "supporting":
        return 0.8
    if authority_level == "historical":
        return 0.65
    if source_type in {"code", "config", "test"}:
        return 0.75
    return 0.55


def stable_id(prefix: str, *parts: Any) -> str:
    raw = "\x1f".join(str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"


def _dedupe(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for row in rows:
        value = str(row.get(key) or "")
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(row)
    return result
