# Data Service 双引擎架构设计

## 目标

在 `backend/app/llmwiki` 和 `backend/app/graphrag` 之上增加一个位于 `backend/data_service` 的上层模块，作为统一的数据编排层。

目标不是让 `llmwiki` 和 `graphrag` 相互吞并，而是明确三者分工：

- `data_service`：负责单次 ingest、共享抽取/规范化、distill 策略、产物布局、运行摘要
- `llmwiki`：负责知识编译、可读页面、轻量检索、证据追溯、本地阅读接口
- `graphrag`：负责实体/关系抽取、图谱索引、跨文档关系发现、图推理上下文

## 设计原则

### 1. 用户单次写入

用户只需要输入一次数据。

内部流程不应是：

```text
raw -> llmwiki -> graphrag
```

而应是：

```text
raw -> extract -> normalize -> distill -> { llmwiki, graphrag }
```

### 2. GraphRAG 不直接默认消费 raw fulltext

原始文件通常包含大量：

- 模板话
- 元数据噪音
- 重复段落
- 寒暄和无效上下文
- 过细但低复用价值的细节

如果 GraphRAG 直接吃原始全文，会产生：

- token 浪费
- 低价值节点膨胀
- 关系图噪音过大
- query 时召回很多无意义上下文

因此 GraphRAG 默认应优先消费 `distill` 层的高信息单元，而不是 raw fulltext。

### 3. LLMWiki 不只是零散文件收集器

`llmwiki` 的核心价值是：

- 把资料编译成可读页面
- 统一零散文档、聊天记录、轻文档的阅读面
- 保留 provenance
- 提供本地可检索、可维护的知识视图

### 4. GraphRAG 不是 LLMWiki 的下游皮肤

`graphrag` 的核心价值是：

- 实体和关系抽取
- 图谱社区和主题发现
- 多跳检索
- 跨材料关系推理

GraphRAG 可以参考 LLMWiki 的 distilled summary，但不应只依赖 LLMWiki 页面作为唯一输入。

## 模块分层

### row

职责：

- 保存原始输入源
- 记录原始路径、sha256、快照位置
- 只做版本管理，不被整理产物回写污染

典型产物：

- `row_manifest.json`
- raw snapshot

### normalize

职责：

- 将不同格式文件统一抽取为标准 sections / passages / message units
- 提供后续 distill 的统一输入

典型产物：

- normalized JSON

### distill

职责：

- 对 normalized material 做高信息密度提炼
- 去噪、去重、筛选
- 输出适合 llmwiki 和 graphrag 复用的高价值单元

典型 unit 类型：

- `fact_candidate`
- `question`
- `conclusion`
- `step`
- `example`
- `note`
- `risk`
- `entity_candidate`
- `relation_candidate`
- `topic_candidate`

### llmwiki

职责：

- 生成 source/topic/conversation 页面
- 提供可读摘要
- 提供本地全文检索
- 输出 provenance 明确的页面结果

### graphrag

职责：

- 从 distilled units 构建图谱输入
- 提取实体、关系、主题社区
- 提供图检索和多跳推理上下文

### summary

职责：

- 面向用户和 agent 输出运行状态与知识状态
- 不承担原始数据存储，也不替代 wiki 页面

## 推荐目录布局

```text
backend/
├─ data_service/
│  ├─ __init__.py
│  ├─ __main__.py
│  ├─ adapters.py
│  ├─ mcp_stdio.py
│  ├─ models.py
│  └─ service.py
└─ app/
   ├─ llmwiki/
   └─ graphrag/
```

workspace 推荐布局：

```text
workspace/
├─ row_manifest.json
├─ summary/
│  ├─ summary.md
│  └─ summary.json
├─ distill/
├─ llmwiki/
│  ├─ raw/
│  ├─ readable/
│  ├─ normalized/
│  ├─ pages/
│  └─ state/
└─ graphrag/
   ├─ input/
   ├─ cache/
   └─ state/
```

## data_service 职责边界

`data_service` 应拥有：

- 单次 ingest 计划
- artifact layout
- distill policy
- summary 输出
- 上层对 `llmwiki` 和 `graphrag` 的统一调度入口

`data_service` 不应拥有：

- LLMWiki 页面编译细节
- GraphRAG 图谱内部算法
- 两个引擎的专属存储细节

## authority 规则

### PRIMARY_DOC

- 允许进入 verified facts
- 可建立高置信图关系

### SECONDARY_CHAT

- 只进入：
  - `unverified_notes`
  - `examples`
  - `candidate_relations`
  - `hypotheses`
- 不应直接进入 verified facts

### DERIVED

- 只作为辅助摘要或路由上下文
- 不作为原始事实来源

## MCP 设计建议

未来通过 MCP 并行暴露时，建议保留三个概念层：

- `data_service`
- `llmwiki`
- `graphrag`

建议接口：

### data_service

- `knowledge.ingest`
- `knowledge.summary`
- `knowledge.plan`
- `knowledge.query`

## 当前实现状态

当前 `backend/data_service` 已具备：

- `python -m data_service ingest --workspace ... <paths...>`
- `python -m data_service query --workspace ... --mode llmwiki|graphrag|hybrid "query"`
- `python -m data_service summary --workspace ...`

查询模式说明：

- `llmwiki`：走本地 wiki 页面与段落检索
- `graphrag`：走 `workspace/graphrag/state/graphrag.db` 的实体/关系/单元查询
- `hybrid`：合并两者结果，返回统一响应结构

`graphrag/state/graphrag.db` 当前包含真实可查询的图索引表，而不是仅保存 staging manifest：

- `documents`
- `distilled_units`
- `entities`
- `document_entities`
- `relationships`
- `entity_fts`
- `unit_fts`

### llmwiki

- `llmwiki.search`
- `llmwiki.read_page`
- `llmwiki.list_pages`

### graphrag

- `graphrag.query`
- `graphrag.entity_context`
- `graphrag.topic_graph`

## 当前实现建议

第一阶段不要求立刻重写 `llmwiki` 和 `graphrag` 内部实现。

优先做：

1. 建立 `data_service` 模块
2. 统一 workspace artifact layout
3. 明确 distill contract
4. 输出 `summary/summary.md` / `summary/summary.json`
5. 保持 `llmwiki` 和 `graphrag` 仅处理各自专长能力

## 一句话总结

- `data_service` 负责“只写一次，统一编排”
- `llmwiki` 负责“把知识编译得能读、能查、能追溯”
- `graphrag` 负责“把知识连接起来，支持关系发现和深推理”
