# V4.2-B Controlled Runtime Design Gate Plan

Status: complete.

Allowed completion claim:

```text
V4.2-B complete: controlled runtime design gate ready for implementation review.
```

Forbidden claims:

```text
forbidden controlled executor ready
forbidden Agent executor ready
forbidden autonomous workflow editing ready
forbidden complete Workflow Studio ready
forbidden complete AgentTalkWindow ready
forbidden production-ready external app support
forbidden full multi-Agent orchestration ready
```

## 1. Stage Goal

V4.2-B is the implementation gate before V4.2-C. It defines the minimum controlled runtime contract and acceptance standard, but does not add runtime routes, executor workers, connector/model invocation paths, production auth, or Agent execution.

V4.2-B exists to prevent V4.2-C from accidentally expanding into an uncontrolled executor.

## 2. Boundaries

V4.2-B must preserve:

```text
source=agent cannot execute mutation
user_confirmed=true required for durable mutation
high-risk actions remain approval-gated
EventBridge refresh-only
executor reads only redacted or approved inputs
WorkflowSpec / Drawio / HTML reports are not runtime truth
```

V4.2-B must not implement:

```text
generic workflow start
generic station rerun
controlled executor runtime
Agent executor
connector.call
external_llm.call
production filesystem permission model
production auth / tenant control plane
forbidden production-ready external app support
```

## 3. PR Slices

### PR1 Contract Baseline

Add a machine-readable design gate contract:

```text
docs/design/V4.2/v4_2_b_controlled_runtime_design_gate_contract.json
```

The contract must mark:

```text
implementation_enabled=false
generic_runtime_mutation_enabled=false
agent_mutation_enabled=false
```

### PR2 Runtime Acceptance Definition

Define V4.2-C acceptance for:

```text
generic workflow start
generic station rerun
StationRun attempt history
downstream stale propagation
artifact sandbox
timeout and kill switch baseline
runtime result evidence
```

### PR3 Real Data Validation Requirement

V4.2-C must use the V4.1 local recursive Markdown workflow as the first real-data validation fixture:

```text
tests/fixtures/desktop/技术分享
tests/fixtures/desktop/技术分享_损坏
```

The V4.2-C acceptance cannot pass on static reports alone.

### PR4 Route And Capability Guard

V4.2-B must not add callable routes for:

```text
/execute
/agent/execute
/kill-switch
/rollback
/admin-override
/connector/call
/external-llm/call
```

Any future V4.2-C operation must require user confirmation and source guard.

### PR5 Documentation Sync

Synchronize:

```text
docs/design/V4.2/00_README.md
docs/design/V4.x/v4_x_headless_current_gap_analysis.md
docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
docs/design/V4.1/v4_1_stage_gate_development_plan.md
docs/design/V4.1/v4_x_auditable_development_blueprint.md
docs/design/V4.x/v4_x_headless_first_roadmap.md
```

## 4. Completion Evidence

V4.2-B completion requires:

```text
design gate contract exists
acceptance document exists
audit document exists
completion note exists
contract tests pass
claim guard passes
V4.2 focused tests pass
V4.0/V4.1 regression remains green
gap md and drawio reflect V4.2-B complete and V4.2-C next
```
