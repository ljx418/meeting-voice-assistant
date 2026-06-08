# V2.16 Phase 81 验收计划：Human-Gated Patch Sandbox

## 1. 验收目标

验证 patch sandbox 只生成预览和审批状态，不在默认路径修改源码。

## 2. 必测断言

- preview artifact 存在。
- diff artifact 存在。
- `mutates_source=false`。
- `approval_state.status=approval_required`。
- apply without approval 返回 `PATCH_APPLY_REQUIRES_HUMAN_APPROVAL`。
- 预览前后目标文件 hash 不变。

## 3. 打回条件

- preview 修改源码。
- apply without approval 修改源码。
- 生成 git commit/push/reset/restore。
- diff 或 rollback 缺失。
