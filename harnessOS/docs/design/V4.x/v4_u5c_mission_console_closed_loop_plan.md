# V4-U5C Mission Console Closed Loop Plan

文档状态：待实现阶段计划。

允许完成声明：

```text
V4-U5C complete: Mission Console closed loop ready for dev/local validation.
```

禁止完成声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

## 1. 目标

Mission Console 必须走通：

```text
用户说目标
 -> IntentCaptured
 -> SpecDrafted
 -> SchemaValidated
 -> DiffReady
 -> AwaitingConfirmation
 -> user_confirmed apply / publish / run
 -> Runtime Report
 -> Evidence Chain
```

状态线必须包含：

```text
IntentCaptured
SpecDrafted
SchemaValidated
DiffReady
AwaitingConfirmation
UserConfirmed
RuntimeStarted 或 transcript_only=true
EvidenceRecorded
```

## 2. 实现范围

```text
Mission Console 使用 ExperienceStateProjection。
Mission Console 显示可用动作和禁止动作原因。
TUI / Command Palette 渲染状态线。
WorkflowSpec / Diff / Blueprint / Runtime Report / Evidence Chain 必须互相可链接。
durable mutation 必须 user_confirmed=true。
source=agent 不能执行 mutation。
```

需要输出的可审计对象：

```text
MissionConsoleTranscript
ExperienceStateProjection snapshot
AvailableAction list
ForbiddenActionReason list
WorkflowSpec link
PatchDiff link
WorkflowBlueprint link
RuntimeReport link
EvidenceChain link
```

## 3. 非目标

```text
不实现 Agent executor。
不实现 production controlled executor。
不实现真实 multi-Agent orchestration。
不实现完整 Web 低代码编辑器。
不把 WorkflowSpec 写成 runtime truth。
```

## 4. 验收

```text
UX-01 至少从 transcript_only 提升为 closed_loop_devlocal 或明确仍为 transcript_only。
状态线来自 ExperienceStateProjection。
apply / publish / run 均包含 user_confirmed=true。
source=agent apply / publish / run 被阻断。
reality-check 不出现 FAIL / BLOCKED。
如果运行依赖 V4.2-C controlled runtime，必须标记 runtime_backed=true。
如果只是 transcript-only，必须标记 transcript_only=true。
Mission Console 不能被描述为 Agent executor。
```

## 5. 停止条件

```text
需要 Agent executor。
需要 production auth。
需要完整 Web Studio。
Spec Drift Risk = HIGH。
False Green Risk = HIGH。
```
