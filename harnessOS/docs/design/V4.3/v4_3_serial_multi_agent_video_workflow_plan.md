# V4.3 Serial Multi-Agent Video Workflow MVP Plan

阶段名称：

```text
V4.3 Serial Multi-Agent Video Workflow MVP / 串行多 Agent 视频工作流 MVP
```

阶段目标：

用真实 dev/local brief fixture 验证一个串行视频创作工作流。工作流包含编剧、分镜、文案、剪辑计划、质量审查、发布准备六个工位。每个工位有 AgentDescriptor、输入输出 artifact contract、可查看文本产物、attempt history、用户确认重跑和下游 stale 状态。

允许声明：

```text
V4.3 complete: serial multi-Agent video workflow MVP ready for dev/local validation.
```

禁止声明：

```text
forbidden complete Workflow Studio ready
forbidden complete AgentTalkWindow ready
forbidden Agent executor ready
forbidden controlled executor ready
forbidden autonomous workflow editing ready
forbidden production-ready external app support
forbidden full multi-Agent orchestration ready
```

## PR Slices

1. V4.3-PR1 Video WorkflowSpec Contract
   - strict serial video WorkflowSpec
   - AgentDescriptor fields for role, goal, model_ref, tool_refs, skill_refs
   - strict validation, no unknown fields, no token/raw payload

2. V4.3-PR2 Deterministic Video Runtime Runner
   - dev/local text artifact runner
   - no model API call
   - no connector credential
   - no real video rendering

3. V4.3-PR3 BFF Controlled Runtime Wrapper
   - `/bff/v4_3/runtime/workflows/serial-video/start`
   - user_confirmed required
   - source=agent rejected
   - rerun and continue-downstream require user confirmation

4. V4.3-PR4 Drawio and HTML Reports
   - workflow drawio
   - status drawio
   - artifact lineage drawio
   - read-only HTML reports

5. V4.3-PR5 Evidence Package
   - TUI transcript
   - workflow YAML and JSON
   - runtime result
   - attempt history
   - downstream stale
   - operation evidence
   - result summary

## Real Data Fixture

```text
tests/fixtures/v4_3/video_brief/launch_brief.md
```

The fixture describes a HarnessOS Headless-first launch video brief and is the required data source for V4.3 focused validation.

## Risk Controls

1. Agent remains a descriptor, not an executor.
2. Runtime is deterministic and dev/local.
3. No external model, connector, rendering, or publishing call.
4. Durable actions require `user_confirmed=true`.
5. `source=agent` cannot start, rerun, or continue.
6. Drawio and HTML reports are read-only.
7. Evidence package must be redacted.
8. Completion notes must include Spec Drift Evaluation and False Green Evaluation.

