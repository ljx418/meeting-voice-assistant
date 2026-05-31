# ResearchNotebook V1.7-F Citation and Drawer Report

日期：2026-05-30

## 完成内容

- EvidenceList 隐藏 unit_id / evidence_id 等技术字段。
- citation 文案改为“可定位到原文片段”。
- SourcePreviewDrawer 默认隐藏 source_id / unit_id / evidence_id，放入调试信息。
- SourceTraceDrawer 默认隐藏 source_id，放入调试信息。

## PRD 对照

符合“引用可跳转到来源片段”的用户体验，不要求用户理解后端 ID。

## 风险评估

| 风险 | 等级 |
| --- | --- |
| 规格漂移 | LOW |
| 虚假验收 | MEDIUM |

## 下一阶段审计

V1.7-G Chinese Copy Cleanup：GO。
