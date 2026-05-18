# ResearchNotebook V1.0 API Adapter Contract

文档状态：P0 implementation contract；V1.0-RC1 real-route hardened。
适用阶段：M1-RC1；RC1 已按真实 data_service envelope response 做 adapter hardening。

## 1. Purpose

`shared/api/dataServiceClient.ts` 是 V1.0 唯一知道 backend route shape 的前端层。

Feature modules must not:

- call `fetch` directly;
- concatenate route strings;
- call `/api/v1/knowledge/*`;
- read raw filesystem paths, cache paths, or artifact physical paths;
- parse `artifact_ref` as a local path.

## 2. OpenAPI Fallback Strategy

If `data_service` OpenAPI or equivalent schema is not ready when M1 starts:

- hand-write V1.0 DTO types in the frontend;
- validate responses with zod, valibot, or a small custom validator;
- keep fixtures for workspace/source/build/query/session/error responses;
- expose only typed wrappers from `dataServiceClient.ts`;
- replace the hand-written DTOs with generated client/types once backend schema is ready.

This fallback is allowed only for V1.0 target routes and must not become a second route-shape layer.

## 3. Minimum DTO Set

Required V1.0 DTOs:

- `WorkspaceSummary`;
- `WorkspaceDetail`;
- `SourceSummary`;
- `SourceDetail`;
- `SourceTrace`;
- `BuildOperation`;
- `QueryRequest`;
- `QueryResponse`;
- `AnswerEvidence`;
- `SessionSummary`;
- `SessionDetail`;
- `SessionQueryResponse`;
- `GraphNode`;
- `GraphEdge`;
- `GraphNeighbor`;
- `GraphNeighborsResponse`;
- `GraphCommunity`;
- `GraphCommunitiesResponse`;
- `SessionGraphContextResponse`;
- `QualityFeedbackRequest`;
- `QualityFeedbackResponse`;
- `NormalizedErrorEnvelope`.

## 4. Typed Wrapper Surface

Minimum wrapper groups:

- `workspaces.list/create/get/archive`;
- `sources.list/create/get/remove/trace`;
- `build.start/getOperation/cancel`;
- `query.workspace`;
- `distill.workspace`;
- `sessions.create/list/get/close/ingest/query`;
- `sessions.build.start/getOperation/cancel`;
- `graph.neighbors/communities/session`;
- `quality.feedback`.

Graph wrappers are read-only in V1.0. Graph query builder / DSL and graph mutation wrappers are not part of M4 acceptance.

Correction rules/plan wrappers are not part of V1.0 release gate. Quality feedback is the only M4 quality wrapper.

Session delete is deferred and is not part of M3 acceptance.

## 5. Evidence DTO

`AnswerEvidence` is the minimum frontend ViewModel for V1.0 evidence rendering:

```ts
type AnswerEvidence = {
  sourceId?: string;
  sourceTitle?: string;
  traceAvailable: boolean;
  artifactRefs?: string[];
  snippet?: string;
  confidence?: number;
};
```

Rules:

- if `sourceId` exists, citation can open source trace drawer;
- if only `artifactRefs` exist, show evidence metadata but do not attempt filesystem resolution;
- if neither `sourceId` nor evidence metadata exists, render explicit no-evidence state.

## 6. Contract Tests

M1 contract tests must cover:

- successful workspace list/create/get;
- normalized error envelope parsing;
- backend unavailable;
- source list/detail/trace fixtures;
- build operation status fixtures;
- query response with evidence;
- query response without evidence;
- no direct `/api/v1/knowledge/*` usage in client code.

M4 contract tests must cover:

- graph neighbors success;
- graph communities success;
- session graph context success;
- missing graph artifact normalization;
- feedback submit success;
- feedback validation error normalization.

RC1 contract tests must additionally cover:

- real envelope `data.items` list fixtures;
- real query `hits` mapped to `AnswerEvidence`;
- real blocked graph envelope mapped to `missing_graph_artifact`;
- target request body mapping for source import, query, session ingest, and feedback.
