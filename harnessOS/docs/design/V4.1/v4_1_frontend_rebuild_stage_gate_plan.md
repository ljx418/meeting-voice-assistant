# V4.1 Frontend Rebuild Stage Gate Plan

Status: active execution plan for the Stitch-aligned Workflow Console frontend rebuild.

This plan is based only on:

```text
docs/design/V4.1/harnessos_v4_1_workflow_studio_prd.md
docs/design/V4.1/DESIGN.md
docs/design/V4.1/v4_1_stitch_frontend_rebuild_review.md
docs/design/V4.1/v4_1_frontend_button_inventory.md
docs/design/V4.1/v4_x_prototype_to_frontend_mapping.md
```

Allowed stage claim:

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

## Stage Gate Rules

Each substage must finish with:

1. End-to-end browser validation.
2. UX review against Stitch screenshots.
3. PRD specification review.
4. Spec Drift Risk.
5. False Green Risk.
6. Proceed / stop decision.

Stop and request user confirmation if:

1. UX conflicts with PRD or Stitch.
2. A required interaction is missing or blocked.
3. A new behavior is needed that PRD and Stitch do not define.
4. Agent behavior drifts into automatic apply, publish, run, or rerun.
5. Browser directly calls `/v1/rpc` or `/v1/events/subscribe`.
6. Spec Drift Risk or False Green Risk is HIGH.

## FE-A Visual System And Five-Zone Shell

Goal:

Align the page shell to the light Stitch workbench.

Required prototype coverage:

```text
00-Design-System-Overview
01-Workflow-Studio-Base-Layout
02-Node-Library-And-Canvas-States
V4.1-00-Workflow-Studio-Home
```

Acceptance:

1. First screen is a usable workbench, not a landing page.
2. Top Bar, Left Node Library, Central Canvas, Right Agent / Inspector Panel, and Bottom Run Panel are visible.
3. Light theme is dominant.
4. Canvas remains the main visual surface.

## FE-B Agent Draft And Patch Diff Flow

Goal:

Complete proposal-first workflow creation.

Required prototype coverage:

```text
V4.1-01-Agent-Create-Draft
V4.1-02-Agent-Draft-Proposal
V4.1-03-Patch-Diff-Review
V4.1-04-Apply-Confirmation
V4.1-05-Draft-Applied-Canvas
```

Acceptance:

1. Agent input generates proposal only.
2. Canvas shows pending / ghost nodes before apply.
3. Patch Diff is visible.
4. Apply requires user confirmation.
5. After apply, formal 9 nodes appear after BFF truth refresh.

## FE-C Folder Inspector, Authorization, And Debug Scan

Goal:

Complete scoped local folder setup and non-mutating debug scan.

Required prototype coverage:

```text
V4.1-06-Folder-Input-Inspector
V4.1-07-Folder-Authorization
V4.1-08-Debug-Scan-Result
```

Acceptance:

1. Folder input path is configurable.
2. Debug scan is disabled before authorization.
3. Debug scan shows file tree/counts only.
4. Debug scan does not generate summary artifacts.

## FE-D Publish, Run, Artifacts, And Quality

Goal:

Complete user-confirmed publish/run and output review.

Required prototype coverage:

```text
V4.1-09-Publish-Version-Confirm
V4.1-10-Run-Workflow-Confirm
V4.1-11-Run-Board-In-Progress
V4.1-12-Run-Completed-Artifacts
V4.1-13-Quality-Report
```

Acceptance:

1. Publish and run are user-triggered.
2. Run board shows 9 logical nodes.
3. Artifacts panel shows required summaries.
4. Quality report shows unsupported file and empty folder.

## FE-E Recovery, Rerun, Agent Debug, And Evidence

Goal:

Complete V4.1 recovery, failure, rerun, Agent debug, and governance evidence surfaces.

Required prototype coverage:

```text
V4.1-14-Refresh-Recovery
V4.1-15-Failure-And-Rerun
V4.1-16-Agent-Debug-Fix-Proposal
V4.1-17-Governance-Evidence-ReadOnly
```

Acceptance:

1. Refresh restores workflow instance state.
2. Failed node shows error and attempt history.
3. Rerun is user-confirmed and preserves old attempts.
4. Agent debug produces explanation or proposal only.
5. Governance evidence is read-only.

## FE-F Consolidation Gate

Goal:

Decide whether this frontend rebuild is ready for dev/local validation.

Acceptance:

1. Full 18-screen Stitch path can be followed.
2. PRD local Markdown summary path passes.
3. No false-green copy exists.
4. Validation commands pass or any failure is recorded with a stop decision.
5. Spec Drift Risk and False Green Risk are not HIGH.
