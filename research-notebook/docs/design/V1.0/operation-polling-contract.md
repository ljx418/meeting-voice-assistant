# ResearchNotebook V1.0 Operation Polling Contract

文档状态：P0 implementation contract；V1.0-M3 frozen。
适用阶段：M2-M3。

## 1. Purpose

Workspace build and session build are long-running operations. V1.0 must implement one shared polling model rather than separate ad hoc polling logic.

## 2. Hook Shape

Recommended hook:

```ts
useOperationPolling({
  operationId,
  scope: "workspace" | "session",
  getStatus,
  cancel,
});
```

Where:

- `operationId`: service-owned operation identifier;
- `getStatus`: typed adapter function for status polling;
- `cancel`: optional typed adapter function;
- `scope`: `"workspace"` or `"session"`.

## 3. Required States

The UI must handle:

- `queued`;
- `running`;
- `completed`;
- `failed`;
- `cancelled`;
- `poll_timeout`;
- `backend_unavailable`;
- `operation_not_found`;
- `operation_unavailable`.

## 4. Behavior Rules

- Start route returns `operation_id`.
- Frontend stores `operation_id` in local UI/query state, not durable business data.
- Poll only the matching workspace/session operation status route.
- Stop polling on `completed`, `failed`, or `cancelled`.
- Cancel button appears only when cancel endpoint exists and operation is cancellable.
- Double cancel click must be idempotent at UI level.
- Workspace/session switch while polling must detach UI from the old operation unless explicitly shown as background state.

## 5. Acceptance

M2/M3 are not complete unless:

- workspace build uses shared polling hook;
- session build uses the same hook;
- failed/cancelled/completed states are visually distinct;
- backend unavailable and operation not found are non-crashing states.
