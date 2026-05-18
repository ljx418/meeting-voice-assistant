# Assessment Service Contract Roadmap

Date: 2026-05-18

## 1. Purpose

Assessment Studio is a future ResearchNotebook product area for generating interview-style questions from imported technical knowledge and evaluating user mastery.

Assessment is not Quality Governance. It should not be implemented through correction rules, correction plans, or feedback review routes.

## 2. Version Roadmap

### V1.2 Dependency: Source Extraction And Evidence Model

Assessment requires:

- normalized `Source`;
- normalized `DocumentUnit`;
- normalized `EvidenceSpan`;
- stable `evidence_refs`;
- source-level fallback evidence.

No assessment feature should ship before generated questions can be grounded in evidence.

### V1.3: Question Generation Contract

Expected service capability:

- question generation from selected sources;
- topic selection;
- difficulty selection;
- question type selection;
- each generated question includes `evidence_refs`;
- generated output includes stable `question_id` or equivalent reference.

Future domain:

- `Question`.

Frontend behavior:

- create assessment draft from selected sources/topic/difficulty/question type;
- display every question with evidence affordance;
- show unsupported state if evidence-backed generation is unavailable.

### V1.4: Attempt Scoring Contract

Expected service capability:

- submit user answers for an assessment attempt;
- return score;
- return per-question feedback;
- return weak points;
- return review source references;
- preserve attempt identity.

Future domain:

- `Assessment`;
- `Attempt`.

Frontend behavior:

- answer questions;
- submit attempt;
- render score, feedback, weak points, and review sources;
- link review sources back to evidence navigation.

### V1.5: Mastery Profile Contract

Expected service capability:

- aggregate attempts into mastery profile;
- identify knowledge areas and weak points;
- link mastery signals back to source/evidence;
- support repeated assessment over time.

Future domain:

- `MasteryProfile`.

Frontend behavior:

- show mastery overview;
- show weak point drilldown;
- recommend review sources;
- avoid claiming learning state without evidence-backed attempt data.

## 3. Minimum Domain Objects

Future contracts should define:

- `Question`: prompt, type, difficulty, expected answer/rubric, `evidence_refs`;
- `Assessment`: selected sources, topic, generated question set, creation metadata;
- `Attempt`: user answers, score, feedback, weak points, review sources;
- `MasteryProfile`: aggregated mastery signals and source-linked review recommendations.

## 4. Frontend Constraints

ResearchNotebook V1.0 must not:

- ship mock question generation as product capability;
- ship mock scoring as product capability;
- present mastery profile as ready;
- mix assessment with Quality Governance;
- generate questions without evidence references.

`features/assessment/` may exist only as a future shell in V1.0:

- type drafts;
- route placeholders;
- UI prototypes;
- documentation.

It must not contain production-facing mock generation, scoring, or mastery logic.

## 5. Acceptance Criteria

Assessment work can move from roadmap to implementation when:

- `data_service` exposes public assessment routes or equivalent schema;
- every generated question includes `evidence_refs`;
- attempt scoring returns score, feedback, weak points, and review sources;
- frontend contract tests cover evidence-backed generation and unsupported states;
- assessment remains separate from Quality Governance in navigation, data model, and route mapping.
