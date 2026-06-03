"""Page plan for V2.1 DevWiki."""

from __future__ import annotations

from .model import REQUIRED_PAGE_SLUGS


PAGE_TITLES = {
    "project-overview": "Project Overview",
    "architecture": "Architecture",
    "public-surface": "Public Surface",
    "http-api": "HTTP API",
    "mcp-tools": "MCP Tools",
    "cli": "CLI",
    "storage": "Storage",
    "build-pipeline": "Build Pipeline",
    "developer-onboarding": "Developer Onboarding",
}


def required_pages() -> list[dict[str, str]]:
    return [{"slug": slug, "title": PAGE_TITLES[slug]} for slug in REQUIRED_PAGE_SLUGS]
