# V2.39-V2.45 目标架构：大项目语义索引与 Agent 阅读优化平台

## 1. 总体架构目标

V2.39-V2.45 的目标架构是在既有 Project Intelligence artifacts 之上增加一组可插拔、可预算、可回归的增强层：

```text
Large Repo Inputs
  -> Budgeted Scale Scanner
  -> Multi-language Fact Providers
  -> Workflow / Runtime Candidate Extractors
  -> Document Semantic Parser
  -> Relationship Chain Builder
  -> Profile / Taxonomy Manager
  -> Token Budget Optimizer
  -> Human Report + Agent Context Pack
```

所有结论仍遵守 evidence-first 原则：

- document claim 不等于 code fact。
- candidate 不等于 accepted runtime topology。
- heuristic dependency 不等于 runtime call。
- provider unavailable 不等于 accepted。
- profile 配置不等于项目特化硬编码。

## 2. 核心组件

### 2.1 Budgeted Scale Scanner

职责：

- 对大型项目建立 scale profile。
- 在扫描前估算文件数、LOC、语言分布、generated/vendor/binary 目录。
- 按 budget 执行扫描，超限时输出 partial status 和 blocker。
- 支持 artifact shard 和 paginated readback。

主要产物：

```text
architecture/scale/
  scale_profile.json
  scan_budget_report.json
  scan_shards/
    files_0001.jsonl
    symbols_0001.jsonl
  paginated_readback_index.json
```

### 2.2 Multi-language AST/LSP Provider Layer

职责：

- 定义统一 provider contract。
- Python AST 为 mandatory baseline。
- TS/JS 可先支持基础 symbol/import。
- tree-sitter/LSP 为 optional provider，未配置时 structured unavailable。

Provider 状态：

```text
accepted
configured
provider_unavailable
unsupported_language
provider_failed
timeout
```

### 2.3 Workflow / Runtime Candidate Extractor

职责：

- 从 manifest、config、registry、decorator、class、CLI parser、TUI/console entry 中抽取候选事实。
- 输出 `workflow_candidate`、`runtime_adapter_candidate`、`agent_registry_candidate`、`entrypoint_candidate`。
- 保留 evidence 和 confidence。

边界：

- 不输出生产 runtime topology。
- 不声称完整执行链路。
- candidate 必须在报告中明确标记。

### 2.4 Relationship Chain Builder v3

职责：

- 构建可供 Agent 使用的轻量链路：

```text
capability -> entrypoint -> handler -> dependency/reference -> test/config/doc claim
```

Edge 分类：

```text
deterministic_handler_mapping
symbol_reference
import_dependency
config_reference
test_reference
doc_constraint_reference
heuristic_candidate
```

禁止 accepted 类型：

```text
runtime_call
data_flow
control_flow
production_topology
type_inferred_dependency
```

### 2.5 Document Semantic Parser

职责：

- Markdown：heading、bullet、table row、acceptance criteria、non-goal、stop condition。
- drawio：page、lane、group、container、edge、legend、milestone、gate。
- 将图形语义转为 document claims 和 relations。

边界：

- drawio claim 不能直接成为 code fact。
- 图表目标节点若无代码证据，只能是 target/document claim。

### 2.6 Token Budget Optimizer + Context Cache

职责：

- 为 Agent 生成任务级阅读预算。
- 记录 cache hit、artifact reuse、omitted_items。
- 按 role 输出 context pack。
- 裁剪时保证 recommendation 与 evidence 一致。

### 2.7 Project Profile / Taxonomy Manager

职责：

- 管理项目族术语、入口模式、workflow patterns、doc authority rules。
- 允许 HarnessOS 通过 profile 配置表达特殊结构。
- 通用 extractor 不能包含 HarnessOS-only path 或 token。

## 3. 数据流

```text
Repo Root
  -> Scale Profile
  -> Budgeted Scan
  -> Language Providers
  -> Code Facts

Docs Root
  -> Document Semantic Parser
  -> Architecture Claims

Profile / Taxonomy
  -> Extractor Pattern Catalog
  -> Candidate Normalization

Code Facts + Claims + Profile
  -> Relationship Chains
  -> Verification / Drift
  -> Reports / Context Packs
```

## 4. Public Contract

目标接口族：

```text
GET  /architecture/scale/profile
POST /architecture/providers/build
GET  /architecture/providers/status
POST /architecture/workflows/extract
GET  /architecture/relationships/chains
POST /architecture/doc-semantics/build
POST /architecture/context/optimize
GET  /architecture/profile
POST /architecture/profile
GET  /architecture/regression/status
```

MCP/CLI 必须提供等价 read/build 能力，并在 stable ids、counts、warnings、unresolved、error codes 上与 HTTP 对齐。

## 5. 架构门禁

- 新逻辑必须放入 focused architecture modules，不扩大 legacy 大文件。
- V2.0-V2.38 artifacts 作为只读输入，除非对应阶段显式 rebuild。
- 所有 public payload 默认 repo-relative path。
- 任何 accepted 结论必须可追踪 artifact id。
- no-hardcode audit 必须检查 HarnessOS/codexPat/data_service 专用路径是否进入通用 extractor。

## 6. 阶段模块落点

Phase 119-122 的实现已按以下 focused module 边界落地；后续维护应继续保持接口薄封装、核心逻辑模块化：

```text
backend/data_service/code_assets/architecture/
  relationship_chains_v3.py       # Phase 119
  document_semantics_v3.py        # Phase 120
  token_context_cache.py          # Phase 121
  profile_taxonomy_regression.py  # Phase 122
```

接口层保持薄封装：

```text
backend/app/api/v1/code_assets_architecture.py
backend/data_service/mcp_code_architecture_tools.py
backend/data_service/cli_code_architecture.py
```

新增接口必须遵守统一 envelope、repo-relative path、artifact_refs、warnings、unresolved、structured error code 和三端 parity。

## 7. 用户体验目标

本阶段结束后，用户应能完成以下路径：

1. 对大型项目生成 scale profile 和 provider/candidate facts。
2. 读取 capability 到入口、handler、dependency、test/config/doc claim 的轻量链路。
3. 从 drawio/Markdown 中看到目标架构声明，并能区分文档声明与代码事实。
4. 请求低 token 预算的 Agent Context Pack，并看到保留项、裁剪项、证据和 cache 命中情况。
5. 通过 profile/taxonomy 管理 HarnessOS 等项目族术语，而不污染通用 extractor。
