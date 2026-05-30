# ResearchNotebook V1.6 Plan Audit

日期：2026-05-28

## 审计结论

PASS。

V1.6 开发及验收计划已经形成可执行、可审计版本。V1.6-0 Scope Rebase / Audit Gate 已补齐并通过。V1.6-A URL 正文抽取已按计划审计后执行，并在限定公开 URL smoke 中 PASS_LIMITED。当前无新增致命或重大规格偏差意见。

## 审计范围

已审计文档：

- `docs/design/V1.6/00_README.md`
- `docs/design/V1.6/v1_6_development_plan.md`
- `docs/design/V1.6/v1_6_acceptance_plan.md`
- `docs/design/V1.6/v1_6_prd_coverage_matrix.md`
- `docs/design/V1.6/v1_6_current_gap_analysis.md`
- `docs/design/V1.6/v1_6_current_gap_analysis.drawio`

## 初始审计意见

| 编号 | 意见 | 风险 | 处理 |
| --- | --- | --- | --- |
| A1 | 开发计划只有阶段标题，缺少进入门槛和阶段报告路径。 | MEDIUM | 已补充每阶段进入门槛、建议实现、报告路径。 |
| A2 | 验收计划缺少自动化、浏览器和人工质量验收的分层。 | MEDIUM | 已补充三类验收要求和建议命令命名。 |
| A3 | URL 抽取容易被误声明为 all websites ready。 | MEDIUM | 已在 V1.6-A 和 coverage matrix 中限定为有限站点。 |
| A4 | OCR 容易把可抽取 PDF 通过误判为扫描 PDF ready。 | HIGH | 已将 V1.6-C 定义为合同发现；无 OCR provider 不声明 ready。 |
| A5 | Phase 2/3 输出能力容易被 disabled shell 误读为 ready。 | MEDIUM | 已明确 V1.6-F 只允许合同发现和 disabled shell。 |
| A6 | 云同步 / 协作需从剩余范围剔除。 | LOW | 已标记为 OUT_OF_SCOPE。 |
| A7 | V1.5 早期 provider BLOCKED 文档与当前 revalidation 状态容易产生冲突。 | HIGH | 已将 `v1_5_0_plan_audit.md` 标记为历史阻塞记录，并指定 `v1_5_revalidation_report.md` 为当前状态来源。 |
| A8 | V1.6-A URL 抽取缺少 SSRF / 权限 / 资源限制门禁会形成安全规格漂移。 | HIGH | 已补充 SSRF、redirect 后校验、robots / permission block、max_response_size、timeout、content_type allowlist 和稳定错误。 |

## 闭环结果

所有初始审计意见和 V1.6-0 新增审计意见均已闭环。当前没有新增审计意见。

## 风险评估

| 项目 | 结论 |
| --- | --- |
| 规格漂移风险 | LOW |
| 虚假验收风险 | MEDIUM |
| 是否存在 HIGH 风险 | NO |

虚假验收风险保持 MEDIUM 的原因：

- V1.6 仍包含 URL、OCR、Research、Phase 2/3 输出合同等容易被误扩大的能力。
- 计划已用 PASS_LIMITED、DISABLED_READY、NOT_READY、OUT_OF_SCOPE 控制声明边界。
- 每阶段必须重新审计，不能用本计划一次性批准全部实质开发。

## V1.6-A 执行后审计

| 项目 | 结论 |
| --- | --- |
| V1.6-A URL source contract | PASS_LIMITED |
| PRD 规格对齐 | PASS，符合 P1 URL 可选且不保证所有站点的边界 |
| 开发计划漂移风险 | LOW |
| 虚假验收风险 | MEDIUM |
| 是否存在 HIGH 风险 | NO |

收敛措施：

- 声明限定为 `http://example.com/` 和 `http://example.org/` 等公开 HTTP URL smoke。
- 保留 all websites URL extraction NOT_READY。
- 下一阶段不得用 URL smoke 替代多数据集质量评分。

## 允许进入的下一阶段

V1.6-B 多数据集质量评分计划审计。

不得直接进入 V1.6-B 实质开发，除非 V1.6-B 计划审计报告确认：

- 至少 3 个真实主题数据集已确定。
- Guide / QA / Studio / citation / 拒答评分表已定义。
- 人工质量评分和自动 smoke 的边界已分开。
- 没有 HIGH 规格漂移或 HIGH 虚假验收风险。
