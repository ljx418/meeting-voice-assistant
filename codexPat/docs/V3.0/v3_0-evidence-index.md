# V3.0 Evidence Index

文档状态：new mainline evidence index；V3.0 final acceptance passed for tested local Codex session scenarios。

## Frozen Evidence Sources

| Evidence | Path | Status | What it proves | What it does not prove |
| --- | --- | --- | --- | --- |
| V2.0 final acceptance | `docs/V2.0/v2_0-final-acceptance-report.md` | passed | V2.0 workflow polish、macOS local unsigned app、HTTP + petctl + diagnostics + safe sound 收口通过。 | 不证明 Windows、MCP、USB 或 production release。 |
| V2.1 baseline audit | `docs/V2.1/v2_1-baseline-audit.md` | passed | 真实接入验证前的本地链路基线可用。 | 不证明真实第三方产品或 Claude Code hook。 |
| Third-party contract report | `docs/V2.1/third-party-agent-contract-report.md` | passed | curl / Node / Python local HTTP contract smoke、401/400/429、redaction 和 diagnostics 安全边界通过。 | 不证明真实第三方 agent 产品集成 verified。 |
| Codex smoke evidence | `docs/V2.1/evidence/codex-smoke-2026-05-19.md` | passed | 真实 `codex exec` 触发 `codex.local` thinking/running/success/error/need_input，且 operator visual accepted。 | 不证明所有 Codex 场景、multi-instance Codex、MCP 或 Windows。 |
| V3.0 baseline freeze report | `docs/V3.0/v3_0-baseline-freeze-report.md` | passed | V2.x/V2.1 allowed/forbidden claims 已冻结。 | 不证明任何 V3.0 多实例能力已完成。 |
| V3.0 final acceptance report | `docs/V3.0/v3_0-final-acceptance-report.md` | passed | 汇总 V3.0 final visual、two-Codex smoke、allowed/forbidden claims 和 residual risks。 | 不证明 all Codex workflows、OS-level window binding、Windows、MCP、USB 或 production release。 |
| Multi-instance foundation evidence | `docs/V3.0/evidence/multi-instance-foundation-2026-05-19.md` | passed | 自动检查、`.app` 打包、legacy health/petctl/raw HTTP 回归通过；Phase 3.2 engineering closure passed。 | 该证据本身不证明 instance-aware routing、Codex quick attach；最终多猫视觉证据见 Phase 3.7 final acceptance。 |
| Instance-aware routing evidence | `docs/V3.0/evidence/instance-aware-routing-2026-05-20.md` | passed | `POST /api/instances/:instanceId/events`、`GET /api/instances`、target metadata diagnostics、invalid/unknown/auth/rate-limit smoke 通过。 | 该证据本身不证明 Codex quick attach、multi-instance Codex verified、per-instance diagnostics 或 per-instance rate limit。 |
| Codex quick attach evidence | `docs/V3.0/evidence/codex-quick-attach-2026-05-20.md` | passed | `POST /api/instances`、`petctl attach codex`、`petctl list`、`notify --instance`、env routing、explicit override、JSON stdin routing smoke 通过。 | 不证明 OS-level window binding、MCP、Windows 或 production release；真实双 Codex session final smoke 见 Phase 3.7 final acceptance。 |
| Multi-pet manager evidence | `docs/V3.0/evidence/multi-pet-manager-ui-2026-05-20.md` | passed | Settings Multi-pet Manager、rename/show/hide/reset/detach Tauri commands、copy-only command templates and routing registry sync are implemented. | 不证明 V3.0 ready、真实双 Codex session visual verified、command execution UI or per-instance deep diagnostics。 |
| Built-in asset pack evidence | `docs/V3.0/evidence/asset-pack-v1-2026-05-20.md` | passed | Built-in CSS profiles, per-instance `catProfileId`, Manager Appearance selector and profile command validation are implemented. | 不证明 Rive/Live2D/3D、照片自定义、用户上传、远程下载、自定义资产包导入或资产市场 ready。 |
| Performance hardening and final acceptance evidence | `docs/V3.0/evidence/performance-hardening-final-acceptance-2026-05-20.md` | passed | soft/hard limits, hidden downgrade, hidden sound skip, event storm guard, Manager count/warning, operator final visual acceptance and two-Codex-session smoke passed. | 只证明 tested local Codex session scenarios；不证明 all Codex workflows、OS-level window binding、per-instance queue、Windows、MCP、USB 或 production release。 |

## Deferred Evidence Sources

| Evidence | Path | Status | Notes |
| --- | --- | --- | --- |
| Claude Code partial evidence | `docs/V2.1/evidence/claude-code-smoke-2026-05-19.md` | blocked | 真实 Claude Code skill runtime 已产生 accepted diagnostics evidence；不证明 Claude Code integration verified。 |
| Claude Code hook hardening evidence | `docs/V3.0/evidence/claude-code-hook-smoke-2026-05-19.md` | blocked | Hook wrapper readiness 已增强；真实 Notification hook 未通过。此项已从当前 V3.0 多实例主线移入 deferred backlog。 |

## Active V3.0 Evidence

| Phase | Evidence | Status |
| --- | --- | --- |
| Phase 3.2 Multi-instance Foundation | `docs/V3.0/evidence/multi-instance-foundation-2026-05-19.md` | passed; manual visual acceptance completed in final V3.0 acceptance |
| Phase 3.3 Instance-aware Event Routing | `docs/V3.0/evidence/instance-aware-routing-2026-05-20.md` | passed |
| Phase 3.4 Codex Quick Attach | `docs/V3.0/evidence/codex-quick-attach-2026-05-20.md` | passed; two-Codex-session final smoke completed in Phase 3.7 final acceptance |
| Phase 3.5 Multi-pet Manager UI | `docs/V3.0/evidence/multi-pet-manager-ui-2026-05-20.md` | passed; direct click visual smoke completed in final V3.0 acceptance |
| Phase 3.6 Asset Pack v1 | `docs/V3.0/evidence/asset-pack-v1-2026-05-20.md` | passed; direct visual profile smoke completed in final V3.0 acceptance |
| Phase 3.7 Performance Hardening | `docs/V3.0/evidence/performance-hardening-final-acceptance-2026-05-20.md` | passed |
| Phase 3.7 Operator Checklist | `docs/V3.0/v3_0-final-visual-acceptance-checklist.md` | operator passed |

V3.0 手工视觉验收已在 final acceptance 阶段收口。V3.0 ready 只覆盖 tested local Codex session scenarios。
