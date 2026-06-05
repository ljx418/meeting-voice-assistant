from __future__ import annotations

import json

from core.product_console.v7_3_workflow_run import build_workflow_spec
from core.station_agents import (
    build_local_document_station_agent_registry,
    create_agent_context_envelopes,
    create_agent_invocation_evidence,
)


def _runtime_result() -> dict:
    return {
        "status": "completed",
        "provider": {
            "provider": "minimax",
            "model_ref": "MiniMax-M2.1",
            "provider_config_source": ".env",
        },
        "quality_report": {"scanner_actual_read_count": 5, "provider_invocation_count": 4},
    }


def test_context_envelopes_use_refs_and_do_not_include_raw_content() -> None:
    spec = build_workflow_spec("递归总结 Markdown 技术文档", "mission-v8", "2026-06-04T00:00:00+00:00")
    registry = build_local_document_station_agent_registry(spec)

    envelopes = [item.to_dict() for item in create_agent_context_envelopes(registry, spec, _runtime_result())]
    dumped = json.dumps(envelopes, ensure_ascii=False)

    assert len(envelopes) == len(spec["stations"])
    assert all(item["context_scope"] == "station_scoped" for item in envelopes)
    assert "raw_prompt" not in dumped
    assert "raw_file_content" not in dumped
    assert "raw_artifact_content" not in dumped
    assert "MINIMAX_API_KEY" not in dumped


def test_invocation_evidence_records_provider_refs_for_llm_stations() -> None:
    spec = build_workflow_spec("递归总结 Markdown 技术文档", "mission-v8", "2026-06-04T00:00:00+00:00")
    registry = build_local_document_station_agent_registry(spec)

    evidence = [item.to_dict() for item in create_agent_invocation_evidence(registry, spec, _runtime_result())]
    llm = [item for item in evidence if item["invocation_kind"] == "llm"]

    assert len(evidence) == len(spec["stations"])
    assert {item["station_id"] for item in llm} == {"per_folder_summary", "overview_summary"}
    assert all(item["provider"] == "minimax" for item in llm)
    assert all(item["model_ref"] == "MiniMax-M2.1" for item in llm)
