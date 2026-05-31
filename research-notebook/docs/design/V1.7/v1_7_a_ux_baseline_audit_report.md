# ResearchNotebook V1.7-A UX Baseline Audit Report

日期：2026-05-30

## 结论

V1.6 已能完成 PRD MVP 受限路径，但普通用户体验仍存在以下问题：

- Sources / Chat / Studio 三列信息密度不均。
- Studio 列混入 Agent 工作流，容易误读为 PRD 主能力。
- 来源卡片直接展示 source_id 等技术字段。
- Studio 四类输出仍使用英文名称。
- Drawer 中单元 ID、证据片段 ID 等调试信息过多。

## PRD 对照

PRD 要求三列布局为 Sources / Chat / Studio，并以 Guide-first 作为中间区域默认体验。V1.7 必须保留该信息架构，不新增非 PRD 主路径入口。

## 风险评估

| 风险 | 等级 | 说明 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | Agent 工作流可能被误读为 MVP 主路径。 |
| 虚假验收 | MEDIUM | 路径可达不代表普通用户可操作。 |

## 下一阶段审计

V1.7-B 三列布局重组：GO。
