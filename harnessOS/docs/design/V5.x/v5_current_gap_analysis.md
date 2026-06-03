# V5 Current Gap Analysis

文档状态：V5 baseline frozen for planning audit。本文用于 V5 gap 审计，不实现功能。

## Current V5 Baseline

```text
Current V5 baseline:
- V4-U9 closure is accepted; V4 feature development is closed.
- V5-0 planning gate is complete / ready for review.
- V5-1 core tenant boundary slice is ready for review, not enterprise auth ready.
- V5-2 core credential/provider lifecycle slice is ready for review, not production secret lifecycle ready.
- V5-3 core observability/audit export slice is ready for review, not production audit export ready.
- V5-4A Agent executor safety gate core slice is ready for review, not Agent executor ready.
- V5-4B synthetic controlled executor dev/local trial is ready for review, not controlled executor ready.
- V5-4C existing V4 local runtime controlled trial is ready for review after bounded dev/local bridge validation.
- V5-5 external app onboarding boundary core slice is ready for review, not production-ready external app support.
- V5-6 Thin Web Console productization slice is ready for review, not complete Workflow Studio ready.
- V5-7A production controlled executor design gate is ready for review, not production controlled executor ready.
- V5-7B limited staging runtime slice is accepted for V5-8 planning entry after external review closure; it remains not production controlled executor ready.
- V5-8A distributed runtime planning gate is ready for review, backed by the existing UX-12 real local Markdown + MiniMax provider evidence.
- V5-8B minimal distributed run coordination slice is ready for review, backed by existing V4 UX-08/09/10 MiniMax provider-backed evidence plus in-memory coordination validation.
- V5-8C artifact lineage and attempt recovery slice is ready for review, backed by existing V4 UX-10 MiniMax provider-backed evidence plus read-only lineage projection.
- V5-8D policy / credential / observability slice is ready for review, backed by existing V4 UX-09 MiniMax provider-backed evidence plus read-only audit projection.
- V5-8E distributed runtime acceptance package is complete and ready for review.
- V5-8 complete: distributed multi-Agent runtime slice ready for review. This is still not full multi-Agent orchestration ready, Agent executor ready, production controlled executor ready, production-ready external app support, or complete Workflow Studio ready.
```

## 1. Baseline

V4-U9 已关闭：

```text
V4-U9 complete: V4 dev/local final human acceptance and V5 handoff package ready for review.
```

V5 从 V4 dev/local evidence 出发，但必须补齐 production productization gaps。

## 2. Gap Table

| Area | V4 Current State | V5 Required State | Status | Owner Stage | Production Blocker |
| --- | --- | --- | --- | --- | --- |
| Mission Console | dev/local evidence | production auth-aware mission entry | inherited_from_v4_devlocal | V5-1 / V5-6 | yes |
| WorkflowSpec Registry | dev/local registry boundary | tenant-bound registry with audit | inherited_from_v4_devlocal | V5-1 / V5-3 | yes |
| Runtime Report | read-only dev/local report | production runtime report with audit source refs | inherited_from_v4_devlocal | V5-3 / V5-6 | yes |
| Review Console | user-confirmed handoff baseline | production policy and approval integrated review | inherited_from_v4_devlocal | V5-4 / V5-6 | yes |
| Evidence Chain | dev/local evidence chain | retained and exportable production audit evidence | inherited_from_v4_devlocal | V5-3 | yes |
| Production Auth Planning | not implemented | enterprise auth boundary implementation plan | completed_for_review | V5-1 planning | yes |
| Tenant Isolation Planning | not implemented | tenant / workspace / app ownership implementation plan | completed_for_review | V5-1 planning | yes |
| Production Auth Core Guard Slice | not implemented | server-bound identity context and audit-aware guard | completed_for_review | V5-1 implementation | yes |
| Tenant Isolation Core Guard Slice | not implemented | tenant / workspace / project / app ownership validation | completed_for_review | V5-1 implementation | yes |
| Enterprise Auth / Tenant Control Plane | not implemented | OAuth/SSO and tenant admin productization | not_implemented | future V5 stage decision | yes |
| Credential Lifecycle Planning | not implemented | issue / rotate / revoke / audit implementation plan | completed_for_review | V5-2 planning | yes |
| Provider Lifecycle Planning | dev/local provider invocation evidence | provider profile and credential boundary implementation plan | completed_for_review | V5-2 planning | yes |
| Credential Lifecycle Implementation | not implemented | issue / rotate / revoke / audit core lifecycle slice | completed_for_review | V5-2 implementation | yes |
| Provider Lifecycle Implementation | dev/local provider invocation evidence | provider profile runtime and redacted invocation evidence core slice | completed_for_review | V5-2 implementation | yes |
| Production Secret Store Integration | not implemented | managed secret store, rotation backend, access broker | not_implemented | future V5 stage decision | yes |
| Observability Planning | dev/local evidence | metrics, alerting, incident timeline implementation plan | planning_package_ready_for_review | V5-3 planning | yes |
| Audit Export Planning | report evidence only | retained exportable audit package implementation plan | planning_package_ready_for_review | V5-3 planning | yes |
| Observability Implementation | dev/local evidence | production metrics, alerting, incident timeline | core_slice_ready_for_review | V5-3 implementation | yes |
| Audit Export Implementation | report evidence only | retained exportable audit package | core_slice_ready_for_review | V5-3 implementation | yes |
| Agent Executor Safety Gate Planning | not ready | design and safety gate only in V5-4A | planning_package_ready_for_review | V5-4A planning | yes |
| Agent Executor Safety Gate Implementation | not ready | safety gate runtime checks, not executor readiness | core_slice_ready_for_review | V5-4A implementation | yes |
| Synthetic Controlled Executor Trial Planning | not ready | synthetic in-memory dev/local trial only | completed_for_review | V5-4B planning | yes |
| Synthetic Controlled Executor Trial Implementation | not ready | synthetic in-memory trial only, not controlled executor ready | core_slice_ready_for_review | V5-4B implementation | yes |
| Existing V4 Runtime Controlled Trial Planning | not ready | dev/local existing V4 local runtime trial only | completed_for_review | V5-4C planning | yes |
| Existing V4 Runtime Controlled Trial Implementation | not ready | V4 local runtime trial only, not production executor | core_slice_ready_for_review | V5-4C implementation | yes |
| External App Onboarding Planning | not implemented | app registration, domain verification, quota implementation plan | planning_package_ready_for_review | V5-5 planning | yes |
| External App Onboarding Implementation | not implemented | app registration, domain verification, quota | core_slice_ready_for_review | V5-5 implementation | yes |
| Thin Web Console Productization Planning | dev/local thin console | productized Thin Web Console first implementation plan | planning_package_ready_for_review | V5-6 planning | no |
| Thin Web Console Productization Implementation | dev/local thin console | productized Thin Web Console first | core_slice_ready_for_review | V5-6 implementation | no |
| Complete Web Studio | not complete | separate PRD and acceptance required | planned | post V5-6 decision | no |
| Production Controlled Executor Design Gate | not implemented | production execution policy, sandbox, rollback, idempotency, audit, incident design gate after V5-6 | design_gate_ready_for_review | V5-7A planning | yes |
| Production Controlled Executor Runtime Slice | limited staging runtime semantics implemented, no route / no worker | limited production-controlled execution runtime with tenant, credential, audit, rollback, kill-switch enforcement | staging_slice_ready_for_review | V5-7B implementation | yes |
| Distributed Multi-Agent Runtime Planning Gate | V5-8A planning gate PASS with UX-12 real local Markdown + MiniMax provider evidence reused as readiness input | production distributed runtime implementation plan reviewed with real-data readiness and No False Green guard | planning_gate_ready_for_review | V5-8A planning | yes |
| Distributed Run Coordination Implementation | V5-8B minimal coordination slice ready for review; no routes / no production workers / no Agent mutation | minimal coordinator / worker assignment / run state transition / restart recovery slice | core_slice_ready_for_review | V5-8B implementation | yes |
| Distributed Artifact Lineage And Attempt Recovery | V5-8C lineage / attempt recovery projection ready for review; no production worker lifecycle | artifact lineage and attempt recovery at distributed runtime scale | core_slice_ready_for_review | V5-8C implementation | yes |
| Distributed Policy / Credential / Observability Runtime | V5-8D policy / credential / observability projection ready for review; no production worker lifecycle | distributed audit export, credential boundary, incident timeline, policy enforcement | core_slice_ready_for_review | V5-8D implementation | yes |
| Distributed Multi-Agent Runtime Acceptance | V5-8E final acceptance package PASS with V5-8A/B/C/D evidence and UX-08/09/10 provider-backed evidence | bounded distributed runtime slice ready for review | slice_ready_for_review | V5-8E acceptance | yes |

## 3. No False Green

The following are not complete in V4 and must not be claimed complete in V5-0:

```text
production-ready external app support
Agent executor ready
controlled executor ready
complete Workflow Studio ready
full multi-Agent orchestration ready
autonomous workflow editing ready
```

V5-1 cannot claim enterprise auth ready unless full acceptance passes. V5-4A cannot claim Agent executor ready. V5-6 cannot claim complete Workflow Studio ready. V5-8 cannot convert V4 UX-08 / UX-09 / UX-10 dev/local provider-backed evidence into full multi-Agent orchestration ready.

V5-1 currently proves only a core boundary guard slice. It does not prove enterprise auth ready, multi-tenant control plane ready, production external app onboarding, or production audit export.

V5-2 currently proves only a core credential / provider lifecycle slice. It includes provider profile DTO, credential reference lifecycle events, redacted provider smoke evidence, source/user confirmation guard, and local `.env.local` provider config validation. It does not implement managed production secret storage, production credential rotation infrastructure, BFF routes, provider billing controls, or production audit export.

V5-3 currently proves only a core observability / audit export slice. It includes redacted security event logging, user-confirmed audit export package creation, source=agent export denial, read-only metrics/alerting outputs, and read-only incident timeline construction. It does not implement production audit export infrastructure, production observability platform, BFF routes, audit retention jobs, production SIEM integration, or production audit export readiness.

V5-4A currently proves only an Agent executor safety gate core slice. It includes policy classification, capability decision, approval gate planning, sandbox input rejection, kill switch checks, and runtime evidence contract shape. It does not execute actions, create executor routes, grant Agent durable mutation authority, implement controlled executor runtime, or prove autonomous workflow editing.

V5-4B currently proves only a synthetic in-memory controlled executor dev/local trial. It includes user-confirmed synthetic workflow start, user-confirmed synthetic station rerun, attempt history retention, downstream stale marker, kill switch denial, approval-gated denial, and redacted runtime evidence marked synthetic_only=true / runtime_backed=false. It does not call existing V4 local runtime, implement controlled executor readiness, grant Agent mutation authority, or prove production controlled executor readiness.

V5-4C now proves only a bounded existing V4 local runtime bridge. It calls the existing `/bff/v4_2/runtime` dev/local BFF entrypoint after user-confirmation, source, kill-switch, redaction, and evidence guards. It does not write WorkflowStore directly, create executor routes, grant Agent mutation authority, or prove production controlled-execution readiness.

Production controlled executor is intentionally moved after V5-6. V5-7A now proves only a design gate ready for review, with policy matrix, runtime action allowlist, execution envelope schema, sandbox input descriptor schema, rollback descriptor schema, kill-switch decision schema, and execution evidence schema. V5-7B has a recorded high-risk proceed decision for limited staging runtime code and focused tests, but it remains blocked from production route / worker exposure and cannot be claimed as production controlled executor ready. Neither stage may inherit V5-4B synthetic evidence or V5-4C dev/local evidence as production execution readiness.

V5-5 currently proves only an in-memory external app onboarding boundary core slice. It includes tenant-bound app registration, domain verification before origin allowlist, unknown origin denial, quota/rate-limit denial evidence, offboarding access revocation, and SDK browser route guard. It does not issue production credentials, create production onboarding routes, implement production customer onboarding, or prove production-ready external app support.

V5-6 currently proves only a Thin Web Console productization slice. It includes read-only Runtime Report, read-only Evidence Review, Audit Export handoff, External App admin observation, manual confirmation record, and browser-safety assertions. It does not implement complete Workflow Studio or new runtime behavior.

V5-7A currently proves only a production controlled executor design gate ready for review. V5-7B currently proves only an isolated staging runtime slice for workflow.instance.start, station.rerun, artifact.write, and quality.evaluation.create with user confirmation, human authorization, approved_api/service_account boundary checks, idempotency, attempt history, append-only artifact/quality behavior, kill-switch denial, and redacted execution evidence. It does not implement production executor routes, runtime workers, Agent direct durable mutation, unrestricted connector calls, unrestricted external LLM calls, or production controlled executor readiness.

V5-8A currently proves only a distributed runtime planning gate ready for review. It validates that the required V5-8 planning documents exist and that the existing UX-12 evidence has real local Markdown read evidence plus MiniMax provider-backed summary evidence.

V5-8B currently proves only a minimal in-memory distributed coordination slice ready for review. It validates DistributedRunCoordinator, AgentWorkerRegistry, scoped worker assignment, restart recovery, lost-worker recovery, source=agent denial, and tenant-scope denial against existing V4 UX-08/09/10 MiniMax provider-backed evidence. It does not implement production routes, production worker processes, unrestricted connector calls, unrestricted external LLM calls, complete distributed recovery, or distributed multi-Agent runtime readiness.

V5-8C currently proves only artifact lineage and attempt recovery projection ready for review. It validates append-only AttemptHistoryStore, ArtifactLineageService, producer attempt tracking, lineage recovery after retry, and read-only Runtime Report projection against existing V4 UX-10 MiniMax provider-backed evidence. It does not implement distributed audit export, production worker lifecycle, full recovery manager, or distributed multi-Agent runtime readiness.

V5-8D currently proves only policy / credential / observability projection ready for review. It validates worker credential refs, source=agent mutation denial, unrestricted connector/external LLM denial flags, audit event projection, incident timeline projection, read-only audit export projection, and redaction against existing V4 UX-09 MiniMax provider-backed evidence. It does not implement production observability infrastructure, production audit export infrastructure, production worker lifecycle, or distributed multi-Agent runtime readiness.

V5-8E currently proves only a bounded distributed runtime slice ready for review. It validates the V5-8A/B/C/D evidence packages and existing UX-08/09/10 MiniMax provider-backed scenario evidence. It still does not prove full multi-Agent orchestration readiness, Agent executor readiness, production controlled executor readiness, production-ready external app support, complete Workflow Studio readiness, or autonomous workflow editing readiness.

## 4. Recommended V5-0 Audit Questions

```text
1. Does every production blocker have an owner V5 stage?
2. Does the gap table distinguish inherited_from_v4_devlocal from production-ready?
3. Does V5-0 avoid implementation claims?
4. Does V5 planning preserve V4 runtime truth boundaries?
5. Are Agent executor and controlled executor still behind safety gates?
6. Has V5-1 implementation been held until a separate V5-1 PRD, architecture delta, ownership model, route design, audit fields, test matrix, and claim guard pass review?
7. Does the V5-1 planning package avoid claiming enterprise auth ready or multi-tenant control plane ready?
8. Does the V5-2 planning package avoid treating provider env keys or dev/local LLM evidence as production credential lifecycle?
9. Do V5-3 to V5-8 planning docs avoid overclaiming implementation readiness?
10. Does V5-8 keep V4 UX-08/09/10 limited to dev/local evidence?
```
