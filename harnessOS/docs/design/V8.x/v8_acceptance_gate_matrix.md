# V8 Acceptance Gate Matrix

文档状态：V8 acceptance control matrix，当前 V8-9 final framework PASS。

| Stage | Entry Gate | Acceptance Gate | Stop Condition |
| --- | --- | --- | --- |
| V8-0 | V7 final acceptance accepted with bounded baseline | V8 PRD, architecture, gap, drawio, plan and claim guard accepted | V8-0 claims implementation complete |
| V8-1 | V8-0 accepted and `v8_schema_contract_pack.md` accepted | StationAgentDescriptor and registry contract accepted | Station can run without AgentDescriptor |
| V8-2 | V8-1 accepted and runtime I/O contract accepted | Station-scoped context and memory refs accepted | raw prompt / secret / file content leaks into evidence |
| V8-3 | V8-2 accepted and Skill/MCP/Tool contract accepted | Skill / MCP / Tool allowlist and denied cases accepted | Agent bypasses capability resolver |
| V8-4 | V8-1..V8-3 evidence exists and evidence contract accepted | Local document workflow runs with per-station Agent evidence | station outputs are claimed Agent-backed without Agent invocation evidence |
| V8-5 | V8-4 accepted | Terminal worker design gate accepted | Codex / Claude / ChromeCLI is described as unrestricted executor |
| V8-6 | V8-5 accepted and human high-risk decision recorded | controlled terminal worker pilot produces transcript and diff evidence | terminal worker mutates without handoff |
| V8-7 | V8-6 evidence exists and separate high-risk decision is recorded | bounded multi-Agent project workflow evidence exists | full multi-Agent orchestration is claimed |
| V8-8 | V8-4 / V8-6 evidence exists | TUI renders Agent identity, capability, state, terminal handoff and evidence | TUI constructs runtime truth |
| V8-9 | V8-0..V8-8 evidence exists and V8-7 bounded runtime evidence is PASS | final dashboard, claim scan, redaction scan and drawio XML pass | final claim is upgraded beyond bounded ready-for-review scope |

## Global Acceptance Requirements

```text
No Agent executor ready claim.
No autonomous coding workflow ready claim.
No full multi-Agent orchestration ready claim.
No source=agent durable mutation.
No raw secret / raw prompt / raw artifact content leakage.
No terminal worker outside workspace scope.
No ChromeCLI production automation claim.
```

## P0 Contract Gate

```text
v8_schema_contract_pack.md must define StationAgentDescriptor and registry contracts.
v8_station_agent_runtime_io_contract.md must define context envelope, run request and run result.
v8_skill_mcp_tool_contract.md must define CapabilityResolver and allowlist rules.
v8_terminal_worker_high_risk_contract.md must define Codex / Claude / ChromeCLI high-risk boundaries.
v8_agent_explainability_tui_contract.md must define required TUI panels and read-only boundaries.
v8_evidence_package_contract.md must define V8 stage and final acceptance evidence.
```
