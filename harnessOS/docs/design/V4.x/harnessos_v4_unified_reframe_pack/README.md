# HarnessOS V4 重新收口规划包

本文档包用于把当前 HarnessOS V4.x 已完成的 Headless-first dev/local 路线重新整理为一套统一、可继续执行的产品与工程计划。

## 当前事实基线

根据当前 Codex 汇总与阶段 completion note，项目已完成：

- V4.1 本地递归 Markdown 总结工作流 MVP
- V4.2 Headless Interaction Pivot + Controlled Runtime MVP
- V4.3 串行多 Agent 视频工作流 MVP
- V4.4 并行多 Agent 讨论工作流 MVP
- V4.5 长时工程工作流 MVP
- V4.6 Governed Agent Workflow Builder UX

当前可以声明：

```text
V4.6 complete: governed Agent workflow builder UX ready for dev/local validation.
```

仍不能声明：

```text
Agent executor ready
controlled executor ready
production-ready external app support
complete Workflow Studio ready
full multi-Agent orchestration ready
complete AgentTalkWindow ready
autonomous workflow editing ready
```

## 本次重新调整的核心结论

当前不应继续把 V4 主线理解为“完整 Web 低代码 Studio”。

新的 V4 目标形态应收敛为：

```text
Headless Workflow Core
+ Mission Console / TUI / Command Palette
+ Workflow Blueprint / Drawio
+ Runtime Report / HTML Report
+ Thin Review Console
+ Experience State Machine
+ Interaction Orchestrator
+ Agent Policy Layer
+ Evidence Chain
```

也就是说，V4 的核心不是“高保真低代码前端”，而是：

```text
用户能通过自然语言或命令定义工作流；
系统能生成可审查 WorkflowSpec；
用户能看到结构、状态、产物、质量和风险；
用户能确认运行、局部重跑、修复；
系统能保留完整治理证据链；
这些能力能被 TUI、Drawio、HTML Report、Thin Web Console 和未来业务 App 共同消费。
```

## 文件清单

| 文件 | 用途 |
|---|---|
| `01_v4_reframed_development_plan.md` | 新的 V4 开发及验收计划。 |
| `02_v4_reframed_prd.md` | 修改后的 V4 PRD，面向目标形态和用户体验。 |
| `03_target_architecture_and_interaction_model.md` | 新目标架构、交互层、中间层、状态机说明。 |
| `04_acceptance_matrix.md` | 以体验路径为中心的验收矩阵。 |
| `05_repo_document_update_plan.md` | 对现有 docs 目录的文档更新建议。 |
| `06_codex_plan_prompt.md` | 可直接给 Codex Plan 模式使用的提示词。 |

## 建议使用方式

1. 先将 `06_codex_plan_prompt.md` 投入 Codex Plan 模式。
2. 让 Codex 先落盘文档，不要直接改代码。
3. 让 Codex 输出待修改文件列表和 diff plan。
4. 人工确认新的 PRD 与开发计划后，再进入实施。
