from __future__ import annotations

from tests.v5_3_observability_support import make_context
from tests.v5_4c_runtime_support import make_v5_4c_bridge


def test_v5_4c_rerun_preserves_attempt_history_and_marks_downstream_stale(monkeypatch, tmp_path) -> None:
    context = make_context()
    bridge, _adapter = make_v5_4c_bridge(monkeypatch, tmp_path)
    failed = bridge.start_local_folder_summary(
        context,
        folder_path="tests/fixtures/desktop/技术分享_损坏",
        source="run_panel",
        actor_type="human_user",
        user_confirmed=True,
    ).to_dict()
    workflow_instance_id = failed["runtime_result"]["workflow_instance_id"]

    rerun = bridge.rerun_station(
        context,
        workflow_instance_id=workflow_instance_id,
        station_id="markdown_parse",
        source="run_panel",
        actor_type="human_user",
        user_confirmed=True,
    ).to_dict()

    parse_node = next(node for node in rerun["runtime_result"]["nodes"] if node["station_id"] == "markdown_parse")
    assert failed["runtime_result"]["status"] == "failed"
    assert rerun["status"] == "applied_existing_v4_runtime"
    assert rerun["runtime_result"]["status"] == "waiting_user_confirmation"
    assert [attempt["status"] for attempt in parse_node["attempts"]] == ["failed", "completed"]
    assert "Markdown parse failed" in parse_node["attempts"][0]["error"]
    assert {item["station_id"] for item in rerun["runtime_result"]["downstream_stale"]} == {
        "folder_group",
        "per_folder_summary",
        "overview_summary",
        "quality_check",
        "artifact_publish",
    }
    assert rerun["bridge_evidence"]["runtime_result_ref"]["workflow_instance_id"] == workflow_instance_id


def test_v5_4c_continue_downstream_after_rerun(monkeypatch, tmp_path) -> None:
    context = make_context()
    bridge, _adapter = make_v5_4c_bridge(monkeypatch, tmp_path)
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

    continued = bridge.continue_downstream(
        context,
        workflow_instance_id=workflow_instance_id,
        source="run_panel",
        actor_type="human_user",
        user_confirmed=True,
    ).to_dict()

    assert continued["status"] == "applied_existing_v4_runtime"
    assert continued["runtime_result"]["status"] == "completed"
    assert continued["runtime_result"]["downstream_stale"] == []
    assert continued["runtime_result"]["quality_report"]["status"] == "passed"
