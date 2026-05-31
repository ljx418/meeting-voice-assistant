# Data Service V1.6 当前架构与目标架构差距分析

更新时间：2026-05-16

## 1. 文档定位

本文档是 V1.6 的 Current vs Target / Gap 设计文档，用来说明：

- V1.5 accepted baseline 下当前系统是什么样。
- V1.6 目标架构希望收敛到什么样。
- 当前架构与目标架构之间有哪些明确差距。
- 每个 V1.6 阶段分别解决哪些差距。
- 每个阶段的验收重点是什么。

本文档以 V1.5 accepted baseline 为冻结起点，并同步记录 V1.6 已接受阶段。V1.6-A、V1.6-B1/B2/B3、V1.6-C1/C2/C3/C4、V1.6-D1/D2/D3/D4/D5/D6、V1.6-E1/E2/E3/E4/E5、V1.6-F1、V1.6-F2 与 V1.6 Closure Acceptance 已 completed。V1.6 Closure Acceptance 只做最终公开面冻结审计、回归验收和文档同步，不新增 backend public surface。

同步规则：每次更新本文档后，必须同步更新 `docs/V1.6/current-vs-target-gap.drawio`，确保 Markdown 与 drawio 在阶段状态、当前架构、目标架构、Gap 清单、route count 和验收门禁上保持一致。

## 2. V1.5 冻结基线

V1.5 已完成 PhaseG31 / PhaseG31.1 收口验收，并作为 V1.6 的起点。

V1.5 baseline：

- MCP tool count：`40`。
- CLI 顶层命令：`build / graph / quality / query / source / trace / workspace`。
- 旧 HTTP 兼容入口：`/api/v1/knowledge/*` 保留。
- V1.5 target HTTP baseline 固定为 3 个 route：
  - `POST /api/workspaces/{workspace_id}/query`
  - `POST /api/workspaces/{workspace_id}/distill`
  - `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`
- MCP graph / session tools 已存在于 V1.5 baseline。
- `knowledge graph` CLI 当前开放 `snapshot`、V1.6-C1 `neighbors`、V1.6-C2 `community`、V1.6-C3 `query` 与 V1.6-C4 `session`。
- `/knowledge` 是 service governance console，不是终端用户知识消费 App。

V1.5 已闭环事项不再作为 V1.6 gap：

- MCP handler 模块化。
- GraphRAG service / session relation extractor 边界抽取。
- MCP / HTTP envelope、error code、debug path contract hardening。
- typed distill units。
- docx / yaml 格式扩展。
- query / distill / source trace shared contract。
- Quality shared helper 与 CLI alias。
- `/knowledge` 治理控制台基础可视化与前端验收。
- PhaseG31 / PhaseG31.1 closure acceptance。

## 3. 当前架构

当前系统是 MCP-first 的本地知识治理微服务。MCP 是默认主入口，CLI 是面向人的操作入口，HTTP 同时存在旧兼容入口和少量 target HTTP 入口。

```text
External Apps / Agents / Operator / Console
  -> MCP primary surface
  -> CLI: knowledge ... / data_service ...
  -> HTTP compatibility: /api/v1/knowledge/*
  -> target HTTP: V1.5 query / distill / source trace
                  V1.6-B1 workspace create/list/describe/archive
                  V1.6-B2 source import/list/describe/remove
                  V1.6-B3 build start/status/cancel
                  V1.6-C1 graph neighbors
                  V1.6-C2 graph community
                  V1.6-C3 graph query
                  V1.6-C4 graph session inspection
                  V1.6-D2 session lifecycle create/list/get/close/delete
                  V1.6-D4 session ingest
                  V1.6-D5 session query
                  V1.6-D6 session build start/status/cancel
                  V1.6-E1 quality feedback
                  V1.6-E2 quality correction rules
                  V1.6-E3 quality correction review
                  V1.6-E4 quality correction plan
                  V1.6-E5 correction-rules artifact build

Knowledge Governance Service
  -> Workspace / Source / Build lifecycle
  -> Query / Distill / Trace shared contracts
  -> Quality governance shared helpers
  -> Session service orchestration
  -> app.llmwiki readable wiki artifacts
  -> app.graphrag.service GraphRAG / session graph / relation extraction

Internal Storage / Artifacts
  -> workspace layout
  -> source registry
  -> build operations
  -> distill bundles
  -> graph artifacts
  -> quality artifacts
```

当前架构特点：

- `backend/data_service` 负责 workspace、source、build、query、distill、trace、quality、MCP、CLI 与 HTTP contract 编排。
- `app.llmwiki` 负责可读 wiki artifacts。
- `app.graphrag.service` 负责 GraphRAG、session graph、relation extraction。
- 外部 contract 已开始从内部 path/layout 收敛到 `workspace_id`、`source_id`、`session_id`、`operation_id`、`artifact_ref`。
- 旧 `/api/v1/knowledge/*` 仍是兼容入口，不能在 V1.6 早期破坏。
- target HTTP 仍按最小能力组推进，当前已覆盖 query、distill、source trace、workspace/source/build lifecycle 最小面、graph neighbors/community/query/session inspection 只读最小面、session lifecycle/ingest/query/build 最小面，以及 quality feedback / correction rules / correction review / correction plan / correction-rules artifact build 最小面。Current accepted target HTTP route count = 35。

## 4. 目标架构

V1.6 目标不是把 data_service 做成终端用户 App，而是在 V1.5 accepted baseline 上继续收敛为边界清晰、公开面可控、契约一致的本地知识治理微服务。

```text
External Apps / Agents / Operator / Console
  -> MCP primary contract
  -> CLI human operator surface: knowledge ...
  -> target HTTP by capability group:
       /api/workspaces/{workspace_id}/...
  -> compatibility HTTP retained during migration:
       /api/v1/knowledge/*

Knowledge Governance Service
  -> Public Surface Guard
  -> Workspace / Source / Build target lifecycle contracts
  -> Query / Distill / Trace stable contracts
  -> Graph advanced target HTTP / CLI minimal surfaces
  -> Cross-surface Session GraphRAG public contract
  -> Quality target HTTP write contracts
  -> Console governance evidence

Domain Engines
  -> app.llmwiki owns readable wiki artifacts
  -> app.graphrag.service owns graph/session graph/relation extraction

Stable External Contract
  -> workspace_id
  -> source_id
  -> session_id
  -> operation_id
  -> artifact_ref
  -> envelope / error contract
```

目标架构原则：

- MCP 继续是 primary contract。
- CLI 继续是人类操作者入口，不成为新的产品边界。
- target HTTP 按 capability group 分阶段开放，不镜像内部方法。
- 旧 `/api/v1/knowledge/*` 在 V1.6 期间继续保留。
- 新公开面必须复用 shared helper 或既有 MCP handler。
- 内部 workspace path/layout 只能是 debug/console-only，不作为稳定 contract。
- `/knowledge` 继续是治理控制台，不转成 end-user knowledge consumption app。

## 5. 当前架构与目标架构关联关系对比

| 领域 | 当前架构 | V1.6 目标架构 | 主要差距 |
| --- | --- | --- | --- |
| 公开面治理 | V1.6-A 已将 PhaseG31 人工审计固化为自动化 guard | 每个阶段自动扫描 MCP / CLI / HTTP / target HTTP | 后续阶段必须持续执行 guard |
| MCP | 40 个 tools，作为主入口 | 保持主入口；除阶段明确声明外不新增 tool | 需要防止隐藏性新增 |
| CLI | `knowledge ...` 已覆盖多个治理能力，graph 开放 snapshot + C1 neighbors + C2 community + C3 query + C4 session | 按最小能力组补齐尚未开放的 operator surface | session lifecycle CLI 仍需规划 |
| 旧 HTTP | `/api/v1/knowledge/*` 保留 | 继续保留为 compatibility surface | 需要迁移期保护 |
| target HTTP | V1.5 query / distill / source trace + V1.6-B1 workspace create/list/describe/archive + V1.6-B2 source import/list/describe/remove + V1.6-B3 build start/status/cancel + V1.6-C1 graph neighbors + V1.6-C2 graph community + V1.6-C3 graph query + V1.6-C4 graph session inspection + V1.6-D2 session lifecycle create/list/get/close/delete + V1.6-D4 session ingest + V1.6-D5 session query + V1.6-D6 session build start/status/cancel + V1.6-E1 quality feedback + V1.6-E2 quality correction rules + V1.6-E3 quality correction review + V1.6-E4 quality correction plan + V1.6-E5 correction-rules artifact build | 分阶段补齐 lifecycle、graph、quality、session | correction apply target HTTP 未开放 |
| Workspace / Source / Build | workspace/source/build target HTTP 已开放最小面 | target HTTP 使用稳定 ID 与 operation envelope | lifecycle target HTTP 最小面已完成，后续需保持 drift guard |
| Query / Distill / Trace | 已有 shared contract，target HTTP 已覆盖首批 3 routes | 继续硬化 artifact_ref、envelope、error consistency | 需要跨入口一致性 guard |
| GraphRAG | MCP graph tools 已存在；CLI snapshot + neighbors + community + query + session；target HTTP 已开放 graph neighbors/community/query/session inspection | Graph advanced target HTTP / CLI 最小公开面 | graph advanced 最小 read-only surface 已完成；不能误把 MCP tools 当作 V1.6 新增 |
| Session GraphRAG | MCP session tools 已存在；D1 contract hardening 已完成；D2 已开放 session lifecycle target HTTP create/list/get/close/delete；D4 已开放 session-scoped ingest target HTTP；D5 已开放 session-scoped read-only query target HTTP；D6 已开放 session-scoped build start/status/cancel target HTTP | 跨 MCP / CLI / HTTP / target HTTP 的 public contract convergence | full Session GraphRAG public contract 收敛仍需持续 guard；quality 不属于 D6 |
| Quality Governance | MCP / CLI / compatibility HTTP 已可用；E1 已开放 quality feedback target HTTP；E2 已开放 quality correction rules target HTTP；E3 已开放 quality correction review target HTTP；E4 已开放 quality correction plan target HTTP；E5 已开放 correction-rules artifact build target HTTP | quality write target HTTP 复用 shared helper | correction apply target HTTP 未开放 |
| Console | `/knowledge` 已是治理控制台 | 展示 public surface、target migration、contract evidence | 需要治理证据更清晰 |
| 外部 contract | 已开始使用稳定 ID 和 artifact_ref | 全部新入口稳定依赖 ID/envelope | 仍需规范化和 drift tests |

## 6. V1.6 Gap 清单

| Gap | 当前状态 | 目标状态 | 优先级 | 对应阶段 |
| --- | --- | --- | --- | --- |
| 公开面护栏不可重复 | V1.6-A 已完成机器可读 baseline 与自动化 guard | 每个阶段都有 MCP / CLI / HTTP / target HTTP 扫描 | closed / ongoing gate | V1.6-A |
| target HTTP lifecycle write 缺失 | V1.6-B1 已开放 workspace target HTTP；V1.6-B2 已开放 source target HTTP；V1.6-B3 已开放 build target HTTP | target HTTP 分阶段开放 lifecycle write routes | closed / ongoing guard | V1.6-B |
| Graph advanced target/CLI surface 缺失 | V1.6-C1 已开放 graph neighbors target HTTP / CLI；V1.6-C2 已开放 graph community target HTTP / CLI；V1.6-C3 已开放 graph query target HTTP / CLI；V1.6-C4 已开放 graph-scoped session graph artifact inspection target HTTP / CLI；MCP graph tools 已存在 | graph advanced 最小 read-only surface 已完成，后续只做 Session GraphRAG contract 收敛 | closed / ongoing guard | V1.6-C |
| Session GraphRAG 跨入口 contract 不完整 | MCP session tools 已存在；D1 已完成 contract hardening；D2 已开放 session lifecycle create/list/get/close/delete target HTTP；D3 已完成 ingest/query/build contract planning；D4/D5/D6 已分别开放 session ingest、session query、session build minimal target HTTP | 建立跨入口 Session GraphRAG public contract，并保持 D2/D4/D5/D6 accepted surfaces 稳定 | closed / ongoing guard | V1.6-D |
| Quality target HTTP write 缺失 | E1 已开放 quality feedback target HTTP；E2 已开放 correction rules target HTTP；E3 已开放 correction review target HTTP；E4 已开放 correction plan target HTTP；E5 已开放 correction-rules artifact build target HTTP；correction apply target HTTP 仍未开放 | target HTTP quality write 复用 shared helper | P2 | V1.6-E |
| artifact_ref 规范化仍需加强 | V1.5 已 accepted，但新入口未全部覆盖 | 新 target routes 均验证 artifact_ref consistency | P2 | V1.6-B/E |
| operation lifecycle consistency 需要扩展 | V1.5 build operation envelope 已稳定 | 新 lifecycle/session/quality route 均使用一致 envelope | P2 | V1.6-B/D/E |
| Console 证据视图不完整 | 控制台已有治理能力 | 展示公开面基线、target HTTP 迁移、contract evidence | P3 | V1.6-F |

## 6.1 Accepted Overlay Route Count

current target HTTP route count = 35。

- A guard: +0
- B1/B2/B3 overlays: +11
- C1/C2/C3/C4 overlays: +4
- D1 planning: +0
- D2 overlay: +5
- D3 planning: +0
- D4/D5/D6 overlays: +5
- E1/E2/E3/E4/E5 overlays: +7

合计：V1.5 baseline 3 + A 0 + B 11 + C 4 + D1 0 + D2 5 + D3 0 + D4/D5/D6 5 + E1/E2/E3/E4/E5 7 = 35。

A / D1 / D3 不是 route overlay；它们分别是 guard、contract planning 或 hardening 阶段。

## 6.2 剩余开发计划总览

截至 V1.6 Closure Acceptance accepted，V1.6 剩余开发计划为 0。后续只能进入 V1.7 planning 或 post-V1.6 backlog triage，不应在 V1.6 内新增 backend public surface。

| 顺序 | 阶段 | 状态 | 核心目标 | 不允许做的事 |
| --- | --- | --- | --- | --- |
| 1 | V1.6-F1 Console Governance Evidence Baseline Sync | completed | 建立 console governance evidence matrix、route count 证据、drawio 同步和 no-public-surface focused guard | 不新增 backend public surface；不修改 frontend 或 `/knowledge` 行为 |
| 2 | V1.6-F2 Console Governance Polish | completed | 在 `/knowledge` 展示公开面、迁移状态、contract evidence 和验收证据 | 不把 `/knowledge` 做成终端用户知识消费 App；不新增 backend public surface |
| 3 | V1.6 Closure Acceptance / Final Release Audit | completed | 全量 public surface audit、回归、文档一致性审计和最终验收报告 | 不新增 backend public surface；不修改功能代码 |

完成这些剩余阶段后，再进入 V1.6 总体验收与收口阶段。总体验收应重新运行 public surface guard、API/MCP/combined regression、前端 build / 截图验收、drawio XML validation 和文档一致性审计。

## 7. 阶段开发计划摘要

### V1.6-A：Public Surface Guard

状态：completed。

目标：把 V1.5 closure audit 变成可重复护栏。本阶段只新增自动化 guard，不新增业务能力。

开发摘要：

- 增加机器可读 V1.5 public surface baseline。
- 增加 MCP registry count / tool list 扫描。
- 增加 CLI top-level / nested command 扫描。
- 增加 HTTP route inventory 扫描。
- 增加 target HTTP allowlist 扫描。
- 增加 `/api/v1/knowledge/*` compatibility retention 检查。
- 增加上层应用生产依赖 import scan。

边界：

- 不新增 MCP tool。
- 不新增 HTTP route。
- 不新增 CLI command。
- 只建立公开面保护机制。
- MCP graph/session tools already exist in the V1.5 baseline；V1.6-A does not add graph/session MCP tools。

### V1.6-B：Lifecycle Target HTTP

目标：为 workspace/source/build lifecycle 建立 target HTTP write surface。

当前状态：V1.6-B1 Workspace Target HTTP completed；V1.6-B2 Source Target HTTP completed；V1.6-B3 Build Target HTTP completed。V1.5 baseline 保持 3 个 target HTTP routes，B1 overlay 新增 4 个 workspace routes，B2 overlay 新增 4 个 source routes，B3 overlay 新增 3 个 build routes。

开发摘要：

- 已完成 workspace target HTTP create/list/describe/archive contract。
- 已完成 source target HTTP import/list/describe/remove contract。
- 已完成 build target HTTP start/status/cancel contract。
- 统一 `operation_id`、envelope、error code。
- 保留旧 `/api/v1/knowledge/*` 行为。

边界：

- 不暴露内部 workspace path/layout。
- 不一次性打开 graph/quality/session target HTTP。
- 不移除 compatibility HTTP。
- B3 不开放 graph/session/quality target HTTP；graph neighbors 由 V1.6-C1 独立开放。

### V1.6-C：Graph Advanced Minimal Surface

目标：不新增 V1.5 已存在的 MCP graph tools，只为尚未开放的 graph advanced target HTTP / CLI surface 建立最小公开面。

当前状态：V1.6-C1 Graph Neighbors Target HTTP / CLI Minimal Surface completed；V1.6-C2 Graph Community Target HTTP / CLI Minimal Surface completed；V1.6-C3 Graph Query Target HTTP / CLI Minimal Surface completed；V1.6-C4 Graph Session Target HTTP / CLI Minimal Surface completed。C1 overlay 新增 `GET /api/workspaces/{workspace_id}/graph/neighbors`，并允许 `knowledge graph neighbors` nested CLI command；C2 overlay 新增 `GET /api/workspaces/{workspace_id}/graph/community`，并允许 `knowledge graph community` nested CLI command；C3 overlay 新增 `GET /api/workspaces/{workspace_id}/graph/query`，并允许 `knowledge graph query` nested CLI command；C4 overlay 新增 `GET /api/workspaces/{workspace_id}/graph/session`，并允许 `knowledge graph session` nested CLI command；V1.5 baseline 保持不变。当前 accepted target HTTP surface 为 18 routes。

开发摘要：

- 已完成 graph neighbors 的 target HTTP / CLI contract。
- 已完成 graph community 的 target HTTP / CLI contract。
- 已完成 graph query 的 target HTTP / CLI contract。
- 已完成 graph session inspection 的 target HTTP / CLI contract。
- 每个子能力单独验收，不一次性扩全图能力。

边界：

- 不把 GraphRAG 内部 layout 暴露为 contract。
- 不把已有 MCP graph tools 当作 V1.6 新增。
- 不破坏 `knowledge graph snapshot`。
- C1 graph neighbors 为 read-only，不触发 build/index/session/quality，不创建 operation，不修改 source registry。
- C2 graph community 为 read-only，不触发 build/index/materialization/session/quality，不创建 operation，不修改 source registry，不写入 graph snapshot。
- C3 graph query 为 read-only，不触发 build/index/materialization/session/quality，不创建 operation，不修改 source registry，不写入 graph snapshot。
- C4 graph session inspection 为 read-only，不触发 build/index/materialization/quality，不创建 operation，不修改 source registry，不写入 graph snapshot，不更新 session lifecycle state。

#### V1.6-C4：Graph Session Target HTTP / CLI Minimal Surface

状态：completed。

目标：只补 graph-scoped session graph artifact inspection 的最小 target HTTP / CLI surface，延续 C1/C2/C3 的 read-only、stable projection 和 phase overlay 机制；它不是 session lifecycle target HTTP，也不是完整 Session GraphRAG public contract。

开发摘要：

- 已新增 C4 phase overlay，只允许 `GET /api/workspaces/{workspace_id}/graph/session`。
- 已新增 `knowledge graph session` 嵌套 CLI 命令。
- 复用现有 session graph / session service helper。
- 固定 `session_id`、`limit`、`include_nodes`、`include_edges` 等最小 contract。
- 默认 response 不暴露 session graph 内部 path/layout。

边界：

- 不新增 MCP tool。
- 不新增 CLI 顶层命令。
- 不开放完整 session target HTTP route group。
- 不触发 build/index/materialization/quality write。
- 不创建 operation，不修改 source registry，不写 graph snapshot，不更新 session lifecycle state。

### V1.6-D：Session GraphRAG Public Contract

当前状态：V1.6-D1 Session GraphRAG Public Contract Planning / Contract Hardening completed；V1.6-D2 Session Lifecycle Target HTTP Minimal Surface completed；V1.6-D3 Session Ingest / Query / Build Contract Planning completed；V1.6-D4 Session Ingest Target HTTP Minimal Surface completed；V1.6-D5 Session Query Target HTTP Minimal Surface completed；V1.6-D6 Session Build Target HTTP Minimal Surface completed。D6 后 target HTTP 当前为 28 routes，MCP tools 仍为 40，CLI top-level 与 nested inventory 不变。

目标：不新增 V1.5 已存在的 MCP session tools，收敛跨入口 Session GraphRAG public contract。

开发摘要：

- D1 已新增 `session-graphrag-contract-plan.md` surface matrix。
- D1 已固化 stable projection、normalized error envelope 与 artifact_ref non-path rules。
- D1 已新增 `test_session_graphrag_contract.py` 防漂移测试。
- D2 已开放 session create/list/get/close/delete target HTTP。
- D2 已固定 session lifecycle stable projection、metadata sanitize、`session://...` artifact_ref 和 cross-workspace isolation。
- D2 明确不开放 session ingest/query/build target HTTP。
- D3 已完成 session ingest/query/build contract matrix 与 future phase split，明确 D4 ingest、D5 query、D6 build 必须拆开执行。
- D4 已开放 session ingest target HTTP，使用 session-scoped source projection、`session-source://...` artifact_ref 和 metadata sanitize。
- D4 明确不开放 session query/build target HTTP，不触发 build/index/materialization/query/quality write。
- D5 已开放 session query target HTTP，使用 session-scoped read-only projection、non-path artifact_ref 和 raw GraphRAG payload 过滤。
- D5 明确不开放 session build target HTTP，不触发 build/index/materialization/quality write。
- D6 已开放 session build start/status/cancel target HTTP，使用真实 session operation lifecycle id、non-path artifact_ref 和 operation path projection。
- D6 明确不开放 quality target HTTP，不触发 workspace-level build 或 quality write。
- 明确 `session_id`、`operation_id`、`artifact_ref` 的稳定语义。

边界：

- 不引入 meeting、ASR、interview、learning、IDE plugin 等上层应用生产依赖。
- 不暴露 session 内部存储路径为稳定 contract。
- 不把 session 能力扩展成上层 workflow。
- D2 只开放 `/api/workspaces/{workspace_id}/sessions*` 中 create/list/get/close/delete 最小 lifecycle route，不新增 session ingest/query/build target HTTP，不新增 quality target HTTP，不把 C4 `/graph/session` 解释成 session lifecycle。
- D3 不新增任何公开面，不新增 session ingest/query/build target HTTP，不新增 quality target HTTP。
- D4 只新增 `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest`，不新增 session query/build target HTTP，不新增 quality target HTTP。
- D5 只新增 `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`，不新增 session build target HTTP，不新增 quality target HTTP。
- D6 只新增 session build start/status/cancel 3 个 target HTTP routes，不新增 quality target HTTP。

### V1.6-E：Quality Target HTTP Write Routes

当前状态：V1.6-E5 Quality Correction Rules Build Target HTTP Minimal Surface completed；current target HTTP route count = 35。Correction apply target HTTP 仍 planned / not implemented。

目标：将 quality write 能力迁移到 target HTTP，而不是继续扩大旧 compatibility HTTP。

开发摘要：

- E1 已完成 quality feedback target route contract。
- E2 已完成 quality correction rules target route contract。
- E3 已完成 quality correction review target route contract。
- E4 已完成 quality correction plan target route contract。
- E5 已完成 correction-rules artifact build target route contract。
- 复用 `quality_contract.py` shared helper。

边界：

- 保持 non-destructive governance。
- 不直接改写 source、wiki 或 graph artifacts。
- 不移除旧 quality compatibility HTTP。

### V1.6-F：Console Governance Evidence / Polish

当前状态：V1.6-F1 Console Governance Evidence Baseline Sync completed；V1.6-F2 Console Governance Polish completed；V1.6 Closure Acceptance completed。

目标：先用 F1 建立 console governance evidence baseline，再由 F2 让 `/knowledge` 更清楚地展示服务治理状态和 V1.6 contract evidence。

开发摘要：

- F1 已新增 `console-governance-evidence-plan.md`，覆盖 V1.5 baseline、A guard、B/C/D/E accepted surfaces 与 F2 planned。
- F1 已新增 focused documentation guard，验证 route count = 35、MCP tool count = 40、CLI diff = none、no frontend behavior change。
- F1 未新增 backend public surface，未修改 frontend 或 `/knowledge` 行为。
- F2 已在 `/knowledge` 增加 public surface baseline 展示、target HTTP migration state 展示、graph/session/quality contract evidence 展示与阶段验收证据入口。
- F2 未新增 backend public surface，不新增 MCP/CLI，不新增 route，不把 `/knowledge` 改成 end-user knowledge consumption app。

边界：

- `/knowledge` 仍是 service governance console。
- 不做成终端用户知识消费 App。
- F1 不新增业务能力，只同步治理证据和 guard。
- Closure Acceptance 已完成最终公开面冻结审计；后续 V1.7 capabilities remain planned only。

## 8. 阶段验收计划摘要

| 阶段 | 必须通过的验收 |
| --- | --- |
| V1.6-A | completed：MCP tool count / tool list 扫描；CLI 顶层与嵌套命令扫描；HTTP route inventory；target HTTP allowlist；compatibility route retention；upper-layer dependency guard |
| V1.6-B | B1 completed：workspace target HTTP focused tests；B2 completed：source target HTTP focused tests；B3 completed：build target HTTP focused tests；public surface overlay guard；API/MCP/combined regression；no internal path contract |
| V1.6-C | C1 completed：graph neighbors target HTTP / CLI focused tests；C2 completed：graph community target HTTP / CLI focused tests；C3 completed：graph query target HTTP / CLI focused tests；C4 completed：graph session target HTTP / CLI focused tests；CLI parser scan；HTTP route scan；GraphRAG boundary check；snapshot compatibility |
| V1.6-D | D1 completed：session contract tests；D2 completed：session lifecycle focused tests；D3 completed：planning guard；D4 completed：session ingest focused tests；D5 completed：session query focused tests；D6 completed：session build focused tests；MCP regression；target/session route scan；upper-layer dependency audit；artifact_ref / debug path audit；no quality target HTTP |
| V1.6-E | E1 completed：quality feedback focused tests；E2 completed：quality correction rules focused tests；E3 completed：quality correction review focused tests；E4 completed：quality correction plan focused tests；E5 completed：quality correction rules build focused tests；API regression；shared helper reuse tests；non-destructive governance verification；compatibility HTTP retention |
| V1.6-F | F1 completed：console governance evidence matrix；target HTTP route count = 35；MCP tool count = 40；CLI diff = none；no new backend route；drawio sync。F2 completed：frontend `npm run build`；public surface evidence 展示；`/knowledge` remains service governance console；no backend public surface |

通用验收：

- 每个阶段完成后必须记录 baseline / current / diff 公开面。
- 未在阶段计划中声明的 MCP tool、HTTP route、CLI command 都是 blocking issue。
- 所有新入口必须使用稳定 ID，不得把内部 path/layout 作为稳定 contract。
- 每个阶段必须同步更新 `development-plan.md`、`acceptance-plan.md`、`current-vs-target-gap.md`、`current-vs-target-gap.drawio` 和相关 contract 文档。
- planned 能力不得写成 implemented。

## 9. V1.6 非目标

- 不把 `/knowledge` 变成 end-user knowledge consumption app。
- 不引入上层应用生产依赖。
- 不暴露内部 workspace path/layout 为稳定 contract。
- 不一次性开放所有 V1.6 候选能力。
- 不移除旧 `/api/v1/knowledge/*` 兼容入口。
- 不把已有 MCP graph/session tools 重新包装成 V1.6 新增 MCP tools。

## 10. 当前结论

V1.6-B1 Workspace Target HTTP、V1.6-B2 Source Target HTTP、V1.6-B3 Build Target HTTP、V1.6-C1 Graph Neighbors、V1.6-C2 Graph Community、V1.6-C3 Graph Query、V1.6-C4 Graph Session Target HTTP / CLI Minimal Surface、V1.6-D1 Session GraphRAG Contract Hardening、V1.6-D2 Session Lifecycle Target HTTP Minimal Surface、V1.6-D3 Session Ingest / Query / Build Contract Planning、V1.6-D4 Session Ingest Target HTTP Minimal Surface、V1.6-D5 Session Query Target HTTP Minimal Surface、V1.6-D6 Session Build Target HTTP Minimal Surface、V1.6-E1 Quality Feedback Target HTTP Minimal Surface、V1.6-E2 Quality Correction Rules Target HTTP Minimal Surface、V1.6-E3 Quality Correction Review Target HTTP Minimal Surface、V1.6-E4 Quality Correction Plan Target HTTP Minimal Surface、V1.6-E5 Quality Correction Rules Build Target HTTP Minimal Surface、V1.6-F1 Console Governance Evidence Baseline Sync、V1.6-F2 Console Governance Polish 与 V1.6 Closure Acceptance 已完成。下一阶段应进入 V1.7 planning 或 post-V1.6 backlog triage，不建议新增 backend public surface。

当前 V1.6 剩余开发计划为 0。V1.6 Closure Acceptance 已完成最终验收并同步 gap 文档、drawio、development plan、acceptance plan 和最终报告。
