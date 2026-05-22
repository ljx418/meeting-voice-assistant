# V3.1 Final Manual Acceptance Checklist

status: ready-for-operator

date: 2026-05-22

purpose: 用于补齐 V3.1 Final Acceptance 当前唯一阻塞项：Manager UI operator acceptance。

## 0. 验收结论填写区

| Item | Result | Notes |
| --- | --- | --- |
| operator |  |  |
| startedAt |  |  |
| completedAt |  |  |
| app visible |  |  |
| Manager UI acceptance |  |  |
| runtime sanity |  |  |
| final decision |  | passed / blocked / failed |

通过后需要更新：

- `docs/V3.1/evidence/manager-ui-polish-2026-05-20.md`
- `docs/V3.1/v3_1-final-acceptance-report.md`

只有这两个文件都更新为 `status: passed` 后，才允许声明：

```text
V3.1 ready: multi-instance Codex pet workflow stabilized with user onboarding, manager polish, repeatable runtime smoke, and migration guidance.
```

## 1. 启动 App

先确认项目根目录：

```bash
cd /Users/Zhuanz/Desktop/workspace/codexPat
```

启动已构建 app：

```bash
open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"
```

确认：

| Check | Result | Notes |
| --- | --- | --- |
| 桌面猫可见 |  |  |
| 透明窗口无黑框、无白底 |  |  |
| 至少 default pet 存在 |  |  |
| 可打开托盘设置页 |  |  |

如果 app 不存在，先构建：

```bash
pnpm --filter desktop tauri build -b app
```

然后重新执行 `open` 命令。

## 2. 创建两只验收猫

创建 Manager A：

```bash
node packages/petctl/dist/cli.js attach codex --name "Manager A" --json
```

创建 Manager B：

```bash
node packages/petctl/dist/cli.js attach codex --name "Manager B" --json
```

把输出里的两个 `instanceId` 记录下来：

| Pet | instanceId | Notes |
| --- | --- | --- |
| Manager A |  |  |
| Manager B |  |  |

查看当前实例列表：

```bash
node packages/petctl/dist/cli.js list --json
```

确认：

| Check | Result | Notes |
| --- | --- | --- |
| list 中包含 default |  |  |
| list 中包含 Manager A |  |  |
| list 中包含 Manager B |  |  |
| Manager UI 显示 default + A + B |  |  |
| Manager UI 和 `petctl list --json` 一致 |  |  |

## 3. Manager UI 中文文案验收

打开托盘设置页，检查多猫管理区域。

| Check | Expected | Result | Notes |
| --- | --- | --- | --- |
| 区域标题 | 多猫管理 |  |  |
| default 标注 | 默认猫 / 旧路由 |  |  |
| A/B 标注 | Codex 实例猫 / 实例路由 |  |  |
| 实例字段 | 实例 ID |  |  |
| 窗口字段 | 窗口标签 |  |  |
| 状态字段 | 当前状态 |  |  |
| 可见字段 | 可见 / 已隐藏 |  |  |
| 外观字段 | 外观，优先显示中文或可读名称 |  |  |

状态中文映射至少检查当前可见状态：

| State | Expected Chinese | Result | Notes |
| --- | --- | --- | --- |
| idle | 空闲 |  |  |
| thinking | 思考中 |  |  |
| running | 执行中 |  |  |
| success | 完成 |  |  |
| warning | 注意 |  |  |
| error | 失败 |  |  |
| need_input | 需要确认 |  |  |
| sleeping | 休息中 |  |  |

## 4. 重命名验收

在 Manager A 的卡片上点击“重命名”。

要求：

- 使用 inline input。
- 不使用系统 prompt。
- 操作后不需要 reload。
- card 和猫窗口 name label 都即时更新。

将 Manager A 重命名为：

```text
评审猫
```

确认：

| Check | Result | Notes |
| --- | --- | --- |
| 点击“重命名”后出现 inline input |  |  |
| 保存后 card 显示“评审猫” |  |  |
| 保存后猫窗口名字即时变为“评审猫” |  |  |
| 页面显示“已重命名”反馈 |  |  |
| 不需要 reload app |  |  |
| 不显示 raw error、stack trace、路径、token、payload |  |  |

执行列表检查：

```bash
node packages/petctl/dist/cli.js list --json
```

确认 `Manager A` 对应实例显示为 `评审猫`。

## 5. 显示 / 隐藏验收

对 Manager B 执行隐藏：

| Check | Result | Notes |
| --- | --- | --- |
| 点击“隐藏”后只隐藏 B |  |  |
| default 不受影响 |  |  |
| 评审猫不受影响 |  |  |
| B card 状态显示“已隐藏”或“已隐藏”反馈 |  |  |

对 Manager B 执行显示：

| Check | Result | Notes |
| --- | --- | --- |
| 点击“显示”后只显示 B |  |  |
| B card 状态显示“可见”或“已显示”反馈 |  |  |
| 其他猫不受影响 |  |  |

## 6. 重置位置验收

对“评审猫”执行“重置位置”。

确认：

| Check | Result | Notes |
| --- | --- | --- |
| 只影响评审猫 |  |  |
| 评审猫回到主屏幕安全区域 |  |  |
| default 不移动 |  |  |
| Manager B 不移动 |  |  |
| 页面显示“已重置位置”反馈 |  |  |

## 7. 复制命令安全验收

对“评审猫”执行“复制环境变量”。

剪贴板内容应类似：

```bash
export AGENT_DESKTOP_PET_INSTANCE_ID=<instanceId>
```

确认剪贴板不包含：

| Forbidden | Result |
| --- | --- |
| token |  |
| `AGENT_DESKTOP_PET_TOKEN` 的真实值 |  |
| `api-token.json` |  |
| `Application Support` |  |
| config path |  |
| workspace path |  |
| raw payload |  |
| metadata |  |

对“评审猫”执行“复制通知命令”。

剪贴板内容必须包含：

```text
--instance <评审猫 instanceId>
```

确认：

| Check | Result | Notes |
| --- | --- | --- |
| 复制命令包含 `--instance` |  |  |
| 复制命令不包含 token |  |  |
| 复制命令不包含 config path |  |  |
| 复制命令不包含 workspace path |  |  |
| 设置页没有 Run / Execute / 执行命令按钮 |  |  |
| 点击复制不会执行 shell、petctl、curl、node 或 osascript |  |  |

## 8. 移除验收

对 Manager B 执行“移除”。

第一次点击：

| Check | Result | Notes |
| --- | --- | --- |
| 按钮变为“确认移除” |  |  |
| B 尚未被移除 |  |  |
| 不使用系统 confirm |  |  |

第二次点击“确认移除”：

| Check | Result | Notes |
| --- | --- | --- |
| B 窗口关闭 |  |  |
| B 从 Manager UI 列表消失 |  |  |
| default 不受影响 |  |  |
| 评审猫不受影响 |  |  |

对 B 的 instanceId 发送事件，期望 404。

把下面命令中的 `<B_INSTANCE_ID>` 替换为 Manager B 的 instanceId：

```bash
node packages/petctl/dist/cli.js notify --instance <B_INSTANCE_ID> --level success --title "after detach"
```

确认：

| Check | Expected | Result | Notes |
| --- | --- | --- | --- |
| CLI exit code | 非 0 |  |  |
| reasonCode | instance_not_found |  |  |
| default 不响应 | 是 |  |  |
| 评审猫不响应 | 是 |  |  |

## 9. Default Guard 验收

检查 default pet 的移除按钮。

| Check | Result | Notes |
| --- | --- | --- |
| default 的移除按钮禁用，或只显示安全中文错误 |  |  |
| 文案包含“默认猫不可移除”或等价说明 |  |  |
| default 没有被移除 |  |  |

## 10. Legacy Route 回归

执行 legacy notify：

```bash
node packages/petctl/dist/cli.js notify --level success --title "legacy manager smoke"
```

确认：

| Check | Expected | Result | Notes |
| --- | --- | --- | --- |
| default 进入 success | 是 |  |  |
| 评审猫不响应 legacy event | 是 |  |  |
| 已移除的 B 不恢复 | 是 |  |  |

## 11. 设置页布局和敏感信息验收

| Check | Result | Notes |
| --- | --- | --- |
| 设置页可滚动 |  |  |
| 多猫 card 在窄窗口下不溢出 |  |  |
| 长 instanceId / windowLabel 不撑破容器 |  |  |
| 中文按钮不挤压变形 |  |  |
| 底部按钮不覆盖内容 |  |  |
| 不显示 token |  |  |
| 不显示 raw payload |  |  |
| 不显示 metadata 全量 |  |  |
| 不显示 workspace path |  |  |
| 不显示 config path |  |  |
| 不显示声音文件路径 |  |  |
| 不显示命令执行按钮 |  |  |

## 12. 重启持久化验收

退出 app，然后重新打开。

如需从终端确认端口退出：

```bash
lsof -iTCP:17321
```

重新打开：

```bash
open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"
```

确认：

| Check | Result | Notes |
| --- | --- | --- |
| default 仍存在 |  |  |
| 评审猫仍存在 |  |  |
| 评审猫名称保持 |  |  |
| Manager B 不恢复 |  |  |
| 位置没有出屏 |  |  |
| 外观保持 |  |  |
| 设置页仍能打开 |  |  |

## 13. 验收后更新文件

如果以上全部通过，把 `docs/V3.1/evidence/manager-ui-polish-2026-05-20.md` 更新为：

```text
status: passed
```

并补充：

- operator
- completedAt
- manager list consistency result
- rename feedback result
- show/hide feedback result
- reset feedback result
- copy command safety result
- detach confirmation result
- after-detach notify rejection result
- default detach guard result
- layout check result
- forbidden data visibility check

然后把 `docs/V3.1/v3_1-final-acceptance-report.md` 更新为：

```text
status: passed
```

只有这时才允许更新 README / active gap 为：

```text
V3.1 ready: multi-instance Codex pet workflow stabilized with user onboarding, manager polish, repeatable runtime smoke, and migration guidance.
```

## 14. 失败处理模板

以下内容仅作为未来重跑本清单时的失败处理模板；本轮 operator 已确认上述验收全部通过。

如果任一项失败：

- 不要声明 V3.1 ready。
- 保持 `docs/V3.1/v3_1-final-acceptance-report.md` 为 `status: blocked` 或改为 `failed`。
- 在失败项 notes 中记录具体表现。
- 不要扩大声明到 Windows、MCP、USB、production release 或 all Codex workflows verified。
