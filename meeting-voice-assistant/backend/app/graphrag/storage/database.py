from pathlib import Path
from typing import Any, Optional

from sqlalchemy import select, delete, or_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from .models import Base, Document, Entity, Relationship, Community
from ..config import settings
from ..core.base import GraphData, GraphNode, GraphEdge


db_path = settings.GRAPHRAG_WORKSPACE / "graphrag.db"
engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_graph_data(
    namespace: str, max_nodes: int = 100
) -> GraphData:
    """
    Get graph data (nodes and edges) for a given namespace.

    Args:
        namespace: The namespace to filter by.
        max_nodes: Maximum number of nodes to return.

    Returns:
        GraphData object with nodes and edges lists.
    """
    async with async_session() as session:
        # Get entities as nodes
        entity_stmt = (
            select(Entity)
            .where(Entity.namespace == namespace)
            .limit(max_nodes)
        )
        result = await session.execute(entity_stmt)
        entities = result.scalars().all()

        nodes: list[GraphNode] = []
        entity_ids = []
        for entity in entities:
            nodes.append(GraphNode(
                node_id=entity.id,
                label=entity.name,
                node_type=entity.type or "unknown",
                attributes={
                    "description": entity.description,
                    "community_id": entity.community_id,
                },
            ))
            entity_ids.append(entity.id)

        # Get relationships as edges
        edges: list[GraphEdge] = []
        if entity_ids:
            edge_stmt = select(Relationship).where(
                Relationship.namespace == namespace,
                Relationship.source_entity_id.in_(entity_ids),
                Relationship.target_entity_id.in_(entity_ids),
            )
            edge_result = await session.execute(edge_stmt)
            relationships = edge_result.scalars().all()

            for rel in relationships:
                edges.append(GraphEdge(
                    edge_id=rel.id,
                    source_id=rel.source_entity_id,
                    target_id=rel.target_entity_id,
                    relationship=rel.relation_type or "related",
                    weight=rel.weight or 1.0,
                    attributes={
                        "description": rel.description,
                    },
                ))

        return GraphData(nodes=nodes, edges=edges)


async def save_document(
    doc_id: str,
    namespace: str,
    filename: str,
    file_path: str,
    chunk_count: Optional[int] = None,
    entity_count: Optional[int] = None,
) -> None:
    """Insert a document record (skips if already exists)."""
    async with async_session() as session:
        # Check if document already exists
        result = await session.execute(
            select(Document).where(Document.id == doc_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return  # Skip duplicates
        doc = Document(
            id=doc_id,
            namespace=namespace,
            filename=filename,
            file_path=file_path,
            chunk_count=chunk_count,
            entity_count=entity_count,
        )
        session.add(doc)
        await session.commit()


async def save_entity(
    entity_id: str,
    namespace: str,
    name: str,
    doc_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    description: Optional[str] = None,
    community_id: Optional[str] = None,
) -> None:
    """Insert an entity record (skips if already exists)."""
    async with async_session() as session:
        # Check if entity already exists
        result = await session.execute(
            select(Entity).where(Entity.id == entity_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return  # Skip duplicates
        entity = Entity(
            id=entity_id,
            doc_id=doc_id,
            namespace=namespace,
            name=name,
            type=entity_type,
            description=description,
            community_id=community_id,
        )
        session.add(entity)
        await session.commit()


async def save_relationship(
    rel_id: str,
    source_entity_id: str,
    target_entity_id: str,
    namespace: str,
    relation_type: Optional[str] = None,
    description: Optional[str] = None,
    weight: float = 1.0,
) -> None:
    """Insert a relationship record (skips if already exists)."""
    async with async_session() as session:
        # Check if relationship already exists
        result = await session.execute(
            select(Relationship).where(Relationship.id == rel_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return  # Skip duplicates
        rel = Relationship(
            id=rel_id,
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relation_type=relation_type,
            description=description,
            weight=weight,
            namespace=namespace,
        )
        session.add(rel)
        await session.commit()


async def save_community(
    community_id: str,
    namespace: str,
    level: Optional[int] = None,
    summary: Optional[str] = None,
    parent_id: Optional[str] = None,
) -> None:
    """Insert a community record (skips if already exists)."""
    async with async_session() as session:
        # Check if community already exists
        result = await session.execute(
            select(Community).where(Community.id == community_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return  # Skip duplicates
        community = Community(
            id=community_id,
            namespace=namespace,
            level=level,
            summary=summary,
            parent_id=parent_id,
        )
        session.add(community)
        await session.commit()


async def delete_document(doc_id: str, namespace: str) -> bool:
    """
    Delete a document and all its associated entities and relationships.

    Args:
        doc_id: The document ID to delete.
        namespace: The namespace to verify ownership.

    Returns:
        True if the document was deleted, False if it was not found.
    """
    async with async_session() as session:
        # First, get all entity IDs for this document
        entity_stmt = select(Entity.id).where(
            Entity.doc_id == doc_id, Entity.namespace == namespace
        )
        entity_result = await session.execute(entity_stmt)
        entity_ids = [row[0] for row in entity_result.fetchall()]

        # Delete relationships where source or target entity belongs to these entities
        if entity_ids:
            delete_rel_stmt = delete(Relationship).where(
                Relationship.source_entity_id.in_(entity_ids),
                Relationship.namespace == namespace,
            )
            await session.execute(delete_rel_stmt)

            delete_rel_stmt = delete(Relationship).where(
                Relationship.target_entity_id.in_(entity_ids),
                Relationship.namespace == namespace,
            )
            await session.execute(delete_rel_stmt)

            # Delete entities
            delete_ent_stmt = delete(Entity).where(
                Entity.doc_id == doc_id, Entity.namespace == namespace
            )
            await session.execute(delete_ent_stmt)

        # Delete the document
        delete_doc_stmt = delete(Document).where(
            Document.id == doc_id, Document.namespace == namespace
        )
        result = await session.execute(delete_doc_stmt)
        deleted = result.rowcount > 0

        await session.commit()
        return deleted


async def clear_all_data(namespace: str) -> dict:
    """
    清空 namespace 下的所有数据（文档、实体、关系、社区）

    Args:
        namespace: 要清空的命名空间

    Returns:
        dict: 包含 deleted_documents, deleted_entities, deleted_relationships, deleted_communities
    """
    async with async_session() as session:
        # 获取所有文档
        doc_stmt = select(Document.id).where(Document.namespace == namespace)
        doc_result = await session.execute(doc_stmt)
        doc_ids = [row[0] for row in doc_result.fetchall()]

        # 获取所有实体
        ent_stmt = select(Entity.id).where(Entity.namespace == namespace)
        ent_result = await session.execute(ent_stmt)
        ent_ids = [row[0] for row in ent_result.fetchall()]

        deleted_entities = 0
        deleted_relationships = 0
        deleted_communities = 0

        # 删除关系（source 或 target 在 ent_ids 中）
        if ent_ids:
            rel_stmt = delete(Relationship).where(
                or_(
                    Relationship.source_entity_id.in_(ent_ids),
                    Relationship.target_entity_id.in_(ent_ids)
                ),
                Relationship.namespace == namespace
            )
            rel_result = await session.execute(rel_stmt)
            deleted_relationships = rel_result.rowcount

            # 删除实体
            ent_del_stmt = delete(Entity).where(Entity.namespace == namespace)
            ent_result = await session.execute(ent_del_stmt)
            deleted_entities = ent_result.rowcount

        # 删除社区
        comm_stmt = delete(Community).where(Community.namespace == namespace)
        comm_result = await session.execute(comm_stmt)
        deleted_communities = comm_result.rowcount

        # 删除文档
        doc_del_stmt = delete(Document).where(Document.namespace == namespace)
        doc_result = await session.execute(doc_del_stmt)
        deleted_documents = doc_result.rowcount

        await session.commit()

        return {
            "deleted_documents": deleted_documents,
            "deleted_entities": deleted_entities,
            "deleted_relationships": deleted_relationships,
            "deleted_communities": deleted_communities,
        }
