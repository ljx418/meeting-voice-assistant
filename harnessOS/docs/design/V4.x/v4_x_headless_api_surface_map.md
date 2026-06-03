# V4.x Headless API Surface Map

Status: planning map for the Headless-first V4 roadmap, updated for Unified Experience Rebaseline.

This map describes the intended headless surfaces for V4.2-A and later stages. It is not an implementation contract and does not add callable routes or runtime authority.

## 1. Principle

Headless outputs are projections, commands, specs, reports, visualizations, and interaction state around the governed workflow runtime. They must not bypass the existing governance boundary.

Rules:

```text
WorkflowSpec does not replace WorkflowDraft / WorkflowVersion runtime truth.
Drawio files are visualization outputs only.
HTML reports are read-only outputs unless they link to explicit user-confirmed operations in Thin Web Console.
TUI commands that mutate durable state must require user_confirmed=true.
source=agent cannot execute mutation.
EventBridge only triggers refresh.
Interaction Orchestrator does not directly write runtime truth.
Experience State Machine is a shared UX read model.
Report Schema is a shared projection contract.
```

V4.2-A audit correction:

```text
V4.2-A defines Headless interaction contracts and evidence outputs.
Generic apply/publish/run/rerun implementation is not part of V4.2-A unless an existing V4.1 local workflow path already supports the operation.
Generic controlled execution belongs to V4.2-B/C.
```

## 2. Core Facts

| Object | Headless role | Runtime truth boundary |
| --- | --- | --- |
| WorkflowSpec | Portable workflow definition input/output for TUI and reports. | Does not directly mutate runtime truth. |
| WorkflowTemplate | Design structure source. | Durable backend object. |
| WorkflowDraft | Mutable design draft. | Mutated only through governed patch/apply paths. |
| WorkflowVersion | Published immutable snapshot. | Created only through user-confirmed publish. |
| WorkflowInstance | Runtime execution instance. | Started only through user-confirmed start. |
| Station | Workflow step definition. | Owned by template/draft/version. |
| StationRun | Runtime attempt record. | Created by governed runtime only. |
| Artifact | Produced or referenced output. | Registered through runtime/artifact boundary. |
| ArtifactLineage | Artifact relationship graph. | Read-only report and drawio source. |
| QualityEvaluation | Quality gate and result. | Runtime/governance output. |
| Approval | Human approval point. | User-confirmed approval panel/TUI action only. |
| WorkflowPatch | Governed proposal/change object. | Durable mutation only after user confirmation. |
| WorkflowContext | Business context. | Updated only through governed context mutation. |
| OperationEvidence | Audit/evidence object. | Read-only reporting source. |
| GovernanceReview | Review summary. | Read-only reporting source. |

## 2.1 Unified Experience DTOs

| Object | Role | Runtime truth boundary |
| --- | --- | --- |
| InteractionIntent | Captures user goal or command from Mission Console / TUI / Thin Web / Agent. | Does not execute mutation. |
| InteractionStateProjection | Shared UX state projection for all Heads. | Derived from governed sources. |
| AvailableActionDTO | Shows allowed and blocked actions. | Mutation requires user confirmation and BFF path. |
| HandoffRequest | Moves user to Review Console or operation panel. | Opening a handoff does not execute. |
| AgentPolicyDecision | Central policy decision for Agent and source boundaries. | `source=agent` cannot mutate. |
| RuntimeCapabilityMatrix | Supported / partial / planned / unsupported capability table. | Prevents false-green claims. |
| WorkflowReportDTO | Shared report projection. | Read-only. |
| EvidenceReportDTO | Shared evidence chain projection. | Read-only. |

## 3. Planned Headless Inputs

### Workflow spec files

```text
workflow.yaml
workflow.json
workflow.schema.json
```

Minimum planned sections:

```text
metadata
stations
edges
artifact_contracts
quality_rules
approval_points
context_refs
evidence_refs
```

The schema should be strict enough for validation but must not become a hidden runtime schema bypass.

### TUI user input

Example:

```text
创建一个工作流，递归总结 Desktop/技术分享 下的 Markdown 文件。
```

The TUI may create a draft spec or patch proposal. It may not apply, publish, run, or rerun without explicit user confirmation.

## 4. Planned Commands

V4.2-A read/spec/report commands:

```text
harness tui
harness workflow create
harness workflow diff
harness workflow status
harness artifacts list
harness quality report
harness evidence show
```

Deferred mutation commands:

```text
harness workflow apply
harness workflow publish
harness workflow run
harness station rerun
```

Deferred mutation commands require separate runtime backing. In V4.2-A they may only appear as user-confirmed transcript steps for the existing V4.1 local workflow or as planned UX contracts.

Command governance:

| Command | Planned behavior | Confirmation |
| --- | --- | --- |
| `harness workflow create` | Create local spec or proposal. | No durable mutation unless explicitly applying. |
| `harness workflow diff` | Show proposed changes. | Read-only. |
| `harness workflow apply` | Deferred mutating command; apply proposal to draft only through governed path. | Required; V4.2-B/C generic scope. |
| `harness workflow publish` | Deferred mutating command; publish version only through governed path. | Required; V4.2-B/C generic scope. |
| `harness workflow run` | Deferred mutating command; start workflow instance only through governed path. | Required; V4.2-B/C generic scope. |
| `harness workflow status` | Show status. | Read-only. |
| `harness station rerun` | Deferred mutating command; generic station rerun with attempt history is V4.2-B/C scope. | Required; V4.2-B/C generic scope. |
| `harness artifacts list` | List artifacts. | Read-only. |
| `harness quality report` | Show quality report. | Read-only. |
| `harness evidence show` | Show evidence chain. | Read-only. |

## 5. Planned Outputs

Drawio:

```text
workflow.drawio
workflow_status.drawio
artifact_lineage.drawio
quality_gate.drawio
rerun_history.drawio
```

HTML reports:

```text
workflow_board.html
station_detail.html
artifacts.html
quality.html
evidence.html
```

Evidence:

```text
tui-transcript.txt
exported-runtime-result.json
operation-evidence.json
result-summary.md
```

## 6. Browser Boundary

Thin Web Console may show and open reports, but it must continue to use BFF-only routes.

Browser must not directly call:

```text
/v1/rpc
/v1/events/subscribe
```

UI and report outputs must not expose:

```text
capability_token
subscription_token
Authorization
Bearer
secret
raw_trace_payload
raw_artifact_content
raw_connector_payload
raw prompt
upstream signed URL
```

## 7. No False Green

This map does not prove:

```text
complete Workflow Studio ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
```
