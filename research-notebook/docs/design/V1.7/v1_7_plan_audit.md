# ResearchNotebook V1.7 Plan Audit

日期：2026-05-30

## 审计结论

V1.7 计划方向正确，可以执行。该阶段是 UX hardening，不是能力扩张阶段。

## 审计意见闭环

| 审计点 | 处理 |
| --- | --- |
| 不能继续堆功能 | 已限定为三列 IA、文案、可操作性和引用交互。 |
| 不能把 Agent 工作流放入 PRD MVP 主路径 | 主 Studio 列移除 Agent 工作流入口。 |
| 不能把 Phase 2/3 disabled shell 写成 ready | 继续显示暂不可用，不发起后端请求。 |
| 不能暴露 source_id / unit_id / evidence_id 给普通用户 | 主路径改为隐藏到调试信息或不展示。 |
| 必须用真实数据验收 | RC 使用数字人 Markdown/PDF 数据集。 |

## 风险评估

| 风险 | 等级 | 收敛措施 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 仅改 UX，不新增 OCR / Audio / PPT / Mindmap / Compare。 |
| 虚假验收 | MEDIUM | 自动化只证明路径可达，最终仍需手工确认截图和内容质量。 |

## 下一步

进入 V1.7-A 到 V1.7-G 实现与报告，随后执行 V1.7-RC。
