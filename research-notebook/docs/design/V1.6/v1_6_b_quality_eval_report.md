# ResearchNotebook V1.6-B Quality Evaluation Report

日期：2026-05-28

## 结论

V1.6-B 自动候选评估已完成，状态为 `CANDIDATE_READY_FOR_MANUAL_REVIEW`。

本阶段没有声明 PASS。原因是多数据集质量评分需要人工判断 citation 语义是否真正支撑结论、是否存在幻觉、拒答是否正确。自动 smoke 只能证明结构、路由和 evidence_refs 可解析。

## 执行命令

`npm run smoke:v1.6-b-quality`

结果：

`FINAL CANDIDATE_READY_FOR_MANUAL_REVIEW`

`npm run check`

结果：

PASS。Boundary checks、lint、126 个 Vitest tests、production build 均通过。

## 数据集

| 数据集 | 真实路径 | 来源数 | Studio artifact | 自动结论 |
| --- | --- | --- | --- | --- |
| 数字人 | `Desktop/技术分享/11-数字人` | 3 | FAQ | CANDIDATE_READY_FOR_MANUAL_REVIEW |
| Claude Code 技术分享 | `Desktop/技术分享/02-claudecode技术分享` | 1 | Study Guide | CANDIDATE_READY_FOR_MANUAL_REVIEW |
| AI 视频工作流 | `Desktop/技术分享/08-AITextToVideoWorkflow` | 1 | Briefing Doc | CANDIDATE_READY_FOR_MANUAL_REVIEW |

## 自动验收结果

| 项目 | 数字人 | Claude Code | AI 视频工作流 |
| --- | --- | --- | --- |
| workspace create | PASS | PASS | PASS |
| source import | PASS | PASS | PASS |
| build | PASS | PASS | PASS |
| Guide evidence_refs | PASS | PASS | PASS |
| 覆盖型 QA 1 | PASS | PASS | PASS |
| 覆盖型 QA 2 | PASS | PASS | PASS |
| 资料外拒答 | PASS | PASS | PASS |
| Studio evidence_refs | PASS | PASS | PASS |
| citation route resolution | PASS | PASS | PASS |
| cleanup | PASS | PASS | PASS |

## Fixtures

保存路径：

`fixtures/real/v1_6/quality-eval/`

关键文件：

- `v1_6_b_quality_eval_smoke_result.json`
- `digital-human/guide.json`
- `digital-human/query-covered-1.json`
- `digital-human/query-covered-2.json`
- `digital-human/query-outside.json`
- `digital-human/studio-faq.json`
- `claude-code/guide.json`
- `claude-code/studio-study_guide.json`
- `ai-video-workflow/guide.json`
- `ai-video-workflow/studio-briefing_doc.json`

Fixtures 已脱敏，脚本过滤 API key、authorization、raw path、cache path、artifact physical path 和 stack trace。

## PRD 规格检视

本阶段对应 PRD 中 Guide、引用问答、资料不足拒答、Studio 轻量输出的多数据集质量抽样。

自动 smoke 已验证：

- 每个数据集可以生成 Guide。
- 覆盖型 QA 返回 evidence_refs。
- 资料外问题出现 source-grounded refusal。
- Studio 输出有 evidence_refs。
- citation route 可解析到 unit / EvidenceSpan。

自动 smoke 尚不能验证：

- citation 片段是否语义上支持结论。
- 输出是否遗漏资料关键主题。
- 是否存在细微幻觉。
- 中文表达是否足够自然。

因此该阶段只能作为人工评分前的候选包。

## 风险评估

开发计划漂移风险：LOW。

原因：本阶段未新增产品功能，只增加评估 harness 和候选 fixtures。

虚假验收风险：MEDIUM。

原因：已明确不声明 PASS，并把人工评分后置到最终阶段。

是否存在 HIGH 风险：NO，前提是继续保持 `CANDIDATE_READY_FOR_MANUAL_REVIEW` 声明。

## 后续人工评分

人工评分模板：

`docs/design/V1.6/v1_6_b_manual_quality_review_template.md`

最终 PASS 需要人工补齐：

- Guide 可用性。
- 资料相关性。
- 覆盖完整性。
- citation 正确率。
- citation 可定位率。
- 拒答正确率。
- 中文表达。
- 高危幻觉数。

## 下一阶段建议

可以进入 V1.6-C OCR / 扫描 PDF Contract Discovery。

注意：V1.6-C 只能做合同发现和 disabled / unsupported 状态，不得声明 OCR ready。
