from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from apps.gateway.artifacts import ArtifactRegistry
from core.apps import ScopeContext
from packs.knowledge.workflow import KnowledgeWorkflow


class ReplacementRuntime:
    def __init__(self, artifact_path: Path) -> None:
        self.artifact_path = artifact_path
        self.calls: list[dict] = []

    def submit(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "job": {"job_id": "job_replacement", "status": "completed"},
            "artifact": {
                "artifact_id": "art_connector_replacement",
                "kind": "connector_result",
                "path": str(self.artifact_path),
            },
        }


def test_knowledge_workflow_accepts_connector_replacement_without_core_changes(tmp_path):
    artifact_path = tmp_path / "connector-result.json"
    artifact_path.write_text(
        json.dumps(
            {
                "result": {
                    "status": "ok",
                    "workspace_id": "workspace_replace",
                    "data": {
                        "answer": "replacement answer",
                        "citations": [{"title": "replacement source"}],
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    runtime = ReplacementRuntime(artifact_path)
    workflow = KnowledgeWorkflow(connector_execution_runtime=runtime)
    context = SimpleNamespace(
        session_id="sess_replace",
        turn_id="turn_replace",
        scope=ScopeContext(app_id="knowledge", workspace_id="workspace_replace"),
        artifact_registry=ArtifactRegistry(tmp_path / "artifacts"),
        approval_id=None,
    )

    result = workflow._run_via_connector("检索知识库 connector replacement", context)

    assert runtime.calls[0]["connector_id"] == "data_service_mcp"
    assert runtime.calls[0]["tool"] == "knowledge_query_v2"
    assert set(result["artifact_records"]) == {"source_reference", "note", "brief", "citation_bundle"}
    assert result["knowledge"]["sources"] == ["replacement source"]
