# V1.9-B Conflict Labeling Report

日期：2026-05-31

## 当前状态

`PASS_LIMITED`

## 命令

```bash
npm run smoke:v1.9-conflict-labeling
```

## 验收结果

| 项 | 状态 |
| --- | --- |
| target route probe | PASS |
| workspace create | PASS |
| conflict source import | PASS |
| research report returned | PASS |
| conflict detected in `conflicts` | PASS |
| conflict evidence resolution | PASS |
| cleanup | PASS |

## 关键发现

V1.9-B 使用两份真实冲突样本：

- 乐观口径：数字人项目 Alpha 在 2026 年已经实现规模化商业化。
- 保守口径：数字人项目 Alpha 在 2026 年尚未实现规模化商业化。

后端 Research report 的 `supported_conclusions` 同时返回了上述两条相反结论，并带有 evidence_refs。

V1.9-B 修复后，Research report 已将两条相反结论提升为 structured `conflicts`：

- topic：数字人项目 Alpha 2026 年规模化商业化状态
- position 1：已经实现规模化商业化
- position 2：尚未实现规模化商业化

两个 position 均带有可解析 evidence_refs。

因此可以声明 approved V1.9 conflict dataset 的 `PASS_LIMITED`，但不能声明 all-domain conflict labeling ready。

## Fixture

- `fixtures/real/v1_9/conflict-labeling/research-conflict.json`
- `fixtures/real/v1_9/conflict-labeling/v1_9_b_conflict_labeling_result.json`
- `fixtures/real/v1_9/conflict-labeling/conflict-evidence-unit.json`
- `fixtures/real/v1_9/conflict-labeling/conflict-evidence-span.json`

## 决策

Conflict labeling is `PASS_LIMITED` for the approved V1.9 conflict dataset.

限制：该结果不代表 all-domain conflict detection ready，仍需人工语义审查确认冲突主题和立场表达质量。
