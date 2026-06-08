# V2.16 Phase 81 开发计划：Human-Gated Patch Sandbox

## 1. 阶段定位

Phase 81 在 V2.12 Safe Patch Plan 基础上增加 patch sandbox preview。系统可以生成 preview、diff、rollback 和 validation links，但未获人工高风险审批前不得 apply。

## 2. In Scope

- 生成 patch preview artifact。
- 生成 diff text artifact。
- 生成 rollback plan。
- 记录 approval state。
- apply without approval 返回 blocked。
- HTTP / MCP / CLI create/read/apply-blocked。

## 3. Out of Scope

- 默认真实修改源码。
- git commit / push / reset / restore。
- 自动解决冲突。

## 4. Artifact

```text
workspace/assets/codebase/{codebase_id}/coding_agent/v2_16/patch_sandbox/
  previews/{preview_id}.json
  diffs/{preview_id}.diff
```

## 5. 出门条件

- preview 阶段 source hash 不变。
- apply without approval blocked。
- preview 包含 diff、rollback、validation profiles。
- public payload 不泄露绝对路径。
