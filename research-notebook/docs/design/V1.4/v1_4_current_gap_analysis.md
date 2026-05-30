# ResearchNotebook V1.4 当前差距分析

日期：2026-05-26

## 一句话结论

V1.4 以 PRD Phase 1 MVP 为主线，目标是完成 NotebookLM 风格的核心体验：

```text
Sources -> Notebook Guide / Chat -> Studio
```

当前 V1.4-0/A/B/C/D/E/F/G/H/RC 已完成到受限可验收状态：文档重基线、三列 Notebook 骨架、Notebook 生命周期、P0 Sources 浏览器上传、后端抽取合同、Notebook Guide 确定性导读、Source-grounded Chat 拒答补源、Studio 轻量输出、citation 定位产品化确认、补源入口和自动化集中验收已落地。

## 当前状态

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| V1.3 Agent folder summary | PASS_LIMITED | 保留为 Studio 侧扩展入口，最终验收后移至 V1.4-RC。 |
| 三列 Notebook 布局 | PASS_LIMITED | Sources / Chat / Studio 骨架已落地；真实 Guide / Studio 输出仍未接入。 |
| Notebook 生命周期 | PASS_LIMITED | 创建、列表、重命名、归档、最近打开可用；物理删除和跨设备最近打开不声明 ready。 |
| Notebook Guide | PASS_LIMITED | 后端 `/guide` 返回 Overview / Key Topics / Suggested Questions；点击建议问题会进入带证据问答。当前为确定性 source-grounded 导读，不声明完整 AI Guide 质量 ready。 |
| Studio 轻量输出 | PASS_LIMITED | Notes / Study Guide / Briefing Doc / FAQ route 与 UI 已接入；每个可用输出保留 evidence_refs。当前为确定性轻量输出，不声明高质量 AI 写作 ready。 |
| Sources P0 | PASS_LIMITED | AI 数字人资料包已证明 Markdown/TXT/可抽取文本 PDF browser upload/import-build-preview-query citation 通过。 |
| PDF P0 | PASS_LIMITED | 用户提供真实 PDF 已完成 `PDF_EXTRACTED` preview 和 query citation；扫描版/OCR/原版 PDF 页面渲染不声明 ready。 |
| Source-grounded Chat | PASS_LIMITED | 引用问答、资料不足拒答、补源建议和轻量推断提示已接入；不声明完整 Research / 冲突分析 / all-session ready。 |
| Citation navigation | PASS_LIMITED | Chat / Studio citation 可进入 SourcePreviewDrawer / DocumentUnit / EvidenceSpan；不声明 all-source-type precise backjump ready。 |
| 补源入口 | PASS_LIMITED | 资料不足时展示补源建议，并可跳转到来源导入表单；不声明自动 Research 或联网搜索 ready。 |
| V1.4-RC 自动化集中验收 | PASS_LIMITED | 后端 focused tests、前端 focused tests、npm run check、sources P0 smoke 均通过。仍需人工体验和 AI 质量验收进入 V1.5。 |

## V1.3 验收迁移

以下 V1.3 验收不再单独提前执行，统一并入 V1.4-RC：

- 手工验收报告补强。
- UI/UX hardening。
- Summary 质量评估。
- 空文件夹、大文件、全 unsupported 文件、权限失败、路径错误、深目录等边界补测。
- V1.3 文档最终同步和 scoped sync。

## V1.4 未完成核心项

| 项 | 状态 | 阻塞 |
| --- | --- | --- |
| Notebook 物理删除 / 跨设备最近打开 | NOT_READY | 当前以归档和本地最近打开满足 MVP 受限范围。 |
| PDF/TXT/Markdown P0 上传解析 | PASS_LIMITED | Markdown/TXT/可抽取文本 PDF 浏览器式上传和后端 smoke 通过；扫描版 PDF/OCR 不声明 ready。 |
| Notebook Guide 后端合同 | PASS_LIMITED | `/api/workspaces/{workspace_id}/guide` 已接入；仍不声明 LLM 深度综合 Guide ready。 |
| Studio 输出后端合同 | PASS_LIMITED | `/studio/artifacts` 支持 Notes / Study Guide / Briefing Doc / FAQ；下载、外发和设计工具流转未声明 ready。 |
| 资料不足拒答与补源引导 | PASS_LIMITED | workspace query 已实现 no_sources / insufficient_evidence refusal、补源建议和“添加来源”入口；session query 与完整 Research 不声明 ready。 |

## V1.5 Backlog

- AI / Claude 质量版 Notebook Guide 和 Studio 输出。
- ChromeCLI / 人工体验验收。
- 摘要质量、引用正确率、拒答正确率评估。
- Audio Overview。
- PPT 生成。
- 思维导图。
- 文档对比。
- 更强 Research 综合输出。
- URL 正文抽取稳定化。
- Studio 下载 / 外发。
- Figma / Stitch 输出协同。
- 移动端完整验收。
- 多格式深度 citation。
- 协作、权限、云同步。
- Assessment / Mastery。
- Quality / Governance Console。
- Graph editing / governance。
