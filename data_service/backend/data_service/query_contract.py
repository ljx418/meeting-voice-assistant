"""Shared query contract helpers for MCP, HTTP, and CLI entrypoints."""

from __future__ import annotations

from typing import Any

from .models import QueryMode, QueryResponse
from .service import DataService


QUERY_TOP_K_MIN = 1
QUERY_TOP_K_MAX = 50
QUERY_TOP_K_DEFAULT = 8


def normalize_query_top_k(value: object, *, default: int = QUERY_TOP_K_DEFAULT) -> int:
    try:
        parsed = int(value if value is not None else default)
    except (TypeError, ValueError) as exc:
        raise ValueError("top_k must be an integer") from exc
    if parsed < QUERY_TOP_K_MIN or parsed > QUERY_TOP_K_MAX:
        raise ValueError(f"top_k must be between {QUERY_TOP_K_MIN} and {QUERY_TOP_K_MAX}")
    return parsed


def normalize_query_mode(value: object) -> QueryMode:
    if isinstance(value, QueryMode):
        return value
    return QueryMode(str(value or QueryMode.HYBRID.value))


def query_response_payload(response: QueryResponse) -> dict[str, Any]:
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


def run_query_contract(
    service: DataService,
    query: object,
    *,
    mode: object = QueryMode.HYBRID.value,
    top_k: object = QUERY_TOP_K_DEFAULT,
) -> dict[str, Any]:
    response = service.query(
        str(query or ""),
        mode=normalize_query_mode(mode),
        top_k=normalize_query_top_k(top_k),
    )
    return query_response_payload(response)
