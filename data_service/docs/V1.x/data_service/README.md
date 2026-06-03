# Local Knowledge Governance Service 跨版本文档入口

本项目已从原会议应用语境中抽象为独立的 MCP-first 本地知识治理服务。它负责把外部应用传入的文本、文档块、会议转写、代码分析产物，以及本地文件夹中的多格式文件，转化为可追溯知识单元、实体关系图谱、可读 Wiki、质量规则和可检索上下文。

上层会议、学习、面试、代码理解等应用只能通过 MCP / CLI / HTTP 调用本服务，不应直接读写内部 workspace 文件结构。

## 当前版本文档

- [V1.5 冻结基线](../V1.5/README.md)：V1.5 accepted 状态、阶段报告、contract 文档、gap 文档和验收截图。
- [V1.6 规划文档](../V1.6/README.md)：V1.6 目标架构、gap、开发计划、验收计划和公开面基线；当前已 accepted 到 E5，target HTTP route count = 35，F console polish 仍为 planned。
- [MCP 外部 Agent 调用说明](./MCP-EXTERNAL-AGENT-GUIDE.md)：跨版本调用说明。

## 早期基线与历史文档

- [项目旧基线](./PROJECT-BASELINE.md)
- [旧验收计划](./ACCEPTANCE-PLAN.md)
- [旧当前架构状态](./CURRENT-STATUS.md)
- [2026-04 开发计划](./2026-04-26-data-service-execution-roadmap.md)
- [2026-04 剩余开发计划](./REMAINING-DEVELOPMENT-PLAN-2026-04-30.md)
- [Knowledge Service Console 早期 Gap 文档](./PERSONAL-KNOWLEDGE-PRODUCT-GAP-2026-05-06.md)
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
