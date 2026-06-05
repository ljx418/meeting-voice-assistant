# V2.10 Real Repo E2E Acceptance Matrix

## Required Repositories

| Repo | Role | Acceptance expectation |
| --- | --- | --- |
| `data_service` | baseline known project | no regression; accepted evidence remains valid |
| `HarnessOS` | large architecture-heavy project | improve line evidence or produce more precise blockers |
| generic fixture / third real repo | generality proof | at least three adapter types work without HarnessOS-specific logic |

## E2E Flow

For each repo:

1. import codebase;
2. create snapshot;
3. build inventory and symbols;
4. build V2.9 evidence;
5. build V2.10 pattern adapters;
6. build bindings and definition lookup;
7. build pattern evidence report;
8. read via HTTP/MCP/CLI;
9. inspect artifacts on disk;
10. run false-green audit.

## Required Assertions

- adapter attempts count > 0;
- accepted bindings or structured blockers exist;
- accepted binding line ranges pass truth check;
- manifest-only entries are not accepted without code binding;
- runtime introspection is disabled unless explicitly enabled;
- report explains adapter matches and blockers;
- no absolute path leak;
- no full-call-graph claim.

## HarnessOS Specific Acceptance Without HarnessOS-Only Code

HarnessOS acceptance may use a project adapter configuration, but generic engine code must not contain hardcoded HarnessOS path names or labels.

Accepted outcomes:

- accepted evidence count improves; or
- blocker changes from generic `LINE_RANGE_INVALID` to precise blockers such as `DYNAMIC_REGISTRY_UNRESOLVED`, `DEFINITION_LOOKUP_UNAVAILABLE`, or `MANIFEST_BINDING_MISSING`.

Rejected outcomes:

- copying HarnessOS design docs into code evidence;
- marking workflow names accepted without source line range;
- hiding unresolved architecture surfaces from report.
