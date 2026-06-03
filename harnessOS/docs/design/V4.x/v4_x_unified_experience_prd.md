# HarnessOS V4.x Unified Experience PRD

文档状态：V4-U5A / V4-U5B 完成后的统一体验收口 PRD。

## 1. 当前事实基线

当前允许声明：

```text
V4-U5A complete: scenario evidence archive ready for review.
V4-U5B complete: experience state projection read-model ready for shared workflow heads.
```

当前仍不能声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

## 2. 产品定位

V4.x 不再把完整 Web 低代码 Studio 作为当前主线。新的主体验是：

```text
Headless Workflow Core
+ Mission Console
+ Workflow Blueprint
+ Runtime Report
+ Review Console
+ Evidence Chain
```

V4.x 的核心价值是让用户能用自然语言或命令定义工作流，看懂结构，确认运行，观察产物和质量，局部修复，并复盘证据链。

## 3. 主体验路径

```text
用户说目标
 -> Mission Console 捕获意图
 -> 生成 WorkflowSpec / Diff
 -> Workflow Blueprint 理解结构
 -> 用户确认
 -> Runtime Report 观察运行
 -> Review Console 做局部重跑 / 修复 / 确认
 -> Evidence Chain 审计复盘
```

## 4. 核心原则

1. WorkflowSpec 不是 WorkflowDraft / WorkflowVersion runtime truth。
2. Workflow Blueprint / Drawio 是只读可视化输出。
3. Runtime Report / HTML Report 是只读报告。
4. Review Console 只能发起用户确认后的受控操作。
5. Agent 只能 propose / explain / handoff / navigate。
6. Agent 不能 auto apply / publish / run / rerun。
7. Durable mutation 必须携带 `user_confirmed=true`。
8. EventBridge 只触发 refresh，不能构造 truth。
9. 所有 Head 必须共享 Experience State Machine 和 Report Schema。
10. Evidence Chain 是审计事实投影，不是执行入口。
11. Mission Console、Runtime Report、Review Console 和 Evidence Chain 必须共享 ExperienceStateProjection。
12. TUI / Command Palette 必须渲染 ExperienceStateProjection 状态线，不能维护独立真相。

## 5. 目标用户体验

用户应能完成以下任务：

1. 用 Mission Console 输入自然语言目标。
2. 看到系统生成的 WorkflowSpec、Diff、风险提示和可用动作。
3. 通过 Workflow Blueprint 理解 station、edge、artifact lineage 和 quality gate。
4. 用户确认后运行 dev/local workflow。
5. 通过 Runtime Report 查看 station 状态、artifact、quality、error、attempt history。
6. 失败时通过 Review Console 请求解释、生成修复 proposal、用户确认 rerun。
7. 通过 Evidence Chain 复盘 proposal、handoff、user_confirmed、runtime result 和 policy decision。

## 6. 非目标

当前统一体验收口不实现：

```text
完整 Web 低代码编辑器
Agent executor
production-ready controlled executor
production auth / tenant control plane
production filesystem permission model
production external app onboarding
autonomous workflow editing
```

## 7. 成功标准

V4.x unified experience 成功标准：

```text
用户能定义工作流。
用户能看懂工作流。
用户能确认并运行。
用户能看到每个工位状态和产物。
用户能在 dev/local 环境中实际启动本地技术文档解析工作流。
用户能获得真实 LLM-backed 的 Markdown 子文件夹总结和总览总结。
用户能对失败环节进行用户确认后的局部重跑或修复。
用户能查看质量、风险和证据链。
TUI / Drawio / HTML Report / Thin Web Console 共享同一状态模型。
Agent 不越权执行。
UX-08 / UX-09 / UX-10 在真实 multi-Agent runtime 前必须保持 deterministic_devlocal PARTIAL 或记录人工 proceed decision。
如果没有可用 LLM provider key，真实 LLM 文档总结能力必须标记 BLOCKED 或 fallback_demo_only，不能写成 PASS。
```
