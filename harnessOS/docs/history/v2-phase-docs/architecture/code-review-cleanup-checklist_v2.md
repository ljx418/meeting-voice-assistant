# harnessOS V2 Code Review Cleanup Checklist

## 1. Maintenance Rule

This checklist is an active architecture document. It must be updated after every major development phase, before the next phase is accepted.

Required update points:

- After cleanup implementation.
- After the second review gate.
- After phase acceptance tests.
- After each future major phase, before marking that phase complete.

Status values:

- `open`: issue confirmed and not fixed.
- `in_progress`: cleanup is being implemented.
- `fixed_pending_review`: implementation completed, waiting for second review.
- `verified`: second review and acceptance tests passed.
- `deferred`: explicitly accepted residual risk with a target phase.

## 2. P0 Security Closure

| ID | Issue | Plane | Main Files | Cleanup Target | Acceptance |
|----|-------|-------|------------|----------------|------------|
| CR-P0-01 | Tool approval can be bypassed by caller-controlled `approved=True` | Connector / Tool / Store, Harness Core | `tools/policy_guard.py`, `core/engine/query.py` | Remove external approval flag trust; only service-verified approval ids can unblock risky tools | Risky tool remains blocked unless approval checker validates the approval id |
| CR-P0-02 | Approval id is not bound to the approved tool action/input | Harness Core, Store | `apps/gateway/runtime.py`, `tools/policy_guard.py` | Bind approvals to tool name, action, session, turn, and normalized input hash | A valid approval id cannot unblock a different tool/input |
| CR-P0-03 | OpenHarness runtime path can bypass tool policy guard | Runtime Adapter, Harness Core | `openharness/engine/query.py`, `core/runtime_adapter/adapters.py` | Inject and enforce policy metadata in OpenHarness tool execution | OpenHarness and Simple runtime paths block the same risky tool calls |
| CR-P0-04 | Artifact RPC can register/read arbitrary local files | Connector / Tool / Store, Gateway | `apps/gateway/artifacts.py`, `apps/gateway/service.py` | Restrict artifact paths to managed/allowed roots and enforce ownership checks | Path traversal and out-of-root artifact reads are rejected |
| CR-P0-05 | Session/artifact/approval/retry/trace lack tenant or owner boundary | Protocol App Server, Store | `apps/gateway/service.py`, `core/services/app_service.py` | Add at least session/owner-scoped validation for public resource reads and updates | Cross-session resource access is rejected or filtered |
| CR-P0-06 | Raw session id is used as a filesystem path segment | Store | `apps/gateway/storage.py` | Validate or encode session ids before path construction | Traversal-style session ids cannot escape storage root |
| CR-P0-07 | Core SQLite can persist unmasked event content | Store, Harness Core | `core/services/app_service.py`, `core/stores/sqlite.py` | Mask event payloads before Core persistence | Secret strings are absent from Core SQLite payloads |

## 3. P1 Architecture Boundary

| ID | Issue | Plane | Main Files | Cleanup Target | Acceptance |
|----|-------|-------|------------|----------------|------------|
| CR-P1-01 | Meeting business RPC bypasses Pack workflow governance | Domain Pack, Gateway | `apps/gateway/service.py`, `packs/meeting/workflow.py` | Keep compatibility methods but route governed work through Meeting Pack/Core path | Meeting RPC and `turn.start(domain=meeting)` produce consistent job/artifact/trace records |
| CR-P1-02 | Domain workflows call tools/connectors/files directly | Domain Pack, Tool | `packs/*/workflow.py` | Provide a governed workflow execution context for external actions | Pack workflows carry policy, trace, job, and artifact metadata |
| CR-P1-03 | GatewayRuntimePool owns too much Core orchestration | Gateway, Harness Core | `apps/gateway/runtime.py` | Stop adding Core policy/job/workflow responsibilities to runtime pool | New cleanup code moves reusable logic toward Core services |
| CR-P1-04 | Pack assembly is still factory-driven instead of manifest/DSL-driven | Domain Pack | `apps/gateway/workflows.py`, `core/packs/registry.py` | Prepare Phase 5-A by exposing blocked reasons and manifest-driven assembly fields | `pack.get` can explain missing connector/policy/skill dependencies |
| CR-P1-05 | Pack code depends upward on Gateway modules | Domain Pack, Gateway | `packs/*/workflow.py`, `apps/gateway/workflows.py` | Move shared protocols to Core or inject dependencies | Pack modules do not import Gateway implementation-only services for new code |

## 4. P2 Functional Consistency

| ID | Issue | Cleanup Target | Acceptance |
|----|-------|----------------|------------|
| CR-P2-01 | Missing resource errors are mapped inconsistently | Use stable resource-specific errors | Missing artifact/pack/connector/job/approval tests assert stable errors |
| CR-P2-02 | Default tools can block without creating an approval request | Ensure guarded default tool path has requester metadata | Risky default tool returns approval id and retry context |
| CR-P2-03 | Retry may replay masked input instead of original executable input | Separate executable retry payload from public masked view | Approved retry executes exactly the originally approved action |
| CR-P2-04 | Real-audio acceptance depends on local absolute paths | Fixture or environment-gated acceptance path | Default tests are portable; local audio is only validation evidence |
| CR-P2-05 | Stub pack explicit domains may fall through to generic chat | Explicit unavailable domains fail clearly | `domain=interview/investment` returns explainable blocked status |

## 5. P3 Maintainability

| ID | Issue | Cleanup Target | Acceptance |
|----|-------|----------------|------------|
| CR-P3-01 | GatewayService remains large | Continue router/handler extraction | New methods register through `RpcRouter` or focused handlers |
| CR-P3-02 | Tests rely on repeated sys.path mutation and ad hoc async execution | Move toward pytest fixtures | New tests avoid new sys.path mutation |
| CR-P3-03 | Duplicate OpenHarness tool package is invalid | Remove or quarantine duplicate path in a later compatibility cleanup | Canonical tool source is documented |

## 6. Second Review Gate

Before running acceptance tests after cleanup, a second review must confirm:

- No new P0 or P1 issue was introduced.
- All changed code has direct or indirect test coverage.
- OpenHarness and Simple runtime governance behavior remains consistent.
- Meeting lineage, approval/retry, artifact read, and pack assembly behavior did not regress.

If a new P0 or P1 issue is found, testing stops and implementation returns to cleanup.

## 7. 2026-04-30 Cleanup Execution Result

Current cleanup status:

| ID | Status | Result |
|----|--------|--------|
| CR-P0-01 | verified | Caller-provided `approved=True` is ignored. Risky tools require a service-verified approval id. |
| CR-P0-02 | verified | Approval ids are bound to session, source turn, tool name, action, and normalized input hash. Mismatched reuse is rejected. |
| CR-P0-03 | verified | Simple and OpenHarness tool paths both call the policy guard before executing risky tools. |
| CR-P0-04 | verified | Artifact register/read now rejects paths outside managed or explicitly allowed roots. |
| CR-P0-05 | deferred | Session id traversal and approval cross-session reuse are closed. Full user/tenant ownership is deferred to Phase 6 governance because the current local-first protocol has no authenticated principal model. |
| CR-P0-06 | verified | Session ids are validated before filesystem path construction. Traversal-style ids are rejected. |
| CR-P0-07 | verified | Gateway/Core event payloads and session snapshots are masked before persistence. |
| CR-P1-01 | deferred | Meeting compatibility RPC remains, but current default workflow execution uses the pack path. Full compatibility-route convergence is Phase 5-A cleanup. |
| CR-P1-02 | deferred | Pack workflow governed execution context is a Phase 5-A/5-C target. Current cleanup prevents new P0 bypasses but does not complete the abstraction. |
| CR-P1-03 | deferred | GatewayRuntimePool remains broad. New fixes avoided adding business workflow responsibility; further extraction belongs to Phase 5. |
| CR-P1-04 | deferred | Manifest-driven assembly exists at MVP scope. DSL/skill/policy bundle assembly remains Phase 5-A. |
| CR-P1-05 | deferred | Existing compatibility imports remain. New pack boundary cleanup is assigned to Phase 5-A. |

Second review result:

- Security review: no remaining P0/P1 found in the modified code.
- Test coverage review: no remaining P0/P1 test gap found for retry reservation, snapshot masking, OpenHarness approval propagation, source-turn retry binding, or cross-session approval rejection.

Acceptance evidence:

- Compile check passed with `PYTHONPYCACHEPREFIX=/tmp/harnessos-pycache python3 -m compileall tools/policy_guard.py apps/gateway/runtime.py apps/gateway/artifacts.py apps/gateway/storage.py core/services/app_service.py core/runtime_adapter/adapters.py core/engine/query.py openharness/engine/query.py`.
- Draw.io XML check passed with `xmllint --noout docs/architecture/current-vs-target-gap_v2.drawio docs/architecture/code-review-cleanup-checklist_v2.drawio`.
- Focused post-fix regression passed: 6 tests.
- Control plane regression passed: 32 tests.
- Meeting/artifact/workflow regression passed: 25 tests.
- Governance regression passed: 33 tests.
- Core/runtime/pack regression passed: 22 tests.
- HarnessOS `tests/` suite passed: 113 passed, 1 skipped.
- Meeting real-audio lineage acceptance passed with `ASR_FUNASR_ENDPOINT=http://127.0.0.1:8001 scripts/e2e_meeting_validation.sh`.
- Meeting acceptance evidence: `session_id=sess_0297614b55d7`, `turn_id=turn_38600f25256d`, `job_id=job_e4aa869ec7e1`, artifacts `transcript=art_7047472d8050`, `analysis=art_797dc6b7f92e`, `result=art_e0e8cc73a25a`, `minutes=art_552939a8fc5f`.

Blocked or environment-gated evidence:

- Full repository `python3 -m pytest` is not a valid HarnessOS acceptance line in the current workspace because it collects `examples/` external framework tests that require a different dependency/runtime setup.
- The default `fixtures/audio_samples/sample_ted_talk.mp3` fixture is not present in this workspace, so the user-state Meeting acceptance used the configured local audio directory.
