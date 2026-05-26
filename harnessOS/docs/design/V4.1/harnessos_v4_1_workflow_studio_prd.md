# HarnessOS Workflow Studio PRD v0.2

> 用于 Stitch 重新生成产品原型图。本文档重点描述 HarnessOS 当前阶段应该呈现的低代码工作流产品体验，而不是完整技术实现文档。

---

## 1. 产品定位

HarnessOS Workflow Studio 是一个面向 AI 工作流搭建、运行和治理的低代码平台。用户可以通过自然语言向 Agent 描述需求，也可以通过节点库和画布手动搭建流程。系统会把用户需求转化为可审查的工作流草案、Patch Diff 和运行计划，最终由用户显式确认后发布并运行。

当前产品不应被设计成普通聊天助手，也不应只像传统 Dashboard。它应该是一个 **低代码工作台 + Agent 工作流助手 + 运行看板 + 治理审计面板** 的组合产品。

第一阶段原型重点不追求完整生产能力，而是优先证明：用户可以用自然语言生成一个基础线性工作流，并完成本地 Markdown 文件夹递归总结任务。

---

## 2. MVP 核心目标

### 2.1 一句话目标

用户输入一句话：

> 帮我创建一个工作流，读取 Desktop/技术分享 文件夹，递归解析里面的 md 文件，并为每个子文件夹生成单独总结，最后生成总览总结。

系统可以生成工作流草案，用户确认后运行，最终生成每个子文件夹的总结、总览总结和质量报告。

### 2.2 本阶段必须突出

1. 自然语言驱动工作流生成。
2. 节点库 + 画布搭建线性工作流。
3. Agent 助手可以解释、生成草案、提出修复建议。
4. 所有持久变更必须用户确认，不允许 Agent 自动执行。
5. 工作流运行过程可见：节点状态、产物、质量、错误、重跑、证据链。
6. 交互体验应简洁、现代、低代码风格，接近 ComfyUI / Dify 的工作台感，但更强调治理、可追踪和用户确认。

---

## 3. 目标用户

| 用户类型 | 核心需求 |
| --- | --- |
| AI 应用开发者 | 快速搭建和调试 AI 工作流，不想从零写编排代码。 |
| 产品经理 / 解决方案顾问 | 用自然语言和可视化方式设计业务流程，验证方案可行性。 |
| 内容生产人员 | 用工作流处理文档、知识、视频、报告等内容生产任务。 |
| 客户成功 / 交付团队 | 快速为客户搭建定制化工作流并展示过程证据。 |
| 内部研发团队 | 将不同业务能力沉淀为可复用的工作流节点和 Agent 工位。 |

---

## 4. 首版 MVP 场景

### 4.1 场景名称

**本地知识文件夹递归总结工作流**

### 4.2 输入

用户选择或授权一个本地文件夹：

```text
Desktop/技术分享
```

如果真实桌面目录不可用，测试环境使用 fixture：

```text
tests/fixtures/desktop/技术分享/
  AgentOS/01-架构.md
  AgentOS/02-工作流.md
  前端低代码/画布设计.md
  前端低代码/节点库.md
  项目复盘/周报.md
  未支持/test.pdf
  空文件夹/
```

### 4.3 输出

```text
技术分享_总结结果/
  总览总结.md
  文件清单.json
  quality_report.json
  子文件夹总结/
    AgentOS_总结.md
    前端低代码_总结.md
    项目复盘_总结.md
```

### 4.4 工作流节点

```text
文件夹输入
 -> 递归文件扫描
 -> Markdown 文件过滤
 -> Markdown 内容解析
 -> 子文件夹分组
 -> 子文件夹总结 Agent
 -> 总目录总结 Agent
 -> 质量检查 Agent
 -> 输出总结文件
```

### 4.5 每个节点的作用

| 顺序 | 节点名称 | 类型 | 作用 | 输出 |
| --- | --- | --- | --- | --- |
| 1 | 文件夹输入 | Input | 用户授权读取目标目录 | folder_ref |
| 2 | 递归文件扫描 | Tool | 遍历子文件夹和文件 | file_tree.json |
| 3 | Markdown 文件过滤 | Tool | 只保留 .md / .markdown 文件 | md_file_list.json |
| 4 | Markdown 内容解析 | Tool | 提取标题、正文、层级 | parsed_docs.json |
| 5 | 子文件夹分组 | Tool | 按子文件夹归类文档 | grouped_docs.json |
| 6 | 子文件夹总结 Agent | Agent | 为每个子文件夹生成总结 | folder_summaries/ |
| 7 | 总目录总结 Agent | Agent | 汇总所有子总结 | 总览总结.md |
| 8 | 质量检查 Agent | Reviewer | 检查缺失、空文件夹、不支持文件 | quality_report.json |
| 9 | 输出总结文件 | Output | 生成可下载结果包 | output_package |

---

## 5. 核心体验线路

## 5.1 体验线路 A：自然语言创建工作流

### 用户操作

用户在右侧 Agent 助手输入：

```text
帮我创建一个工作流，读取 Desktop/技术分享 文件夹，递归解析里面的 md 文件，并为每个子文件夹生成单独总结，最后生成总览总结。
```

### 系统反馈

Agent 不应直接执行，而应展示：

1. 工作流草案名称。
2. 9 个节点列表。
3. 节点之间的线性连接关系。
4. 需要用户确认的事项：是否授权读取文件夹、是否只处理 Markdown、是否生成 Markdown 输出。
5. “查看 Diff”和“应用到草稿”入口。

### 关键要求

- Agent 不能自动扫描文件夹。
- Agent 不能自动 Apply。
- Agent 不能自动 Publish。
- Agent 不能自动 Run。
- 所有持久操作必须由用户确认。

---

## 5.2 体验线路 B：调试文件夹扫描

### 用户操作

用户点击“文件夹输入”节点，在右侧 Inspector 中填写或选择：

```text
Desktop/技术分享
```

然后点击：

```text
授权读取
调试扫描
```

### 系统反馈

扫描结果区域展示：

- 文件夹树。
- 总文件数。
- Markdown 文件数。
- 子文件夹数。
- 不支持文件数。
- 空文件夹数量。

### 关键要求

- Debug Scan 只做预览，不生成总结。
- 不读取未授权目录。
- 不把 raw Markdown 内容直接展示在页面里。
- 不支持文件应进入质量报告。

---

## 5.3 体验线路 C：发布并运行工作流

### 用户操作

1. 用户点击“发布版本”。
2. 二次确认。
3. 用户点击“运行工作流”。
4. 进入运行看板。

### 系统反馈

运行看板展示 9 个节点状态：

```text
pending / running / completed / failed / waiting_approval
```

每个节点卡片展示：

- 节点名称。
- 当前状态。
- 输入 artifact。
- 输出 artifact。
- 耗时。
- 质量状态。
- 错误状态。

---

## 5.4 体验线路 D：查看总结产物

### 用户操作

用户打开底部 “Artifacts / 产物” 面板。

### 系统反馈

展示生成文件：

```text
AgentOS_总结.md
前端低代码_总结.md
项目复盘_总结.md
总览总结.md
quality_report.json
```

每个总结文件可预览。

### 每个子文件夹总结内容

```text
# 子文件夹名称

## 1. 内容概览
## 2. 核心主题
## 3. 关键知识点
## 4. 重要文件列表
## 5. 可用于技术分享的材料
## 6. 待补充 / 不完整内容
## 7. 引用文件
```

### 总览总结内容

```text
# 技术分享文件夹总览

## 1. 文件夹结构概览
## 2. 主要技术主题
## 3. 每个子文件夹摘要
## 4. 推荐技术分享顺序
## 5. 可直接用于 PPT 的内容
## 6. 未处理文件 / 异常文件
## 7. 生成时间与统计信息
```

---

## 5.5 体验线路 E：质量检查与异常处理

### 质量报告需要展示

- 是否所有子文件夹都生成总结。
- 是否存在空文件夹。
- 是否存在不支持文件。
- 是否存在解析失败文件。
- 是否存在低质量总结。
- 是否建议用户重跑某个节点。

### 示例

```json
{
  "status": "warning",
  "unsupported_files": ["未支持/test.pdf"],
  "empty_folders": ["空文件夹/"],
  "missing_summaries": [],
  "suggestions": ["空文件夹已记录，无需生成正式总结"]
}
```

---

## 5.6 体验线路 F：失败重跑与恢复

### 用户操作

当 Markdown 解析节点失败时：

1. 用户点击失败节点。
2. 查看错误原因。
3. 点击“重跑当前节点”。
4. 用户确认。

### 系统反馈

- 创建新的 attempt。
- 旧 attempt 和旧错误保留。
- 新 attempt 开始运行。
- 下游节点等待新结果。

### 刷新恢复

用户刷新页面后：

- 当前 workflow instance 仍可恢复。
- 已完成节点仍显示 completed。
- 已生成 artifact 仍可查看。
- 失败节点仍显示错误。

---

## 5.7 体验线路 G：Agent 调试和修复建议

### 用户输入

```text
为什么这个文件夹没有生成总结？
```

Agent 应只读解释，不执行任何操作。

### 用户继续输入

```text
帮我修复，让空文件夹也生成一份无内容总结。
```

Agent 应生成 Patch Proposal，例如：

```text
修改节点：子文件夹总结 Agent
修改内容：当子文件夹无有效 Markdown 文件时，生成“无内容”占位总结。
状态：等待用户确认
```

### 关键要求

- Agent 不能自动 Apply。
- Agent 不能自动重跑。
- Agent 不能自动修改文件。
- 用户确认后才应用 Patch。

---

## 5.8 体验线路 H：治理审计

治理审计面板展示：

```text
Agent 建议
 -> Handoff
 -> 用户确认
 -> Operation Panel 执行
 -> Runtime 结果
 -> Evidence 记录
```

### 必须展示

- proposal_id。
- handoff_id。
- user_confirmed。
- operation_type。
- runtime_result_ref。
- risk_flags。
- policy_decision。
- correlation_id。
- redaction_status。

### 禁止出现

```text
Apply
Publish
Approve
Reject
Execute
Run
自动应用
自动发布
Agent 已执行
Agent 已发布
```

治理审计面板只读。

---

## 6. 信息架构

## 6.1 顶部栏

- 产品名称：HarnessOS Workflow Studio。
- 当前项目名称。
- 当前工作流名称。
- Draft / Version 状态。
- 运行状态。
- 保存草稿。
- 发布版本。
- 运行工作流。
- 搜索。
- 通知。
- 用户头像。

## 6.2 左侧节点库

节点分类：

```text
输入节点
文件处理节点
AI Agent 节点
质量治理节点
审批节点
输出节点
```

首版节点：

```text
文件夹输入
递归文件扫描
Markdown 文件过滤
Markdown 内容解析
子文件夹分组
子文件夹总结 Agent
总目录总结 Agent
质量检查 Agent
输出总结文件
```

## 6.3 中央画布

画布风格：

- 浅色背景。
- 点阵网格。
- 白色卡片节点。
- 蓝紫色高亮。
- 清晰连线。
- 节点状态 Badge。
- Ghost / Pending 节点样式。
- 可折叠侧栏。
- 画布保持主视觉中心。

## 6.4 右侧面板

Tabs：

```text
Agent 助手
节点配置
Patch Diff
运行详情
治理审计
```

Agent 助手默认优先显示。

## 6.5 底部运行面板

Tabs：

```text
Events
Trace
Artifacts
Quality
Approval
Patch
Evidence
```

---

## 7. 关键页面原型要求

## 7.1 首页 / Workflow List

展示：

- 最近工作流。
- 新建工作流按钮。
- 本地知识总结模板卡片。
- 视频创作流水线模板卡片。
- 长时工程任务模板卡片。

重点突出：

```text
用自然语言生成工作流
从模板开始
查看最近运行
```

## 7.2 Workflow Studio 页面

这是 Stitch 需要重点生成的页面。

页面结构：

```text
顶部栏
左侧节点库
中央画布
右侧 Agent 助手 / Inspector
底部运行面板
```

画布中展示“技术分享资料递归总结工作流”的 9 个节点。

右侧 Agent 对话框中展示用户输入和 Agent 生成的工作流草案。

底部展示运行事件和产物。

## 7.3 调试扫描状态页

展示：

- 文件夹授权状态。
- 文件树。
- 文件数量统计。
- Markdown 文件数量。
- 不支持文件数量。
- 空文件夹数量。
- “开始运行”按钮。

## 7.4 运行中页面

展示：

- 节点状态动态变化。
- 当前运行节点高亮。
- 已完成节点绿色。
- 失败节点红色。
- waiting 状态黄色。
- 右侧显示当前节点详情。
- 底部显示 event feed。

## 7.5 产物查看页面

展示：

- Artifact 列表。
- Markdown 总结预览。
- 总览总结预览。
- 质量报告预览。
- 下载结果包按钮。

## 7.6 治理审计页面

展示：

- 操作证据链时间线。
- Agent 建议。
- 用户确认。
- Runtime 结果。
- 风险标记。
- 策略决策。
- 只读状态。

---

## 8. 视觉风格要求

建议给 Stitch 的视觉关键词：

```text
现代 SaaS
低代码工作台
ComfyUI-like canvas
Dify-like clean layout
浅色主题
蓝紫色高亮
卡片式节点
细线连接
可折叠面板
中文界面
专业但简洁
信息密度适中
强调 Agent 辅助
强调用户确认
强调运行状态和产物可见
```

不要生成：

```text
深色黑客风
复杂运维后台
纯聊天界面
传统表单后台
过度科幻风
过多装饰插画
```

---

## 9. 核心交互规则

1. Agent 只能生成建议、解释、Patch Proposal、Handoff。
2. Agent 不能自动 Apply、Publish、Run、Rerun。
3. 用户确认前，工作流草案只显示为 ghost / pending。
4. Debug Scan 不生成总结。
5. Apply 后才正式写入草稿。
6. Publish 后才生成可运行版本。
7. Run 必须由用户确认。
8. EventBridge 只触发刷新，不构造状态。
9. Governance Evidence 面板只读。
10. 浏览器不能直接访问 `/v1/rpc` 或 `/v1/events/subscribe`。

---

## 10. 主要验收标准

## 10.1 Agent 生成工作流

- 用户输入需求后，Agent 生成工作流草案。
- 画布显示 9 个 pending 节点。
- 不自动扫描文件。
- 不自动应用草稿。

## 10.2 文件夹调试扫描

- 可授权读取 `Desktop/技术分享`。
- 可显示文件树和统计。
- 可记录 unsupported 文件。
- 可记录空文件夹。
- 不生成总结。

## 10.3 工作流运行

- Publish 和 Run 都需要用户确认。
- Pipeline Board 显示 9 个节点。
- 节点状态可变化。
- Artifacts 里有 3 个子文件夹总结、1 个总览总结和 1 个质量报告。

## 10.4 失败重跑

- 失败节点显示 error。
- 用户确认后重跑。
- 新 attempt 创建。
- 旧 error 保留。

## 10.5 治理证据

- Evidence chain 可见。
- 包含 proposal、handoff、user_confirmed、runtime result。
- 面板只读。

---

## 11. 不在本阶段支持

```text
PDF / DOCX / PPTX 解析
生产文件系统权限模型
完整 Agent executor
controlled executor
多 Agent 视频工作流
并行 Agent 讨论
长时工程任务工作流
生产级 OAuth / SSO
生产级多租户控制台
production-ready external app support
```

---

## 12. Stitch 生成原型时请重点表现

1. 用户在 Agent 助手输入自然语言需求。
2. Agent 生成工作流草案。
3. 画布出现 9 个 ghost 节点。
4. 用户点击查看 Diff 和应用到草稿。
5. 用户配置文件夹路径并点击调试扫描。
6. 页面显示文件树和扫描统计。
7. 用户发布并运行工作流。
8. 运行看板显示节点状态变化。
9. 产物面板显示 Markdown 总结文件。
10. 质量面板显示 unsupported file 和 empty folder。
11. 治理审计面板显示用户确认链路。

---

## 13. 推荐 Stitch Prompt

请基于以下描述生成一组高保真中文 SaaS 原型图：

```text
为 HarnessOS Workflow Studio 设计一个低代码 AI 工作流平台界面。界面采用浅色现代 SaaS 风格，类似 ComfyUI 的画布工作台和 Dify 的简洁产品体验。核心场景是“本地知识文件夹递归总结工作流”：用户在右侧 Agent 助手中输入“帮我创建一个工作流，读取 Desktop/技术分享 文件夹，递归解析里面的 md 文件，并为每个子文件夹生成单独总结，最后生成总览总结”。

请生成以下页面：
1. Workflow Studio 主页面：顶部栏、左侧节点库、中央画布、右侧 Agent 助手、底部运行面板。画布中显示 9 个工作流节点：文件夹输入、递归文件扫描、Markdown 文件过滤、Markdown 内容解析、子文件夹分组、子文件夹总结 Agent、总目录总结 Agent、质量检查 Agent、输出总结文件。
2. Agent 生成工作流草案页面：右侧聊天框显示用户需求和 Agent 生成的工作流计划，画布节点为 ghost / pending 状态，显示“查看 Diff”“应用到草稿”。
3. 文件夹调试扫描页面：选中文件夹输入节点，右侧 Inspector 显示路径 Desktop/技术分享、授权读取按钮、调试扫描按钮、文件树、总文件数、Markdown 文件数、不支持文件数、空文件夹数。
4. 工作流运行页面：Pipeline Board 显示 9 个节点的 running / completed / failed / waiting 状态，底部 Events 面板展示运行日志。
5. 产物查看页面：Artifacts 面板展示 AgentOS_总结.md、前端低代码_总结.md、项目复盘_总结.md、总览总结.md、quality_report.json，并展示 Markdown 预览。
6. 治理审计页面：展示 Agent 建议 -> Handoff -> 用户确认 -> Runtime 结果 -> Evidence 的只读证据链。

视觉要求：中文界面、浅色背景、白色卡片节点、蓝紫色高亮、清晰连线、点阵画布、可折叠左右面板、专业简洁、不要深色黑客风，不要传统表单后台，不要纯聊天产品。

交互边界请在界面文案中体现：Agent 只生成建议，不会自动执行；应用草稿、发布版本、运行工作流都需要用户确认；治理审计面板只读。
```

---

## 14. 原型图建议数量

建议 Stitch 生成 6 张图：

1. 工作流 Studio 总览图。
2. Agent 生成草案图。
3. 文件夹授权与调试扫描图。
4. 工作流运行看板图。
5. 产物与质量报告图。
6. 治理审计证据链图。
