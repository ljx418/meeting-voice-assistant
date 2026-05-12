"""Session-scoped GraphRAG primitives for Data Service MCP sessions."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any


SESSION_GRAPH_MODEL_VERSION = "session-graph-1.0"
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


class SessionGraphService:
    """Owns session graph materialization and read-side graph operations."""

    def __init__(self, *, workspace_id: str):
        self.workspace_id = workspace_id

    def build_graph(
        self,
        *,
        session_id: str,
        units: list[dict[str, Any]],
        relations: list[dict[str, Any]],
        actors: dict[str, dict[str, Any]],
        source_nodes: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        nodes: dict[str, dict[str, Any]] = {}
        for actor_id, actor in actors.items():
            nodes[f"actor:{actor_id}"] = {
                "id": f"actor:{actor_id}",
                "type": "actor",
                "label": actor["label"],
                "metadata": {"role": actor.get("role")},
            }
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
        for relation in relations:
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
                    "metadata": {"relation_registry": SESSION_GRAPH_MODEL_VERSION},
                }
            )

        node_items = list(nodes.values())
        communities = self._build_communities(session_id=session_id, nodes=node_items, edges=edges)
        return {
            "graph_model_version": SESSION_GRAPH_MODEL_VERSION,
            "workspace_id": self.workspace_id,
            "scope": "session",
            "session_id": session_id,
            "status": "ok",
            "nodes": node_items,
            "edges": edges,
            "communities": communities,
            "stats": self.graph_stats(node_items, edges, communities),
            "relation_types": sorted(SESSION_RELATION_TYPES),
            "unit_types": sorted(SESSION_UNIT_TYPES),
            "updated_at": utc_now(),
        }

    def snapshot(
        self,
        graph: dict[str, Any],
        *,
        session_id: str,
        max_nodes: int = 200,
        include_communities: bool = True,
        include_source_refs: bool = True,
        node_types: list[str] | None = None,
    ) -> dict[str, Any]:
        allowed_types = {str(item) for item in (node_types or []) if item}
        nodes = [node for node in graph.get("nodes", []) if not allowed_types or node.get("type") in allowed_types][:max_nodes]
        node_ids = {node["id"] for node in nodes}
        edges = [edge for edge in graph.get("edges", []) if edge.get("source") in node_ids and edge.get("target") in node_ids]
        if not include_source_refs:
            edges = [{key: value for key, value in edge.items() if key != "source_refs"} for edge in edges]
        communities = graph.get("communities", []) if include_communities else []
        return {
            **graph,
            "workspace_id": self.workspace_id,
            "scope": "session",
            "session_id": session_id,
            "status": "ok",
            "nodes": nodes,
            "edges": edges,
            "communities": communities,
            "stats": self.graph_stats(nodes, edges, communities),
        }

    def neighbors(self, snapshot: dict[str, Any], *, node_id: str, depth: int = 1, max_nodes: int = 80) -> dict[str, Any]:
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
        return {
            **snapshot,
            "root_node_id": node_id,
            "nodes": nodes,
            "edges": edges[: max_nodes * 3],
            "stats": self.graph_stats(nodes, edges, []),
        }

    def community_summary(self, snapshot: dict[str, Any], *, community_id: str | None = None, limit: int = 20) -> dict[str, Any]:
        if snapshot.get("status") != "ok":
            return snapshot
        communities = snapshot.get("communities", [])
        if community_id:
            communities = [item for item in communities if item.get("id") == community_id]
        return {
            "workspace_id": self.workspace_id,
            "scope": "session",
            "session_id": snapshot.get("session_id"),
            "items": communities[:limit],
        }

    def query_session(
        self,
        snapshot: dict[str, Any],
        *,
        query: str,
        top_k: int = 8,
        include_workspace_context: bool = False,
        workspace_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
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
            "session_id": snapshot.get("session_id"),
            "query": query,
            "answer": f"Session graph returned {min(len(hits), top_k)} hits.",
            "hits": hits[:top_k],
            "session_payload": {
                "nodes": snapshot.get("nodes", []),
                "edges": snapshot.get("edges", []),
                "communities": snapshot.get("communities", []),
            },
        }
        if include_workspace_context:
            payload["workspace_context"] = workspace_context or {}
        return payload

    def actor_summary(
        self,
        snapshot: dict[str, Any],
        *,
        actor_id: str,
        include_units: bool = True,
        unit_types: list[str] | None = None,
    ) -> dict[str, Any]:
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
            "session_id": snapshot.get("session_id"),
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

    def build_session_summary(self, *, session_id: str, graph: dict[str, Any]) -> dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "session_id": session_id,
            "stats": graph.get("stats", {}),
            "communities": graph.get("communities", [])[:10],
            "updated_at": utc_now(),
        }

    def _build_communities(self, *, session_id: str, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
    def graph_stats(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], communities: list[dict[str, Any]]) -> dict[str, Any]:
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
