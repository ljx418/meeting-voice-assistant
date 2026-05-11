# V3.5 Python SDK Contract

Status: V3.5-D implementation baseline.

The Python SDK is a thin protocol client for local/backend integration smoke.
It consumes the V3.5 JSON-RPC default method surface and does not import server
runtime internals.

## Runtime Boundary

- `harnessos_client` must not import `apps.*`, `core.*`, GatewayService, RuntimeAdapter, Core Store, or server `METHOD_SCHEMAS`.
- Runtime uses a local protocol snapshot.
- Tests compare the snapshot with server schema registry.
- SDK does not provide token issuance or signing.

## Public API

`__all__` is limited to:

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

Forbidden from default exports:

- MeetingClient / KnowledgeClient
- `generateMinutes`
- `ingestDocument`
- `runMeetingWorkflow`
- `generateVideo`
- `analyzePortfolio`
- `processRecording`
- `searchKnowledgeBase`

## Behavior

- SDK defaults to `/v1/rpc`.
- Every wrapper injects default scope unless a compatible per-call scope is supplied.
- Obvious app/project/workspace conflicts are rejected locally as `ScopeMismatchError`.
- Resource ownership mismatch remains a server-side `SCOPE_MISMATCH`.
- `client.rpc()` rejects unknown, forbidden, legacy, debug, admin, and business facade methods by default.
- `events_subscribe()` returns a descriptor only; it does not implement SSE reconnect or buffering.
- `repr(client)`, `repr(EventSubscription)`, and exception strings must not leak capability or subscription tokens.

## Exit Statement

V3.5-D complete means:

```text
Python SDK MVP usable for local/backend integration smoke
```

It does not mean SDK production-ready, external app ready, or V3.5-MVP complete.
