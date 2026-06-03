from core.workflows.v4_unified_experience import (
    build_mission_console_projection,
    build_experience_state_projection,
    build_review_action,
    render_tui_state_timeline,
    resolve_available_action,
    validate_transition,
)


def test_experience_state_projection_is_read_model():
    projection = build_experience_state_projection(
        workflow_state="DiffReady",
        station_states=[{"station_id": "folder_scan", "state": "completed"}],
        evidence_state="EvidenceReady",
        operations=["workflow.patch.apply", "evidence.show"],
        source="mission_console",
        source_refs=["workflow_draft:draft-1", "patch:patch-1"],
        refresh_generation=7,
        stale_reasons=["selected_patch_base_revision_mismatch"],
    ).to_dict()

    assert projection["read_model_only"] is True
    assert projection["refresh_generation"] == 7
    assert projection["stale_reasons"] == ["selected_patch_base_revision_mismatch"]
    assert "WorkflowDraft" in projection["runtime_truth_boundary"]
    assert "workflow.patch.apply" not in projection["blocked_actions"]


def test_source_agent_cannot_execute_mutation():
    action = resolve_available_action("workflow.instance.start", source="agent")
    assert action.agent_executable is False
    assert action.requires_user_confirmation is True
    assert action.policy_decision == "blocked"

    review_action = build_review_action(
        operation="station.rerun",
        source="agent",
        actor_type="agent",
    )
    assert review_action["operation_executed"] is False
    assert review_action["policy_decision"] == "blocked"


def test_state_transition_validator():
    assert validate_transition("IntentCaptured", "SpecDrafted") is True
    assert validate_transition("IntentCaptured", "Running") is False


def test_tui_state_timeline_renders_shared_projection_without_runtime_write():
    projection = build_mission_console_projection(
        workflow_state="DiffReady",
        refresh_generation=12,
        stale_reasons=["runtime_report_refresh_required"],
    )
    text = render_tui_state_timeline(projection)

    assert "current_state=DiffReady" in text
    assert "refresh_generation=12" in text
    assert "○ IntentCaptured" in text
    assert "● DiffReady" in text
    assert "workflow.patch.apply policy=user_confirmed_only" in text
    assert "station.rerun policy=user_confirmed_only" in text
    assert "agent_executable=false requires_user_confirmation" in text
    assert "runtime_truth_boundary=read_model_only" in text
    assert "runtime_report_refresh_required" in text
