# Test & Acceptance Plan - harnessOS

## Overview

This document defines the acceptance criteria for each development phase. Each phase must satisfy **Functionality**, **Stability**, **Observability**, and **Documentation** requirements.

---

## Phase 0: Foundation & Skeleton

**Goal**: Build a runnable empty shell

### Acceptance Criteria

| Category | Criteria | Verification |
|----------|----------|--------------|
| **Repository** | Single or clear multi-repo structure; `apps/core/agents/tools/skills/execution/devplane` directories in place | Directory check |
| **Run Chain** | `POST /v1/runs` completes one minimal闭环 from user input to streaming response | E2E smoke test |
| **File Chain** | `POST /v1/uploads` uploads a file, then `GET /v1/artifacts/{id}` retrieves it | Upload → retrieve test |
| **Agent Kernel** | `lead_orchestrator` can call 1 dummy tool and output structured result | Unit test |
| **State Management** | `session_id`, `run_id`, `artifact_id`, `tool_call_id` all linked | Integration test |
| **Observability** | Each run has `trace_id`, logs, error codes | Log review |
| **CI** | lint, unit test, smoke test all green | CI pipeline |
| **Documentation** | README + local startup guide + .env.example complete | Doc review |

### Exit Condition
- [ ] Repository structure verified
- [ ] `/v1/runs` → streaming response E2E passes
- [ ] File upload → artifact retrieval passes
- [ ] Lead orchestrator calls dummy tool with structured output
- [ ] All IDs (`session_id`/`run_id`/`artifact_id`/`tool_call_id`) traceable
- [ ] Trace ID present in every run
- [ ] CI: lint + unit + smoke test green
- [ ] README + startup guide + .env.example exist

---

## Phase 1: Meeting MCP MVP

**Goal**: Meeting scenario works through Headless/RPC and ordinary `turn.start` chat by calling the external Meeting MCP server.

### Acceptance Criteria

| Category | Criteria | Verification |
|----------|----------|--------------|
| **Meeting MCP Discovery** | harnessOS can start Meeting MCP, read `meeting://agent-guide`, and list meeting tools | RPC test |
| **Meeting Text Analysis** | `meeting.analyze_text` returns structured analysis and minutes path | Unit/integration test |
| **Real Audio Chain** | `/Users/Zhuanz/Desktop/workspace/音频资料` real audio → transcript, segments, analysis, minutes | Default acceptance test |
| **Chat Auto Orchestration** | `turn.start(domain=meeting)` and natural-language audio path prompts enter Meeting workflow | Gateway workflow test + CLI manual test |
| **Artifact Chain** | `transcript.json`, `analysis.json`, `result.json`, `minutes.md` exist after processing | Filesystem assertion |
| **No Interview Scope** | Phase1 does not call interview tools or score candidates | Test/doc review |
| **Documentation** | Current/target architecture and manual acceptance docs updated | Doc review |

### Exit Condition
- [x] `meeting.capabilities` returns meeting tools and agent guide.
- [x] `meeting.analyze_text` supports text-only analysis path.
- [x] `meeting.process_recording` processes a real file from `/Users/Zhuanz/Desktop/workspace/音频资料`.
- [x] Real audio acceptance produced `session_id=meeting_895b5d29`.
- [x] Real audio acceptance produced `minutes.md`.
- [x] `turn.start(domain=meeting)` and ordinary meeting audio prompts route to Meeting workflow.
- [x] Chat/headless acceptance produced `session_id=meeting_8e8d3499`.
- [x] Unit/regression tests pass.
- [x] Interview workflow remains out of scope.
- [x] Artifact registration is available in Gateway RPC for meeting outputs.

---

## Phase 1-C: Artifact Store for Meeting Outputs

**Goal**: Register Meeting MCP transcript, analysis, result, and minutes outputs as harnessOS first-class artifacts while preserving existing path-based compatibility.

### Acceptance Criteria

| Category | Criteria | Verification |
|----------|----------|--------------|
| **Artifact Model** | Each artifact has `artifact_id`, `session_id`, `turn_id`, `domain`, `kind`, `path`, `mime`, `created_at`, and metadata | Unit test |
| **Artifact Registry** | External files can be registered without moving them | Unit/integration test |
| **Gateway RPC** | `artifact.register`, `artifact.list`, `artifact.get`, and `artifact.read` are available through `/v1/rpc` and stdio JSONL | Gateway protocol test |
| **Meeting Integration** | Meeting workflow registers `transcript`, `analysis`, `result`, and `minutes` after real audio processing | Real audio acceptance |
| **Compatibility** | Existing `minutes_path` and artifacts path outputs remain present | Regression test |
| **Documentation** | Current/target gap, drawio, automated cases, and manual cases updated after implementation | Doc review |

### Exit Condition

- [x] `artifact.list(session_id)` lists artifacts from a completed meeting run.
- [x] `artifact.read(minutes_artifact_id)` returns non-empty markdown text.
- [x] `artifact.read(analysis_artifact_id)` returns valid JSON.
- [x] `turn.completed.data.meeting.artifacts` includes both source paths and artifact ids.
- [x] Real audio acceptance continues to use `/Users/Zhuanz/Desktop/workspace/音频资料`.
- [x] Existing Phase1 meeting tests remain green.
- [x] Interview workflow remains out of scope.

Acceptance evidence:

- Real audio: `/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_How to tune your inner voice  Rhonda Ross Daniel A.mp3`
- Gateway session: `sess_a08b1f628ce2`
- Meeting session: `meeting_c4dc4073`
- Registered artifacts: `analysis=art_9c1eb1071d60`, `minutes=art_c27fa88d8d93`, `result=art_abd235cc9239`, `transcript=art_69cdc30584b0`

---

## Phase 1-D: Lead Orchestrator and Domain Workflow Registry

**Goal**: Move meeting routing from a `GatewayRuntimePool` special case into a reusable orchestration layer, then add the first knowledge workflow path.

### Acceptance Criteria

| Category | Criteria | Verification |
|----------|----------|--------------|
| **DomainWorkflow Interface** | Workflows implement consistent `should_handle` and `run` contract | Unit test |
| **Workflow Registry** | Meeting and knowledge workflows can be registered and selected | Routing test |
| **Lead Orchestrator** | `turn.start` routes by explicit domain, keyword, path, and context | Integration test |
| **Meeting Regression** | Real audio meeting flow still returns transcript, minutes, and artifact ids | Real audio acceptance |
| **Knowledge MVP** | Knowledge request can ingest/search/synthesize with source references | Integration test |
| **No Interview Scope** | Interview terms do not trigger meeting workflow | Regression test |

### Exit Condition

- [x] Meeting real-audio acceptance remains green.
- [x] `turn.start(domain=meeting)` and natural meeting audio prompts route through the orchestrator.
- [x] Generic “你好” goes to normal chat.
- [x] Knowledge requests route to knowledge workflow MVP.
- [x] Existing artifact ids remain available in meeting outputs.

Acceptance evidence:

- Real audio: `/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_How to tune your inner voice  Rhonda Ross Daniel A.mp3`
- Gateway session: `sess_2858157d522e`
- Meeting session: `meeting_882541b5`
- Minutes artifact: `art_3b24d8ee4fe2`
- Registered workflows: `meeting.workflow`, `knowledge.workflow`

---

## Phase 2: Production & Governance

**Goal**: From "usable" to "controllable"

Phase 2 is split into five implementation gates. The order is intentional:
build trace/audit first, then approval, then policy enforcement, then retry,
then secret hygiene hardening.

### Phase 2 Development Plan

| Gate | Scope | Deliverables | Exit Gate |
|------|-------|--------------|-----------|
| 2-A Trace/Audit MVP | session/turn/workflow/artifact trace chain | Done: trace store, `trace.list/get`, trace ids in turn data | chat, meeting, artifact read all queryable by trace |
| 2-B Approval Coordinator | approval request and decision lifecycle | Done: `approval.request/list/get/approve/reject` | approval lifecycle is persisted and trace-linked |
| 2-C Policy Rules | risk based turn/tool gating | Done: policy evaluator, `policy.evaluate`, write/send/publish preflight approval defaults | write requires approval, read does not |
| 2-D Retry/Resume | recover policy-blocked turn/workflow | Done: `turn.retry`, saved retry context, approved-action continuation, duplicate retry prevention | approved retry succeeds; pending retry is blocked |
| 2-E Secret Hygiene | mask sensitive strings before persistence | Done: secret masker, persistence-boundary scan tests | `sk-*`, token, Authorization not persisted in plaintext |
| 2-F Architecture Hardening | reduce local persistence race risk | Done: file locks, atomic writes, concurrent persistence tests | concurrent local writes do not lose records |
| 3-A App Lifecycle | remove API route module singleton | Done: app-scoped GatewayService, FastAPI dependency injection, injectable `create_app` | injected service is shared by `/v1/runs` and `/v1/rpc` |
| Core v1.5 Docs | redefine next architecture as local-first Agent OS Core | Done: Core/Store/Pack/Job/Policy plan and diagrams | docs are internally consistent and updated with each migration step |
| Core v1.5-A Protocol + Store | introduce Core objects and SQLite foundation | Done: protocol models, CoreAppService, SQLite CRUD/filtering, legacy session import, native session/turn/item/artifact/trace/approval/retry mutation/conversion, no Gateway runtime recorder dependency | Core Store foundation works; Gateway execution and governance/artifact records enter Core through CoreAppService |
| Core v1.5-E Runtime Adapter | converge Simple/OpenHarness runtime boundary | Done: RuntimeHandle/RuntimeAdapter, SimpleRuntimeAdapter, OpenHarnessRuntimeAdapter, Gateway adapter start/invoke/stream/continue/close | Gateway no longer directly creates runtime internals; Simple and OpenHarness paths remain compatible |
| V2.0 Target Architecture | adopt Protocol-first Harness Core + OS-like App Server + Domain Pack Platform as the formal target | Done: V2 target doc, status, gap, drawio, and acceptance docs updated | Core v1.5-E remains current baseline; V2.0 is the target architecture |
| Phase 3-B Core-native Session/Event Store | make Core Store the primary session/event source | Planned | Core records can rebuild session events/transcript; legacy JSON remains compatible |
| Phase 3-C Background Job Worker | turn synchronous Job MVP into long-running job service | Planned | queued/running/completed/failed/cancelled states and job events are queryable |
| Phase 3-D Adapter-level Governance Injection | inject policy/approval/trace/tool metadata through Runtime Adapter defaults | Planned | risky tools are blocked in default Simple/OpenHarness paths until approved |
| Phase 3-E Pack Assembly MVP | let pack manifest drive workflow/connector/skill/policy registration | Planned | meeting/knowledge are assembled from packs and still pass real-audio acceptance |
| Phase 3-F Connector Registry MVP | manage Meeting MCP as a connector record with health/capabilities | Planned | connector list/get/health can discover and validate Meeting MCP |

### Acceptance Criteria

| Category | Criteria | Verification |
|----------|----------|--------------|
| **Permissions** | All write/send/publish tools require approval by default | Policy test |
| **Audit** | Every tool_call has input summary, caller, timestamp, status, artifact reference | Audit log review |
| **Isolation** | Different users/sessions have non-crossing data and artifacts | Multi-tenant test |
| **Recovery** | Session resume, run retry, run cancel all functional | Integration test |
| **Security** | Secrets don't enter prompt, logs, or artifact plaintext | Security scan |
| **Observability** | Trace, metrics, error dashboard available | Dashboard check |
| **Testing** | 30+ E2E regression scenarios passing | Test suite |
| **Documentation** | Ops manual, permission policy docs, audit field specs complete | Doc review |

### Exit Condition
- [x] `trace.list/get` available through Gateway service and stdio JSONL
- [x] Chat, meeting workflow, knowledge workflow, and artifact reads produce trace records
- [x] `approval.request/list/get/approve/reject` available through Gateway service and stdio JSONL
- [x] Write/send/publish turns default to approval through Gateway preflight
- [x] Rejected/pending approval blocks execution; approved approval can continue via `turn.retry`
- [ ] Audit log includes input summary, caller/session, timestamp, status, workflow id, artifact ref, and approval ref
- [x] Policy-blocked turn retry works for approved approvals
- [ ] Generic failed workflow retry works for simulated failures
- [x] No common secrets in persisted event/log/trace/approval/retry/artifact read plaintext
- [x] API routes use app-scoped GatewayService instead of a module-level `_gateway`
- [x] Core v1.5 direction documented before implementation
- [x] V2.0 target architecture adopted after Core v1.5-E
- [x] Core protocol models and SQLite Store foundation exist
- [x] CoreAppService exists as the service facade over Core Store and Gateway-to-Core writes
- [x] RuntimeHandle/RuntimeAdapter exist as the Core runtime boundary
- [x] Gateway session start/turn/continue/close use RuntimeAdapter for Simple/OpenHarness paths
- [x] Gateway session start/close writes through Core-native session mutation
- [x] Gateway turn/item events write through Core-native thread/turn/item mutation
- [x] Gateway turn events write Core session/thread/turn/items and trace records through CoreAppService
- [x] Meeting workflow artifacts write through Core-native artifact conversion
- [x] Policy approval/retry records write through Core-native approval/retry/trace conversion
- [x] Phase 1 meeting real-audio acceptance still passes with `/Users/Zhuanz/Desktop/workspace/音频资料`
- [x] Phase 1 MVP complete
- [x] Phase 2 MVP complete
- [x] Phase 3-A complete
- [ ] Phase 3-B Core-native session/event store complete
- [ ] Phase 3-C background job worker complete
- [ ] Phase 3-D adapter-level governance injection complete
- [ ] Phase 3-E pack assembly complete
- [ ] Phase 3-F connector registry complete
- [ ] Ops + permission + audit docs complete

### Phase 2 Test Plan

| Test ID | Test | Command / Entry | Expected Result |
|---------|------|-----------------|-----------------|
| P2-A01 | Trace store unit test | `pytest tests/test_trace_gateway.py` | Trace records are persisted and queryable |
| P2-A02 | Trace from chat turn | `pytest tests/test_gateway_protocol.py::test_turn_start_records_trace` | `turn.completed` links to trace_id |
| P2-A03 | Trace from meeting workflow | `pytest tests/test_meeting_turn_workflow.py tests/test_meeting_audio_acceptance.py` | Meeting artifacts and `meeting.workflow` are trace-linked |
| P2-B01 | Approval state machine | `pytest tests/test_approval_gateway.py` | pending/approved/rejected states are valid and persisted |
| P2-B02 | Approval protocol parity | `pytest tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py` | service and stdio responses match |
| P2-C01 | Policy write gating | `pytest tests/test_policy_approval.py` | write operation creates pending approval |
| P2-C02 | Read-only policy bypass | `pytest tests/test_policy_approval.py` | read/list/search do not create approvals |
| P2-C03 | Meeting policy bypass | `pytest tests/test_policy_approval.py` | meeting minutes requests do not trigger write approval |
| P2-C04 | Policy evaluate RPC | `pytest tests/test_policy_approval.py` | write tool requires approval and read tool does not |
| P2-D01 | Retry failed turn | `pytest tests/test_retry_resume.py` | retry succeeds and events remain linked |
| P2-D02 | Meeting regression after retry changes | `pytest tests/test_meeting_gateway.py tests/test_meeting_turn_workflow.py` | Meeting workflow and artifact ids do not regress |
| P2-E01 | Secret masking | `pytest tests/test_secret_hygiene.py` | API keys/tokens are masked before persistence |
| P3-A01 | API app lifecycle injection | `pytest tests/test_api_runs.py::test_create_app_accepts_injected_gateway_service` | Injected GatewayService is used by `/v1/runs` and visible through `/v1/rpc` |
| C15-D01 | Core v1.5 documentation consistency | Manual doc review | status, gap, design, acceptance, test plan, and drawio agree on the same next architecture |
| C15-D02 | Core v1.5 drawio validity | `xmllint --noout docs/architecture/current-vs-target-gap.drawio` | drawio remains valid XML |
| C15-A01 | Core protocol model round trip | `pytest tests/test_core_v15_protocol_store.py::test_core_protocol_objects_round_trip` | Session/Thread/Turn/Item records have stable ids and content |
| C15-A01b | Core app service facade | `pytest tests/test_core_v15_protocol_store.py::test_core_app_service_records_runtime_session_via_native_mutation` | CoreAppService records and updates Gateway runtime sessions through native mutation |
| C15-A01c | Core turn/item native mutation | `pytest tests/test_core_v15_protocol_store.py::test_core_app_service_records_gateway_events_via_native_mutation` | CoreAppService records Gateway events as native thread/turn/item mutations |
| C15-A01d | Core governance/artifact native mutation | `pytest tests/test_core_v15_protocol_store.py::test_core_app_service_records_governance_and_artifacts_via_native_mutation` | CoreAppService records artifact/trace/approval/retry through native conversion paths |
| C15-A02 | Core SQLite CRUD and filters | `pytest tests/test_core_v15_protocol_store.py::test_core_sqlite_store_crud_and_filters` | Core records can be saved, read, and filtered |
| C15-A03 | Legacy session import | `pytest tests/test_core_v15_protocol_store.py::test_core_sqlite_store_imports_legacy_gateway_sessions` | Legacy Gateway snapshot/events import into Core records |
| C15-A04 | Gateway turn Core write | `pytest tests/test_gateway_protocol.py::test_turn_start_mirrors_core_records` | Existing `turn.start` creates Core session/thread/turn/items and query RPC can read them |
| C15-A05 | Gateway governance Core write | `pytest tests/test_gateway_protocol.py::test_policy_approval_and_retry_mirror_core_governance_records` | Policy-blocked turns create Core approval/retry/trace records and query RPC can read them |
| C15-A06 | Gateway artifact Core write | `pytest tests/test_gateway_protocol.py::test_turn_completed_artifacts_mirror_core_records` | Workflow artifact records create Core artifacts and query RPC can read them |
| C15-E01 | Runtime adapter boundary | `pytest tests/test_runtime_adapter.py` | Simple/OpenHarness adapters start handles, invoke/stream/continue, and Gateway sessions keep adapter handles |
| V20-D01 | V2.0 target architecture consistency | Manual doc review + `xmllint --noout docs/architecture/current-vs-target-gap.drawio` | CURRENT-STATUS, target architecture, gap, drawio, and acceptance docs agree that V2.0 is the target and Core v1.5-E is current |
| P3-B01 | Core session/event source | TBD after implementation | New chat and meeting turns write session/thread/turn/items and can rebuild events/transcript from Core records |
| P3-C01 | Background job lifecycle | TBD after implementation | Meeting audio job moves through queued/running/completed or failed/cancelled states and exposes job events |
| P3-D01 | Adapter governance injection | TBD after implementation | Default runtime adapter paths carry policy/approval/trace metadata and block risky tools before execution |
| P3-E01 | Pack assembly | TBD after implementation | meeting/knowledge workflows are registered from pack assembly and real-audio acceptance passes |
| P3-F01 | Connector registry | TBD after implementation | Meeting MCP appears in connector list/get/health and drives meeting workflow |

Phase 2-A evidence:

- `pytest tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_artifact_gateway.py`: 13 passed.
- `pytest tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py`: 38 passed.
- Manual smoke: `python3 -m cli.main run --json '你好'` returned top-level `trace_id=trace_f124c372d3f3`.
- Manual stdio query: `trace.get(trace_id=trace_f124c372d3f3)` returned persisted trace records.

Residual risk: trace metadata currently stores event details and tool outputs. Secret masking is not complete until Phase 2-E.

Phase 2-B evidence:

- `pytest tests/test_approval_gateway.py tests/test_gateway_stdio.py tests/test_trace_gateway.py`: 11 passed.
- `pytest tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py`: 42 passed.
- Manual stdio request created `approval_id=appr_df10a7c3946c` with `trace_id=trace_manual_phase2b`.
- Manual stdio approve updated the approval to `approved`; `trace.get(trace_manual_phase2b)` returned both `approval.request` and `approval.approve`.

Residual risk closed by Phase 2-C for Gateway preflight. ToolRegistry-level defense in depth remains future work.

Phase 2-C evidence:

- `pytest tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py`: 10 passed.
- Full related regression passed: `tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py`: 45 passed.
- Write-like `turn.start` creates pending approval and does not invoke the agent.
- Manual write-like CLI smoke returned `approval_id=appr_1532cf6d65fc`, `trace_id=trace_030c83793b25`, and did not create `phase2c_policy_manual.txt`.
- Read-only `turn.start` continues normally and creates no approval.
- `policy.evaluate` classifies `workspace_write_file` as approval-required and `workspace_read_file` as read-only.
- Meeting request text containing `生成会议纪要` does not trigger write approval.

Residual risk closed by Phase 2-D for policy-blocked turns. Generic workflow failure retry remains future hardening.

Phase 2-D evidence:

- `pytest tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py`: 12 passed.
- Full related regression passed: `tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py`: 47 passed.
- Pending approval retry is rejected.
- Approved approval retry executes the saved original input and marks retry context as `retried`.
- Retry events include `retry_of_turn_id` and `approval_id`.
- Duplicate retry is rejected before re-executing the action.

Residual risk: Phase 2-D covers policy-blocked turns. Generic workflow failure retry remains a later hardening item.

Phase 2-E evidence:

- `pytest tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py`: 15 passed.
- Full related regression passed: `tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py`: 50 passed.
- Session `events.jsonl`, TraceStore, ApprovalStore, RetryStore, artifact metadata, and `artifact.read` results mask `sk-*`, `Authorization: Bearer ...`, and common token fields.

Residual risk: Phase 2-E is regex-based and does not rewrite external source artifact files. Full DLP remains future hardening.

Phase 2-F evidence:

- `pytest tests/test_gateway_persistence.py tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py`: 19 passed.
- Full related regression passed: `tests/test_gateway_persistence.py tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py`: 54 passed.
- ApprovalStore, RetryStore, and ArtifactRegistry concurrent writes do not lose records in the local-file backend.
- Session snapshots use atomic replacement and event logs use locked append.

Residual risk: local file locks are single-machine hardening, not a multi-worker or distributed persistence strategy.

Phase 3-A evidence:

- `pytest tests/test_api_runs.py tests/test_gateway_persistence.py tests/test_gateway_protocol.py`: 15 passed.
- Full related regression passed: `tests/test_api_runs.py tests/test_gateway_persistence.py tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py`: 57 passed.
- `create_app(gateway_service=...)` can inject a GatewayService and both `/v1/runs` and `/v1/rpc` observe the same service state.
- API routes no longer create or hold a module-level `_gateway`.

Residual risk: app-scoped service state is still process-local. Multi-worker production requires external session/runtime storage or a single-worker deployment policy.

Core v1.5 documentation-first evidence:

- `CURRENT-STATUS.md` identifies Core v1.5 as the next architecture direction.
- `current-vs-target-gap.md` describes the delta from current Gateway/Workflow primitives to Core/SQLite/Pack/Job/Tool Policy.
- `04_PHASE3_DETAILED_ARCHITECTURE.md` defines Core objects and implementation order.
- `acceptance-test-cases.md` and this test plan distinguish document approval from later code implementation.
- No Python code is changed in the documentation-first stage.

Core v1.5 future code acceptance:

- Normal chat creates queryable `session/thread/turn/items`.
- SQLite writes to `.harnessos/core.sqlite3` and legacy JSON/JSONL can be imported or read.
- `pack.list` exposes meeting, knowledge, investment, interview, and video_studio. Completed in Core v1.5-B MVP.
- Meeting real audio creates a job and produces transcript/minutes/analysis/result artifacts.
- Tool Policy Middleware blocks risky tool execution until approval.

Core v1.5-A evidence:

- `pytest tests/test_core_v15_protocol_store.py tests/test_gateway_protocol.py`: 17 passed.
- Governance regression passed: `tests/test_approval_gateway.py tests/test_policy_approval.py tests/test_retry_resume.py tests/test_secret_hygiene.py tests/test_gateway_stdio.py`: 15 passed.
- `PYTHONPYCACHEPREFIX=/tmp/harnessos-pycache python3 -m compileall core/protocol core/stores apps/gateway tests/test_core_v15_protocol_store.py tests/test_gateway_protocol.py`: passed.
- `CoreSQLiteStore` currently covers session/thread/turn/item/job/artifact/trace/approval/retry and legacy session import.
- `CoreAppService` is now the facade used by Gateway runtime/service for Core queries and native session/turn/item/artifact/trace/approval/retry mutation/conversion.
- `GatewayRuntimePool` and `GatewayService` no longer expose `CoreRuntimeRecorder`; the recorder remains only as legacy compatibility code.
- Gateway Core write path is active: `turn.start` records Core session/thread/turn/items/trace.
- Artifact Core write path is active: meeting/workflow artifact records become Core artifacts through CoreAppService.
- Governance Core write path is active: policy-blocked turns record Core approval/retry/trace through CoreAppService.
- Query RPC is active: `session.get`, `thread.list`, `turn.get`, `turn.items`, `core.artifact.list`, `core.trace.list`, `core.approval.list`, `core.retry.list`.
- Core v1.5-A status: complete. Remaining platform work moves to Pack System, Job Service, Tool Policy Middleware, and Runtime Adapter convergence.

Core v1.5-B evidence:

- `core.packs.PackRegistry` loads repository-local `packs/*/manifest.json`.
- Active packs: `meeting`, `knowledge`.
- Stub packs: `investment`, `interview`, `video_studio`.
- `pack.list` and `pack.get` are available through Gateway RPC and stdio JSONL.
- `workflow.list` includes `pack_name`, `pack_version`, and `pack_status` for manifest-backed workflows.
- Targeted regression: `tests/test_pack_registry.py tests/test_gateway_protocol.py tests/test_lead_orchestrator.py tests/test_gateway_stdio.py` passed with 22 tests.
- Stage regression: `tests/test_api_runs.py tests/test_gateway_persistence.py tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py tests/test_core_v15_protocol_store.py tests/test_pack_registry.py` passed with 70 tests.
- Real-audio acceptance passed with `/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3`; generated output was cleaned after verification.
- Draw.io validation: `xmllint --noout docs/architecture/current-vs-target-gap.drawio` passed.

Core v1.5-C evidence:

- `CoreAppService` exposes `start_job/update_job/cancel_job/get_job/list_jobs`.
- DomainWorkflow execution creates a Core job, updates it to `completed` or `failed`, and includes `job_id` in `turn.completed.data`.
- `job.list`, `job.get`, `job.cancel`, and `core.job.list` are available through Gateway RPC/stdio.
- Targeted regression: `tests/test_core_v15_protocol_store.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_lead_orchestrator.py tests/test_meeting_turn_workflow.py` passed with 36 tests.
- Stage regression: `tests/test_api_runs.py tests/test_gateway_persistence.py tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py tests/test_core_v15_protocol_store.py tests/test_pack_registry.py` passed with 72 tests.
- Real-audio acceptance passed with `/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3`; generated job `job_c3f8541207ed` reached `completed` and linked four meeting artifacts. Output and local validation records were cleaned after verification.
- Draw.io validation: `xmllint --noout docs/architecture/current-vs-target-gap.drawio` passed.
- Scope note: Core v1.5-C is synchronous Job Service MVP; background workers, progress events, and runtime cancellation are deferred.

Core v1.5-D evidence:

- `tools.policy_guard` blocks mutating builtin tools before real function execution unless approved.
- Gateway default agent tools are created with `PolicyEvaluator` and ApprovalStore checker.
- Core engine `_execute_tool_call` can enforce `tool_metadata.policy_evaluator` before `tool.execute(...)`.
- Targeted regression: `tests/test_tool_policy_middleware.py tests/test_policy_approval.py tests/test_gateway_protocol.py` passed with 20 tests.
- Stage regression: `tests/test_api_runs.py tests/test_gateway_persistence.py tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py tests/test_core_v15_protocol_store.py tests/test_pack_registry.py tests/test_tool_policy_middleware.py` passed with 77 tests.
- Real-audio acceptance passed with `/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3`; generated job `job_741a70df5a79` reached `completed`. Output and local validation records were cleaned after verification.
- Draw.io validation: `xmllint --noout docs/architecture/current-vs-target-gap.drawio` passed.
- Scope note: this phase blocks execution; automatic approval request creation from tool middleware is deferred.

Core v1.5-E evidence:

- `RuntimeHandle`, `RuntimeAdapter`, `SimpleRuntimeAdapter`, and `OpenHarnessRuntimeAdapter` define the Core runtime boundary.
- `GatewayRuntimePool` creates, invokes, streams, continues, and closes runtime sessions through adapters while preserving legacy fake-agent and RuntimeBundle tests.
- Targeted regression: `tests/test_runtime_adapter.py tests/test_gateway_protocol.py::test_gateway_runtime_bundle_backend_paths` passed with 5 tests.
- Targeted phase regression: `tests/test_runtime_adapter.py tests/test_gateway_protocol.py tests/test_rpc_stdio_compat.py tests/test_cli_headless.py` passed with 20 tests.
- Stage regression: `tests/test_api_runs.py tests/test_gateway_persistence.py tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py tests/test_core_v15_protocol_store.py tests/test_pack_registry.py tests/test_tool_policy_middleware.py tests/test_runtime_adapter.py` passed with 81 tests.
- Draw.io validation: `xmllint --noout docs/architecture/current-vs-target-gap.drawio` passed.
- Real-audio acceptance passed with `/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3`; generated job `job_e881abee5217` reached `completed` and linked four meeting artifacts. Output and local validation records were cleaned after verification.
- Scope note: this phase converges runtime ownership. Adapter-level approval coordinator injection, Core-native session/event store replacement, and background Job Worker remain future work.

V2.0 target architecture evidence:

- `docs/design/V2.0/harnessos_architecture_master_spec.md` is adopted as the formal target architecture baseline.
- `docs/architecture/harnessos_target_architecture_v2.md` records the implementation-facing V2.0 target, design quality judgment, known gaps, and next landing order.
- Current state remains Core v1.5-E; V2.0 is the target, not a completed code phase.
- Next implementation priority is Core-native session/event store, Background Job Worker, adapter-level governance injection, Pack Assembly MVP, and Connector Registry MVP.
- Draw.io validation remains required after every architecture update.

Phase 3+ development plan:

- Phase 1 and Phase 2 are complete at MVP scope; future work there is regression and hardening only.
- Phase 3-A is complete.
- Phase 3-B is the next implementation phase: Core-native Session/Event Store.
- Phase 3-C through 3-F are ordered dependencies and should not be skipped unless docs are updated with a replacement order.
- `docs/architecture/development_plan_v2.md` is the source of truth for the Phase 3+ development plan.

### Phase 2 Manual Acceptance

1. Run a normal chat turn with JSON output:
   ```bash
   python3 -m cli.main run --json '你好'
   ```
   Expected: result is successful and has a trace id, or trace can be queried by session/turn.

2. Run meeting real-audio analysis:
   ```bash
   python3 -m cli.main run --json '请分析 /Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3，生成会议纪要'
   ```
   Expected: meeting minutes are generated; trace links session, turn, `meeting.workflow`, and meeting artifacts.

3. Trigger a write operation:
   ```bash
   python3 -m cli.main run --json '请在 workspace 下写入 approval_test.txt，内容为 hello'
   ```
   Expected: pending approval is returned and file is not written before approval. The final text contains `操作需要审批` and an `Approval ID`.

   Optional direct policy check:
   ```bash
   printf '%s\n' '{"id":"policy-1","method":"policy.evaluate","params":{"tool_name":"workspace_write_file","tool_input":{"file_path":"approval_test.txt"}}}' | python3 -m apps.gateway.stdio_server
   ```
   Expected: `requires_approval=true` and `action=workspace.write`.

4. Reject and approve approval requests through RPC:
   ```json
   {"id":"reject","method":"approval.reject","params":{"approval_id":"<approval_id>","reason":"manual test"}}
   ```
   ```json
   {"id":"approve","method":"approval.approve","params":{"approval_id":"<approval_id>"}}
   ```
   Expected: rejection/approval update approval status and trace.

5. Retry an approved action:
   ```json
   {"id":"retry","method":"turn.retry","params":{"session_id":"<session_id>","approval_id":"<approval_id>"}}
   ```
   Expected: retry succeeds only after approval is `approved`; returned events include `retry_of_turn_id` and `approval_id`.

6. Verify masking:
   ```bash
   python3 -m cli.main run --json '请记录测试密钥 sk-test-1234567890 和 Authorization: Bearer abcdef'
   ```
   Expected: trace/log/artifact output contains only masked secret values.

---

## V2.0: Protocol-first Harness Core + OS-like App Server

**Goal**: Move from Gateway-centered assistant to reusable Core + Domain Pack platform.

### Acceptance Criteria

| Category | Criteria | Verification |
|----------|----------|--------------|
| **Core Objects** | Session, Thread, Turn, Item are first-class and queryable | Protocol tests |
| **SQLite Store** | New state writes to SQLite, legacy JSON can be imported/read | Store tests |
| **Domain Packs** | meeting/knowledge real packs; investment/interview/video stubs | Complete MVP: Pack registry and Gateway RPC tests |
| **Long Tasks** | Meeting real audio runs through Job Service | Complete MVP: synchronous workflow job record and query tests |
| **Policy** | Tool execution layer blocks risky writes/sends/publishes/trades until approval | Complete MVP: builtin/Core engine middleware tests |
| **Artifacts** | Job outputs produce trace-linked artifacts with lineage | Artifact tests |
| **Documentation** | Current/target diagrams and acceptance docs updated each stage | Doc review |

### Exit Condition
- [ ] Core protocol models implemented
- [ ] SQLite Store enabled for new writes
- [ ] Legacy JSON/JSONL migration path exists
- [x] Pack Registry loads five pack manifests
- [x] Meeting Pack real-audio job acceptance passes for synchronous Job MVP
- [x] Tool Policy Middleware protects risky tools in builtin/Core engine MVP paths
- [ ] Docs and drawio updated after implementation stage

---

## Phase 4: Local Video Workflow Integration

**Goal**: Connect AI short drama production execution layer

### Acceptance Criteria

| Category | Criteria | Verification |
|----------|----------|--------------|
| **Orchestration** | Input short drama brief → output script, storyboard, shot list | E2E test |
| **Task Flow** | Launch local video workflow task, poll status continuously | Integration test |
| **Artifact Flow** | `script → storyboard → assets → render output` artifact lineage traceable | Lineage test |
| **Retry** | Single shot or single render step failure supports local retry | Chaos test |
| **Batch** | At least 3 consecutive short drama tasks complete in batch | Batch test |
| **Approval** | Human confirmation point before publish or final render | Approval test |
| **Documentation** | Local video adapter integration manual complete | Doc review |

### Exit Condition
- [ ] Brief → script + storyboard + shot list
- [ ] Video workflow jobs launchable + pollable
- [ ] Artifact lineage (script→storyboard→assets→output) traceable
- [ ] Local retry on step failure
- [ ] 3 consecutive batch jobs complete
- [ ] Approval gate before publish/render
- [ ] Video adapter integration manual complete

---

## Phase 5: Open Source & Production Ready

**Goal**: From "project" to "product + platform"

### Acceptance Criteria

| Category | Criteria | Verification |
|----------|----------|--------------|
| **API Stability** | External API versioned, core schema frozen to `v1alpha` or `v1beta` | Schema review |
| **Extensibility** | tools/skills/plugins each have 2+ third-party extension examples | Extension samples |
| **Developer Experience** | New developer can run smoke test locally in 30 minutes | Onboarding test |
| **Legal** | LICENSE, contribution agreement, privacy + telemetry notice complete | Legal review |
| **Release** | tag, changelog, release note, CI release pipeline functional | Release test |
| **Documentation** | Architecture docs, extension dev docs, deployment docs complete | Doc review |
| **Production Ready** | Multi-tenant policy, audit strategy, billing/rate limit interfaces reserved | Architecture review |

### Exit Condition
- [ ] API versioned, core schema frozen
- [ ] 2+ extension examples per (tools/skills/plugins)
- [ ] Developer can run smoke test in ≤30 min
- [ ] LICENSE + CLA + privacy notice present
- [ ] Release pipeline (tag + changelog + notes) functional
- [ ] Architecture + extension + deployment docs complete
- [ ] Multi-tenant + audit + billing interfaces reserved

---

## Module Acceptance Matrix

| Module | Directory | Phase Required | Acceptance Criteria |
|--------|-----------|----------------|---------------------|
| API Gateway / BFF | `apps/api` | 0 | `/v1/runs` → streaming, `/v1/uploads` → artifact |
| Web App | `apps/web` | 0 | Chat UI + file upload + results page load |
| Core Schemas | `core/schemas` | 0 | All 12 types in `RunEvent`, `Artifact`, `ToolCallRecord` |
| Orchestration Service | `core/orchestration` | 0 | Intent routing + workflow dispatch functional |
| Agent Runtime Adapter | `core/runtime_adapter` | 0 | Wraps Deep Agents, doesn't leak underlying impl |
| Knowledge Service | `core/knowledge` | 1 | Ingest → search → cite with source tracking |
| Memory Service | `core/memory` | 2 | User profile + long-term memory + session summary |
| Artifact Service | `execution/artifacts` | 0 | Save + version + access + lineage |
| Workspace Service | `execution/workspace` | 0 | Per-session/per-task workspace isolation |
| Job Service | `execution/jobs` | 3 | Background + retry + cancel + poll |
| Sandbox Adapter | `execution/sandbox` | 0 | Shell/fs/browser execution adapter |
| Media Pipeline Adapter | `execution/video_pipeline` | 4 | Local video workflow integration |
| Tools Registry | `tools/` | 0 | 10 minimum tools registered and functional |
| Skills Registry | `skills/` | 1 | 10 minimum skill manifests in markdown |
| Developer Plane | `devplane/` | 2 | CLI + TUI + commands + hooks functional |
| Policy & Approval | `core/policies` | 2 | Approval + permission + risk rules enforced |
| Observability | `infra/observability` | 0 | Trace + metrics + logs + error dashboard |

---

## Test Execution Schedule

| Phase | Test Focus | Minimum Tests | Quality Gate |
|------|-----------|---------------|--------------|
| 0 | Smoke + unit | 20 | 100% pass |
| 1 | E2E scenarios | 30 | 80% completion |
| 2 | Security + multi-tenant | 50 | 0 security issues |
| 3 | Concurrency + load | 80 | 85% completion |
| 4 | Batch + lineage | 100 | All pass |
| 5 | Onboarding + release | 120 | 100% pass |

---

## v1 Minimum Tool Set (10 tools)

For MVP, these 10 tools must be implemented first:

1. `workspace_ls` - List directory
2. `workspace_read_file` - Read workspace file
3. `workspace_write_file` - Write file/draft
4. `artifact_save` - Save structured output as artifact
5. `kb_ingest` - Document ingestion + indexing
6. `kb_search` - Knowledge fragment search
7. `transcript_parse` - Parse meeting transcript/captions
8. `score_answer` - Structured scoring
9. `draft_email` - Generate email draft
10. `approval_request` - Request approval for high-risk tools

---

## v1 Minimum Skill Set (10 skills)

| Skill | Trigger | Phase |
|-------|---------|-------|
| `global-routing` | Lead agent receives complex task | 0 |
| `meeting-prep` | Pre-meeting preparation | 1 |
| `meeting-minutes` | Post-meeting summary | 1 |
| `action-items` | Extract action items from meeting | 1 |
| `jd-gap-analysis` | JD vs candidate background comparison | 1 |
| `mock-interview` | Generate mock Q&A | 1 |
| `answer-review` | Review and score answers | 1 |
| `knowledge-ingest` | Document ingestion | 1 |
| `knowledge-synthesis` | Topic synthesis from citations | 1 |
| `followup-scheduler` | Follow-up email/calendar drafting | 2 |
