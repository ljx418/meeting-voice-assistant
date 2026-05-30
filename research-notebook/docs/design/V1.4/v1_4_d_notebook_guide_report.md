# ResearchNotebook V1.4-D Notebook Guide Report

日期：2026-05-26

## 阶段结论

V1.4-D Notebook Guide 达到 PASS_LIMITED。

已完成：

- data_service 新增 `GET /api/workspaces/{workspace_id}/guide`。
- Guide 返回 Overview、Key Topics、Suggested Questions。
- Guide evidence_refs 使用 registry source_id、DocumentUnit unit_id、EvidenceSpan evidence_id。
- 无来源时返回稳定 `no_sources` 空状态。
- ResearchNotebook 中列默认展示真实 Guide 数据。
- 点击 Suggested Question 会直接进入带证据问答。

## 限定范围

- 当前 Guide 是后端确定性 source-grounded 导读，不声明 Claude / LLM 质量摘要 ready。
- 当前只基于已导入来源、DocumentUnit 和 EvidenceSpan 生成简洁 Guide。
- 不声明跨 Notebook Guide、长文档深度综合、冲突分析或 Research 输出 ready。

## 验证结果

后端 focused tests：

```text
python3 -m pytest backend/tests/test_target_http_notebook_guide.py backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_document_units.py backend/tests/test_target_http_evidence_spans.py -q
25 passed
```

前端 focused tests：

```text
npm run test -- src/shared/api/dataServiceClient.test.ts src/features/workspaces/WorkspacePage.test.tsx
94 passed
```

## 风险评估

规格漂移风险：MEDIUM

原因：PRD 使用“自动生成 Notebook Guide”表述，当前实现是确定性导读，不是完整 AI 综合摘要。

收敛措施：所有文档和 UI 只声明 PASS_LIMITED，不声明完整 AI Guide ready。

虚假验收风险：MEDIUM

原因：用户可能把 Guide-first UI 误认为完整 NotebookLM 级别导读。

收敛措施：保留 Source-grounded Chat、Studio 输出和资料不足拒答的后续阶段，不把 V1.4-D 单独作为 Phase 1 完成。

结论：无 HIGH 风险，可以进入 V1.4-E Source-grounded Chat。

## 下一阶段

V1.4-E Source-grounded Chat。

目标：

- 资料不足时明确拒答。
- 给出补源建议和添加来源入口。
- 区分来源结论和推断/解释。
- 保持关键断言带引用。
