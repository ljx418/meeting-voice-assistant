# ResearchNotebook V1.5-B AI Notebook Guide Report

日期：2026-05-27

## 执行状态

PASS。

## 当前结果

V1.5-B AI Notebook Guide 已完成真实 MiniMax 生成路径，并通过 AI 数字人 P0 数据集 smoke。

实现内容：

- `/api/workspaces/{workspace_id}/guide` 接入真实 AI Guide generation path。
- 保留 deterministic fallback，但通过 `generation_metadata.fallback_mode` 明确标记。
- Guide 返回 `generation_metadata`。
- Key Topics 支持 topic-level `evidence_refs`。
- 前端 adapter 已映射 `generation_metadata` 和 topic evidence。
- 新增 `npm run smoke:v1.5-b-guide`。

## 验收结果

| 项目 | 状态 |
| --- | --- |
| 数字人资料导入 | PASS |
| AI Overview | PASS |
| AI Key Topics | PASS |
| AI Suggested Questions | PASS |
| Guide evidence_refs | PASS |
| Topic evidence_refs | PASS |
| generation_metadata | PASS |
| fallback_mode=false | PASS |
| fixture 脱敏 | PASS |
| 后端 focused tests | PASS |
| npm run check | PASS |

## Smoke 证据

命令：

```bash
npm run smoke:v1.5-b-guide
```

结果：

- Markdown import：PASS。
- Technology Markdown import：PASS。
- PDF import：PASS。
- Workspace build：PASS。
- AI Guide validation：PASS。
- Cleanup：PASS。

关键输出：

- Overview 概括 AI 数字人行业、技术进展和产业发展。
- Key Topics 4 个。
- Suggested Questions 4 个。
- 全局 evidence_refs 3 条。
- 每个 Key Topic 都有 evidence_refs。
- provider：MiniMax。
- model：MiniMax-M2.7。
- fallback_mode：false。

Fixtures：

- `fixtures/real/v1_5/ai-guide/ai-guide-success.json`
- `fixtures/real/v1_5/ai-guide/v1_5_b_ai_guide_smoke_result.json`

## 风险评估

- 规格漂移风险：LOW。
- 虚假验收风险：MEDIUM。

原因：V1.5-B 已证明 AI Guide 不是 deterministic template，且带 evidence_refs；但这只覆盖 AI 数字人 P0 数据集，不代表所有来源类型或所有行业 ready。

## PRD 规格检视

PRD 要求进入 Notebook 后默认展示 Notebook Guide，包含 Overview / Key Topics / Suggested Questions。

当前结论：

- PRD Guide-first：PASS_LIMITED。
- 自动生成 Notebook Guide：PASS，限定 AI 数字人 P0 数据集。
- 引用可追溯：PASS，Guide 和 topic 都带 evidence_refs。
- all-source-type Guide quality：NOT_READY。

## 下一阶段审计意见

可以进入 V1.5-C AI Studio Outputs。

进入 C 前必须补强：

- Notes 每条摘录或每个 block 有 citation。
- Study Guide 每个核心 section 有 citation。
- Briefing Doc 每个关键结论 section 有 citation。
- FAQ 每条答案必须有 citation 或明确未覆盖。
- 无 evidence 时拒绝生成。
- 不声明 Audio / PPT / Mindmap / Document comparison ready。
