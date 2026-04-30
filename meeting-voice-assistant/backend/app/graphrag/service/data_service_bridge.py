"""Bridge layer exposing graph snapshot/query for data_service workspaces."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .data_service_query_model import (
    GRAPH_QUERY_MODEL_VERSION,
    build_graph_snapshot,
    query_graph_db,
)


def materialize_workspace_graph_state(
    workspace: Path,
    contract_payload: Dict[str, Any],
    *,
    execution_owner: str = "app.graphrag",
) -> Dict[str, Any]:
    """Materialize one compatibility graph state DB for data_service consumers."""
    from .data_service_materializer import GraphCompatMaterializer

    stats = GraphCompatMaterializer.write_compat_state_from_contract(
        workspace,
        contract_payload,
        execution_owner=execution_owner,
    )
    return {
        "source": "app.graphrag.bridge",
        **stats,
    }


def read_workspace_graph_snapshot(workspace: Path, *, max_nodes: int = 120) -> Dict[str, Any]:
    db_path = Path(workspace).resolve() / "graphrag" / "state" / "graphrag.db"
    return build_graph_snapshot(db_path, max_nodes=max_nodes, source_label="app.graphrag.bridge")


def query_workspace_graph(workspace: Path, query_text: str, *, top_k: int = 8) -> Dict[str, Any]:
    db_path = Path(workspace).resolve() / "graphrag" / "state" / "graphrag.db"
    return query_graph_db(db_path, query_text, top_k=top_k, source_label="app.graphrag.bridge")
