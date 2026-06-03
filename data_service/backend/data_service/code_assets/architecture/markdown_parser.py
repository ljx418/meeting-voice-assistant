"""Markdown architecture source parser."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .drawio_parser import classify_label


def parse_markdown(path: Path, rel_path: str) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    nodes: list[dict[str, Any]] = []
    mermaid_blocks: list[dict[str, Any]] = []
    in_mermaid = False
    current: list[str] = []
    start_line = 0
    for lineno, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("```mermaid"):
            in_mermaid = True
            current = []
            start_line = lineno
            continue
        if in_mermaid and line.strip().startswith("```"):
            mermaid_blocks.append({"line_range": [start_line, lineno], "content": "\n".join(current)})
            in_mermaid = False
            continue
        if in_mermaid:
            current.append(line)
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            title = match.group(2).strip()
            nodes.append({"label": title, "level": len(match.group(1)), "line_range": [lineno, lineno], "node_type": classify_label(title)})
    return {"source_type": "markdown", "path": rel_path, "nodes": nodes, "mermaid_blocks": mermaid_blocks}
