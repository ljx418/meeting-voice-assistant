"""Markdown renderer for V2.1 DevWiki pages."""

from __future__ import annotations

from typing import Any


def render_page_markdown(page: dict[str, Any]) -> str:
    lines = [
        f"# {page['title']}",
        "",
        f"- page_id: `{page['page_id']}`",
        f"- snapshot_id: `{page['snapshot_id']}`",
        f"- stale: `{str(bool(page.get('stale'))).lower()}`",
        f"- confidence: `{page.get('confidence')}`",
        "",
    ]
    for section in page.get("sections", []):
        lines.extend(
            [
                f"## {section['title']}",
                "",
                str(section.get("body") or ""),
                "",
                f"- generated_from: `{section.get('generated_from')}`",
                f"- evidence_count: `{len(section.get('evidence') or [])}`",
                f"- needs_review_count: `{len(section.get('needs_review') or [])}`",
                "",
            ]
        )
        if section.get("evidence"):
            lines.append("Evidence:")
            for item in section.get("evidence", [])[:8]:
                label = item.get("evidence_id") or item.get("artifact_ref") or item.get("path") or item.get("source_file") or item.get("type")
                lines.append(f"- `{label}`")
            lines.append("")
        if section.get("needs_review"):
            lines.append("Needs review:")
            for item in section.get("needs_review", [])[:8]:
                label = item.get("code") or item.get("reason") or item
                lines.append(f"- `{label}`")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
