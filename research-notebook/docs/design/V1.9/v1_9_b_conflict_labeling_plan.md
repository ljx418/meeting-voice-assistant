# V1.9-B Conflict Labeling Plan

日期：2026-05-30

## 目标

使用真实冲突样本验证 Research `conflicts` 字段，而不是只验证字段存在。

## 验收

- 至少两个来源对同一问题给出不同口径。
- Research report 中 `conflicts` 至少 1 条。
- conflict 包含 topic 和至少两个 positions。
- 每个 position 有 evidence_refs。
- 至少一个 conflict evidence 可解析到 DocumentUnit / EvidenceSpan。
- 如果后端未识别冲突，记录 NOT_READY，不伪造 PASS。

## 命令

```bash
npm run check
npm run smoke:v1.9-conflict-labeling
```
