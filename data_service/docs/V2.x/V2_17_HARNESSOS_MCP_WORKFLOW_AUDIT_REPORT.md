# V2.17 审计报告：HarnessOS MCP 工作流接入

## 1. 审计结论

结论：有条件通过。

`data_service` 当前可以作为 HarnessOS 多 Agent 联合开发工作流中的“项目智能 MCP 工具层”接入，承担项目理解、证据追踪、任务上下文、影响分析、Review 输入、patch preview 和受控 runtime profile 等职责。

但 `data_service` 不应被声明为 HarnessOS 工作流编排核心。HarnessOS 仍需负责 Agent 编排、权限审批、执行状态机、任务生命周期和真实代码修改/提交策略。

## 2. 审计证据

### 2.1 MCP 工具能力

本地检查结果：

```text
all_tool_specs() tool_count = 156
knowledge_code_* = 99
knowledge_code_architecture_* = 57
knowledge_codebase_* = 5
```

代表性工具：

```text
knowledge_codebase_import
knowledge_codebase_snapshot
knowledge_code_architecture_docs_build
knowledge_code_architecture_doc_code_alignment_build
knowledge_code_architecture_human_report_v2_build
knowledge_code_architecture_context_pack_v3
knowledge_code_actionability_build
knowledge_code_impact_analyze
knowledge_code_task_plan
knowledge_code_patch_plan_create
knowledge_code_patch_preview_create
knowledge_code_runtime_profiles_build
knowledge_code_runtime_profile_run
knowledge_code_workbench_v2_build
knowledge_code_large_project_advisor_build
```

### 2.2 V2.16 closure

`V2_16_PHASE_82_CLOSURE_AUDIT_REPORT.md` 记录：

- Provider Capability Registry：accepted。
- Semantic Provider Orchestrator：accepted。
- Runtime Profile Manager：accepted。
- Workbench v2：accepted。
- Large-Project Abstraction Advisor：accepted。
- Human-Gated Patch Sandbox：accepted。
- Closure Acceptance：accepted。

自动化测试记录：

```text
27 passed
git diff --check -- . passed
```

近期全量防护记录：

```text
PYTHONPATH=backend python3 -m pytest backend/tests -q
456 passed, 617 warnings

npm run build
passed
```

### 2.3 HarnessOS repo 和文档资产

本地路径存在：

```text
/Users/Zhuanz/Desktop/workspace/harnessOS
```

已发现文档资产：

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `docs/design/V4.x/*`
- `docs/design/V9.x/*`
- `docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio`
- workflow spec、runtime matrix、acceptance gate、security threat model、controlled executor、terminal sandbox 等文档。

## 3. 职责边界审计

| 能力 | data_service | HarnessOS | 审计意见 |
| --- | --- | --- | --- |
| 项目理解 | 是 | 消费输出 | 通过 |
| 证据追踪 | 是 | 消费输出 | 通过 |
| context pack | 是 | 分发给 Agent | 通过 |
| task plan | 是 | 纳入 workflow | 通过 |
| patch preview | 是，只读 | 审批后决定下一步 | 通过 |
| runtime profile | 是，allowlist-only | 定义/批准策略 | 通过 |
| Agent orchestration | 否 | 是 | 边界清晰 |
| 任意命令执行 | 否 | 需受控 | 边界清晰 |
| 自动修改源码 | 否 | 高风险审批 | 边界清晰 |
| git commit/push | 否 | HarnessOS/人类 | 边界清晰 |

## 4. PRD 规格检视

| 检视项 | 结论 |
| --- | --- |
| 文档是否说明目标体验 | 通过 |
| 是否区分 MCP 工具层和编排核心 | 通过 |
| 是否使用真实 MCP 工具数据 | 通过 |
| 是否确认 HarnessOS 真实路径 | 通过 |
| 是否定义用户场景 | 通过 |
| 是否定义 ready/gated/blocked | 通过 |
| 是否防止 autonomous code modification 过度声明 | 通过 |
| 是否防止 full static analysis 过度声明 | 通过 |

## 5. False-Green 审计

拒绝项：

- 只因 MCP tool 存在就声称 HarnessOS 编排闭环完成：未发现。
- 将 patch preview 说成 patch apply：未发现。
- 将 runtime profile 说成任意命令执行：未发现。
- 将文档 claim 说成代码 fact：未发现。
- 将 data_service 说成 HarnessOS workflow engine：未发现。

## 6. 风险与限制

| 风险 | 等级 | 处理 |
| --- | --- | --- |
| 尚未通过 HarnessOS MCP client 做真实端到端调用 | Major for production integration | 正式接入前必须补真实 MCP client E2E。 |
| HarnessOS 大项目仍可能有 needs_review / blocker | Medium | 保持 structured blocker，不假装 accepted。 |
| runtime profile 需要和 HarnessOS 权限策略映射 | Medium | 由 HarnessOS 负责审批和 profile policy。 |
| patch apply 默认 blocked | Accepted boundary | 这是安全边界，不是缺陷。 |

## 7. 最终审计意见

- Fatal findings：0
- Major planning findings：0
- Major production integration prerequisites：1
  - 需要 HarnessOS MCP client 真实端到端接入验收。
- Minor findings：0

最终结论：

```text
V2.17 特殊验收文档和接入审计通过。
data_service 可以作为 HarnessOS 项目智能 MCP 工具层进入真实接入前试运行。
正式生产级联合开发闭环还需要 HarnessOS 侧 MCP client E2E 和 workflow state 消费验证。
```

