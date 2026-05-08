# Meeting Voice Assistant Plan

## 当前目标

本仓库专注会议语音助手：音频采集、ASR 转写、说话人处理、会议分析、会议控制台和基础会话管理。

知识治理已抽离为独立 Local Knowledge Governance Service，位于 `~/Desktop/workspace/data_service`。会议应用只通过 MCP / CLI / HTTP contract 接入，不直接读写其 workspace 文件结构。

## 当前边界

本项目包含：

- 实时语音识别 WebSocket
- 文件上传识别
- 说话人与会议章节处理
- LLM 会议摘要、决策、行动项分析
- 会议控制台
- `/knowledge` 服务治理控制台入口和后端代理

本项目不包含：

- GraphRAG 执行服务
- LLMWiki 编译链路
- Source Trace 存储
- Quality Governance
- MCP Server
- 独立知识库 workspace 存储

这些能力由 `data_service` 独立提供。

## 开发原则

1. 不恢复已迁出的内嵌知识服务代码。
2. 不新增旧知识消费终端用户页面。
3. 会议应用只处理音频和转写后的会议分析结果。
4. 需要知识固化时，把转写文本或结构化会议分析产物作为 source 交给外部知识服务。
5. `/knowledge` 是 Knowledge Service Console，不是会议应用内置知识库产品。

## 验收重点

- 前端构建通过。
- 后端核心 import 通过。
- 旧内嵌图谱服务端口和模块路径不再出现在运行时代码中。
- README 和开发文档明确 data_service 是独立服务。
