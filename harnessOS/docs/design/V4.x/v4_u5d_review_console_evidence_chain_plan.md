# V4-U5D Review Console And Evidence Chain Plan

文档状态：待实现阶段计划。

允许完成声明：

```text
V4-U5D complete: Review Console and Evidence Chain baseline ready for review.
```

## 1. 目标

Review Console 统一失败解释、修复 proposal、用户确认 handoff 和局部重跑入口。Evidence Chain 统一只读审计视图。

## 2. 实现范围

```text
Review Console 使用 ExperienceStateProjection。
ReviewActionDTO 包含 operation、source、actor_type、requires_user_confirmation、policy_decision、risk_flags、target_refs。
EvidenceReportDTO 只允许 view / export / open_handoff。
Evidence Chain 展示 proposal、handoff、user_confirmed、runtime_result_ref、policy_decision、correlation_id、redaction_status。
failure explanation 和 repair proposal 不直接执行。
rerun 必须 user_confirmed=true。
source=agent 不能 rerun。
```

ReviewActionDTO 必须至少包含：

```text
operation
source
actor_type
requires_user_confirmation
policy_decision
risk_flags
target_refs
```

EvidenceReportDTO 只允许：

```text
view
export
open_handoff
```

## 3. 非目标

```text
不新增 Agent executor。
不新增 production controlled executor。
不把 Evidence Chain 变成操作面板。
不让 Agent 自动修复、自动重跑、自动发布。
```

## 4. 验收

```text
Evidence Chain 不出现 Apply / Publish / Approve / Reject / Execute / Run 按钮。
Evidence Chain 不出现 自动应用 / 自动发布 / Agent 已执行。
Review Console 只能发起 handoff。
old attempt、新 attempt、downstream stale 可审计。
Evidence 与 Runtime Report 能互相引用。
No token/raw payload leakage。
```

## 5. 停止条件

```text
Evidence Chain 出现执行按钮。
source=agent 可以执行 mutation。
Review Console 绕过 user_confirmed。
Spec Drift Risk = HIGH。
False Green Risk = HIGH。
```
