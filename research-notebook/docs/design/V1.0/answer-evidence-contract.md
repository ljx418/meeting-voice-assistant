# ResearchNotebook V1.0 Answer Evidence Contract

文档状态：P0 implementation contract；V1.0-RC5 release package current。
适用阶段：M2-M4 / RC2-RC7。

## 1. Purpose

V1.0 Ask with Evidence must not be a plain chat UI. Every answer view must make evidence state explicit.

Minimum flow:

```text
question -> answer -> source-level citation -> source trace/provenance drawer
```

## 2. AnswerEvidence ViewModel

V1.0 frontend renders evidence through:

```ts
type AnswerEvidence = {
  evidenceKey: string;
  sourceId?: string;      // registry source_id only; safe for sources.trace
  sourceRef?: string;     // hit.source / slug / backend ref; display-only by default
  sourceTitle?: string;
  traceAvailable: boolean;
  artifactRefs?: string[];
  snippet?: string;
  confidence?: number;
  traceUnavailableReason?: "missing_source_id" | "source_ref_not_traceable" | "trace_route_failed";
};
```

The ViewModel may be adapted from backend query response fields, but UI components must consume this normalized shape.

## 3. Rendering Rules

When evidence exists:

- render source-level citation chips/cards near the answer;
- show source title when available;
- show snippet when available;
- show trace availability state;
- clicking a citation with registry `sourceId` opens source trace/provenance drawer.

Evidence source resolution:

- `evidence.source_id` may become `sourceId` only when it is a registry source id or matches the source registry list;
- `hit.source` may become `sourceId` only when it exactly matches a registry source id;
- `hit.source`, `hit.meta.slug`, page slug, or llmwiki page id that does not match registry source ids must be rendered as `sourceRef`;
- `sourceRef` evidence is display-only and must not call source trace;
- no string-prefix heuristic may mark a source ref as traceable.

When precise locator is missing:

- fall back to source-level evidence;
- do not hide the citation;
- do not fabricate page/slide/timestamp/json path.

When no evidence exists:

- render explicit `no evidence available` state;
- keep the answer visible if backend returned one;
- do not present the answer as fully grounded.

When trace route fails:

- keep the answer and citation visible;
- mark citation or drawer as `trace unavailable`;
- if `sources.get` succeeds but `sources.trace` returns 404, the drawer may show source title/source_id/artifact refs as metadata fallback;
- if evidence has only `sourceRef`, do not call trace route;
- show retry affordance where practical;
- do not crash or clear the answer.

## 4. Multi-source Answers

If one answer references multiple sources:

- render one citation chip/card per source;
- keep ordering stable according to backend order;
- collapse overflow only if all sources remain accessible;
- opening one citation opens drawer scoped to that source.

## 5. Session Reuse

Session query evidence must reuse the same ViewModel and rendering components as workspace query evidence.

Session-specific metadata may be shown around the answer, but evidence behavior remains source-grounded.

## 6. Acceptance

M2 is not complete unless:

- workspace query answer has evidence/no-evidence state;
- source-level citation click opens trace drawer via `source_id`;
- trace failure is visible and non-fatal;
- artifact refs are never treated as paths.
