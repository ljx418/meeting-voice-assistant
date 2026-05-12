# V3.5 Completion Evidence Bundle

Evidence date: 2026-05-12

Claim under evidence:

```text
V3.5 complete at dev/local Application Adaptation Layer level.
```

Boundary:

- This does not claim production-ready external app support.
- This does not claim complete AgentTalkWindow.
- This does not claim complete Workflow Studio.
- This does not claim enterprise auth/OAuth/SSO readiness.
- This does not claim a multi-tenant production control plane.

## 1. Test Files And Results

Required V3.5 evidence tests:

| Area | Test file | Evidence covered |
| --- | --- | --- |
| Reference App | `tests/test_v3_5_reference_app.py` | BFF-only frontend source scan, BFF EventSource path, approval.respond, scope isolation, external pack/connector discovery, no Core/Gateway hardcoded reference IDs. |
| Embed Contract | `tests/test_v3_5_embed_contract.py` | EmbedDefinition / EmbedBootstrap split, token redaction, allowed actions/channels, trace channel denied by default, EVENT_SCHEMAS alignment. |
| Full BFF Template contract | `tests/test_v3_5_bff_template_contract.py` | BFF import boundary, config safety, `/bff/rpc` denylist including `events.subscribe`, docs status. |
| Full BFF Template E2E | `tests/test_v3_5_bff_template_e2e.py` | Structured routes, BFF-side CapabilityPolicy, EventSource proxy, cursor propagation, redaction, no `/v1/runs/stream` default path. |
| Pack template contract | `tests/test_v3_5_pack_template_contract.py` | Template not auto-discovered, manifest fields, external dummy pack assembly, blocked envelope. |
| Connector template contract | `tests/test_v3_5_connector_template_contract.py` | Template not auto-discovered, descriptor security fields, external dummy connector discovery. |
| Pack/Connector template E2E | `tests/test_v3_5_pack_connector_template_e2e.py` | Dummy pack + connector work together through explicit external paths; no hardcoded ids in Core/Gateway. |
| Existing combined template coverage | `tests/test_v3_5_pack_connector_templates.py` and `tests/test_v3_5_pack_connector_version_compatibility.py` | Version compatibility, unsupported schema/min version blocked, target mismatch degraded, platform neutrality. |
| TypeScript SDK / hooks | `sdk/typescript/tests/client.test.mjs`, `sdk/typescript/tests/embed.test.mjs`, `sdk/typescript/tests/react-hooks.test.mjs` | TS SDK surface, protocol snapshot, EventSource auth helpers, embed validation, hooks no-auto-start/reconnect/dedupe/redaction. |

Observed verification:

```text
./.venv/bin/python -m pytest tests/test_v3_5_*.py -q
144 passed, 6 warnings

./.venv/bin/python -m pytest -q
350 passed, 3 skipped, 6 warnings

cd sdk/typescript && npm test
23 passed

cd examples/reference_app/frontend && npm run build
tsc --noEmit passed
```

Warnings are existing Pydantic / LangGraph deprecation warnings and do not change V3.5 acceptance status.

## 2. Reference App Evidence

Implemented files:

- `examples/reference_app/README.md`
- `examples/reference_app/frontend/src/harness.ts`
- `examples/reference_app/frontend/src/App.tsx`
- `examples/reference_app/frontend/src/views/*`
- `examples/reference_app/pack/manifest.json`
- `examples/reference_app/connector/descriptor.json`
- `examples/reference_app/bff/config.example.json`

Evidence:

- Frontend source defaults to `/bff/*` routes.
- Frontend source does not contain direct `/v1/rpc` or `/v1/events/subscribe` calls.
- Frontend uses `GET /bff/events/subscribe` for browser event subscription.
- Reference pack and connector live under `examples/reference_app/pack` and `examples/reference_app/connector`.
- Reference fixture is platform-neutral and has no Meeting / Knowledge / `data_service` / `voice_service` / `funasr` dependency.
- `tests/test_v3_5_reference_app.py::test_reference_ids_are_not_hardcoded_in_core_or_gateway` verifies no reference app id is hardcoded in Core/Gateway registry files.

## 3. Embed Contract Evidence

Implemented files:

- `sdk/typescript/src/embed.ts`
- `templates/bff/fastapi/app.py` route `GET /bff/embed/bootstrap`
- `examples/embed_contract_demo/embed_definition.example.json`
- `examples/reference_app/frontend/src/views/EmbedPanel.tsx`

Evidence:

- `EmbedDefinition` is static and excludes `capability_token`, `session_id`, `thread_id`, `eventsource_url`, and `subscription_token`.
- Runtime session/thread/event subscription fields are carried by `EmbedBootstrap`.
- BFF bootstrap returns a BFF-local `/bff/events/subscribe` URL.
- BFF bootstrap does not expose upstream `subscription_token`.
- `allowedActions` and `allowedEventChannels` are enforced in tests.
- Trace channel is default closed and requires `traces.read` or `debug`.

## 4. Pack / Connector Template Evidence

Implemented files:

- `templates/pack/manifest.json`
- `templates/connector/descriptor.json`
- `tests/fixtures/v3_5/dummy_pack/manifest.json`
- `tests/fixtures/v3_5/dummy_connector/descriptor.json`
- `core/packs/registry.py`
- `apps/gateway/connectors.py`

Evidence:

- `templates/pack` and `templates/connector` are templates and are not runtime auto-discovered.
- Runtime-discoverable dummy instances live under explicit fixture/reference paths.
- Dummy pack discovery uses `PackRegistry.load_from_paths(...)`.
- Dummy connector discovery uses `ConnectorRegistry(..., connector_descriptor_paths=[...])`.
- Core/Gateway default registry does not hardcode dummy or reference app ids.
- Missing dependencies return stable blocked/degraded assembly envelopes with `blocked_reason`, `missing_dependencies`, and `next_actions`.

## 5. Full BFF Template Evidence

Implemented files:

- `templates/bff/fastapi/app.py`
- `templates/bff/fastapi/capability_policy.py`
- `templates/bff/fastapi/rpc_proxy.py`
- `templates/bff/fastapi/event_proxy.py`
- `templates/bff/fastapi/settings.py`
- `templates/bff/fastapi/security.py`

Evidence:

- `/bff/rpc` is a constrained proxy and rejects `events.subscribe`.
- Browser event subscription uses `/bff/events/subscribe`.
- BFF obtains upstream subscription through Python SDK `events_subscribe`.
- Browser does not see upstream `subscription_token`.
- BFF-side `CapabilityPolicy` gates structured routes and `/bff/rpc`.
- CORS/config/secret hygiene is covered by BFF contract/E2E tests.
- Full BFF template is independent and does not import `templates/bff/fastapi_minimal` internals.

## 6. Documentation Sync Evidence

Documents updated:

- `docs/design/V3.5/00_README.md`
- `docs/design/V3.5/v3_5_current_gap_analysis.md`
- `docs/design/V3.5/v3_5_current_gap_analysis.drawio`
- `docs/design/V3.5/v3_5_event_bridge_plan.md`
- `docs/design/V3.5/v3_5_embed_contract_plan.md`
- `docs/design/V3.5/v3_5_acceptance_plan.md`
- `docs/design/V3.5/v3_5_reference_app_plan.md`

Evidence:

- `00_README.md` describes V3.5 complete at dev/local Application Adaptation Layer level, not a planning entrypoint.
- `v3_5_current_gap_analysis.md` no longer describes V3.5 as not yet in code implementation.
- `v3_5_event_bridge_plan.md` distinguishes native EventSource signed URL / BFF cookie mode from fetch stream bearer mode; native EventSource does not rely on Authorization headers.
- `v3_5_embed_contract_plan.md` separates `EmbedDefinition` from runtime `EmbedBootstrap`; `EmbedDefinition` does not include capability token or eventsource URL.
- `v3_5_acceptance_plan.md` records the dev/local completion claim and preserves No False Green boundaries.

## 7. Final Baseline Statement

The V3.5 baseline can be frozen as:

```text
V3.5 complete at dev/local Application Adaptation Layer level.
```

The next stage should start from productionization or the next named roadmap phase, not by re-opening V3.5 Core/Application Adaptation Layer contracts unless new failures are found.
