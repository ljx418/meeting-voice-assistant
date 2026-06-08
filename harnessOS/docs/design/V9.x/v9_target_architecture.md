# V9 Target Architecture

文档状态：V9 target architecture / V9-2 evidence-aligned baseline。

## 1. Architecture Goal

V9 在 V8 Station Agent Operating Layer 上新增高风险执行和产品化平面：

```text
Agent Execution Plane
Multi-Agent Orchestration Plane
Autonomous Coding Workflow Plane
Workflow Studio Productization Plane
Governed Terminal Worker Plane
Production Governance / Evidence Hardening and Terminal Automation Gate
```

目标是让 Agent 可以在受控、可审计、可回滚的边界内执行，而不是成为无限制 executor。

## 1.1 Current Architecture Delta After V9-2

当前已落地并可审计的架构切片：

```text
Agent Executor Safety Gate validators
HumanAuthorizationRef validator
CapabilityResolver deny-by-default engine
V9-2 limited controlled runtime fixture for four operations
Append-only execution evidence for V9-2 fixture
No False Green / redaction validation reports
```

当前仍未落地的目标架构切片：

```text
OrchestrationCoordinator runtime with serial / parallel / fan-in / fan-out.
CodingWorkflowRuntime with diff / test / review / fix-loop.
TerminalWorkerSandbox write expansion.
WorkflowStudioBFF product UI.
ProductionGovernanceAutomationGate runtime evidence.
V9 final evidence aggregation dashboard.
Creative workflow scenario adapters for Roman Forum debate and video storyboard generation.
Natural-language workflow optimization proposal path.
```

V9-2 的 ControlledAgentExecutor 仍是 limited runtime fixture，不是 production executor route，也不是 runtime worker。

## 2. Target Planes

```text
Small Studio / Workflow Studio Plane
Mission TUI Plane
Workflow Blueprint Plane
Station Agent Operating Layer
Agent Execution Plane
Multi-Agent Orchestration Plane
Autonomous Coding Workflow Plane
Skill / MCP / Tool Capability Plane
Governed Terminal Worker Plane
Controlled Runtime Plane
Credential / Tenant / Policy Plane
Runtime Report Plane
Review Console Plane
Evidence And Audit Plane
Production Governance / Evidence Hardening and Terminal Automation Gate
```

## 3. Target Architecture Flow

```text
User Goal
 -> Mission TUI / Workflow Studio
 -> WorkflowSpec / Diff / Blueprint
 -> Agent Registry
 -> Orchestration Planner
 -> AgentExecutionEnvelope
 -> CapabilityResolver
 -> ApprovalGate / HumanAuthorization
 -> Controlled Agent Executor
 -> Skill / MCP / Tool / Terminal Worker
 -> Attempt History / Artifact Lineage
 -> Runtime Report
 -> Review Console
 -> Evidence Chain
 -> Studio / TUI Explainability
```

## 4. New Components

| Component | Responsibility | Boundary |
| --- | --- | --- |
| AgentExecutionPolicy | Defines allowed Agent actions by role, stage, tenant and risk | policy only |
| AgentExecutionEnvelope | Carries actor, source, scope, target refs, approval refs and idempotency key | no raw secret or raw payload |
| ControlledAgentExecutor | Executes only the V9-2 allowlisted fixture actions today; target is approved actions only | not unrestricted executor; no production route / worker |
| OrchestrationCoordinator | Coordinates serial, parallel and fan-in/fan-out runs | next implementation candidate; keeps attempt history |
| CodingWorkflowRuntime | Runs planning, implementation, test, review and fix loops | no auto commit / auto push / auto deploy by default |
| DebateWorkflowAdapter | Maps a discussion goal into role-specific Agents, multi-round messages and attributed synthesis | V9-3 user scenario fixture; not full orchestration GA |
| StoryboardWorkflowAdapter | Maps a video idea into brief, script, shot list, storyboard prompts and image artifact refs | provider-backed or explicitly fallback; no raw prompt leakage |
| WorkflowOptimizationPlanner | Converts natural-language optimization requests into WorkflowDiff proposals | no durable mutation before confirmation |
| TerminalWorkerSandbox | Runs scoped commands and captures transcript/diff | no arbitrary shell by default |
| WorkflowStudioBFF | Product UI boundary for Studio operations | no direct runtime truth writes |
| ProductionGovernanceAutomationGate | High-risk gate for production governance, evidence hardening and terminal/browser automation | separate approval, credential, evidence and incident review |

## 5. Runtime Truth Boundary

V9 必须保留并强化：

```text
WorkflowSpec does not replace WorkflowDraft / WorkflowVersion.
Workflow Studio cannot directly write WorkflowStore / StationRun / Artifact.
AgentExecutionEnvelope is request evidence, not runtime truth.
EventBridge only triggers refresh.
Evidence Chain is read-only.
Runtime Report is read-only.
source=agent cannot default durable mutation.
Durable mutation requires user_confirmed=true or human_authorization_ref.
source=agent default durable mutation remains denied even when an Agent proposes the operation.
HumanAuthorizationRef binds issuer, operation hash, target refs, expiry, revocation and audit linkage.
Terminal worker cannot escape workspace sandbox.
Credential leases cannot expose raw secret.
Image generation providers expose redacted invocation refs only.
Workflow optimization from natural language produces proposal / diff / handoff first.
```

## 6. High-Risk Boundaries

需要独立人工决策的阶段：

```text
V9-1 Agent executor safety gate acceptance
V9-2 controlled Agent execution runtime
V9-4 autonomous coding workflow
V9-5 terminal worker write sandbox
V9-7 production governance / evidence hardening and terminal automation gate
```

## 7. Exit Architecture

V9 完成后最多声明：

```text
V9 complete: high-risk Agent execution and workflow productization baseline ready for review.
```

它仍不得默认证明：

```text
full production GA
unrestricted Agent executor
unrestricted terminal worker
production browser automation
complete Workflow Studio GA
```
