"""Session-scoped knowledge graph support for MCP consumers."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from app.graphrag.service import SESSION_RELATION_TYPES, SESSION_UNIT_TYPES, SessionGraphService, SessionRelationExtractor


SESSION_BUILD_MODES = {"distill", "graph", "communities", "full"}
SESSION_TERMINAL_STATUSES = {"succeeded", "failed", "cancelled", "disposed", "blocked"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_slug(value: object, *, fallback: str = "item", limit: int = 48) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip().lower()).strip("-")
    return text[:limit] or fallback


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp_path, path)


def normalize_workspace_arg(workspace: str | None) -> str | None:
    if str(workspace or "").strip() in {"", "default"}:
        return None
    return workspace


class SessionKnowledgeService:
    """Owns session lifecycle, structured ingestion, and session graph state."""

    def __init__(self, workspace: Path, *, workspace_id: str):
        self.workspace = Path(workspace).resolve()
        self.workspace_id = workspace_id
        self.graph_service = SessionGraphService(workspace_id=workspace_id)
        self.relation_extractor = SessionRelationExtractor()
        self.lifecycle_dir = self.workspace / "lifecycle"
        self.registry_path = self.lifecycle_dir / "sessions.json"
        self.sessions_dir = self.workspace / "sessions"

    def create_session(
        self,
        *,
        external_id: str | None,
        session_type: str = "generic",
        title: str = "",
        ephemeral: bool = False,
        ttl_seconds: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        metadata = dict(metadata or {})
        external_id = str(external_id or metadata.get("meeting_id") or uuid.uuid4().hex).strip()
        if not external_id:
            raise ValueError("external_id is required")
        registry = self._read_registry()
        now = utc_now()
        existing = self._find_by_external_id(registry, external_id)
        if existing and existing.get("status") != "disposed":
            existing.update(
                {
                    "session_type": session_type or existing.get("session_type") or "generic",
                    "title": title or existing.get("title") or external_id,
                    "metadata": {**dict(existing.get("metadata") or {}), **metadata},
                    "updated_at": now,
                }
            )
            self._write_registry(registry)
            self._session_dir(existing["session_id"]).mkdir(parents=True, exist_ok=True)
            return {"session": existing, "created": False}

        digest = hashlib.sha256(external_id.encode("utf-8")).hexdigest()[:16]
        session_id = f"ksess_{digest}"
        if any(item.get("session_id") == session_id for item in registry["items"]):
            session_id = f"ksess_{digest}_{uuid.uuid4().hex[:6]}"
        expires_at = None
        if ephemeral and ttl_seconds:
            expires_at = (datetime.now(timezone.utc) + timedelta(seconds=int(ttl_seconds))).isoformat().replace("+00:00", "Z")
        session = {
            "session_id": session_id,
            "workspace_id": self.workspace_id,
            "external_id": external_id,
            "session_type": session_type or "generic",
            "title": title or external_id,
            "status": "active",
            "ephemeral": bool(ephemeral),
            "ttl_seconds": int(ttl_seconds) if ttl_seconds is not None else None,
            "expires_at": expires_at,
            "metadata": metadata,
            "created_at": now,
            "updated_at": now,
            "closed_at": None,
            "deleted_at": None,
        }
        registry["items"].append(session)
        self._write_registry(registry)
        self._session_dir(session_id).mkdir(parents=True, exist_ok=True)
        return {"session": session, "created": True}

    def get_session(self, session_id: str | None = None, external_id: str | None = None) -> dict[str, Any] | None:
        registry = self._read_registry()
        for session in registry["items"]:
            if session_id and session.get("session_id") == session_id:
                return session
            if external_id and session.get("external_id") == external_id:
                return session
        return None

    def list_sessions(
        self,
        *,
        status: str | None = None,
        session_type: str | None = None,
        include_disposed: bool = False,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        items = []
        for session in sorted(self._read_registry()["items"], key=lambda item: item.get("updated_at", ""), reverse=True):
            if not include_disposed and session.get("status") == "disposed":
                continue
            if status and session.get("status") != status:
                continue
            if session_type and session.get("session_type") != session_type:
                continue
            items.append(session)
            if len(items) >= limit:
                break
        return items

    def close_session(self, session_id: str, *, reopen: bool = False) -> dict[str, Any]:
        session = self._require_session(session_id)
        if session.get("status") == "disposed":
            return session
        now = utc_now()
        if reopen:
            session["status"] = "active"
            session["closed_at"] = None
        else:
            session["status"] = "closed"
            session["closed_at"] = now
        session["updated_at"] = now
        self._replace_session(session)
        return session

    def delete_session(self, session_id: str) -> dict[str, Any]:
        session = self._require_session(session_id)
        session_dir = self._session_dir(session_id)
        if session_dir.exists():
            shutil.rmtree(session_dir)
        now = utc_now()
        session.update({"status": "disposed", "deleted_at": now, "updated_at": now})
        self._replace_session(session)
        return session

    def cleanup_expired_sessions(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        disposed = []
        for session in list(self._read_registry()["items"]):
            expires_at = session.get("expires_at")
            if session.get("status") == "disposed" or not expires_at:
                continue
            try:
                expires = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00"))
            except ValueError:
                continue
            if expires <= now:
                disposed.append(self.delete_session(str(session["session_id"]))["session_id"])
        return {"disposed_session_ids": disposed}

    def ingest(
        self,
        *,
        session_id: str,
        source_type: str,
        content_format: str,
        title: str,
        records: list[dict[str, Any]] | None = None,
        content: Any = None,
        metadata: dict[str, Any] | None = None,
        related_source_ids: list[str] | None = None,
        related_paths: list[str] | None = None,
        auto_link: bool = False,
        allow_closed_write: bool = False,
    ) -> dict[str, Any]:
        session = self._require_writable_session(session_id, allow_closed_write=allow_closed_write)
        content_format = str(content_format or "text")
        if content_format not in {"text", "markdown", "turns", "json"}:
            raise ValueError("content_format must be one of: text, markdown, turns, json")
        metadata = dict(metadata or {})
        normalized_records = self._normalize_records(content_format=content_format, records=records, content=content)
        source_seed = json.dumps(
            {"session_id": session_id, "title": title, "records": normalized_records, "metadata": metadata},
            ensure_ascii=False,
            sort_keys=True,
        ).encode("utf-8")
        source_id = f"src_{hashlib.sha256(source_seed).hexdigest()[:16]}"
        explicit_related_source_ids = [str(item) for item in (related_source_ids or [])]
        if auto_link:
            explicit_related_source_ids.extend(
                self._auto_link_source_ids(
                    session_id=session_id,
                    title=title,
                    records=normalized_records,
                    exclude_source_id=source_id,
                )
            )
            explicit_related_source_ids = list(dict.fromkeys(explicit_related_source_ids))
        source = {
            "source_id": source_id,
            "session_id": session_id,
            "source_type": source_type or "structured",
            "content_format": content_format,
            "title": title or source_id,
            "metadata": {**metadata, "external_id": session.get("external_id")},
            "record_count": len(normalized_records),
            "related_source_ids": explicit_related_source_ids,
            "related_paths": [str(item) for item in (related_paths or [])],
            "auto_link": bool(auto_link),
            "created_at": utc_now(),
        }
        session_dir = self._session_dir(session_id)
        source_path = self._source_path(session_id, source_id)
        write_json(source_path, {"source": source, "records": normalized_records})
        manifest = read_json(session_dir / "sources.json", {"items": []})
        manifest["items"] = [item for item in manifest.get("items", []) if item.get("source_id") != source_id]
        manifest["items"].append(source)
        write_json(session_dir / "sources.json", manifest)
        session["updated_at"] = utc_now()
        self._replace_session(session)
        return {"source": source, "records": normalized_records}

    def start_build(self, *, session_id: str, mode: str = "full") -> dict[str, Any]:
        session = self._require_session(session_id)
        if session.get("status") == "disposed":
            raise ValueError("session is disposed")
        if mode not in SESSION_BUILD_MODES:
            raise ValueError("mode must be one of: communities, distill, full, graph")
        operation_id = f"sop_{uuid.uuid4().hex[:12]}"
        operation = {
            "operation_id": operation_id,
            "workspace_id": self.workspace_id,
            "session_id": session_id,
            "mode": mode,
            "status": "queued",
            "stage": "queued",
            "progress": 0.0,
            "error": None,
            "retryable": True,
            "artifacts": [],
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        write_json(self._operation_path(session_id, operation_id), operation)
        return operation

    def run_build(self, session_id: str, operation_id: str) -> None:
        operation = self.get_operation(session_id, operation_id) or {}
        try:
            if operation.get("cancel_requested"):
                self._update_operation(session_id, operation_id, status="cancelled", stage="cancelled", retryable=False)
                return
            self._update_operation(session_id, operation_id, status="running", stage="distill", progress=0.2)
            units, relations, actors, source_nodes = self._distill_session(session_id)
            artifacts: list[str] = []
            units_path = self._session_dir(session_id) / "distill" / "units.json"
            write_json(units_path, {"items": units, "schema_version": "session-distill-1.0"})
            artifacts.append(str(units_path))
            if operation.get("cancel_requested"):
                self._update_operation(session_id, operation_id, status="cancelled", stage="cancelled", retryable=False)
                return
            self._update_operation(session_id, operation_id, stage="graph", progress=0.55)
            graph = self.graph_service.build_graph(
                session_id=session_id,
                units=units,
                relations=relations,
                actors=actors,
                source_nodes=source_nodes,
            )
            graph_path = self._graph_path(session_id)
            write_json(graph_path, graph)
            artifacts.append(str(graph_path))
            self._update_operation(session_id, operation_id, stage="communities", progress=0.8)
            summary_path = self._session_dir(session_id) / "summary.json"
            write_json(summary_path, self.graph_service.build_session_summary(session_id=session_id, graph=graph))
            artifacts.append(str(summary_path))
            self._update_operation(
                session_id,
                operation_id,
                status="succeeded",
                stage="completed",
                progress=1.0,
                retryable=False,
                artifacts=artifacts,
                results={"unit_count": len(units), "relation_count": len(graph["edges"]), "node_count": len(graph["nodes"])},
            )
        except Exception as exc:  # pragma: no cover - defensive operation recording
            self._update_operation(
                session_id,
                operation_id,
                status="failed",
                stage="failed",
                error={"code": exc.__class__.__name__, "message": str(exc), "retryable": True},
                retryable=True,
            )

    def get_operation(self, session_id: str, operation_id: str) -> dict[str, Any] | None:
        return read_json(self._operation_path(session_id, operation_id), None)

    def cancel_operation(self, session_id: str, operation_id: str, *, reason: str = "") -> dict[str, Any]:
        operation = self.get_operation(session_id, operation_id)
        if not operation:
            raise ValueError(f"Unknown operation_id: {operation_id}")
        if operation.get("status") in SESSION_TERMINAL_STATUSES:
            return operation
        if operation.get("status") == "queued":
            operation.update({"status": "cancelled", "stage": "cancelled", "retryable": False})
        else:
            operation["cancel_requested"] = True
        operation["cancel_reason"] = reason
        operation["updated_at"] = utc_now()
        write_json(self._operation_path(session_id, operation_id), operation)
        return operation

    def graph_snapshot(
        self,
        *,
        scope: str = "session",
        session_id: str | None = None,
        max_nodes: int = 200,
        include_communities: bool = True,
        include_source_refs: bool = True,
        node_types: list[str] | None = None,
    ) -> dict[str, Any]:
        if scope != "session":
            raise ValueError("SessionKnowledgeService only handles scope=session")
        session = self._require_session(str(session_id or ""))
        if session.get("status") == "disposed":
            return self._disposed_payload(session_id=str(session_id or ""))
        graph = self._read_graph(str(session_id or ""))
        if graph is None:
            return self._empty_graph(session_id=str(session_id or ""), status="missing_graph")
        return self.graph_service.snapshot(
            graph,
            session_id=str(session_id or ""),
            max_nodes=max_nodes,
            include_communities=include_communities,
            include_source_refs=include_source_refs,
            node_types=node_types,
        )

    def graph_neighbors(self, *, session_id: str, node_id: str, depth: int = 1, max_nodes: int = 80) -> dict[str, Any]:
        snapshot = self.graph_snapshot(session_id=session_id, max_nodes=1000)
        return self.graph_service.neighbors(snapshot, node_id=node_id, depth=depth, max_nodes=max_nodes)

    def community_summary(self, *, session_id: str, community_id: str | None = None, limit: int = 20) -> dict[str, Any]:
        snapshot = self.graph_snapshot(session_id=session_id, max_nodes=1000)
        return self.graph_service.community_summary(snapshot, community_id=community_id, limit=limit)

    def query_session(
        self,
        *,
        session_id: str,
        query: str,
        top_k: int = 8,
        include_workspace_context: bool = False,
        workspace_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        snapshot = self.graph_snapshot(session_id=session_id, max_nodes=1000)
        return self.graph_service.query_session(
            snapshot,
            query=query,
            top_k=top_k,
            include_workspace_context=include_workspace_context,
            workspace_context=workspace_context,
        )

    def actor_summary(
        self,
        *,
        session_id: str,
        actor_id: str,
        include_units: bool = True,
        unit_types: list[str] | None = None,
    ) -> dict[str, Any]:
        snapshot = self.graph_snapshot(session_id=session_id, max_nodes=1000)
        return self.graph_service.actor_summary(
            snapshot,
            actor_id=actor_id,
            include_units=include_units,
            unit_types=unit_types,
        )

    def _normalize_records(self, *, content_format: str, records: list[dict[str, Any]] | None, content: Any) -> list[dict[str, Any]]:
        if content_format == "turns":
            return [self._normalize_turn(index, item) for index, item in enumerate(records or []) if str((item or {}).get("text") or "").strip()]
        if content_format == "json":
            payload = records if records is not None else content
            if isinstance(payload, list):
                return [
                    {
                        "record_id": str((item or {}).get("record_id") or f"record-{index + 1:04d}"),
                        "text": json.dumps(item, ensure_ascii=False),
                        "metadata": dict((item or {}).get("metadata") or {}),
                    }
                    for index, item in enumerate(payload)
                ]
            return [{"record_id": "record-0001", "text": json.dumps(payload, ensure_ascii=False), "metadata": {}}]
        text = str(content if content is not None else "\n".join(str((item or {}).get("text") or "") for item in records or []))
        return [{"record_id": "record-0001", "text": text, "metadata": {}, "actor_id": None, "actor_label": None, "role": None}]

    def _auto_link_source_ids(
        self,
        *,
        session_id: str,
        title: str,
        records: list[dict[str, Any]],
        exclude_source_id: str,
    ) -> list[str]:
        query_tokens = self._link_tokens(" ".join([str(title or ""), " ".join(str(record.get("text") or "") for record in records)]))
        if not query_tokens:
            return []
        candidates = []
        session_manifest = read_json(self._session_dir(session_id) / "sources.json", {"items": []})
        workspace_manifest = read_json(self.workspace / "lifecycle" / "sources.json", {"items": []})
        for item in list(session_manifest.get("items", [])) + list(workspace_manifest.get("items", [])):
            source_id = str(item.get("source_id") or "")
            if not source_id or source_id == exclude_source_id:
                continue
            candidate_text = " ".join(
                [
                    str(item.get("title") or ""),
                    json.dumps(item.get("metadata", {}), ensure_ascii=False),
                    str(item.get("original_path") or ""),
                ]
            )
            score = len(query_tokens & self._link_tokens(candidate_text))
            if score > 0:
                candidates.append((score, source_id))
        candidates.sort(key=lambda item: (-item[0], item[1]))
        return [source_id for _score, source_id in candidates[:8]]

    @staticmethod
    def _link_tokens(text: str) -> set[str]:
        tokens = set()
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_.+-]{2,}|[\u4e00-\u9fff]{2,8}", text):
            if token not in {"我们", "这个", "需要", "可以", "进行", "项目"}:
                tokens.add(token.lower())
        return tokens

    @staticmethod
    def _normalize_turn(index: int, item: dict[str, Any]) -> dict[str, Any]:
        actor_id = str(item.get("actor_id") or item.get("speaker") or item.get("speaker_id") or f"actor_{index + 1}")
        return {
            "record_id": str(item.get("record_id") or f"turn-{index + 1:04d}"),
            "actor_id": actor_id,
            "actor_label": str(item.get("actor_label") or item.get("speaker_label") or item.get("speaker") or actor_id),
            "role": str(item.get("role") or "speaker"),
            "start_time": item.get("start_time"),
            "end_time": item.get("end_time"),
            "text": str(item.get("text") or "").strip(),
            "metadata": dict(item.get("metadata") or {}),
        }

    def _distill_session(self, session_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        manifest = read_json(self._session_dir(session_id) / "sources.json", {"items": []})
        sources = []
        for source in manifest.get("items", []):
            source_id = source["source_id"]
            payload = read_json(self._source_path(session_id, source_id), {"records": []})
            sources.append({"source": source, "records": payload.get("records", [])})
        return self.relation_extractor.extract(session_id=session_id, sources=sources)

    def _read_registry(self) -> dict[str, Any]:
        payload = read_json(self.registry_path, {"items": []})
        payload.setdefault("items", [])
        return payload

    def _write_registry(self, payload: dict[str, Any]) -> None:
        write_json(self.registry_path, payload)

    @staticmethod
    def _find_by_external_id(registry: dict[str, Any], external_id: str) -> dict[str, Any] | None:
        return next((item for item in registry.get("items", []) if item.get("external_id") == external_id), None)

    def _replace_session(self, session: dict[str, Any]) -> None:
        registry = self._read_registry()
        registry["items"] = [session if item.get("session_id") == session.get("session_id") else item for item in registry["items"]]
        self._write_registry(registry)

    def _require_session(self, session_id: str) -> dict[str, Any]:
        session = self.get_session(session_id=session_id)
        if not session:
            raise ValueError(f"Unknown session_id: {session_id}")
        return session

    def _require_writable_session(self, session_id: str, *, allow_closed_write: bool) -> dict[str, Any]:
        session = self._require_session(session_id)
        if session.get("status") == "disposed":
            raise ValueError("session is disposed")
        if session.get("status") == "closed" and not allow_closed_write:
            raise ValueError("session is closed; pass allow_closed_write=true to write")
        return session

    def _session_dir(self, session_id: str) -> Path:
        return self.sessions_dir / stable_slug(session_id, fallback="session")

    def _source_path(self, session_id: str, source_id: str) -> Path:
        return self._session_dir(session_id) / "sources" / f"{stable_slug(source_id, fallback='source')}.json"

    def _operation_path(self, session_id: str, operation_id: str) -> Path:
        return self._session_dir(session_id) / "operations" / f"{stable_slug(operation_id, fallback='operation')}.json"

    def _graph_path(self, session_id: str) -> Path:
        return self._session_dir(session_id) / "graph" / "graph.json"

    def _read_graph(self, session_id: str) -> dict[str, Any] | None:
        return read_json(self._graph_path(session_id), None)

    def _empty_graph(self, *, session_id: str, status: str) -> dict[str, Any]:
        return {
            "graph_model_version": "session-graph-1.0",
            "workspace_id": self.workspace_id,
            "scope": "session",
            "session_id": session_id,
            "status": status,
            "nodes": [],
            "edges": [],
            "communities": [],
            "stats": self.graph_service.graph_stats([], [], []),
        }

    def _disposed_payload(self, *, session_id: str) -> dict[str, Any]:
        payload = self._empty_graph(session_id=session_id, status="disposed")
        payload["error"] = {"code": "session_disposed", "message": "Session graph has been disposed", "retryable": False}
        return payload

    def _update_operation(self, session_id: str, operation_id: str, **updates: Any) -> dict[str, Any]:
        operation = self.get_operation(session_id, operation_id) or {}
        operation.update(updates)
        operation["updated_at"] = utc_now()
        write_json(self._operation_path(session_id, operation_id), operation)
        return operation
