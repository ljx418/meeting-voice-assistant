# V4.1 Frontend Stitch Alignment Gap Audit

Date: 2026-05-26

## Source Of Truth

Stitch project: `projects/10240451325799222489`

Authoritative screens and design inputs used for this pass:

- `00-Design-System-Overview`
- `01-Workflow-Studio-Base-Layout`
- `V4.1-00-Workflow-Studio-Home`
- `harnessOS Workflow Studio - 左右双折叠交互设计`
- `harnessOS Workflow Studio - 统一术语与强化节点库`
- `docs/design/V4.1/DESIGN.md`
- `docs/design/V4.1/harnessos_v4_1_workflow_studio_prd.md`

The active Stitch screens and HarnessOS Workflow Studio design systems are light, canvas-centric, five-zone workbench designs. The older project-level dark Glacier metadata is treated as stale metadata and is not used as the V4.1 implementation source of truth.

## Gaps Closed

1. Canvas first layout

- Canvas remains the base layer of the Studio workspace.
- Left node library, right Agent / Inspector panel, and bottom run panel are overlay panels.
- Floating panel controls were replaced by persistent collapsed rails.
- Left and right collapsed states now leave 64px rails that can reopen the corresponding panel.
- Bottom collapsed state now leaves a 48px rail that can reopen run, event, artifact, quality, patch, and governance views.

2. Top mode tabs

- The top tabs now use Chinese UI copy: 工作流, 节点, Agent, 日志.
- Each tab changes the visible work mode instead of acting as a passive label.
- Workflows shows the full Studio, Nodes focuses the node library and inspector, Agent focuses the assistant, Logs focuses the bottom evidence and event area.

3. Canvas interaction

- ReactFlow remains the canvas engine.
- Zoom out, zoom in, fit view, reset view, and minimap controls are wired to real ReactFlow actions.
- Dragging a node from the library uses the drop location for local ghost placement.
- Node movement remains UI local state only and is not written into patch payloads or runtime contracts.
- Canvas grid now uses 24px dotted spacing.

4. Node library and node visual language

- Node library categories now match the V4.1 PRD and DESIGN.md taxonomy.
- Category chips are interactive filters.
- V4.1 local knowledge workflow nodes are visible in the default library.
- Node cards include icon, type, status, artifact contract summary, quality mini-state, attempt count, and ports.
- Ghost nodes use dashed proposal styling.

## Boundary Checks

- No BFF route was added.
- No runtime mutation path was added.
- Canvas layout state remains UI local.
- Agent remains proposal / explain / handoff / navigate only.
- Apply, Publish, Run, and Rerun remain user-confirmed flows.
- Governance evidence remains read-only.

## No False Green

The implementation must not claim:

- complete Workflow Studio ready
- complete AgentTalkWindow ready
- Agent executor ready
- controlled executor ready
- autonomous workflow editing ready
- production-ready external app support
- full multi-Agent orchestration ready

The implementation must not show:

- 自动应用
- 自动发布
- Agent 已执行
- Agent 已发布

## Validation

Focused validation to run after this alignment pass:

```bash
cd apps/workflow-console && npm test
cd apps/workflow-console && npm run build
cd apps/workflow-console && CI=1 npm run test:e2e
```

Screenshot evidence should be saved under:

`docs/design/V4.1/acceptance-evidence/frontend-stitch-alignment/`

## Re-Audit 2026-05-27

### Evidence Captured

Current implementation screenshot:

```text
docs/design/V4.1/ux-audit-evidence/08-current-loaded.png
```

Transient loading screenshot:

```text
docs/design/V4.1/ux-audit-evidence/07-current-after-ux-repair.png
```

Stitch reference screenshot set:

```text
docs/design/V4.1/stitch-screenshots-review/
```

Key Stitch references used in this re-audit:

```text
01-Workflow-Studio-Base-Layout
V4.1-00-Workflow-Studio-Home
V4.1-01-Agent-Create-Draft
V4.1-02-Agent-Draft-Proposal
V4.1-05-Draft-Applied-Canvas
V4.1-11-Run-Board-In-Progress
V4.1-17-Governance-Evidence-ReadOnly
```

### Revised Finding

The previous "Gaps Closed" section is no longer accurate as a completion statement. It should be read only as intended design direction. The current implementation has functional pieces, but the visible UI remains significantly misaligned with Stitch and the V4.1 PRD.

The current screen is closer to a dense internal test console than to the Stitch low-code workflow workbench. It satisfies some automated selectors and BFF-only constraints, but it does not yet satisfy the expected human-facing product experience.

### Critical Gaps Still Open

1. Canvas is not visually first.

- The central canvas exists, but it is visually compressed by the left library, right Agent panel, top scenario stepper, and bottom run board.
- The right Agent panel overlays the canvas and hides part of the workflow surface.
- The stepper is a large floating card inside the canvas instead of a lightweight journey state aligned with Stitch.
- The bottom panel consumes a large part of the viewport and makes the canvas feel like a middle strip.

2. Stitch proportions are not matched.

- Stitch uses a calmer five-zone layout with a clean top bar, compact left navigation, spacious central dotted canvas, right assistant, and bottom run panel.
- The current implementation has too many high-contrast cards and dense chips competing for attention.
- The top bar, left library, stepper, canvas controls, right panel, and bottom board all have similar visual weight, so the hierarchy is flat.

3. Node styling still feels unfinished.

- Current nodes are boxy, large, and visually inconsistent with the Stitch node cards.
- Connector lines and port treatment are not prominent enough for a low-code workflow builder.
- Node labels are truncated aggressively in the stepper and canvas, reducing scannability.
- The selected node state is strong, but the overall flow does not read as a polished 9-node pipeline.

4. Node library is too verbose and not close enough to Stitch.

- Stitch treats the left side as a compact library/navigation surface.
- Current library mixes instruction copy, search, category chips, custom node affordance, and repeated node cards in a dense vertical stack.
- The "自定义节点" entry has too much emphasis for V4.1 and distracts from the canonical 9 Markdown workflow nodes.

5. Top mode tabs exist but do not feel like primary product modes.

- The tab labels are present, but the visual treatment is too small and low-contrast.
- Stitch expects top-level modes to organize the product frame.
- Current tab switching does not clearly reshape the workspace enough for a user to understand why the mode changed.

6. Agent panel is not yet a polished chat TUI.

- The right panel contains useful proposal-only boundaries, but the visual density is high.
- The message layout, composer, proposal cards, and audit entry points still feel like debug panels.
- The panel overlaps the canvas and weakens the "canvas first" requirement.

7. Loading and real-data connection behavior creates a poor first impression.

- The first screenshot captured a blank loading screen with only "正在连接真实工作流数据...".
- Even if the loaded state appears shortly after, the product lacks a polished skeleton layout or graceful connection state.
- This makes the app feel unstable during manual review.

8. Previous automated green results are not enough.

- The current UI can pass frontend tests and E2E selectors while still failing manual UX acceptance.
- Current false-green risk for frontend quality is HIGH.
- Current spec-drift risk against Stitch visual direction is MEDIUM to HIGH.

### Required UX Repair Direction

The next UI repair should not add new runtime capability. It should focus on rebuilding the visual hierarchy around the Stitch workbench:

1. Rebuild the shell proportions:

- top bar 56px
- left rail around 260px expanded, 64px collapsed
- right panel around 360px expanded, 64px collapsed
- bottom panel around 220 to 260px expanded, 48px collapsed
- canvas should fill the remaining surface and remain visible as the base layer

2. Move the scenario stepper out of the canvas center.

- Use a compact horizontal progress strip or toolbar state.
- Do not let the stepper cover or compete with workflow nodes.

3. Simplify the node library.

- Make the canonical 9 V4.1 nodes the primary content.
- Reduce instructional copy.
- Lower visual priority of custom-node and future capability controls.

4. Redesign node cards and edges.

- Use smaller, cleaner cards with consistent icon, title, type, status badge, artifact line, quality mini-state, and attempt count.
- Make ports and connector lines visually clear.
- Ensure the 9-node flow is readable at 1440x960 without crowding.

5. Turn the right Agent panel into a true chat TUI.

- Message stream, composer, proposal cards, and handoff buttons should be visually distinct.
- Keep proposal-only boundaries, but avoid debug-like labels.
- Ensure collapsing the panel leaves a visible reopen rail.

6. Improve loading and connection states.

- Show the five-zone skeleton immediately.
- Put connection status in a subtle top or bottom status area.
- Avoid a blank full-page loading state for normal startup.

### Re-Audit Decision

Do not claim Stitch alignment complete.

Do not continue adding new V4.2 or multi-Agent capability before this V4.1 front-end shell is repaired.

Recommended next stage:

```text
V4.1-UX-R2 Stitch Workbench Alignment Repair / Stitch 工作台对齐修复
```

Proceed only with UI shell, visual hierarchy, node/card/edge styling, panel collapse behavior, loading state, and manual UX evidence. Runtime behavior and governance boundaries should remain unchanged.
