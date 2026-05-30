# ResearchNotebook V1.6 Development Plan

日期：2026-05-28

## 目标

V1.6 聚焦 PRD 中 V1.5 后仍未闭环或未验收的功能点。目标不是扩大成完整企业知识库，而是在 V1.x 内把 NotebookLM-like MVP 做到更完整、可验收、可审计。

云同步 / 协作已剔除，不作为 V1.6 或 V1.x 剩余开发项。

## 总阶段

每个阶段必须先完成阶段计划审计，再进入实质开发。阶段报告必须记录：

- PRD 规格对齐结论。
- 开发计划漂移风险。
- 虚假验收风险。
- 是否出现 HIGH 风险。
- 若出现 HIGH 风险，停止进入下一阶段。
- 若为 LOW / MEDIUM，必须写明收敛措施后才能继续。

### V1.6-0 Scope Rebase / Audit Gate

目标：
- 以用户提供的 PRD v0.2 为规格基线。
- 从剩余 backlog 中删除云同步 / 协作。
- 冻结 V1.6 阶段边界和验收状态词。
- 明确 V1.5 当前有效状态以 `v1_5_revalidation_report.md` 为准。
- 将 V1.5 早期 provider BLOCKED 审计记录标记为历史记录，不作为 V1.6 entry gate 当前判断。

验收：
- V1.6 docs 存在。
- V1.6 gap / drawio 显示云同步 / 协作为 out of scope。
- 所有后续阶段都有 PRD 规格检视、规格漂移风险和虚假验收风险。
- V1.5 provider、Guide、Studio、QA、ChromeCLI E2E 当前均为 PASS_LIMITED。
- P0 Markdown / PDF import、build、citation 路径已在 V1.5 revalidation 中确认。
- V1.6-A 安全门禁已写入计划。

风险门禁：
- 规格漂移风险 HIGH：停止。
- 虚假验收风险 HIGH：停止。

计划产物：
- `v1_6_development_plan.md`
- `v1_6_acceptance_plan.md`
- `v1_6_prd_coverage_matrix.md`
- `v1_6_current_gap_analysis.md`
- `v1_6_current_gap_analysis.drawio`
- `v1_6_plan_audit.md`
- `v1_6_0_scope_rebase_report.md`

### V1.6-A URL 正文抽取 P1 Contract / Smoke

目标：
- 实现或确认 URL source 导入合同。
- 抽取网页正文，进入来源列表、Guide、QA、Studio 证据链。

进入门槛：
- V1.5 revalidation PASS_LIMITED。
- data_service 可启动。
- AI provider 可用。
- P0 PDF / TXT / Markdown 回归通过。
- 至少准备 3 个真实 URL，其中 1 个允许失败。

建议实现：
- data_service 增加 URL source import / extraction route 或扩展 source create contract。
- response 区分 `ok`、`unsupported_site`、`extraction_failed`、`robots_or_permission_blocked`。
- URL source 进入现有 source preview / DocumentUnit / EvidenceSpan 流程。
- ResearchNotebook 只通过 dataServiceClient 调用，不在 feature 层拼 route。
- SSRF 防护必须在后端执行：禁止 localhost、127.0.0.1、0.0.0.0、private IP ranges、link-local、metadata service、file://、ftp://、data:、javascript:，redirect 后也必须重新校验。
- URL 抽取不得携带 cookies，不访问登录页、私有页或付费墙，不绕过 robots / permission block。
- HTML 只做正文抽取和 sanitize，不执行 script，不使用 `dangerouslySetInnerHTML`。
- 必须设置资源限制：max_response_size、timeout、redirect_limit、content_type allowlist。

验收：
- 支持至少 3 个真实网页 URL，其中至少 1 个失败站点返回稳定 unsupported / extraction_failed。
- response 不包含 raw cache path、临时文件路径或内部 stack trace。
- URL source 可生成 source preview、DocumentUnit、EvidenceSpan。
- Guide / QA / Studio 对 URL source 可引用。
- blocked/private/unsafe URL 返回稳定错误，不发起内部网络访问。
- 失败状态覆盖 `unsupported_site`、`extraction_failed`、`robots_or_permission_blocked`、`fetch_timeout` 中的相关场景。
- 不声明所有网站都支持。

打回：
- 网页正文抽取不稳定。
- citation 不能定位。
- 失败页面硬崩或泄漏内部路径。

阶段报告：
- `v1_6_a_url_extraction_report.md`

### V1.6-B P0/P1 扩展评测集和质量评分

目标：
- 将 V1.5 的单一数字人数据集扩展为至少 3 组 P0/P1 数据集。
- 建立人工评分表，覆盖 Guide、QA、Studio、拒答和 citation。

进入门槛：
- V1.6-A 若实现，则限定 URL smoke 通过；若打回，则明确 URL 仍为 NOT_READY。
- V1.5 数字人数据集回归通过。

建议实现：
- 新增评测集 manifest，记录每组数据集的来源类型、问题集、预期拒答问题、预期 citation 覆盖点。
- 新增评分表模板，评分维度包括资料相关性、覆盖完整性、引用可信度、拒答正确性、中文表达、幻觉风险。
- 自动 smoke 只负责生成候选结果；人工评分结果单独落盘。

验收：
- 至少 3 个主题数据集，每个包含 Markdown/TXT/PDF 中至少两类。
- 每个数据集跑 Guide / QA / Studio / citation。
- 人工评分表落盘。
- 通过阈值明确：Guide 可用性 >= 4/5，QA citation 正确率 >= 80%，拒答正确率 >= 80%，citation 可定位率 >= 90%，高危幻觉 = 0。

打回：
- 只跑一个主题却声明泛化质量。
- 只跑 API 不做人工质量抽样。

阶段报告：
- `v1_6_b_quality_eval_report.md`

### V1.6-C OCR / 扫描 PDF Contract Discovery

目标：
- 明确扫描 PDF / 图片 OCR 是否进入 V1.x 可实现范围。
- 先做合同发现和 disabled shell，不直接声明 OCR ready。

进入门槛：
- 至少准备 1 个真实扫描 PDF。
- 明确是否存在 OCR provider；若不存在，只能做 contract discovery。

建议实现：
- capability manifest 增加 OCR 相关字段，但默认 false。
- 扫描 PDF import 返回稳定 `ocr_required` 或 `unsupported_ocr` 状态。
- UI 显示“需要 OCR 合同 / 当前不可用”，不伪装为 PDF 解析失败。

验收：
- OCR capability manifest 字段设计完成。
- 扫描 PDF response 语义明确：ocr_required / unsupported / processing。
- 若没有 OCR provider，不声明 ready。
- 若有 OCR provider，必须单独 smoke：文本抽取、citation 定位、页码/片段定位。

打回：
- 把可抽取文本 PDF 的通过结论套到扫描 PDF。
- 无 OCR provider 却声明 OCR ready。

阶段报告：
- `v1_6_c_ocr_contract_report.md`

### V1.6-D Studio Export / Download

目标：
- Notes / Study Guide / Briefing Doc / FAQ 支持复制、下载或导出。
- 保留 citation metadata。

进入门槛：
- V1.5-C Studio AI output 复验通过。
- Artifact schema 中已有 section-level evidence_refs。

建议实现：
- 前端提供 Copy / Download controls。
- 后端或前端生成 Markdown / JSON 导出时保留 artifact id、section id、evidence_refs。
- 导出文件名使用 workspace / artifact 的安全 slug，不包含本地路径。
- JSON export 至少包含 artifact_id、artifact_type、sections、evidence_refs、schema_version、exported_at。

验收：
- 每类 Studio artifact 可导出 Markdown 或 JSON。
- 导出内容包含标题、正文、引用元数据。
- JSON export 字段完整。
- 不泄漏 raw path、cache path、artifact physical path。
- 浏览器路径可点击生成、预览、导出。

打回：
- 导出丢失 citation。
- 导出包含内部 artifact 路径。

阶段报告：
- `v1_6_d_studio_export_report.md`

### V1.6-E Research 补源 / 冲突分析

目标：
- 实现 PRD 7.4 中的“资料不足 -> 引导补源 -> 新增资料后 Research 综合输出”闭环。
- 支持冲突标注。

进入门槛：
- Source-grounded QA 资料外拒答仍通过。
- Studio / Guide citation 路径仍通过。
- 至少准备一组会产生资料缺口的问题，以及一组补源后可回答的新资料。

建议实现：
- Chat 中资料不足时提供补源建议和添加来源入口。
- Research 输出结构区分 supported_conclusions、inferences、conflicts、missing_evidence。
- 冲突分析必须逐条绑定 evidence_refs。
- 不做外部互联网自动搜索，不把 provider 常识当作来源。

验收：
- 资料不足问题先拒答并建议补充资料类型 / 搜索关键词。
- 用户添加来源后可触发 Research。
- Research 输出区分“资料明确支持”与“基于来源的推断”。
- 冲突来源被显式列出，并附 citation。
- 每个关键结论带引用。

打回：
- 未补源时硬答。
- 不区分推断和来源结论。
- 冲突不标注。

阶段报告：
- `v1_6_e_research_workflow_report.md`

### V1.6-F Phase 2/3 Output Contract Discovery

目标：
- 对 Audio Overview、PPT、思维导图、文档对比做合同发现。
- 只允许 disabled shell / contract / adapter shell。

进入门槛：
- Studio 导出已通过或明确保持 PASS_LIMITED。
- 不允许在没有后端合同时实现真输出。

建议实现：
- 为四类能力分别定义 capability、request、response、artifact metadata、unsupported/error 状态。
- UI 只显示 disabled / coming later / contract required。
- 文档明确 Phase 2/3 能力不会被 V1.6-RC 声明 ready。

验收：
- 每个输出能力都有 capability、route、DTO、错误语义和验收计划。
- UI 不显示为 ready。
- 不生成伪输出冒充完成。

打回：
- 没有真实后端合同却声明 ready。
- 把 Studio 文本输出伪装成 PPT / Audio / Mindmap。

阶段报告：
- `v1_6_f_phase2_3_contract_report.md`

### V1.6-RC Integrated PRD Closure Smoke

目标：
- 集中验证 V1.6 已实现能力。

进入门槛：
- A-F 每阶段都有报告。
- 所有 HIGH 风险均已关闭或阶段停止。
- 所有 fixtures 均完成脱敏检查。

验收：
- Markdown / TXT / 可抽取 PDF 主路径仍通过。
- URL source 路径按限定范围通过。
- Studio 导出通过。
- Research 补源 / 冲突分析通过。
- OCR 若未通过，明确保持 NOT_READY。
- Phase 2/3 输出若只有合同，保持 DISABLED_READY / NOT_READY。
- `npm run check` 通过。
- ChromeCLI 或手工浏览器验收通过。

阶段报告：
- `v1_6_rc_integrated_prd_closure_report.md`

## 状态词

- PASS：合同、实现、真实数据 smoke、浏览器路径均通过。
- PASS_LIMITED：限定数据集或限定 source type 通过。
- DISABLED_READY：合同和 disabled shell 可用，但能力未 ready。
- NOT_READY：未实现或未通过验收。
- BLOCKED：后端合同、provider、数据或环境阻塞。
- OUT_OF_SCOPE：明确剔除出 V1.x 范围。
