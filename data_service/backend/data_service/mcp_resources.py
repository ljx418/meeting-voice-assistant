"""MCP resource specs and readers for data_service."""

from __future__ import annotations

import json
from typing import Any

from .service import DataService


RESOURCE_SPECS = [
    {
        "uri": "data-service://summary",
        "name": "Workspace Summary",
        "description": "Current data_service summary for the active workspace",
        "mimeType": "text/markdown",
    },
    {
        "uri": "data-service://layout",
        "name": "Workspace Layout",
        "description": "Artifact layout for row, llmwiki, graphrag, and summary layers",
        "mimeType": "application/json",
    },
]


def read_resource_payload(uri: str, *, service: DataService, layout_payload: Any) -> tuple[str, str]:
    if uri in {"data-service://summary", "data_service://summary"}:
        plan = service.build_ingest_plan([])
        service.write_summary_files(plan)
        return "text/markdown", service.layout.summary_md.read_text(encoding="utf-8")
    if uri in {"data-service://layout", "data_service://layout"}:
        payload = layout_payload(service)
        return "application/json", json.dumps(payload, ensure_ascii=False, indent=2)
    raise ValueError(f"Unknown resource: {uri}")


def canonical_resource_uri(uri: str) -> str:
    if uri == "data_service://summary":
        return "data-service://summary"
    if uri == "data_service://layout":
        return "data-service://layout"
    return uri
