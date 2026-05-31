# ResearchNotebook V1.7 UX Recomposition Development Plan

日期：2026-05-30

## 目标

V1.7 不新增产品能力，只把 V1.6 已通过的 PRD MVP 受限能力整理成更接近 NotebookLM 的三列体验。

核心用户路径：

1. 创建 Notebook。
2. 导入 PDF / TXT / Markdown 或限定公开 URL。
3. 查看资料导读。
4. 点击建议追问。
5. 查看带引用回答。
6. 点击引用定位来源片段。
7. 生成笔记、学习导读、资料简报、常见问题。
8. 导出 Markdown / JSON。

## 子阶段

| 阶段 | 目标 | 状态 |
| --- | --- | --- |
| V1.7-0 | 计划与审计门禁 | PASS |
| V1.7-A | UX baseline 审计 | PASS |
| V1.7-B | 三列布局重组 | PASS_LIMITED |
| V1.7-C | 来源 UX hardening | PASS_LIMITED |
| V1.7-D | Guide-first Chat UX | PASS_LIMITED |
| V1.7-E | Studio 输出 UX | PASS_LIMITED |
| V1.7-F | 引用与 Drawer 交互清理 | PASS_LIMITED |
| V1.7-G | 中文文案与开发态文字清理 | PASS_LIMITED |
| V1.7-RC | 浏览器与手工验收 | PENDING |

## 风险门禁

每个阶段必须记录：

- PRD 对照。
- 真实数据验收结果。
- 自动化命令结果。
- 规格漂移风险。
- 虚假验收风险。
- 下一阶段审计结论。

若规格漂移或虚假验收任一为 HIGH，停止自动推进。

## 禁止项

- 不实现 OCR。
- 不实现音频概览。
- 不实现 PPT。
- 不实现思维导图。
- 不实现文档对比。
- 不实现云同步或协作。
- 不新增任意 Agent 工具执行。
- 不把 disabled shell 写成 ready。
