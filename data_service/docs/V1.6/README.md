# Data Service V1.6 文档入口

更新时间：2026-05-12

V1.6 从 V1.5 accepted baseline 出发。V1.5 已完成 MCP-first local knowledge governance microservice 的收口验收，后续 V1.6 文档只描述下一阶段规划、目标架构、gap、验收标准和公开面护栏，不表示这些能力已经实现。

V1.6 的核心方向是：在不破坏 V1.5 兼容入口和微服务边界的前提下，按最小能力组继续开放 target HTTP、Graph advanced、Session GraphRAG public contract 和 quality governance 能力。

## 文档索引

- `public-surface-baseline.md`：V1.5 冻结基线，作为 V1.6 的公开面起点。
- `target-architecture.md`：V1.6 目标架构。
- `current-vs-target-gap.md`：V1.6 当前与目标差距。
- `current-vs-target-gap.drawio`：V1.6 gap 图。
- `development-plan.md`：V1.6 分阶段开发计划。
- `acceptance-plan.md`：V1.6 验收计划。
- `interface-convergence-plan.md`：V1.6 MCP / CLI / HTTP / target HTTP 接口收敛计划。
- `target-http-routes-plan.md`：V1.6 target HTTP route 开放计划。

## 基线

V1.5 基线已固化在 `../V1.5/`：

- V1.5 closure status：accepted。
- MCP tool count：40。
- CLI 顶层命令：`build / graph / quality / query / source / trace / workspace`。
- target HTTP 当前只开放 3 个 route：
  - `POST /api/workspaces/{workspace_id}/query`
  - `POST /api/workspaces/{workspace_id}/distill`
  - `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`
- `/api/v1/knowledge/*` compatibility routes retained。
- `/knowledge` 是 service governance console，不是 end-user knowledge consumption app。

## 同步规则

V1.6 开始后，每个子阶段完成时必须同步更新：

- `development-plan.md`
- `acceptance-plan.md`
- `current-vs-target-gap.md`
- `current-vs-target-gap.drawio`
- 与该阶段直接相关的 contract / convergence plan

任何文档不得暗示未实现的 V1.6 候选能力已经开放。公开面状态以实测 MCP registry、CLI parser 和 HTTP route 扫描为准。
