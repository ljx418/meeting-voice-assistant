# V3.0 Multi-instance Codex Working Partner System

文档状态：V3.0 new mainline；V3.0 final acceptance passed for tested local Codex session scenarios。

V3.0 的定位是把单实例 Agent 状态猫升级为多实例 Codex 工作伙伴系统。

用户可能同时打开多个 Codex 窗口、终端会话或 workspace instance。V3.0 不读取 OS 级窗口句柄，而是把一个本地 Codex session / terminal tab / workspace instance 视为一个可绑定的工作实例。每个实例可以拥有一只独立桌面猫，并保留自己的名字、窗口位置、状态 runtime 和外观配置。

## Scope

V3.0 主线包含：

- Multi-instance Foundation。
- Instance-aware Event Routing。
- Codex Quick Attach。
- Multi-pet Manager UI。
- Asset Pack v1 + per-instance appearance。
- Multi-pet performance hardening。

V3.0 当前不做：

- Claude Code 完整验证。
- MCP server。
- Windows ready / cross-platform ready。
- USB。
- Rive / Live2D / 3D。
- 照片自定义。
- 正式签名、公证、自动更新。

## Documents

- [V3.0 Development Plan](v3_0-development-plan.md)
- [V3.0 Acceptance Plan](v3_0-acceptance-plan.md)
- [V3.0 Current Gap Analysis](v3_0-current-gap-analysis.md)
- [V3.0 Claim Matrix](v3_0-claim-matrix.md)
- [V3.0 Backlog](v3_0-backlog.md)
- [V3.0 Evidence Index](v3_0-evidence-index.md)
- [V3.0 Baseline Freeze Report](v3_0-baseline-freeze-report.md)
- [V3.0 Final Acceptance Report](v3_0-final-acceptance-report.md)
- [V3.0 Final Visual Acceptance Checklist](v3_0-final-visual-acceptance-checklist.md)

## Current Allowed Claims

```text
macOS-first MVP ready: local desktop agent status pet with HTTP + petctl integration and safe sound feedback.
V2.0 ready: local agent workflow integration and developer usability polish complete.
Third-party local HTTP contract smoke passed.
Codex local workflow integration verified for tested local Codex CLI smoke scenarios.
V3.0 Phase 3.1 complete: V2.x baseline frozen and complex integration backlog aligned.
Phase 3.2 complete: multi-instance pet foundation ready.
Phase 3.3 complete: instance-aware event routing ready.
Phase 3.4 complete: Codex quick attach and instance-scoped petctl routing ready.
Phase 3.5 complete: multi-pet manager UI ready.
Phase 3.6 complete: built-in asset pack v1 and per-instance appearance selection ready.
Phase 3.7 engineering hardening complete: multi-pet runtime limits and stability guards ready.
V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.
```

Phase 3.2 只证明 multi-instance pet foundation ready。Phase 3.3 只证明 HTTP instance-aware event routing ready。Phase 3.4 只证明 Codex quick attach 和 instance-scoped petctl routing ready。Phase 3.5 只证明 Multi-pet Manager UI ready，不代表通知中心、命令执行 UI 或 per-instance deep diagnostics ready。Phase 3.6 只证明内置 CSS Asset Pack v1 和每实例外观选择，不代表 Rive/Live2D/3D、照片自定义、用户上传或自定义资产包 ready。V3.0 ready 只覆盖 tested local Codex session scenarios，不代表所有 Codex workflow、OS-level window binding、MCP 或跨平台能力。

## Forbidden Claims

```text
all Codex workflows verified
unqualified multi-instance Codex verified beyond tested local scenarios
OS-level Codex window binding ready
per-instance queue ready
Claude Code integration verified
MCP ready
Windows ready
cross-platform ready
USB ready
Rive/Live2D/3D ready
photo customization ready
user asset upload ready
custom asset pack import ready
production signed release ready
auto update ready
```
