# harnessOS TypeScript SDK

V3.5-E1 implements the TypeScript SDK core client for dev/local protocol integration smoke.
V3.5-E2 adds React hooks for dev/local UI integration smoke.

The SDK is a thin JSON-RPC client. It does not import harnessOS server internals and does not expose Meeting, Knowledge, or other business workflow wrappers.

## Commands

```bash
npm install
npm test
```

## Boundary

- Default transport: JSON-RPC `/v1/rpc`.
- Native EventSource mode uses the signed URL returned by `events.subscribe` and does not require an Authorization header.
- Fetch stream mode can use `Authorization: Bearer <capability-token>`.
- React hooks are exposed through `@harnessos/client/react`; importing the core client does not require React.
- Hooks do not auto-start sessions, turns, or event streams on mount.
