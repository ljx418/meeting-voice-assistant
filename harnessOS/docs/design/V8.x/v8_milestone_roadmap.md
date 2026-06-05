# V8 Milestone Roadmap

文档状态：V8 milestone roadmap，当前 V8-9 final framework PASS。

## 1. Milestone Table

| Milestone | Stage | Purpose | Evidence Scope | Exit Claim |
| --- | --- | --- | --- | --- |
| M0 | V8-0 | Station Agent planning gate | planning_gate | V8-0 complete: station-agent workflow planning gate ready for review. |
| M1 | V8-1 | Station Agent contracts | contract | V8-1 complete: station agent contract baseline ready for review. |
| M2 | V8-2 | Context and memory | contract / fixture | V8-2 complete: station agent context and memory contract ready for review. |
| M3 | V8-3 | Skill / MCP / Tool binding | contract / fixture | V8-3 complete: station agent skill and MCP capability binding baseline ready for review. |
| M4 | V8-4 | Local document station-agent runtime | real_runtime_fixture | V8-4 complete: station-agent local document workflow pilot ready for review. |
| M5 | V8-5 | Terminal worker design gate | high_risk_design | V8-5 complete: terminal worker design gate ready for review. |
| M6 | V8-6 | Controlled terminal worker pilot | controlled_runtime_fixture | V8-6 complete: controlled terminal worker pilot ready for review. |
| M7 | V8-7 | Multi-Agent project workflow pilot | bounded_runtime_fixture | V8-7 complete: multi-agent project workflow pilot ready for review. |
| M8 | V8-8 | Agent explainability TUI | read_model_from_v8_4_v8_6_evidence | V8-8 complete: agent explainability TUI baseline ready for review. |
| M9 | V8-9 | Final acceptance | final_acceptance_framework / PASS | V8 complete: station-agent workflow pilot ready for review. |

## 2. Priority Recommendation

```text
First: V8-1 to V8-4, prove every station has an Agent.
Second: V8-5 to V8-6, add Codex / Claude terminal worker under governance.
Third: V8-8, improve TUI explainability from V8-4 / V8-6 evidence.
Fourth: V8-7 has bounded runtime evidence after separate human decision.
Fifth: V8-9 final framework can issue only the bounded ready-for-review claim.
```

## 3. Exit Criteria

V8 final exit requires:

```text
Every workflow station has StationAgentDescriptor.
Every Agent has role / goal / model / memory / skills / MCP / tools.
At least one WorkflowExplainerAgent exists.
Agent context injection evidence exists.
Agent LLM invocation evidence exists.
Skill / MCP / Tool allowlist evidence exists.
source=agent durable mutation denied evidence exists.
Terminal worker evidence exists if V8-6 is enabled.
TUI shows Agent identity, capability, state and evidence.
No False Green scan PASS.
Redaction scan PASS.
Drawio XML valid.
```

## 4. Remaining Blockers

```text
No V8 final blocker remains for the bounded station-agent workflow pilot claim.
Remaining out-of-scope capabilities must move to a later stage: unrestricted Agent executor, autonomous coding workflow, full multi-Agent orchestration and production terminal automation.
```

## 5. Documentation Readiness

```text
V8-0 through V8-8 have evidence or completion notes.
V8-8 read-model TUI evidence exists.
V8-7 bounded runtime evidence exists.
V8-9 final framework exists and final bounded claim is allowed.
```
