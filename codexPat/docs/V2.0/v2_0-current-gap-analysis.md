# V2.0 Current Gap Analysis

文档状态：V2.0 planning baseline；Phase 2.1 complete；Phase 2.2 complete；Phase 2.3 complete；Phase 2.4 complete；final acceptance passed。  
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

- Codex / Claude Code instruction template 已落地。
- `petctl` recipes 已覆盖常见开发任务。
- shell / Node 示例已可复制运行。
- 设置页 diagnostics 已打磨为只读运行状态面板。
- CSS 占位猫体验已完成 polish，8 个状态更可区分且保持低打扰。
- README、doctor、troubleshoot、macOS local unsigned app 分发准备已完成。
- V2.0 final acceptance report 已通过。

## 3. 差距矩阵

| Gap | 当前状态 | V2.0 目标 | 阶段 |
| --- | --- | --- | --- |
| 文档基线 | V1.0 已归档，活动文档仍在 docs 根层。 | `docs/V2.0` 独立说明基线、计划、验收、边界和 gap。 | Phase 2.0 |
| Codex 接入 | 已有 HTTP/petctl 能力，已新增 Codex instruction template。 | 后续如需验证真实 Codex 工作流，应单独验收；当前不声明 Codex integration verified。 | Phase 2.1 complete |
| Claude Code 接入 | 已有 HTTP/petctl 能力，已新增 Claude Code instruction template。 | 后续如需验证真实 Claude Code 工作流，应单独验收；当前不声明 Claude Code integration verified。 | Phase 2.1 complete |
| recipes | 已新增 `docs/reference/petctl-recipes.md`。 | 后续可在 settings 中增加复制命令入口。 | Phase 2.1 complete |
| 示例 | 已新增 shell / Node 示例。 | 后续可补充更多语言示例，但不新增 SDK。 | Phase 2.1 complete |
| settings diagnostics | 已完成 runtime health、sound、accepted/rejected events 和 quick commands 分区展示。 | 后续只做视觉细节打磨，不引入通知中心或日志数据库。 | Phase 2.2 complete |
| 猫咪体验 | 已完成 CSS 占位猫 polish；8 个状态肉眼可区分，拖拽优先，窗口不抖动。 | 后续仍不引入 Rive/Live2D/3D；如需资产系统单独立项。 | Phase 2.3 complete |
| 快速部署 | 已完成 README quick start、developer setup、network mirrors、troubleshooting、macOS local distribution 和 release boundary 文档。 | 后续如需正式发布，需签名、公证、安装器和发布流水线。 | Phase 2.4 complete |
| Final acceptance | `docs/V2.0/v2_0-final-acceptance-report.md` status 为 passed。 | 当前允许声明 V2.0 ready，但不扩大到真实 Codex/Claude 集成、Windows、签名发布或 MCP/USB。 | Final acceptance passed |
| Windows | 未做 Windows smoke。 | V2.0 仍不声明 Windows ready，仅保留后续计划。 | 后续 |
| MCP / USB | 未实现。 | V2.0 仍不实现，仅保留后续扩展方向。 | 后续 |

## 4. 允许声明

当前可以声明：

```text
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
```

同时仍可声明：

```text
V2.0 Phase 2.1 complete: local workflow integration templates and petctl recipes ready.
```

当前 Phase 2.2 可声明：

```text
V2.0 Phase 2.2 complete: settings diagnostics polish ready.
```

当前 Phase 2.3 可声明：

```text
V2.0 Phase 2.3 complete: CSS placeholder cat experience polish ready.
```

当前 Phase 2.4 可声明：

```text
V2.0 Phase 2.4 complete: macOS distribution readiness and user onboarding docs ready.
```

V2.0 ready 的依据是 `docs/V2.0/v2_0-final-acceptance-report.md`，其 status 为 `passed`。

## 5. 禁止声明

V2.0 不得声明：

```text
Codex integration verified
Claude Code integration verified
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
