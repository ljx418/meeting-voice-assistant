# ResearchNotebook V1.4-RC Final Acceptance Report

日期：2026-05-26

## 最终结论

V1.4-RC 达到 PASS_LIMITED。

当前可以声明：

- PRD Phase 1 的三列 Notebook 主界面已落地。
- Notebook 生命周期达到受限可用。
- PDF / TXT / Markdown P0 来源导入达到受限可用。
- Notebook Guide 达到受限可用。
- Source-grounded Chat 支持引用问答、资料不足拒答和补源建议。
- Studio Notes / Study Guide / Briefing Doc / FAQ 达到受限可用。
- Chat / Studio citation 可进入来源预览、DocumentUnit 和 EvidenceSpan 受限定位。

不能声明：

- Claude / LLM 高质量 Guide 或 Studio 输出 ready。
- 扫描版 PDF / OCR ready。
- all-source-type precise backjump ready。
- all-session precise navigation ready。
- Audio Overview、PPT、思维导图、文档对比 ready。
- 完整 Research、冲突分析、联网搜索 ready。
- Cloud sync / collaboration ready。

## 验证命令

后端 focused tests：

```text
python3 -m pytest backend/tests/test_target_http_source_preview.py backend/tests/test_target_http_document_units.py backend/tests/test_target_http_evidence_spans.py backend/tests/test_target_http_notebook_guide.py backend/tests/test_target_http_studio_artifacts.py -q
30 passed
```

前端 focused tests：

```text
npm run test -- src/shared/api/dataServiceClient.test.ts src/features/workspaces/WorkspacePage.test.tsx
97 passed
```

全量前端 check：

```text
npm run check
Boundary checks passed
124 passed
build passed
```

真实来源 smoke：

```text
npm run smoke:v1.4-sources-p0
FINAL PASS_LIMITED
```

覆盖：

- Markdown import / preview / query citation。
- TXT import / preview / query citation。
- PDF browser upload import / PDF_EXTRACTED preview / query citation。
- workspace build。
- cleanup。

## 阶段状态

| 阶段 | 状态 |
| --- | --- |
| V1.4-0 PRD 重基线 | PASS |
| V1.4-A 三列 Notebook | PASS_LIMITED |
| V1.4-B Notebook 生命周期 | PASS_LIMITED |
| V1.4-C Sources P0 | PASS_LIMITED |
| V1.4-D Notebook Guide | PASS_LIMITED |
| V1.4-E Source-grounded Chat | PASS_LIMITED |
| V1.4-F Studio 轻量输出 | PASS_LIMITED |
| V1.4-G Citation navigation | PASS_LIMITED |
| V1.4-H 补源入口 | PASS_LIMITED |
| V1.4-RC 自动化集中验收 | PASS_LIMITED |

## 风险评估

规格漂移风险：MEDIUM

原因：PRD 描述是 AI 驱动研究助手，并指定 Claude API；当前 V1.4 输出仍是确定性 source-grounded 合同和模板化轻量输出。

虚假验收风险：MEDIUM

原因：如果把 PASS_LIMITED 说成完整 NotebookLM 级体验，会造成虚假验收。

收敛措施：

- 所有 ready 声明均限定为 PASS_LIMITED。
- 不声明高质量 AI 生成 ready。
- 不声明 OCR、多格式、Research、Phase 2/3 ready。

结论：无 HIGH 风险，但若目标是“完整 PRD 商用品质”，下一阶段必须进入 AI 输出质量、人工验收和 UX polish，而不能继续扩大 PASS_LIMITED 声明。

## 建议下一阶段

V1.5 AI Quality and Manual Acceptance。

目标：

- 接入真实 LLM 生成 Guide / Studio。
- 对 AI 数字人资料包执行 ChromeCLI / 人工体验验收。
- 评估摘要质量、引用正确率、拒答正确率。
- 决定是否进入 Phase 2 Studio 扩展。
