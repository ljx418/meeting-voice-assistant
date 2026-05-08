"""Session-scoped knowledge graph support for MCP consumers."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SESSION_BUILD_MODES = {"distill", "graph", "communities", "full"}
SESSION_TERMINAL_STATUSES = {"succeeded", "failed", "cancelled", "disposed", "blocked"}
SESSION_UNIT_TYPES = {
    "statement",
    "question",
    "decision",
    "task",
    "risk",
    "issue",
    "requirement",
    "fact",
    "evidence",
    "summary",
    "topic",
    "entity",
}
SESSION_RELATION_TYPES = {
    "actor_made_statement",
    "actor_asked_question",
    "actor_proposed_decision",
    "actor_accepted_task",
    "actor_raised_risk",
    "unit_about_topic",
    "unit_mentions_entity",
    "unit_supported_by_evidence",
    "unit_related_to_source",
    "source_related_to_source",
    "topic_related_to_topic",
    "entity_co_occurs",
}


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
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_workspace_arg(workspace: str | None) -> str | None:
    if str(workspace or "").strip() in {"", "default"}:
        return None
    return workspace


class SessionKnowledgeService:
    """Owns session lifecycle, structured ingestion, and session graph state."""

    def __init__(self, workspace: Path, *, workspace_id: str):
        self.workspace = Path(workspace).resolve()
        self.workspace_id = workspace_id
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
            graph = self._build_graph(session_id, units, relations, actors, source_nodes)
            graph_path = self._graph_path(session_id)
            write_json(graph_path, graph)
            artifacts.append(str(graph_path))
            self._update_operation(session_id, operation_id, stage="communities", progress=0.8)
            summary_path = self._session_dir(session_id) / "summary.json"
            write_json(summary_path, self._build_session_summary(session_id, graph))
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
        allowed_types = {str(item) for item in (node_types or []) if item}
        nodes = [node for node in graph.get("nodes", []) if not allowed_types or node.get("type") in allowed_types][:max_nodes]
        node_ids = {node["id"] for node in nodes}
        edges = [edge for edge in graph.get("edges", []) if edge.get("source") in node_ids and edge.get("target") in node_ids]
        if not include_source_refs:
            edges = [{key: value for key, value in edge.items() if key != "source_refs"} for edge in edges]
        return {
            **graph,
            "workspace_id": self.workspace_id,
            "scope": "session",
            "session_id": session_id,
            "status": "ok",
            "nodes": nodes,
            "edges": edges,
            "communities": graph.get("communities", []) if include_communities else [],
            "stats": self._graph_stats(nodes, edges, graph.get("communities", [])),
        }

    def graph_neighbors(self, *, session_id: str, node_id: str, depth: int = 1, max_nodes: int = 80) -> dict[str, Any]:
        snapshot = self.graph_snapshot(session_id=session_id, max_nodes=1000)
        if snapshot.get("status") != "ok":
            return snapshot
        depth = max(1, min(int(depth), 3))
        frontier = {node_id}
        visited = {node_id}
        edges = []
        for _ in range(depth):
            next_frontier = set()
            for edge in snapshot.get("edges", []):
                if edge["source"] in frontier or edge["target"] in frontier:
                    edges.append(edge)
                    next_frontier.add(edge["source"])
                    next_frontier.add(edge["target"])
            next_frontier -= visited
            visited |= next_frontier
            frontier = next_frontier
        visited = set(list(visited)[:max_nodes])
        nodes = [node for node in snapshot.get("nodes", []) if node.get("id") in visited]
        return {**snapshot, "root_node_id": node_id, "nodes": nodes, "edges": edges[: max_nodes * 3], "stats": self._graph_stats(nodes, edges, [])}

    def community_summary(self, *, session_id: str, community_id: str | None = None, limit: int = 20) -> dict[str, Any]:
        snapshot = self.graph_snapshot(session_id=session_id, max_nodes=1000)
        if snapshot.get("status") != "ok":
            return snapshot
        communities = snapshot.get("communities", [])
        if community_id:
            communities = [item for item in communities if item.get("id") == community_id]
        return {"workspace_id": self.workspace_id, "scope": "session", "session_id": session_id, "items": communities[:limit]}

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
        if snapshot.get("status") != "ok":
            return snapshot
        query_l = str(query or "").lower()
        hits = []
        for node in snapshot.get("nodes", []):
            haystack = " ".join([str(node.get("label", "")), json.dumps(node.get("metadata", {}), ensure_ascii=False)]).lower()
            if query_l and query_l not in haystack:
                continue
            hits.append(
                {
                    "title": node.get("label"),
                    "snippet": node.get("metadata", {}).get("text") or node.get("label"),
                    "source": node.get("id"),
                    "score": 1.0,
                    "kind": node.get("type"),
                    "source_refs": node.get("source_refs", []),
                }
            )
        if not hits:
            for edge in snapshot.get("edges", []):
                haystack = json.dumps(edge, ensure_ascii=False).lower()
                if query_l in haystack:
                    hits.append(
                        {
                            "title": edge.get("type"),
                            "snippet": f"{edge.get('source')} -> {edge.get('target')}",
                            "source": edge.get("id"),
                            "score": float(edge.get("weight", 0.5)),
                            "kind": "relation",
                            "source_refs": edge.get("source_refs", []),
                        }
                    )
        payload = {
            "workspace_id": self.workspace_id,
            "scope": "session",
            "session_id": session_id,
            "query": query,
            "answer": f"Session graph returned {min(len(hits), top_k)} hits.",
            "hits": hits[:top_k],
            "session_payload": {"nodes": snapshot.get("nodes", []), "edges": snapshot.get("edges", []), "communities": snapshot.get("communities", [])},
        }
        if include_workspace_context:
            payload["workspace_context"] = workspace_context or {}
        return payload

    def actor_summary(
        self,
        *,
        session_id: str,
        actor_id: str,
        include_units: bool = True,
        unit_types: list[str] | None = None,
    ) -> dict[str, Any]:
        snapshot = self.graph_snapshot(session_id=session_id, max_nodes=1000)
        if snapshot.get("status") != "ok":
            return snapshot
        actor_node_id = f"actor:{actor_id}"
        actor = next((node for node in snapshot.get("nodes", []) if node.get("id") == actor_node_id), None)
        allowed = {str(item) for item in unit_types or []}
        buckets = {key: [] for key in ["statements", "decisions", "tasks", "risks", "questions"]}
        topics = []
        source_refs = []
        unit_by_id = {node["id"]: node for node in snapshot.get("nodes", []) if node.get("type") == "unit"}
        for edge in snapshot.get("edges", []):
            if edge.get("source") != actor_node_id or not str(edge.get("target", "")).startswith("unit:"):
                continue
            unit = unit_by_id.get(edge["target"])
            if not unit:
                continue
            unit_type = unit.get("metadata", {}).get("unit_type", "statement")
            if allowed and unit_type not in allowed:
                continue
            item = {
                "unit_id": unit["id"].replace("unit:", "", 1),
                "unit_type": unit_type,
                "text": unit.get("metadata", {}).get("text") or unit.get("label"),
                "source_refs": unit.get("source_refs", []),
            }
            if unit_type == "decision":
                buckets["decisions"].append(item)
            elif unit_type == "task":
                buckets["tasks"].append(item)
            elif unit_type == "risk":
                buckets["risks"].append(item)
            elif unit_type == "question":
                buckets["questions"].append(item)
            else:
                buckets["statements"].append(item)
            source_refs.extend(item["source_refs"])
        for edge in snapshot.get("edges", []):
            if not edge.get("source", "").startswith("unit:"):
                continue
            if edge.get("type") == "unit_about_topic" and edge.get("source") in unit_by_id:
                topic = next((node for node in snapshot.get("nodes", []) if node.get("id") == edge.get("target")), None)
                if topic and topic.get("label") not in topics:
                    topics.append(topic.get("label"))
        label = actor.get("label") if actor else actor_id
        unit_count = sum(len(items) for items in buckets.values())
        result = {
            "workspace_id": self.workspace_id,
            "scope": "session",
            "session_id": session_id,
            "actor": {"actor_id": actor_id, "label": label, "metadata": (actor or {}).get("metadata", {})},
            "summary": f"{label} has {unit_count} relevant units in this session.",
            "topics": topics[:10],
            **buckets,
            "source_refs": self._dedupe_dicts(source_refs),
        }
        if not include_units:
            for key in buckets:
                result[key] = []
        return result

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
        units = []
        relations = []
        actors: dict[str, dict[str, Any]] = {}
        source_nodes: dict[str, dict[str, Any]] = {}
        for source in manifest.get("items", []):
            source_id = source["source_id"]
            source_nodes[source_id] = source
            payload = read_json(self._source_path(session_id, source_id), {"records": []})
            for record in payload.get("records", []):
                text = str(record.get("text") or "").strip()
                if not text:
                    continue
                actor_id = record.get("actor_id")
                if actor_id:
                    actors[str(actor_id)] = {
                        "actor_id": str(actor_id),
                        "label": str(record.get("actor_label") or actor_id),
                        "role": str(record.get("role") or ""),
                    }
                unit_type = self._classify_unit(text)
                unit_id = f"unit_{hashlib.sha256((source_id + record.get('record_id', '') + text).encode('utf-8')).hexdigest()[:16]}"
                topics = self._extract_topics(text)
                entities = self._extract_entities(text, actors)
                source_refs = [{"source_id": source_id, "record_id": record.get("record_id"), "start_time": record.get("start_time"), "end_time": record.get("end_time")}]
                unit = {
                    "unit_id": unit_id,
                    "session_id": session_id,
                    "unit_type": unit_type,
                    "text": text,
                    "actors": ([{"actor_id": str(actor_id), "role": self._actor_relation_role(unit_type)}] if actor_id else []),
                    "source_refs": source_refs,
                    "topics": topics,
                    "entities": entities,
                    "confidence": self._unit_confidence(unit_type),
                    "metadata": {"record_id": record.get("record_id"), "source_type": source.get("source_type")},
                }
                units.append(unit)
                if actor_id:
                    relations.append(self._relation_for_actor(unit_type, str(actor_id), unit_id, source_refs))
                relations.append({"source": f"unit:{unit_id}", "target": f"source:{source_id}", "type": "unit_related_to_source", "weight": 1.0, "source_refs": source_refs})
                for topic in topics:
                    relations.append({"source": f"unit:{unit_id}", "target": f"topic:{stable_slug(topic, fallback='topic')}", "type": "unit_about_topic", "weight": 0.8, "source_refs": source_refs, "label": topic})
                for entity in entities:
                    relations.append({"source": f"unit:{unit_id}", "target": f"entity:{stable_slug(entity, fallback='entity')}", "type": "unit_mentions_entity", "weight": 0.72, "source_refs": source_refs, "label": entity})
                for left, right in self._pairwise(entities):
                    relations.append(
                        {
                            "source": f"entity:{stable_slug(left, fallback='entity')}",
                            "target": f"entity:{stable_slug(right, fallback='entity')}",
                            "type": "entity_co_occurs",
                            "weight": 0.45,
                            "source_refs": source_refs,
                        }
                    )
            for related_source_id in source.get("related_source_ids", []):
                relations.append(
                    {
                        "source": f"source:{source_id}",
                        "target": f"source:{related_source_id}",
                        "type": "source_related_to_source",
                        "weight": 0.6,
                        "source_refs": [{"source_id": source_id}],
                    }
                )
        return units, relations, actors, source_nodes

    def _build_graph(
        self,
        session_id: str,
        units: list[dict[str, Any]],
        relations: list[dict[str, Any]],
        actors: dict[str, dict[str, Any]],
        source_nodes: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        nodes: dict[str, dict[str, Any]] = {}
        for actor_id, actor in actors.items():
            nodes[f"actor:{actor_id}"] = {"id": f"actor:{actor_id}", "type": "actor", "label": actor["label"], "metadata": {"role": actor.get("role")}}
        for source_id, source in source_nodes.items():
            nodes[f"source:{source_id}"] = {
                "id": f"source:{source_id}",
                "type": "source",
                "label": source.get("title") or source_id,
                "metadata": {"source_type": source.get("source_type"), "content_format": source.get("content_format")},
            }
        for unit in units:
            nodes[f"unit:{unit['unit_id']}"] = {
                "id": f"unit:{unit['unit_id']}",
                "type": "unit",
                "label": unit["text"][:80],
                "metadata": {"unit_type": unit["unit_type"], "text": unit["text"], "confidence": unit["confidence"]},
                "source_refs": unit["source_refs"],
            }
            for topic in unit.get("topics", []):
                node_id = f"topic:{stable_slug(topic, fallback='topic')}"
                nodes.setdefault(node_id, {"id": node_id, "type": "topic", "label": topic, "metadata": {}})
            for entity in unit.get("entities", []):
                node_id = f"entity:{stable_slug(entity, fallback='entity')}"
                nodes.setdefault(node_id, {"id": node_id, "type": "entity", "label": entity, "metadata": {}})
        edges = []
        seen_edges = set()
        for index, relation in enumerate(relations):
            source = relation["source"]
            target = relation["target"]
            if source not in nodes or target not in nodes:
                continue
            key = (source, target, relation["type"], json.dumps(relation.get("source_refs", []), sort_keys=True))
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edges.append(
                {
                    "id": f"edge_{len(edges) + 1}",
                    "source": source,
                    "target": target,
                    "type": relation["type"],
                    "relation": relation["type"],
                    "label": relation["type"],
                    "weight": float(relation.get("weight", 0.5)),
                    "source_refs": relation.get("source_refs", []),
                    "metadata": {"relation_registry": "session-graph-1.0"},
                }
            )
        communities = self._build_communities(session_id, list(nodes.values()), edges)
        return {
            "graph_model_version": "session-graph-1.0",
            "workspace_id": self.workspace_id,
            "scope": "session",
            "session_id": session_id,
            "status": "ok",
            "nodes": list(nodes.values()),
            "edges": edges,
            "communities": communities,
            "stats": self._graph_stats(list(nodes.values()), edges, communities),
            "relation_types": sorted(SESSION_RELATION_TYPES),
            "unit_types": sorted(SESSION_UNIT_TYPES),
            "updated_at": utc_now(),
        }

    def _build_communities(self, session_id: str, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
        node_by_id = {node["id"]: node for node in nodes}
        topic_edges = defaultdict(list)
        for edge in edges:
            if edge.get("type") == "unit_about_topic":
                topic_edges[edge["target"]].append(edge)
        communities = []
        for topic_id, connected_edges in topic_edges.items():
            topic = node_by_id.get(topic_id)
            if not topic:
                continue
            node_ids = [topic_id] + [edge["source"] for edge in connected_edges]
            actor_ids = []
            for edge in edges:
                if edge.get("target") in node_ids and edge.get("source", "").startswith("actor:"):
                    actor_ids.append(edge["source"])
            node_ids.extend(actor_ids)
            node_ids = list(dict.fromkeys(node_ids))
            communities.append(
                {
                    "id": f"comm_{session_id}_{stable_slug(topic.get('label'), fallback='topic')}",
                    "title": str(topic.get("label") or "Session Topic"),
                    "summary": self._community_summary_text(topic.get("label"), node_ids, node_by_id, edges, len(connected_edges)),
                    "node_ids": node_ids,
                    "entity_ids": node_ids,
                    "score": float(len(connected_edges)),
                    "entity_count": len(node_ids),
                    "relationship_count": len(connected_edges),
                }
            )
        if not communities and nodes:
            node_ids = [node["id"] for node in nodes[:12]]
            communities.append(
                {
                    "id": f"comm_{session_id}_overview",
                    "title": "会议全局脉络",
                    "summary": self._community_summary_text("会议全局脉络", node_ids, node_by_id, edges, len(node_ids)),
                    "node_ids": node_ids,
                    "entity_ids": node_ids,
                    "score": float(len(node_ids)),
                    "entity_count": len(node_ids),
                    "relationship_count": len(edges),
                }
            )
        return communities

    @staticmethod
    def _community_summary_text(label: Any, node_ids: list[str], node_by_id: dict[str, dict[str, Any]], edges: list[dict[str, Any]], unit_count: int) -> str:
        actors = []
        units = []
        entities = []
        for node_id in node_ids:
            node = node_by_id.get(node_id) or {}
            node_type = node.get("type")
            if node_type == "actor":
                actors.append(str(node.get("label") or node_id.replace("actor:", "")))
            elif node_type == "unit":
                text = str((node.get("metadata") or {}).get("text") or node.get("label") or "").strip()
                if text:
                    units.append(text)
            elif node_type == "entity":
                entities.append(str(node.get("label") or node_id.replace("entity:", "")))
        actors = list(dict.fromkeys(actors))[:5]
        entities = list(dict.fromkeys(entities))[:5]
        lead = f"围绕“{label or '会议主题'}”，该社区汇聚 {len(actors)} 位说话人、{unit_count} 个会议知识单元和 {len(edges)} 条关系。"
        actor_text = f"核心发言人包括 {', '.join(actors)}。" if actors else ""
        entity_text = f"高频关联对象包括 {', '.join(entities)}。" if entities else ""
        if units:
            sample = "；".join(units[:2])
            return f"{lead}{actor_text}{entity_text}代表性内容：{sample}"
        return f"{lead}{actor_text}{entity_text}".strip()

    def _build_session_summary(self, session_id: str, graph: dict[str, Any]) -> dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "session_id": session_id,
            "stats": graph.get("stats", {}),
            "communities": graph.get("communities", [])[:10],
            "updated_at": utc_now(),
        }

    @staticmethod
    def _classify_unit(text: str) -> str:
        lowered = text.lower()
        if "?" in text or "？" in text or any(token in text for token in ["吗", "如何", "怎么", "是否"]):
            return "question"
        if any(token in text for token in ["决定", "确认", "定为", "通过", "验收"]):
            return "decision"
        if any(token in text for token in ["负责", "完成", "跟进", "推进", "提交", "整理"]):
            return "task"
        if any(token in text for token in ["风险", "担心", "阻塞", "延期", "问题", "失败"]):
            return "risk"
        if any(token in lowered for token in ["must", "require", "requirement"]) or any(token in text for token in ["必须", "需要"]):
            return "requirement"
        if re.search(r"\d{4}|\d+月|\d+日|下周|今天|明天|昨天", text):
            return "fact"
        return "statement"

    @staticmethod
    def _actor_relation_role(unit_type: str) -> str:
        return {
            "decision": "proposer",
            "task": "assignee",
            "risk": "raiser",
            "question": "asker",
        }.get(unit_type, "speaker")

    @staticmethod
    def _unit_confidence(unit_type: str) -> float:
        return 0.82 if unit_type in {"question", "decision", "task", "risk"} else 0.68

    @staticmethod
    def _relation_for_actor(unit_type: str, actor_id: str, unit_id: str, source_refs: list[dict[str, Any]]) -> dict[str, Any]:
        relation_type = {
            "question": "actor_asked_question",
            "decision": "actor_proposed_decision",
            "task": "actor_accepted_task",
            "risk": "actor_raised_risk",
        }.get(unit_type, "actor_made_statement")
        return {"source": f"actor:{actor_id}", "target": f"unit:{unit_id}", "type": relation_type, "weight": 0.91, "source_refs": source_refs}

    @staticmethod
    def _extract_topics(text: str) -> list[str]:
        candidates = []
        for token in ["发布计划", "最终验收", "验收", "测试", "风险", "任务", "需求", "预算", "客户", "排期"]:
            if token in text:
                candidates.append(token)
        if not candidates:
            cn = re.findall(r"[\u4e00-\u9fff]{2,6}", text)
            candidates.extend(cn[:2])
        return list(dict.fromkeys(candidates))[:5]

    @staticmethod
    def _extract_entities(text: str, actors: dict[str, dict[str, Any]]) -> list[str]:
        entities = []
        for actor in actors.values():
            label = str(actor.get("label") or "")
            if label and label in text:
                entities.append(label)
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_.+-]{1,}|[\u4e00-\u9fff]{2,8}", text):
            if token not in {"我们", "这个", "下周一", "今天", "明天"}:
                entities.append(token)
        return list(dict.fromkeys(entities))[:8]

    @staticmethod
    def _pairwise(items: list[str]) -> list[tuple[str, str]]:
        pairs = []
        for index, left in enumerate(items):
            for right in items[index + 1:]:
                if left != right:
                    pairs.append((left, right))
        return pairs

    @staticmethod
    def _dedupe_dicts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result = []
        seen = set()
        for item in items:
            key = json.dumps(item, ensure_ascii=False, sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
        return result

    @staticmethod
    def _graph_stats(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], communities: list[dict[str, Any]]) -> dict[str, Any]:
        counts = Counter(node.get("type") for node in nodes)
        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "community_count": len(communities),
            "actor_count": counts.get("actor", 0),
            "unit_count": counts.get("unit", 0),
            "topic_count": counts.get("topic", 0),
            "entity_count": counts.get("entity", 0),
            "source_count": counts.get("source", 0),
        }

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
            "stats": self._graph_stats([], [], []),
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
