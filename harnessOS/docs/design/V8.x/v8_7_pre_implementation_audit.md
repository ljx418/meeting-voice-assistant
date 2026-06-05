# V8-7 Multi-Agent Project Workflow Pre-Implementation Audit

文档状态：V8-7 pre-implementation audit / high-risk gate。

## Current Decision

```text
NO_GO_FOR_RUNTIME_IMPLEMENTATION
```

V8-7 可以继续做 planning refinement、contract alignment、test matrix finalization、evidence package design 和 high-risk decision preparation。不得在本审计通过前进入 runtime implementation。

## Dependency Evidence

```text
V8-4 station-agent runtime evidence: PASS / real_runtime_fixture
V8-6 controlled terminal worker evidence: PASS / controlled_runtime_fixture
```

可继承：

```text
per-station AgentDescriptor
station-scoped context envelope
capability decisions and forbidden reasons
LLM invocation evidence
source=agent durable mutation denial
workspace-scoped readonly terminal handoff
transcript capture
diff proposal capture
```

不得继承为已完成：

```text
Agent executor ready
autonomous coding workflow ready
full multi-Agent orchestration ready
unrestricted terminal worker ready
production browser automation
auto commit / push / publish
```

## Required V8-7 Contracts

V8-7 runtime implementation 前必须补齐或确认：

```text
ProjectWorkflowSpec
ProjectStationAgentMap
ProjectAgentHandoff
ProjectAttemptHistory
ProjectArtifactLineage
ProjectReviewArtifact
ProjectEvidenceBundle
ProjectExplainerSummary
```

## Minimum Bounded Pilot

V8-7 最小运行范围只能是：

```text
ProductAgent -> ArchitectureAgent -> PlanningAgent -> ImplementationAgent -> TestAgent -> ReviewAgent -> EvidenceAgent -> ExplainerAgent
```

其中：

```text
ImplementationAgent 只能生成 controlled terminal worker handoff proposal。
TestAgent 只能请求 allowlisted readonly test command。
ReviewAgent 只能生成 review artifact。
EvidenceAgent 只能汇总 transcript / diff proposal / test output。
ExplainerAgent 只能解释流程、证据和禁止原因。
```

## Required Test Matrix

```text
project_workflow_requires_agent_for_each_station
project_workflow_requires_explainer_agent
implementation_agent_uses_handoff_not_direct_shell
test_agent_uses_allowlisted_readonly_command
source_agent_durable_mutation_denied
auto_commit_push_publish_denied
attempt_history_retained
review_artifact_exists
evidence_agent_links_transcript_diff_test_output
project_explainer_links_agent_evidence
v8_7_no_false_green_scan_pass
v8_7_redaction_scan_pass
```

## Stop Conditions

```text
V8-7 claims Agent executor ready.
V8-7 claims full multi-Agent orchestration ready.
Any Agent directly commits, pushes, publishes, applies patch, or writes runtime truth.
source=agent bypasses user confirmation or controlled terminal worker handoff.
Terminal worker executes outside workspace scope.
Raw secret / raw prompt / raw artifact content appears in evidence.
```

## Audit Opinion

```text
spec_drift_risk=MEDIUM
false_green_risk=HIGH
runtime_implementation_allowed=false
```

V8-7 是高风险阶段。当前 V8-4 / V8-6 evidence 足以支撑实现前审计和设计收敛，但不足以直接声明 multi-Agent project workflow pilot complete。
