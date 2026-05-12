"""Standalone-safe graph service exports."""

from .data_service_bridge import (
    materialize_workspace_graph_state,
    query_workspace_graph,
    read_workspace_graph_snapshot,
)
from .data_service_query_model import (
    build_graph_snapshot,
    graph_stats_dict,
    query_graph_db,
)
from .session_graph_service import (
    SESSION_GRAPH_MODEL_VERSION,
    SESSION_RELATION_TYPES,
    SESSION_UNIT_TYPES,
    SessionGraphService,
)
from .session_relation_extractor import SessionRelationExtractor

try:
    from .data_service_runner import run_data_service_execution_request
except Exception as exc:  # pragma: no cover - fallback path for standalone extraction
    def run_data_service_execution_request(request_path):
        raise RuntimeError(
            "GraphRAG delegated execution is unavailable in the standalone build. "
            f"Missing dependency: {exc}"
        )

__all__ = [
    "build_graph_snapshot",
    "graph_stats_dict",
    "materialize_workspace_graph_state",
    "query_graph_db",
    "query_workspace_graph",
    "read_workspace_graph_snapshot",
    "run_data_service_execution_request",
    "SESSION_GRAPH_MODEL_VERSION",
    "SESSION_RELATION_TYPES",
    "SESSION_UNIT_TYPES",
    "SessionGraphService",
    "SessionRelationExtractor",
]
