# ResearchNotebook V1.0-RC5 Repository Hygiene Summary

文档状态：RC5 release packaging record。

## 1. Scope

RC5 performs release packaging and repository hygiene only. It does not add M5+ product capability and does not change `data_service`.

RC5 means `Release Candidate 5`. In this project it is a packaging/readiness stage, not a feature milestone. The M0-M4 product implementation already exists before RC5; RC5 only makes the candidate package easier to verify, hand off, and audit.

RC5 is intentionally narrow:

- normalize the release smoke command;
- make README/onboarding state match the real product state;
- separate real smoke fixtures from adapter-only fixtures;
- keep release checklist honest with `PASS` / `DEGRADED_ACCEPTED` / `NOT_READY`;
- keep gap markdown and drawio synchronized.

RC5 does not upgrade any future capability to ready.

## 2. Command Naming

Recommended release smoke command:

```bash
npm run smoke:release
```

Legacy alias retained:

```bash
npm run smoke:rc1
```

Both commands run `scripts/release-smoke.mjs`. The release smoke defaults to `http://127.0.0.1:8003` and can be pointed at another backend with `RN_DATA_SERVICE_BASE_URL` or `VITE_DATA_SERVICE_BASE_URL`.

## 3. Fixture Hygiene

Real backend smoke fixtures:

- `fixtures/real/`

Synthetic adapter contract fixtures:

- `fixtures/adapter/`

Adapter fixtures must not be reported as real backend pass cases. The key adapter-only fixtures are:

- `query-hit-source-registry-id.json`;
- `session-query-with-evidence.json`;
- `graph-community-without-node-id.json`.

## 4. Package Hygiene

`.gitignore` covers:

- `node_modules/`;
- `dist/`;
- `.DS_Store`;
- `.env` / `.env.*`;
- `coverage/`;
- Playwright/test output;
- local `.data_service_workspace.json`;
- temporary smoke directories.

## 5. Current Release Statement

Allowed:

```text
ResearchNotebook V1.0 release candidate package is repository-ready.
ResearchNotebook V1.0 M0-M4 is integration-smoke-ready.
ResearchNotebook V1.0 source-grounded personal knowledge MVP is release candidate ready with trace-unavailable fallback.
```

Not allowed:

```text
source trace integration ready
source preview ready
precise citation backjump ready
multi-format ingestion ready
assessment ready
quality governance console ready
graph editing/governance ready
cloud sync/collaboration ready
```

## 6. Remaining Development After RC5

For V1.0 release gate, the remaining work is not a broad feature implementation track. The main remaining items are:

| Track | V1.0 RC blocking | Meaning |
| --- | --- | --- |
| Scoped commit / push | No | Package the current `research-notebook/` working tree without mixing sibling workspace projects. |
| Optional `smoke:release` rerun | No, unless release evidence must be refreshed | Requires local `data_service` to be running. RC3 real smoke remains the current integration evidence. |
| Source trace backend alignment | No for RC; yes for claiming trace integration ready | `sources.trace` must return stable provenance for registry `source_id`; until then V1.0 only supports trace-unavailable fallback. |
| M5 Source Preview / Evidence Navigation | No | Post-MVP / V1.1 work depending on `DocumentUnit` and `EvidenceSpan`. |
| M6 Multi-format Foundation | No | V1.2 direction depending on capability manifest and parser contracts. |
| M7 Assessment Future Shell | No | V2.0 direction; no question generation/scoring/mastery in V1.0. |

Short version:

```text
V1.0 M0-M4 development: complete.
V1.0 RC5 package hygiene: complete.
V1.0 source trace integration: not ready, accepted fallback only.
V1.1+ / V1.2+ / V2.0 capability work: still future.
```
