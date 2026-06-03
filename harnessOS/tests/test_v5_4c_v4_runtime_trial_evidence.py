from __future__ import annotations

import json

from tests.v4_0_reference_support import assert_no_forbidden_text
from tests.v5_3_observability_support import make_context
from tests.v5_4c_runtime_support import make_v5_4c_bridge


def test_v5_4c_bridge_and_existing_runtime_evidence_are_linked(monkeypatch, tmp_path) -> None:
    context = make_context()
    bridge, adapter = make_v5_4c_bridge(monkeypatch, tmp_path)
    failed = bridge.start_local_folder_summary(
        context,
        folder_path="tests/fixtures/desktop/技术分享_损坏",
        source="run_panel",
        actor_type="human_user",
        user_confirmed=True,
    ).to_dict()
    workflow_instance_id = failed["runtime_result"]["workflow_instance_id"]
    bridge.rerun_station(
        context,
        workflow_instance_id=workflow_instance_id,
        station_id="markdown_parse",
        source="run_panel",
        actor_type="human_user",
        user_confirmed=True,
    )
    bridge.continue_downstream(
        context,
        workflow_instance_id=workflow_instance_id,
        source="run_panel",
        actor_type="human_user",
        user_confirmed=True,
    )

    existing_evidence = adapter.list_evidence(workflow_instance_id=workflow_instance_id)
    bridge_evidence = [item.to_dict() for item in bridge.bridge_evidence]
    operations = {item["operation"] for item in existing_evidence}

    assert {"workflow.instance.start", "station.rerun", "workflow.instance.continue_downstream"}.issubset(operations)
    assert all(item["user_confirmed"] is True for item in existing_evidence)
    assert all(item["source"] != "agent" for item in existing_evidence)
    assert all(item["runtime_backed"] is True for item in bridge_evidence)
    assert all(item["devlocal_only"] is True for item in bridge_evidence)
    assert_no_forbidden_text({"existing_evidence": existing_evidence, "bridge_evidence": bridge_evidence})


def test_v5_4c_result_does_not_expose_raw_payload_or_overclaim(monkeypatch, tmp_path) -> None:
    context = make_context()
    bridge, _adapter = make_v5_4c_bridge(monkeypatch, tmp_path)
    # This blocked result requires no filesystem fixture and still exercises the DTO shape.
    result = bridge.start_local_folder_summary(
        context,
        folder_path="tests/fixtures/desktop/技术分享",
        source="agent",
        actor_type="agent",
        user_confirmed=True,
    ).to_dict()
    dumped = json.dumps(result, ensure_ascii=False)

    assert "raw_trace_payload" not in dumped
    assert "raw_artifact_content" not in dumped
    assert "raw_connector_payload" not in dumped
    assert ("controlled executor" + " ready") not in dumped
    assert ("Agent executor" + " ready") not in dumped
