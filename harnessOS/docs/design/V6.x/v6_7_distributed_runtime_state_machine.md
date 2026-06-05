# V6-7 Distributed Runtime State Machine

文档状态：V6-7 complete / ready for review contract。本文定义状态语义，已由 V6-7 pilot runtime slice 实现验证。

## State Model

Distributed run state:

```text
draft
 -> awaiting_human_high_risk_decision
 -> ready_for_assignment
 -> assigning_workers
 -> running
 -> partially_failed
 -> recovering
 -> completed
 -> failed
```

Station branch state:

```text
pending
 -> assigned
 -> running
 -> completed
 -> failed
 -> stale
 -> retry_scheduled
 -> recovered
```

Worker state:

```text
registered
 -> available
 -> assigned
 -> running
 -> lost
 -> timeout
 -> recovered
 -> failed
 -> released
```

## Serial Branch Rules

- A downstream station may enter `pending` only after upstream dependency is `completed` or explicitly waived by policy.
- If an upstream retry creates a new attempt, downstream stations become `stale`.
- Old downstream artifacts remain visible as prior versions and cannot be silently overwritten.

## Parallel Branch Rules

- Parallel branches have independent `branch_id` and `branch_state`.
- One branch failure must not overwrite sibling branch attempts.
- Synthesis or join station may start only after required branches reach `completed`, or after policy marks failed branches as accepted exceptions.

## Recovery Rules

- `worker_lost` may transition to `retry_scheduled`, `recovered`, or `failed`.
- Retry creates a new attempt and keeps old attempt plus old error.
- Recovery emits incident timeline event and audit_ref.
- Mark failed preserves the last known checkpoint and failure evidence.

## Runtime Truth Boundary

The state machine is a production pilot runtime model only after V6-7 implementation is explicitly approved. Before that, it is a design contract and must not be treated as runtime truth.
