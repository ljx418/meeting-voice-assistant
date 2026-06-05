# V7 Target PRD

文档状态：V7 PRD baseline / V7-3 implementation planning entry。本文定义 V7 的目标产品规格。

当前进展：

```text
V7-0 planning hardening 已完成 review baseline。
V7-1 Small Studio Control Plane 已完成 repo-backed projection baseline。
V7-2 Explainable Mission TUI 已完成 transcript-only pilot baseline。
V7-3 仍需实现真实 natural-language -> workflow spec -> blueprint -> user-confirmed run -> evidence 链路。
V7-4 仍需在 V7-3 证据存在后执行最终验收。
```

## 1. Product Positioning

V7 不追求完整企业 GA，也不回到完整 Web 低代码 Studio 主线。V7 的定位是：

```text
Small Studio Production Pilot
+ Explainable Mission TUI
+ Governed Workflow Run Experience
```

目标是让一个小型工作室能在可审计边界内使用 HarnessOS：

```text
管理 workspace / project / app
配置 provider 和 credential ref
用自然语言创建 workflow
查看 Workflow Blueprint
人工确认后运行
查看 Runtime Report / Quality / Evidence Chain / Audit Export
通过 Review Console 处理失败、修复和重跑 handoff
```

## 2. Target Users

| User | Goal | V7 Experience |
| --- | --- | --- |
| Studio Admin | 配置工作室、provider、凭证、配额和成员 | 使用 Product Console / CLI 查看控制面和审计证据 |
| Workflow Operator | 用自然语言创建和运行工作流 | 使用 Mission TUI 输入目标、查看状态线、确认运行 |
| Reviewer | 审查质量、证据和失败修复 | 使用 Review Console / Evidence Chain 做复核 |
| External App Developer | 在小工作室边界内接入 approved API | 使用 app registration、domain、quota 和 SDK guard |

## 3. Main User Journey

```text
用户打开 harness tui
 -> 输入“递归总结 Desktop/技术分享 下的 Markdown 技术文档”
 -> Mission TUI 捕获 IntentCaptured
 -> 生成 WorkflowSpec 和 Diff
 -> 展示 Workflow Blueprint / Drawio link
 -> 展示 Available Actions 和 Forbidden Action Reasons
 -> 用户确认运行
 -> Controlled Runtime 执行
 -> Runtime Report 展示 station 状态
 -> Artifact / Quality / Evidence Chain 可查看
 -> Review Console 给出失败解释或 repair proposal
 -> 所有 durable action 仍需 user_confirmed=true
```

## 4. Capability Groups

### Small Studio Control Plane

V7-1 负责：

```text
StudioContext
Workspace / Project / App inventory
Role / Permission projection
Provider Profile
Credential Ref
Quota / Rate Limit
Audit source refs
```

### Explainable Mission TUI

V7-2 负责：

```text
harness tui
natural-language mission input
experience state timeline
available action resolver
forbidden action reason
blueprint / report / evidence links
```

### Workflow Creation And Run

V7-3 负责：

```text
WorkflowSpec / Diff generation
Workflow Blueprint projection
user-confirmed run
local Markdown technical document workflow
MiniMax or OpenAI-compatible provider evidence
Runtime Report
Review Console
Evidence Chain
```

当前缺口：

```text
V7-2 已能让用户输入自然语言并看到可解释状态线。
V7-2 不能被写成 runtime-backed workflow run。
V7-3 必须补齐真实 WorkflowSpec / Diff / Blueprint 生成、人工确认、受控运行和 Evidence Chain。
```

### Final Acceptance

V7-4 负责：

```text
final acceptance HTML dashboard
TUI transcript
Drawio blueprint
runtime evidence
quality report
claim scan
redaction scan
human acceptance summary
```

## 5. Success Criteria

V7 通过条件：

```text
Small Studio scope is auditable.
harness tui is a real command.
Natural-language mission input produces explainable state transitions.
WorkflowSpec / Diff / Blueprint / Runtime Report / Evidence Chain are cross-linked.
User confirmation is required before durable mutation.
source=agent direct durable mutation is denied.
Real local Markdown workflow can run with provider-backed summaries.
Evidence contains provider/model refs without raw prompt, raw content or token leakage.
Final HTML acceptance dashboard is generated.
No False Green scan passes.
```

V7-3 的关键产品验收：

```text
用户输入自然语言目标后，系统真实生成 workflow spec 和 diff。
用户确认前不执行 durable mutation。
系统能在授权路径内读取真实 Markdown 文件或等价 fixture。
系统能生成 provider-backed summaries，或在无 key 时明确 blocked/fallback，不伪装成 real runtime。
TUI、Blueprint、Runtime Report、Quality 和 Evidence Chain 互相可链接。
```

## 6. Non-Goals

V7 不证明：

```text
production ready
full production GA
enterprise auth ready
complete Workflow Studio ready
Agent executor ready
production controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```
