# Local Knowledge Governance Service 文档入口

本项目已从原会议应用语境中抽象为独立的 MCP-first 本地知识治理服务。它负责把外部应用传入的文本、文档块、会议转写、代码分析产物，以及本地文件夹中的多格式文件，转化为可追溯知识单元、实体关系图谱、可读 Wiki、质量规则和可检索上下文。

上层会议、学习、面试、代码理解等应用只能通过 MCP / CLI / HTTP 调用本服务，不应直接读写内部 workspace 文件结构。

## 当前使用文档

1. [项目最新基线](./PROJECT-BASELINE.md)
2. [验收计划](./ACCEPTANCE-PLAN.md)
3. [当前架构状态](./CURRENT-STATUS.md)
4. [当前与目标架构 Gap](./current-vs-target-gap.md)
5. [开发计划](./2026-04-26-data-service-execution-roadmap.md)
6. [剩余开发计划](./REMAINING-DEVELOPMENT-PLAN-2026-04-30.md)
7. [MCP 外部 Agent 调用说明](./MCP-EXTERNAL-AGENT-GUIDE.md)
8. [Knowledge Service Console Gap 文档](./PERSONAL-KNOWLEDGE-PRODUCT-GAP-2026-05-06.md)
9. 当前 / 目标架构图
- [当前与目标差异图](./current_vs_target_flow.drawio)
- [当前架构图](./diagrams/01_current_architecture.drawio)
- [目标架构图](./diagrams/02_target_architecture.drawio)

## 当前实现承载层

- `backend/data_service`: Knowledge Governance Service 当前实现承载层，负责 workspace、source、build、distill、query、quality、CLI、MCP。
- `backend/app/llmwiki`: 可读 Wiki 固化引擎。
- `backend/app/graphrag`: 内置 GraphRAG 执行与图谱查询服务。
- `backend/app/api/v1/data_service.py`: HTTP API 边界。
- `/knowledge`: 服务治理控制台，不是会议、学习、面试或代码助手的终端用户 App。

## 历史文档

过时草案和旧过渡图已收纳到 [history](./history/)。
