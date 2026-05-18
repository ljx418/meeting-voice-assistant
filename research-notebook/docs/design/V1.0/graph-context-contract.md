# ResearchNotebook V1.0 Graph Context Contract

文档状态：P0 implementation contract；V1.0-M4 frozen。
适用阶段：M4 only；M5+ source preview / precise backjump 不属于本文范围。

## 1. Purpose

Graph Context is a read-only product context surface. It helps users inspect related workspace/session knowledge without turning ResearchNotebook into a graph governance console.

## 2. Allowed Scope

- Workspace graph neighbors.
- Workspace graph communities.
- Session graph context.
- Missing graph artifact / graph unavailable / backend unavailable states.
- Local node selection or highlight only.

## 3. Forbidden Scope

- Graph DSL or query builder.
- Graph editing, merge, delete, rebuild, or mutation workflows.
- Graph governance console.
- Parsing `artifact_ref` as a filesystem path.
- Blocking workspace/session ask flows when graph routes fail.
- Calling `/api/v1/knowledge/*`.

## 4. DTO Surface

M4 frontend fallback DTOs:

- `GraphNode`;
- `GraphEdge`;
- `GraphNeighbor`;
- `GraphNeighborsResponse`;
- `GraphCommunity`;
- `GraphCommunitiesResponse`;
- `SessionGraphContextResponse`.

All backend raw responses must be mapped inside `shared/api/dataServiceClient.ts` before feature modules render them.

## 5. Typed Wrappers

The product-facing wrapper surface is:

- `graph.neighbors(workspaceId)`;
- `graph.communities(workspaceId)`;
- `graph.session(workspaceId, sessionId)`.

If backend route naming differs, only `dataServiceClient.ts` may adapt route shape.

## 6. UI Rules

- Graph routes render read-only lists/cards or compact visual context.
- Missing graph artifact renders explicit unavailable state.
- Node clicks may update local UI selection only.
- Graph failure must not clear workspace or session answers.
- Session graph context must not block session query or evidence rendering.

## 7. Query Keys

- `['graph-neighbors', workspaceId]`;
- `['graph-communities', workspaceId]`;
- `['session-graph', workspaceId, sessionId]`.

## 8. Acceptance

M4 is API-adapter-ready when:

- graph neighbors and communities render through typed wrappers;
- session graph context renders in Session Workbench without blocking answers;
- missing graph artifact and service unavailable states are visible;
- no graph write/governance actions are exposed.
