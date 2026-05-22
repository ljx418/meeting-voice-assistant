# V3.1 Phase 3 Evidence：Manager UI Usability Polish

status: passed

date: 2026-05-20

commit: 8872bf82
checkedAt: 2026-05-21 Asia/Shanghai
finalAcceptanceCheckedAt: 2026-05-22 Asia/Shanghai
operatorAcceptanceAt: 2026-05-22 Asia/Shanghai

## Scope

V3.1 Phase 3 只做 Multi-pet Manager 的文案、反馈、布局和安全复制体验。

## Automatic Checks

| Command | Result | Notes |
| --- | --- | --- |
| `pnpm run doctor` | pass-with-warn | 无 hard failure。WARN：未安装 rustup；网络探测不可达；沙箱下 127.0.0.1:1420 listen EPERM。 |
| `pnpm --filter @agent-desktop-pet/petctl check` | pass | TypeScript check passed。 |
| `pnpm --filter @agent-desktop-pet/petctl test` | pass | 14 tests passed。 |
| `pnpm --filter desktop check` | pass | `tsc --noEmit` passed。 |
| `cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml` | pass | Rust check passed。 |
| `pnpm --filter desktop build` | pass | Vite production build passed。 |
| `pnpm --filter desktop tauri build -b app` | pass | `.app` generated at `apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app`。 |

## Acceptance Evidence

| Item | Result | Notes |
| --- | --- | --- |
| manager list consistency result | passed | Operator confirmed Manager UI matches `petctl list --json`. |
| rename feedback result | passed | Operator confirmed inline rename works and cat name updates without reload. |
| show/hide feedback result | passed | Operator confirmed show/hide only affects the target pet. |
| reset feedback result | passed | Operator confirmed reset position only affects the target pet. |
| copy command safety result | passed | Operator confirmed copied env/notify templates contain no token, config path, workspace path or raw payload. |
| detach confirmation result | passed | Operator confirmed remove / confirm remove flow works and target pet closes. |
| after-detach notify rejection result | passed | Operator confirmed notify to detached instance returns `instance_not_found` and does not affect other pets. |
| default detach guard result | passed | Operator confirmed default pet cannot be removed. |
| layout check result | passed | Operator confirmed settings page is scrollable and cards/buttons do not overflow. |
| forbidden data visibility check | passed | Operator confirmed Manager UI does not show token, raw payload, metadata full content, workspace path, config path or command execution buttons. |

## Operator Visual Acceptance

| Check | Result | Notes |
| --- | --- | --- |
| app visible | passed | Operator confirmed app was visible during checklist execution. |
| Manager UI Chinese copy | passed | Operator confirmed Chinese labels and actions are understandable. |
| default / extra pet route labels | passed | Operator confirmed default shows “默认猫 / 旧路由” and extra pets show “Codex 实例猫 / 实例路由”. |
| currentState Chinese labels | passed | Operator confirmed state labels are shown in Chinese. |
| rename persistence | passed | Operator confirmed renamed pet remains correct after restart. |
| detach persistence | passed | Operator confirmed detached pet does not restore after restart. |

## Manual Checklist

1. 启动 app。
2. 打开托盘设置页。
3. 创建两只 Codex 猫：

   ```bash
   node packages/petctl/dist/cli.js attach codex --name "Manager A" --json
   node packages/petctl/dist/cli.js attach codex --name "Manager B" --json
   ```

4. 确认设置页显示 default + A + B。
5. 执行：

   ```bash
   node packages/petctl/dist/cli.js list --json
   ```

   确认与 Manager UI 一致。

6. 确认 default 标注“默认猫 / 旧路由”。
7. 确认 A/B 标注“Codex 实例猫 / 实例路由”。
8. 将 A 重命名为“评审猫”，确认 card 和猫窗口名字即时更新，显示“已重命名”。
9. 重启 app，确认“评审猫”名称保持。
10. 点击 B 的“隐藏”，确认 B 窗口隐藏，card 状态变为“已隐藏”。
11. 点击 B 的“显示”，确认 B 窗口出现，card 状态变为“可见”。
12. 点击 A 的“重置位置”，确认 A 回到安全区域。
13. 点击 A 的“复制环境变量”，确认剪贴板不含 token、`api-token.json`、`Application Support`、workspace path。
14. 点击 A 的“复制通知命令”，确认包含 `--instance <A>`，不含 token。
15. 点击 B 的“移除”，确认按钮变为“确认移除”。
16. 再点“确认移除”，确认 B 窗口关闭、B 从列表消失、default 和 A 不受影响。
17. 对 B 发送 notify，期望 404：

   ```bash
   node packages/petctl/dist/cli.js notify --instance <B_INSTANCE_ID> --level success --title "after detach"
   ```

18. 重启 app，确认 B 不恢复。
19. legacy notify 仍只影响 default：

   ```bash
   node packages/petctl/dist/cli.js notify --level success --title "legacy manager smoke"
   ```

20. 检查设置页无 token、raw payload、metadata 全量、workspace path。
21. 检查没有命令执行按钮。
22. 检查设置页可滚动，无明显布局溢出。
23. 检查 currentState 值为中文。
24. 检查 default pet 的移除按钮不可点击或只显示安全中文错误。

## Allowed Claim

本 evidence status 已为 `passed`，允许声明：

```text
V3.1 Phase 3 complete: multi-pet manager usability polish ready.
```

## Forbidden Claims

本 Phase 3 evidence 不单独授权以下声明；V3.1 ready 只能由 `docs/V3.1/v3_1-final-acceptance-report.md` 授权。

```text
MCP ready
Windows ready
cross-platform ready
USB ready
production signed release ready
OS-level Codex window binding ready
all Codex workflows verified
per-instance queue ready
```

## Remaining Blockers

- None for V3.1 Phase 3 Manager UI Usability Polish.
