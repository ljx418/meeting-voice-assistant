"""Service layer for V2.1 Code Graph."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json

from ..artifacts import snapshot_files_path
from ..devwiki.persistence import read_index as read_devwiki_index, read_page as read_devwiki_page
from ..inventory import CodebaseInventoryService
from ..overview import CodebaseOverviewService
from ..registry import CodebaseRegistry
from ..snapshot import CodebaseSnapshotService
from ..symbols import CodebaseSymbolIndexService
from ..trace import CodebaseTraceService
from .builder import build_graph_model
from .neighbors import neighbors
from .persistence import graph_artifact_refs, read_graph, read_mermaid, write_graph
from .renderer_mermaid import render_mermaid


class CodeGraphService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(workspace, workspace_id=workspace_id)
        self.inventory = CodebaseInventoryService(workspace, workspace_id=workspace_id)
        self.symbols = CodebaseSymbolIndexService(workspace, workspace_id=workspace_id)
        self.trace = CodebaseTraceService(workspace, workspace_id=workspace_id)
        self.overview = CodebaseOverviewService(workspace, workspace_id=workspace_id)

    def build_graph(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        snapshot = self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = self._read_required_files(codebase_id, resolved_snapshot_id)
        inventory = self._read_required_inventory(codebase_id, resolved_snapshot_id)
        symbols = self._read_required_symbols(codebase_id, resolved_snapshot_id)
        trace = self._read_required_trace(codebase_id, resolved_snapshot_id)
        overview = self._read_required_overview(codebase_id, resolved_snapshot_id)
        devwiki = self._read_required_devwiki(codebase_id, resolved_snapshot_id)
        graph = build_graph_model(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            snapshot=snapshot,
            files=files,
            inventory=inventory,
            symbols=symbols,
            trace=trace,
            devwiki=devwiki,
            created_at=now(),
        )
        graph["artifact_refs"] = graph_artifact_refs(codebase_id)
        mermaid = render_mermaid(graph["nodes"], graph["edges"])
        write_graph(self.workspace, codebase_id, graph, mermaid)
        return graph

    def read_graph(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        graph = read_graph(self.workspace, codebase_id)
        return self._with_stale(codebase_id, graph)

    def read_neighbors(self, codebase_id: str, node_id: str, *, depth: int = 1, limit: int = 100) -> dict[str, Any]:
        graph = self.read_graph(codebase_id)
        payload = neighbors(graph, node_id, depth=depth, limit=limit)
        payload["snapshot_id"] = graph["snapshot_id"]
        payload["stale"] = graph.get("stale", False)
        return payload

    def read_mermaid(self, codebase_id: str) -> dict[str, Any]:
        graph = self.read_graph(codebase_id)
        return {"snapshot_id": graph["snapshot_id"], "stale": graph.get("stale", False), "content": read_mermaid(self.workspace, codebase_id)}

    def _with_stale(self, codebase_id: str, graph: dict[str, Any]) -> dict[str, Any]:
        latest = self._latest_snapshot_id(codebase_id)
        payload = dict(graph)
        payload["stale"] = payload.get("snapshot_id") != latest
        payload["latest_snapshot_id"] = latest
        return payload

    def _read_required_files(self, codebase_id: str, snapshot_id: str) -> list[dict[str, Any]]:
        rows = read_jsonl_path(snapshot_files_path(self.workspace, codebase_id, snapshot_id))
        if not rows:
            raise FileNotFoundError("V20_ARTIFACT_MISSING: files")
        return rows

    def _read_required_inventory(self, codebase_id: str, snapshot_id: str) -> dict[str, Any]:
        try:
            return self.inventory.read_inventory(codebase_id, snapshot_id=snapshot_id)
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"V20_ARTIFACT_MISSING: inventory ({exc})") from exc

    def _read_required_symbols(self, codebase_id: str, snapshot_id: str) -> dict[str, Any]:
        try:
            return self.symbols.read_symbol_index(codebase_id, snapshot_id=snapshot_id)
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"V20_ARTIFACT_MISSING: symbols ({exc})") from exc

    def _read_required_trace(self, codebase_id: str, snapshot_id: str) -> dict[str, Any]:
        try:
            return self.trace.read_trace(codebase_id, snapshot_id=snapshot_id)
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"V20_ARTIFACT_MISSING: trace ({exc})") from exc

    def _read_required_overview(self, codebase_id: str, snapshot_id: str) -> dict[str, Any]:
        payload = read_json(self.workspace / "assets" / "codebase" / codebase_id / "overview.json", None)
        if not payload or payload.get("snapshot_id") != snapshot_id:
            raise FileNotFoundError("V20_ARTIFACT_MISSING: overview")
        return payload

    def _read_required_devwiki(self, codebase_id: str, snapshot_id: str) -> dict[str, Any]:
        try:
            index = read_devwiki_index(self.workspace, codebase_id)
        except FileNotFoundError as exc:
            raise FileNotFoundError("DEVWIKI_NOT_FOUND") from exc
        if index.get("snapshot_id") != snapshot_id:
            raise FileNotFoundError("DEVWIKI_STALE")
        pages = [read_devwiki_page(self.workspace, codebase_id, str(item["slug"])) for item in index.get("pages", [])]
        return {"index": index, "pages": pages, "artifact_refs": index.get("artifact_refs", []), "source_artifact_refs": index.get("source_artifact_refs", [])}

    def _latest_snapshot_id(self, codebase_id: str) -> str:
        snapshots = self.snapshots.list_snapshots(codebase_id, limit=1)
        if not snapshots:
            raise FileNotFoundError("SNAPSHOT_NOT_FOUND")
        return str(snapshots[0]["snapshot_id"])


def public_graph_payload(graph: dict[str, Any]) -> dict[str, Any]:
    return dict(graph)


def public_neighbors_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return dict(payload)


def read_jsonl_path(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    import json

    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows
