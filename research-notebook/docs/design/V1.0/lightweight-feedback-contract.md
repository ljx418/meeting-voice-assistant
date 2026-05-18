# ResearchNotebook V1.0 Lightweight Feedback Contract

文档状态：P0 implementation contract；V1.0-M4 frozen。
适用阶段：M4 only；Quality/Governance console 不属于 V1.0 release gate。

## 1. Purpose

Lightweight Feedback captures user reactions near product answers or graph context. It is a product feedback affordance, not a quality governance workflow.

## 2. Allowed Scope

- Feedback entry near workspace answer.
- Feedback entry near session answer.
- Feedback entry near graph context when useful.
- Rating up/down.
- Optional short comment.
- Local submitted / failed states.

## 3. Forbidden Scope

- Correction rules CRUD.
- Correction plan UI.
- Governance review workflow.
- Quality console as a primary page.
- Clearing answer content when feedback submission fails.
- Calling `/api/v1/knowledge/*`.

## 4. DTO Surface

```ts
type QualityFeedbackRequest = {
  target_type: 'workspace_answer' | 'session_answer' | 'source' | 'graph_context';
  rating: 'up' | 'down';
  comment?: string;
  session_id?: string;
  source_id?: string;
  evidence_key?: string;
};
```

The adapter attaches `workspace_id` through the typed wrapper route context.

## 5. Typed Wrapper

- `quality.feedback(workspaceId, request)`.

Route shape belongs only in `shared/api/dataServiceClient.ts`.

## 6. UI Rules

- Feedback appears as a secondary action near the content it targets.
- Feedback success can be app-local state.
- Feedback failure is scoped to the feedback component.
- Feedback failure must not clear workspace answer, session answer, evidence, or graph context.
- Validation errors and service unavailable states use normalized error envelopes.

## 7. Acceptance

M4 is API-adapter-ready when:

- workspace answer feedback can submit through the typed wrapper;
- session answer feedback can submit through the typed wrapper;
- feedback failure renders locally and does not erase answer content;
- no correction rules or governance workflow is exposed as product UI.
