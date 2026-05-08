"""Legacy compatibility boundary for knowledge-base imports.

The meeting backend no longer owns graph storage, wiki artifacts, or global
knowledge-base merge logic. Those responsibilities moved to the standalone
Local Knowledge Governance Service under `~/Desktop/workspace/data_service`.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx


NAMESPACE_GLOBAL = "global"
NAMESPACE_PREFIX_MEETING = "meeting_"


def is_meeting_namespace(namespace: str) -> bool:
    return namespace.startswith(NAMESPACE_PREFIX_MEETING)


def make_meeting_namespace(meeting_id: str) -> str:
    return f"{NAMESPACE_PREFIX_MEETING}{meeting_id}"


def extract_meeting_id(namespace: str) -> Optional[str]:
    if is_meeting_namespace(namespace):
        return namespace[len(NAMESPACE_PREFIX_MEETING):]
    return None


class SynonymRegistry:
    def __init__(self) -> None:
        self._synonym_groups: Dict[str, set[str]] = {}
        self._synonym_to_canonical: Dict[str, str] = {}

    def add_synonym_group(self, canonical: str, synonyms: List[str]) -> None:
        canonical_lower = canonical.lower().strip()
        synonym_set = {canonical_lower, *(syn.lower().strip() for syn in synonyms)}
        self._synonym_groups[canonical_lower] = synonym_set
        for synonym in synonym_set:
            self._synonym_to_canonical[synonym] = canonical_lower

    def get_canonical(self, name: str) -> Optional[str]:
        return self._synonym_to_canonical.get(name.lower().strip())

    def are_synonyms(self, name1: str, name2: str) -> bool:
        canonical1 = self.get_canonical(name1)
        canonical2 = self.get_canonical(name2)
        return bool(canonical1 and canonical2 and canonical1 == canonical2)

    def to_dict(self) -> Dict[str, List[str]]:
        return {key: sorted(value) for key, value in self._synonym_groups.items()}


class EmbeddingSimilarity:
    async def compute_entity_similarity(
        self,
        entity1: Dict[str, Any],
        entity2: Dict[str, Any],
        synonym_registry: Optional[SynonymRegistry] = None,
    ) -> float:
        if entity1.get("name") == entity2.get("name"):
            return 1.0
        if synonym_registry and synonym_registry.are_synonyms(
            str(entity1.get("name", "")),
            str(entity2.get("name", "")),
        ):
            return 0.95
        return 0.0


class _ExternalKnowledgeServiceClient:
    def __init__(self) -> None:
        self.base_url = os.getenv(
            "DATA_SERVICE_HTTP_BASE_URL",
            "http://127.0.0.1:8003/api/v1/knowledge",
        ).rstrip("/")

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        api_key = os.getenv("DATA_SERVICE_API_KEY", "").strip()
        if api_key:
            headers["x-api-key"] = api_key
        return headers

    async def post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()


class NamespaceManager:
    """Compatibility facade; namespace data is governed by data_service."""

    def __init__(self) -> None:
        self.client = _ExternalKnowledgeServiceClient()


class EntityMerger:
    """Compatibility facade retained for old imports."""

    def __init__(self) -> None:
        self.synonym_registry = SynonymRegistry()
        self.similarity = EmbeddingSimilarity()


class GlobalKnowledgeBase:
    """Compatibility facade for the migrated knowledge service."""

    def __init__(self) -> None:
        self.client = _ExternalKnowledgeServiceClient()

    async def import_source(self, workspace: str, path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self.client.post(
            "/sources/import",
            {"workspace": workspace, "paths": [str(Path(path))], "metadata": metadata or {}},
        )

    async def query(self, workspace: str, query: str, mode: str = "hybrid", top_k: int = 8) -> Dict[str, Any]:
        return await self.client.post(
            "/query",
            {"workspace": workspace, "query": query, "mode": mode, "top_k": top_k},
        )

    async def graph(self, workspace: str, max_nodes: int = 120) -> Dict[str, Any]:
        return await self.client.post("/graph", {"workspace": workspace, "max_nodes": max_nodes})

    async def export_knowledge_base(self, namespace: str) -> Dict[str, Any]:
        workspace = os.getenv("DATA_SERVICE_WORKSPACE") or namespace
        return await self.client.post("/summary", {"workspace": workspace})


_global_knowledge_base: Optional[GlobalKnowledgeBase] = None


def get_knowledge_base() -> GlobalKnowledgeBase:
    global _global_knowledge_base
    if _global_knowledge_base is None:
        _global_knowledge_base = GlobalKnowledgeBase()
    return _global_knowledge_base
