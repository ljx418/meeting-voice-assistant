# ResearchNotebook V1.0 Architecture Baseline

文档状态：V1.0 planning baseline。
配套核心文档：`v1_0_current_gap_analysis.md` 与 `v1_0_current_gap_analysis.drawio`。

## 1. 架构定位

ResearchNotebook V1.0 是 `data_service` 之上的产品应用层。

```text
Plane-0 Product Interaction
  NotebookLM-like source-grounded ask
  Obsidian-like workspace / graph / backlink mental model

Plane-1 ResearchNotebook Frontend App
  routes / UI state / AppShell / source trace drawer / evidence affordance

Plane-2 API Adapter Contract
  shared/api/dataServiceClient.ts
  typed client / runtime validation / contract tests

Plane-3 data_service Target APIs
  /api/workspaces/... workspace / source / build / query / session / graph / quality

Plane-4 data_service Knowledge Backend
  ingestion / indexing / retrieval / graph / artifact refs / governance

Plane-5 Future Service Contracts
  capability manifest / DocumentUnit / EvidenceSpan / Assessment routes
```

## 2. 前端拥有的职责

ResearchNotebook owns:

- page routing；
- UI shell；
- product navigation；
- local UI state；
- source library presentation；
- source-level citation affordance；
- source trace/provenance drawer；
- session workbench；
- graph visualization；
- lightweight feedback UI；
- unsupported/future capability states。

## 3. 后端拥有的职责

`data_service` owns:

- workspace identity；
- source import and governance；
- parser and extraction；
- build/index lifecycle；
- retrieval and query；
- graph data；
- session-scoped knowledge；
- quality governance；
- stable artifact refs；
- future multi-format and assessment contracts。

## 4. API Boundary

Rules:

- route shapes live only in `shared/api/dataServiceClient.ts`;
- feature modules call typed wrappers, not raw `fetch`;
- IDs are service-owned stable identifiers;
- artifacts are referenced by `artifact_ref`, not read from disk;
- build/session build operations are polled by `operation_id`;
- normalized error envelopes map to product states。

## 5. Product Priority Boundary

V1.0 priority:

```text
source library > ask with evidence > session workbench > graph context > lightweight feedback
```

Quality/Governance must not become the primary product surface.

Assessment is a future product line and backend contract phase, not V1.0 implementation.
