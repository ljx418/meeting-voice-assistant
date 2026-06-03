# V4 Target Acceptance Plan After U9

文档状态：V4-U9 后的 V4 目标验收计划冻结版。本文用于人工验收和外部审计，不新增 V4 功能范围。

## 1. Acceptance Baseline

当前允许声明：

```text
V4-U9 complete: V4 dev/local final human acceptance and V5 handoff package ready for review.
```

V4-U9 后的验收目标不是新增能力，而是确认 V4 dev/local evidence、claim guard、redaction 和 V5 handoff 边界一致。

## 2. Required Evidence

Core evidence:

```text
docs/design/V4.x/evidence/final-human-acceptance/u9-final-acceptance-report.html
docs/design/V4.x/evidence/final-human-acceptance/u9-final-acceptance-data.json
docs/design/V4.x/evidence/final-human-acceptance/u9-prd-spec-review.md
docs/design/V4.x/evidence/final-human-acceptance/u9-false-green-audit.md
docs/design/V4.x/evidence/unified-experience/reality-check/index.html
docs/design/V4.x/evidence/unified-experience/reality-check/audit-data.json
docs/design/V4.x/evidence/manual-acceptance/u8-manual-acceptance-report.html
docs/design/V4.x/evidence/manual-acceptance/u8-manual-acceptance-data.json
docs/design/V5.x/v5_0_production_productization_planning_brief.md
```

UX evidence:

```text
UX-01 to UX-12 result-summary.md files
UX-08 / UX-09 / UX-10 provider-backed runtime-result.json files
UX-12 local-document-workflow-result.json
UX-12 quality_report.json
UX-12 evidence_chain.json
```

## 3. Manual Acceptance Steps

1. Open `u9-final-acceptance-report.html`.
2. Parse `u9-final-acceptance-data.json`.
3. Confirm UX-01 to UX-12 are PASS.
4. Confirm every UX case preserves `status`, `evidence_scope`, and `evidence_refs`.
5. Confirm PRD main path maps to evidence refs.
6. Confirm false-green audit is PASS.
7. Confirm redaction is PASS.
8. Confirm provider-backed dev/local evidence is not described as production-ready.
9. Confirm real_runtime dev/local evidence is not described as distributed runtime.
10. Confirm V5 brief is planning-only.
11. Confirm Agent Workflow Builder is not described as Agent executor.
12. Confirm Evidence Chain and Review Console are not described as execution panels.

## 4. Automated Acceptance Commands

```bash
./.venv/bin/python scripts/v4_unified_reality_check_audit.py
xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
./.venv/bin/python -c 'import json; json.load(open("docs/design/V4.x/evidence/final-human-acceptance/u9-final-acceptance-data.json", encoding="utf-8")); print("u9 json parse PASS")'
```

Expected results:

```text
reality-check: 12 PASS / 0 PARTIAL / 0 FAIL / 0 BLOCKED
claim violations: 0
redaction: PASS
drawio XML: valid
U9 final acceptance tests: PASS
U9 JSON parse: PASS
```

## 5. Stop Conditions

Stop and request human decision if:

```text
any UX case becomes FAIL or BLOCKED
any forbidden completion claim appears outside forbidden/no-false-green context
U9 allowed claim is missing or changed
V5 brief upgrades V4 into production readiness
u9-final-acceptance-data.json cannot parse
u9-final-acceptance-report.html is missing
drawio XML is invalid
evidence_scope is removed from UX cases
UX status or evidence_scope changes during R2 except broken-link correction to existing evidence
R0-R3 plan proposes new runtime, Agent, controlled executor, or production feature
```

## 6. Completion Decision

If all checks pass:

```text
After V4-U9, V4 remains closed.
R0-R3 closure work may proceed.
V5 planning may proceed only after R0-R3 pass.
```

No False Green：以下完成声明仍然禁止：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```
