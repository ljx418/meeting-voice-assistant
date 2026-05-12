"""Workspace build runtime used by MCP build tools."""

from __future__ import annotations

import threading
import time
import traceback
from pathlib import Path
from typing import Any, Callable

from .mcp_build_tools import TERMINAL_OPERATION_STATUSES
from .mcp_common import envelope, now, read_json, write_json
from .mcp_workspace_runtime import WorkspaceRuntime
from .service import DataService


class BuildCancelled(Exception):
    """Internal sentinel used to stop a build at stage boundaries."""


class BuildRuntime:
    def __init__(self, workspace_runtime: WorkspaceRuntime) -> None:
        self.workspace_runtime = workspace_runtime
        self._workers: set[str] = set()
        self._workers_lock = threading.Lock()

    def operation_envelope(
        self,
        workspace_id: str,
        operation_id: str,
        operation: dict[str, Any],
        *,
        warnings: list[str] | None = None,
        next_actions: list[str] | None = None,
    ) -> dict[str, Any]:
        status = operation.get("status", "queued")
        if next_actions is None:
            next_actions = ["knowledge_build_status"]
            if status not in TERMINAL_OPERATION_STATUSES:
                next_actions.append("knowledge_build_cancel")
        return envelope(
            workspace_id=workspace_id,
            operation_id=operation_id,
            status=status,
            warnings=warnings,
            artifact_refs=operation.get("artifacts", []),
            next_actions=next_actions,
            data=self.operation_payload(operation),
        )

    @staticmethod
    def operation_payload(operation: dict[str, Any]) -> dict[str, Any]:
        return {
            "mode": operation.get("mode"),
            "stage": operation.get("stage"),
            "progress": operation.get("progress", 0.0),
            "error": operation.get("error"),
            "retryable": operation.get("retryable", True),
            "artifacts": operation.get("artifacts", []),
        }

    def ensure_build_worker(self, workspace: Path) -> None:
        key = self._workspace_worker_key(workspace)
        with self._workers_lock:
            if key in self._workers:
                return
            self._workers.add(key)
        self.mark_interrupted_running_operations(workspace)
        threading.Thread(target=self.run_build_queue, args=(workspace,), daemon=True).start()

    def mark_interrupted_running_operations(self, workspace: Path) -> None:
        for operation_file in self.workspace_runtime.operations_dir(workspace).glob("*.json"):
            operation = read_json(operation_file, {})
            if operation.get("status") != "running":
                continue
            self.update_operation(
                workspace,
                str(operation.get("operation_id") or operation_file.stem),
                status="failed",
                stage="failed",
                error={
                    "message": "MCP server stopped while this build was running",
                    "type": "server_interrupted",
                    "retryable": True,
                },
                retryable=True,
            )

    def run_build_queue(self, workspace: Path) -> None:
        try:
            while True:
                operation = self.next_queued_operation(workspace)
                if not operation:
                    return
                operation_id = str(operation.get("operation_id") or "")
                if not operation_id:
                    return
                if operation.get("cancel_requested"):
                    self.update_operation(
                        workspace,
                        operation_id,
                        status="cancelled",
                        stage="cancelled",
                        retryable=False,
                        error=None,
                    )
                    continue
                self.run_build_operation(workspace, operation_id)
                time.sleep(0.01)
        finally:
            with self._workers_lock:
                self._workers.discard(self._workspace_worker_key(workspace))
            if self.next_queued_operation(workspace):
                self.ensure_build_worker(workspace)

    def run_build_operation(self, workspace: Path, operation_id: str) -> None:
        operation = read_json(self.workspace_runtime.operation_path(workspace, operation_id), {})
        mode = operation.get("mode", "full")
        try:
            self.update_operation(workspace, operation_id, status="running", stage="source_import", progress=0.05)
            self.raise_if_cancelled(workspace, operation_id)
            source_paths = self.active_source_paths(workspace)
            self.raise_if_cancelled(workspace, operation_id)
            if not source_paths:
                self.update_operation(
                    workspace,
                    operation_id,
                    status="blocked",
                    stage="failed",
                    progress=0.0,
                    error={"code": "no_active_sources", "message": "No active sources imported for workspace", "stage": "source_import", "retryable": True},
                    retryable=True,
                )
                return

            include_llmwiki = mode in ("full", "incremental", "llmwiki_only")
            include_graphrag = mode in ("full", "incremental", "graph_only")
            service = DataService(workspace)
            plan = service.build_ingest_plan(
                source_paths,
                include_llmwiki=include_llmwiki,
                include_graphrag=include_graphrag,
            )
            service.write_summary_files(plan)
            self.update_operation(workspace, operation_id, stage="distill", progress=0.25)
            self.raise_if_cancelled(workspace, operation_id)
            units = service.build_distilled_units(plan)
            artifacts: list[str] = []
            if include_llmwiki:
                self.update_operation(workspace, operation_id, stage="llmwiki", progress=0.45)
            elif include_graphrag:
                self.update_operation(workspace, operation_id, stage="graphrag", progress=0.45)
            self.raise_if_cancelled(workspace, operation_id)
            results = service.run_default_pipeline(plan, distilled_units=units)
            self.raise_if_cancelled(workspace, operation_id)
            service.write_summary_files(plan)
            for result in results:
                artifacts.extend(str(item) for item in result.artifacts)
            self.update_operation(workspace, operation_id, stage="quality_plan", progress=0.9, artifacts=artifacts)
            self.update_source_ingest_status(workspace, "built")
            self.update_operation(
                workspace,
                operation_id,
                status="completed",
                stage="completed",
                progress=1.0,
                retryable=False,
                artifacts=artifacts,
                results=[
                    {"engine": result.engine, "status": result.status, "meta": result.meta}
                    for result in results
                ],
            )
        except BuildCancelled:
            return
        except Exception as exc:  # pragma: no cover - defensive operation recording
            self.update_source_ingest_status(workspace, "failed")
            self.update_operation(
                workspace,
                operation_id,
                status="failed",
                stage="failed",
                error={
                    "message": str(exc),
                    "type": exc.__class__.__name__,
                    "traceback": traceback.format_exc(limit=6),
                    "retryable": True,
                },
                retryable=True,
            )

    def update_operation(self, workspace: Path, operation_id: str, **updates: Any) -> dict[str, Any]:
        operation_path = self.workspace_runtime.operation_path(workspace, operation_id)
        operation = read_json(operation_path, {})
        operation.update(updates)
        operation["updated_at"] = now()
        write_json(operation_path, operation)
        return operation

    def active_source_paths(self, workspace: Path) -> list[str]:
        manifest = read_json(self.workspace_runtime.sources_manifest_path(workspace), {"items": []})
        paths: list[str] = []
        for item in manifest.get("items", []):
            if item.get("status", "active") != "active":
                continue
            path = item.get("path")
            if path:
                paths.append(str(path))
        return paths

    def update_source_ingest_status(self, workspace: Path, status: str) -> None:
        manifest_path = self.workspace_runtime.sources_manifest_path(workspace)
        manifest = read_json(manifest_path, {"items": []})
        changed = False
        for item in manifest.get("items", []):
            if item.get("status", "active") == "active":
                item["ingest_status"] = status
                item["ingest_updated_at"] = now()
                changed = True
        if changed:
            write_json(manifest_path, manifest)

    def next_queued_operation(self, workspace: Path) -> dict[str, Any] | None:
        operation_files = sorted(
            self.workspace_runtime.operations_dir(workspace).glob("*.json"),
            key=lambda item: (read_json(item, {}).get("created_at", ""), item.name),
        )
        for operation_file in operation_files:
            operation = read_json(operation_file, {})
            if operation.get("status") == "queued":
                return operation
        return None

    def operation_cancel_requested(self, workspace: Path, operation_id: str) -> bool:
        operation = read_json(self.workspace_runtime.operation_path(workspace, operation_id), {})
        return bool(operation.get("cancel_requested")) or operation.get("status") == "cancelled"

    def raise_if_cancelled(self, workspace: Path, operation_id: str) -> None:
        if self.operation_cancel_requested(workspace, operation_id):
            self.update_operation(
                workspace,
                operation_id,
                status="cancelled",
                stage="cancelled",
                retryable=False,
                error=None,
            )
            raise BuildCancelled()

    @staticmethod
    def _workspace_worker_key(workspace: Path) -> str:
        return str(workspace.resolve())
