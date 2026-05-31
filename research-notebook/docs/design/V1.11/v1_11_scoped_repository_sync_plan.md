# V1.11 Scoped Repository Sync / Release Handoff Plan

日期：2026-05-31

## 审查结论

`CONDITIONAL GO`

V1.11 只允许执行仓库同步收口，不做功能开发，不扩大 ready 声明。由于当前 git remote 与子项目名称不一致，commit / push 必须等待人工确认。

## Entry Gate

1. V1.x final PRD acceptance 为 `V1_X_FINAL_ACCEPTANCE_PASS_LIMITED`。
2. `npm run smoke:v1.x-rc` 通过。
3. `npm run check` 通过。
4. `.smoke-artifacts/` 不进入 git。
5. V1.x fixtures / docs 不包含本地绝对路径、cache path、artifact physical path、API key。
6. git root / remote / branch 已记录。
7. 用户确认当前 remote 是 ResearchNotebook 目标远端。
8. 用户确认允许在上层 workspace 仓库提交 `research-notebook/` 子目录。

如果第 7 或第 8 项未确认，停止在 `BLOCKED_BY_REMOTE_CONFIRMATION`。

## 允许操作

- 复跑 V1.9 / V1.x final smoke。
- 复跑 `npm run check`。
- 输出 scoped git status / diff。
- 更新 V1.11 sync report。
- 在人工确认 remote 后执行 scoped staging。
- commit / push 并记录 hash / branch / remote。

## 禁止操作

- 不做功能开发。
- 不进入 V2。
- 不修改 data_service。
- 不使用 `git add .`。
- 不提交 `.smoke-artifacts/`。
- 不混入 sibling project。
- 不把 `PASS_LIMITED` 写成 full ready。
- 不声明 OCR / Audio / PPT / Mindmap / Compare ready。

## 必跑命令

```bash
npm run smoke:v1.9-rc
npm run smoke:v1.x-rc
npm run check
git status --short -- .smoke-artifacts
find docs/design -name "*.bkp" -print
```

## Boundary / Hygiene

执行敏感信息扫描，覆盖本地绝对路径、文件 URI、缓存路径、物理制品路径、密钥与鉴权字段等模式。

验收：

- 命中仅允许出现在 redaction / guard regex。
- fixtures 和 docs 不得出现敏感路径或 API key。

## Scoped Staging 建议

如果确认当前 remote 正确，只允许 staging ResearchNotebook 范围。禁止 `git add .`。

最小 V1.x/V1.11 staging：

```bash
git add research-notebook/package.json \
  research-notebook/scripts/v1_x_interactive_acceptance_capture.mjs \
  research-notebook/scripts/v1_x_rc_final_prd_acceptance.mjs \
  research-notebook/docs/design/V1.x \
  research-notebook/docs/design/V1.11 \
  research-notebook/fixtures/real/v1_x
```

如需一次同步 V1.7-V1.10 历史阶段，必须先人工确认 staged diff。

## 完成声明上限

如果 commit / push 成功，最多声明：

```text
ResearchNotebook V1.x PASS_LIMITED release handoff is committed and pushed.
```

仍不能声明 all-source / all-domain / OCR / Phase 2/3 ready。
