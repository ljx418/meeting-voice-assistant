# V3.5 SDKs

This directory contains V3.5 Application Adaptation Layer SDKs.

Current status:

- V3.5-D: Python SDK MVP is implemented for local/backend integration smoke.
- V3.5-E1: TypeScript SDK core client is implemented for dev/local protocol integration smoke.
- V3.5-E2: React hooks are implemented for dev/local UI integration smoke.

Boundaries:

- SDKs are thin protocol clients.
- SDKs do not import harnessOS server internals.
- SDKs do not expose Meeting, Knowledge, or business workflow wrappers in the default surface.
- TypeScript React hooks are exposed through `@harnessos/client/react`; importing the core TS SDK does not require React.
