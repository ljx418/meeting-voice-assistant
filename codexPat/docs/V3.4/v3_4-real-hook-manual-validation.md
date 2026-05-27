# V3.4 Real Codex Hook Manual Validation

status: ready-for-operator

date: 2026-05-24

## Purpose

This document is the manual validation checklist for V3.4 real Codex hook lifecycle evidence.

V3.4 fixture smoke has passed, but full V3.4 acceptance remains blocked until a real Codex session:

- is launched through `petctl codex launch`.
- has `AGENT_DESKTOP_PET_INSTANCE_ID`.
- reviews and trusts `.codex/hooks.json` through `/hooks`.
- produces observable hook-driven pet state changes.

## Current Boundary

Allowed after fixture smoke only:

```text
V3.4 Codex hook wrapper fixture smoke passed.
```

Not allowed until this manual validation passes:

```text
V3.4 Codex hooks state mapping smoke passed for tested local Codex hook scenarios.
```

Still forbidden:

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

## Preconditions

Run from repo root:

```bash
cd /Users/Zhuanz/Desktop/workspace/codexPat
```

Confirm desktop app health:

```bash
curl -sS http://127.0.0.1:17321/api/health
```

If not running:

```bash
open "apps/desktop/src-tauri/target/release/bundle/macos/Agent Desktop Pet.app"
```

Build `petctl`:

```bash
pnpm --filter @agent-desktop-pet/petctl build
```

Confirm hook files exist:

```bash
test -f .codex/hooks.json
test -f scripts/codex-pet-hook.mjs
```

## Step 1：Launch A Bound Codex Session

Run in a normal terminal:

```bash
node packages/petctl/dist/cli.js codex launch --name "V3.4 Hook Cat" --
```

Expected:

- A new Codex session opens/runs under the wrapper.
- A new pet instance is created.
- The new Codex process receives `AGENT_DESKTOP_PET_INSTANCE_ID`.
- The target cat enters `running` at session start.

Operator record:

```text
status:
target cat name:
target instance visible:
initial state observed:
notes:
```

## Step 2：Review And Trust Hooks

Inside the newly launched Codex session, type:

```text
/hooks
```

Review the project hook config. Expected hook commands:

```text
node scripts/codex-pet-hook.mjs SessionStart
node scripts/codex-pet-hook.mjs UserPromptSubmit
node scripts/codex-pet-hook.mjs PreToolUse
node scripts/codex-pet-hook.mjs PermissionRequest
node scripts/codex-pet-hook.mjs PostToolUse
node scripts/codex-pet-hook.mjs Stop
```

Trust only if:

- Commands point to `scripts/codex-pet-hook.mjs`.
- No unexpected shell, network, credential, or destructive command appears.
- No command prints token, Authorization header, raw hook stdin, transcript path, config path, workspace path, or full local path.

Operator record:

```text
status:
hooks reviewed:
hooks trusted:
unexpected hook command observed:
notes:
```

## Step 3：Validate UserPromptSubmit -> thinking

Inside the bound Codex session, submit:

```text
请简单说明当前目录是做什么的，不要修改文件。
```

Expected:

- After prompt submit, target cat enters `thinking`.
- Event routes only to `V3.4 Hook Cat`.
- Default cat and other Codex cats are not affected.

Operator record:

```text
status:
thinking observed:
wrong cat changed:
notes:
```

## Step 4：Validate PreToolUse -> running

Ask Codex to inspect files:

```text
请列出当前目录文件，不要修改文件。
```

Expected:

- Before or during tool use, target cat enters `running`.
- No tool command text is printed by the hook wrapper.
- No raw hook stdin appears in terminal output.

Operator record:

```text
status:
running observed:
raw hook stdin printed:
tool command leaked:
notes:
```

## Step 5：Validate PostToolUse Failure -> error

Ask Codex to run a failing command:

```text
请运行一个必然失败的命令：false。不要修复它，只观察结果。
```

Expected:

- Target cat enters `running` before tool use.
- If Codex hook payload exposes a stable failure field, target cat enters `error`.
- If `Stop -> success` immediately overwrites `error`, record both observations.

Accepted outcomes:

- `passed`: `error` visibly observed.
- `blocked`: no stable failure signal appears in hook payload or `error` cannot be observed before `Stop`.
- `failed`: hook runs but routes to the wrong cat or leaks sensitive data.

Operator record:

```text
status:
error observed:
overwritten by Stop:
wrong cat changed:
notes:
```

## Step 6：Validate PermissionRequest -> need_input

Trigger a permission prompt if possible. The exact trigger depends on the active Codex sandbox and approval policy.

Suggested prompt:

```text
请尝试执行一个需要我批准的高风险命令，但在请求批准前不要解释太多。
```

Expected:

- If Codex emits `PermissionRequest`, target cat enters `need_input`.
- If the environment does not emit `PermissionRequest`, mark this case `blocked`, not failed.

Operator record:

```text
status:
permission prompt observed:
need_input observed:
wrong cat changed:
notes:
```

## Step 7：Validate Stop -> success

Submit a simple request that completes successfully:

```text
请回复一句：V3.4 hook stop check complete。
```

Expected:

- At turn completion, target cat enters `success`.
- This does not prove all Codex workflows succeeded; it only proves the `Stop` mapping.

Operator record:

```text
status:
success observed:
notes:
```

## Step 8：Run Real Lifecycle Gate

After hook review/trust is complete, run from a normal terminal:

```bash
CODEX_PET_HOOK_TRUST_CONFIRMED=1 node scripts/v3_4_codex_hook_real_lifecycle_smoke.mjs
```

Expected:

- Codex CLI available: passed.
- petctl dist exists: passed.
- project hook config exists: passed.
- Codex hook trust review: passed.
- real lifecycle trigger remains manual unless automated evidence is added.

Operator record:

```text
status:
command exit:
notes:
```

## Security Checklist

Mark each item:

```text
token printed: no / yes
Authorization header printed: no / yes
raw hook stdin printed: no / yes
raw payload printed: no / yes
prompt text echoed by hook wrapper: no / yes
tool input command leaked by hook wrapper: no / yes
transcript path printed: no / yes
config path printed: no / yes
workspace path printed: no / yes
full local path printed: no / yes
```

Any `yes` is a hard failure unless it came from Codex itself outside hook wrapper evidence and is explicitly documented as unrelated.

## Final Manual Decision Template

Copy this block into `docs/V3.4/evidence/codex-hook-real-lifecycle-smoke-2026-05-24.md` after validation:

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

## Pass Rule

Full V3.4 manual validation can pass only if:

- hooks were trusted through `/hooks`.
- at least `UserPromptSubmit`, `PreToolUse`, and `Stop` were observed in the real bound Codex session.
- `PostToolUse failure` is passed or explicitly blocked with reason.
- `PermissionRequest` is passed or explicitly blocked with reason.
- no sensitive output leakage occurred.
- no forbidden claim is used as ready.
