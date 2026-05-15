"""V3.6 workflow runtime object contract schemas.

Contract metadata only; not a stable V4.0 UI contract and not a runtime
handler registry.
"""

from __future__ import annotations

from typing import Any

from core.workflows.models import (
    ArtifactContract,
    BusinessEvent,
    BusinessEventBinding,
    PipelineBoard,
    QualityContract,
    QualityEvaluation,
    Station,
    StationRun,
    WorkflowAction,
    WorkflowContext,
    WorkflowDraft,
    WorkflowEdge,
    WorkflowInstance,
    WorkflowPatch,
    WorkflowTemplate,
    WorkflowVersion,
)

FAMILY = "workflow_runtime"
INTRODUCED_IN = "V3.6"


def _object_schema(name: str, model: type[Any]) -> dict[str, Any]:
    return {
        "name": name,
        "schema_ref": f"protocol.workflow.objects.{name}",
        "family": FAMILY,
        "introduced_in": INTRODUCED_IN,
        "schema_status": "contract",
        "stable_for_ui": False,
        "schema": model.model_json_schema(),
    }


WORKFLOW_OBJECT_SCHEMAS: list[dict[str, Any]] = [
    _object_schema("WorkflowTemplate", WorkflowTemplate),
    _object_schema("WorkflowVersion", WorkflowVersion),
    _object_schema("WorkflowDraft", WorkflowDraft),
    _object_schema("WorkflowInstance", WorkflowInstance),
    _object_schema("Station", Station),
    _object_schema("WorkflowEdge", WorkflowEdge),
    _object_schema("StationRun", StationRun),
    _object_schema("ArtifactContract", ArtifactContract),
    _object_schema("QualityContract", QualityContract),
    _object_schema("QualityEvaluation", QualityEvaluation),
    _object_schema("WorkflowAction", WorkflowAction),
    _object_schema("WorkflowPatch", WorkflowPatch),
    _object_schema("WorkflowContext", WorkflowContext),
    _object_schema("BusinessEvent", BusinessEvent),
    _object_schema("BusinessEventBinding", BusinessEventBinding),
    _object_schema("PipelineBoard", PipelineBoard),
]
