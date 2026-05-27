# MCP Adapter Smoke Evidence Template

status: planned

date: YYYY-MM-DD

## Scope

Validate `packages/pet-mcp` as a minimal MCP adapter that routes only through localhost HTTP/Event Bridge.

## Required Cases

| Case | Expected |
| --- | --- |
| `pet_notify` default route | accepted; affects default route only |
| `pet_notify` with `instanceId` | accepted; affects target instance only |
| unknown instance | rejected with `instance_not_found` |
| invalid instance | rejected with `instance_id_invalid` |
| invalid sound/path | rejected and redacted |
| `pet_list_instances` | sanitized; no local paths or position |
| `pet_get_capabilities` | public capability summary |
| `pet_get_state` | sanitized state for all or one instance |

## Security Scan

The evidence summary must not contain token values, auth header values, request-body dumps, config file names, workspace locations, full user-local paths, or rejected unsafe input values.

## Result

planned
