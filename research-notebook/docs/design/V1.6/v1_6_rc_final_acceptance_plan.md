# ResearchNotebook V1.6-RC Final PRD Acceptance / Manual Quality Review Plan

日期：2026-05-28

## 阶段目标

集中验收 V1.6 剩余 PRD 闭环：

- V1.6-B 多数据集候选输出人工评分。
- V1.6-D Studio Markdown / JSON 导出文件人工检查。
- V1.6-E Research report 质量人工检查。
- ChromeCLI / 浏览器路径验收。
- 最终 PRD coverage matrix 更新。

## Entry Gate

- V1.6-A URL：PASS_LIMITED。
- V1.6-B 自动质量候选包：CANDIDATE_READY_FOR_MANUAL_REVIEW。
- V1.6-C OCR：CONTRACT_DISCOVERY_READY。
- V1.6-D Studio 导出：PASS_LIMITED_UI_TESTED。
- V1.6-E Research：PASS_LIMITED_CONTRACT_SMOKE。
- V1.6-F Phase 2/3：DISABLED_READY。
- `npm run check` 当前通过。

## 硬规则

1. V1.6-B 自动候选评估不能替代人工质量评分。
2. Studio 导出文件必须在真实浏览器中人工下载并打开检查。
3. Research 质量不能只靠 contract smoke。
4. ChromeCLI / 浏览器路径不能证明内容质量。
5. 自动路径和人工质量评分必须同时通过。
6. 人工验收未完成前，规格漂移风险和虚假验收风险保持 HIGH。
7. 不得在人工验收未完成前声明 V1.6 completed。
8. 不得在任一人工验收失败时进入 final sync / release handoff。

## 环境记录

必须在 `docs/design/V1.6/v1_6_rc_final_acceptance_report.md` 中填写：

- frontend URL。
- data_service URL。
- browser / ChromeCLI。
- smoke timestamp。
- frontend commit / branch。
- data_service commit / branch。

## 浏览器主路径人工验收

1. 打开浏览器进入 ResearchNotebook。
2. 使用数字人 P0 数据集创建 Notebook。
3. 导入数字人 P0 Markdown。
4. 导入数字人 P0 PDF。
5. 查看 Notebook Guide。
6. 点击 Suggested Question。
7. 查看引用问答。
8. 点击 citation，确认 SourcePreview / DocumentUnit / EvidenceSpan 定位。
9. 生成 Studio Notes / Study Guide / Briefing Doc / FAQ。
10. 下载 Markdown / JSON。
11. 提问资料外问题，确认拒答和补源建议。
12. 添加补充来源后生成 Research report。
13. 检查 Phase 2/3 工具全部 disabled，不生成伪输出。
14. cleanup / archive workspace。

## Studio 导出人工检查

至少检查：

- Markdown 文件可下载并打开。
- Markdown 包含标题、summary、sections。
- Markdown 包含 citation metadata。
- JSON 文件可下载并打开。
- JSON 包含 artifact_id / artifact_type。
- JSON 包含 sections / evidence_refs。
- JSON 包含 schema_version / exported_at。
- 文件内容不含 `/Users`、`file://`、cache path、artifact physical path。

## 人工评分

使用：

```text
docs/design/V1.6/v1_6_b_manual_quality_review_template.md
```

必须覆盖：

- 资料相关性。
- 覆盖完整性。
- citation 正确性。
- 拒答正确性。
- 中文表达。
- 幻觉风险。

通过阈值：

- Guide 可用性 >= 4/5。
- QA citation 正确率 >= 80%。
- 拒答正确率 >= 80%。
- citation 可定位率 >= 90%。
- 高危幻觉 = 0。

## Research 人工检查

必须检查：

- 无来源时拒答。
- 补源后可生成 structured report。
- supported_conclusions 来自来源。
- supported_conclusions 绑定 evidence_refs。
- inferences 明确标注为基于来源的推断。
- conflicts 为空时没有宣称完整冲突分析 ready。
- missing_evidence 合理。
- suggested_source_actions 可执行。
- 未自动联网搜索。

## Phase 2/3 disabled 检查

必须确认：

- Audio Overview disabled。
- PPT generation disabled。
- Mindmap disabled。
- Document comparison disabled。
- 不生成真实输出。
- 不发起后端生成请求。
- UI 显示合同未就绪 / 暂不可用。

## RC report 更新规则

如果任一项失败：

- 记录 FAIL / NOT_READY / DEGRADED_ACCEPTED。
- 不改 final decision。
- 不进入 final sync。

如果全部通过：

- 将 Final Decision 从 NOT_READY_FOR_FINAL_DECLARATION 改为 V1.6_FINAL_ACCEPTANCE_PASS。
- 同步更新：
  - `docs/design/V1.6/v1_6_current_gap_analysis.md`
  - `docs/design/V1.6/v1_6_current_gap_analysis.drawio`
  - `docs/design/V1.6/v1_6_prd_coverage_matrix.md`
  - `docs/design/V1.6/00_README.md`

## 完成口径

如果人工验收通过，最多声明：

ResearchNotebook V1.6 PRD MVP path is broader-smoke-ready for validated PDF / TXT / Markdown and limited URL sources, with source-grounded Guide, QA, Studio exports, and Research contract smoke on approved datasets.

仍不能声明：

- all websites URL extraction ready。
- OCR ready。
- Audio / PPT / Mindmap / Document comparison ready。
- all-domain Research ready。
- 云同步 / 协作。

## 停止条件

本阶段存在人工验收要求，自动执行必须停止，由用户主导最终质量判断。

如果人工验收未完成：

```text
ResearchNotebook V1.6 remains PENDING_HUMAN_ACCEPTANCE.
Do not final sync.
Do not release.
```
