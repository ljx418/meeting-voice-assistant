# Data Service V1.6 Target Architecture

更新时间：2026-05-16

## Target Shape

V1.6 的目标形态是在 V1.5 accepted baseline 上继续推进 MCP-first、最小粒度和微服务边界清晰化。

V1.6-A Public Surface Guard 已 accepted。V1.6-B1 Workspace Target HTTP、V1.6-B2 Source Target HTTP、V1.6-B3 Build Target HTTP 已 accepted，并以 phase overlay 方式新增 workspace/source/build target HTTP minimal lifecycle routes。V1.6-C1 Graph Neighbors、V1.6-C2 Graph Community、V1.6-C3 Graph Query 与 V1.6-C4 Graph Session Target HTTP / CLI Minimal Surface 已 accepted，只开放 graph neighbors/community/query/session inspection 最小 read-only 公开面。V1.6-D1 Session GraphRAG contract planning / hardening 已 accepted，未新增公开面。V1.6-D2 Session Lifecycle Target HTTP Minimal Surface 已 accepted，只开放 create/list/get/close/delete 5 个 session lifecycle target HTTP routes。V1.6-D3 Session Ingest / Query / Build Contract Planning 已 accepted，未新增公开面。V1.6-D4 Session Ingest Target HTTP Minimal Surface 已 accepted，只开放 1 个 session-scoped ingest target HTTP route。V1.6-D5 Session Query Target HTTP Minimal Surface 已 accepted，只开放 1 个 session-scoped read-only query target HTTP route。V1.6-D6 Session Build Target HTTP Minimal Surface 已 accepted，只开放 session build start/status/cancel 3 个 session-scoped operation routes。V1.6-E1 Quality Feedback Target HTTP Minimal Surface 已 accepted，只开放 1 个 quality feedback route。V1.6-E2 Quality Correction Rules Target HTTP Minimal Surface 已 accepted，只开放 correction rules list/write 2 个 target HTTP routes。V1.6-E3 Quality Correction Review Target HTTP Minimal Surface 已 accepted，只开放 correction rule review 1 个 target HTTP route。V1.6-E4 Quality Correction Plan Target HTTP Minimal Surface 已 accepted，只开放 correction plan read/generate 2 个 target HTTP routes。V1.6-E5 Quality Correction Rules Build Target HTTP Minimal Surface 已 accepted，只开放 correction-rules artifact build 1 个 target HTTP route。V1.6-F1 Console Governance Evidence Baseline Sync 已 accepted，未新增公开面、未修改 frontend 或 `/knowledge` 行为。V1.6-F2 Console Governance Polish 已 accepted，只更新 `/knowledge` governance evidence display 和前端静态 build 产物，不新增 backend public surface。V1.6 Closure Acceptance 已 accepted，只做最终公开面冻结审计、focused closure test、回归验收和文档同步，不新增 backend public surface。Current accepted target HTTP route count = 35。V1.5 baseline 仍不可变；V1.7 capabilities remain planned only。

```text
External Apps / Agents / CLI / Console
  -> MCP primary contract
  -> CLI human operator entrypoint: knowledge ...
  -> target HTTP: /api/workspaces + /api/workspaces/{workspace_id}/...
  -> Knowledge Governance Service
     -> Public Surface Guard
     -> Workspace / Source / Build target HTTP minimal lifecycle
     -> Query / Distill / Trace shared contracts
     -> Quality Governance contracts
     -> Session GraphRAG public contract
     -> app.llmwiki readable wiki artifacts
     -> app.graphrag.service graph / session graph / relation extraction
```

## Architecture Principles

- MCP remains the default primary contract.
- CLI remains a human operator surface, not a separate product boundary.
- target HTTP is opened by capability group, not by exposing internal service structure.
- `/api/v1/knowledge/*` remains a compatibility surface during V1.6.
- `/knowledge` remains a service governance console.
- `app.llmwiki` owns readable wiki artifacts.
- `app.graphrag.service` owns GraphRAG, session graph and relation extraction.
- Stable external contracts use IDs and envelopes, not internal paths.
- Public surface changes must pass baseline/current/diff guard before a phase is accepted.

## V1.6 Target Capability Groups

| group | target shape | V1.5 baseline |
| --- | --- | --- |
| public surface guard | completed；automated scans protect MCP / CLI / HTTP public surface using machine-readable V1.5 baseline | PhaseG31 manual closure audit accepted |
| lifecycle target HTTP | B1 workspace、B2 source、B3 build target HTTP minimal lifecycle completed | compatibility HTTP exists; V1.5 target HTTP write routes were not open |
| graph advanced | C1 graph neighbors、C2 graph community、C3 graph query and C4 graph session inspection target HTTP / CLI completed | MCP graph tools exist; CLI exposes `knowledge graph snapshot`、`knowledge graph neighbors`、`knowledge graph community`、`knowledge graph query` and `knowledge graph session`; target HTTP graph neighbors/community/query/session inspection is open |
| session public contract | D1 contract inventory/hardening completed; D2 session lifecycle target HTTP create/list/get/close/delete completed; D3 ingest/query/build contract planning completed with no new public surface; D4 session ingest target HTTP completed; D5 session query target HTTP completed; D6 session build start/status/cancel target HTTP completed | MCP session tools exist; C4 is graph-scoped inspection only; D6 does not open quality target HTTP |
| quality target HTTP | E1 quality feedback completed；E2 correction rules completed；E3 correction review completed；E4 correction plan completed；E5 correction-rules artifact build completed | compatibility HTTP and CLI exist; quality feedback/rules/review/plan/rules-build target HTTP are open |
| console governance | F1 evidence baseline completed；F2 console polish completed | `/knowledge` governance console displays public surface evidence and remains non-consumption app |

## Non Goals

- Do not turn `/knowledge` into an end-user knowledge consumption app.
- Do not add production dependencies on meeting, ASR, interview, learning, IDE plugin or upper-layer agent workflow modules.
- Do not expose internal workspace path/layout as stable external contract.
- Do not open all V1.6 candidates in one phase.

## Phase Gate

Before entering the next phase after `V1.6-F2 Console Governance Polish`, run the public surface guard:

- MCP registry count and tool set must match V1.5 baseline.
- CLI top-level and nested command inventory must match V1.5 baseline unless the phase explicitly opens a CLI surface.
- `/api/v1/knowledge/*` compatibility routes must remain retained.
- target HTTP allowlist must match the accepted phase scope.
- No upper-layer production dependency may be introduced.
