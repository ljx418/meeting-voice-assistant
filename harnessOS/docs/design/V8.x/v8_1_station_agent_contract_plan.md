# V8-1 Station Agent Contract Plan

文档状态：V8-1 development and acceptance plan。

目标：

```text
每个 workflow station 都绑定一个独立 StationAgentDescriptor。
```

核心合同：

```text
StationAgentDescriptor
AgentRuntimeProfile
AgentRole
AgentGoal
AgentModelProfile
AgentMemoryPolicy
AgentToolPolicy
AgentSkillBinding
AgentMcpBinding
StationAgentRegistry
```

验收：

```text
station_agent_descriptor_required_for_each_station=PASS
workflow_requires_explainer_agent=PASS
agent_model_profile_per_station=PASS
source_agent_durable_mutation_denied=PASS
```

禁止：

```text
Agent executor ready
source=agent durable mutation
complete Workflow Studio ready
```

