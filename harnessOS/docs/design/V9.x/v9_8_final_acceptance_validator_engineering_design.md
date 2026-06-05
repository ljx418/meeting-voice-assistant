# V9-8 Final Acceptance Validator Engineering Design

文档状态：V9-8 engineering design / planned only。

## 1. Purpose

V9-8 validator aggregates stage evidence and decides whether the final V9 ready-for-review claim can be emitted. It must reject planning-only evidence for runtime stages.

Current rejection fixture:

```text
docs/design/V9.x/fixtures/evidence/v9_8_reject_planning_only_sample.json
```

## 2. Discovery Rules

Expected evidence roots:

```text
docs/design/V9.x/evidence/v9-0/
docs/design/V9.x/evidence/v9-1/
docs/design/V9.x/evidence/v9-2/
docs/design/V9.x/evidence/v9-3/
docs/design/V9.x/evidence/v9-4/
docs/design/V9.x/evidence/v9-5/
docs/design/V9.x/evidence/v9-6/
docs/design/V9.x/evidence/v9-7/
```

Each root must contain:

```text
evidence-package.json
result-summary.md
claim-scan.json
redaction-scan.json
test-results.json
```

## 3. Validation Algorithm

```text
load evidence package for every stage.
validate package schema.
verify runtime_backed requirements by stage.
verify high-risk human_decision_refs.
verify no FAIL or BLOCKED.
verify PARTIAL has proceed decision.
run No False Green claim scan.
run redaction scan.
validate drawio XML.
generate final dashboard.
```

The validator must treat `docs/design/V9.x/fixtures/evidence/v9_8_reject_planning_only_sample.json` as BLOCKED, not PASS.

## 4. Rejection Cases

```text
missing stage evidence package
planning docs counted as runtime evidence
missing human_decision_ref for high-risk stage
runtime_backed=false for runtime stage
forbidden claim outside allowed context
raw secret / raw prompt / raw artifact content
drawio XML invalid
```

## 5. Final Output

```text
v9-final-acceptance-dashboard.html
v9-final-acceptance-data.json
v9-final-claim-scan.md
v9-final-redaction-scan.md
v9-final-result-summary.md
```
