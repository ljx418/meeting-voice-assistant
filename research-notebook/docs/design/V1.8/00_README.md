# ResearchNotebook V1.8 设计与验收索引

日期：2026-05-30

## 阶段定位

V1.8 按新的产品策略执行：ResearchNotebook 前端保持弱前端，优先在 Agent / workflow / backend contract 层验证 PRD MVP 能力。

V1.7 人工 UX 验收被策略性跳过，记录为 accepted UX debt。V1.8 不声明普通用户体验 ready，只声明 Agent-led capability validation 的受限路径结果。

## 当前边界

- 不追求强前端 polish。
- 不把 Agent 自动验收等同于人工 UX 验收。
- 不声明 all-source-type ready。
- 不声明 all websites URL ready。
- 不声明 OCR ready。
- 不声明 Audio / PPT / Mindmap / Document comparison ready。
- 不声明 arbitrary Agent tool execution ready。
- 云同步 / 协作保持 OUT_OF_SCOPE。

## 文档索引

| 文档 | 用途 |
| --- | --- |
| `v1_8_agent_led_capability_validation_plan.md` | V1.8 总开发与验收计划。 |
| `v1_8_plan_audit.md` | 对 V1.8 计划初稿的自审与修正意见。 |
| `v1_8_0_scope_rebase_report.md` | V1.7 人工 UX 跳过后的范围重定基。 |
| `v1_8_a_agent_task_contract_plan.md` | Agent task 合同计划。 |
| `v1_8_b_agent_source_import_plan.md` | Agent-led 来源导入编排计划。 |
| `v1_8_c_agent_guide_qa_validation_plan.md` | Agent-led Guide / QA / citation 验证计划。 |
| `v1_8_d_agent_studio_validation_plan.md` | Agent-led Studio 输出验证计划。 |
| `v1_8_d_agent_studio_validation_plan_audit.md` | V1.8-D Studio 输出验证计划审计。 |
| `v1_8_d_agent_studio_validation_report.md` | V1.8-D Studio 输出验证执行报告。 |
| `v1_8_e_weak_frontend_shell_plan.md` | 弱前端结果展示壳验收计划。 |
| `v1_8_e_weak_frontend_shell_plan_audit.md` | V1.8-E 弱前端展示壳计划审计。 |
| `v1_8_e_weak_frontend_shell_report.md` | V1.8-E 弱前端展示壳执行报告。 |
| `v1_8_e_weak_frontend_shell_report.html` | V1.8-E 弱前端可读 HTML 展示壳。 |
| `v1_8_rc_agent_led_prd_smoke_plan.md` | V1.8-RC Agent-led PRD smoke 计划。 |
| `v1_8_rc_agent_led_prd_smoke_plan_audit.md` | V1.8-RC Agent-led PRD smoke 计划审计。 |
| `v1_8_rc_agent_led_prd_smoke_report.md` | V1.8-RC Agent-led PRD smoke 执行报告。 |

## 统一停止规则

任一子阶段出现以下情况必须停止推进：

- 规格漂移风险为 HIGH。
- 虚假验收风险为 HIGH。
- Agent 使用 mock 或 fixture 冒充真实能力验收。
- 未授权读取本地目录。
- 输出、日志、fixture 泄露绝对路径、API key、cache path、artifact physical path。
- citation 无法解析却被记录为 PASS。
- 弱前端缺陷被写成 UX ready。
