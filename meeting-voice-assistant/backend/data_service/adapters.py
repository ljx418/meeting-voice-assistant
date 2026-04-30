"""Adapter contracts for the upstream data_service layer.

These adapters intentionally keep llmwiki and graphrag behind narrow
capability-specific interfaces.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Protocol

from .models import DistilledUnit, IngestPlan


@dataclass
class AdapterResult:
    """Result returned by one downstream engine adapter."""

    engine: str
    status: str
    artifacts: List[str] = field(default_factory=list)
    meta: Dict[str, object] = field(default_factory=dict)


class LLMWikiAdapter(Protocol):
    """Capability contract for llmwiki integration."""

    def compile(self, plan: IngestPlan, units: List[DistilledUnit]) -> AdapterResult:
        """Compile readable wiki artifacts from distilled units."""


class GraphRAGAdapter(Protocol):
    """Capability contract for graphrag integration."""

    def index(self, plan: IngestPlan, units: List[DistilledUnit]) -> AdapterResult:
        """Index distilled units into graph-oriented assets."""
