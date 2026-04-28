# OpenHarness + Codex-Style JSON-RPC Architecture Pack

This pack is designed to be consumed by Claude Code as a project architecture brief.

## Files

- `01_OVERALL_ARCHITECTURE.md`
  - Overall target architecture
  - System boundaries
  - Core modules
  - End-to-end request flow
- `02_PHASE1_DETAILED_ARCHITECTURE.md`
  - Phase 1 detailed architecture
  - JSON-RPC protocol layer and OpenHarness adapter
- `03_PHASE2_DETAILED_ARCHITECTURE.md`
  - Phase 2 detailed architecture
  - CLI-first delivery and local testing loop
- `04_PHASE3_DETAILED_ARCHITECTURE.md`
  - Phase 3 detailed architecture
  - Backend hardening, observability, approvals, artifact service

## Design Intent

Build a Codex-style app-server around OpenHarness so that:

1. CLI is the first-class client.
2. Backend behavior can be tested and iterated quickly without waiting for frontend work.
3. Web can be added later as another client over the same protocol.
4. Domain workflows for meeting assistant, interview assistant, and personal knowledge assistant can be plugged into one runtime.

## Design Basis

This design intentionally combines:

- Codex app-server ideas:
  - JSON-RPC style bidirectional protocol
  - `initialize -> thread/start -> turn/start -> notifications -> turn/completed`
  - Thread / Turn / Item primitives
- OpenHarness ideas:
  - `build_runtime()` -> `RuntimeBundle`
  - `QueryEngine`
  - `run_query()` tool-aware loop
  - hooks / permissions / commands / session snapshots

## Suggested Reading Order for Claude Code

1. Read `01_OVERALL_ARCHITECTURE.md`
2. Read `02_PHASE1_DETAILED_ARCHITECTURE.md`
3. Read `03_PHASE2_DETAILED_ARCHITECTURE.md`
4. Read `04_PHASE3_DETAILED_ARCHITECTURE.md`

## Implementation Note

The architecture intentionally does **not** expose OpenHarness internal message types directly to clients.
A project-owned protocol and project-owned schema layer sits in front of the OpenHarness runtime.
