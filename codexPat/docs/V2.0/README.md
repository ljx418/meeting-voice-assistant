# agent-desktop-pet V2.0

V2.0 定位为 Developer Workflow Integration Release：从“本地可用的 Agent 状态桌宠 MVP”升级为“可被真实开发工作流稳定接入的 Agent 状态伙伴”。

## 文档索引

- [Docs Map：文档分层与维护规则](../README.md)
- [V2.0 实现基线](v2_0-baseline.md)
- [V2.0 开发计划](v2_0-development-plan.md)
- [V2.0 验收计划](v2_0-acceptance-plan.md)
- [V2.0 范围边界](v2_0-scope-boundaries.md)
- [V2.0 工作流接入](v2_0-workflow-integration.md)
- [V2.0 当前差距分析](v2_0-current-gap-analysis.md)
- [V2.0 当前差距图](v2_0_current_gap_analysis.drawio)
- [V2.0 最终验收报告](v2_0-final-acceptance-report.md)

## 基线说明

V2.0 以 V1.0 macOS-first MVP 为基线。V1.0 已完成本地桌面壳、低打扰状态机、localhost HTTP API、PetEvent 校验、diagnostics、`petctl notify` 和安全声音反馈。

V2.0 不重做 V1.0 架构，不扩大为通知中心，也不提前引入 MCP、USB、Windows ready、Live2D/Rive/3D、照片自定义、自动更新或正式签名。

当前已完成 Phase 2.1、2.2、2.3、2.4，并已通过 final acceptance report。

## 允许声明

当前可以声明：

```text
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
```

## 禁止声明

V2.0 不允许声明：

```text
MCP server ready
USB hardware ready
Windows ready
cross-platform ready
production signed release ready
auto update ready
Live2D/Rive/3D ready
photo customization ready
team collaboration hub ready
```
