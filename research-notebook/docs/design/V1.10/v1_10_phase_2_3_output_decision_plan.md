# ResearchNotebook V1.10 Phase 2/3 Output Decision Plan

日期：2026-05-31

## 目标

对 PRD Phase 2/3 输出能力做 V1.x 最终决策：

- Audio Overview
- PPT generation
- Mindmap
- Document comparison

本计划默认建议继续 disabled，不在 V1.10 直接实现真实输出。

## 决策原则

1. Disabled shell 不等于 ready。
2. 单项实现不代表 Phase 2/3 全部 ready。
3. 没有 provider、schema、真实 smoke 和人工质量验收，不进入实现。
4. 不生成伪音频、伪 PPT、伪思维导图或伪文档对比。
5. 不把 Markdown / JSON 导出伪装成 PPT / Mindmap。

## 单项实现前置条件

任一能力从 disabled 升级到真实实现前，必须具备：

- 后端 route contract。
- request / response schema。
- artifact schema。
- provider 或 deterministic generator。
- UI preview。
- export / download contract。
- citation metadata 保留策略。
- 真实数据 smoke。
- 人工质量验收。

## 默认验收

当前 V1.10 默认验收为 disabled boundary：

- Studio 中能看到后续输出工具。
- 每个工具显示“暂不可用”或“合同未就绪”。
- button disabled。
- 点击或键盘操作不会发起生成请求。
- 不生成 artifact。
- 文档保持 `DISABLED_READY` / `NOT_READY`。
- `npm run check` PASS。

## 当前决策

V1.10 当前决策建议：

| 能力 | 当前状态 | V1.10 决策 |
| --- | --- | --- |
| Audio Overview | DISABLED_READY | 继续 disabled |
| PPT generation | DISABLED_READY | 继续 disabled |
| Mindmap | DISABLED_READY | 继续 disabled |
| Document comparison | DISABLED_READY | 继续 disabled |

## 风险评估

| 风险项 | 评级 | 收敛措施 |
| --- | --- | --- |
| 规格漂移 | HIGH | 不进入真实实现，除非单项合同先通过 |
| 虚假验收 | HIGH | 文档保持 disabled / NOT_READY，不写 ready |
| 用户误导 | MEDIUM | UI 明确“暂不可用 / 后续能力” |
