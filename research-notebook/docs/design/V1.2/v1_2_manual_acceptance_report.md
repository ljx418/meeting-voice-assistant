# ResearchNotebook V1.2 手工验收报告

文档状态：SKIPPED_BY_PRODUCT_DECISION。

V1.2 不再执行传统手工验收。原因是当前用户体验仍偏“手动导入 + 手动提问 + 手动查看证据”，不符合目标体验“用户直接对 Agent 说目标，由 Agent 搭建并运行 workflow”。

V1.2 自动浏览器 smoke 仍保留为技术基线；最终用户验收迁移到 V1.3 Agent Workflow 入口。

## 验收范围

- Markdown source import。
- JSON source import。
- Source Preview Drawer。
- DocumentUnit selection。
- workspace query citation。
- EvidenceSpan highlight。

不验收 PDF/PPTX/HTML/video/audio ready。

## 原手工验收用例状态

| 用例 | 状态 | 备注 |
| --- | --- | --- |
| 打开首页，中文界面可读 | SKIPPED | V1.3 Agent entry 将作为最终入口。 |
| 创建 workspace | PASS_AUTOMATED | V1.2 browser smoke 已创建并进入 workspace。 |
| 导入 markdown source | PASS_AUTOMATED | 格式选择为 Markdown。 |
| markdown preview | PASS_AUTOMATED | Drawer 可见，文本安全渲染。 |
| markdown citation highlight | PASS_AUTOMATED | 高亮在 selected unit 内。 |
| 导入 json source | PASS_AUTOMATED | 格式选择为 JSON。 |
| json preview | PASS_AUTOMATED | Drawer 可见，文本安全渲染。 |
| json citation highlight | PASS_AUTOMATED | 高亮在 selected unit 内。 |
| PDF/PPTX/HTML/video/audio 边界 | SKIPPED | 边界继续保持 NOT_READY，后续通过 V1.3 合同处理。 |
| cleanup | PASS_AUTOMATED | smoke workspace 已归档。 |

## V1.3 验收替代路径

V1.3 的最终验收用例为：

```text
用户输入：递归总结 Desktop/技术分享，每个子文件夹生成一份总结。
系统行为：Agent 生成 workflow draft，用户授权后运行，输出子文件夹 summary 和根目录总览，并支持 evidence citation 回跳。
```
