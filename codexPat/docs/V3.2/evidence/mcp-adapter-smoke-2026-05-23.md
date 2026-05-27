# MCP Adapter Smoke Evidence

status: passed

date: 2026-05-23

## Scope

Validate `packages/pet-mcp` as a minimal MCP adapter that routes only through localhost HTTP/Event Bridge.

## Commands

```bash
pnpm --filter @agent-desktop-pet/petctl build
pnpm --filter @agent-desktop-pet/pet-mcp build
curl -sS http://127.0.0.1:17321/api/health
node scripts/v3_2_mcp_adapter_smoke.mjs
```

## Results

| Check | Result | Notes |
| --- | --- | --- |
| desktop health | passed | `/api/health` returned `ok: true` before smoke. |
| `petctl` build | passed | CLI dist was available for smoke. |
| `pet-mcp` build | passed | MCP dist was available for smoke. |
| `node scripts/v3_2_mcp_adapter_smoke.mjs` | passed | Run id `1779548637375-10bd56`. |

## Smoke Cases

| Case | Result |
| --- | --- |
| MCP initialize | passed |
| tools list includes `pet_notify`, `pet_list_instances`, `pet_get_capabilities`, `pet_get_state` | passed |
| `pet_list_instances` sanitized response | passed |
| `pet_get_capabilities` public summary | passed |
| `pet_notify` default route accepted | passed |
| default route did not alter target smoke instance | passed |
| `pet_notify` instance route accepted | passed |
| instance route updated target to `need_input` | passed |
| `pet_get_state` returned target state | passed |
| unknown instance returned `instance_not_found` | passed |
| invalid instance returned `instance_id_invalid` | passed |
| invalid sound rejected before bridge with `schema_invalid` | passed |
| temporary smoke instance cleanup | passed |
| security redaction scan | passed |

## Security

The smoke summary did not include token values, auth header values, request-body dumps, config file names, workspace locations, full user-local paths, or the rejected sound input.

## Decision

MCP adapter runtime acceptance passed for the scoped localhost bridge adapter.

Allowed scoped claim:

```text
V3.2 MCP adapter minimal smoke passed for localhost bridge routing.
```

Still forbidden:

```text
MCP ready
```
