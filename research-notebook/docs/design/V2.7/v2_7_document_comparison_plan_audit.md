# V2.7 Document Comparison Plan Audit

日期：2026-06-02

## 审计结论

**当前状态**：待审计

## 审计检查表

### 规格漂移风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| 不把 Research report 伪装成 Compare | ✅ | 计划明确区分 Research 和 Compare |
| Compare schema 与 PRD 一致 | ⏳ | CompareResult 结构需要确认 |
| evidence binding 覆盖 | ⏳ | Conflict.evidence_a/b 需要确认 |
| 不声明 all document types ready | ✅ | 计划限制为受限 MVP |

### 虚假验收风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| Pairwise comparison 测试 | ⏳ | 需要验证 2 个文档对比 |
| Multi-document comparison 测试 | ⏳ | 需要验证 3+ 文档对比 |
| evidence binding 验证 | ⏳ | 需要验证 conflict 两侧有 evidence_refs |
| 人工质量审查标准 | ⏳ | 审查标准是否明确 |

### 实现风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| Comparison generator 可用性 | ⏳ | 需要确认是否有 generator |
| Compare artifact schema 与后端对齐 | ⏳ | ComparisonResult 结构需要确认 |
| 前端 Comparison UI 实现 | ⏳ | 需要新增 ComparePanel 组件 |
| 与 Research report 的关系 | ⏳ | Compare 依赖 conflict detection 能力 |

## 审计结论

**规格漂移风险**：MEDIUM
- 需要明确 Compare 和 Research 的区别

**虚假验收风险**：MEDIUM
- 需要验证 evidence binding 完整性

**实现风险**：MEDIUM
- 依赖 comparison generator 能力
- 需要确认与 Research 的关系

**是否可以进入实现**：需要确认

### 关键决策点

1. Compare vs Research：Compare 是文档间对比，Research 是基于 source 回答问题
2. Evidence binding：conflict 两侧都需要有 evidence_refs

### 前置确认事项

- [ ] 确认是否有 comparison generator
- [ ] 若有，确认 Compare artifact schema（similarities、differences、conflicts）
- [ ] 确认 comparison UI 设计
- [ ] 确认人工质量审查标准

若有 generator，审计通过后进入实现。
若无 generator，保持 NOT_READY。