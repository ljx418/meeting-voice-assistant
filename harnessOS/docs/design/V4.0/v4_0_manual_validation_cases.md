# V4.0 Manual Validation Cases

Status: manual validation checklist for human review after V4.0 final audit package.

Allowed V4.0 claim:

```text
V4.0 complete: governed dev/local Workflow Console and production readiness design gates ready for implementation review.
```

Do not validate V4.0 as production-ready, executor-ready, enterprise-auth-ready, or complete Workflow Studio.

## MV-01: Open Dev/Local Workflow Console

Goal: confirm the console opens against the local BFF and does not silently fall back to demo data.

Steps:

1. Start the local BFF and Workflow Console preview.
2. Open the Workflow Console in a browser.
3. Confirm board, instance status, stations, artifacts, quality, approval, and context are visible.
4. Inspect browser network requests.

Expected:

Forbidden claims / No False Green: the following claims are explicitly forbidden and must not be treated as completed capabilities.

- UI loads from the BFF.
- No silent demo fallback is used unless explicitly configured.
- No browser request is sent to `/v1/rpc`.
- No browser request is sent to `/v1/events/subscribe`.
- No capability token, subscription token, Authorization value, Bearer value, secret, raw payload, raw prompt, or signed URL appears in the DOM.

## MV-02: Board And Status Refresh

Goal: confirm board/status are BFF truth, not event payload truth.

Steps:

1. Open the board/status area.
2. Trigger a refresh from the UI.
3. If a test event injection tool is available, send a fake event payload with a forged station or revision.
4. Observe the UI after refresh.

Expected:

- Board/status refresh from BFF DTOs.
- Fake event payload does not directly create station, edge, context, patch, evidence, or status truth.
- EventBridge only triggers refresh.

## MV-03: Canvas Node Proposal

Goal: confirm node drag/click creates proposal only.

Steps:

1. Open `节点库`.
2. Drag or click a node template onto the canvas.
3. Observe the ghost node and pending state.
4. Check draft revision and board/status before apply.

Expected:

- A ghost or pending proposal is visible.
- PatchDiffDTO appears.
- Draft revision remains unchanged before apply.
- Board/status remain unchanged before apply.
- No direct Station creation occurs.

## MV-04: Canvas Edge Proposal

Goal: confirm edge creation uses governed `update_edge` proposal path.

Steps:

1. Try creating a self-loop edge.
2. Try creating an edge to a missing station.
3. Try creating a duplicate edge.
4. Try creating a valid edge.

Expected:

- Invalid edges are rejected with stable validation errors.
- Valid edge creates a proposal.
- Edge drag does not write WorkflowEdge directly.
- No new direct `add_edge` route is used.

## MV-05: Inspector Mapping

Goal: confirm Inspector typing is local-only until Generate Patch.

Steps:

1. Open Inspector for a station.
2. Type into prompt, connector, artifact contract, quality rule, or approval fields.
3. Watch network requests while typing.
4. Click `生成 Patch`.

Expected:

- Typing does not send network requests.
- Generate Patch sends exactly one proposal request.
- Proposal payload excludes layout fields.
- Proposal payload excludes token, Authorization, secret, raw trace, raw artifact, raw connector, and raw prompt fields.
- PatchDiffDTO is shown after proposal.

## MV-06: User-Confirmed Editing Panel

Goal: confirm apply/reject/publish require explicit user confirmation.

Steps:

1. Select a pending patch.
2. Review PatchDiffDTO.
3. Click apply only through the Editing Panel confirmation control.
4. Repeat for reject.
5. Publish only through the governed user-confirmed path.

Expected:

- `user_confirmed=true` is required.
- `source=editing_panel` is used for apply/reject/publish.
- Apply/reject/publish refresh patch queue, patch diff, draft/template/version, board/status, and canvas projection from BFF truth.
- Stale patch cannot be applied.
- High-risk patch cannot direct apply.

## MV-07: AgentTalk Explain And Summarize

Goal: confirm explain and summarize are read-only.

Steps:

1. Open Agent assistant.
2. Ask it to explain the workflow.
3. Ask it to summarize events, context, or quality.
4. Inspect network requests and UI state.

Expected:

- Explain/summarize do not create patch proposals.
- Explain/summarize do not create handoffs.
- Explain/summarize do not call mutation routes.
- No apply, publish, approve, context update, business event emit, start, rerun, connector call, or external LLM call is executed by Agent.

## MV-08: Agent Suggest Patch And Handoff

Goal: confirm Agent suggestion enters proposal flow and handoff only opens panels.

Steps:

1. Ask Agent assistant to suggest a workflow improvement.
2. Select the suggestion.
3. Open the handoff target panel.
4. Do not confirm any panel action.

Expected:

- Agent suggest patch creates proposal only.
- Handoff opens Editing, Approval, or Context panel only.
- Opening a panel does not execute mutation.
- `source=agent` cannot apply, publish, approval.respond, context.update, business.event.emit, start workflow, or rerun station.

## MV-09: Evidence Review Read-Only

Goal: confirm governance evidence review is read-only.

Steps:

1. Open governance review or operation evidence panel.
2. Review evidence chain.
3. Inspect available buttons/actions.

Expected:

- Evidence chain is visible.
- No Apply, Publish, Approve, Reject, Execute, or Run action appears in evidence review.
- No executor route is invoked.

## MV-10: Patch Queue Stale Guard

Goal: confirm selected stale patches are not silently usable.

Steps:

1. Create multiple patch proposals.
2. Select one patch.
3. Change draft revision through a valid user-confirmed apply path or refresh fixture.
4. Observe selected patch state.

Expected:

- Selected stale patch shows stale state.
- Apply is disabled for stale patch.
- Apply/reject/publish refreshes queue state.
- Selected patch is refreshed or cleared after apply/reject/publish.

## MV-11: Catalog Version Guard

Goal: confirm frontend node library uses BFF controlled catalog.

Steps:

1. Open node library.
2. Attempt proposal with current catalog version.
3. Attempt proposal using an intentionally stale catalog version if a test control exists.
4. Attempt unknown node or unsupported connector/skill if a test control exists.

Expected:

- Current catalog renders node library.
- Catalog version mismatch blocks proposal.
- Unknown node returns stable error.
- Unsupported connector or skill returns stable error.
- Frontend does not define runtime semantics independently.

## MV-12: Redaction

Goal: confirm sensitive fields never leak through DTO, DOM, error, audit, or event surfaces.

Steps:

1. Inspect browser DOM.
2. Inspect network responses.
3. Inspect visible error messages.
4. Inspect evidence and audit summary panels.

Expected:

The following never appear:

- capability_token
- subscription_token
- Authorization
- Bearer
- secret
- raw_trace_payload
- raw_artifact_content
- raw_connector_payload
- raw prompt
- upstream signed URL

## MV-13: Forbidden Copy

Goal: confirm no false-green UI copy is present.

Steps:

1. Search visible UI and documentation surfaces used in the demo.
2. Inspect Agent assistant copy, editing panel copy, production readiness copy, and completion notes.

Expected:

Forbidden claims / No False Green: the following claims are explicitly forbidden and must not appear as completed capabilities:

- production-ready external app support
- enterprise auth ready
- multi-tenant control plane ready
- OAuth ready
- SSO ready
- controlled executor ready
- Agent executor ready
- autonomous workflow editing ready
- complete Workflow Studio ready
- complete AgentTalkWindow ready
- full low-code canvas editing ready

禁止误导文案：the following misleading copy must not appear in the UI or completion surfaces.

- 自动应用
- 自动发布
- 已帮你修改并发布
- Agent 已执行
- Agent 已发布
- 生产认证已完成
- 企业级认证已完成
- 多租户控制台已完成
- 生产接入已完成
- production ready

## MV-14: Production Design Gate Boundary

Goal: confirm production readiness work is still design-gate or future implementation work.

Steps:

1. Review V4.0 R/S/T/U/V/W/X/Y/Z design contracts and completion notes.
2. Confirm no production auth, OAuth, SSO, tenant admin, token rotate/revoke, audit export, controlled executor, or Agent executor route has been added.

Expected:

- V4.0 only proves governed dev/local Workflow Console and production readiness design gates.
- Production auth, tenant control plane, token lifecycle runtime, secret manager, observability platform, audit export, external app onboarding, and executor implementation remain future work.

## MV-15: Image Guide Asset Verification

Goal: confirm local usage guide image assets exist after Garden Mode generation.

Steps:

1. Enable Garden Mode with `ENABLE_GARDEN_IMAGEGEN=1`.
2. Configure `OPENAI_API_KEY`.
3. Run the six generation commands in `v4_0_project_usage_guide_image_prompts.md`.
4. Inspect generated PNG files.

Expected:

- Six PNG files exist under `docs/design/V4.0/usage-guide-images/`.
- Each PNG is non-empty.
- The images do not contain false-green production or executor claims.
- The images do not contain secrets, tokens, Authorization headers, Bearer values, raw payloads, raw prompts, or signed URLs.
