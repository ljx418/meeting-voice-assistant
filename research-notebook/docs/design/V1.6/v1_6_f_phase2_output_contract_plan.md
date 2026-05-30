# ResearchNotebook V1.6-F Phase 2/3 Output Contract Discovery Plan

日期：2026-05-28

## 阶段目标

为 PRD Phase 2/3 输出能力建立 disabled shell 和合同发现边界：

- Audio Overview
- PPT 生成
- 思维导图
- 文档对比

本阶段不生成真实输出，不调用后端，不声明 ready。

## 范围

- Studio UI 展示 Phase 2/3 输出能力为 disabled。
- 每个工具显示：
  - contract required
  - 当前不可用
  - 后续需要独立 provider / schema / smoke
- 文档记录每个工具的后续合同要求。

## 禁止

- 不生成假音频。
- 不生成假 PPT。
- 不生成假思维导图。
- 不生成假文档对比。
- 不把 Markdown 文本伪装成 PPT / Mindmap。
- 不声明 Phase 2/3 ready。

## 验收

- Studio 中能看到 Phase 2/3 输出工具。
- 工具按钮为 disabled 或不可执行。
- UI 文案明确“合同未就绪 / 暂不可用”。
- 点击或键盘操作不会发起后端请求。
- npm run check PASS。

## 风险评估

开发计划漂移风险：LOW。

虚假验收风险：LOW。

原因：本阶段只做 disabled shell，不做生成能力。
