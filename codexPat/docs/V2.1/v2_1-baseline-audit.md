# V2.1 Integration Baseline Audit

status: passed  
date: 2026-05-18 17:20:16 CST

## Purpose

确认进入 V2.1 真实 Agent 验证前，V2.0 已有接入基线是否足够支撑 Codex、Claude Code 和自定义 Agent smoke。

## Current Integration State

| Area | Current state | V2.1 implication |
| --- | --- | --- |
| `petctl` | 已支持 `notify`、参数模式、JSON stdin、本地校验、token/url 读取和 HTTP 写入。 | 作为 Codex、Claude Code hook、shell 和 Node 的主要写入路径。 |
| HTTP API | 已支持 `GET /api/health`、`GET /api/capabilities`、`POST /api/events`、`GET /api/diagnostics`。 | third-party agent 可直接接入；所有真实 smoke 必须能在 diagnostics 看到 source。 |
| diagnostics | 已显示 accepted/rejected summaries、queue、sound decision，不暴露 token/payload/metadata 全量。 | 作为真实接入验收的主要证据源。 |
| Codex template | `skills/codex-agent-pet/SKILL.md` 已存在，source 固定为 `codex.local` / `codex` / `Codex`。 | 仍未完成真实 Codex CLI smoke，不能声明 verified。 |
| Claude Code template | `skills/claude-agent-pet/SKILL.md` 已存在，source 固定为 `claude-code.local` / `claude_code` / `Claude Code`。 | 仍未完成真实 Claude Code skill/hook smoke，不能声明 verified。 |
| shell example | `examples/shell/task-with-pet.sh` 已存在，使用 `--` 分隔命令并保留 exit code。 | 作为 baseline regression。 |
| Node example | `examples/node/notify-pet.mjs` 已存在，使用 `spawnSync` 调用 `petctl`。 | 作为 baseline regression；要求 `petctl` 在 PATH 中可用。 |

## Baseline Acceptance Result

- Automatic baseline checks passed, with only non-blocking doctor WARN items.
- HTTP bridge launched and listened on `127.0.0.1:17321`.
- curl / Node / Python third-party HTTP success examples were accepted.
- diagnostics showed `curl.local`, `http-node.local`, `http-python.local`, and `load.local`.
- rate limit smoke returned `429 rate_limited` after rapid events.
- rejected reason sanitization passed: invalid sound paths, invalid sound URLs, and invalid source IDs were rejected without being echoed in HTTP responses or diagnostics.

## Current Blockers For Verified Claims

- 尚未在真实 Codex CLI 任务中验证 `codex.local`。
- 尚未在真实 Claude Code skill 任务中验证 `claude-code.local`。
- 尚未在真实 Claude Code hook 配置中验证 `claude-code.local`。
- third-party local HTTP contract smoke 已通过；这仍不等于真实第三方 agent 产品集成已验证。
