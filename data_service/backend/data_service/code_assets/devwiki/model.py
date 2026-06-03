"""Data helpers for V2.1 DevWiki pages."""

from __future__ import annotations

from typing import Any


DEVWIKI_SCHEMA_VERSION = "v2.1"
REQUIRED_PAGE_SLUGS = [
    "project-overview",
    "architecture",
    "public-surface",
    "http-api",
    "mcp-tools",
    "cli",
    "storage",
    "build-pipeline",
    "developer-onboarding",
]


def page_id(slug: str) -> str:
    return f"devwiki:{slug}"


def make_section(
    *,
    section_id: str,
    title: str,
    body: str,
    generated_from: str,
    source_artifact_refs: list[dict[str, Any]] | None = None,
    evidence: list[dict[str, Any]] | None = None,
    needs_review: list[dict[str, Any]] | None = None,
    confidence: float = 0.9,
) -> dict[str, Any]:
    return {
        "section_id": section_id,
        "title": title,
        "body": body,
        "generated_from": generated_from,
        "source_artifact_refs": list(source_artifact_refs or []),
        "evidence": list(evidence or []),
        "needs_review": list(needs_review or []),
        "confidence": float(confidence),
    }
