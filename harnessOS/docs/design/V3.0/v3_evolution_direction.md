# harnessOS V3.x 演进方向说明

文档状态：REFERENCE / FUTURE BLUEPRINT。

重要声明：

- 本文件不是当前 V3.0-PhaseA 到 V3.0-PhaseE 活动实施计划。
- 当前活动实施计划以 `docs/design/V3.0/v3_development_plan_multi_app_core.md` 为准。
- Low-Code Workflow、Core Memory、Feedback Optimization Loop、Workflow Library 均属于 V3.x+ 远期方向，不进入当前 V3.0-PhaseA 到 V3.0-PhaseE 验收范围。

说明：本文件为未来演进讨论，不代表当前活动架构基线。当前处于活动状态的 V3.0 计划保存在 `docs/design/V3.0/v3_development_plan_multi_app_core.md`。

当前落地策略：下一阶段不直接实现完整低代码画布、Core Memory、Feedback Optimization Loop 或 Workflow Library，而是先推进 **Multi-App Core Readiness / Pack Assembly + Connector Registry / Meeting and Knowledge reference pack validation**。Meeting 和 Knowledge 是当前标准迁移样板，Video Studio 延后到 V3.3。

## 1. V3.x+ 远期总体定位

harnessOS V3.x+ 的远期目标不是围绕某一个业务场景继续扩展，而是从 V2.0 的：

> Protocol-first Harness Core + OS-like Agent App Server + Domain Pack Platform

进一步演进为：

> 可交互、可编排、可扩展、可组装的 Agent 工作流平台

V3.x+ 的重点是让用户既可以通过低代码方式搭建工作流，也可以通过 Domain Pack 的方式沉淀复杂、多智能体、可复用的业务能力。同时，V3.x+ 将深入 Harness Core 内部，强化记忆机制，让系统具备更强的上下文延续、经验沉淀、偏好学习和自我优化能力。

## 2. V3.x+ 与 V2.0 的关系

V2.0 解决的是平台基础设施问题：

- 统一协议入口
- Session / Thread / Turn / Item 对象模型
- Job / Artifact / Trace / Approval / Retry
- Runtime Adapter
- Domain Pack
- Connector Registry
- Policy / Secret / Governance

V3.x+ 不推翻 V2.0 六层架构，而是在其上增强三类能力：

1. 通用工作流编排能力
2. 低代码交互与 Domain Pack 双模式装配能力
3. Harness Core 级记忆与反馈优化能力

## 3. V3.x+ 远期核心能力

### 3.1 通用工作流编排

V3.x+ 可引入更通用的 Workflow Model，支持：

- 节点
- 边
- 条件分支
- 并行执行
- 循环
- 人工确认
- 审批点
- 工具调用
- Connector 调用
- Artifact 输入输出
- Job 化执行
- 局部重跑
- 失败恢复

这使 harnessOS 不再只是调用某个 agent 完成任务，而是可以运行可追踪、可治理、可复用的复杂工作流。

### 3.2 低代码工作流平台

V3.x+ 可支持用户通过低代码方式定义工作流，例如：

- 定义工位 / 工种
- 定义每个节点的输入输出
- 选择可用工具或 Connector
- 设置审批点
- 设置失败重试策略
- 设置产物类型
- 设置质量评审标准

初期不一定需要复杂图形画布，可以先从表单、YAML、manifest 或配置式工作流开始。关键是先把运行模型和协议模型稳定下来。

### 3.3 Domain Pack 多智能体编排

Domain Pack 仍然是复杂业务能力的正式发布单元。Pack 应该可以声明：

- workflow
- workflow templates / Typed DAG
- subagent
- Pack-owned agents / roles
- skill
- connector refs
- connector capabilities / tool contracts
- policy bundle
- artifact kinds
- artifact schemas / lineage
- memory scopes
- evaluation rules

低代码工作流适合快速搭建和试验，Domain Pack 适合工程化沉淀和复用。

二者关系是：

```text
低代码工作流 = 快速搭建、实验、个人化自动化
Domain Pack = 稳定发布、复用、版本化、团队级能力
```

低代码工作流成熟后，可以升级为 Domain Pack 或 Pack 内部的 workflow template。

### 3.4 DomainPack 2.0 Assembly Kernel

本节是旧 V3.0 草案中的远期平台能力说明，不是当前 V3.0-PhaseA 到 V3.0-PhaseE 的实施边界。当前活动计划中的对应交付是 `PackAssemblyResult` 合同与 Pack Assembly MVP，详见 `v3_development_plan_multi_app_core.md`。

远期 DomainPack 2.0 Assembly Kernel 负责把 Pack manifest 中的 workflow templates、Agent、skills、connector contracts、policy bundles、artifact schemas、memory scopes 和 evaluation rules 装配成可查询、可治理、可执行前置校验的 assembly result。

Assembly result 至少包含：

- `status`: `assembled / blocked / degraded / stub`
- `workflow_templates`
- `agents`
- `connector_requirements`
- `missing_dependencies`
- `blocked_reason`
- `next_actions`

远期 Typed DAG MVP 可作为后续扩展方向：

- 支持 node / edge / dependencies / inputs / outputs / artifact refs。
- 节点类型限定为 `agent`、`skill`、`tool`、`connector`、`artifact`、`approval`、`evaluation`。
- 暂不支持循环和复杂条件；并行先作为 DSL 表达，不作为第一阶段执行要求。

### 3.5 Knowledge Connector 远期执行化参考

本节保留旧计划中的 Knowledge connector 资料作为 V3.0-PhaseE 的参考背景。当前活动验收只要求 Knowledge Pack 通过 ConnectorRegistry 接入本地 Knowledge MCP，并完成 ingest/search/summarize/citation 端到端迁移。

- 声明 connector ref、tool schema、capability requirements 和 health/assembly 展示。
- `pack.get(domain=knowledge)` 能展示知识库生命周期 DAG、Pack-owned agents、`data_service_mcp` connector requirement 和 tool contract。
- 默认仍保持 contract stub，不阻塞本地开发和 CI。
- 显式设置 `HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio` 后，harnessOS 可启动相邻项目 `data_service.mcp_stdio` 并通过 MCP `tools/call` 执行 lifecycle / v2 tools。
- Knowledge lifecycle runner 在真实 stdio 模式下复用持久 MCP session，保证 data_service build queue 状态可跨 `knowledge_build_start` 与 `knowledge_build_status` 保留。
- 外部 Agent 调用说明以 `/Users/Zhuanz/Desktop/workspace/data_service/docs/MCP-EXTERNAL-AGENT-GUIDE.md` 为准，入口已随 data_service 迁移到独立 `/Users/Zhuanz/Desktop/workspace/data_service` 项目。
- Knowledge Pack 后续搭建知识库工作流时，只通过 `data_service_mcp` lifecycle tools 和 v2 envelope tools 操作 GraphRAG + llmwiki 知识库，不直接读写 data_service 内部产物目录。
- Meeting Pack 的底层语音转写能力使用 `funasr_mcp` / `funasr_service`，Knowledge Pack 的知识库能力使用 `data_service_mcp` / `data_service`。

`data_service_mcp` 预期工具：

- `knowledge_workspace_create`
- `knowledge_workspace_list`
- `knowledge_workspace_describe`
- `knowledge_source_import`
- `knowledge_source_list`
- `knowledge_source_remove`
- `knowledge_build_start`
- `knowledge_build_status`
- `knowledge_build_cancel`
- `knowledge_workspace_archive`
- `knowledge_query_v2`
- `knowledge_quality_summary_v2`
- `knowledge_quality_feedback_v2`
- `knowledge_correction_rules_v2`
- `knowledge_review_correction_rule_v2`
- `knowledge_correction_plan_v2`

统一返回字段为 `workspace_id`、`operation_id`、`status`、`warnings`、`artifact_refs`、`next_actions` 和 `data`。workspace 必须受 `DATA_SERVICE_WORKSPACE_ROOT` allowlist 约束，source path 必须经过 allowlist、大小上限、sha256 去重和 symlink 防绕过。

## 4. Harness Core 记忆机制强化（Deferred）

本节为 V3.x+ 远期蓝图，不进入当前 V3.0-PhaseA 到 V3.0-PhaseE 验收。当前 V3.0 只做 Core scope、Pack、Connector、Job、Artifact、Governance 稳定化。

当前系统已有 session、compact、memory file 等能力，但还不够成为平台级智能能力。V3.0 需要将 memory 设计为 Core 的一等能力之一。

建议分层：

- Session Memory：当前会话内的长期上下文摘要。
- Project Memory：项目规则、架构约定、长期开发偏好。
- Workflow Memory：某类工作流的历史执行经验、失败原因、优化策略。
- Agent Memory：不同 agent / role 的行为偏好和协作经验。
- User Preference Memory：用户偏好的表达方式、审美、决策习惯。
- Evaluation Memory：用户评审、质量判断、验收标准、历史反馈。

Memory 不应该只是写入一些文本。它应该能参与：

- intent routing
- workflow planning
- prompt construction
- tool selection
- retry optimization
- artifact review
- agent coordination

同时，Memory 必须受治理约束：

- 可追踪
- 可撤销
- 可审计
- 敏感信息脱敏
- 关键记忆写入可触发 approval

## 5. V3.x+ 与现有 Agent 框架的关系

OpenHarness、DeepAgents 等框架本身也有 tool、skill、memory、session、MCP 等能力，但 harnessOS 不应该直接把这些内部机制作为产品边界。

原因是：

- Agent 框架关注单个 agent 如何运行。
- harnessOS 关注多个 runtime、多个业务 Pack、多个客户端、多个工作流如何统一治理和长期演进。

因此 V3.x+ 的关系应是：

```text
OpenHarness / DeepAgents
  = 可插拔执行内核

Runtime Adapter
  = 隔离不同执行内核

Harness Core
  = 统一协议、状态、治理、记忆、作业、产物

Domain Pack / Low-Code Workflow
  = 业务工作流装配层

Connector / Tool / Store
  = 外部能力、工具、数据和持久化事实源
```

这不是重复造轮子，而是把框架能力纳入平台边界中统一治理。

## 6. 典型案例

### 案例一：AI 视频生产

用户通过低代码方式配置脚本、导演、分镜、拍摄、剪辑、配音、质检等工种，并接入本地 ComfyUI 工作站。

流程：

```text
创作 brief
  -> 脚本
  -> 分镜
  -> prompt
  -> 文生图 / 文生视频
  -> 配音
  -> 剪辑方案
  -> 成片
  -> 用户评审
  -> 局部优化
```

该案例验证的是：

- 多工种协作
- 长任务 Job 化
- Connector 接入
- Artifact lineage
- 用户反馈驱动优化

视频只是 V3.x+ 的应用案例之一，不是当前 V3.0-PhaseA 到 V3.0-PhaseE 的唯一方向或验收重点。

### 案例二：投资研究工作流

用户可以配置一个投资分析工作流：

```text
输入标的
  -> 获取市场数据
  -> 检索新闻
  -> 分析财报
  -> 生成风险摘要
  -> 形成投资备忘录
  -> 人工审批
  -> 记录决策和复盘结果
```

该案例验证的是：

- 数据 Connector
- 多步骤分析
- 审批治理
- 记忆化复盘
- 长期策略偏好沉淀

### 案例三：知识库研究工作流

用户可以配置：

```text
导入资料
  -> 分类
  -> 摘要
  -> 建立引用
  -> 生成专题报告
  -> 用户评审
  -> 调整知识结构
```

该案例验证的是：

- 文档 Artifact
- Citation
- Project Memory
- Knowledge Pack
- Review-driven refinement

## 7. V3.x+ 远期阶段建议

以下阶段名称来自旧草案，仅作为 V3.x+ 蓝图排序参考，不是当前 V3.0-PhaseA 到 V3.0-PhaseE 活动计划。

### V3.x+ Deferred：Generic Workflow Model

定义通用 workflow / node / edge / role / artifact / approval / retry 模型。

### V3.x+ Deferred：Low-Code Workflow Runtime

支持配置式创建、运行、暂停、重试、局部重跑和查看产物。

### V3.x+ Deferred：Domain Pack 2.0

让 Pack 支持完整多智能体 workflow、connector refs、skill refs、policy bundle、artifact kinds 和 memory scopes。

远期参考切片：

- Knowledge Pack primary：作为远期 Pack 复杂度样板参考；当前执行以 `v3_development_plan_multi_app_core.md` 的 V3.0-PhaseE 为准。
- Video Studio secondary：作为 V3.3 后的外部项目集成参考。
- Meeting regression：真实音频 workflow 和 artifact lineage 不回归。
- Backend Protocol First：先稳定协议、assembly model 和自动化测试，不做 UI / visual canvas。

### V3.x+ Deferred：Core Memory System

建立分层 memory，并接入 orchestrator、workflow planning、runtime adapter 和 retry/resume。

### V3.x+ Deferred：Feedback Optimization Loop

用户反馈可作用于整体工作流或单个节点产物，系统生成优化计划并执行局部重跑。

### V3.x+ Deferred：Workflow Library / Pack Library

沉淀可复用 workflow template、role template、skill template 和 connector template。
