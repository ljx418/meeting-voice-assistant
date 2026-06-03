# V5-4B Target Architecture Delta

文档状态：V5-4B synthetic-only core slice implemented for review。

## Trial Components

```text
ControlledExecutorTrialRunner
UserConfirmedActionGate
ApprovalGatedActionGate
TrialSandboxAdapter
TrialRuntimeEvidenceRecorder
TrialKillSwitch
```

## Boundary

```text
dev/local trial only
no production executor service
no production connector mutation
no autonomous Agent execution
```

## Implemented Core Slice

```text
core/policies/controlled_executor_trial.py
 -> ControlledExecutorTrialRunner
 -> SyntheticWorkflowState
 -> SyntheticStationState
 -> TrialAttempt
 -> TrialRuntimeEvidence
```

V5-4B uses V5-4A CapabilityDecisionService before any synthetic state change. It does not call the V4 local workflow runtime. That integration is deferred to V5-4C.
