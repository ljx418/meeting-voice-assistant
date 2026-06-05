# V8 Development And Acceptance Plan

文档状态：V8 development and acceptance control plan，当前 V8-4 real runtime fixture PASS，V8-6 controlled runtime fixture PASS，V8-7 bounded runtime fixture PASS，V8-8 read-model TUI PASS，V8-9 final framework PASS。

## 1. Stage Status Table

| Stage | Purpose | Current Status | Allowed Claim | Boundary |
| --- | --- | --- | --- | --- |
| V8-0 | Station Agent Planning Gate | complete_for_review | V8-0 complete: station-agent workflow planning gate ready for review. | documentation only |
| V8-1 | Station Agent Contract | complete_for_review | V8-1 complete: station agent contract baseline ready for review. | no generic Agent executor |
| V8-2 | Agent Context And Memory | complete_for_review | V8-2 complete: station agent context and memory contract ready for review. | no raw context leakage |
| V8-3 | Skill / MCP / Tool Binding | complete_for_review | V8-3 complete: station agent skill and MCP capability binding baseline ready for review. | allowlist only |
| V8-4 | Station Agent Runtime Pilot | PASS / real_runtime_fixture | V8-4 complete: station-agent local document workflow pilot ready for review. | local workflow pilot only |
| V8-5 | Terminal Worker Design Gate | complete_for_review / high-risk | V8-5 complete: terminal worker design gate ready for review. | design only |
| V8-6 | Controlled Terminal Worker Pilot | PASS / controlled_runtime_fixture | V8-6 complete: controlled terminal worker pilot ready for review. | no autonomous terminal executor |
| V8-7 | Multi-Agent Project Workflow Pilot | PASS / bounded_runtime_fixture | V8-7 complete: multi-agent project workflow pilot ready for review. | bounded pilot only |
| V8-8 | Agent Explainability TUI | PASS / read_model | V8-8 complete: agent explainability TUI baseline ready for review. | read-model experience |
| V8-9 | Final Acceptance | PASS / final_acceptance_framework | V8 complete: station-agent workflow pilot ready for review. | not Agent executor ready |

## 2. Development Order

```text
V8-0 -> V8-1 -> V8-2 -> V8-3 -> V8-4 -> V8-5 -> V8-6 -> V8-7 -> V8-8 -> V8-9
```

V8-5 / V8-6 / V8-7 are high-risk stages. They require separate human proceed decisions before implementation.

## 3. Implementation Readiness Requirements

Before V8-1 implementation:

```text
V8-0 accepted.
StationAgentDescriptor contract accepted.
Agent role / goal / model / memory / skill / MCP schema accepted.
V8 schema contract pack accepted.
Station Agent runtime I/O contract accepted.
Skill / MCP / Tool capability contract accepted.
Evidence package contract accepted.
No False Green guard accepted.
V8 drawio XML valid.
External audit has no critical or major open issue.
```

Before V8-4 implementation:

```text
V8-1 / V8-2 / V8-3 evidence exists.
Local Markdown workflow agentization plan accepted.
WorkflowExplainerAgent required.
source=agent durable mutation denial test matrix accepted.
```

Before V8-6 implementation:

```text
V8-5 terminal worker design gate accepted.
Terminal worker high-risk contract accepted.
Human high-risk proceed decision recorded.
Workspace scope guard accepted.
Command allowlist accepted.
Transcript / diff capture accepted.
Kill switch and timeout policies accepted.
```

## 3.1 P0 Contract References

```text
docs/design/V8.x/v8_schema_contract_pack.md
docs/design/V8.x/v8_station_agent_runtime_io_contract.md
docs/design/V8.x/v8_skill_mcp_tool_contract.md
docs/design/V8.x/v8_terminal_worker_high_risk_contract.md
docs/design/V8.x/v8_agent_explainability_tui_contract.md
docs/design/V8.x/v8_evidence_package_contract.md
docs/design/V8.x/v8_implementation_readiness_audit.md
```

## 4. Test Matrix

```text
station_agent_descriptor_required_for_each_station
workflow_requires_explainer_agent
agent_context_scope_no_raw_secret
agent_context_scope_no_raw_prompt
agent_model_profile_per_station
skill_binding_allowlist_enforced
mcp_binding_allowlist_enforced
source_agent_durable_mutation_denied
terminal_worker_requires_human_handoff
codex_worker_diff_capture_required
claude_worker_transcript_capture_required
chromecli_connector_high_risk_guard
agent_evidence_chain_complete
agent_tui_explainability_links_complete
v8_no_false_green_scan_pass
v8_redaction_scan_pass
```

## 5. Validation Commands

```text
python -m pytest tests/test_v8_*.py -q
python -m pytest tests/test_v7_*.py -q
python -m pytest tests/test_v6_*.py -q
xmllint --noout docs/design/V8.x/v8_current_gap_analysis.drawio
```

Latest validation:

```text
python -m pytest tests/test_v8_*.py -q -> 15 passed
python -m pytest tests/test_v8_*.py tests/test_v7_*.py tests/test_v6_*.py -q -> 137 passed
python -m pytest -q -> 1117 passed, 3 skipped
xmllint --noout docs/design/V8.x/v8_current_gap_analysis.drawio docs/design/V8.x/evidence/v8-4-station-agent-runtime/workflow.drawio docs/design/V8.x/evidence/v8-4-station-agent-runtime/workflow_status.drawio -> PASS
V8-4 real provider evidence -> status=PASS, provider_invocation_count=4, folder_summaries_llm_backed=PASS, overview_summary_llm_backed=PASS
V8-6 controlled terminal worker evidence -> status=PASS, workspace_scope_guard=PASS, command_allowlist=PASS, diff_proposal_captured=PASS
V8-8 Agent explainability TUI evidence -> status=PASS, readonly=true, panel_count=8
V8-7 bounded multi-Agent project workflow evidence -> status=PASS, station_count=8, agent_descriptor_count=8, implementation_agent_uses_handoff_not_direct_shell=PASS
V8-9 final acceptance framework -> status=PASS, final_claim_allowed=true, blockers=0
python -m pytest tests/test_v8_*.py -> 23 passed
python -m pytest tests/test_v8_*.py tests/test_v7_*.py tests/test_v6_*.py -> 145 passed
python -m pytest -q -> 1125 passed, 3 skipped
latest python -m pytest tests/test_v8_*.py -> 29 passed
latest python -m pytest tests/test_v8_*.py tests/test_v7_*.py tests/test_v6_*.py -> 151 passed
latest python -m pytest -q -> 1131 passed, 3 skipped
```

## 6. Stop Conditions

```text
V8 claims Agent executor ready.
Any Agent performs durable mutation without user_confirmed=true.
source=agent bypasses controlled runtime.
Terminal worker executes outside workspace scope.
ChromeCLI automates production account actions.
MCP / Skill / Tool call bypasses allowlist.
Raw secret / raw prompt / raw artifact content appears in evidence.
V8-9 final claim emitted without V8-0..V8-8 evidence.
```
