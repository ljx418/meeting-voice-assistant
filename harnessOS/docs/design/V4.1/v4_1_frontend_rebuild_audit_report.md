# V4.1 Frontend Rebuild Audit Report

Status: active audit report for the Stitch-aligned frontend rebuild.

## Audit Sources

```text
docs/design/V4.1/harnessos_v4_1_workflow_studio_prd.md
docs/design/V4.1/DESIGN.md
docs/design/V4.1/v4_1_stitch_frontend_rebuild_review.md
docs/design/V4.1/v4_1_frontend_button_inventory.md
docs/design/V4.1/v4_x_prototype_to_frontend_mapping.md
```

## Current Audit Verdict

Verdict:

```text
PASS TO IMPLEMENT FE-A THROUGH FE-F WITH GUARDS
```

Rationale:

1. The PRD and Stitch screens agree on a light five-zone low-code workflow workbench.
2. The V4.1 target scenario is narrow: local recursive Markdown folder summary.
3. The 18 canonical Stitch screens define a complete button-level MVP path.
4. Existing BFF/browser tests already cover much of the local workflow behavior.
5. The remaining implementation work can stay frontend-scoped without adding Agent executor or generic controlled executor behavior.

## Closed Audit Items

| Item | Resolution |
| --- | --- |
| Dark theme conflict | Use the latest light Stitch prototype and `DESIGN.md` as source of truth. |
| Older 7-screen summary vs 18-screen canonical path | Treat `V4.1-00` through `V4.1-17` as canonical. Older screens are reference only. |
| ChromeCLI availability | `chromecli` and `chrome-cli` are not in shell PATH; use existing local Chrome Playwright scripts unless a binary path is provided. |
| Agent boundary | Agent remains propose / explain / handoff / navigate only. |
| Runtime scope | V4.1 frontend rebuild must not implement generic controlled executor or V4.2+ behavior. |

## UX Review Criteria

Each stage must check:

1. Does the screen visually match the Stitch light workbench?
2. Is the canvas still the primary surface?
3. Is the right panel an Agent / Inspector panel, not a pure chatbot app?
4. Are user-confirmed operations visually distinguishable?
5. Is governance evidence read-only?

## PRD Spec Review Criteria

Each stage must check:

1. Does the flow still implement the Desktop/技术分享 Markdown summary scenario?
2. Are the 9 nodes present and named consistently?
3. Does Debug Scan avoid summary generation?
4. Are artifacts and quality report visible?
5. Does Agent avoid automatic scan, apply, publish, run, and rerun?

## Risk Assessment

Spec Drift Risk:

```text
MEDIUM
```

Reason:

The frontend has accumulated many V4.0/V4.x surfaces. The rebuild must avoid pulling V4.2-V4.6 ideas into the V4.1 implementation.

False Green Risk:

```text
MEDIUM
```

Reason:

Existing E2E fixtures are strong but can still pass if the UI is only functionally correct and not UX-aligned with the new Stitch path. Manual screenshot review is required after automated E2E.

Proceed Decision:

```text
Proceed with FE-A through FE-F implementation. Stop if either risk becomes HIGH.
```
