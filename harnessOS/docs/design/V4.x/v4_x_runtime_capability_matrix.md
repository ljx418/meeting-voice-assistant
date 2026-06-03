# V4.x Runtime Capability Matrix

文档状态：V4-U5A/U6 审计输入。本文是能力边界 read model，不声明 runtime ready。

## Baseline

```text
V4.6 complete: governed Agent workflow builder UX ready for dev/local validation.
```

仍禁止声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

## Capability Rules

`runtime_capability_matrix.schema.json` 必须记录每项能力的：

```text
capability_id
target_type
status: supported / partial / planned / unsupported
evidence_ref
stage_owner
runtime_backed
deterministic_only
false_green_risk
agent_executable
requires_user_confirmation
```

## Required Boundary Entries

| capability_id | status | stage_owner | runtime_backed | deterministic_only | agent_executable | requires_user_confirmation | false_green_risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| local_markdown_summary_workflow | supported | V4.1 | true | false | false | true | LOW |
| real_llm_local_technical_document_workflow | supported | V4-U5E | true | false | false | true | LOW |
| mission_console_spec_draft | partial | V4.6/U5C | false | false | true | false | MEDIUM |
| workflow_blueprint_drawio | supported | V4.2-A | false | true | false | false | LOW |
| html_runtime_report | partial | V4.2-A/V4.2-C | true | true | false | false | MEDIUM |
| local_station_rerun_slice | partial | V4.1-C/V4.2-C | true | true | false | true | MEDIUM |
| serial_video_workflow_devlocal | partial | V4.3 | true | true | false | true | MEDIUM |
| parallel_deliberation_devlocal | partial | V4.4 | true | true | false | true | MEDIUM |
| long_running_engineering_devlocal | partial | V4.5 | true | true | false | true | MEDIUM |
| serial_video_provider_backed_devlocal | supported | V4-U7 | true | false | false | true | MEDIUM |
| parallel_deliberation_provider_backed_devlocal | supported | V4-U7 | true | false | false | true | MEDIUM |
| engineering_workflow_provider_backed_devlocal | supported | V4-U7 | true | false | false | true | MEDIUM |
| v4_closure_manual_acceptance_package | supported | V4-U8 | false | false | false | false | LOW |
| v4_final_human_acceptance_and_v5_handoff | supported | V4-U9 | false | false | false | false | LOW |
| agent_workflow_builder_governed | partial | V4.6 | false | true | true | false | MEDIUM |
| agent_executor | unsupported | Future | false | false | false | true | HIGH |
| controlled_executor_production | unsupported | Future | false | false | false | true | HIGH |
| production_external_app_support | unsupported | Future | false | false | false | true | HIGH |
| full_multi_agent_orchestration | unsupported | Future | false | false | false | true | HIGH |

## No False Green

V4.3/V4.4/V4.5 deterministic dev/local evidence 仍作为历史证据保留；V4-U7 provider-backed dev/local evidence 只能证明场景切片，不得写成 full multi-Agent orchestration。V4.2-C controlled runtime MVP 不得写成 controlled executor ready。V4.6 Agent Workflow Builder UX 不得写成 Agent executor ready。
