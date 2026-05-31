# ResearchNotebook V1.x 剩余开发及验收计划

日期：2026-05-31

## 1. 当前结论

V1.x PRD MVP 受限路径已经完成最终验收收口，当前状态为：

```text
V1_X_FINAL_ACCEPTANCE_PASS_LIMITED
```

此前 V1.x 剩余阶段已按以下顺序完成或收口：

1. V1.7-H 人工 UX 验收与 final sync。
2. V1.8 Sources P0/P1 Completion。
3. V1.9 Research Quality / Conflict Labeling Completion。
4. V1.10 Phase 2/3 Output Contract-to-Implementation Decision。
5. V1.x-RC Final PRD Acceptance / Release Handoff。

云同步 / 协作已从 V1.x 剩余范围剔除，不再作为 V1.x 未完成项。

## 2. 仍未完成或未最终验收的 PRD 功能点

| PRD 功能点 | 当前状态 | 后续处理 |
| --- | --- | --- |
| V1.7 普通用户 UX | PASS_LIMITED_ACCEPTED | V1.x 交互式浏览器证据包已获认可；仍不代表强前端 UX polish。 |
| PDF / TXT / Markdown 导入稳定性 | PASS_LIMITED | V1.x 真实数据路径已复核。 |
| URL 正文抽取 | PASS_LIMITED | limited URL，不声明 all websites ready。 |
| 来源删除 / 重命名 | PASS_LIMITED | 受限路径已纳入 UX hardening；复杂批量管理不在 V1.x 扩展。 |
| 解析 / 索引状态与重试 | PASS_LIMITED | 可见状态和失败路径受限验收；不声明全场景 ready。 |
| 来源引用高亮 | PASS_LIMITED | V1.x-RC 交互式证据包复核。 |
| Studio Markdown / JSON 导出 | PASS_LIMITED_ACCEPTED | V1.x 交互式证据包显示导出入口，内容质量按受限路径认可。 |
| Research 补源 / 综合输出 | V1.9 PASS_LIMITED | V1.9-A 已通过 Research quality smoke；仍不代表 all-domain ready |
| 冲突标注 | V1.9 PASS_LIMITED | V1.9-B 真实冲突样本已进入 structured conflicts；仍不代表 all-domain conflict detection ready。 |
| OCR / 扫描 PDF | CONTRACT_DISCOVERY_READY | V1.10 决定是否接 provider；否则保持 NOT_READY |
| Audio Overview | DISABLED_READY | V1.10 决定是否实现或继续 disabled |
| PPT 生成 | DISABLED_READY | V1.10 决定是否实现或继续 disabled |
| 思维导图 | DISABLED_READY | V1.10 决定是否实现或继续 disabled |
| 文档对比 | DISABLED_READY | V1.10 决定是否实现或继续 disabled |
| all websites URL extraction | NOT_READY | V1.x 不建议声明 |
| all-source-type ready | NOT_READY | V1.x 不建议声明 |
| 云同步 / 协作 | OUT_OF_SCOPE | 已剔除 |

## 3. V1.7-H 人工 UX 验收与 final sync

### 目标

把 V1.7 自动化 UX PASS 推进到人工 UX 验收 PASS，并同步最终文档。

### 开发内容

- 不新增功能。
- 根据人工验收反馈修复：
  - 页面重叠。
  - 文案不可读。
  - 按钮不可点击。
  - 来源区或输出区操作不清晰。
  - 未完成能力被误展示为可用。

### 验收标准

- 三列布局在桌面 / 中等宽度 / 窄屏均无明显重叠。
- 来源、问答、输出三列普通用户可理解。
- citation 点击能定位来源片段。
- Studio 四类轻量输出可生成，引用信息可见。
- Phase 2/3 输出保持 disabled，不生成伪输出。
- 页面主流程无 V1.x / smoke / RC / source_id / unit_id / evidence_id 等开发态暴露。
- 用户确认人工 UX 验收通过。

### 必跑命令

```bash
npm run check
npm run smoke:v1.7-ux
npm run smoke:v1.5-e-e2e
```

### 风险评估

- 规格漂移风险：MEDIUM。原因是 UX 修复容易误改能力边界。
- 虚假验收风险：MEDIUM。原因是自动 smoke 不能证明用户体验质量。
- 停止条件：人工验收失败或出现 HIGH 风险。

## 4. V1.8 Sources P0/P1 Completion

### 目标

补齐 PRD MVP 的来源导入与来源管理体验，范围限定为：

- P0：PDF / TXT / Markdown。
- P1：有限公开 URL 正文抽取。

### 开发内容

1. 来源导入 UI 完整化。
2. 来源删除。
3. 来源重命名。
4. 解析 / 索引状态展示。
5. 失败重试。
6. URL 抽取失败态展示。
7. PDF / TXT / Markdown 的 preview / DocumentUnit / EvidenceSpan 回归。
8. 来源列表空态、处理中、失败态、完成态文案统一。

### 验收数据

- `Desktop/技术分享/11-数字人` 中的 Markdown 和 PDF。
- 至少 1 个 TXT 样本。
- 至少 3 个真实 URL：
  - 2 个可抽取公开网页。
  - 1 个稳定失败网页，返回 `unsupported_site` 或 `extraction_failed`。

### 验收标准

- 用户可导入 PDF / TXT / Markdown。
- 用户可添加有限公开 URL。
- 来源列表显示解析状态：待处理 / 处理中 / 完成 / 失败。
- 失败来源可重试。
- 用户可重命名来源。
- 用户可删除来源。
- 删除后 Guide / QA / Studio 不引用已删除来源，或明确提示来源已不可用。
- PDF / TXT / Markdown citation 可打开 SourcePreviewDrawer。
- 可定位时显示 DocumentUnit / EvidenceSpan。
- 不支持 URL 或失败 URL 不导致全页崩溃。
- 不声明 all websites URL ready。
- 不声明 Word / PPT / audio / video ready。

### 必跑命令

```bash
npm run check
npm run smoke:v1.4-sources-p0
npm run smoke:v1.6-a-url
npm run smoke:v1.5-e-e2e
```

### 风险评估

- 规格漂移风险：MEDIUM。原因是 URL 抽取容易扩大成 all websites。
- 虚假验收风险：MEDIUM。原因是少量 URL smoke 不能证明全网支持。
- 停止条件：URL 安全边界不清、PDF citation 失败、删除/重命名破坏引用合同。

## 5. V1.9 Research Quality / Conflict Labeling Completion

### 目标

将 V1.6-E 的 Research contract smoke 推进到人工质量可验收状态。

### 开发内容

1. Research 输出质量评估。
2. supported_conclusions / inferences / conflicts / missing_evidence 展示优化。
3. 冲突标注真实样本验收。已完成 approved dataset 的 `PASS_LIMITED`。
4. 补源建议可执行。
5. 无来源或资料不足时拒答。
6. 不自动联网搜索。

### 验收数据

- 数字人 P0 数据集。
- 至少 1 组存在观点差异或时间差异的补充资料。
- 至少 1 个资料不足问题。

### 验收标准

- Research 无来源时拒答。
- 补源后生成结构化报告。
- supported_conclusions 每条绑定 evidence_refs。
- inferences 明确标注为“基于来源的推断”。
- conflicts 如存在，逐条绑定来源证据。
- conflicts 为空时不宣称“完整冲突分析 ready”。
- missing_evidence 能说明缺口。
- suggested_source_actions 可执行。
- 不使用 provider 外部常识硬答。

### 必跑命令

```bash
npm run check
npm run smoke:v1.6-e-research
npm run smoke:v1.5-e-e2e
```

### 当前执行结果

- `npm run smoke:v1.9-research-quality`：PASS_LIMITED。
- `npm run smoke:v1.9-conflict-labeling`：PASS_LIMITED。
- `npm run smoke:v1.9-human-ux-package`：READY_FOR_HUMAN_ACCEPTANCE。
- `npm run smoke:v1.9-rc`：V1_9_READY_FOR_FINAL_HUMAN_ACCEPTANCE。

V1.9 剩余项转为人工 Research / conflict / UX 质量审查。

### 风险评估

- 规格漂移风险：HIGH 候选。原因是 Research 容易变成通用联网问答。
- 虚假验收风险：HIGH 候选。原因是 contract smoke 不能证明内容质量。
- 停止条件：无法提供人工质量评审，或出现资料外硬答。

## 6. V1.10 Phase 2/3 Output Contract-to-Implementation Decision

### 目标

对 PRD Phase 2/3 能力做最终 V1.x 决策：实现、继续 disabled，或移出 V1.x。

### 涉及能力

- Audio Overview。
- PPT generation。
- Mindmap。
- Document comparison。
- OCR / 扫描 PDF。

### 推荐策略

V1.x 阶段只建议做以下两类之一：

1. 保持 disabled shell，并明确 NOT_READY。
2. 如果要实现，必须逐项开独立阶段，不能一次性实现全部。

### 每项实现前置条件

- 后端合同。
- provider 或生成器。
- schema。
- UI 预览。
- 下载 / 导出。
- 真实数据 smoke。
- 人工质量验收。

### 验收标准

如果保持 disabled：

- UI 显示暂不可用或合同未就绪。
- 不发起生成请求。
- 不生成伪输出。
- 文档保持 NOT_READY。

如果实现任一项：

- 必须独立计划、独立测试、独立 RC。
- 不得把单项 PASS 扩大成 Phase 2/3 全部 ready。

### 风险评估

- 规格漂移风险：HIGH。
- 虚假验收风险：HIGH。
- 默认停止条件：没有独立合同和真实数据前，不进入实现。

### V1.10 文档入口

- `docs/design/V1.10/00_README.md`
- `docs/design/V1.10/v1_10_remaining_development_and_acceptance_plan.md`
- `docs/design/V1.10/v1_10_phase_2_3_output_decision_plan.md`
- `docs/design/V1.10/v1_10_ocr_scanned_pdf_decision_plan.md`
- `docs/design/V1.10/v1_10_plan_audit.md`
- `docs/design/V1.10/v1_10_manual_acceptance_checklist.md`

## 7. V1.x-RC Final PRD Acceptance / Release Handoff

### 目标

完成 V1.x 的最终 PRD 覆盖矩阵、人工验收、发布交接和 scoped sync。

### 必须验收路径

1. 创建 Notebook。
2. 导入 PDF / TXT / Markdown。
3. 添加有限公开 URL。
4. 等待解析 / 索引。
5. 查看 Notebook Guide。
6. 点击 Suggested Question。
7. 查看引用问答。
8. 点击 citation 定位来源片段。
9. 生成 Notes / Study Guide / Briefing Doc / FAQ。
10. 下载 Markdown / JSON。
11. 提问资料外问题，确认拒答和补源建议。
12. 添加补充来源。
13. 生成 Research report。
14. 检查 conflicts / missing_evidence。
15. 检查 Audio / PPT / Mindmap / Compare disabled 或单项已通过独立验收。
16. 归档 Notebook。

### 必跑命令

```bash
npm run check
npm run smoke:v1.5-e-e2e
npm run smoke:v1.7-ux
npm run smoke:v1.6-e-research
npm run smoke:v1.x-rc
```

V1.8 完成后补充：

```bash
npm run smoke:v1.4-sources-p0
npm run smoke:v1.6-a-url
```

### 人工验收与当前决策

当前交互式浏览器证据包已获用户认可，V1.x 最终状态为 `V1_X_FINAL_ACCEPTANCE_PASS_LIMITED`。以下内容保留为后续抽样复核建议，不再阻塞本轮 scoped sync：

- Guide 内容质量。
- QA citation 正确性。
- Studio 输出质量和引用完整性。
- Research 是否 source-grounded。
- 导出 Markdown / JSON 是否可打开。
- 页面是否具备普通用户可操作性。
- 是否存在未完成能力误导。

### 完成声明上限

当前 PASS_LIMITED 验收口径下，最多声明：

ResearchNotebook V1.x PRD MVP path is release-candidate-ready for validated PDF / TXT / Markdown and limited URL sources, with source-grounded Guide, QA, lightweight Studio outputs, export, citation navigation, and Research补源 workflow on approved datasets.

### 仍不能声明

- all websites URL extraction ready。
- all-source-type ready。
- OCR ready，除非 V1.10 独立实现并验收。
- Audio Overview ready，除非 V1.10 独立实现并验收。
- PPT generation ready，除非 V1.10 独立实现并验收。
- Mindmap ready，除非 V1.10 独立实现并验收。
- Document comparison ready，除非 V1.10 独立实现并验收。
- cloud sync / collaboration ready。

### 当前 RC 汇总入口

V1.x-RC 自动化汇总脚本：

```bash
npm run smoke:v1.x-rc
```

该脚本读取 V1.9-RC 与 V1.10 disabled boundary 结果，生成：

- `fixtures/real/v1_x/final-prd-acceptance/v1_x_final_prd_acceptance_result.json`
- `docs/design/V1.x/v1_x_final_prd_acceptance_report.md`
- `docs/design/V1.x/v1_x_release_handoff.md`

脚本在未获得人工认可前最高状态为 `V1_X_READY_FOR_FINAL_HUMAN_ACCEPTANCE`。当前已记录交互式浏览器证据包人工认可，因此最高状态为 `V1_X_FINAL_ACCEPTANCE_PASS_LIMITED`，但仍不得写成 all-source / all-domain ready。

## 8. 需要 ChatGPT 审计的文档路径

### 总计划

- `docs/design/V1.x/00_README.md`
- `docs/design/V1.x/v1_x_remaining_development_and_acceptance_plan.md`

### 当前基线

- `docs/design/V1.7/v1_7_current_gap_analysis.md`
- `docs/design/V1.7/v1_7_rc_browser_acceptance_report.md`
- `docs/design/V1.7/v1_7_manual_acceptance_checklist.md`
- `docs/design/V1.6/v1_6_prd_coverage_matrix.md`
- `docs/design/V1.6/v1_6_rc_final_acceptance_report.md`
- `docs/design/V1.5/v1_5_e_chromecli_manual_e2e_report.md`

### 后续执行时需要新增的文档

- `docs/design/V1.8/v1_8_sources_p0_p1_completion_plan.md`
- `docs/design/V1.8/v1_8_sources_p0_p1_acceptance_report.md`
- `docs/design/V1.9/v1_9_research_quality_completion_plan.md`
- `docs/design/V1.9/v1_9_research_quality_acceptance_report.md`
- `docs/design/V1.10/v1_10_phase_2_3_output_decision_plan.md`
- `docs/design/V1.x/v1_x_final_prd_acceptance_report.md`
- `docs/design/V1.x/v1_x_release_handoff.md`

## 9. 审计问题清单

请重点审计：

1. 是否仍存在把 PASS_LIMITED 扩大成全量 ready 的风险。
2. V1.8 是否过度扩大 URL 抽取范围。
3. V1.9 是否可能把 Research 做成通用联网问答。
4. V1.10 是否应该继续 disabled，而不是贸然实现 Phase 2/3。
5. V1.x-RC 的人工质量验收是否足够防止虚假验收。
6. 云同步 / 协作是否已正确剔除。
7. 每个阶段的停止条件是否足够明确。
