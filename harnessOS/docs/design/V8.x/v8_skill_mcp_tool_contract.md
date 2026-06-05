# V8 Skill / MCP / Tool Contract

文档状态：V8-0 P0 capability contract / implementation-readiness input。

## 1. Capability Model

V8 Agent 能力分三类：

```text
Skill: instruction / task method capability.
MCP: external server/resource/tool capability.
Tool: local runtime or connector action capability.
```

它们都不能绕过：

```text
CapabilityResolver
PolicyDecision
CredentialBoundary
UserConfirmation
EvidenceRecorder
```

## 2. CapabilityResolver Input

Required fields:

```text
agent_id
station_id
operation
capability_type: skill | mcp | tool | terminal_worker
capability_id
target_refs
source
actor_type
user_confirmed
human_authorization_ref
context_envelope_ref
correlation_id
request_id
```

## 3. CapabilityResolver Output

Required fields:

```text
decision_id
allowed
risk_level: low | medium | high | critical
requires_user_confirmation
requires_handoff
requires_approval_gate
requires_credential_decision
forbidden_reason
policy_decision_ref
evidence_required
created_at
```

## 4. Skill Binding Rules

```text
Skill can shape reasoning and output format.
Skill cannot grant runtime permission.
Skill cannot access artifacts except through context refs.
Skill invocation must be recorded if it materially changes output.
```

## 5. MCP Binding Rules

```text
MCP server must be allowlisted per Agent.
MCP tool must be allowlisted per Agent.
MCP resource scope must be explicit.
MCP call must produce evidence.
MCP output must be redacted before entering Evidence Chain.
```

## 6. Tool Binding Rules

```text
Read-only tools can be allowed with scoped refs.
Write/mutation tools require user_confirmed=true.
source=agent cannot directly execute durable mutation.
High-risk tools require handoff and approval gate.
```

## 7. Denied Operations

Default denied unless later stage separately approves:

```text
unrestricted connector.call
unrestricted external_llm.call
business.event.emit
context.update
workflow.template.publish
approval.respond
git commit
git push
production deploy
browser production account automation
```

