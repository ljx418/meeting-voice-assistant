# V5-4A Target Architecture Delta

文档状态：V5-4A core slice implemented for review。

## Logical Components

```text
ExecutorPolicyMatrix
CapabilityDecisionService
ApprovalGatePlanner
ExecutorSandboxBoundary
KillSwitchRegistry
RuntimeEvidenceContract
```

## Data Flow

```text
RequestedAction
 -> ExecutorPolicyMatrix
 -> CapabilityDecisionService
 -> ApprovalGatePlanner
 -> ExecutorSandboxBoundary
 -> RuntimeEvidenceContract
```

## Boundary

```text
V5-4A does not run executor actions.
V5-4A does not grant Agent mutation authority.
V5-4A only decides whether a future trial may be designed.
```

## Implemented Core Slice

```text
core/policies/executor_safety.py
 -> ExecutorPolicyMatrix
 -> CapabilityDecisionService
 -> ApprovalGatePlanner
 -> ExecutorSandboxBoundary
 -> KillSwitchRegistry
 -> RuntimeEvidenceContract
```

All decisions set runtime_execution_allowed=false. A user-confirmed action can only be classified as handoff/evidence-ready inside the safety gate; it is not executed by V5-4A.
