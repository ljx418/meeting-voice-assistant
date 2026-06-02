# ResearchNotebook V2.1 PRD MVP Gap Closure

日期：2026-06-02

## 阶段目标

补齐 Phase 1 中仍未完整产品化的能力，包括 Sources 搜索、Notes 管理、Notebook 删除语义、Studio artifact 管理、AI 质量闭环。

## 开发内容

1. **Sources 搜索入口**
   - 支持按标题、类型、正文片段搜索
   - 搜索结果可打开 SourcePreview / DocumentUnit
   - 搜索失败不清空来源列表

2. **Notes 保存与管理**
   - 从回答保存到 Notes
   - 从来源摘录保存到 Notes
   - 支持用户手写 note
   - 支持 note 编辑、删除、citation 跳转

3. **Notebook 删除语义**
   - 决策归档是否满足 PRD 删除
   - 若不满足，补安全删除、确认弹窗和资源处理策略

4. **Studio artifact 管理**
   - 输出列表、重命名、删除、重新生成、导出状态

5. **AI Guide / QA / Studio 质量闭环**
   - 修复 fallback / schema mismatch
   - 从 `REVIEWED_WITH_LIMITATIONS` 推进到可人工确认的 `PASS_LIMITED`

## 验收标准

- 用户能搜索来源并打开 SourcePreview / DocumentUnit
- 用户能把回答或摘录保存为 Note
- Notes 保留 evidence_refs
- Studio artifact 可管理且不丢失 citation
- Guide 可用性 >= 4/5
- citation 可定位率 >= 90%
- 拒答正确率 >= 80%
- 高危幻觉 = 0

## 出门状态

- `PRD_MVP_GAP_CLOSURE_PASS_LIMITED`

## 文档索引

| 文档 | 用途 |
| --- | --- |
| `v2_1_prd_mvp_gap_closure_plan.md` | 阶段开发计划 |
| `v2_1_prd_mvp_gap_closure_plan_audit.md` | 计划审计 |
| `v2_1_prd_mvp_gap_closure_report.md` | 阶段报告 |

## 统一门禁

每个子阶段必须先完成：
1. 阶段开发计划
2. 阶段验收计划
3. 计划审计
4. 规格漂移风险评估
5. 虚假验收风险评估

若任一风险为 HIGH，停止并重新审计，不进入实现。

每个子阶段完成后必须执行：
1. 自动化 smoke
2. 真实数据验收
3. PRD 规格检视
4. 人工质量评分（若涉及内容质量）
5. 阶段报告
6. 覆盖矩阵更新