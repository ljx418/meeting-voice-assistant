from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SourceChunk:
    chunk_id: str
    text: str
    document_id: str
    offset: int = 0


@dataclass
class EntityInfo:
    entity_id: str
    name: str
    entity_type: str
    description: str | None = None
    source_chunk_id: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class CommunityInfo:
    community_id: str
    level: int
    title: str | None = None
    summary: str | None = None
    entity_ids: list[str] = field(default_factory=list)


@dataclass
class QueryResult:
    query_text: str
    answer: str
    source_chunks: list[SourceChunk] = field(default_factory=list)
    entities: list[EntityInfo] = field(default_factory=list)
    communities: list[CommunityInfo] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class SummaryResult:
    summary: str
    community_summaries: list[CommunityInfo] = field(default_factory=list)
    total_entities: int = 0
    total_communities: int = 0


@dataclass
class GraphNode:
    node_id: str
    label: str
    node_type: str
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    edge_id: str
    source_id: str
    target_id: str
    relationship: str
    weight: float = 1.0
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphData:
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)


@dataclass
class IndexResult:
    document_id: str
    namespace: str
    status: str
    entity_count: int = 0
    relationship_count: int = 0
    community_count: int = 0
    error: str | None = None


@dataclass
class BatchIndexResult:
    total: int
    succeeded: int
    failed: int
    results: list[IndexResult] = field(default_factory=list)


class GraphRAGCore(ABC):
    """Abstract base class for GraphRAG implementations."""

    @abstractmethod
    async def index_document(self, doc_path: Path, namespace: str) -> IndexResult:
        """Index a single document."""
        pass

    @abstractmethod
    async def index_documents_batch(
        self, doc_paths: list[Path], namespace: str
    ) -> BatchIndexResult:
        """Index multiple documents in batch."""
        pass

    @abstractmethod
    async def query(
        self,
        query_text: str,
        namespace: str,
        top_k: int = 10,
        context: str | None = None,
    ) -> QueryResult:
        """Query the knowledge graph."""
        pass

    @abstractmethod
    async def summarize(
        self, namespace: str, query: str | None = None
    ) -> SummaryResult:
        """Generate a summary of the knowledge graph."""
        pass

    @abstractmethod
    async def get_graph_data(
        self, namespace: str, max_nodes: int = 100
    ) -> GraphData:
        """Retrieve graph data for visualization."""
        pass

    @abstractmethod
    async def delete_document(self, doc_id: str, namespace: str) -> None:
        """Delete a document and its associated data."""
        pass
