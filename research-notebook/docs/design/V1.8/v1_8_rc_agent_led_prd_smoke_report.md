# V1.8-RC Agent-Led PRD Smoke Report

日期：2026-05-30

## 当前状态

`AGENT_CAPABILITY_SMOKE_READY`

## 执行结果

| 项 | 状态 | 说明 |
| --- | --- | --- |
| V1.8-B source import | PASS | PASS_LIMITED |
| V1.8-C guide qa citation | PASS | PASS_LIMITED |
| V1.8-D studio validation | PASS | PASS_LIMITED |
| V1.8-E weak frontend shell | PASS | UX boundary preserved |
| source import raw_fixture_refs | PASS |  |
| guide qa raw_fixture_refs | PASS |  |
| studio raw_fixture_refs | PASS |  |
| agent prd no sensitive fixtures | PASS |  |
| covered Agent draft | PASS |  |
| covered permission boundary | PASS |  |
| covered Notebook create | PASS |  |
| covered Markdown/TXT/PDF/limited URL import | PASS |  |
| covered build/index | PASS |  |
| covered Notebook Guide | PASS |  |
| covered Suggested Question QA | PASS |  |
| covered citation resolution | PASS |  |
| covered Notes/Study Guide/Briefing Doc/FAQ | PASS |  |
| covered Markdown/JSON export | PASS |  |
| covered outside-question refusal | PASS |  |
| covered validation report | PASS |  |
| covered weak frontend shell | PASS |  |

## Fixture

- `fixtures/real/v1_8/agent-prd/v1_8_rc_agent_prd_result.json`
- `docs/design/V1.8/v1_8_e_weak_frontend_shell_report.html`

## 声明边界

如果状态为 `AGENT_CAPABILITY_SMOKE_READY`，最多声明：

ResearchNotebook V1.8 Agent-led PRD MVP capability validation is smoke-ready for validated PDF / TXT / Markdown and limited URL sources on approved datasets.

仍不能声明：

- 普通用户 UX fully ready
- all websites URL ready
- all-source-type ready
- OCR ready
- Audio Overview ready
- PPT generation ready
- Mindmap ready
- Document comparison ready
- arbitrary Agent tool execution ready
- cloud sync / collaboration ready

## 风险评估

| 风险 | 等级 | 处理 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 限定为 Agent-led capability validation |
| 虚假验收 | MEDIUM-HIGH | 不替代人工 UX / 内容质量验收 |
| UX 债务 | HIGH accepted | 保留 V1.x Final Human UX Acceptance |
