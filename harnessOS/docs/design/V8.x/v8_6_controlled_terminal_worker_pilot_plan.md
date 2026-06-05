# V8-6 Controlled Terminal Worker Pilot Plan

文档状态：V8-6 high-risk pilot plan / completed for review。

目标：

```text
在人工高风险确认后，让 Coding Station Agent 通过 Codex / Claude CLI 生成 patch proposal。
```

边界：

```text
Terminal worker 只生成 proposal / diff / transcript。
apply / commit / push 需要人类确认或受控执行器。
source=agent 不能直接 durable mutation。
```

验收：

```text
workspace scope guard 生效。
command allowlist 生效。
terminal transcript captured。
diff captured。
human review handoff exists。
kill switch / timeout policy exists。
```

当前验收结果：

```text
status=PASS
evidence_scope=controlled_runtime_fixture
worker_type=codex_cli
workspace_scope_guard=PASS
command_allowlist=PASS
terminal transcript captured=PASS
diff proposal captured=PASS
human review handoff exists=PASS
source_agent_mutation_denied=PASS
auto_commit_enabled=false
auto_push_enabled=false
production_browser_automation_enabled=false
evidence_dir=docs/design/V8.x/evidence/v8-6-controlled-terminal-worker/
```

注意：

```text
V8-6 不证明 Agent executor ready。
V8-6 不证明 Codex / Claude 生产级终端执行器 ready。
V8-6 不证明完整多 Agent 项目开发工作流 ready。
```
