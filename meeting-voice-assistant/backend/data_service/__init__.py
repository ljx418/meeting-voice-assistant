"""Shared data service layer above llmwiki and graphrag.

This package defines the orchestration boundary for single-ingest,
dual-engine processing:

raw -> extract -> normalize -> distill -> {llmwiki, graphrag}
"""

from .models import (
    ArtifactLayout,
    AuthorityLevel,
    DistilledUnit,
    DistilledUnitKind,
    EngineTarget,
    GraphExecutionOwner,
    IngestPlan,
    QueryHit,
    QueryMode,
    QueryResponse,
    SourceEnvelope,
)
from .adapters import AdapterResult, GraphRAGAdapter, LLMWikiAdapter
from .default_adapters import GraphRAGWorkspaceAdapter, LLMWikiEngineAdapter
from .service import DataService

__all__ = [
    "AdapterResult",
    "ArtifactLayout",
    "AuthorityLevel",
    "DataService",
    "DistilledUnit",
    "DistilledUnitKind",
    "EngineTarget",
    "GraphExecutionOwner",
    "GraphRAGAdapter",
    "GraphRAGWorkspaceAdapter",
    "IngestPlan",
    "LLMWikiAdapter",
    "LLMWikiEngineAdapter",
    "QueryHit",
    "QueryMode",
    "QueryResponse",
    "SourceEnvelope",
]
