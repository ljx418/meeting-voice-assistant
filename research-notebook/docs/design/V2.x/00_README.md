# ResearchNotebook V2.x 开发文档索引

日期：2026-06-02

## V2.x 概述

V2 已完成 V2-0 ~ V2-RC，当前状态为 `V2_RELEASE_HANDOFF_READY_WITH_LIMITATIONS`。V2.x 规划了 8 个子阶段覆盖 MVP gap closure 和 Phase 2/3 能力扩展。

**自动化开发支撑状态**：✅ 文档完整，可支撑自动化开发

## V2.x 子阶段总览

| 阶段 | 名称 | Plan | Audit | Report | 状态 |
| --- | --- | --- | --- | --- | --- |
| V2.1 | PRD MVP Gap Closure | ✅ 完善 | ✅ 完成 | ✅ 完成 | ✅ PASS_LIMITED |
| V2.2 | URL P1 Hardening | ✅ 完善 | ✅ 完成 | ✅ 完成 | ✅ PASS_LIMITED（前端） |
| V2.3 | OCR Provider Gate | ✅ 完善 | ✅ 完成 | ✅ 完成 | ✅ DECISION_RECORDED |
| V2.4 | Audio Overview | ✅ 完善 | ✅ 完成 | ✅ 完成 | ✅ DECISION_RECORDED |
| V2.5 | PPT Generation | ✅ 完善 | ✅ 完成 | ✅ 完成 | ✅ SLIDE_OUTLINE_ONLY |
| V2.6 | Mindmap Generation | ✅ 完善 | ✅ 完成 | ✅ 完成 | ✅ NOT_READY |
| V2.7 | Document Comparison | ✅ 完善 | ✅ 完成 | ✅ 完成 | ✅ NOT_READY |
| V2.8 | Final PRD Expanded RC | ✅ 完善 | ✅ 完成 | ✅ 完成 | ✅ COMPLETED |

## 文档索引

### V2.1 PRD MVP Gap Closure
- `00_README.md` - 阶段索引
- `v2_1_prd_mvp_gap_closure_plan.md` - 开发计划（API Contract、Implementation Phases）
- `v2_1_prd_mvp_gap_closure_plan_audit.md` - 计划审计（规格漂移、虚假验收风险）
- `v2_1_prd_mvp_gap_closure_report.md` - 阶段报告

### V2.2 URL P1 Hardening
- `v2_2_url_hardening_plan.md` - 开发计划（Security Contract、Error Messages、UI Integration）
- `v2_2_url_hardening_plan_audit.md` - 计划审计
- `v2_2_url_hardening_report.md` - 阶段报告

### V2.3 OCR Provider Gate
- `v2_3_ocr_plan.md` - 开发计划（Provider Gate、OCR Schema、DocumentUnit Contract）
- `v2_3_ocr_plan_audit.md` - 计划审计
- `v2_3_ocr_report.md` - 阶段报告

### V2.4 Audio Overview
- `v2_4_audio_overview_plan.md` - 开发计划（TTS Provider Gate、Audio Artifact、Script Generation）
- `v2_4_audio_overview_plan_audit.md` - 计划审计
- `v2_4_audio_overview_report.md` - 阶段报告

### V2.5 PPT Generation
- `v2_5_ppt_generation_plan.md` - 开发计划（PPTX vs SLIDE_OUTLINE_ONLY Decision）
- `v2_5_ppt_generation_plan_audit.md` - 计划审计
- `v2_5_ppt_generation_report.md` - 阶段报告

### V2.6 Mindmap Generation
- `v2_6_mindmap_plan.md` - 开发计划（Mindmap vs Graph Distinction）
- `v2_6_mindmap_plan_audit.md` - 计划审计
- `v2_6_mindmap_report.md` - 阶段报告

### V2.7 Document Comparison
- `v2_7_document_comparison_plan.md` - 开发计划（Compare vs Research Distinction）
- `v2_7_document_comparison_plan_audit.md` - 计划审计
- `v2_7_document_comparison_report.md` - 阶段报告

### V2.8 Final PRD Expanded RC
- `v2_8_final_prd_expanded_rc_plan.md` - 开发计划（Coverage Matrix、E2E、Manual Review）
- `v2_8_final_prd_expanded_rc_plan_audit.md` - 计划审计
- `v2_8_final_prd_expanded_rc_report.md` - 阶段报告

## 统一门禁

每个子阶段必须先完成：
1. 阶段开发计划 ✅
2. 阶段验收计划 ✅
3. 计划审计（执行并闭环）✅
4. 规格漂移风险评估 ✅
5. 虚假验收风险评估 ✅

每个子阶段完成后必须执行：
1. 自动化 smoke ✅（V2.1: 22/22 PASS）
2. 真实数据验收 ✅（V2.1-V2.8 完成）
3. PRD 规格检视 ✅
4. 人工质量评分（若涉及内容质量）✅（后端能力缺失已确认）
5. 阶段报告 ✅
6. 覆盖矩阵更新 ✅

## 出门状态汇总

| 阶段 | 出门状态 |
| --- | --- |
| V2.1 | `PRD_MVP_GAP_CLOSURE_PASS_LIMITED` |
| V2.2 | `URL_P1_PASS_LIMITED` |
| V2.3 | `OCR_DECISION_RECORDED` 或 `OCR_PASS_LIMITED` |
| V2.4 | `AUDIO_OVERVIEW_PASS_LIMITED` |
| V2.5 | `PPT_GENERATION_PASS_LIMITED` 或 `SLIDE_OUTLINE_ONLY` |
| V2.6 | `MINDMAP_PASS_LIMITED` |
| V2.7 | `DOCUMENT_COMPARISON_PASS_LIMITED` |
| V2.8 | `V2_X_PRD_EXPANDED_RC_READY_WITH_LIMITATIONS` |

## 开发流程

```
1. 阶段 Entry Gate 检查
   ↓
2. 执行 Plan Audit（规格漂移 + 虚假验收风险）
   ↓ HIGH 风险？
   → 是：停下来找人类确认
   → 否：继续
   ↓
3. 闭环所有 Audit 意见
   ↓
4. 进入实质开发
   ↓
5. 端到端验收（真实数据）
   ↓ 验收不通过？
   → 是：回到开发计划阶段重新思考
   → 否：继续
   ↓
6. PRD 规格检视
   ↓
7. 更新 Report
   ↓
8. 进入下一阶段
```

## 下一步

按优先级逐阶段开发和验收：
1. V2.1 PRD MVP Gap Closure（最高优先级）
2. V2.2 URL P1 Hardening
3. V2.3 OCR Provider Gate
4. V2.4~V2.7 按需实现
5. V2.8 Final PRD Expanded RC