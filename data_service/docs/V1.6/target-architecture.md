# Data Service V1.6 Target Architecture

更新时间：2026-05-12

## Target Shape

V1.6 的目标形态是在 V1.5 accepted baseline 上继续推进 MCP-first、最小粒度和微服务边界清晰化。

```text
External Apps / Agents / CLI / Console
  -> MCP primary contract
  -> CLI human operator entrypoint: knowledge ...
  -> target HTTP: /api/workspaces/{workspace_id}/...
  -> Knowledge Governance Service
     -> Workspace / Source / Build lifecycle
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

## V1.6 Target Capability Groups

| group | target shape | V1.5 baseline |
| --- | --- | --- |
| public surface guard | automated scans protect MCP / CLI / HTTP public surface | PhaseG31 manual closure audit accepted |
| lifecycle target HTTP | workspace/source/build write routes use stable IDs and operation envelopes | compatibility HTTP exists; target HTTP write routes not open |
| graph advanced | graph advanced target HTTP / CLI minimal surfaces opened in smallest useful slices where not yet open | MCP graph tools exist; CLI exposes `knowledge graph snapshot`; target HTTP graph advanced planned |
| session public contract | Session GraphRAG converges across selected surfaces through stable session IDs and envelopes | MCP session tools exist; target HTTP/session CLI planned |
| quality target HTTP | quality write routes converge on shared helpers and stable governance semantics | compatibility HTTP and CLI exist; target HTTP quality write not open |
| console governance | console shows service state, contracts and traces through target surfaces where available | `/knowledge` governance console exists |

## Non Goals

- Do not turn `/knowledge` into an end-user knowledge consumption app.
- Do not add production dependencies on meeting, ASR, interview, learning, IDE plugin or upper-layer agent workflow modules.
- Do not expose internal workspace path/layout as stable external contract.
- Do not open all V1.6 candidates in one phase.
