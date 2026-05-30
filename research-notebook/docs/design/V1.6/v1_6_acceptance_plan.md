# ResearchNotebook V1.6 Acceptance Plan

日期：2026-05-28

## 验收原则

V1.6 每个阶段必须同时完成：

1. 功能验收。
2. PRD 规格检视。
3. 规格漂移风险评估。
4. 虚假验收风险评估。
5. 文档和 fixture 脱敏检查。

若规格漂移或虚假验收风险为 HIGH，停止进入下一阶段。

## 真实数据要求

V1.6 不允许只用 mock 数据声明 ready。

最低要求：
- 继续保留 `Desktop/技术分享/11-数字人` 作为回归数据集。
- 新增至少 2 个不同主题数据集。
- URL 验收必须使用真实网页。
- OCR 验收必须使用真实扫描 PDF；若没有 OCR provider，则只做合同发现。

## 阶段验收摘要

| 阶段 | 必须验收 | 不得声明 |
| --- | --- | --- |
| V1.6-0 Gate | V1.5 revalidation、V1.6 scope、URL 安全门禁 | 直接进入实质开发 |
| V1.6-A URL | URL source 导入、抽取、citation 定位 | all websites ready |
| V1.6-B 扩展评测 | 至少 3 组数据集和人工评分 | 单数据集泛化 ready |
| V1.6-C OCR | OCR 合同或真实 OCR smoke | 扫描 PDF ready，除非 OCR smoke 通过 |
| V1.6-D Studio 导出 | Markdown/JSON 导出保留 citation | 设计工具流转 ready，除非单独验收 |
| V1.6-E Research | 补源、综合、冲突标注、引用 | 互联网通用问答 ready |
| V1.6-F Phase 2/3 合同 | Audio/PPT/Mindmap/Compare 合同和 disabled shell | 输出能力 ready |
| V1.6-RC | 集中浏览器验收和 `npm run check` | 全格式 / 全网站 / 全行业 ready |

## 必须执行的验收类型

### V1.6-0 文档验收

- `v1_5_0_plan_audit.md` 明确为历史阻塞记录。
- `v1_5_revalidation_report.md` 是 V1.6 entry gate 的 V1.5 当前状态来源。
- V1.6-A URL 安全门禁包含 SSRF、权限、内容安全、资源限制和稳定错误。
- V1.6 drawio 可解析，并显示 V1.6-0 gate 和 OUT_OF_SCOPE。
- 本阶段不新增业务代码、不新增 route、不新增 smoke script。

### 自动化验收

- 每个实现阶段必须有 smoke script 或 focused test。
- 任何涉及 source / route / adapter 的改动必须通过 `npm run check`。
- 涉及 data_service 的阶段必须有 backend focused tests。

### 浏览器验收

- V1.6-D、V1.6-E、V1.6-RC 必须通过 ChromeCLI 或手工浏览器路径。
- 浏览器验收必须覆盖普通用户路径，不只验证 API。

### 人工质量验收

- V1.6-B 和 V1.6-E 必须有人工作质量表。
- ChromeCLI 通过不能替代人工内容质量判断。
- 人工评分表必须记录样本、问题、输出、citation、评分和结论。

### V1.6-RC 最终人工验收门禁

V1.6-RC 必须执行人工验收。自动化 smoke 只能作为 baseline，不能替代最终质量判断。

必须覆盖：

- 环境记录：frontend URL、data_service URL、browser / ChromeCLI、timestamp、frontend commit / branch、data_service commit / branch。
- 浏览器主路径：创建 Notebook、导入数字人 P0 Markdown、导入数字人 P0 PDF、查看 Guide、点击 Suggested Question、引用问答、citation 回跳、Studio 四类输出、导出 Markdown / JSON、资料外拒答、Research report、Phase 2/3 disabled、cleanup。
- Studio 导出人工检查：Markdown / JSON 可打开，包含 citation metadata / evidence_refs / schema_version，且不含本地绝对路径、cache path、artifact physical path。
- 多数据集人工评分：Guide 可用性 >= 4/5，QA citation 正确率 >= 80%，拒答正确率 >= 80%，citation 可定位率 >= 90%，高危幻觉 = 0。
- Research 人工检查：无来源拒答、补源后 structured report、supported_conclusions 绑定 evidence_refs、inferences 标注为基于来源的推断、missing_evidence 合理、未自动联网搜索。
- Phase 2/3 disabled 检查：Audio / PPT / Mindmap / Compare 不生成真实输出、不发起后端生成请求。

如果任一项失败：

- 记录 FAIL / NOT_READY / DEGRADED_ACCEPTED。
- 不改 final decision。
- 不进入 final sync。

如果人工验收未完成：

```text
ResearchNotebook V1.6 remains PENDING_HUMAN_ACCEPTANCE.
Do not final sync.
Do not release.
```

## 建议命令命名

- `npm run smoke:v1.6-a-url`
- `npm run smoke:v1.6-b-quality`
- `npm run smoke:v1.6-c-ocr`
- `npm run smoke:v1.6-d-export`
- `npm run smoke:v1.6-e-research`
- `npm run smoke:v1.6-f-contracts`
- `npm run smoke:v1.6-rc`

这些命令只有在对应阶段实现后才需要加入 `package.json`。

## 打回规则

任一情况发生时，阶段验收失败：

- 关键结论无 citation。
- citation 无法定位。
- 资料不足时硬答。
- 失败状态没有稳定错误语义。
- fixtures 或报告泄漏 API key、本地绝对路径、cache path、artifact physical path。
- 将 disabled shell 声明为 ready。
- 将限定数据集通过扩大为 all-source-type ready。
- URL 抽取计划缺少 SSRF / redirect / private IP / robots / max_response_size / content_type allowlist 任一关键门禁。

## V1.x 范围剔除

云同步 / 协作不纳入 V1.6 验收，不作为 V1.x 剩余闭环项。
