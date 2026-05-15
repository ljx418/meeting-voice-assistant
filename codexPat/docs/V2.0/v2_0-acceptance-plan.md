# V2.0 Acceptance Plan

文档状态：V2.0 planning baseline。

## 1. V2.0 最终验收标准

V2.0 完成必须满足：

1. V1.0 全量自动检查继续通过。
2. V1.0 macOS smoke 不回归：窗口、托盘、拖拽、HTTP、diagnostics、`petctl`、声音。
3. Codex / Claude Code instruction template 可用于真实本地任务状态汇报。
4. shell / Node 示例可触发 `running`、`success`、`error`、`need_input`。
5. `petctl` recipes 覆盖常见开发工作流：测试、构建、长任务、需要输入、失败恢复。
6. 设置页能解释 API 健康、最近事件、拒绝原因和声音决策。
7. README 能指导 macOS 用户完成本地部署、启动、验证和排障。
8. CSS 猫咪体验 polish 后不出现黑框、尺寸抖动或拖拽回归。
9. V1.0 安全边界不被破坏。

## 2. 自动检查命令

V2.0 每个实现阶段完成后建议执行：

```bash
pnpm run doctor
pnpm --filter @agent-desktop-pet/pet-protocol check
pnpm --filter @agent-desktop-pet/pet-protocol test
pnpm --filter @agent-desktop-pet/petctl check
pnpm --filter @agent-desktop-pet/petctl test
pnpm --filter desktop check
pnpm --filter desktop build
cargo check --manifest-path apps/desktop/src-tauri/Cargo.toml
pnpm --filter desktop tauri build -b app
```

## 3. 工作流 smoke test

### petctl recipes

- `petctl notify --level running --title "正在运行测试"` 触发 running。
- `petctl notify --level success --title "测试通过" --sound success_chime` 触发 success 和受控声音。
- `petctl notify --level error --title "构建失败" --sound error_chime` 触发 error。
- `petctl notify --level need_input --title "需要确认" --sound need_input_chime` 触发 need_input。

### shell 示例

- 包裹成功命令时：先 running，后 success。
- 包裹失败命令时：先 running，后 error，并保留原命令退出码。
- token 缺失或 desktop 未启动时：输出可理解错误，不吞掉原任务错误。

### Node 示例

- Node 示例不依赖未声明的 SDK。
- 使用 `petctl` 或 HTTP 触发事件。
- 不打印完整 token。
- 不发送路径或 URL 作为 sound。

### Codex / Claude Code template

- 模板引导 agent 在开始任务时发送 running/thinking。
- 完成后发送 success。
- 阻塞时发送 error 或 need_input。
- 不鼓励高频循环通知。
- 不允许直接控制 UI、执行任意脚本、传入本地资源路径。

## 4. Settings & diagnostics 验收

- 能看到 API enabled 和 listen address。
- 能看到 queue length / capacity。
- 能看到最近 accepted/rejected 摘要。
- rejected 摘要包含 reasonCode 和简短 reason。
- 能看到 sound playbackAvailable、muted、cooldownMs、acceptedIds、lastDecision。
- 能看到 petctl 测试命令。
- 不显示 token 全量。
- 不显示原始 payload。
- 不显示 metadata 全量。
- 不显示 message 全文。
- 不显示声音文件路径。

## 5. Cat experience 验收

- idle、thinking、running、success、warning、error、need_input、sleeping 肉眼可区分。
- thinking/running 低打扰。
- success 短反馈后回 idle。
- warning 明显但不抢占用户注意力。
- error/need_input 明显但受锁定期和 cooldown 控制。
- 动画不改变窗口尺寸。
- 透明窗口不出现黑框。
- 拖拽优先于动画。

## 6. No False-Green

V2.0 全部验收通过后可以声明：

```text
V2.0 ready: local agent workflow integration and developer usability polish complete.
Codex and Claude Code local workflow templates ready.
```

仍不能声明：

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

