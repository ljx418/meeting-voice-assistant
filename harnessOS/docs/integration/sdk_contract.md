# V3.5 SDK Contract

Status: V3.5-D Python SDK MVP complete; V3.5-E1 TypeScript SDK Core Client complete; V3.5-E2 React Hooks ready for dev/local UI integration smoke.

The SDKs are thin protocol clients for the V3.5 Application Adaptation Layer.
They consume the V3.5 JSON-RPC default method surface and do not import server
runtime internals. React hooks wrap the TypeScript SDK public API into frontend
state helpers without redefining protocol behavior.

## Runtime Boundary

- `harnessos_client` must not import `apps.*`, `core.*`, GatewayService, RuntimeAdapter, Core Store, or server `METHOD_SCHEMAS`.
- `sdk/typescript/src` must not import `apps/*`, `core/*`, GatewayService, RuntimeAdapter, or server `METHOD_SCHEMAS`.
- `sdk/typescript/src/react` must only depend on the E1 TypeScript SDK public API and React.
- Importing the TypeScript core client must not require React.
- Runtime uses a local protocol snapshot.
- Tests compare the snapshot with server schema registry.
- SDKs do not provide token issuance or signing.

## Public API

Python `__all__` is limited to the following platform client objects and typed errors.

Python:

- `HarnessOSClient`
- `HarnessOSAsyncClient`
- `Scope`
- `CapabilityToken`
- `EventSubscription`
- `HarnessOSError`
- `RpcError`
- `ProtocolError`
- `TransportError`
- typed protocol errors

TypeScript core exports:

- `HarnessOSClient`
- `Scope`
- `CapabilityToken`
- `EventSubscription`
- `JsonRpcTransport`
- `RpcError` / typed protocol errors
- `nativeEventSourceUrl`
- `fetchStreamRequest`

TypeScript React exports:

- `useHarnessSession`
- `useTurn`
- `useEvents`
- `useArtifacts`
- `useJobs`
- `useApprovals`

Forbidden from default exports:

- MeetingClient / KnowledgeClient
- `generateMinutes`
- `ingestDocument`
- `runMeetingWorkflow`
- `generateVideo`
- `analyzePortfolio`
- `processRecording`
- `searchKnowledgeBase`
- business hooks such as `useMeetingMinutes` or `useKnowledgeSearch`

## Behavior

- SDK defaults to `/v1/rpc`.
- Every wrapper injects default scope unless a compatible per-call scope is supplied.
- Obvious app/project/workspace conflicts are rejected locally as `ScopeMismatchError`.
- Resource ownership mismatch remains a server-side `SCOPE_MISMATCH`.
- `client.rpc()` rejects unknown, forbidden, legacy, debug, admin, and business facade methods by default.
- Python `events_subscribe()` returns a descriptor only; it does not implement SSE reconnect or buffering.
- TypeScript `eventsSubscribe()` returns an `EventSubscription` descriptor and EventSource/fetch stream helpers.
- Native EventSource mode uses the signed URL returned by `events.subscribe` and does not set an Authorization header.
- Fetch stream mode may use `Authorization: Bearer <capability-token>` only when explicitly requested.
- `repr(client)`, `repr(EventSubscription)`, and exception strings must not leak capability or subscription tokens.
- React hooks do not auto-start sessions, turns, or event streams on mount.
- `useEvents` connects only when `enabled=true` or `connect()` is called, supports basic reconnect, cursor, dedupe, and close on unmount.
- `useApprovals` only calls `approval.respond`.
- `useArtifacts` does not default to inline `artifact.read`.
- `useJobs` does not default to polling.

## Exit Statement

V3.5-D complete means:

```text
Python SDK MVP usable for local/backend integration smoke
```

V3.5-E1 complete means:

```text
TypeScript SDK core client ready for dev/local protocol integration smoke
```

V3.5-E2 complete means:

```text
React hooks ready for dev/local UI integration smoke
```

These do not mean SDK production-ready, external app ready, production-ready browser integration, or V3.5 complete.
