"""Service facade for V2.31 task-aware navigation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json

from ..artifacts import (
    evidence_path,
    imports_path,
    inventory_surfaces_path,
    mappings_path,
    overview_path,
    read_jsonl,
    snapshot_files_path,
    symbols_path,
)
from ..registry import CodebaseRegistry
from ..snapshot import CodebaseSnapshotService
from .navigation_index import build_navigation_index_payload, build_task_query_payload, public_navigation_index_payload, public_task_query_payload
from .impact_analysis import build_impact_payloads, public_impact_payload, public_test_selection_payload
from .handoff import build_handoff_payload, public_handoff_payload
from .handoff_persistence import handoff_artifact_ref, handoff_dir, read_handoff, write_handoff
from .closure_report import build_closure_payloads, public_closure_payload
from .closure_persistence import (
    closure_artifact_refs,
    read_closure_bundle,
    write_closure_bundle,
)
from .impact_persistence import (
    impact_artifact_refs,
    read_impact_bundle,
    write_impact_bundle,
)
from .persistence import (
    read_navigation_index,
    read_task_query,
    task_navigation_artifact_refs,
    task_query_artifact_ref,
    write_navigation_index,
    write_task_query,
)
from .relationship_graph import build_relationship_graph_payload, public_relationship_graph_payload
from .relationship_persistence import (
    read_relationship_bundle,
    relationship_artifact_refs,
    write_relationship_bundle,
)
from .reading_pack import build_reading_pack_payload, public_reading_pack_payload
from .reading_pack_persistence import (
    read_reading_pack,
    reading_pack_artifact_refs,
    write_reading_pack,
)


class CodingAgentNavigationService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)
        self.snapshots = CodebaseSnapshotService(workspace, workspace_id=workspace_id)

    def build_navigation_index(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        files = read_jsonl(snapshot_files_path(self.workspace, codebase_id, resolved_snapshot_id))
        surfaces = read_jsonl(inventory_surfaces_path(self.workspace, codebase_id, resolved_snapshot_id))
        symbols = read_jsonl(symbols_path(self.workspace, codebase_id, resolved_snapshot_id))
        if not files:
            raise FileNotFoundError("SNAPSHOT_FILES_NOT_FOUND")
        if not symbols:
            raise FileNotFoundError("SYMBOLS_NOT_FOUND")
        evidence = []
        try:
            evidence = read_jsonl(evidence_path(self.workspace, codebase_id, resolved_snapshot_id))
        except FileNotFoundError:
            evidence = []
        overview = read_json(overview_path(self.workspace, codebase_id), None)
        payload = build_navigation_index_payload(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            files=files,
            surfaces=surfaces,
            symbols=symbols,
            evidence=evidence,
            overview=overview,
            architecture_report=None,
        )
        if not evidence:
            payload.setdefault("warnings", []).append("EVIDENCE_TRACE_NOT_FOUND")
        write_navigation_index(self.workspace, codebase_id, payload)
        return payload

    def read_navigation_index(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_navigation_index(self.workspace, codebase_id)

    def prepare_task_navigation(self, codebase_id: str, *, task: str, snapshot_id: str | None = None, limit: int = 25) -> dict[str, Any]:
        try:
            index = self.read_navigation_index(codebase_id)
            if snapshot_id and index.get("snapshot_id") != snapshot_id:
                index = self.build_navigation_index(codebase_id, snapshot_id=snapshot_id)
        except FileNotFoundError:
            index = self.build_navigation_index(codebase_id, snapshot_id=snapshot_id)
        payload = build_task_query_payload(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=str(index.get("snapshot_id") or snapshot_id or ""),
            task=task,
            index=index,
            limit=limit,
        )
        write_task_query(self.workspace, codebase_id, payload)
        return payload

    def read_task_query(self, codebase_id: str, task_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_task_query(self.workspace, codebase_id, task_id)

    def build_relationship_graph(self, codebase_id: str, *, snapshot_id: str | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        if asset.status != "active":
            raise ValueError("CODEBASE_NOT_ACTIVE")
        resolved_snapshot_id = snapshot_id or self._latest_snapshot_id(codebase_id)
        self.snapshots.read_snapshot(codebase_id, resolved_snapshot_id)
        surfaces = read_jsonl(inventory_surfaces_path(self.workspace, codebase_id, resolved_snapshot_id))
        symbols = read_jsonl(symbols_path(self.workspace, codebase_id, resolved_snapshot_id))
        imports = read_jsonl(imports_path(self.workspace, codebase_id, resolved_snapshot_id))
        mappings = read_jsonl(mappings_path(self.workspace, codebase_id, resolved_snapshot_id))
        evidence = read_jsonl(evidence_path(self.workspace, codebase_id, resolved_snapshot_id))
        if not symbols:
            raise FileNotFoundError("SYMBOLS_NOT_FOUND")
        try:
            navigation_index = self.read_navigation_index(codebase_id)
            if navigation_index.get("snapshot_id") != resolved_snapshot_id:
                navigation_index = self.build_navigation_index(codebase_id, snapshot_id=resolved_snapshot_id)
        except FileNotFoundError:
            navigation_index = self.build_navigation_index(codebase_id, snapshot_id=resolved_snapshot_id)
        payload = build_relationship_graph_payload(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            repo_root=Path(asset.root_path),
            surfaces=surfaces,
            symbols=symbols,
            imports=imports,
            mappings=mappings,
            evidence=evidence,
            navigation_index=navigation_index,
        )
        write_relationship_bundle(self.workspace, codebase_id, payload)
        return payload

    def read_relationship_graph(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_relationship_bundle(self.workspace, codebase_id)

    def build_impact_analysis(
        self,
        codebase_id: str,
        *,
        task: str | None = None,
        task_id: str | None = None,
        snapshot_id: str | None = None,
        max_items: int = 50,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        self.registry.describe(codebase_id)
        if task_id:
            task_query = self.read_task_query(codebase_id, task_id)
            if snapshot_id and task_query.get("snapshot_id") != snapshot_id:
                raise ValueError("TASK_QUERY_SNAPSHOT_MISMATCH")
        else:
            task_query = self.prepare_task_navigation(codebase_id, task=str(task or ""), snapshot_id=snapshot_id, limit=max_items)
        resolved_snapshot_id = str(task_query.get("snapshot_id") or snapshot_id or "")
        try:
            relationship_graph = self.read_relationship_graph(codebase_id)
            if relationship_graph.get("snapshot_id") != resolved_snapshot_id:
                relationship_graph = self.build_relationship_graph(codebase_id, snapshot_id=resolved_snapshot_id)
        except FileNotFoundError:
            relationship_graph = self.build_relationship_graph(codebase_id, snapshot_id=resolved_snapshot_id)
        impact, test_selection = build_impact_payloads(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            task_query=task_query,
            relationship_graph=relationship_graph,
            max_items=max_items,
        )
        write_impact_bundle(self.workspace, codebase_id, impact, test_selection)
        return impact, test_selection

    def read_impact_analysis(self, codebase_id: str, task_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
        self.registry.describe(codebase_id)
        return read_impact_bundle(self.workspace, codebase_id, task_id)

    def build_reading_pack(
        self,
        codebase_id: str,
        *,
        task: str | None = None,
        task_id: str | None = None,
        snapshot_id: str | None = None,
        max_tokens: int = 12000,
        role: str = "coding_agent",
        max_items: int = 50,
    ) -> tuple[dict[str, Any], str, dict[str, Any]]:
        self.registry.describe(codebase_id)
        if task_id:
            task_query = self.read_task_query(codebase_id, task_id)
            if snapshot_id and task_query.get("snapshot_id") != snapshot_id:
                raise ValueError("TASK_QUERY_SNAPSHOT_MISMATCH")
            try:
                impact, test_selection = self.read_impact_analysis(codebase_id, task_id)
            except FileNotFoundError:
                if not task:
                    raise
                impact, test_selection = self.build_impact_analysis(
                    codebase_id,
                    task=task,
                    task_id=task_id,
                    snapshot_id=snapshot_id,
                    max_items=max_items,
                )
        else:
            task_query = self.prepare_task_navigation(
                codebase_id,
                task=str(task or ""),
                snapshot_id=snapshot_id,
                limit=max_items,
            )
            impact, test_selection = self.build_impact_analysis(
                codebase_id,
                task_id=str(task_query.get("task_id")),
                snapshot_id=str(task_query.get("snapshot_id") or snapshot_id or ""),
                max_items=max_items,
            )
        pack, markdown, ledger = build_reading_pack_payload(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            task_query=task_query,
            impact=impact,
            test_selection=test_selection,
            max_tokens=max_tokens,
            role=role,
        )
        refs = reading_pack_artifact_refs(codebase_id, str(pack.get("pack_id")))
        pack["artifact_refs"] = refs
        ledger["artifact_refs"] = refs
        write_reading_pack(self.workspace, codebase_id, pack, markdown, ledger)
        return pack, markdown, ledger

    def read_reading_pack(self, codebase_id: str, pack_id: str) -> tuple[dict[str, Any], str, dict[str, Any]]:
        self.registry.describe(codebase_id)
        return read_reading_pack(self.workspace, codebase_id, pack_id)

    def build_agent_handoff(
        self,
        codebase_id: str,
        *,
        target_agent: str = "generic",
        pack_id: str | None = None,
        task: str | None = None,
        task_id: str | None = None,
        snapshot_id: str | None = None,
        max_tokens: int = 12000,
        max_items: int = 50,
    ) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        if pack_id:
            reading_pack, _markdown, token_ledger = self.read_reading_pack(codebase_id, pack_id)
        else:
            reading_pack, _markdown, token_ledger = self.build_reading_pack(
                codebase_id,
                task=task,
                task_id=task_id,
                snapshot_id=snapshot_id,
                max_tokens=max_tokens,
                role="coding_agent",
                max_items=max_items,
            )
        resolved_task_id = str(reading_pack.get("task_id") or task_id or "")
        impact, test_selection = self.read_impact_analysis(codebase_id, resolved_task_id)
        payload = build_handoff_payload(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            target_agent=target_agent,
            reading_pack=reading_pack,
            token_ledger=token_ledger,
            impact=impact,
            test_selection=test_selection,
        )
        write_handoff(self.workspace, codebase_id, payload)
        return payload

    def read_agent_handoff(self, codebase_id: str, handoff_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        return read_handoff(self.workspace, codebase_id, handoff_id)

    def build_closure_report(
        self,
        codebase_id: str,
        *,
        handoff_id: str | None = None,
        task: str | None = None,
        task_id: str | None = None,
        snapshot_id: str | None = None,
        max_tokens: int = 12000,
        max_items: int = 50,
    ) -> tuple[dict[str, Any], str, str, dict[str, Any], dict[str, Any], dict[str, Any]]:
        self.registry.describe(codebase_id)
        try:
            navigation_index = self.read_navigation_index(codebase_id)
        except FileNotFoundError:
            navigation_index = self.build_navigation_index(codebase_id, snapshot_id=snapshot_id)
        resolved_snapshot_id = str(navigation_index.get("snapshot_id") or snapshot_id or "")
        try:
            relationship_graph = self.read_relationship_graph(codebase_id)
            if relationship_graph.get("snapshot_id") != resolved_snapshot_id:
                relationship_graph = self.build_relationship_graph(codebase_id, snapshot_id=resolved_snapshot_id)
        except FileNotFoundError:
            relationship_graph = self.build_relationship_graph(codebase_id, snapshot_id=resolved_snapshot_id)
        handoff = self._resolve_handoff(
            codebase_id,
            handoff_id=handoff_id,
            task=task,
            task_id=task_id,
            snapshot_id=resolved_snapshot_id,
            max_tokens=max_tokens,
            max_items=max_items,
        )
        resolved_task_id = str(handoff.get("task_id") or task_id or "")
        impact = None
        test_selection = None
        reading_pack = None
        if resolved_task_id:
            try:
                impact, test_selection = self.read_impact_analysis(codebase_id, resolved_task_id)
            except FileNotFoundError:
                impact, test_selection = None, None
        pack_id = _pack_id_from_handoff(handoff)
        if pack_id:
            try:
                reading_pack, _markdown, _ledger = self.read_reading_pack(codebase_id, pack_id)
            except FileNotFoundError:
                reading_pack = None
        refs = closure_artifact_refs(codebase_id)
        report, html, mermaid, coverage, governance, audit = build_closure_payloads(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            snapshot_id=resolved_snapshot_id,
            navigation_index=navigation_index,
            relationship_graph=relationship_graph,
            impact=impact,
            test_selection=test_selection,
            reading_pack=reading_pack,
            handoff=handoff,
            artifact_refs=refs,
        )
        write_closure_bundle(self.workspace, codebase_id, report, html, mermaid, coverage, governance, audit)
        return report, html, mermaid, coverage, governance, audit

    def read_closure_report(self, codebase_id: str) -> tuple[dict[str, Any], str, str, dict[str, Any], dict[str, Any], dict[str, Any]]:
        self.registry.describe(codebase_id)
        return read_closure_bundle(self.workspace, codebase_id)

    def read_closure_view(self, codebase_id: str, view_id: str) -> dict[str, Any]:
        report, html, mermaid, _coverage, _governance, _audit = self.read_closure_report(codebase_id)
        if view_id == "html":
            return {"view_id": "html", "content_type": "text/html", "content": html, "artifact_refs": closure_artifact_refs(codebase_id)}
        if view_id in {"mermaid", "mmd"}:
            return {"view_id": "mermaid", "content_type": "text/vnd.mermaid", "content": mermaid, "artifact_refs": closure_artifact_refs(codebase_id)}
        raise FileNotFoundError("TASK_NAVIGATION_CLOSURE_VIEW_NOT_FOUND")

    def _resolve_handoff(
        self,
        codebase_id: str,
        *,
        handoff_id: str | None,
        task: str | None,
        task_id: str | None,
        snapshot_id: str | None,
        max_tokens: int,
        max_items: int,
    ) -> dict[str, Any]:
        if handoff_id:
            return self.read_agent_handoff(codebase_id, handoff_id)
        latest = self._latest_handoff_id(codebase_id)
        if latest:
            return self.read_agent_handoff(codebase_id, latest)
        return self.build_agent_handoff(
            codebase_id,
            target_agent="generic",
            task=task,
            task_id=task_id,
            snapshot_id=snapshot_id,
            max_tokens=max_tokens,
            max_items=max_items,
        )

    def _latest_handoff_id(self, codebase_id: str) -> str | None:
        directory = handoff_dir(self.workspace, codebase_id)
        if not directory.exists():
            return None
        files = sorted(directory.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
        return files[0].stem if files else None

    def _latest_snapshot_id(self, codebase_id: str) -> str:
        snapshots = self.snapshots.list_snapshots(codebase_id, limit=1)
        if not snapshots:
            raise FileNotFoundError("SNAPSHOT_NOT_FOUND")
        return str(snapshots[0]["snapshot_id"])


def public_task_navigation_index_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_navigation_index_payload(payload)


def public_task_navigation_query_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_task_query_payload(payload)


def task_navigation_refs(codebase_id: str) -> list[dict[str, str]]:
    return task_navigation_artifact_refs(codebase_id)


def task_query_refs(codebase_id: str, task_id: str) -> list[dict[str, str]]:
    return task_navigation_artifact_refs(codebase_id) + [task_query_artifact_ref(codebase_id, task_id)]


def public_task_relationship_graph_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_relationship_graph_payload(payload)


def task_relationship_refs(codebase_id: str) -> list[dict[str, str]]:
    return relationship_artifact_refs(codebase_id)


def public_task_impact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_impact_payload(payload)


def public_task_test_selection_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_test_selection_payload(payload)


def task_impact_refs(codebase_id: str, task_id: str) -> list[dict[str, str]]:
    return impact_artifact_refs(codebase_id, task_id)


def public_task_reading_pack_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_reading_pack_payload(payload)


def task_reading_pack_refs(codebase_id: str, pack_id: str) -> list[dict[str, str]]:
    return reading_pack_artifact_refs(codebase_id, pack_id)


def public_task_handoff_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_handoff_payload(payload)


def task_handoff_refs(codebase_id: str, handoff_id: str) -> list[dict[str, str]]:
    return [handoff_artifact_ref(codebase_id, handoff_id)]


def public_task_closure_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_closure_payload(payload)


def task_closure_refs(codebase_id: str) -> list[dict[str, str]]:
    return closure_artifact_refs(codebase_id)


def _pack_id_from_handoff(handoff: dict[str, Any]) -> str | None:
    ref = str(handoff.get("reading_pack_ref") or "")
    marker = "/reading_packs/"
    if marker not in ref:
        return None
    tail = ref.split(marker, 1)[1]
    if tail.endswith(".json"):
        tail = tail[:-5]
    return tail or None
