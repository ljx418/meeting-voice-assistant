# V3.5 Embed Contract / AgentTalkWindow Preparation Plan

文档状态：V3.5-H planning artifact。

## 1. Goal

定义未来 AgentTalkWindow 所需的 embed contract。本阶段只做 contract 和最小 demo 规划，不实现完整 AgentTalkWindow。

## 2. EmbedDefinition

字段：

- `embed_id`
- `app_id`
- `project_id`
- `workspace_id`
- `session_id`
- `capability_token`
- `eventsource_url`
- `allowed_event_channels`
- `artifact_preview_policy`
- `approval_policy`
- `theme`
- `metadata`

## 3. Event Union

必须支持：

- chat events
- job events
- artifact events
- approval events
- trace events
- business events

## 4. UI States

Embed consumer 必须能区分：

- `idle`
- `connecting`
- `streaming`
- `approval_required`
- `blocked`
- `failed`
- `completed`
- `reconnecting`

## 5. Minimal Demo

最小 demo 只展示：

- bootstrap session
- start turn
- subscribe events
- show job progress
- show artifact metadata
- respond approval

## 6. Acceptance

- contract 不引用 Gateway 内部对象。
- contract 可由 SDK/BFF/Event Bridge 组合实现。
- business event namespace 由 pack/template 显式声明。

