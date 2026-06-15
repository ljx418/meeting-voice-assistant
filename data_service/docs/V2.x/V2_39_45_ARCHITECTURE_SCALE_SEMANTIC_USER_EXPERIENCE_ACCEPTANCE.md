# V2.39-V2.45 User Experience Acceptance

## 1. 目标体验

V2.39-V2.45 完成后，用户应能把本项目用于大型项目的模块辅助阅读、架构设计看护、调用/依赖链路管理和 Agent 低 token 成本上下文生成。

用户看到的不应只是文件树或简单枚举图，而应是：

- 项目规模和扫描预算。
- 目标架构与当前实现差异。
- workflow/runtime candidates。
- capability 到代码实现和测试的证据链。
- 文档图与代码事实的对齐状态。
- Agent 任务阅读路径和 token 预算。
- profile/taxonomy 与真实项目回归状态。

## 2. 用户场景

### 场景 A：新人快速读大型项目

用户导入 HarnessOS 或类似大型项目后，应看到规模概览、目标/当前/差异图、入口和 workflow candidates。每个重要节点必须能追踪 evidence 或 blocker。

### 场景 B：Coding Agent 修复任务

用户输入任务和 max_tokens 后，应得到相关 capability、entrypoint、handler、dependency、test、设计约束、recommended reading order、omitted_items 和 token estimate。

### 场景 C：架构审计

用户运行 document semantic parser 和 verification 后，应看到 drawio page/lane/group/edge claims、Markdown acceptance/non-goal/stop condition claims，以及 supported、weak、unsupported、contradicted、needs_review。

### 场景 D：持续项目治理

用户配置 project profile / taxonomy 后，应能把 data_service、HarnessOS、codexPat 加入回归矩阵，并看到 accepted、blocker、provider_unavailable 和 no-hardcode audit 结果。

## 3. 最终用户验收门槛

- 报告可读，有结构化图表。
- Agent context 可用于减少重复代码阅读。
- 架构声明和代码事实分离清楚。
- 低置信推断可见，不被包装为确定事实。
- 每个 accepted 用户可见结论都有 evidence。
