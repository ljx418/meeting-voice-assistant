# Third-party Contract v3 Smoke Evidence

status: passed

date: 2026-05-23

## Scope

Validate the V3 third-party local agent contract against a running desktop bridge.

## Command

```bash
node scripts/v3_2_third_party_contract_smoke.mjs
```

## Result

`node scripts/v3_2_third_party_contract_smoke.mjs` passed with run id `1779548639344-b9d16e`.

## Smoke Cases

| Case | Result |
| --- | --- |
| desktop health | passed |
| missing token returned `401 auth_missing` | passed |
| invalid token returned `401 auth_invalid` | passed |
| `petctl list` baseline | passed |
| `petctl attach` smoke instance | passed |
| `/api/events` legacy default accepted | passed |
| legacy default did not alter target instance | passed |
| `/api/instances/:instanceId/events` accepted | passed |
| instance route updated target to `need_input` | passed |
| `petctl notify --instance` accepted | passed |
| `petctl notify --instance` updated target to `warning` | passed |
| unknown instance returned `instance_not_found` | passed |
| invalid instance returned `instance_id_invalid` | passed |
| invalid sound redaction | passed |
| curl local contract example | passed |
| Node local contract example | passed |
| Python local contract example | passed |
| hard limit returned `instance_limit_reached` | passed |
| temporary smoke instance cleanup | passed |
| security redaction scan | passed |

## Security

Auth failure cases verified `auth_missing` and `auth_invalid` without printing token values or auth header values. The smoke summary did not include request-body dumps, config file names, workspace locations, full user-local paths, or the rejected sound input.

## Decision

Third-party contract v3 local smoke passed.

Allowed scoped claim:

```text
V3.2 third-party contract v3 smoke passed.
```

Still forbidden:

```text
Third-party agent integration verified
```
