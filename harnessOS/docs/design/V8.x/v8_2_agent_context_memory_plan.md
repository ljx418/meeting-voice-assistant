# V8-2 Agent Context And Memory Plan

文档状态：V8-2 development and acceptance plan。

目标：

```text
为每个 station Agent 提供 station-scoped context 和 memory。
```

核心合同：

```text
StationAgentContextEnvelope
WorkflowContextRef
ArtifactContextRef
EvidenceContextRef
MemoryContextRef
PromptTemplateRef
RedactionStatus
```

验收：

```text
Agent 只能读取授权 station context。
Agent memory policy 明确 short-term / long-term / disabled。
LLM invocation evidence 记录 provider / model / prompt_template_ref / input_refs / output_refs。
raw secret / raw prompt / raw file content 不进入 evidence。
```

