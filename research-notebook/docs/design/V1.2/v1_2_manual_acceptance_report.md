# ResearchNotebook V1.2 手工验收报告

文档状态：待人工执行；自动浏览器 smoke 已覆盖 markdown/json 主路径。

## 验收范围

- Markdown source import。
- JSON source import。
- Source Preview Drawer。
- DocumentUnit selection。
- workspace query citation。
- EvidenceSpan highlight。

不验收 PDF/PPTX/HTML/video/audio ready。

## 手工验收用例

| 用例 | 状态 | 备注 |
| --- | --- | --- |
| 打开首页，中文界面可读 | PENDING_MANUAL | 不应显示内部阶段码作为主要用户文案。 |
| 创建 workspace | PASS_AUTOMATED | V1.2 browser smoke 已创建并进入 workspace。 |
| 导入 markdown source | PASS_AUTOMATED | 格式选择为 Markdown。 |
| markdown preview | PASS_AUTOMATED | Drawer 可见，文本安全渲染。 |
| markdown citation highlight | PASS_AUTOMATED | 高亮在 selected unit 内。 |
| 导入 json source | PASS_AUTOMATED | 格式选择为 JSON。 |
| json preview | PASS_AUTOMATED | Drawer 可见，文本安全渲染。 |
| json citation highlight | PASS_AUTOMATED | 高亮在 selected unit 内。 |
| PDF/PPTX/HTML/video/audio 边界 | PENDING_MANUAL | UI 不声明 ready。 |
| cleanup | PASS_AUTOMATED | smoke workspace 已归档。 |
