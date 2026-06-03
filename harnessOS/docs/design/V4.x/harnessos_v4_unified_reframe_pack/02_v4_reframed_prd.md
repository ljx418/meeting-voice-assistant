# HarnessOS V4 目标形态 PRD：Headless AI Workflow OS

## 1. 产品定位

HarnessOS V4 不再以“完整低代码拖拽式 Workflow Studio”为核心产品形态，而是演进为一个 **Headless-first AI Workflow OS**。

它的核心价值是：

```text
让用户通过自然语言或命令定义工作流；
通过 Drawio / HTML Report / Thin Web Console 理解和观察工作流；
通过 Mission Console 进行确认、运行、修复、重跑和审计；
通过后端 Headless Workflow Core 保持统一事实源。
```

## 2. 目标用户

| 用户类型 | 目标 |
|---|---|
| AI 应用开发者 | 快速定义、运行、调试 AI 工作流，不被复杂前端拖累。 |
| 产品 / 解决方案人员 | 用自然语言生成工作流方案，并用报告和图示向团队解释。 |
| 客户成功 / 交付团队 | 通过可审计报告展示工作流运行过程、产物和质量。 |
| 工程团队 | 用 TUI / WorkflowSpec / HTML Report 管理长时工程任务。 |
| 未来业务 App | 通过 Headless API / BFF / Embed Head 复用 HarnessOS 工作流能力。 |

## 3. 核心产品原则

### 3.1 不再以完整 Web Studio 为主线

完整 Web Workflow Studio 可以作为未来增强，但不再是当前 V4 主交付。

当前主线是：

```text
Mission Console + Workflow Blueprint + Runtime Report + Review Console + Evidence Chain
```

### 3.2 所有 Head 共享同一事实源

TUI、Drawio、HTML Report、Thin Web Console、未来业务 App 都不能自建 runtime truth。

它们必须消费同一组事实源：

```text
WorkflowSpec
WorkflowDraft / WorkflowVersion
WorkflowInstance / StationRun
Artifact / QualityEvaluation
OperationEvidence / GovernanceReview
```

### 3.3 Agent 是协作者，不是执行者

Agent 可以：

```text
解释
总结
追问
生成 WorkflowSpec
生成 Patch Proposal
提出修复建议
handoff 到操作面板
```

Agent 不能：

```text
auto apply
auto publish
auto run
auto rerun
auto approval.respond
auto context.update
auto business.event.emit
```

### 3.4 用户确认是核心体验，不是多余摩擦

任何 durable mutation 都必须经过用户确认。

用户确认时必须看到：

```text
操作摘要
影响范围
风险标记
是否可恢复
是否生成 evidence
下一步状态
```

## 4. 目标体验主线

V4 结束后的目标用户体验可以压缩为一条线：

```text
用户说目标
 -> Mission Console 捕获意图
 -> 系统生成 WorkflowSpec
 -> 系统生成 Workflow Blueprint / Drawio
 -> 系统展示 Diff / 风险 / 可用动作
 -> 用户确认
 -> 系统运行工作流
 -> Runtime Report 展示状态、产物、质量
 -> 失败时用户局部重跑或让 Agent 提出修复
 -> Evidence Chain 留下审计记录
```

## 5. 核心界面与交互形态

### 5.1 Mission Console / 任务驾驶舱

主要入口。可以是 TUI、Command Palette 或 Thin Web Console 中的命令面板。

承担：

```text
输入目标
生成方案
查看 Diff
确认 Apply / Publish / Run
查看状态
发起局部重跑
请求 Agent 解释失败
生成修复建议
查看 Evidence
```

### 5.2 Workflow Blueprint / 工作流图纸

由 Drawio 生成。

承担：

```text
展示工作流结构
展示工位关系
展示 Artifact 血缘
展示质量门禁
展示重跑历史
```

它是只读图示，不是 runtime truth。

### 5.3 Runtime Report / 运行报告

由 HTML Report 生成。

承担：

```text
展示 WorkflowInstance 状态
展示 StationRun 列表
展示每个工位输入输出
展示 Artifact
展示 QualityEvaluation
展示错误和重跑历史
展示 Evidence Chain
```

### 5.4 Review Console / 审查控制台

Thin Web Console 或 Mission Console 的受限操作入口。

承担：

```text
确认运行
确认重跑
确认继续下游
查看 evidence
归档结果
```

不承担完整低代码编辑。

### 5.5 Evidence Chain / 证据链

记录：

```text
Agent 建议
Handoff
用户确认
Runtime 结果
Artifact / Quality
OperationEvidence
GovernanceReview
```

## 6. 关键体验路径

### 路径一：自然语言创建工作流

用户输入：

```text
帮我创建一个工作流，递归总结 Desktop/技术分享 下的 Markdown 文件。
```

系统输出：

```text
WorkflowSpec
Diff
Drawio Blueprint
可用动作
风险提示
用户确认入口
```

验收：

```text
用户确认前不写 runtime。
Agent 不自动 apply。
WorkflowSpec 不替代 WorkflowDraft / WorkflowVersion。
```

---

### 路径二：工作流结构可视化

系统生成：

```text
workflow.drawio
workflow_status.drawio
artifact_lineage.drawio
quality_gate.drawio
rerun_history.drawio
```

验收：

```text
Drawio 可重现。
Drawio 不包含敏感字段。
Drawio 不可反写 runtime。
```

---

### 路径三：运行与观察

用户确认运行后，系统展示：

```text
workflow_board.html
station_detail.html
artifacts.html
quality.html
evidence.html
```

验收：

```text
HTML Report 只读。
EventBridge 只触发 refresh。
状态来自 BFF / runtime DTO。
```

---

### 路径四：工位产物与质量监控

每个工位展示：

```text
输入 Artifact
输出 Artifact
质量结果
错误摘要
耗时
attempt 历史
上下游关系
```

验收：

```text
Artifact 可见。
Quality report 可见。
低质量或失败工位可定位。
```

---

### 路径五：局部失败修复与重跑

当某个 Station 失败：

```text
系统显示失败原因。
用户可请求 Agent 解释。
Agent 可生成修复 proposal。
用户确认后执行 rerun。
旧 attempt 保留。
下游 stale 可见。
```

验收：

```text
rerun 必须 user_confirmed。
source=agent 不能 rerun。
旧 attempt 不被覆盖。
```

---

### 路径六：治理证据链审查

每次关键操作留下：

```text
proposal_id
handoff_id
user_confirmed
operation_type
runtime_result_ref
risk_flags
policy_decision
correlation_id
redaction_status
```

验收：

```text
Evidence 只读。
不能伪造 evidence。
不能从 evidence 页面直接执行 mutation。
```

---

### 路径七：串行多 Agent 视频工作流

目标流程：

```text
编剧 Agent
 -> 分镜 Agent
 -> 文案 Agent
 -> 剪辑计划 Agent
 -> 质量审查 Agent
 -> 发布准备 Agent
```

用户能看到：

```text
每个工位 role / goal / model / tool / skill 配置
每个工位产物
中间工位重跑
下游 stale
视频 workflow report
```

---

### 路径八：并行多 Agent 罗马广场讨论

目标流程：

```text
Orchestrator
  -> Persona A
  -> Persona B
  -> Persona C
  -> Synthesis
  -> Contradiction Review
```

用户能看到：

```text
多 Agent 并行状态
每个 Persona 独立观点 Artifact
交叉启发关系
观点归因
最终汇总报告
```

---

### 路径九：长时工程任务工作流

目标流程：

```text
产品规划
规格梳理
项目蓝图
架构评审
子阶段审计
开发实施
代码检视
E2E
人工确认
```

用户能看到：

```text
durable task board
stage artifacts
quality gates
manual checkpoint
rerun history
evidence chain
```

## 7. 非目标

当前 V4 统一体验阶段不追求：

```text
完整 Web 低代码编辑器
高保真 ComfyUI 克隆
Agent 自动执行器
生产级多租户控制台
生产文件系统权限模型
完整 AgentTalkWindow
production-ready external app support
```

## 8. 成功标准

V4 统一体验成功标准：

```text
用户可以定义工作流。
用户可以看懂工作流。
用户可以确认并运行。
用户可以看到每个工位状态和产物。
用户可以对失败环节局部重跑。
用户可以查看质量和风险。
用户可以查看完整证据链。
TUI / Drawio / HTML Report / Thin Web Console 共享同一状态模型。
Agent 不越权执行。
```

## 9. 推荐对外描述

```text
HarnessOS V4 是一个 Headless-first AI Workflow OS。它不再把完整 Web Studio 作为唯一入口，而是通过 Mission Console、Workflow Blueprint、Runtime Report 和 Review Console，让用户以自然语言和可审查报告的方式定义、运行、观察、修复和审计 AI 工作流。
```
