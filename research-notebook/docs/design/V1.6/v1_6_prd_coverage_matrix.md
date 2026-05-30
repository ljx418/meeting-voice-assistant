# ResearchNotebook V1.6 PRD Coverage Matrix

日期：2026-05-29

| PRD 功能点 | V1.5 状态 | V1.6 最终状态 | 备注 |
| --- | --- | --- | --- |
| Notebook 创建 / 列表 / 最近打开 | PASS_LIMITED | PASS_LIMITED | V1.6 只做回归，不扩大范围。 |
| PDF / TXT / Markdown 导入 | PASS_LIMITED | PASS_LIMITED | 增加扩展评测集；扫描 PDF 单独走 OCR。 |
| URL 正文抽取 | NOT_READY | PASS_LIMITED | V1.6-A 已完成限定公开 HTTP URL smoke；不声明 all websites ready。 |
| Notebook Guide | PASS_LIMITED | PASS_LIMITED_ACCEPTED | 扩展到多数据集评分，并经截图报告人工验收接受；不声明 all-domain。 |
| 引用问答 | PASS_LIMITED | PASS_LIMITED_ACCEPTED | 扩展到多数据集评分，并经 ChromeCLI / citation screenshot 人工验收接受。 |
| 资料不足拒答 | PASS_LIMITED | PASS_LIMITED | 加入 Research 补源路径。 |
| Notes | PASS_LIMITED | PASS_LIMITED | 加入导出。 |
| Study Guide | PASS_LIMITED | PASS_LIMITED | 加入导出。 |
| Briefing Doc | PASS_LIMITED | PASS_LIMITED | 加入导出。 |
| FAQ | PASS_LIMITED | PASS_LIMITED | 加入导出。 |
| Studio 输出下载 / 外发 | NOT_READY | PASS_LIMITED_ACCEPTED | V1.6-D 已实现 Markdown/JSON 下载和复制；截图报告人工验收接受，仍限 scoped artifacts。 |
| Research 补源 / 综合输出 | NOT_READY | PASS_LIMITED_CONTRACT_SMOKE | V1.6-E 已完成 source-grounded contract smoke；最终质量审查留到 RC。 |
| 冲突标注 | NOT_READY | CONTRACT_ONLY | V1.6-E 返回 conflicts 字段但不声明完整冲突识别 ready。 |
| OCR / 扫描 PDF | NOT_READY | CONTRACT_DISCOVERY_READY | OCR provider 未接入，不声明 ready。 |
| Audio Overview | NOT_READY | DISABLED_READY | V1.6-F 已展示 disabled shell；不生成音频。 |
| PPT 生成 | NOT_READY | DISABLED_READY | V1.6-F 已展示 disabled shell；不生成 PPT。 |
| 思维导图 | NOT_READY | DISABLED_READY | V1.6-F 已展示 disabled shell；不生成图。 |
| 文档对比 | NOT_READY | DISABLED_READY | V1.6-F 已展示 disabled shell；不生成对比报告。 |
| 云同步 / 协作 | OUT_OF_SCOPE | OUT_OF_SCOPE | 已从 V1.x 剩余目标剔除。 |

## V1.6 完成口径

V1.6 完成后最多声明：

ResearchNotebook PRD MVP path is broader-smoke-ready for validated PDF / TXT / Markdown and limited URL sources, with source-grounded Guide, QA, Studio exports, and Research补源 / 冲突分析 on approved datasets.

本声明依赖：

- `npm run check` PASS。
- `npm run smoke:v1.5-e-e2e` PASS。
- `npm run smoke:v1.1-visible-user-e2e` PASS。
- 用户对 `v1_6_manual_quality_review_screenshot_report.html` 的人工验收通过。

仍不得声明：

- all-source-type ready。
- all websites URL extraction ready。
- OCR ready，除非单独 smoke 通过。
- Audio / PPT / Mindmap / Document comparison ready，除非对应阶段从合同发现升级为真实实现和验收。
