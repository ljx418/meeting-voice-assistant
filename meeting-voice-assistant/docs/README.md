# 项目技术文档

## 当前使用文档

当前项目文档以 Data Service 知识库架构为主线。Data Service 后续更新只维护 [docs/data_service](./data_service/) 内文档；过时草案和早期阶段文档已收纳到 [history](./history/) 或 [data_service/history](./data_service/history/)。

1. [Data Service 文档入口](./data_service/README.md)
2. [项目最新基线文档](./data_service/PROJECT-BASELINE.md)
3. [项目验收计划](./data_service/ACCEPTANCE-PLAN.md)
4. [项目当前架构状态](./data_service/CURRENT-STATUS.md)
5. [当前与目标架构 Gap](./data_service/current-vs-target-gap.md)
6. [当前与目标差异图](./data_service/current_vs_target_flow.drawio)
7. [当前架构图](./data_service/diagrams/01_current_architecture.drawio)
8. [目标架构图](./data_service/diagrams/02_target_architecture.drawio)
9. [开发计划 / 执行路线图](./data_service/2026-04-26-data-service-execution-roadmap.md)

## 通用参考文档

1. [系统概述](./architecture/overview.md)
2. [数据流](./architecture/dataflow.md)
3. [模块详细设计](./architecture/module-design.md)
4. [API 参考](./api/)
5. [快速开始](./guides/quickstart.md)
6. [配置说明](./guides/configuration.md)
7. [部署指南](./guides/deployment.md)
8. [ASR 扩展指南](./guides/asr-adapter-guide.md)
9. [LLMWiki CLI 使用指南](./llmwiki-cli.md)

---

## 项目简介

项目当前已经从单一会议语音助手演进为本地知识库 Data Service。当前主线支持：

- 真实资料一次 ingest
- `distill` 中间层结构化
- LLMWiki 可读知识页面
- GraphRAG 实体、主题、关系和社区图谱
- `/knowledge` 知识库工作台
- CLI / HTTP API / MCP 统一入口

会议语音助手能力仍作为项目能力的一部分保留。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + TypeScript + Pinia |
| 后端 | Python FastAPI |
| ASR引擎 | SenseVoice (阿里开源) |
| 通信 | WebSocket (实时) + REST (控制) |

## 在线文档

- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
