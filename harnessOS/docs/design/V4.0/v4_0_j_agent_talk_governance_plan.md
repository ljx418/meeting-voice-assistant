# V4.0-J AgentTalk Governance & Controlled Executor Preparation Plan

文档状态：V4.0-J complete implementation baseline；completion evidence 见 `v4_0_j_agent_talk_governance_completion_note.md`。

## Positioning

V4.0-J builds on:

```text
V4.0-G complete: governed patch apply/reject/publish editing hardening ready.
V4.0-H complete: canvas-to-runtime patch bridge ready.
V4.0-I complete: governed stateful Agent assistant baseline ready.
```

V4.0-J does not implement a real autonomous Agent executor. It makes Agent suggestions governable, auditable, dismissible and transferable to user-confirmed panels.

## Allowed Scope

```text
Agent reads board/status/context/patch/quality/approval summary.
Agent explains workflow / station / event / quality issue.
Agent creates action proposal.
Agent creates patch proposal.
Agent asks user to navigate to Editing / Approval / Context / Quality / Artifact panels.
Agent action proposal writes redacted BFF audit record.
Agent suggestion and proposal lifecycle are traceable in dev/local BFF state.
```

## Forbidden Scope

```text
Agent auto apply patch
Agent auto reject patch
Agent auto publish version
Agent auto approval.respond
Agent auto workflow.context.update
Agent auto business.event.emit
Agent auto start workflow
Agent auto rerun station
Agent call external LLM / MCP / connector
Agent bypass BFF / SDK / hooks / V3.6 runtime contract
Agent write WorkflowStore / WorkflowDraft / WorkflowVersion directly
```

## Action Policy Classes

```text
display_only:
  explain_workflow
  summarize_events
  summarize_quality
  summarize_context
  show_approval_notice
  show_patch_diff
  show_context_summary

navigation:
  open_editing_panel
  open_approval_panel
  open_context_panel
  open_quality_panel
  open_artifact_panel

proposal_only:
  propose_patch
  propose_context_update
  propose_approval_decision
  propose_station_rerun

forbidden:
  apply_patch
  reject_patch
  publish_version
  respond_approval
  update_context
  emit_business_event
  start_workflow
  rerun_station
  call_connector
  call_external_llm
```

## BFF Routes

```text
GET  /bff/instances/{workflow_instance_id}/agent/action-proposals
POST /bff/instances/{workflow_instance_id}/agent/action-proposals
GET  /bff/instances/{workflow_instance_id}/agent/action-proposals/{proposal_id}
POST /bff/instances/{workflow_instance_id}/agent/action-proposals/{proposal_id}/dismiss
```

No `/execute`, `/run`, `/apply`, or `/publish` Agent action route is added.

## Capability Profile

```text
agent_actions.read
agent_actions.write
agent_talk.read
agent_talk.write
agent_suggestions.read
agent_suggestions.write
```

Default Agent routes must not require:

```text
workflow_patches.write
workflow_versions.publish
approvals
workflow_context.write
business_events.write
workflows.execute
```

## PR Slices

1. Agent governance contract and DTOs.
2. BFF Agent action proposal routes.
3. Agent action policy guard.
4. Agent proposal queue UI.
5. Audit / redaction / EventBridge refresh boundaries.
6. Tests / docs / drawio / completion note.

## Test Plan

```text
tests/test_v4_0_agent_action_proposals_bff.py
tests/test_v4_0_agent_action_policy_guard.py
tests/test_v4_0_agent_action_scope.py
tests/test_v4_0_agent_action_redaction.py
apps/workflow-console/src/__tests__/agentActionGovernance.test.tsx
apps/workflow-console/e2e/workflow-agent-governance-smoke.spec.ts
```

## Exit Claim

Allowed:

```text
V4.0-J complete: AgentTalk governance and controlled action proposal baseline ready for dev/local Workflow Console.
```

Forbidden:

```text
complete AgentTalkWindow ready
complete Workflow Studio ready
autonomous workflow editing ready
controlled executor ready
production-ready external app support
enterprise auth/OAuth/SSO ready
```
