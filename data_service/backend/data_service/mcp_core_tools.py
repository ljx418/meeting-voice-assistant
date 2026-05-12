"""Core ingest and query MCP tool schemas and handlers."""

from __future__ import annotations

from typing import Any, Callable

from .distill_contract import run_distill_contract
from .models import QueryMode
from .query_contract import run_query_contract
from .security import validate_source_paths
from .service import DataService
from .source_trace_contract import source_trace_payload


CORE_TOOL_NAMES = {"knowledge_ingest", "knowledge_query", "knowledge_distill_preview", "knowledge_source_trace"}

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
    {
        "name": "knowledge_distill_preview",
        "description": "Preview distilled source and unit artifacts for a workspace",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "source_id": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
                "kind": {"type": "string"},
                "typed_unit_type": {"type": "string"},
                "min_importance": {"type": "number", "default": 0.0},
                "llm_enriched_only": {"type": "boolean", "default": False},
                "authority": {"type": "string"},
                "min_source_weight": {"type": "number", "default": 0.0},
                "min_source_density": {"type": "number", "default": 0.0},
            },
        },
    },
    {
        "name": "knowledge_source_trace",
        "description": "Trace one source through distill, wiki, and graph artifacts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace": {"type": "string"},
                "workspace_id": {"type": "string"},
                "source_id": {"type": "string"},
                "limit": {"type": "integer", "default": 12},
            },
            "required": ["source_id"],
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
        return run_query_contract(
            service,
            arguments.get("query", ""),
            mode=arguments.get("mode", QueryMode.HYBRID.value),
            top_k=bounded_int(arguments.get("top_k"), default=8, minimum=1, maximum=50, field="top_k"),
        )

    if name == "knowledge_distill_preview":
        return run_distill_contract(
            service,
            source_id=arguments.get("source_id"),
            limit=arguments.get("limit", 20),
            kind=arguments.get("kind"),
            typed_unit_type=arguments.get("typed_unit_type"),
            min_importance=arguments.get("min_importance", 0.0),
            llm_enriched_only=arguments.get("llm_enriched_only", False),
            authority=arguments.get("authority"),
            min_source_weight=arguments.get("min_source_weight", 0.0),
            min_source_density=arguments.get("min_source_density", 0.0),
        )

    if name == "knowledge_source_trace":
        return source_trace_payload(
            service,
            arguments.get("source_id"),
            limit=arguments.get("limit", 12),
        )

    raise ValueError(f"Unknown core MCP tool: {name}")
