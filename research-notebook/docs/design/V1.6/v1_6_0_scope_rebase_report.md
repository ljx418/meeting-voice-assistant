# ResearchNotebook V1.6-0 Scope Rebase / Audit Gate Report

日期：2026-05-28

## 结论

PASS。

V1.6-0 已完成范围重基线和审计闭环。当前允许进入 V1.6-A URL 正文抽取详细实施计划审计，但不得直接进入实质开发。

## V1.5 当前状态确认

当前有效 V1.5 状态以以下文档为准：

- `docs/design/V1.5/v1_5_revalidation_report.md`
- `docs/design/V1.5/v1_5_current_gap_analysis.md`
- `docs/design/V1.5/v1_5_rc_quality_release_handoff.md`

确认结果：

| 项目 | 状态 |
| --- | --- |
| AI Provider | PASS |
| AI Notebook Guide | PASS_LIMITED |
| AI Studio Outputs | PASS_LIMITED |
| Source-grounded QA | PASS_LIMITED |
| ChromeCLI / Manual E2E | PASS_LIMITED |
| P0 Markdown / PDF import + build + citation path | PASS_LIMITED |

`docs/design/V1.5/v1_5_0_plan_audit.md` 已标记为 SUPERSEDED_BY_REVALIDATION，仅保留为历史阻塞记录。

## V1.6 范围确认

纳入 V1.6：

- URL 正文抽取限定站点 smoke。
- 多数据集质量评分。
- OCR / 扫描 PDF contract discovery。
- Studio Markdown / JSON 导出。
- Research 补源 / 冲突分析。
- Phase 2/3 输出合同发现和 disabled shell。

剔除出 V1.x：

- 云同步 / 协作。

## V1.6-A 准入补强

V1.6-A 进入实质开发前，详细实施计划必须覆盖：

- SSRF 防护：禁止 localhost、127.0.0.1、0.0.0.0、private IP ranges、link-local、metadata service、file://、ftp://、data:、javascript:，redirect 后也必须重新校验。
- 权限边界：不带 cookies，不访问登录页、私有页或付费墙，不绕过 robots / permission block。
- 内容安全：HTML 只做正文抽取和 sanitize，不执行 script，不使用 `dangerouslySetInnerHTML`。
- 资源限制：max_response_size、timeout、redirect_limit、content_type allowlist。
- 稳定错误：unsupported_site、extraction_failed、robots_or_permission_blocked、fetch_timeout。

## 验收结果

| 项目 | 状态 |
| --- | --- |
| V1.5 revalidation 确认 | PASS |
| V1.5 历史 BLOCKED 记录标注 | PASS |
| 云同步 / 协作 OUT_OF_SCOPE | PASS |
| V1.6-A 安全门禁补强 | PASS |
| V1.6 阶段边界 | PASS |

## 风险评估

| 项目 | 结论 |
| --- | --- |
| 规格漂移风险 | LOW |
| 虚假验收风险 | MEDIUM |
| 是否出现 HIGH 风险 | NO |

虚假验收风险保持 MEDIUM 的原因：

- V1.6-A URL 抽取容易被误扩大为 all websites ready。
- V1.6-C / V1.6-F 只能做 contract discovery / disabled shell，仍需持续防止误声明 ready。

## 下一阶段

V1.6-A URL 正文抽取详细实施计划审计。

下一阶段不得直接开发，必须先产出：

- `v1_6_a_url_extraction_plan.md`
- `v1_6_a_url_extraction_acceptance.md`
- `v1_6_a_url_extraction_plan_audit.md`
