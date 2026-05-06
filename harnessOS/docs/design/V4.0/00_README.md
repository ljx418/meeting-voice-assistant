# harnessOS V4.0 Design Docs

文档状态：V4.0 design entrypoint。

## Positioning

V4.0 不是继续堆单一业务，而是把 harnessOS 从 “多 app 共用 Core” 推进成：

> Workflow Descriptor Platform + Studio Console + Nested HarnessOS Runtime

V3.0 解决 Core、Pack、Connector、Governance 的稳定化；V4.0 才把这些底座产品化为：

- Studio UI
- Workflow Console
- Agent / Workflow / Skill / Connector Descriptor
- Quality Board
- Embedded / Nested HarnessOS

## Documents

| 文件 | 状态 | 用途 |
| --- | --- | --- |
| `v4_target_architecture_workflow_console.md` | DRAFT TARGET ARCHITECTURE | V4.0 目标架构、控制台、嵌套调用和 descriptor 平台说明。 |
| `v4_target_architecture_workflow_console.drawio` | DRAFT TARGET DIAGRAM | V4.0 目标架构图。 |

## Scope

V4.0 主要关注：

- 用户自然语言生成工作流
- 用户可视化微调 workflow / agent / skill / quality rules
- 业务方把生成出的工作流嵌入自己的项目
- HarnessOS 作为工作流平台而不只是单一助手后端

## Non-Goals

以下内容不应在 V4 文档中被误写为“已实现”：

- 任意外部模型 / 视频引擎即插即用
- 全自动高质量剧情视频生成
- 完整多租户商业化权限系统
- 完整分布式调度 / GPU 资源编排
