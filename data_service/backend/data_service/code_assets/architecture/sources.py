"""Architecture source discovery for V2.3."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..artifacts import read_jsonl, snapshot_files_path
from .drawio_parser import parse_drawio
from .markdown_parser import parse_markdown
from .model import architecture_source


ARCHITECTURE_SOURCE_EXTENSIONS = {".drawio", ".mmd", ".md", ".markdown"}
ARCHITECTURE_PATH_HINTS = ("architecture", "arch", "design", "prd", "drawio", "gap", "target", "baseline")
MAX_MARKDOWN_SOURCES = 80


def discover_architecture_sources(*, workspace: Path, workspace_id: str, codebase_id: str, snapshot_id: str, root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records = read_jsonl(snapshot_files_path(workspace, codebase_id, snapshot_id))
    sources: list[dict[str, Any]] = []
    parsed: list[dict[str, Any]] = []
    seen: set[str] = set()
    markdown_count = 0
    for rel, record in _candidate_records(root, records):
        if not _is_architecture_candidate(rel):
            continue
        if rel in seen:
            continue
        if _source_type(rel) == "markdown":
            if not _is_high_value_markdown(rel) or markdown_count >= MAX_MARKDOWN_SOURCES:
                continue
            markdown_count += 1
        seen.add(rel)
        source_type = _source_type(rel)
        path = root / rel
        evidence = [{"type": "source_file", "path": rel, "line_range": record.get("line_range"), "extractor": "architecture_source_index"}]
        source = architecture_source(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=snapshot_id, path=rel, source_type=source_type, parser=_parser_name(source_type), evidence=evidence, confidence=0.9)
        sources.append(source)
        try:
            payload = parse_drawio(path, rel) if source_type == "drawio" else parse_markdown(path, rel) if source_type in {"markdown", "mermaid"} else {"source_type": source_type, "path": rel, "nodes": []}
            payload["source_id"] = source["source_id"]
            parsed.append(payload)
        except ValueError as exc:
            source["needs_review"] = [{"code": "ARCHITECTURE_SOURCE_PARSE_FAILED", "reason": str(exc)}]
    return sources, parsed


def _candidate_records(root: Path, records: list[dict[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    result = [(str(record.get("path") or ""), record) for record in records if record.get("included")]
    known = {path for path, _record in result}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in known or _is_excluded(rel):
            continue
        if _is_architecture_candidate(rel):
            result.append((rel, {"path": rel, "line_range": None}))
    return result


def _is_excluded(path: str) -> bool:
    parts = set(Path(path).parts)
    return bool(parts & {".git", ".venv", "node_modules", "dist", "build", "__pycache__", ".pytest_cache", ".harnessos", ".openharness"})


def _is_architecture_candidate(path: str) -> bool:
    low = path.lower()
    suffix = Path(path).suffix.lower()
    if suffix not in ARCHITECTURE_SOURCE_EXTENSIONS:
        return False
    if suffix == ".drawio":
        return True
    return any(hint in low for hint in ARCHITECTURE_PATH_HINTS) or low in {"readme.md", "agents.md", "claude.md"}


def _is_high_value_markdown(path: str) -> bool:
    low = path.lower()
    name = Path(path).name.lower()
    if name in {"readme.md", "agents.md"}:
        return True
    high_value_names = ("prd", "architecture", "target", "baseline", "current-gap", "gap_analysis", "development_plan", "acceptance_plan")
    return any(part in name for part in high_value_names) and ("docs/" in low or low.startswith("docs"))


def _source_type(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".drawio":
        return "drawio"
    if suffix == ".mmd":
        return "mermaid"
    return "markdown"


def _parser_name(source_type: str) -> str:
    return {"drawio": "drawio_mxcell", "markdown": "markdown_headings", "mermaid": "mermaid_text"}.get(source_type, "architecture_source")
