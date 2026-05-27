# V3.4 真实 Codex Hook 手工验收

状态：ready-for-operator

日期：2026-05-24

## 目的

本文档用于完成 V3.4 真实 Codex hook lifecycle 的手工验收。

当前 V3.4 fixture smoke 已通过，但完整 V3.4 acceptance 仍是 blocked。必须完成真实 Codex 会话里的 hook review / trust，并观察到 hook 驱动的猫状态变化后，才能允许真实 lifecycle 相关声明。

## 当前声明边界

fixture smoke 通过后，仅允许声明：

```text
V3.4 Codex hook wrapper fixture smoke passed.
```

在本文档的真实手工验收完成前，不能声明：

```text
V3.4 Codex hooks state mapping smoke passed for tested local Codex hook scenarios.
```

仍禁止声明：

```text
Codex internal reasoning exact mapping ready
ModelThinkingStart / ModelThinkingEnd verified
OS-level Codex window binding ready
all Codex workflows verified
Claude Code integration verified
MCP ready
Third-party agent integration verified
Windows ready
cross-platform ready
USB ready
production signed release ready
per-instance queue ready
```

## 前置条件

进入项目目录：

```bash
cd /Users/Zhuanz/Desktop/workspace/codexPat
```

确认桌宠 app 正在运行：

```bash
curl -sS http://127.0.0.1:17321/api/health
```

如果没有返回 `ok: true`，先启动桌宠：

```bash
open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"
```

构建 `petctl`：

```bash
pnpm --filter @agent-desktop-pet/petctl build
```

确认 hook 文件存在：

```bash
test -f .codex/hooks.json
test -f scripts/codex-pet-hook.mjs
```

## Codex 窗口如何绑定到单个猫实例

V3.4 的绑定不是通过读取 macOS 窗口句柄完成的，而是通过 **wrapper-first session binding** 完成：

```text
petctl codex launch
  -> 调用 /api/instances 创建一个 Codex PetInstance
  -> 获得 instanceId
  -> 把 AGENT_DESKTOP_PET_INSTANCE_ID 注入到新 Codex 子进程环境变量
  -> 当前 Codex 会话里的 hooks 继承这个环境变量
  -> scripts/codex-pet-hook.mjs 调用 petctl notify
  -> petctl notify 自动读取 AGENT_DESKTOP_PET_INSTANCE_ID
  -> 事件只路由到这个 instanceId 对应的猫
```

也就是说，“一个 Codex 窗口/会话绑定一只猫”的关键是：

```text
同一个 Codex 子进程环境里只有一个 AGENT_DESKTOP_PET_INSTANCE_ID。
```

hook wrapper 不需要知道窗口 ID，也不需要控制 UI。它只通过当前进程环境变量找到目标猫。

### 正确绑定方式

必须使用 wrapper 启动新的 Codex 会话：

```bash
node packages/petctl/dist/cli.js codex launch --name "V3.4 Hook Cat" --
```

这个命令会创建一只新猫，并把它的 `instanceId` 注入到新 Codex 会话。

### 错误方式

不要直接在普通终端里运行：

```bash
codex
```

这种方式不会自动创建猫，也不会注入 `AGENT_DESKTOP_PET_INSTANCE_ID`。即使 hook 触发，`scripts/codex-pet-hook.mjs` 也会安全 no-op，无法证明窗口绑定。

也不要在当前未绑定的旧 Codex 窗口里验收 V3.4 real hooks。当前窗口如果没有 `AGENT_DESKTOP_PET_INSTANCE_ID`，就不是有效验收窗口。

### 绑定关系验证

在 wrapper 启动的新 Codex 会话里，可以让 Codex 执行：

```text
请运行：printenv AGENT_DESKTOP_PET_INSTANCE_ID
```

预期：

- 命令输出一个类似 `codex_...` 的 instanceId。
- 该 instanceId 能在以下命令输出中找到：

```bash
node packages/petctl/dist/cli.js list --json
```

如果 `printenv AGENT_DESKTOP_PET_INSTANCE_ID` 没有输出，说明当前 Codex 窗口没有绑定猫，不能继续做 V3.4 real hook 验收。

### 单实例隔离验证

在绑定 Codex 会话里执行：

```text
请运行：node packages/petctl/dist/cli.js notify --level thinking --title "binding check"
```

预期：

- 只有 `V3.4 Hook Cat` 进入 `thinking`。
- 默认猫不变化。
- 其他 Codex 猫不变化。

这个用例先证明“当前 Codex 窗口 -> 单个猫实例”的绑定关系，再继续验证 hooks。

## 步骤 1：启动一个已绑定的 Codex 会话

在普通终端中执行：

```bash
node packages/petctl/dist/cli.js codex launch --name "V3.4 Hook Cat" --
```

预期结果：

- 新 Codex 会话由 wrapper 启动。
- 新猫实例被创建。
- 新 Codex 进程继承 `AGENT_DESKTOP_PET_INSTANCE_ID`。
- 目标猫在 session start 时进入 `running`。
- `printenv AGENT_DESKTOP_PET_INSTANCE_ID` 能输出该猫对应的 `instanceId`。

记录：

```text
状态：
目标猫名称：
目标实例是否可见：
AGENT_DESKTOP_PET_INSTANCE_ID 是否存在：
初始状态是否观察到：
备注：
```

## 步骤 2：Review 并 Trust Hooks

在新启动的 Codex 会话中输入：

```text
/hooks
```

检查项目 hook 配置。预期只能看到以下命令：

```text
node scripts/codex-pet-hook.mjs SessionStart
node scripts/codex-pet-hook.mjs UserPromptSubmit
node scripts/codex-pet-hook.mjs PreToolUse
node scripts/codex-pet-hook.mjs PermissionRequest
node scripts/codex-pet-hook.mjs PostToolUse
node scripts/codex-pet-hook.mjs Stop
```

如果 `/hooks` 显示所有事件都是：

```text
Installed 0
Active 0
```

说明 Codex 没有加载 hook 配置。先检查 `.codex/hooks.json` 是否是 Codex 0.131 支持的三层结构：

```text
事件名 -> matcher group -> hooks array -> command hook
```

正确结构示例：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "node scripts/codex-pet-hook.mjs PreToolUse",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

修正后需要退出当前 Codex 会话，并重新通过下面命令启动：

```bash
node packages/petctl/dist/cli.js codex launch --name "V3.4 Hook Cat" --
```

然后再次输入：

```text
/hooks
```

预期至少目标事件的 `Installed` 不再是 `0`。

只有在满足以下条件时才 trust：

- 命令指向 `scripts/codex-pet-hook.mjs`。
- 没有意外 shell、外网、凭据读取或破坏性命令。
- 命令不会打印 token、Authorization header、raw hook stdin、transcript path、config path、workspace path 或完整本地路径。

记录：

```text
状态：
是否已 review hooks：
是否已 trust hooks：
是否看到意外 hook 命令：
备注：
```

## 步骤 3：验证 UserPromptSubmit -> thinking

在已绑定的 Codex 会话中提交：

```text
请简单说明当前目录是做什么的，不要修改文件。
```

预期结果：

- 提交 prompt 后，目标猫进入 `thinking`。
- 事件只路由到 `V3.4 Hook Cat`。
- 默认猫和其他 Codex 猫不受影响。

记录：

```text
状态：
是否观察到 thinking：
是否有错误猫被改变：
备注：
```

## 步骤 4：验证 PreToolUse -> running

让 Codex 检查文件：

```text
请列出当前目录文件，不要修改文件。
```

预期结果：

- 工具调用前或工具调用期间，目标猫进入 `running`。
- hook wrapper 不打印 tool command 原文。
- 终端中不出现 raw hook stdin。

记录：

```text
状态：
是否观察到 running：
是否打印 raw hook stdin：
是否泄露 tool command：
备注：
```

## 步骤 5：验证 PostToolUse failure -> error

让 Codex 执行一个失败命令：

```text
请运行一个必然失败的命令：false。不要修复它，只观察结果。
```

预期结果：

- 工具调用前，目标猫进入 `running`。
- 如果 Codex hook payload 暴露稳定失败字段，目标猫进入 `error`。
- 如果 `Stop -> success` 很快覆盖了 `error`，需要记录两个状态都曾出现。

可接受结果：

- `passed`：明确观察到 `error`。
- `blocked`：hook payload 没有稳定失败信号，或 `error` 在 `Stop` 覆盖前无法观察。
- `failed`：hook 运行但路由到了错误猫，或泄露敏感信息。

记录：

```text
状态：
是否观察到 error：
是否被 Stop 覆盖：
是否有错误猫被改变：
备注：
```

## 步骤 6：验证 PermissionRequest -> need_input

尝试触发权限请求。具体是否能触发取决于当前 Codex sandbox 和 approval policy。

建议 prompt：

```text
请尝试执行一个需要我批准的高风险命令，但在请求批准前不要解释太多。
```

预期结果：

- 如果 Codex 发出 `PermissionRequest`，目标猫进入 `need_input`。
- 如果当前环境没有发出 `PermissionRequest`，该用例记为 `blocked`，不是 `failed`。

记录：

```text
状态：
是否出现 permission prompt：
是否观察到 need_input：
是否有错误猫被改变：
备注：
```

## 步骤 7：验证 Stop -> success

提交一个可以成功完成的简单请求：

```text
请回复一句：V3.4 hook stop check complete。
```

预期结果：

- 回合完成时，目标猫进入 `success`。
- 这只证明 `Stop` 映射，不证明所有 Codex workflow 成功。

记录：

```text
状态：
是否观察到 success：
备注：
```

## 步骤 8：运行 Real Lifecycle Gate

完成 `/hooks` review / trust 后，在普通终端执行：

```bash
CODEX_PET_HOOK_TRUST_CONFIRMED=1 node scripts/v3_4_codex_hook_real_lifecycle_smoke.mjs
```

预期结果：

- Codex CLI available: passed。
- petctl dist exists: passed。
- project hook config exists: passed。
- Codex hook trust review: passed。
- 真实 lifecycle 观察仍以本文档手工记录为准，除非后续补自动化 evidence。

记录：

```text
状态：
命令退出码：
备注：
```

## 安全检查

逐项标记：

```text
是否打印 token：no / yes
是否打印 Authorization header：no / yes
是否打印 raw hook stdin：no / yes
是否打印 raw payload：no / yes
hook wrapper 是否回显 prompt text：no / yes
hook wrapper 是否泄露 tool input command：no / yes
是否打印 transcript path：no / yes
是否打印 config path：no / yes
是否打印 workspace path：no / yes
是否打印完整本地路径：no / yes
```

任一项为 `yes` 都是 hard failure，除非能证明它来自 Codex 自身正常输出、与 hook wrapper evidence 无关，并且已明确记录。

## 最终记录模板

验收完成后，把下面内容复制到：

```text
docs/V3.4/evidence/codex-hook-real-lifecycle-smoke-2026-05-24.md
```

模板：

```text
Codex CLI version:
Hook trust:
Bound instance:

Observed:
- SessionStart -> running:
- UserPromptSubmit -> thinking:
- PreToolUse -> running:
- PermissionRequest -> need_input:
- PostToolUse failure -> error:
- Stop -> success:

Security:
- token printed:
- Authorization header printed:
- raw hook stdin printed:
- local path printed:

Final:
real lifecycle smoke: passed / blocked / failed

Notes:
```

## 通过规则

V3.4 真实手工验收通过条件：

- hooks 已通过 `/hooks` review / trust。
- 真实绑定 Codex 会话中至少观察到 `UserPromptSubmit`、`PreToolUse`、`Stop`。
- `PostToolUse failure` 通过，或明确记录 blocked 原因。
- `PermissionRequest` 通过，或明确记录 blocked 原因。
- 没有敏感输出泄露。
- 没有把 forbidden claims 当成 ready claims。
