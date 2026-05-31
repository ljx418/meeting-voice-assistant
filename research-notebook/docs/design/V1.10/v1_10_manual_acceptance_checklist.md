# ResearchNotebook V1.10 手工验收清单

日期：2026-05-31

## 验收目标

确认 V1.10 的 Phase 2/3 和 OCR 边界清晰，用户不会误以为未实现能力已经可用。

## 环境

- frontend URL：待填写
- data_service URL：待填写
- browser：待填写
- tester：待填写
- timestamp：待填写

## 手工验收步骤

1. 打开 ResearchNotebook。
2. 创建或进入一个 Notebook。
3. 导入 Markdown / TXT / 可抽取文本 PDF。
4. 确认轻量 Studio 输出仍可生成：
   - Notes
   - Study Guide
   - Briefing Doc
   - FAQ
5. 在 Studio 中找到“后续输出工具”。
6. 确认 Audio Overview 显示暂不可用。
7. 确认 PPT generation 显示暂不可用。
8. 确认 Mindmap 显示暂不可用。
9. 确认 Document comparison 显示暂不可用。
10. 尝试点击 disabled 工具，确认不会生成 artifact。
11. 打开浏览器 Network，确认 disabled 工具不会发起后端生成请求。
12. 导入可抽取文本 PDF，确认仍可 preview / citation。
13. 如有扫描 PDF 样本，导入后确认显示 OCR required / unsupported，不声明 OCR ready。
14. 检查页面文案，不应出现“音频概览已就绪”“PPT 已就绪”“OCR 已就绪”等误导。

## PASS 标准

- 所有 Phase 2/3 工具都保持 disabled。
- disabled 工具不会触发后端生成请求。
- 不生成伪音频、伪 PPT、伪思维导图、伪文档对比。
- 可抽取文本 PDF 不回退。
- 扫描 PDF 不被误写成 OCR ready。
- 文档和 UI 的声明一致。

## FAIL 条件

- 任一 disabled 工具可点击并触发后端生成。
- 生成了伪输出 artifact。
- 页面或文档声明 OCR / Audio / PPT / Mindmap / Compare ready。
- 扫描 PDF 被当作可抽取文本 PDF 成功。
- 出现 raw filesystem path、cache path、artifact physical path。

## 人工验收结论

状态：`PENDING_HUMAN_ACCEPTANCE`

备注：

- 待人工填写。
