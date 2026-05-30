# ResearchNotebook V1.5 Acceptance Plan

日期：2026-05-26

## 真实数据

验收目录：

```text
Desktop/技术分享/11-数字人
```

验收文件：

- PDF：`AI数字人产业发展报告_2026-05-26.pdf`
- Markdown：`AI数字人资料包/*.md`

## 端到端验收主路径

1. 启动 data_service。
2. 启动 ResearchNotebook。
3. 打开浏览器。
4. 创建 Notebook：`V1.5 AI 数字人验收`。
5. 上传 Markdown 文件。
6. 上传可抽取文本 PDF。
7. 等待解析完成。
8. 查看 Notebook Guide。
9. 点击 Suggested Question。
10. 查看带引用回答。
11. 点击 citation，确认 SourcePreviewDrawer 打开。
12. 确认 DocumentUnit / EvidenceSpan 定位。
13. 生成 Notes。
14. 生成 Study Guide。
15. 生成 Briefing Doc。
16. 生成 FAQ。
17. 点击 Studio citation，确认定位。
18. 提问资料外问题，确认拒答。
19. 点击添加来源，确认进入来源导入。
20. 归档验收 Notebook。

## 质量验收

### Guide

- Overview 不是固定模板。
- Key Topics 与数字人资料相关。
- Suggested Questions 可用于继续问答。
- Guide 至少引用一个来源片段。

### Chat

- 回答默认基于 sources。
- 关键断言带 citation。
- 无依据时拒答。
- 推断内容标注为推断。

### Studio

- Notes 可保存重点摘录。
- Study Guide 有结构化大纲。
- Briefing Doc 面向汇报。
- FAQ 每条有答案和引用。
- 无证据时不生成无来源输出。

## 打回规则

任一情况发生时，验收失败并打回计划阶段：

- LLM 未真实调用。
- 输出仍是模板化占位。
- 关键结论无 citation。
- citation 无法定位。
- 资料不足时硬答。
- fixtures 或报告泄漏 API key / 本地绝对路径 / cache path。
- ChromeCLI 路径无法完成主流程。

## 成功声明

仅当真实 LLM + 真实数据 + E2E 验收全部通过，才允许声明：

```text
ResearchNotebook V1.5 AI Guide and Studio outputs are quality-smoke-ready for the AI digital human P0 dataset.
```

仍不能声明：

- all-source-type ready。
- OCR ready。
- Word / PPT / audio / video ready。
- arbitrary Agent ready。

范围剔除：

- 云同步 / 协作不进入 V1.x 剩余验收范围。
