# V2.16 Phase 78 验收计划：Runtime Profile Manager

## 1. 验收目标

验证 runtime profile 能替代散落命令执行，并保持 default-deny 安全边界。

## 2. 必测断言

- `profiles.json` 落盘。
- 每个 profile 有 `profile_id`、`profile_type`、`command_id`、`allowed_args_policy`、`timeout_seconds`、`writes_source=false`。
- 非 profile_id 执行返回 `RUNTIME_PROFILE_NOT_REGISTERED`。
- profile run 不泄露绝对路径。
- run status 属于 `passed | failed | timeout | blocked`。

## 3. 三端验收

HTTP / MCP / CLI 需比较：

- `schema_version`
- `summary`
- profile ids
- run status
- artifact refs
- warnings / unresolved count

## 4. 打回条件

- 任意命令可绕过 profile。
- profile run 修改源码。
- failed / timeout 被包装成 passed。
- logs 泄露绝对路径或 secret。
