from __future__ import annotations

import json
from pathlib import Path

from core.auth.tenant_boundary import IdentityContext
from core.product_console.v9_6_workflow_studio import (
    build_manual_confirmation,
    build_workflow_diff_proposal,
    build_workflow_studio_state,
    write_v9_6_evidence,
)


OUT_DIR = Path("docs/design/V9.x/evidence/v9-6-workflow-studio")


def make_context() -> IdentityContext:
    return IdentityContext(
        tenant_id="tenant_v9_6",
        workspace_id="workspace_v9_6",
        project_id="project_v9_6",
        app_id="app_v9_6",
        actor_type="human_user",
        actor_id="user_v9_6_reviewer",
        user_id="user_v9_6_reviewer",
        service_account_id="service_account_v9_6",
        request_id="request_v9_6",
        correlation_id="correlation_v9_6",
    )


def build_state():
    context = make_context()
    proposal = build_workflow_diff_proposal(
        context,
        natural_language_goal="减少一个冗余审查工位，并新增安全审查 Agent。",
        workflow_spec_ref="workflow-spec://v9-6/studio-productization",
        target_refs={"workflow_id": "workflow-v9-6", "workflow_version_id": "workflow-version-v9-6"},
    )
    confirmation = build_manual_confirmation(context, proposal=proposal, expires_at="2999-01-01T00:00:00+00:00")
    return build_workflow_studio_state(
        context,
        workflow_graph={
            "nodes": ["intent", "architect", "security-review", "runtime-report"],
            "edges": [["intent", "architect"], ["architect", "security-review"], ["security-review", "runtime-report"]],
        },
        station_agent_profiles=[
            {"station_id": "intent", "agent_id": "agent-intent", "role": "目标澄清", "tool_refs": ["tool://tui-input"]},
            {"station_id": "architect", "agent_id": "agent-architect", "role": "工作流架构", "tool_refs": ["tool://workflow-diff"]},
            {"station_id": "security-review", "agent_id": "agent-security", "role": "安全审查", "tool_refs": ["tool://evidence-chain"]},
        ],
        runtime_report={"status": "ready_for_review", "attempts": [{"attempt_id": "attempt-v9-6-1"}]},
        evidence_chain={"evidence_refs": ["evidence://v9-3/orchestration", "evidence://v9-4/coding", "evidence://v9-5/terminal"], "claim_scan": "PASS", "redaction_scan": "PASS"},
        artifact_lineage=[{"artifact_id": "artifact-v9-6-blueprint", "producer_agent_id": "agent-architect", "producer_attempt_id": "attempt-v9-6-1"}],
        workflow_diff_proposal=proposal,
        manual_confirmation=confirmation,
        browser_network_log=[
            "GET /bff/v9/studio-state",
            "GET /bff/v9/runtime-report",
            "GET /bff/v9/evidence-chain",
            "GET /bff/v9/workflow-blueprint",
            "POST /bff/v9/workflow-diff-proposal",
            "POST /bff/v9/manual-confirmation",
            "POST /bff/v9/review-handoff",
        ],
        source_refs={
            "workflow_blueprint": "docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json",
            "agent_profiles": "docs/design/V9.x/evidence/v9-3-orchestration-runtime/user-scenarios.json",
            "runtime_report": "docs/design/V9.x/evidence/v9-4-coding-workflow-runtime/acceptance-data.json",
            "evidence_chain": "docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json",
            "artifact_lineage": "docs/design/V9.x/evidence/v9-3-orchestration-runtime/acceptance-data.json",
        },
    )


def main() -> int:
    acceptance = write_v9_6_evidence(build_state(), OUT_DIR)
    print(json.dumps({"status": acceptance["status"], "output": str(OUT_DIR / "index.html")}, ensure_ascii=False, indent=2))
    return 0 if acceptance["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
