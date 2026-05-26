# V4.1 Frontend Rebuild Completion Note

Status: completed for dev/local validation.

Allowed claim after successful validation:

```text
V4.1 frontend rebuild complete: Stitch-aligned local knowledge workflow UI ready for dev/local validation.
```

Forbidden claims:

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
```

## Implementation Summary

Completed in this pass:

1. Added frontend rebuild stage gate plan.
2. Added frontend rebuild acceptance plan.
3. Added frontend rebuild audit report.
4. Added completion note.
5. Updated Workflow Console bottom panel with an explicit `运行看板` tab.
6. Updated V4.1 rerun and Agent debug button copy to match PRD/Stitch intent.

Additional rewrite pass after manual UX rejection:

1. Replaced the Workflow Console shell with a Stitch-aligned five-zone layout:
   Top Bar, Left Node Library, Central Canvas, Right Agent or Inspector Panel, Bottom Run Panel.
2. Replaced the legacy dark CSS with a light canvas-first UI style matching the V4.1 prototype direction.
3. Kept BFF client, DTO types, hooks, proposal-first apply, publish, run, rerun, and governance paths unchanged.
4. Preserved controlled catalog rendering from BFF DTOs and removed local fallback duplication for BFF-supplied labels.
5. Preserved V4.1 local folder summary controls, artifacts, quality report, evidence review, and no direct browser `/v1/*` access checks.

Latest canvas-first closure pass:

1. Added prototype top tabs: Workflows, Nodes, Agents, Logs.
2. Made the canvas the base layer and moved Node Library, Agent/Inspector, and Run Panel into independently collapsible overlays.
3. Replaced the static canvas node layout with `@xyflow/react` so the browser view has real graph nodes, handles, curved edges, and edge proposal controls.
4. Added a static SSR fallback for contract tests so rendered HTML still exposes station cards, ghost nodes, and edge proposal copy.
5. Reworked node placement and default viewport so the first screen keeps nodes readable between the left and right panels.
6. Hardened V4.1 folder summary proposal actions by passing the visible `proposal_id` into apply, publish, and run handlers.
7. Hardened Agent handoff routing by using the clicked proposal's bound `workflow_instance_id`, avoiding stale selected-instance routing.

## Files Changed

```text
apps/workflow-console/src/components/ConsoleShell.tsx
apps/workflow-console/src/components/AgentTalkShell.tsx
apps/workflow-console/src/components/WorkflowHeader.tsx
apps/workflow-console/src/hooks/useWorkflowConsoleData.ts
apps/workflow-console/src/main.tsx
apps/workflow-console/src/styles.css
apps/workflow-console/package.json
apps/workflow-console/package-lock.json
docs/design/V4.1/v4_1_frontend_rebuild_stage_gate_plan.md
docs/design/V4.1/v4_1_frontend_rebuild_acceptance_plan.md
docs/design/V4.1/v4_1_frontend_rebuild_audit_report.md
docs/design/V4.1/v4_1_frontend_rebuild_completion_note.md
docs/design/V4.1/acceptance-evidence/frontend-rebuild-latest.png
```

## UX Review

Current assessment:

```text
PASS WITH MANUAL REVIEW REQUIRED
```

Reason:

The UI now exposes an explicit run board tab and uses V4.1 button language for rerun and Agent repair proposal. The automated browser path passes. A human should still compare the rendered screen with the saved Stitch screenshots before treating visual fidelity as fully accepted.

## PRD Spec Review

Current assessment:

```text
PASS
```

Checked requirements:

1. Agent remains proposal-first.
2. Folder authorization and debug scan remain user-triggered.
3. Publish, run, and rerun remain user-triggered.
4. Run board, artifacts, quality, and governance surfaces remain available.

## Spec Drift Evaluation

Risk:

```text
MEDIUM
```

Reason:

The implementation only changed V4.1 frontend surfaces, but V4.2+ terms still exist in surrounding planning documents. No V4.2+ runtime behavior was added.

## False Green Evaluation

Risk:

```text
MEDIUM
```

Reason:

Automated tests verify the interaction path, redaction, BFF-only browser requests, and 10-case V4.1 acceptance. They cannot fully judge visual fidelity against Stitch. Manual screenshot review remains required.

## Validation Commands

Executed:

```text
workflow-console npm test: PASS, 75/75
workflow-console build: PASS
workflow-console e2e: PASS, 17/17
V4.1 folder summary 10-case browser acceptance: PASS, 10/10
```

Latest rewrite validation:

```text
cd apps/workflow-console && npm test: PASS, 75/75
cd apps/workflow-console && npm run build: PASS
cd apps/workflow-console && CI=1 npm run test:e2e: PASS, 17/17
```

Latest canvas-first closure validation:

```text
cd apps/workflow-console && npm test: PASS, 75/75
cd apps/workflow-console && npm run build: PASS
cd apps/workflow-console && CI=1 npm run test:e2e: PASS, 17/17
Chrome screenshot capture: PASS
```

Acceptance evidence:

```text
docs/design/V4.1/acceptance-evidence/desktop-folder-summary/result-summary.md
docs/design/V4.1/acceptance-evidence/desktop-folder-summary/network-log.json
docs/design/V4.1/acceptance-evidence/desktop-folder-summary/console-errors.json
docs/design/V4.1/acceptance-evidence/desktop-folder-summary/screenshots/
docs/design/V4.1/acceptance-evidence/frontend-rebuild-latest.png
```

No False Green scan:

```text
apps/workflow-console/src: PASS, no forbidden completion or automation copy found
docs/design/V4.1: REVIEWED, forbidden phrases appear only in PRD/design guardrails, no-false-green lists, acceptance criteria, or completion boundary sections
```

## Proceed Decision

```text
Proceed to manual screenshot review. Do not proceed to the next product stage if the manual review finds major PRD/Stitch mismatch.
```

Manual validation focus after rewrite:

```text
1. Compare the running page against the V4.1 Stitch screenshots in docs/design/V4.1/stitch-screenshots-review/.
2. Verify the five-zone layout is visually close enough before continuing deeper frontend work.
3. Treat any major mismatch in layout hierarchy, light visual style, or proposal-first interaction as a stop-and-correct issue.
```
