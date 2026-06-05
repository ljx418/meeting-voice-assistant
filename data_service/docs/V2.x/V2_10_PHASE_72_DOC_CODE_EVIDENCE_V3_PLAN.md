# V2.10 Phase 72 Document-Code Evidence v3 Plan

## Objective

Align architecture document claims with V2.10 code bindings without conflating document intent and code evidence.

## Development Plan

Consume:

- V2.7 document registry and claims;
- V2.7/V2.8 document-code alignment where available;
- V2.10 adapter attempts and AST bindings;
- V2.10 accepted pattern evidence.

Produce:

- document-claim to code-binding alignment v3;
- code binding coverage summary;
- missing-code-evidence blockers;
- code-not-documented findings.

## Match Status

```text
matched
weak_match
missing_code_evidence
code_not_documented
conflict
needs_review
```

Matched requires:

- document evidence;
- code evidence;
- accepted V2.10 binding;
- confidence >= 0.80;
- non-token-only match strategy.

Weak match:

- label/token/path similarity only;
- document-only claim;
- low-confidence concept relation.

## Artifact Outputs

```text
architecture/v2_10/doc_code_evidence_v3.jsonl
architecture/v2_10/doc_code_evidence_summary.json
```

## Acceptance Plan

Assertions:

- matched rows include both `document_evidence_refs` and `code_evidence_refs`;
- weak matches are never accepted;
- document/drawio labels cannot become code evidence;
- code_not_documented count is reported even if zero;
- HarnessOS design docs remain target/document facts unless code evidence is found.

False-green rejection:

- copied drawio architecture treated as code fact;
- document claim accepted without line-level code evidence;
- token-only match accepted;
- missing code evidence hidden from report.
