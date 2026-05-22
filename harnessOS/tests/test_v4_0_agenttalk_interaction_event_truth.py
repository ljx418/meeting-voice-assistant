"""V4.0-P AgentTalk event truth regression tests."""

from __future__ import annotations

from pathlib import Path


def test_frontend_refreshes_agent_truth_from_bff_instead_of_event_payload() -> None:
    hook = Path("apps/workflow-console/src/hooks/useWorkflowConsoleData.ts").read_text(encoding="utf-8")

    assert "agent.action_proposal.created" in hook
    assert "agent.handoff_created" in hook
    assert "operation.evidence.created" in hook
    assert "refreshWorkflowConsoleRuntimeState(client, loaded)" in hook
    assert "getAgentInteractionState" in hook
    assert "loadGovernanceState(client, current.selectedInstanceId)" in hook
    assert "event.data?.selected_proposal_id" not in hook
    assert "event.data?.selected_patch_id" not in hook
    assert "event.data?.evidence_id" not in hook
