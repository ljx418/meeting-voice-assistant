# V2.31-V2.36 Gap Analysis：从项目解释到任务级开发导航

## 1. 当前能力

- 已能导入项目、生成 snapshot、inventory、symbols、evidence。
- 已能生成 DevWiki、Code Graph、Quality、文档-代码对齐、架构意图、diagram-code verification、HTML/Mermaid report。
- 已有 Coding Agent actionability、patch plan、runtime evidence、workbench 基线。
- 已有 architecture intent HTTP/MCP/CLI 公共入口。

## 2. 当前 Gap

| Gap | 当前表现 | 风险 | V2.31-V2.36 目标 |
| --- | --- | --- | --- |
| 任务级导航不够精确 | Agent 仍可能重复读很多文件 | token 浪费，改错模块 | 建立 task-aware navigation index |
| 调用/引用关系不可管理 | 当前避免 full call graph，但缺轻量关系层 | 影响分析无法解释 | 建立可证据化 lightweight relationship graph |
| 影响分析不够开发导向 | 报告偏架构审计 | Review/测试建议弱 | 输出 impacted files/symbols/tests |
| Token 节流不够显式 | Context Pack 有裁剪但 ledger 不强 | 保留建议却删 evidence | 输出 token budget ledger 和 omitted reason |
| Copilot 集成不够直接 | 偏报告式 API | 外部 Agent 难以工作流化 | 暴露 task_navigation/impact/test/context APIs |
| 大项目泛化仍需证明 | HarnessOS 关系可能 blocker 较多 | 专用规则或假成功 | accepted 或 structured blocker，禁止硬编码项目特化 |

## 3. 风险

- 将 import dependency 误写成 runtime call。
- 为了大项目看起来完整而伪造 accepted relationship。
- Token 裁剪删掉 evidence 后保留建议。
- HarnessOS 特化，失去泛用性。
- HTML/Mermaid 报告为了可读性新增不存在的事实。

## 4. 应对

- `relationship_type` 与 `semantic_limit` 必填。
- forbidden relationship scanner。
- evidence retention gate。
- data_service + HarnessOS + generic fixture 三类验收。
- public contract parity。
- source artifact immutability hash gate。

## 5. V2.31-V2.36 完成后的剩余非目标

即使本阶段完成，系统仍不声明：

- 完整自动恢复人类设计意图。
- 完整静态调用图。
- 数据流/控制流/类型推断。
- 生产运行时观测。
- 自动修改代码和自动提交 PR。
