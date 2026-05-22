# V3.0 Final Visual Acceptance Checklist

文档状态：historical operator checklist；V3.0 final acceptance passed for tested local Codex session scenarios。

本清单曾用于完成 V3.0 Phase 3.7 后延后的最终视觉验收和 two-Codex-session smoke。当前 operator result 已通过，并已同步更新 `docs/V3.0/evidence/performance-hardening-final-acceptance-2026-05-20.md` 为 passed，因此允许声明：

```text
V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.
```

如果只完成 A-I，未完成 J，则只能继续声明：

```text
Phase 3.7 engineering hardening complete: multi-pet runtime limits and stability guards ready.
```

仍禁止声明：

```text
Windows ready
cross-platform ready
MCP ready
USB ready
production signed release ready
OS-level Codex window binding ready
all Codex workflows verified
per-instance queue ready
```

## 0. 准备

进入项目目录：

```bash
cd /Users/Zhuanz/Desktop/workspace/codexPat
```

构建 `.app`：

```bash
pnpm --filter desktop tauri build -b app
```

启动 `.app`：

```bash
open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"
```

确认 HTTP health：

```bash
curl -sS http://127.0.0.1:17321/api/health
```

期望：返回 `ok` 或包含 `"ok":true`。

验收记录：

- [ ] `.app` 构建成功。
- [ ] `.app` 启动成功。
- [ ] `/api/health` 正常。

## A. 基础视觉验收

- [ ] 默认猫可见。
- [ ] 窗口透明，无白底。
- [ ] 没有黑框、脏边、阴影错位。
- [ ] 默认猫可拖拽。
- [ ] 拖拽后动画不抢控制。
- [ ] 托盘菜单可打开设置页。
- [ ] 关闭设置页不影响猫窗口。
- [ ] 托盘退出后所有猫窗口关闭。

退出后确认端口不再监听：

```bash
lsof -iTCP:17321
```

期望：无输出。

- [ ] 退出后 `17321` 不再监听。

## B. 多猫创建验收

重新启动 app：

```bash
open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"
```

创建两只 Codex 猫：

```bash
node packages/petctl/dist/cli.js attach codex --name "Codex A" --json
```

```bash
node packages/petctl/dist/cli.js attach codex --name "Codex B" --json
```

记录返回的 `instanceId`：

```text
A=<Codex A instanceId>
B=<Codex B instanceId>
```

查看实例列表：

```bash
node packages/petctl/dist/cli.js list --json
```

验收记录：

- [ ] 桌面上至少有 default、Codex A、Codex B 三只猫。
- [ ] 三只猫不是完全重叠。
- [ ] 每只猫有独立名字。
- [ ] 每只猫可独立拖拽。
- [ ] 三只猫都透明、无边框、置顶。
- [ ] 没有白底、黑框、系统标题栏。
- [ ] 设置页 Multi-pet Manager 显示 default + A + B。
- [ ] `petctl list --json` 与设置页列表一致。

## C. Instance Routing 验收

把 `<A>` 和 `<B>` 替换为上一步记录的 instanceId。

A success：

```bash
node packages/petctl/dist/cli.js notify --instance <A> --level success --title "A success"
```

验收记录：

- [ ] 只有 A 进入 success。
- [ ] B 不变化。
- [ ] default 不变化。

B error：

```bash
node packages/petctl/dist/cli.js notify --instance <B> --level error --title "B error"
```

验收记录：

- [ ] 只有 B 进入 error。
- [ ] A 不变化。
- [ ] default 不变化。

legacy default：

```bash
node packages/petctl/dist/cli.js notify --level success --title "legacy default"
```

验收记录：

- [ ] 只有 default 进入 success。
- [ ] A/B 不响应 legacy event。

## D. 多猫管理验收

在设置页「多猫管理」中操作。

验收记录：

- [ ] 将 A 的「名称」输入框改为 `Review Cat`，点击「重命名」。
- [ ] A 名字在「多猫管理」中更新。
- [ ] A 名字在桌面 name tag 中更新。
- [ ] `petctl list --json` 显示新名字。
- [ ] 点击 B 的「隐藏」后，只有 B 消失。
- [ ] 点击 B 的「显示」后，只有 B 恢复。
- [ ] 点击 A 的「重置位置」后，A 回到主屏幕可见区域。
- [ ] 「重置位置」A 不影响 B/默认猫。
- [ ] 「复制环境变量」只复制文本，不执行命令。
- [ ] 「复制通知命令模板」只复制文本，不执行命令。
- [ ] 复制内容不包含 token。
- [ ] 复制内容不包含 config path。
- [ ] 复制内容不包含完整 workspace path。
- [ ] 点击 B 的「移除」后，按钮变为「确认移除」。
- [ ] 再次点击「确认移除」后，B 窗口关闭，并从「多猫管理」列表移除。
- [ ] 默认猫的「移除」被禁用或拒绝。

移除 B 后验证路由拒绝：

```bash
node packages/petctl/dist/cli.js notify --instance <B> --level success --title "after detach"
```

期望：返回 `404 instance_not_found`。

- [ ] 返回 `404 instance_not_found`。
- [ ] default 不响应。
- [ ] A 不响应。

如果后续步骤仍需要 B，请重新创建 B 并更新 `<B>`：

```bash
node packages/petctl/dist/cli.js attach codex --name "Codex B" --json
```

## E. 外观 / 内置资产包验收

在「多猫管理」里切换外观：

- 默认猫：`default-cat`
- A：`black-cat`
- B：`orange-tabby` 或 `white-cat`

验收记录：

- [ ] 默认猫保持 `default-cat`。
- [ ] A 切换为 `black-cat`。
- [ ] B 切换为 `orange-tabby` 或 `white-cat`。
- [ ] 三只猫肉眼可区分。
- [ ] 切换 A 外观不影响 B/默认猫。
- [ ] 切换 B 外观不影响 A/默认猫。
- [ ] 状态动画和外观不冲突。
- [ ] success/error/need_input 状态下外观仍可识别。
- [ ] 没有窗口尺寸抖动。
- [ ] 没有黑框或脏边。

## F. Hidden Pet 行为验收

在「多猫管理」中隐藏 B。

验收记录：

- [ ] B 窗口不可见。
- [ ] B 仍在「多猫管理」中显示为「隐藏」。

向隐藏的 B 发送 need_input：

```bash
node packages/petctl/dist/cli.js notify --instance <B> --level need_input --title "hidden need input" --sound need_input_chime
```

查看列表：

```bash
node packages/petctl/dist/cli.js list --json
```

验收记录：

- [ ] B 不自动显示。
- [ ] B 状态在 Manager 或 `list --json` 中更新为 `need_input`。
- [ ] 不播放声音。
- [ ] 显示 B 后，B 展示最新状态。

## G. 性能与数量限制验收

继续创建猫，直到 total pets 达到 12。根据当前已有数量调整命令次数。

```bash
node packages/petctl/dist/cli.js attach codex --name "Load Cat 3" --json
```

```bash
node packages/petctl/dist/cli.js attach codex --name "Load Cat 4" --json
```

```bash
node packages/petctl/dist/cli.js attach codex --name "Load Cat 5" --json
```

```bash
node packages/petctl/dist/cli.js attach codex --name "Load Cat 6" --json
```

```bash
node packages/petctl/dist/cli.js attach codex --name "Load Cat 7" --json
```

```bash
node packages/petctl/dist/cli.js attach codex --name "Load Cat 8" --json
```

```bash
node packages/petctl/dist/cli.js attach codex --name "Load Cat 9" --json
```

```bash
node packages/petctl/dist/cli.js attach codex --name "Load Cat 10" --json
```

```bash
node packages/petctl/dist/cli.js attach codex --name "Load Cat 11" --json
```

```bash
node packages/petctl/dist/cli.js list --json
```

尝试创建第 13 只：

```bash
node packages/petctl/dist/cli.js attach codex --name "Load Cat 13" --json
```

验收记录：

- [ ] 到 6 只及以上时 Manager 显示 soft limit warning。
- [ ] 到 12 只时 Manager 显示 hard limit。
- [ ] 第 13 只创建失败。
- [ ] 第 13 只返回 `instance_limit_reached`。
- [ ] 没有幽灵窗口。
- [ ] 没有残留 instance。
- [ ] 已有猫不受影响。

## H. Event Storm 验收

对 A 高频发送 running：

```bash
for i in {1..20}; do
  node packages/petctl/dist/cli.js notify --instance <A> --level running --title "A storm $i"
done
```

立即对 B 发送 success：

```bash
node packages/petctl/dist/cli.js notify --instance <B> --level success --title "B after storm"
```

验收记录：

- [ ] A 可能出现 rate limit。
- [ ] B 仍能进入 success。
- [ ] B 不被 A 的 storm 影响。
- [ ] 没有声音轰炸。
- [ ] UI 没有明显卡死。
- [ ] diagnostics rejected summary 不回显 token、路径、URL、raw payload。

## I. 重启持久化验收

退出 app，再重新打开：

```bash
open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"
```

验收记录：

- [ ] 默认猫恢复。
- [ ] 未移除的额外猫恢复。
- [ ] 名字恢复。
- [ ] 位置恢复。
- [ ] 外观 profile 恢复。
- [ ] 隐藏状态按预期恢复。
- [ ] 不出现已移除的猫。
- [ ] 不出现重复猫。
- [ ] 不出屏。
- [ ] 不全部堆叠在同一点。

## J. 双 Codex 会话最终验收

Case J 分成两层：

- J1 是“等价本地终端验收”：用两个 instance 模拟两个 Codex 会话，确认 `--instance` 路由不会串猫。J1 通过只能证明多实例路由可用。
- J2 是“真实 Codex 双会话验收”：必须真的打开两个 Codex terminal/session，并让两个 Codex 会话各自绑定一只猫。只有 J2 也通过，才允许声明 V3.0 ready。

如果只跑 J1，没有跑 J2，最终结论只能写：

```text
Phase 3.7 engineering hardening complete: multi-pet runtime limits and stability guards ready.
V3.0 ready: not yet, real two-Codex-session smoke not run.
```

### J1. 等价本地终端路由验收

这个步骤在普通终端执行即可。它不等于真实 Codex 验收，但可以先确认多猫路由链路没有问题。

创建 A：

```bash
node packages/petctl/dist/cli.js attach codex --name "J1 Codex A" --json
```

从输出中复制 A 的 `instanceId`，写到下面：

```text
instanceIdA=<粘贴 J1 Codex A 的 instanceId>
```

触发 A：

```bash
node packages/petctl/dist/cli.js notify --instance <instanceIdA> --level running --title "J1 A running"
```

```bash
node packages/petctl/dist/cli.js notify --instance <instanceIdA> --level success --title "J1 A success"
```

创建 B：

```bash
node packages/petctl/dist/cli.js attach codex --name "J1 Codex B" --json
```

从输出中复制 B 的 `instanceId`，写到下面：

```text
instanceIdB=<粘贴 J1 Codex B 的 instanceId>
```

触发 B：

```bash
node packages/petctl/dist/cli.js notify --instance <instanceIdB> --level running --title "J1 B running"
```

```bash
node packages/petctl/dist/cli.js notify --instance <instanceIdB> --level error --title "J1 B error"
```

检查 diagnostics：

1. 打开托盘设置页。
2. 点击“刷新”。
3. 在 recent accepted events / diagnostics 中确认能看到 A 和 B 对应的 `targetInstanceId`。

J1 验收记录：

- [ ] A 和 B 是两只不同的猫。
- [ ] A running/success 只影响 A。
- [ ] B running/error 只影响 B。
- [ ] diagnostics 里能看到不同 `targetInstanceId`。
- [ ] 没有串猫。
- [ ] 没有 legacy default 被误触发。
- [ ] 没有高频刷事件。
- [ ] 没有 token 泄露。
- [ ] 没有非法 sound。
- [ ] operator 人工确认两只猫分别变化。

J1 结论：

```text
J1 equivalent local terminal routing: passed / blocked / failed
```

### J2. 真实两个 Codex 会话验收

这个步骤必须在两个真实 Codex terminal/session 中执行，不能只用普通终端手动 `petctl notify` 替代。J2 是声明 V3.0 ready 的关键。

#### J2-A：Codex 会话 A

打开第一个 Codex 终端窗口或标签页，让 Codex 执行或按 Codex skill 指引执行：

```bash
node packages/petctl/dist/cli.js attach codex --name "Real Codex A" --json
```

记录 A 的 instanceId：

```text
realCodexInstanceIdA=<粘贴 Real Codex A 的 instanceId>
```

在同一个 Codex 会话 A 中继续触发：

```bash
node packages/petctl/dist/cli.js notify --instance <realCodexInstanceIdA> --level running --title "Real Codex A running"
node packages/petctl/dist/cli.js notify --instance <realCodexInstanceIdA> --level success --title "Real Codex A success"
```

#### J2-B：Codex 会话 B

打开第二个 Codex 终端窗口或标签页，让 Codex 执行或按 Codex skill 指引执行：

```bash
node packages/petctl/dist/cli.js attach codex --name "Real Codex B" --json
```

记录 B 的 instanceId：

```text
realCodexInstanceIdB=<粘贴 Real Codex B 的 instanceId>
```

在同一个 Codex 会话 B 中继续触发：

```bash
node packages/petctl/dist/cli.js notify --instance <realCodexInstanceIdB> --level running --title "Real Codex B running"
node packages/petctl/dist/cli.js notify --instance <realCodexInstanceIdB> --level error --title "Real Codex B error"
```

J2 验收记录：

- [ ] A 和 B 来自两个真实 Codex terminal/session。
- [ ] A 和 B 绑定到两个不同 instanceId。
- [ ] Real Codex A running/success 只影响 A 的猫。
- [ ] Real Codex B running/error 只影响 B 的猫。
- [ ] diagnostics 中出现两个不同的 `targetInstanceId`。
- [ ] diagnostics 中 sourceId 为 `codex.local`。
- [ ] 没有串猫。
- [ ] 没有 legacy default 被误触发。
- [ ] 没有高频刷事件。
- [ ] 没有 token 泄露。
- [ ] 没有非法 sound。
- [ ] operator 人工确认两只真实 Codex 猫分别变化。

J2 结论：

```text
J2 real two-Codex-session smoke: passed / blocked / failed / not-run
```

如果 J2 没有执行或没有通过，不要声明 V3.0 ready。

## K. 验收结论

如果 A-I 通过，但 J1/J2 都没跑：

```text
Phase 3.7 engineering hardening complete: multi-pet runtime limits and stability guards ready.
```

如果 A-I 和 J1 通过，但 J2 没跑或没通过：

```text
Phase 3.7 engineering hardening complete: multi-pet runtime limits and stability guards ready.
V3.0 ready: not yet, real two-Codex-session smoke not passed.
```

如果 A-I、J1、J2 全部通过：

```text
V3.0 ready: multi-instance Codex desktop pet workflow ready for tested local Codex session scenarios.
```

即使 A-I、J1、J2 全部通过，仍禁止声明：

```text
Windows ready
cross-platform ready
MCP ready
USB ready
production signed release ready
OS-level Codex window binding ready
all Codex workflows verified
```

## Operator Result

验收结果：

```text
operator: Zhuanz
date: 2026-05-20

A 基础视觉: passed
B 多猫创建: passed
C Instance Routing: passed
D Manager UI: passed
E Appearance / Asset Pack: passed
F Hidden Pet: passed
G 数量限制: passed
H Event Storm: passed
I 重启持久化: passed
J1 等价本地终端路由: passed
J2 真实双 Codex 会话: passed

最终结论: V3.0 ready for tested local Codex session scenarios.
失败项: none
备注:
- Real Codex A: codex_1779267171861, windowLabel=pet-codex_1779267171861, running event evt_1779267224048_25.
- Real Codex B: codex_1779267264893, windowLabel=pet-codex_1779267264893, currentState=error, lastEventAt=1779267327641.
- 该结论不扩展到 all Codex workflows、OS-level window binding、Windows、MCP、USB 或 production signed release。
```
