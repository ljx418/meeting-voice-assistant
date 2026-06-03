"""Persistence helpers for V2.1 DevWiki artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import (
    devwiki_index_path,
    devwiki_page_json_path,
    devwiki_page_markdown_path,
)


def devwiki_artifact_refs(codebase_id: str, page_slug: str | None = None) -> list[dict[str, str]]:
    if page_slug:
        return [
            {"type": "devwiki_page_json", "artifact_ref": f"devwiki://{codebase_id}/pages/{page_slug}.json"},
            {"type": "devwiki_page_markdown", "artifact_ref": f"devwiki://{codebase_id}/pages/{page_slug}.md"},
        ]
    return [{"type": "devwiki_index", "artifact_ref": f"devwiki://{codebase_id}/index.json"}]


def write_page(workspace: Path, codebase_id: str, page: dict[str, Any], markdown: str) -> None:
    slug = str(page["slug"])
    write_json(devwiki_page_json_path(workspace, codebase_id, slug), page)
    path = devwiki_page_markdown_path(workspace, codebase_id, slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")


def read_page(workspace: Path, codebase_id: str, page_slug: str) -> dict[str, Any]:
    payload = read_json(devwiki_page_json_path(workspace, codebase_id, page_slug), None)
    if not payload:
        raise FileNotFoundError("DEVWIKI_PAGE_NOT_FOUND")
    return payload


def write_index(workspace: Path, codebase_id: str, index: dict[str, Any]) -> None:
    write_json(devwiki_index_path(workspace, codebase_id), index)


def read_index(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(devwiki_index_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("DEVWIKI_NOT_FOUND")
    return payload
