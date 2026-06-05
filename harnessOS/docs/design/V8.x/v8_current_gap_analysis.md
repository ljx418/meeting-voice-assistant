# V8 Current Gap Analysis

文档状态：V8 gap analysis，当前 V8-4 real runtime fixture PASS，V8-6 controlled terminal worker fixture PASS，V8-7 bounded runtime fixture PASS，V8-8 read-model TUI PASS，V8-9 final framework PASS。

## 1. Current Baseline

```text
V7 complete: small studio production pilot and explainable TUI baseline ready for review.
```

V7 可以作为 V8 输入，但不能被反向升级为 Agent executor ready、complete Workflow Studio ready 或 production ready。

## 2. Gap Table

| Area | Current V7 State | V8 Required State | Status | Owner Stage | Blocker |
| --- | --- | --- | --- | --- | --- |
| Station Agent | Station uses workflow logic and LLM provider adapter | Every station has independent AgentDescriptor | complete_for_review | V8-1 | no |
| Agent Role / Goal | Role exists mostly in prompts or product docs | Explicit role / goal per Agent | complete_for_review | V8-1 | no |
| Agent Memory | No station-level memory policy | Station-scoped memory policy and memory refs | complete_for_review | V8-2 | no |
| Agent Context | Prompt refs and artifact refs exist | StationAgentContextEnvelope with strict redaction | complete_for_review | V8-2 | no |
| Per-Agent Model | Provider invocation exists | Model profile per station Agent | complete_for_review | V8-2 | no |
| Skill Binding | Skill registry exists but not per station Agent | AgentSkillBinding with allowlist | complete_for_review | V8-3 | no |
| MCP Binding | MCP connector runtime exists in parts | AgentMcpBinding with allowlist and evidence | complete_for_review | V8-3 | no |
| Station Agent Runtime | Local document workflow runs without per-station Agent | Agentized local document workflow pilot | PASS / real_runtime_fixture | V8-4 | no |
| Terminal Worker | Codex / Claude / connector traces exist historically | Governed terminal worker design and pilot | PASS / controlled_runtime_fixture | V8-5 / V8-6 | no |
| Multi-Agent Project Workflow | Distributed runtime pilot exists, not per-station coding Agent workflow | bounded multi-Agent project workflow pilot | PASS / bounded_runtime_fixture | V8-7 | no |
| TUI Explainability | V7 TUI state line exists and V8 evidence HTML exists | per-Agent status / capability / evidence TUI view | PASS / read_model | V8-8 | no |
| Final Acceptance | V7 acceptance dashboard exists | V8 Station Agent acceptance dashboard | PASS / final_acceptance_framework | V8-9 | no |

## 3. Documentation Readiness Assessment

当前 V8 已完成 V8-1 到 V8-4 的 bounded station-agent local document workflow pilot，完成 V8-5 高风险设计门禁，并在用户明确授权范围内完成 V8-6 controlled terminal worker fixture 与 V8-7 bounded multi-Agent project workflow runtime fixture。V8-7 仍不能声明完整多 Agent 编排、Agent executor 或自主代码工作流。

```text
V8-4 evidence package: docs/design/V8.x/evidence/v8-4-station-agent-runtime/
status: PASS
evidence_scope: real_runtime_fixture
station_count: 7
agent_descriptor_count: 7
scanner_actual_read_count: 5
provider_invocation_count: 4
claim_scan: PASS
redaction_scan: PASS
terminal_worker_enabled: false
V8-6 evidence package: docs/design/V8.x/evidence/v8-6-controlled-terminal-worker/
status: PASS
evidence_scope: controlled_runtime_fixture
workspace_scope_guard: PASS
command_allowlist: PASS
diff_proposal_captured: PASS
source_agent_mutation_denied: PASS
auto_commit_enabled: false
auto_push_enabled: false
V8-8 evidence package: docs/design/V8.x/evidence/v8-8-agent-explainability-tui/
status: PASS
evidence_scope: read_model_from_v8_4_v8_6_evidence
readonly: true
panel_count: 8
tui_does_not_construct_runtime_truth: PASS
V8-7 evidence package: docs/design/V8.x/evidence/v8-7-multi-agent-project-workflow/
status: PASS
evidence_scope: bounded_runtime_fixture
station_count: 8
agent_descriptor_count: 8
implementation_agent_uses_handoff_not_direct_shell: PASS
source_agent_mutation_denied: PASS
V8-9 final framework: docs/design/V8.x/evidence/v8-9-final-acceptance-framework/
status: PASS
final_claim_allowed: true
blockers: 0
```

## 4. Gap Classification

```text
inherited_from_v7: V7 evidence can be reused as input only.
planned: V8 documentation / implementation / validation required.
high_risk: requires human proceed decision before implementation.
out_of_scope: outside V8 default scope.
```

## 5. No False Green Notes

V8 gap 文档不得把以下状态写成完成：

```text
Agent executor ready
production Agent executor ready
autonomous coding workflow ready
full multi-Agent orchestration ready
complete Workflow Studio ready
unrestricted terminal worker ready
ChromeCLI production automation ready
```
