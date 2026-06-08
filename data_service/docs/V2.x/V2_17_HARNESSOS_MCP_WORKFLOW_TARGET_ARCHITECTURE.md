# V2.17 目标架构：HarnessOS MCP 工作流接入

## 1. 架构结论

目标架构不是“data_service 接管 HarnessOS”，而是：

```text
HarnessOS = 工作流编排 / Agent 调度 / 权限审批 / 执行状态机
data_service = 项目智能 MCP 工具层 / 证据层 / 上下文层 / 风险审查层
```

## 2. 高层架构

```text
┌────────────────────────────────────────────────────────────┐
│ HarnessOS Multi-Agent Workflow                             │
│                                                            │
│  Workflow Agent ─┬─ Coding Agent                           │
│                  ├─ Review Agent                           │
│                  ├─ Documentation Agent                    │
│                  └─ Human Approval Gate                    │
└───────────────────────────┬────────────────────────────────┘
                            │ MCP calls
┌───────────────────────────▼────────────────────────────────┐
│ data_service Project Intelligence MCP Tool Layer            │
│                                                            │
│  Codebase Registry / Snapshot / Surface / Symbols           │
│  Architecture Docs / Claims / Alignment / Human Report      │
│  Actionability / Impact / Task Plan / Context Pack          │
│  Patch Preview / Runtime Profile / Workbench v2             │
└───────────────────────────┬────────────────────────────────┘
                            │ reads local repo artifacts
┌───────────────────────────▼────────────────────────────────┐
│ HarnessOS Local Repository                                  │
│                                                            │
│  source code / docs/design / workflow specs / tests         │
└────────────────────────────────────────────────────────────┘
```

## 3. 组件职责

| 组件 | 归属 | 职责 |
| --- | --- | --- |
| Workflow Coordinator | HarnessOS | 决定任务流、Agent 顺序、状态迁移。 |
| Human Authorization | HarnessOS | 高风险动作审批。 |
| Agent Runtime / Executor | HarnessOS | 执行 Agent 或终端任务。 |
| MCP Project Intelligence | data_service | 项目理解、证据、上下文、审查报告。 |
| Safe Patch Preview | data_service | 只读 diff / rollback / validation plan。 |
| Runtime Profile Evidence | data_service | allowlist-only 验证建议和结果记录。 |
| Codebase Artifacts | data_service | snapshot、surface、symbols、architecture、context pack。 |

## 4. MCP 工具分层

### 4.1 项目资产层

```text
knowledge_codebase_import
knowledge_codebase_snapshot
knowledge_codebase_describe
knowledge_codebase_list
```

### 4.2 项目理解层

```text
knowledge_code_architecture_docs_build
knowledge_code_architecture_doc_claims_build
knowledge_code_architecture_doc_code_alignment_build
knowledge_code_architecture_human_report_v2_build
knowledge_code_architecture_context_pack_v3
knowledge_code_architecture_large_project_advisor_read
```

### 4.3 Coding Agent 准备层

```text
knowledge_code_actionability_build
knowledge_code_impact_analyze
knowledge_code_task_plan
knowledge_code_patch_plan_create
knowledge_code_patch_preview_create
knowledge_code_workbench_v2_build
```

### 4.4 受控验证层

```text
knowledge_code_runtime_profiles_build
knowledge_code_runtime_profile_run
knowledge_code_runtime_profile_result
knowledge_code_incremental_diff
knowledge_code_drift_timeline
```

## 5. 数据流

```text
HarnessOS task
  -> MCP: project/context request
  -> data_service reads HarnessOS repo
  -> data_service emits evidence-backed artifacts
  -> HarnessOS assigns Agent work
  -> Coding Agent reads context
  -> Review Agent checks evidence/risk
  -> data_service produces patch preview / runtime evidence
  -> HarnessOS handles approval and execution
```

## 6. 安全边界

### 6.1 data_service 禁止事项

- 不运行任意命令。
- 不自动修改源码。
- 不自动 git commit / push。
- 不绕过 HarnessOS human approval。
- 不把低置信结论写成 accepted。
- 不把文档声明伪装成代码事实。

### 6.2 允许事项

- 生成只读 patch preview。
- 生成 rollback artifact。
- 运行 allowlist runtime profile。
- 返回 structured blocker。
- 给 HarnessOS 提供 evidence-backed context。

## 7. 接入模式

### 模式 A：只读审计接入

HarnessOS 只调用导入、snapshot、architecture、report、context pack。

适用：项目理解、文档审计、架构差异分析。

### 模式 B：开发前准备接入

HarnessOS 调用 impact analysis、task plan、safe patch plan。

适用：Coding Agent 开始写代码前。

### 模式 C：审查与验证接入

HarnessOS 调用 patch preview、runtime profile、workbench。

适用：Review Agent 和人类审批前。

## 8. 目标状态

V2.17 目标状态：

- data_service 作为 MCP tool provider 被 HarnessOS 调用。
- HarnessOS 将 data_service 输出当作 evidence/context/risk 输入。
- data_service 不控制 HarnessOS workflow。
- 所有高风险动作由 HarnessOS 或人类审批。

