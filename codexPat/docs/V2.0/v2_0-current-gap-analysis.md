# V2.0 Current Gap Analysis

文档状态：V2.0 planning baseline。  
配套图：`v2_0_current_gap_analysis.drawio`。

## 1. 当前状态

V1.0 macOS-first MVP 已完成：

- 桌面猫可常驻、透明、无边框、置顶、可拖拽。
- 低打扰状态机和 CSS 占位状态动画已完成。
- 本地 HTTP API、PetEvent JSON Schema、token、白名单、rate limit 已完成。
- diagnostics 和 accepted/rejected 摘要已完成。
- `petctl notify` 已完成。
- 内置安全声音反馈已完成。

## 2. V2.0 目标状态

V2.0 目标是让真实开发工作流更容易稳定接入：

- Codex / Claude Code instruction template 可用。
- `petctl` recipes 覆盖常见开发任务。
- shell / Node 示例可复制运行。
- 设置页 diagnostics 更易理解。
- README、doctor、troubleshoot、macOS 分发准备更完整。
- CSS 猫咪体验更稳定、更有状态区分度。

## 3. 差距矩阵

| Gap | 当前状态 | V2.0 目标 | 阶段 |
| --- | --- | --- | --- |
| 文档基线 | V1.0 已归档，活动文档仍在 docs 根层。 | `docs/V2.0` 独立说明基线、计划、验收、边界和 gap。 | Phase 2.0 |
| Codex 接入 | 只有 HTTP/petctl 能力，无 Codex instruction template。 | 提供 Codex 本地工作流模板。 | Phase 2.1 |
| Claude Code 接入 | 只有 HTTP/petctl 能力，无 Claude Code instruction template。 | 提供 Claude Code 本地工作流模板。 | Phase 2.1 |
| recipes | `petctl` 命令可用，但场景化 recipes 不完整。 | 覆盖测试、构建、长任务、失败、需要输入。 | Phase 2.1 |
| 示例 | 暂无 shell / Node 示例。 | 提供可复制的本地脚本示例。 | Phase 2.1 |
| settings diagnostics | 已可观察，但偏底层。 | 更清楚展示健康、拒绝原因、声音决策和测试命令。 | Phase 2.2 |
| 猫咪体验 | CSS 占位状态已可用。 | 状态更好区分，窗口不抖动，低打扰不破坏。 | Phase 2.3 |
| 快速部署 | 已有开发和发布说明。 | 新用户能更快完成 macOS 本地部署和排障。 | Phase 2.4 |
| Windows | 未做 Windows smoke。 | V2.0 仍不声明 Windows ready，仅保留后续计划。 | 后续 |
| MCP / USB | 未实现。 | V2.0 仍不实现，仅保留后续扩展方向。 | 后续 |

## 4. 允许声明

V2.0 全部验收通过后可声明：

```text
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
```

## 5. 禁止声明

V2.0 不得声明：

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

