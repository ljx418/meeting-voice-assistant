"""Core contracts for the shared data_service layer."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class AuthorityLevel(str, Enum):
    """Authority used by distilled and compiled units."""

    PRIMARY_DOC = "PRIMARY_DOC"
    SECONDARY_CHAT = "SECONDARY_CHAT"
    DERIVED = "DERIVED"


class DistilledUnitKind(str, Enum):
    """High-value unit types emitted by the distill layer."""

    FACT_CANDIDATE = "fact_candidate"
    QUESTION = "question"
    CONCLUSION = "conclusion"
    STEP = "step"
    EXAMPLE = "example"
    NOTE = "note"
    RISK = "risk"
    ENTITY_CANDIDATE = "entity_candidate"
    RELATION_CANDIDATE = "relation_candidate"
    TOPIC_CANDIDATE = "topic_candidate"


class EngineTarget(str, Enum):
    """Downstream engines fed by the shared data_service pipeline."""

    LLMWIKI = "llmwiki"
    GRAPHRAG = "graphrag"


class GraphExecutionOwner(str, Enum):
    """Who currently executes GraphRAG indexing work."""

    DATA_SERVICE = "data_service"
    APP_GRAPHRAG = "app.graphrag"


class QueryMode(str, Enum):
    """Query modes exposed by data_service."""

    LLMWIKI = "llmwiki"
    GRAPHRAG = "graphrag"
    HYBRID = "hybrid"


@dataclass
class ArtifactLayout:
    """Workspace-level artifact layout for the shared pipeline."""

    workspace: Path
    row_manifest: Path
    raw_dir: Path
    readable_dir: Path
    normalized_dir: Path
    distill_dir: Path
    distill_sources_dir: Path
    distill_units_dir: Path
    distill_manifest: Path
    distill_schema: Path
    llmwiki_dir: Path
    llmwiki_pages_dir: Path
    llmwiki_state_dir: Path
    graphrag_dir: Path
    graphrag_input_dir: Path
    graphrag_cache_dir: Path
    graphrag_state_dir: Path
    graphrag_execution_owner: Path
    graphrag_execution_request: Path
    summary_dir: Path
    summary_md: Path
    summary_json: Path
    quality_dir: Path
    quality_feedback_jsonl: Path
    quality_correction_rules_json: Path
    quality_correction_plan_json: Path

    @classmethod
    def from_workspace(cls, workspace: Path) -> "ArtifactLayout":
        workspace = workspace.resolve()
        llmwiki_dir = workspace / "llmwiki"
        graphrag_dir = workspace / "graphrag"
        return cls(
            workspace=workspace,
            row_manifest=workspace / "row_manifest.json",
            raw_dir=llmwiki_dir / "raw",
            readable_dir=llmwiki_dir / "readable",
            normalized_dir=llmwiki_dir / "normalized",
            distill_dir=workspace / "distill",
            distill_sources_dir=workspace / "distill" / "sources",
            distill_units_dir=workspace / "distill" / "units",
            distill_manifest=workspace / "distill" / "manifest.json",
            distill_schema=workspace / "distill" / "schema.json",
            llmwiki_dir=llmwiki_dir,
            llmwiki_pages_dir=llmwiki_dir / "pages",
            llmwiki_state_dir=llmwiki_dir / "state",
            graphrag_dir=graphrag_dir,
            graphrag_input_dir=graphrag_dir / "input",
            graphrag_cache_dir=graphrag_dir / "cache",
            graphrag_state_dir=graphrag_dir / "state",
            graphrag_execution_owner=graphrag_dir / "cache" / "execution_owner.json",
            graphrag_execution_request=graphrag_dir / "cache" / "execution_request.json",
            summary_dir=workspace / "summary",
            summary_md=workspace / "summary" / "summary.md",
            summary_json=workspace / "summary" / "summary.json",
            quality_dir=workspace / "quality",
            quality_feedback_jsonl=workspace / "quality" / "feedback.jsonl",
            quality_correction_rules_json=workspace / "quality" / "correction_rules.json",
            quality_correction_plan_json=workspace / "quality" / "correction_plan.json",
        )

    def ensure_directories(self) -> None:
        for path in [
            self.raw_dir,
            self.readable_dir,
            self.normalized_dir,
            self.distill_dir,
            self.distill_sources_dir,
            self.distill_units_dir,
            self.llmwiki_pages_dir,
            self.llmwiki_state_dir,
            self.graphrag_input_dir,
            self.graphrag_cache_dir,
            self.graphrag_state_dir,
            self.summary_dir,
            self.quality_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)


@dataclass
class SourceEnvelope:
    """Immutable source descriptor accepted by data_service."""

    path: str
    source_id: Optional[str] = None
    sha256: Optional[str] = None
    authority_hint: Optional[AuthorityLevel] = None
    meta: Dict[str, str] = field(default_factory=dict)


@dataclass
class DistilledUnit:
    """Shared unit passed to llmwiki and/or graphrag."""

    unit_id: str
    source_id: str
    kind: DistilledUnitKind
    authority: AuthorityLevel
    text: str
    normalized_text: str
    importance: float = 0.0
    confidence: float = 0.0
    source_weight: float = 1.0
    source_density_score: float = 1.0
    is_title_derived: bool = False
    is_llm_enriched: bool = False
    tags: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    relations: List[Dict[str, str]] = field(default_factory=list)
    provenance: Dict[str, object] = field(default_factory=dict)


@dataclass
class IngestPlan:
    """Execution plan for a single-ingest dual-engine run."""

    workspace: Path
    layout: ArtifactLayout
    sources: List[SourceEnvelope]
    targets: List[EngineTarget]
    stages: List[str]
    graphrag_execution_owner: GraphExecutionOwner = GraphExecutionOwner.APP_GRAPHRAG
    distill_policy: Dict[str, object] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)


@dataclass
class QueryHit:
    """One query hit from a downstream engine."""

    title: str
    snippet: str
    source: str
    score: float = 0.0
    meta: Dict[str, object] = field(default_factory=dict)


@dataclass
class QueryResponse:
    """Unified data_service query response."""

    mode: QueryMode
    query: str
    answer: str
    hits: List[QueryHit] = field(default_factory=list)
    engine_payloads: Dict[str, object] = field(default_factory=dict)
