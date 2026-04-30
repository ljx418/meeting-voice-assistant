"""Shared graph query-model builders for data_service workspaces."""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional


GRAPH_QUERY_MODEL_VERSION = "1.0"


def build_graph_snapshot(db_path: Path, *, max_nodes: int = 120, source_label: str) -> Dict[str, Any]:
    db_path = Path(db_path)
    if not db_path.exists():
        return {
            "graph_model_version": GRAPH_QUERY_MODEL_VERSION,
            "nodes": [],
            "edges": [],
            "communities": [],
            "stats": graph_stats_dict(0, 0, 0, 0, 0),
            "db_path": str(db_path),
            "source": source_label,
        }

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        entity_rows = conn.execute(
            """
            SELECT entity_id AS node_id, name, occurrence_count AS raw_count,
                   weighted_occurrence_count AS weighted_count,
                   document_count, 'entity' AS node_type
            FROM entities
            ORDER BY weighted_occurrence_count DESC, document_count DESC, name ASC
            LIMIT ?
            """,
            (max(10, int(max_nodes * 0.7)),),
        ).fetchall()
        theme_rows = conn.execute(
            """
            SELECT theme_id AS node_id, label AS name, weighted_score AS weighted_count,
                   source_count AS document_count, source_count AS raw_count, 'theme' AS node_type
            FROM themes
            ORDER BY weighted_score DESC, source_count DESC, label ASC
            LIMIT ?
            """,
            (max(6, int(max_nodes * 0.35)),),
        ).fetchall()
        node_rows = list(theme_rows) + list(entity_rows)
        node_ids = [row["node_id"] for row in node_rows]
        relationship_rows: List[sqlite3.Row] = []
        if node_ids:
            placeholders = ", ".join("?" for _ in node_ids)
            candidate_relationship_rows = conn.execute(
                f"""
                WITH node_names AS (
                    SELECT entity_id AS node_id, name, 'entity' AS node_type FROM entities
                    UNION ALL
                    SELECT theme_id AS node_id, label AS name, 'theme' AS node_type FROM themes
                )
                SELECT r.relationship_id, r.relation_type, r.weight,
                       r.source_node_id, r.target_node_id,
                       r.source_node_kind, r.target_node_kind,
                       sn.name AS source_name, tn.name AS target_name
                FROM relationships r
                JOIN node_names sn ON sn.node_id = r.source_node_id
                JOIN node_names tn ON tn.node_id = r.target_node_id
                WHERE r.source_node_id IN ({placeholders})
                   OR r.target_node_id IN ({placeholders})
                ORDER BY r.weight DESC
                LIMIT ?
                """,
                (*node_ids, *node_ids, max_nodes * 6),
            ).fetchall()
            node_id_set = set(node_ids)
            relationship_rows = [
                row
                for row in candidate_relationship_rows
                if row["source_node_id"] in node_id_set and row["target_node_id"] in node_id_set
            ]
        document_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        theme_count = conn.execute("SELECT COUNT(*) FROM themes").fetchone()[0]

    node_lookup = {row["node_id"]: row for row in node_rows}
    communities = build_theme_communities(node_lookup, relationship_rows)
    community_by_node = {
        entity_id: community["id"]
        for community in communities
        for entity_id in community["entity_ids"]
    }
    return {
        "graph_model_version": GRAPH_QUERY_MODEL_VERSION,
        "nodes": [graph_node_dict(row, community_by_node.get(row["node_id"])) for row in node_rows],
        "edges": [graph_edge_dict(row) for row in relationship_rows],
        "communities": [graph_community_dict(item) for item in communities],
        "stats": graph_stats_dict(
            len(entity_rows),
            theme_count,
            len(relationship_rows),
            len(communities),
            document_count,
        ),
        "db_path": str(db_path),
        "source": source_label,
    }


def query_graph_db(db_path: Path, query_text: str, *, top_k: int, source_label: str) -> Dict[str, Any]:
    db_path = Path(db_path)
    if not db_path.exists():
        return {
            "status": "missing_db",
            "db_path": str(db_path),
            "graph_model_version": GRAPH_QUERY_MODEL_VERSION,
            "nodes": [],
            "edges": [],
            "communities": [],
            "hits": [],
            "stats": graph_stats_dict(0, 0, 0, 0, 0),
            "source": source_label,
        }

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        entity_rows = query_graph_nodes(conn, query_text, top_k=top_k)
        unit_rows = query_graph_units(conn, query_text, top_k=top_k)
        relationship_rows = query_graph_relationships(conn, entity_rows, top_k=top_k)
        node_lookup_rows = list(entity_rows)
        theme_ids = [row["node_id"] for row in entity_rows if row["node_type"] == "theme"]
        if theme_ids:
            placeholders = ", ".join("?" for _ in theme_ids)
            theme_rows = conn.execute(
                f"""
                SELECT theme_id AS node_id, label AS name, weighted_score AS weighted_count,
                       source_count AS document_count, source_count AS raw_count, 'theme' AS node_type
                FROM themes
                WHERE theme_id IN ({placeholders})
                """,
                (*theme_ids,),
            ).fetchall()
            node_lookup_rows = list(theme_rows) + [row for row in entity_rows if row["node_type"] != "theme"]

    hits: List[Dict[str, Any]] = []
    for row in entity_rows:
        hits.append(
            {
                "title": f"{row['node_type'].title()}: {row['name']}",
                "snippet": f"weighted={row['weighted_count']:.2f}, documents={row['document_count']}",
                "source": str(row["node_id"]),
                "score": float(row["score"]),
                "kind": row["node_type"],
                "meta": {"kind": row["node_type"]},
            }
        )
    for row in relationship_rows:
        hits.append(
            {
                "title": f"{row['source_name']} -> {row['target_name']}",
                "snippet": f"{row['relation_type']} (weight={row['weight']})",
                "source": str(row["relationship_id"]),
                "score": float(row["weight"]),
                "kind": "relationship",
                "meta": {"kind": "relationship"},
            }
        )
    for row in unit_rows:
        hits.append(
            {
                "title": f"Unit: {row['source_id']}",
                "snippet": str(row["text"])[:280],
                "source": str(row["unit_id"]),
                "score": float(row["score"]),
                "kind": "unit",
                "meta": {"kind": "unit"},
            }
        )

    node_lookup = {row["node_id"]: row for row in node_lookup_rows}
    communities = build_theme_communities(node_lookup, relationship_rows)
    return {
        "graph_model_version": GRAPH_QUERY_MODEL_VERSION,
        "entities": [dict(row) for row in entity_rows],
        "relationships": [dict(row) for row in relationship_rows],
        "units": [dict(row) for row in unit_rows],
        "nodes": [graph_query_node_dict(row) for row in entity_rows],
        "edges": [graph_edge_dict(row) for row in relationship_rows],
        "communities": [graph_community_dict(item) for item in communities],
        "hits": hits[:top_k],
        "stats": graph_stats_dict(
            len(entity_rows),
            len([row for row in entity_rows if row["node_type"] == "theme"]),
            len(relationship_rows),
            len(communities),
            len({row["source_id"] for row in unit_rows}) if unit_rows else 0,
        ),
        "db_path": str(db_path),
        "source": source_label,
    }


def graph_node_dict(row: sqlite3.Row, community_id: Optional[str]) -> Dict[str, Any]:
    size = max(10, min(48, int(10 + float(row["weighted_count"] or 0) * 3)))
    return {
        "id": row["node_id"],
        "label": row["name"],
        "name": row["name"],
        "type": row["node_type"],
        "node_type": row["node_type"],
        "size": size,
        "count": row["raw_count"],
        "weighted_count": row["weighted_count"],
        "document_count": row["document_count"],
        "community_id": community_id,
        "metrics": {
            "count": row["raw_count"],
            "weighted_count": row["weighted_count"],
            "document_count": row["document_count"],
        },
        "attributes": {
            "community_id": community_id,
        },
    }


def graph_query_node_dict(row: sqlite3.Row) -> Dict[str, Any]:
    size = max(10, min(48, int(10 + float(row["weighted_count"] or 0) * 3)))
    return {
        "id": row["node_id"],
        "label": row["name"],
        "name": row["name"],
        "type": row["node_type"],
        "node_type": row["node_type"],
        "size": size,
        "score": float(row["score"]),
        "weighted_count": row["weighted_count"],
        "document_count": row["document_count"],
        "metrics": {
            "score": float(row["score"]),
            "weighted_count": row["weighted_count"],
            "document_count": row["document_count"],
        },
        "attributes": {},
    }


def graph_edge_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["relationship_id"],
        "source": row["source_node_id"],
        "target": row["target_node_id"],
        "relation": row["relation_type"],
        "label": row["relation_type"],
        "weight": row["weight"],
        "source_kind": row["source_node_kind"],
        "target_kind": row["target_node_kind"],
        "source_name": row["source_name"],
        "target_name": row["target_name"],
        "attributes": {
            "source_kind": row["source_node_kind"],
            "target_kind": row["target_node_kind"],
        },
    }


def graph_community_dict(community: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": community["id"],
        "title": community["title"],
        "summary": community.get("summary", ""),
        "entity_ids": community["entity_ids"],
        "node_ids": community["entity_ids"],
        "score": community["score"],
        "entity_count": community["entity_count"],
        "relationship_count": community["relationship_count"],
        "stats": {
            "entity_count": community["entity_count"],
            "relationship_count": community["relationship_count"],
            "score": community["score"],
        },
        "attributes": {
            "source_theme": community.get("source_theme"),
        },
    }


def graph_stats_dict(
    entity_count: int,
    theme_count: int,
    relationship_count: int,
    community_count: int,
    document_count: int,
) -> Dict[str, Any]:
    return {
        "entity_count": entity_count,
        "theme_count": theme_count,
        "relationship_count": relationship_count,
        "community_count": community_count,
        "document_count": document_count,
    }


def build_theme_communities(node_lookup: Dict[str, sqlite3.Row], relationship_rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    communities: List[Dict[str, Any]] = []
    theme_edges: Dict[str, List[sqlite3.Row]] = defaultdict(list)
    for row in relationship_rows:
        if row["source_node_kind"] == "theme":
            theme_edges[row["source_node_id"]].append(row)
        if row["target_node_kind"] == "theme":
            theme_edges[row["target_node_id"]].append(row)
    for theme_id, theme_row in node_lookup.items():
        if theme_row["node_type"] != "theme":
            continue
        connected = theme_edges.get(theme_id, [])
        entity_ids: List[str] = []
        for row in connected:
            other_id = row["target_node_id"] if row["source_node_id"] == theme_id else row["source_node_id"]
            if other_id != theme_id and other_id in node_lookup:
                entity_ids.append(other_id)
        unique_entity_ids = list(dict.fromkeys(entity_ids))
        support_names = [node_lookup[item]["name"] for item in unique_entity_ids[:6]]
        communities.append(
            {
                "id": f"community-{len(communities) + 1}",
                "title": theme_row["name"],
                "summary": "、".join(support_names) if support_names else theme_row["name"],
                "entity_count": len(unique_entity_ids) + 1,
                "relationship_count": len(connected),
                "entity_ids": [theme_id] + unique_entity_ids,
                "score": theme_row["weighted_count"],
                "theme_labels": [theme_row["name"]],
                "supporting_source_ids": [],
            }
        )
    if not communities:
        isolated_entities = [row for row in node_lookup.values() if row["node_type"] == "entity"][:8]
        for row in isolated_entities:
            communities.append(
                {
                    "id": f"community-{len(communities) + 1}",
                    "title": row["name"],
                    "summary": row["name"],
                    "entity_count": 1,
                    "relationship_count": 0,
                    "entity_ids": [row["node_id"]],
                    "score": row["weighted_count"],
                    "theme_labels": [],
                    "supporting_source_ids": [],
                }
            )
    communities.sort(key=lambda item: (item.get("score", 0), item["entity_count"], item["relationship_count"]), reverse=True)
    return communities


def query_graph_nodes(conn: sqlite3.Connection, query_text: str, *, top_k: int) -> List[sqlite3.Row]:
    try:
        rows = conn.execute(
            """
            SELECT e.entity_id AS node_id, e.name, e.weighted_occurrence_count AS weighted_count,
                   e.document_count, 'entity' AS node_type, bm25(entity_fts) * -1.0 AS score
            FROM entity_fts
            JOIN entities e ON e.entity_id = entity_fts.entity_id
            WHERE entity_fts MATCH ?
            ORDER BY score DESC
            LIMIT ?
            """,
            (query_text, top_k),
        ).fetchall()
        theme_rows = conn.execute(
            """
            SELECT t.theme_id AS node_id, t.label AS name, t.weighted_score AS weighted_count,
                   t.source_count AS document_count, 'theme' AS node_type, bm25(theme_fts) * -1.0 AS score
            FROM theme_fts
            JOIN themes t ON t.theme_id = theme_fts.theme_id
            WHERE theme_fts MATCH ?
            ORDER BY score DESC
            LIMIT ?
            """,
            (query_text, top_k),
        ).fetchall()
        merged = list(rows) + list(theme_rows)
        if merged:
            merged.sort(key=lambda row: float(row["score"]), reverse=True)
            return merged[:top_k]
    except sqlite3.OperationalError:
        pass
    like = f"%{query_text.lower()}%"
    entity_rows = conn.execute(
        """
        SELECT entity_id AS node_id, name, weighted_occurrence_count AS weighted_count,
               document_count, 'entity' AS node_type, 0.1 AS score
        FROM entities
        WHERE lower(name) LIKE ? OR lower(normalized_name) LIKE ?
        ORDER BY weighted_occurrence_count DESC
        LIMIT ?
        """,
        (like, like, top_k),
    ).fetchall()
    theme_rows = conn.execute(
        """
        SELECT theme_id AS node_id, label AS name, weighted_score AS weighted_count,
               source_count AS document_count, 'theme' AS node_type, 0.1 AS score
        FROM themes
        WHERE lower(label) LIKE ? OR lower(normalized_label) LIKE ?
        ORDER BY weighted_score DESC
        LIMIT ?
        """,
        (like, like, top_k),
    ).fetchall()
    merged = list(entity_rows) + list(theme_rows)
    merged.sort(key=lambda row: (float(row["score"]), float(row["weighted_count"])), reverse=True)
    return merged[:top_k]


def query_graph_units(conn: sqlite3.Connection, query_text: str, *, top_k: int) -> List[sqlite3.Row]:
    try:
        rows = conn.execute(
            """
            SELECT unit_id, source_id, text, bm25(unit_fts) * -1.0 AS score
            FROM unit_fts
            WHERE unit_fts MATCH ?
            ORDER BY score DESC
            LIMIT ?
            """,
            (query_text, top_k),
        ).fetchall()
        if rows:
            return rows
    except sqlite3.OperationalError:
        pass
    like = f"%{query_text.lower()}%"
    return conn.execute(
        """
        SELECT unit_id, source_id, text, importance AS score
        FROM distilled_units
        WHERE lower(text) LIKE ?
        ORDER BY importance DESC, confidence DESC
        LIMIT ?
        """,
        (like, top_k),
    ).fetchall()


def query_graph_relationships(
    conn: sqlite3.Connection,
    entity_rows: List[sqlite3.Row],
    *,
    top_k: int,
) -> List[sqlite3.Row]:
    node_ids = [row["node_id"] for row in entity_rows[: max(1, top_k)]]
    if not node_ids:
        return []
    placeholders = ", ".join("?" for _ in node_ids)
    return conn.execute(
        f"""
        WITH node_names AS (
            SELECT entity_id AS node_id, name FROM entities
            UNION ALL
            SELECT theme_id AS node_id, label AS name FROM themes
        )
        SELECT r.relationship_id, r.relation_type, r.weight,
               r.source_node_id, r.target_node_id, r.source_node_kind, r.target_node_kind,
               s.name AS source_name, t.name AS target_name
        FROM relationships r
        JOIN node_names s ON s.node_id = r.source_node_id
        JOIN node_names t ON t.node_id = r.target_node_id
        WHERE r.source_node_id IN ({placeholders}) OR r.target_node_id IN ({placeholders})
        ORDER BY r.weight DESC
        LIMIT ?
        """,
        (*node_ids, *node_ids, top_k),
    ).fetchall()
