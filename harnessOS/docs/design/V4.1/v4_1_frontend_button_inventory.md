# V4.1 Frontend Button Inventory

Status: implementation audit inventory for the Stitch-aligned V4.1 frontend rebuild.

This inventory is scoped to the V4.1 local recursive Markdown summary workflow. It is not a generic controlled executor contract and does not grant Agent mutation authority.

## 1. Button-Level MVP Inventory

| Control | Primary screen | Expected behavior | Confirmation required | Agent allowed |
| --- | --- | --- | --- | --- |
| `发送需求` | `V4.1-01-Agent-Create-Draft` | Send natural-language request to proposal flow | No | Yes, as user message input only |
| `查看 Diff` | `V4.1-02-Agent-Draft-Proposal` | Open patch diff review | No | Handoff / navigate only |
| `应用到草稿` | `V4.1-03-Patch-Diff-Review` | Start apply confirmation flow | Yes | No |
| `确认应用` | `V4.1-04-Apply-Confirmation` | Apply patch with `user_confirmed=true` and non-agent source | Yes | No |
| `选择文件夹输入节点` | `V4.1-05-Draft-Applied-Canvas` | Select node and open Inspector | No | Navigate only |
| `授权读取` | `V4.1-07-Folder-Authorization` | Authorize scoped dev/local folder read | Yes | No |
| `调试扫描` | `V4.1-08-Debug-Scan-Result` | Return tree and counts without summaries | Yes | No |
| `发布版本` | `V4.1-09-Publish-Version-Confirm` | Start publish confirmation flow | Yes | No |
| `确认发布` | `V4.1-09-Publish-Version-Confirm` | Publish version with user confirmation | Yes | No |
| `运行工作流` | `V4.1-10-Run-Workflow-Confirm` | Start run confirmation flow | Yes | No |
| `确认运行` | `V4.1-10-Run-Workflow-Confirm` | Create workflow instance with user confirmation | Yes | No |
| `查看运行看板` | `V4.1-11-Run-Board-In-Progress` | Open bottom run panel | No | Navigate only |
| `查看产物` | `V4.1-12-Run-Completed-Artifacts` | Open artifact viewer | No | Navigate only |
| `查看质量报告` | `V4.1-13-Quality-Report` | Open quality report | No | Navigate only |
| `刷新恢复` | `V4.1-14-Refresh-Recovery` | Re-fetch BFF truth after page refresh | No | No direct mutation |
| `重跑当前节点` | `V4.1-15-Failure-And-Rerun` | Start rerun confirmation flow for scoped failed node | Yes | No |
| `确认重跑` | `V4.1-15-Failure-And-Rerun` | Create new attempt while preserving old attempt | Yes | No |
| `Agent 解释` | `V4.1-16-Agent-Debug-Fix-Proposal` | Read-only explanation | No | Yes |
| `Agent 生成修复 Proposal` | `V4.1-16-Agent-Debug-Fix-Proposal` | Create patch proposal only | No durable mutation | Yes, propose only |
| `查看治理证据` | `V4.1-17-Governance-Evidence-ReadOnly` | Open read-only evidence chain | No | Navigate only |

## 2. Required Disabled Or Guarded States

1. `应用到草稿` disabled when selected patch is stale, blocked, rejected, or requires approval without the proper user path.
2. `授权读取` disabled when folder path is empty, root-like, or outside dev/local allowlist.
3. `调试扫描` disabled before folder authorization.
4. `发布版本` disabled before draft has applied workflow nodes.
5. `运行工作流` disabled before publish.
6. `确认运行` disabled when required folder authorization is missing.
7. `重跑当前节点` visible only for failed scoped V4.1 local Markdown parse/run node.
8. Governance evidence panel must not show Apply, Publish, Approve, Reject, Execute, or Run controls.

## 3. Network And Truth Boundaries

Browser allowed:

```text
/bff/*
static assets
```

Browser forbidden:

```text
/v1/rpc
/v1/events/subscribe
direct filesystem read
direct WorkflowStore write
```

Agent allowed:

```text
propose
explain
handoff
navigate
```

Agent forbidden:

```text
apply
publish
run
rerun
approval.respond
context.update
business.event.emit
```

## 4. No False Green Copy Guard

The V4.1 frontend must not show:

```text
自动应用
自动发布
Agent 已执行
Agent 已发布
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
```
