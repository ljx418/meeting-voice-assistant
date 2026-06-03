from __future__ import annotations

from core.policies.executor_safety import CapabilityDecisionService, KillSwitchRegistry
from core.policies.existing_v4_runtime_trial import ExistingV4RuntimeTrialBridge
from tests.v5_3_observability_support import make_context
from tests.v5_4c_runtime_support import BffV42RuntimeAdapter, make_v5_4c_bridge


def test_v5_4c_start_uses_existing_v4_runtime_entrypoint(monkeypatch, tmp_path) -> None:
    context = make_context()
    bridge, adapter = make_v5_4c_bridge(monkeypatch, tmp_path)

    result = bridge.start_local_folder_summary(
        context,
        folder_path="tests/fixtures/desktop/技术分享",
        source="run_panel",
        actor_type="human_user",
        user_confirmed=True,
    ).to_dict()

    assert adapter.call_count == 1
    assert result["status"] == "applied_existing_v4_runtime"
    assert result["runtime_result"]["backed_by"] == "generic_controlled_runtime"
    assert result["runtime_result"]["status"] == "completed"
    assert len(result["runtime_result"]["nodes"]) == 9
    assert result["bridge_evidence"]["runtime_backed"] is True
    assert result["bridge_evidence"]["devlocal_only"] is True
    assert result["bridge_evidence"]["v4_runtime_entrypoint"] == "bff:/bff/v4_2/runtime"
    assert result["decision"]["runtime_execution_allowed"] is False


def test_v5_4c_blocks_missing_confirmation_before_runtime_call(monkeypatch, tmp_path) -> None:
    context = make_context()
    bridge, adapter = make_v5_4c_bridge(monkeypatch, tmp_path)

    result = bridge.start_local_folder_summary(
        context,
        folder_path="tests/fixtures/desktop/技术分享",
        source="run_panel",
        actor_type="human_user",
        user_confirmed=False,
    ).to_dict()

    assert adapter.call_count == 0
    assert result["status"] == "blocked"
    assert result["blocked_reason"] == "missing_user_confirmation"
    assert result["runtime_result"] is None


def test_v5_4c_blocks_agent_source_before_runtime_call(monkeypatch, tmp_path) -> None:
    context = make_context(actor_type="agent", actor_id="agent_v5_4c")
    bridge, adapter = make_v5_4c_bridge(monkeypatch, tmp_path)

    result = bridge.start_local_folder_summary(
        context,
        folder_path="tests/fixtures/desktop/技术分享",
        source="agent",
        actor_type="agent",
        user_confirmed=True,
    ).to_dict()

    assert adapter.call_count == 0
    assert result["status"] == "blocked"
    assert result["blocked_reason"] == "source_agent_cannot_execute_mutation"
    assert result["decision"]["agent_executable"] is False


def test_v5_4c_kill_switch_blocks_before_runtime_call(monkeypatch, tmp_path) -> None:
    context = make_context()
    kill_switches = KillSwitchRegistry()
    kill_switches.disable_workspace(context.workspace_id)
    bridge, adapter = make_v5_4c_bridge(monkeypatch, tmp_path)
    bridge = ExistingV4RuntimeTrialBridge(adapter, decision_service=CapabilityDecisionService(kill_switches=kill_switches))

    result = bridge.start_local_folder_summary(
        context,
        folder_path="tests/fixtures/desktop/技术分享",
        source="run_panel",
        actor_type="human_user",
        user_confirmed=True,
    ).to_dict()

    assert adapter.call_count == 0
    assert result["status"] == "blocked"
    assert result["blocked_reason"] == "kill_switch:workspace_kill_switch_active"
