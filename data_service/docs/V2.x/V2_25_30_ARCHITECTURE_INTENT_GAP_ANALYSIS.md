# V2.25-V2.30 Gap Analysis

## 1. 当前能力与目标能力差异

| 维度 | 当前能力 | 目标能力 | Gap |
| --- | --- | --- | --- |
| 架构图解析 | 可登记 drawio / 文档 claim，粒度有限。 | 抽取 diagram cell、node、edge、relation、authority。 | 需要统一 source model 和 diagram parser。 |
| 代码事实 | 已有 surface、symbol、relationship、public evidence。 | 形成 proof graph，加入 config/test/runtime/human_confirmed。 | 需要 proof node/edge schema。 |
| 设计意图 | 只能输出报告和弱推断。 | intent candidate 有 evidence/counter evidence/confidence。 | 需要意图推断引擎和审计规则。 |
| 反推验证 | 文档-代码 alignment 已存在。 | diagram node/edge 可反推代码落地状态。 | 需要 diagram-to-code verification。 |
| 用户体验 | 报告已有，但 target/current/inferred/confirmed/diff 不够清晰。 | 用户可看到五区块架构理解视图。 | 需要新 HTML 与 Context Pack。 |
| 治理闭环 | 已有 feedback/rule/overlay。 | 支持 architecture intent confirmation/revoke。 | 需要 target resolver 和 hash gate。 |

## 2. 技术风险

| 风险 | 等级 | 应对 |
| --- | --- | --- |
| 把推断当事实 | Fatal | intent candidate 与 accepted fact 分离。 |
| token-only 假匹配 | Major | token_overlap_only 永远 weak_match。 |
| HarnessOS 动态工作流难以定位 | Major | structured blocker 与 human review queue。 |
| 报告图形引入新事实 | Major | report JSON -> HTML/Mermaid 一致性测试。 |
| 运行时证据越界 | Major | runtime descriptor 默认 unavailable，非只读采集需人工批准。 |
| 文档历史版本混淆 | Major | authority_role、supersedes、stale policy。 |

## 3. 不解决的 Gap

- 不做完整调用图。
- 不做数据流/控制流。
- 不做自动架构重构。
- 不做没有人工确认的自动文档改写。
- 不承诺对任意项目都能产生 accepted runtime evidence。
