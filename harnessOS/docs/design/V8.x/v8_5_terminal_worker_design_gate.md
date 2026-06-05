# V8-5 Terminal Worker Design Gate

文档状态：V8-5 high-risk design gate / completed for review。

目标：

```text
为 Codex / Claude / ChromeCLI 接入定义高风险边界。
```

设计对象：

```text
CodexCliWorkerDescriptor
ClaudeCliWorkerDescriptor
ChromeCliSessionConnectorDescriptor
TerminalSessionPolicy
WorkspaceScopeGuard
CommandAllowlist
TranscriptCapture
DiffCapture
HumanReviewHandoff
KillSwitch
TimeoutPolicy
```

优先级：

```text
1. Codex CLI Worker
2. Claude CLI Worker
3. ChromeCLI WebChat Worker
```

禁止：

```text
自动 commit / push / publish
自动操作生产账号
绕过 workspace scope
绕过 human review handoff
把 ChromeCLI 写成 production automation ready
```

当前决定：

```text
terminal_worker_runtime_enabled=false
controlled_terminal_worker_pilot_allowed=false
human_high_risk_proceed_decision_required=true
V8-6 implementation remains NO-GO
```
