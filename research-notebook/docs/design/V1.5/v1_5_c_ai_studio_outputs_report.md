# ResearchNotebook V1.5-C AI Studio Outputs Report

日期：2026-05-27

## 执行状态

PASS_LIMITED。

V1.5-C 已完成真实 AI Studio 输出质量 smoke。Notes、Study Guide、Briefing Doc、FAQ 均使用 MiniMax provider 生成，且每个 section 均保留 `evidence_refs`。

## 真实数据

- 数据目录：`Desktop/技术分享/11-数字人`
- Markdown：`AI数字人资料包/01_industry_overview.md`
- Markdown：`AI数字人资料包/02_technology_trends.md`
- PDF：`AI数字人产业发展报告_2026-05-26.pdf`

## 验收结果

| 项目 | 状态 |
| --- | --- |
| 后端 focused tests | PASS |
| `npm run check` | PASS |
| `npm run smoke:v1.5-c-studio` | PASS |
| Notes | PASS |
| Study Guide | PASS |
| Briefing Doc | PASS |
| FAQ | PASS |
| section-level evidence refs | PASS |
| fallback_mode=false | PASS |
| fixture 脱敏 | PASS |

## 命令证据

- `python3 -m pytest tests/test_target_http_ai_provider.py tests/test_target_http_notebook_guide.py tests/test_target_http_studio_artifacts.py -q`
  - 结果：14 passed。
- `npm run check`
  - 结果：boundary checks、lint、tests、build 均通过。
- `npm run smoke:v1.5-c-studio`
  - 结果：workspace/source/build/四类 Studio 输出/cleanup 全部 PASS。

## Fixtures

保存位置：

- `fixtures/real/v1_5/ai-studio/`

关键文件：

- `studio-notes-success.json`
- `studio-study_guide-success.json`
- `studio-briefing_doc-success.json`
- `studio-faq-success.json`
- `v1_5_c_ai_studio_smoke_result.json`

脱敏检查：

- 未发现 `/Users`
- 未发现 `file://`
- 未发现 `cache_path`
- 未发现 `artifact_path`
- 未发现 `physical_path`
- 未发现 API key / Authorization / Bearer

## PRD 规格检视

覆盖项：

- Notes：PASS_LIMITED，真实 AI 输出，保留引用。
- Study Guide：PASS_LIMITED，真实 AI 输出，保留引用。
- Briefing Doc：PASS_LIMITED，真实 AI 输出，保留引用。
- FAQ：PASS_LIMITED，真实 AI 输出，保留引用。

边界：

- 仅覆盖数字人 P0 数据集。
- 不声明 Audio Overview ready。
- 不声明 PPT ready。
- 不声明 Mindmap ready。
- 不声明 Document comparison ready。
- 不声明 all-source-type Studio ready。

## 风险评估

- 规格漂移风险：LOW。
- 虚假验收风险：MEDIUM。

原因：

- 已通过真实 MiniMax 输出和真实数字人资料 smoke。
- 仍未经过人工内容质量深审。
- 仍只覆盖 P0 数字人数据集，不代表所有行业和所有来源类型。

收敛措施：

- V1.5-D 继续做 source-grounded QA 质量验收。
- V1.5-E 统一做 ChromeCLI / manual E2E 和人工质量检查。

## 下一阶段审计意见

V1.5-D Source-grounded QA Quality 可进入开发计划审计。

准入条件：

- V1.5-A provider PASS。
- V1.5-B Guide PASS_LIMITED。
- V1.5-C Studio PASS_LIMITED。
- `npm run check` 当前 PASS。

V1.5-D 不得把 Studio 输出通过结论扩大为引用问答质量通过。QA 必须单独验证覆盖型问题、资料外拒答、推断标注、citation 定位和 provider failure 局部错误。
