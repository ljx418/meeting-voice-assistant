# V2.10 Gap Analysis

## 1. Current V2.9 Baseline

V2.9 accepted:

- line-level public-surface evidence for `data_service`;
- shallow relationships;
- calibrated ranking;
- human review report;
- Architecture Context Pack v3;
- structured blocker behavior for HarnessOS.

HarnessOS E2E result:

```json
{
  "accepted_evidence": 0,
  "evidence_rows": 120,
  "blocker_counts": {
    "LINE_RANGE_INVALID": 120
  }
}
```

## 2. Remaining Gap

V2.9 can reject false evidence but cannot yet resolve many large-project architecture patterns to source line ranges.

## 3. V2.10 Target Gap Closure

| Gap | Current | V2.10 Target |
| --- | --- | --- |
| registry patterns | candidate only | registry key binds to symbol definition |
| decorators | not generalized | decorator registration binds to function/class |
| workflow/adapters/agents | project-specific concepts unresolved | generic adapter taxonomy and config |
| imports | weak path reference | local definition lookup |
| manifests | not a first-class input | schema-validated candidate source |
| runtime introspection | not supported | optional safe candidate importer |
| HarnessOS blockers | `LINE_RANGE_INVALID` | accepted evidence or precise blockers |

## 4. Major Risks

- overfitting to HarnessOS;
- running unsafe target project commands;
- accepting manifest/document claims without code evidence;
- treating imports as runtime calls;
- adding optional provider dependencies that break local runs.

## 5. Controls

- adapter registry must be generic and configurable;
- runtime introspection disabled by default;
- accepted evidence still requires line truth check;
- definition lookup unavailable is structured, not fatal;
- closure requires data_service, HarnessOS, and generic fixture evidence.

## 6. Closure Status

V2.10 has closed the planned gaps for the deterministic local adapter baseline.

| Gap | Closure status |
| --- | --- |
| registry patterns | closed |
| decorators | closed |
| workflow/adapters/agents generic taxonomy | closed |
| imports / local definition lookup | closed for AST baseline; optional providers conditionally accepted |
| manifests | closed as candidate-only contract |
| runtime introspection | closed as disabled-by-default safe candidate contract |
| HarnessOS blockers | closed by accepted line-level evidence and precise blockers |

Real E2E results:

```text
data_service: accepted=206 attempts=2559
HarnessOS: accepted=431 attempts=7599
```

Remaining non-blocking limitations:

- Dynamic registry expressions remain `needs_review`.
- Manifest and runtime outputs remain candidate-only until statically bound to code evidence.
- Optional Jedi/tree-sitter providers are not required for V2.10 closure.
