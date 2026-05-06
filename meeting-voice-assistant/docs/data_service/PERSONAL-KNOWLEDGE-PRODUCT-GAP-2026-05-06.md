# 个人知识库管理产品 Gap 文档

日期：2026-05-06

## 目标产品描述

目标不是继续做一个偏工程巡检的 Data Service 控制台，而是做一个顺手的个人知识库管理产品。

用户期望的主流程：

1. 在网页上创建或选择一个个人知识库工作区
2. 指定一个本地工作路径，或者把文件导入系统管理区
3. 页面展示知识库状态，例如收录文件数、待处理文件、最近刷新时间和失败状态
4. 用户执行首次刷新或增量刷新
5. 后端通过 distill、LLMWiki 和 GraphRAG 生成知识产物
6. 前端展示 LLMWiki 摘要和页面
7. 前端展示 GraphRAG 社区实体图
8. 用户可以按 source 查看知识蒸馏过程

产品约束：

- 支持“目录即知识库”和“导入式知识库”两种模式
- 绑定目录只读，不修改用户原文件
- 导入式 source area 可由系统复制和管理
- 刷新优先手动确认，目录监听只进入待刷新队列，不默认自动重建
- 蒸馏过程首版按 source 展示，不做逐 token 或逐 prompt 调试界面

## 当前已具备能力

- `/knowledge` 已能展示 summary、query、LLMWiki 页面、GraphRAG 图和质量反馈
- HTTP API 已有 `/summary / graph / query / page / distill / ingest / reset`
- Data Service CLI 已有 ingest/query/summary/distill 等能力
- MCP lifecycle 已有 workspace、source、build、archive tools
- MCP build queue 已支持 operation status polling、cancel、blocked 和 server_interrupted
- `distill v1.1` 已有 source profile、low_signal、unit kind counts 和 profile_debug
- LLMWiki 已能生成 source/topic/conversation 页面
- GraphRAG snapshot/query 默认由 `app.graphrag.service` bridge 提供
- GraphRAG diagnostics 第一版已完成，能展示 top communities、weak communities、isolated nodes 和 low value nodes

## 真实产品 Gap

### Gap 1：工作区入口不够顺手

当前状态：

- 前端通过文本框输入 workspace 路径
- 后端 HTTP 接口接受 workspace path
- MCP 已支持 workspace create/list/describe/archive

目标状态：

- 用户从网页创建或选择知识库
- 页面展示最近工作区
- 页面展示工作区路径、绑定目录、source 数、最近刷新和健康状态
- 用户不需要理解内部 workspace 目录布局

缺口：

- HTTP API 没有完整对齐 MCP workspace lifecycle
- 前端没有工作区向导、最近工作区、工作区健康卡
- 空 workspace 的下一步引导不够清晰

### Gap 2：文件收录状态不可管理

当前状态：

- ingest 支持目录递归
- MCP source lifecycle 支持 import/list/remove
- summary 展示部分统计

目标状态：

- 前端展示 source 文件台账
- 每个 source 展示 `pending / indexed / failed / disabled / low_signal`
- 展示原始路径、导入方式、sha256、重复状态、文件大小、最后修改时间和最近构建结果
- 支持停用、重新收录和查看失败原因

缺口：

- `/knowledge` 没有完整 source list
- HTTP API 没有完整对齐 MCP source lifecycle
- 用户无法判断某个文件是否已收录、失败、跳过或低信号

### Gap 3：刷新流程仍偏同步工程操作

当前状态：

- 前端有“运行 ingest”和“刷新工作台”
- MCP build queue 已经具备异步能力

目标状态：

- 首次刷新、增量刷新、LLMWiki-only、GraphRAG-only 都是前端可见任务
- 任务显示 operation id、状态、阶段、进度、错误、retryable 和产物
- 支持取消、重试、轮询状态

缺口：

- 浏览器侧未接入 build queue
- HTTP API 缺少 build start/status/cancel 等价接口
- 同步 ingest 不适合长任务和首次刷新体验

### Gap 4：蒸馏过程没有产品化流水线

当前状态：

- distill 预览可以看到 source、units、profile_debug 和 low_signal
- LLMWiki 页面和 GraphRAG 图谱可以分别查看

目标状态：

- 用户点击 source 后看到：
  `原始文件 -> 标题/正文抽取 -> distill units -> LLMWiki 页面 -> GraphRAG entity/theme/community`
- 每个阶段显示状态、产物数量、诊断和跳转入口
- LLMWiki 页面和 GraphRAG 节点可以反向定位 source

缺口：

- distill 视图偏调试字段，不是用户理解的过程图
- source 到 page/node/community 的关联没有产品化展示
- 用户难以判断一个 source 是如何变成摘要、页面和图谱的

### Gap 5：目录监听和待刷新队列缺失

当前状态：

- 用户需要手动刷新
- Data Service 产品链路没有可见 watcher 状态

目标状态：

- 用户绑定目录后可以开启监听
- 前端展示新增、修改、删除、无法读取等变化
- 默认不自动重建，只提示用户确认刷新

缺口：

- 缺 watcher 状态 API
- 缺变更队列数据结构
- 前端没有“有 N 个变更待刷新”的提示

### Gap 6：空状态和错误状态不够产品化

当前状态：

- API key 缺失、workspace 空、构建失败时会出现空数据或错误提示
- 页面能力块很多，但首次使用路径不够明确

目标状态：

- 空状态明确引导创建/选择工作区、绑定目录或导入文件、执行首次刷新
- 错误状态明确区分 API key、路径权限、allowlist、构建失败、GraphRAG native CLI 失败等情况
- 每个错误给出下一步动作

缺口：

- 初次用户需要知道较多内部概念
- 错误恢复入口不集中

## 开发阶段映射

| 阶段 | 目标 | 主要交付 |
| --- | --- | --- |
| Phase 5.2 | Workspace & Source Manager | 工作区向导、目录绑定、导入式 source、source 台账 |
| Phase 5.3 | Refresh Operation UI | 首次刷新、增量刷新、operation 状态、取消、重试 |
| Phase 5.4 | Source Distill Trace | source 级蒸馏流水线、page/node/community 追溯 |
| Phase 5.5 | Directory Watcher | 目录监听、待刷新队列、手动确认刷新 |
| Phase 5.6 | Quality Regression | 低信号 source 抽查、topic/page 可读性、GraphRAG owner 边界下沉 |

## 验收口径

一个用户在不理解内部目录结构的前提下，应该能完成：

1. 创建或选择知识库
2. 绑定本地目录或导入文件
3. 看到文件收录状态
4. 点击首次刷新
5. 看到刷新进度和失败原因
6. 刷新完成后看到 LLMWiki 摘要和 GraphRAG 图谱
7. 点击某个 source 查看蒸馏过程
8. 从摘要、页面或图谱反向追溯到 source
9. 后续目录变化进入待刷新队列

达到以上能力后，项目才从“可用的双引擎工作台”进入“顺手的个人知识库管理产品”。
