# HarnessOS V4 统一体验验收矩阵

文档状态：historical/deprecated reframe-pack snapshot。

此文件保留用于追溯 V4 统一体验重构过程，不再作为 canonical acceptance。当前 canonical acceptance 为：

```text
docs/design/V4.x/v4_x_unified_experience_acceptance.md
```

原因：

```text
本历史快照只覆盖 UX-01 到 UX-11。
当前 V4-U5E 已新增 UX-12 真实 LLM 本地技术文档解析门禁。
不得用本文件绕过 UX-12 或进入 V4-U6。
```

## 1. 验收原则

所有验收不再只按技术模块，而按用户体验路径组织。

每条路径必须标记：

```text
PASS | PARTIAL | FAIL | BLOCKED
```

每条路径必须保存：

```text
transcript
drawio
html report
runtime/evidence json
screenshots if web involved
result-summary
```

## 2. 核心验收路径

| ID | 体验路径 | 入口 | 主要输出 | 验收重点 |
|---|---|---|---|---|
| UX-01 | 自然语言创建工作流 | Mission Console / Agent | WorkflowSpec、Diff、Drawio | 用户确认前不写 runtime |
| UX-02 | 工作流结构可视化 | WorkflowSpec / runtime DTO | workflow.drawio | Drawio 只读、可重现 |
| UX-03 | 工作流运行与观察 | user-confirmed run | workflow_board.html | 状态来自 runtime truth |
| UX-04 | 工位产物查看 | Artifact Report | artifacts.html | 输入输出与 lineage 可见 |
| UX-05 | 质量监控 | Quality Report | quality.html | 质量问题可定位 |
| UX-06 | 局部失败修复与重跑 | Mission Console / Thin Web | new attempt、stale 下游 | user_confirmed，旧 attempt 保留 |
| UX-07 | 治理证据链审查 | Evidence Report | evidence.html | Evidence 只读、不可伪造 |
| UX-08 | 串行多 Agent 视频工作流 | V4.3 scenario | video report | 工位可配置、产物可见 |
| UX-09 | 并行多 Agent 罗马广场 | V4.4 scenario | persona reports | 并行观点、归因汇总 |
| UX-10 | 长时工程任务工作流 | V4.5 scenario | durable task board | 刷新恢复、阶段产物、人工确认 |
| UX-11 | Agent Workflow Builder | V4.6 scenario | workflow draft / repair proposal | Agent 不自动执行 |

## 3. 全局断言

所有路径必须满足：

```text
source=agent cannot execute mutation
durable mutation requires user_confirmed=true
EventBridge only triggers refresh
WorkflowSpec cannot mutate runtime truth
Drawio is visualization only
HTML Report is read-only
Browser does not call /v1/rpc
Browser does not call /v1/events/subscribe
No token/raw payload leakage
No false-green claims
```

## 4. Forbidden Claims

任何路径、报告、completion note 都不得出现：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

## 5. UX-01 自然语言创建工作流

### 用户动作

```text
用户输入：创建一个递归总结 Desktop/技术分享 的 Markdown 工作流。
```

### 期望输出

```text
WorkflowSpec draft
schema validation result
workflow diff
risk summary
available actions
```

### PASS 条件

```text
WorkflowSpec 生成。
Diff 可见。
Agent 不自动 apply。
用户确认前 runtime 不变。
```

## 6. UX-02 工作流结构可视化

### 期望输出

```text
workflow.drawio
workflow_status.drawio
artifact_lineage.drawio
```

### PASS 条件

```text
drawio XML valid。
包含 expected nodes / edges。
不包含 token / raw payload。
不可作为 runtime truth。
```

## 7. UX-03 工作流运行与观察

### 期望输出

```text
workflow_board.html
station_detail.html
```

### PASS 条件

```text
运行必须 user_confirmed。
工作流状态可见。
每个 station 状态可见。
HTML 只读。
```

## 8. UX-04 工位产物查看

### 期望输出

```text
artifacts.html
artifact_lineage.drawio
```

### PASS 条件

```text
每个 station output 可见。
Artifact lineage 可还原。
不泄露 raw artifact content，除非显式允许。
```

## 9. UX-05 质量监控

### 期望输出

```text
quality.html
quality_report.json
```

### PASS 条件

```text
quality status 可见。
failed/warning 可定位到 station / artifact。
quality report 不改变 runtime state。
```

## 10. UX-06 局部失败修复与重跑

### 期望输出

```text
rerun_history.drawio
new attempt
stale downstream state
```

### PASS 条件

```text
rerun 必须 user_confirmed。
source=agent 不能 rerun。
旧 attempt 保留。
下游 stale 可见。
```

## 11. UX-07 治理证据链审查

### 期望输出

```text
evidence.html
operation-evidence.json
```

### PASS 条件

```text
proposal_id / handoff_id / user_confirmed / runtime_result_ref 可见。
Evidence panel 只读。
不可直接执行 Apply / Publish / Approve / Reject / Run。
```

## 12. UX-08 串行多 Agent 视频工作流

### PASS 条件

```text
编剧、分镜、文案、剪辑计划、质量审查、发布准备工位存在。
每个工位有 artifact。
至少一个中间工位可重跑。
下游 stale 可见。
```

## 13. UX-09 并行多 Agent 罗马广场

### PASS 条件

```text
至少 3 个 persona agent 并行产出 artifact。
存在 cross-inspiration edge。
Synthesis 输出包含观点归因。
Contradiction Review 记录分歧与风险。
```

## 14. UX-10 长时工程任务工作流

### PASS 条件

```text
11 个工程阶段可见。
每个阶段有 artifact。
代码检视 / E2E / 人工确认可见。
失败阶段可重跑。
刷新恢复通过。
```

## 15. UX-11 Agent Workflow Builder

### PASS 条件

```text
Agent 追问需求。
Agent 生成 workflow draft。
Agent 解释 plan。
Agent 生成 repair proposal。
Agent 不 auto apply / publish / run / rerun。
```

## 16. 验收输出结构

```text
docs/design/V4.x/evidence/unified-experience/
  UX-01/
  UX-02/
  ...
  UX-11/
  result-summary.md
```

每个目录包含：

```text
transcript.txt
workflow.yaml 或 scenario_spec.json
*.drawio
*.html
runtime-result.json
evidence.json
screenshots/ 可选
network-log.json 可选
console-errors.json 可选
```
