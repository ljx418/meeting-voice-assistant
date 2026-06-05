# V9 Target Architecture

文档状态：V9 target architecture / planning baseline。

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
| ControlledAgentExecutor | Executes only approved actions | not unrestricted executor |
| OrchestrationCoordinator | Coordinates serial, parallel and fan-in/fan-out runs | keeps attempt history |
| CodingWorkflowRuntime | Runs planning, implementation, test, review and fix loops | no auto commit / auto push / auto deploy by default |
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
