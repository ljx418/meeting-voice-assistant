# ResearchNotebook V1.4 PRD Phase 1 MVP Plan

日期：2026-05-26

## 目标

V1.4 将产品主线从 V1.3 的受限 Agent 文件夹总结工作流，调整为 PRD Phase 1 MVP：

```text
导入资料 -> 自动生成 Notebook Guide -> 基于来源的引用问答 -> Studio 轻量输出
```

V1.3 遗留的手工验收、summary 质量验收、异常边界验收统一后移到 V1.4-RC Final Acceptance。

## 范围

V1.4 必须完成：

- Notebook 三列布局：Sources / Chat / Studio。
- Notebook 生命周期：创建、列表、重命名、删除或归档、最近打开。
- Sources P0：PDF / TXT / Markdown 导入、解析状态、删除、重命名、失败重试。
- Notebook Guide：Overview / Key Topics / Suggested Questions。
- Source-grounded Chat：只基于当前 sources 回答，关键断言带引用，资料不足时拒答并引导补源。
- Studio 轻量输出：Notes / Study Guide / Briefing Doc / FAQ，均带引用。
- 引用定位：Chat / Studio citation 可定位到来源片段。

V1.4 不声明：

- Audio Overview。
- PPT 生成。
- 思维导图。
- 文档对比。
- 完整 Research 综合输出。
- 云同步、协作、治理、Assessment。

这些内容进入 V1.5 backlog。

## 阶段拆分

| 阶段 | 目标 | 状态 |
| --- | --- | --- |
| V1.4-0 | PRD 重基线和文档重排 | PASS |
| V1.4-A | 三列 Notebook 信息架构 | PASS_LIMITED |
| V1.4-B | Notebook 生命周期补齐 | PASS_LIMITED |
| V1.4-C | Sources P0 导入与解析 | PASS_LIMITED |
| V1.4-D | Notebook Guide | PASS_LIMITED |
| V1.4-E | Source-grounded Chat | PASS_LIMITED |
| V1.4-F | Studio 轻量输出 | PASS_LIMITED |
| V1.4-G | 来源定位与引用高亮产品化 | PASS_LIMITED |
| V1.4-H | 资料不足补源引导 | PASS_LIMITED |
| V1.4-RC | PRD Phase 1 + V1.3 后移验收 | PASS_LIMITED |

## V1.4-0 验收

- V1.4 文档目录存在。
- V1.3 验收后移到 V1.4-RC 的决策已记录。
- V1.5 backlog 已记录 Phase 2/3 和未完成增强项。

## V1.4-A 验收

- 工作区页面展示 Sources / Chat / Studio 三列。
- 中列默认展示 Notebook Guide 区域。
- Studio 列展示 Notes / Study Guide / Briefing Doc / FAQ 入口。
- Agent 文件夹总结工作流保留为 Studio 侧扩展入口。
- Guide / Studio 后端合同未接入时，不伪造 ready。

当前结论：V1.4-A 为 PASS_LIMITED。三列信息架构和 Guide / Studio 壳已落地，但 Guide 生成、Studio 输出、P0 文件导入仍依赖后续后端合同和真实 smoke，不得声明 PRD Phase 1 ready。

## V1.4-B 验收

- 创建和列表：PASS。
- 重命名：PASS。
- 删除或归档：PASS_LIMITED，当前通过归档满足，不声明物理删除。
- 最近打开：PASS_LIMITED，本地浏览器状态，不声明跨设备同步。

当前结论：V1.4-B 为 PASS_LIMITED。Notebook 生命周期 MVP 基础可用，但物理删除和跨设备最近打开不在当前 ready 范围内。

## V1.4-C 审计

- TXT / Markdown browser text submit：PASS_LIMITED。
- Source remove / rename / build / preview 受限路径：PARTIAL。
- PDF browser upload / 抽取 / preview / citation smoke：PASS_LIMITED。
- 扫描版 PDF / OCR：NOT_READY。

AI 数字人资料包 smoke 更新：

- Markdown import / build / preview / query citation：PASS。
- TXT import / build / preview / query citation：PASS。
- 用户提供 PDF 样本：browser upload import PASS，preview 为 PDF_EXTRACTED，query citation PASS。

当前结论：V1.4-C 为 PASS_LIMITED。Markdown / TXT / 可抽取文本 PDF 浏览器式上传 smoke 通过；下一步应执行 V1.4-D Notebook Guide。不得声明扫描版 PDF、OCR 或原版 PDF 页面渲染 ready。

## V1.4-D 审计

- Guide 后端 route：PASS，`GET /api/workspaces/{workspace_id}/guide`。
- Overview / Key Topics / Suggested Questions：PASS。
- Suggested Question 进入带证据问答：PASS。
- evidence_refs 使用 source_id / unit_id / evidence_id：PASS_LIMITED。
- 完整 AI 质量 Guide：NOT_READY。

当前结论：V1.4-D 为 PASS_LIMITED。Notebook Guide 已从 shell 升级为确定性 source-grounded 导读，但不声明完整 LLM 深度综合质量 ready。下一步应执行 V1.4-E Source-grounded Chat，补齐资料不足拒答、补源引导和推断标注。

## V1.4-E 审计

- 有证据回答：PASS。
- 无来源拒答：PASS。
- 有来源但无匹配证据拒答：PASS。
- 补源建议：PASS。
- 轻量推断提示：PASS_LIMITED。
- 完整 Research、冲突分析、session query 全量策略：NOT_READY。

当前结论：V1.4-E 为 PASS_LIMITED。workspace query 已遵守 source-grounded 默认行为，不再硬答资料外问题。下一步应执行 V1.4-F Studio 轻量输出。

## V1.4-F 审计

- Notes：PASS_LIMITED。
- Study Guide：PASS_LIMITED。
- Briefing Doc：PASS_LIMITED。
- FAQ：PASS_LIMITED。
- evidence_refs：PASS。
- 无证据拒绝生成：PASS。
- 高质量 AI 输出、下载、外发、设计工具流转：NOT_READY。

当前结论：V1.4-F 为 PASS_LIMITED。Studio 轻量输出合同和 UI 可用，但当前为确定性模板化输出，不声明完整 AI 写作质量 ready。下一步应执行 V1.4-G 来源定位与引用高亮产品化确认。

## V1.4-G 审计

- Chat citation 定位：PASS_LIMITED。
- Studio citation 定位：PASS_LIMITED。
- SourcePreviewDrawer / DocumentUnit / EvidenceSpan 复用路径：PASS。
- all-source-type precise backjump：NOT_READY。
- OCR / 扫描版 PDF 定位：NOT_READY。

当前结论：V1.4-G 为 PASS_LIMITED。下一步应执行 V1.4-H 资料不足补源入口收口。

## V1.4-H 审计

- 资料不足状态展示：PASS。
- 补源建议展示：PASS。
- 添加来源入口：PASS。
- 焦点跳转到来源导入表单：PASS。
- 联网搜索 / 自动 Research：NOT_READY。

当前结论：V1.4-H 为 PASS_LIMITED。下一步进入 V1.4-RC 集中验收。

## V1.4-RC 审计

- 后端 focused tests：PASS。
- 前端 focused tests：PASS。
- `npm run check`：PASS。
- V1.4 Sources P0 真实 smoke：PASS_LIMITED。
- 人工体验验收：NOT_READY。
- AI / Claude 输出质量：NOT_READY。

当前结论：V1.4-RC 为 PASS_LIMITED。V1.4 开发主线收口，但如果按完整 PRD 商用品质验收，还需要 V1.5 进入 AI 输出质量和人工体验验收。

## 风险门禁

每个阶段结束后必须记录：

- 完成内容。
- 未完成内容。
- 测试结果。
- 规格漂移评估。
- 虚假验收评估。
- 是否允许进入下一阶段。

HIGH 或 BLOCKING 风险必须停止自动推进。
