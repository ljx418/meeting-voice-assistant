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
