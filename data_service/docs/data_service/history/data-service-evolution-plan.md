# Data Service / LLMWiki / GraphRAG 整体开发计划

## 1. 背景

当前仓库已经从单一的会议语音助手，演进出一条面向本地知识资产的数据通路：

- `backend/data_service`：统一编排层
- `backend/app/llmwiki`：知识编译与可读页面层
- `backend/app/graphrag`：图谱与关系推理能力层
- `frontend/src/pages/KnowledgePage.vue`：双引擎工作台

但当前状态仍然是“可用版”，还没有完全达到“稳定的数据服务底座 + 清晰的双引擎分工 + 高质量知识产物”的目标状态。

本计划用于明确：

- 当前已经完成了什么
- 当前与目标架构的主要差异
- 后续建议的实施阶段
- 每一阶段的影响范围

## 2. 总体目标

项目的知识侧目标不是把 `llmwiki` 和 `graphrag` 合并成一个黑箱，而是形成稳定的双引擎架构：

```text
raw sources
  -> extract
  -> normalize
  -> distill
     -> llmwiki compile
     -> graphrag index/query
  -> summary / page / graph / query API
```

职责定位：

- `data_service`：上游编排、目录布局、distill 策略、统一 ingest/query/summary 接口
- `llmwiki`：可读页面、知识编译、来源追溯、本地检索
- `graphrag`：实体/主题/关系图谱、社区发现、图检索和推理上下文

## 3. 当前实现状态

### 已完成

- `data_service` 独立于 `app/` 外，位于 `backend/data_service`
- 用户支持单次 ingest，内部同时驱动 `llmwiki` 和 `graphrag`
- `workspace` 已形成三层产物：
  - `summary/`
  - `llmwiki/`
  - `graphrag/`
- `/api/v1/knowledge/*` 已接通：
  - `ingest`
  - `summary`
  - `query`
  - `graph`
  - `page`
  - `reset`
- `/knowledge` 页面已接到 `data_service`
- `llmwiki` 已支持：
  - source/topic/conversation 页面
  - 本地检索
  - MiniMax 驱动的编译
- `graphrag` 轻量实现已支持：
  - entity/theme 双层节点
  - weighted graph
  - community 提取
  - graphrag 查询
- 目录 ingest 已支持递归展开
- workspace reset 已支持，且只清中间产物，不触碰 `row`

### 已知问题

- `distill` 层还偏启发式，未完全稳定
- `GraphRAG` 的实体与主题清洗仍有中文碎片噪音
- `GraphRAG` 社区仍是轻量自建索引，不是完整图推理引擎
- `LLMWiki` 的页面标题、topic 归并和摘要质量还有提升空间
- 目前并存两套 GraphRAG 相关能力：
  - `backend/data_service` 里的轻量图索引链
  - `backend/app/graphrag` 原有服务链
  边界虽然已经收紧，但还没有完全统一为同一个“上层入口 + 下游专用引擎”的形态

## 4. 当前架构与目标架构的核心差异

### 当前架构

- `data_service` 已经存在，但更偏“编排 + 轻量算法承载”
- `graphrag` 当前主要消费 `distill` 后的高信息单元，但图构建逻辑仍部分内嵌在 `data_service`
- `llmwiki` 和 `graphrag` 的“共享 normalize / distill 契约”已经形成，但还未彻底沉淀为稳定的通用中间层
- 前端 `/knowledge` 已经可用，但仍更像“工作台”，而不是成熟的数据产品界面

### 目标架构

- `data_service` 成为稳定的上游数据底座
- `distill` 成为清晰、稳定、可版本化的中间契约层
- `llmwiki` 只关心编译与可读知识页
- `graphrag` 只关心图索引、社区、关系、查询
- `data_service` 不再长期承载过多 Graph 算法细节，而是负责：
  - ingest 编排
  - workspace 管理
  - distill 分发
  - summary / API / MCP 接口
- `/knowledge` 页面升级为统一知识运营台，而不是测试面板

## 5. 建议分阶段实施

### Phase 1：稳定当前双引擎工作流

目标：

- 把当前“可用版”变成“稳定版”

范围：

- 固化 `distill` 数据结构
- 收紧实体、主题、标题噪音清理
- 提升 `LLMWiki` 页面可读性
- 提升 `/knowledge` 页面错误态、空态、状态反馈
- 强化 `summary.json` 的观测字段

完成标志：

- `row/deepseek_split` 全量 ingest 稳定
- `summary / llmwiki / graphrag` 产物稳定可读
- 头部社区和头部 topic 与真实知识结构基本一致

### Phase 2：把 distill 沉淀为正式中间层

目标：

- 让 `distill` 从“内部实现细节”变成正式的中间契约

范围：

- 为 `distill` 设计版本字段
- 区分 source-level summary 与 unit-level distilled units
- 为 `llmwiki` 和 `graphrag` 明确输入边界
- 增加 `distill` 的调试、预览和导出能力

完成标志：

- `distill/` 目录与 schema 稳定
- `llmwiki` 与 `graphrag` 均通过统一契约消费数据
- API 可暴露 `distill` 相关状态

### Phase 3：收口 GraphRAG 的职责边界

目标：

- 让 `data_service` 不再持续背负越来越多图算法逻辑

范围：

- 梳理 `backend/data_service` 与 `backend/app/graphrag` 的关系
- 决定是否把轻量图构建迁回 `app/graphrag`
- 或将 `app/graphrag` 改造成明确的下游引擎适配层
- 统一 Graph 查询模型与社区模型

完成标志：

- 图算法职责主要位于 `graphrag`
- `data_service` 主要负责编排和 API
- 查询结果结构统一

### Phase 4：MCP 与 Agent 化接入

目标：

- 让本地 Agent 和外部工具稳定调用知识底座

范围：

- `data_service` MCP tools 精细化
- `llmwiki` 与 `graphrag` 工具边界明确
- Agent 路由策略固化：
  - 阅读/编译类 -> `llmwiki`
  - 图谱/关系类 -> `graphrag`
  - 混合问题 -> `data_service`

完成标志：

- MCP 可稳定暴露 summary/query/page/graph/ingest
- Agent 可根据问题类型进行双引擎路由

### Phase 5：知识产品化

目标：

- 把 `/knowledge` 从工程工作台推进到知识产品界面

范围：

- 更强的 graph 可视化
- summary 与 page 的多层级预览
- 批量 ingest 任务管理
- 数据质量面板
- 社区与 topic 的人工校正入口

完成标志：

- 前端具备稳定运营、验证、巡检能力
- 不再只是调试界面

## 6. 风险点

### 风险 1：`data_service` 继续膨胀

如果不控制边界，`data_service` 很容易同时承载：

- 编排
- distill
- graph 算法
- API
- MCP
- summary

这会让它再次变成一个过度耦合层。

控制策略：

- 保持 `data_service` 优先负责“上游组织”
- 下游算法逐步回归 `llmwiki` / `graphrag`

### 风险 2：图谱质量不稳定

如果中文短语切分、主题抽取、权重策略不稳定，社区图会继续出现：

- 标题噪音
- 伪实体
- 大主题不突出

控制策略：

- 先稳定 `distill`
- 再稳定图算法
- 最后再追求更复杂的 graph UI

### 风险 3：两套 GraphRAG 并存时间过长

如果 `backend/app/graphrag` 与 `backend/data_service` 的图能力长期平行发展，会造成：

- 接口重复
- 数据模型分裂
- 前端和 API 认知混乱

控制策略：

- 在 Phase 3 明确收口

## 7. 近期优先级建议

当前最值得优先做的是：

1. 固化 `distill` schema 和 graph node schema
2. 继续清理 Graphrag 的中文噪音实体和伪主题
3. 提升 `LLMWiki` 的 topic 合并和页面标题质量
4. 统一 `data_service` 与 `app/graphrag` 的职责边界
5. 强化 `/knowledge` 的可视化与数据质量反馈

## 8. 对应图示

- [Data Service 当前架构状态](../CURRENT-STATUS.md)
- [Data Service V1.5 当前与目标差距分析](../../V1.5/current-vs-target-gap.md)
- [当前架构图](../diagrams/01_current_architecture.drawio)
- [目标架构图](../diagrams/02_target_architecture.drawio)
