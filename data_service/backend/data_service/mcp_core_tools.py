"""Core ingest and query MCP tool schemas and handlers."""

from __future__ import annotations

from typing import Any, Callable

from .models import QueryMode
from .security import validate_source_paths
from .service import DataService


CORE_TOOL_NAMES = {"knowledge_ingest", "knowledge_query"}

CORE_TOOL_SPECS = [
    {
        "name": "knowledge_ingest",
        "description": "Ingest files once and fan out to llmwiki and graphrag",
        "inputSchema": {
            "type": "object",
            "properties": {
                "paths": {"type": "array", "items": {"type": "string"}},
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
            },
            "required": ["paths"],
        },
    },
    {
        "name": "knowledge_query",
        "description": "Query llmwiki, graphrag, or hybrid mode",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "mode": {"type": "string", "enum": [mode.value for mode in QueryMode]},
                "top_k": {"type": "integer", "default": 8},
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
            },
            "required": ["query"],
        },
    },
]


def handle_core_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    service: DataService,
    bounded_int: Callable[..., int],
) -> dict[str, Any]:
    if name == "knowledge_ingest":
        paths = validate_source_paths(arguments.get("paths") or [], workspace=service.workspace)
        plan = service.build_ingest_plan(paths)
        service.write_summary_files(plan)
        results = service.run_default_pipeline(plan)
        return {
            "workspace": str(service.workspace),
            "results": [
                {"engine": result.engine, "status": result.status, "meta": result.meta}
                for result in results
            ],
        }

    if name == "knowledge_query":
        response = service.query(
            arguments.get("query", ""),
            mode=QueryMode(arguments.get("mode", QueryMode.HYBRID.value)),
            top_k=bounded_int(arguments.get("top_k"), default=8, minimum=1, maximum=50, field="top_k"),
        )
        return {
            "mode": response.mode.value,
            "query": response.query,
            "answer": response.answer,
            "hits": [
                {
                    "title": hit.title,
                    "snippet": hit.snippet,
                    "source": hit.source,
                    "score": hit.score,
                    "meta": hit.meta,
                }
                for hit in response.hits
            ],
            "engine_payloads": response.engine_payloads,
        }

    raise ValueError(f"Unknown core MCP tool: {name}")
