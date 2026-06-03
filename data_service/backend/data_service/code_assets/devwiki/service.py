"""Service layer for V2.1 DevWiki artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now, read_json

from ..inventory import CodebaseInventoryService
from ..overview import CodebaseOverviewService, public_overview_payload
from ..registry import CodebaseRegistry
from ..snapshot import CodebaseSnapshotService
from ..symbols import CodebaseSymbolIndexService
from ..trace import CodebaseTraceService
from .builder import build_pages
from .model import DEVWIKI_SCHEMA_VERSION, REQUIRED_PAGE_SLUGS
from .persistence import devwiki_artifact_refs, read_index, read_page, write_index, write_page
from .renderer_markdown import render_page_markdown


class CodebaseDevWikiService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(workspace, workspace_id=workspace_id)
        self.inventory = CodebaseInventoryService(workspace, workspace_id=workspace_id)
        self.symbols = CodebaseSymbolIndexService(workspace, workspace_id=workspace_id)
        self.trace = CodebaseTraceService(workspace, workspace_id=workspace_id)
        self.overview = CodebaseOverviewService(workspace, workspace_id=workspace_id)

    def build_devwiki(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        overview = self._read_required_overview(codebase_id, resolved_snapshot_id)
        inventory = self._read_required_inventory(codebase_id, resolved_snapshot_id)
        symbols = self._read_required_symbols(codebase_id, resolved_snapshot_id)
        trace = self._read_required_trace(codebase_id, resolved_snapshot_id)
        created_at = now()
        pages = build_pages(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            overview=overview,
            inventory=inventory,
            symbols=symbols,
            trace=trace,
            created_at=created_at,
        )
        for page in pages:
            refs = devwiki_artifact_refs(codebase_id, str(page["slug"]))
            page["artifact_refs"] = refs
            write_page(self.workspace, codebase_id, page, render_page_markdown(page))
        index = self._build_index(codebase_id, resolved_snapshot_id, pages, created_at)
        write_index(self.workspace, codebase_id, index)
        return {"index": index, "pages": pages}

    def list_pages(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        index = read_index(self.workspace, codebase_id)
        return self._with_stale_index(codebase_id, index)

    def read_page(self, codebase_id: str, page_slug: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        if page_slug not in REQUIRED_PAGE_SLUGS:
            raise FileNotFoundError("DEVWIKI_PAGE_NOT_FOUND")
        page = read_page(self.workspace, codebase_id, page_slug)
        return self._with_stale_page(codebase_id, page)

    def _build_index(self, codebase_id: str, snapshot_id: str, pages: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
        items = [
            {
                "page_id": page["page_id"],
                "slug": page["slug"],
                "title": page["title"],
                "snapshot_id": page["snapshot_id"],
                "stale": bool(page.get("stale", False)),
                "confidence": page.get("confidence"),
                "evidence_count": len(page.get("evidence") or []),
                "needs_review_count": len(page.get("needs_review") or []),
                "artifact_refs": devwiki_artifact_refs(codebase_id, str(page["slug"])),
            }
            for page in pages
        ]
        return {
            "schema_version": DEVWIKI_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "snapshot_id": snapshot_id,
            "created_at": created_at,
            "updated_at": created_at,
            "page_count": len(items),
            "pages": items,
            "artifact_refs": devwiki_artifact_refs(codebase_id),
            "source_artifact_refs": _source_refs(pages),
        }

    def _with_stale_index(self, codebase_id: str, index: dict[str, Any]) -> dict[str, Any]:
        latest = self._latest_snapshot_id(codebase_id)
        payload = dict(index)
        payload["stale"] = payload.get("snapshot_id") != latest
        payload["latest_snapshot_id"] = latest
        pages = []
        for page in payload.get("pages", []):
            item = dict(page)
            item["stale"] = item.get("snapshot_id") != latest
            pages.append(item)
        payload["pages"] = pages
        return payload

    def _with_stale_page(self, codebase_id: str, page: dict[str, Any]) -> dict[str, Any]:
        latest = self._latest_snapshot_id(codebase_id)
        payload = dict(page)
        payload["stale"] = payload.get("snapshot_id") != latest
        payload["latest_snapshot_id"] = latest
        return payload

    def _read_required_overview(self, codebase_id: str, snapshot_id: str) -> dict[str, Any]:
        payload = read_json(self.workspace / "assets" / "codebase" / codebase_id / "overview.json", None)
        if not payload or payload.get("snapshot_id") != snapshot_id:
            raise FileNotFoundError("V20_ARTIFACT_MISSING: overview")
        return public_overview_payload(payload)

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

    def _latest_snapshot_id(self, codebase_id: str) -> str:
        snapshots = self.snapshots.list_snapshots(codebase_id, limit=1)
        if not snapshots:
            raise FileNotFoundError("SNAPSHOT_NOT_FOUND")
        return str(snapshots[0]["snapshot_id"])


def public_devwiki_index_payload(index: dict[str, Any]) -> dict[str, Any]:
    return dict(index)


def public_devwiki_page_payload(page: dict[str, Any]) -> dict[str, Any]:
    return dict(page)


def _source_refs(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    refs = []
    for page in pages:
        for ref in page.get("source_artifact_refs", []):
            key = (str(ref.get("type")), str(ref.get("artifact_ref")))
            if key in seen:
                continue
            seen.add(key)
            refs.append(dict(ref))
    return refs
