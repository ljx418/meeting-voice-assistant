# ResearchNotebook V1.10 剩余开发及验收计划

日期：2026-05-31

## 1. 当前基线

V1.10 承接 V1.9：

- V1.9 Research quality：`PASS_LIMITED`
- V1.9 conflict labeling：`PASS_LIMITED`
- V1.9 human UX acceptance package：`READY_FOR_HUMAN_ACCEPTANCE`
- V1.9 RC：`V1_9_READY_FOR_FINAL_HUMAN_ACCEPTANCE`

V1.10 处理 PRD Phase 2/3 与 OCR / 扫描 PDF 的剩余决策，不再扩展云同步 / 协作。云同步 / 协作已从 V1.x 剩余范围剔除。

## 2. 阶段目标

V1.10 的目标不是“把所有 Phase 2/3 都做完”，而是完成 V1.x 的高风险能力决策：

1. OCR / 扫描 PDF 是否进入实现。
2. Audio Overview 是否进入实现。
3. PPT generation 是否进入实现。
4. Mindmap 是否进入实现。
5. Document comparison 是否进入实现。
6. 如果不实现，确保 UI / 文档 / 验收报告都保持 disabled / NOT_READY。

## 3. 推荐阶段划分

### V1.10-0 Scope Rebase / PRD Decision Gate

目标：

- 复核 PRD 中 Phase 2/3 是后置能力，不是 MVP 必须完成项。
- 复核 V1.6-F disabled shell 当前仍有效。
- 复核 V1.9 已进入人工验收入口。

验收：

- `npm run check` PASS。
- V1.10 文档明确不把 disabled shell 写成 ready。
- 规格漂移风险和虚假验收风险已记录。

状态建议：`PASS`

### V1.10-A OCR / Scanned PDF Decision

目标：

- 确认是否接入 OCR provider。
- 如果没有 provider，保持 OCR `NOT_READY`，扫描 PDF 返回 `ocr_required` / `unsupported_ocr`。
- 不把可抽取文本 PDF 的 PASS_LIMITED 扩大为扫描 PDF ready。

默认决策：

- 不实现 OCR。
- 保持 `CONTRACT_DISCOVERY_READY`。

如果未来实现，必须新增独立阶段：

- OCR provider contract。
- page text extraction schema。
- page_no / bbox / confidence schema。
- DocumentUnit / EvidenceSpan 对 OCR text 的定位合同。
- 扫描 PDF 真实 smoke。
- 人工质量验收。

### V1.10-B Audio Overview Decision

目标：

- 判断是否进入音频概览真实生成。

默认决策：

- 不实现 Audio Overview。
- 保持 disabled shell。

如果未来实现，必须具备：

- audio script schema。
- TTS provider。
- audio artifact schema。
- 播放器 UI。
- 下载 / 导出合同。
- 真实播放 smoke。
- 人工收听验收。

### V1.10-C PPT Generation Decision

目标：

- 判断是否进入 PPT 生成。

默认决策：

- 不实现 PPT generation。
- 保持 disabled shell。

如果未来实现，必须具备：

- slide schema。
- layout schema。
- export format 决策。
- 下载合同。
- citation metadata 保留。
- 真实 PPT 文件打开验收。

### V1.10-D Mindmap Decision

目标：

- 判断是否进入思维导图生成。

默认决策：

- 不实现 Mindmap。
- 保持 disabled shell。

如果未来实现，必须具备：

- node / edge schema。
- layout contract。
- citation refs。
- 可视化预览。
- 导出合同。
- 人工可读性验收。

### V1.10-E Document Comparison Decision

目标：

- 判断是否进入文档对比分析。

默认决策：

- 不实现 Document comparison。
- 保持 disabled shell。

如果未来实现，必须具备：

- 至少两个来源输入合同。
- diff / agreement / disagreement schema。
- conflict evidence refs。
- citation backjump。
- 真实对比数据集。
- 人工质量验收。

### V1.10-RC Disabled Boundary Acceptance

目标：

- 验证 Phase 2/3 和 OCR 仍以正确方式 disabled，不生成伪输出，不误导用户。

验收：

- 页面可见 Audio / PPT / Mindmap / Document comparison 为“暂不可用”。
- disabled 工具不发起后端生成请求。
- OCR / 扫描 PDF 不声明 ready。
- PRD coverage matrix 保留 NOT_READY / DISABLED_READY。
- `npm run check` PASS。

## 4. 必跑命令

```bash
npm run check
npm run smoke:v1.7-ux
npm run smoke:v1.9-rc
npm run smoke:v1.10-disabled-boundary
```

如果 V1.10 只保持 disabled / decision 状态，可不新增真实生成 smoke。

如果任一能力进入实现，则必须新增对应 smoke：

- `npm run smoke:v1.10-ocr`
- `npm run smoke:v1.10-audio`
- `npm run smoke:v1.10-ppt`
- `npm run smoke:v1.10-mindmap`
- `npm run smoke:v1.10-compare`

未新增 smoke 时，不得声明对应能力 ready。

## 5. 手工验收标准

1. 打开 Notebook 工作区。
2. 进入 Studio 输出列。
3. 确认轻量输出 Notes / Study Guide / Briefing Doc / FAQ 仍可用。
4. 确认 Audio Overview 显示暂不可用。
5. 确认 PPT generation 显示暂不可用。
6. 确认 Mindmap 显示暂不可用。
7. 确认 Document comparison 显示暂不可用。
8. 尝试点击或键盘聚焦 disabled 工具，不应触发后端生成请求。
9. 导入可抽取文本 PDF，确认仍按 P0 PASS_LIMITED 工作。
10. 对扫描 PDF / 图片 PDF，确认状态是 OCR required / unsupported，而不是普通崩溃。

## 6. 完成声明

如果 V1.10 只完成决策和 disabled 验收，最多声明：

ResearchNotebook V1.10 Phase 2/3 and OCR decision gate is complete. OCR, Audio Overview, PPT generation, Mindmap, and Document comparison remain NOT_READY / DISABLED_READY unless separately implemented and smoked.

不得声明：

- OCR ready
- scanned PDF ready
- Audio Overview ready
- PPT generation ready
- Mindmap ready
- Document comparison ready
- all-source-type ready

## 7. 风险评估

| 风险项 | 评级 | 说明 |
| --- | --- | --- |
| 规格漂移 | HIGH | Phase 2/3 容易从决策阶段膨胀为真实实现 |
| 虚假验收 | HIGH | disabled shell 容易被误写成功能 ready |
| UX 误导 | MEDIUM | 用户可能误以为后续工具可用 |

停止条件：

- 任一 disabled 工具发起后端生成请求。
- 文档把 disabled shell 写成 ready。
- 没有 provider / schema / smoke 就实现真实输出。
- 自动 smoke 被写成人工质量验收。

## 8. 当前执行结果

V1.10 disabled-boundary acceptance 已补充自动化入口：

```bash
npm run smoke:v1.10-disabled-boundary
```

该 smoke 验证：

- Studio 后续输出工具仍是 disabled-facing。
- 没有 Phase 2/3 artifact mutation 或 backend route string。
- V1.4 P0 Markdown / TXT / 可抽取文本 PDF 真实数据 smoke 仍为 `PASS_LIMITED`。
- OCR / scanned PDF 仍保持 `CONTRACT_DISCOVERY_READY` / `NOT_READY`。
- V1.9 RC 前置状态仍为 `V1_9_READY_FOR_FINAL_HUMAN_ACCEPTANCE`。
