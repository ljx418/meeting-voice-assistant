# ResearchNotebook V1.0-RC2 Source Trace / Graph Context Alignment Plan

文档状态：RC2 implementation record。
适用阶段：V1.0-RC2；不进入 M5+。

## 1. Scope

RC2 resolves or formalizes two RC1 degraded states:

- query evidence may return llmwiki page refs/slugs that are not registry `source_id`;
- graph neighbors requires `node_id` or `entity_id` and cannot be called as workspace overview.

Out of scope: source preview, precise citation backjump, multi-format ingestion, assessment, graph editing/governance, quality governance console.

## 2. Source Trace Alignment

`AnswerEvidence` now separates:

- `sourceId`: registry source id only; can call `sources.trace`;
- `sourceRef`: hit source, slug, page id, or backend raw ref; display-only unless exactly matched to registry source ids.

Mapper rules:

- `evidence.source_id` or `hit.source` becomes `sourceId` only after exact registry source id matching;
- `hit.source` / `hit.meta.slug` that does not match registry ids becomes non-clickable `sourceRef`;
- trace 404 keeps answer visible and shows trace unavailable;
- trace 404 with a valid source detail can show source title/source_id/artifact refs as metadata fallback.

## 3. Graph Context Alignment

Graph overview now calls communities first:

- `graph.communities(workspaceId)` maps to `/graph/community?include_members=true`;
- `graph.neighbors(workspaceId, { nodeId } | { entityId })` is only called after selection;
- no feature module may call neighbors without node/entity scope.

Query keys:

- `['graph-neighbors', workspaceId, 'node', nodeId]`;
- `['graph-neighbors', workspaceId, 'entity', entityId]`;
- `['graph-communities', workspaceId]`.

## 4. Acceptance

RC2 is complete when:

- query hit source slug renders as non-traceable evidence metadata;
- registry source id evidence remains clickable;
- trace route 404 does not clear answers;
- graph overview does not issue unscoped neighbors requests;
- selecting a community member with `node_id` triggers node-scoped neighbors;
- boundary checks and `npm run check` pass.
