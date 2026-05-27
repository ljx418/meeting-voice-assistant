# Multi-Codex Workflow Guide

本文说明如何实现“一只 Codex 窗口/会话一只猫”。

V3.3 增加 wrapper-first 绑定路径。这里的 Codex 窗口指通过 `petctl codex launch` 启动的本地 Codex session / terminal tab；wrapper 会创建实例、注入 `AGENT_DESKTOP_PET_INSTANCE_ID` 并设置终端标题。

V3.7 增加 `codex exec --json` 的 project-owned JSONL monitor 路径，并成为当前推荐的 Codex exec 监听方案。它只适用于通过 `petctl codex launch --monitor jsonl` 启动的 wrapper-launched exec session，不是 Codex official hook lifecycle evidence，也不会把 V3.6 hook-only historical blocked 证据改写为 passed。

V3.3 仍不声明通用 OS-level Codex window binding ready。未通过 wrapper 启动的任意系统窗口不会被自动识别。

## 准备

进入项目目录：

```bash
cd /Users/Zhuanz/Desktop/workspace/codexPat
```

启动已构建的桌宠：

```bash
open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"
```

确认本地 API 正常：

```bash
curl -sS http://127.0.0.1:17321/api/health
```

如果返回 `ok: true`，说明桌宠可接收本地事件。

## 推荐：用 wrapper 启动 Codex Session

为当前 Codex session 创建一只猫并启动 Codex：

```bash
node packages/petctl/dist/cli.js codex launch --name "Review Cat" -- --help
```

实际使用时，把 `--help` 替换成需要传给 `codex` 的参数；如果没有参数，保留 `--` 后为空也可以。

期望结果：

- wrapper 创建一只 Codex instance cat。
- 当前 Codex 子进程继承 `AGENT_DESKTOP_PET_INSTANCE_ID`。
- wrapper 在子进程启动时发送 `running`。
- 子进程成功退出时发送 `success`。
- 子进程失败退出时发送 `error`。
- 会话内后续 `petctl notify` 默认只影响该 session 的猫。

## V3.7：JSONL Monitor for `codex exec --json`

如果你希望 wrapper 从 `codex exec --json` 的结构化 JSONL stdout 映射状态，可以启用 monitor：

```bash
node packages/petctl/dist/cli.js codex launch \
  --monitor jsonl \
  --name "Review Cat" \
  -- codex exec --json "summarize this repository"
```

也可以省略重复的 `codex`，直接通过默认 bin 启动：

```bash
node packages/petctl/dist/cli.js codex launch \
  --monitor jsonl \
  --name "Review Cat" \
  -- exec --json "summarize this repository"
```

状态映射边界：

| JSONL event type | 猫状态 |
| --- | --- |
| `turn.started` | `thinking` |
| `item.started` | `running` |
| `turn.completed` | `success`，仅限本轮没有 error |
| `turn.failed` / `error` | `error` |

注意：

- 这是 project-owned structured monitor，不是 official Codex hook lifecycle evidence。
- 不覆盖 interactive Codex TUI。
- 不解析人类可读终端文本。
- 不读取或依赖 `transcript_path`。
- 不记录 raw JSONL、prompt 原文、tool command 原文、token、Authorization、完整本地路径、workspace path 或 config path。
- `turn.completed` 只表示 non-error turn completion，不代表业务质量成功。
- 如果当前轮已经出现 `turn.failed` 或 `error`，后续 completion 不得覆盖 `error`。

## 手动 attach 当前 Shell

如果不想由 wrapper 启动 Codex，也可以为当前 shell 创建一只猫：

```bash
node packages/petctl/dist/cli.js attach codex --name "Review Cat" --json
```

从输出中复制 `instanceId`，然后向这只猫发送事件：

```bash
node packages/petctl/dist/cli.js notify --instance <instanceId> --level running --title "Codex running"
node packages/petctl/dist/cli.js notify --instance <instanceId> --level success --title "Codex success"
```

期望结果：

- 只影响 `<instanceId>` 对应的猫。
- 默认猫不响应 `--instance` 事件。
- 其他 Codex 实例猫不响应该事件。

## 使用当前 Shell 环境变量

如果希望当前终端后续命令默认路由到同一只猫，可以执行：

```bash
eval "$(node packages/petctl/dist/cli.js attach codex --name 'Refactor Cat' --print-env)"
```

然后可以省略 `--instance`：

```bash
node packages/petctl/dist/cli.js notify --level running --title "Refactor running"
node packages/petctl/dist/cli.js notify --level success --title "Refactor done"
```

注意：

- `eval "$( ... --print-env)"` 只影响当前 shell。
- 它不会永久修改父 shell、其他终端标签页或未来 Codex session。
- 可重复脚本中更推荐显式使用 `--instance <instanceId>`。

## 两个 Codex Session

推荐 wrapper 方式：

```bash
node packages/petctl/dist/cli.js codex launch --name "Codex A" -- --help
node packages/petctl/dist/cli.js codex launch --name "Codex B" -- --help
```

手动 attach 方式仍可用。

在 Codex session A 中执行：

```bash
node packages/petctl/dist/cli.js attach codex --name "Codex A" --json
node packages/petctl/dist/cli.js notify --instance <instanceIdA> --level running --title "A running"
node packages/petctl/dist/cli.js notify --instance <instanceIdA> --level success --title "A success"
```

在 Codex session B 中执行：

```bash
node packages/petctl/dist/cli.js attach codex --name "Codex B" --json
node packages/petctl/dist/cli.js notify --instance <instanceIdB> --level running --title "B running"
node packages/petctl/dist/cli.js notify --instance <instanceIdB> --level error --title "B error"
```

验收标准：

- A 和 B 创建两只不同的猫。
- A 的事件只影响 A 的猫。
- B 的事件只影响 B 的猫。
- 默认猫不响应 A/B 的 `--instance` 事件。

## 查看和管理猫

列出实例：

```bash
node packages/petctl/dist/cli.js list
node packages/petctl/dist/cli.js list --json
```

也可以打开托盘设置页，在“多猫管理”中检查：

- 每只猫的名称。
- `instanceId`。
- 当前状态。
- 显示 / 隐藏状态。
- 外观 profile。
- 默认猫和 Codex 实例猫的区别。

多猫管理只复制命令文本，不执行 shell、`petctl`、`curl`、`node` 或任何系统命令。

## 默认猫旧路由

如果没有传 `--instance`，并且当前 shell 中没有 `AGENT_DESKTOP_PET_INSTANCE_ID`，`petctl notify` 会路由到默认猫：

```bash
node packages/petctl/dist/cli.js notify --level success --title "default success"
```

这适合只需要一个全局状态猫的场景。

## 常见错误

| 错误 | 含义 | 处理 |
| --- | --- | --- |
| `desktop_not_running` | 桌宠没有启动或本地 API 不可用。 | 启动 app，再执行 `curl /api/health`。 |
| `token_missing` | CLI 找不到本地 token。 | 启动桌宠；仅在私有本地脚本中使用 `--token` 或 `AGENT_DESKTOP_PET_TOKEN`。 |
| `unauthorized` | token 缺失或不正确。 | 不要把 token 写进公开脚本；重新启动 app 或使用正确 token 来源。 |
| `instance_not_found` | 目标 `instanceId` 不存在。 | 执行 `petctl list`，或重新 `attach codex`。 |
| `instance_id_invalid` | `instanceId` 格式非法。 | 使用 `attach` 或 `list` 返回的完整 id。 |
| `instance_limit_reached` | 达到 12 只猫硬上限。 | 在多猫管理里移除不用的实例猫。 |
| `rate_limited` | 事件发送太频繁。 | 只在任务阶段变化时发送事件，不要每行日志都发。 |
| `whitelist_invalid` | sound/action/effect 不在白名单。 | 只使用已接受 ID，不要传路径或 URL。 |

## 安全边界

- 本地 API 只监听 `127.0.0.1`。
- Agent 只能发送结构化状态事件，不能直接控制 UI。
- Codex 不能通过该接入直接操作桌宠窗口。
- JSONL monitor 只能解析结构化 event type，不能把 terminal text 或 transcript 当状态接口。
- 不允许把本地文件路径、URL 或上传资源作为 sound/profile ID。
- 不要打印、提交或公开 token。
- 不要对每个文件、每行日志、每个微小步骤刷事件；只在状态阶段变化时发送。
