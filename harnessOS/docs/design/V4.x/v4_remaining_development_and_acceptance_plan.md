# V4 Remaining Development And Acceptance Plan

文档状态：V4-U9 后的 V4 剩余开发与验收计划。本文用于外部审计和人工验收，不新增 V4 功能范围。

## 0. R 阶段性质说明

R0-R3 are non-feature closure gates.

They may fix documentation, links, evidence packaging, wording, and claim alignment.

They must not add runtime behavior, Agent execution authority, controlled executor scope, production auth, production external app onboarding, or full Web Studio capability.

它们只允许修复：

```text
documentation
links
evidence packaging
wording
claim alignment
```

它们不得新增：

```text
runtime behavior
Agent execution authority
controlled executor scope
production auth
production external app onboarding
full Web Studio capability
```

## 1. 当前基线

当前允许声明：

```text
V4-U9 complete: V4 dev/local final human acceptance and V5 handoff package ready for review.
```

当前仍禁止声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

当前 reality-check：

```text
PASS: 12
PARTIAL: 0
FAIL: 0
BLOCKED: 0
claim violations: 0
redaction: PASS
```

## 2. V4 剩余开发判断

V4 功能开发应收口，不再继续新增功能阶段。

原因：

1. V4.1 到 V4.6 的 Headless-first dev/local 主线已完成。
2. V4-U5 到 V4-U9 已完成统一体验证据、人工验收代理、最终人工验收和 V5 移交包。
3. UX-01 到 UX-12 已全部有可审计证据。
4. 继续在 V4 中新增 production auth、Agent executor、controlled executor 或 production external app support 会造成规格漂移。

因此，V4 剩余事项只包括：

```text
V4-R0 文档审计与口径冻结
V4-R1 人工验收复核
V4-R2 勘误修复
V4-R3 V5 进入前门禁
```

这些阶段不允许新增 runtime 能力，不允许扩展 Agent 执行权限，不允许新增 production 能力。

## 3. V4-R0 文档审计与口径冻结

目标：

确认 V4 文档没有把 dev/local evidence 写成 production-ready，也没有把 report-only、transcript-only、deterministic evidence 写成 runtime-backed 能力。

输入：

```text
docs/design/V4.x/00_README.md
docs/design/V4.x/v4_x_headless_current_gap_analysis.md
docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
docs/design/V4.x/v4_remaining_development_audit_for_chatgpt.md
docs/design/V4.x/v4_u9_final_human_acceptance_and_v5_handoff_completion_note.md
docs/design/V4.x/v4_target_architecture_after_u9.md
docs/design/V4.x/v4_target_spec_prd_after_u9.md
docs/design/V4.x/v4_target_acceptance_plan_after_u9.md
docs/design/V4.x/v4_document_review_for_chatgpt_after_u9.md
docs/design/V4.x/evidence/final-human-acceptance/u9-final-acceptance-data.json
```

验收标准：

1. 只允许使用 V4-U9 allowed claim。
2. forbidden claims 只出现在 forbidden / no false green 上下文。
3. V5 planning brief 不改变 V4 completion claim。
4. V4.x gap markdown 和 drawio 都指向 U9。
5. drawio XML valid。
6. `docs/design/V4.x/00_README.md` 是 V4.x canonical index。
7. `docs/design/V4.x/v4_remaining_development_and_acceptance_plan.md` 是 V4-U9 后剩余事项唯一控制计划。
8. `docs/design/V4.x/v4_remaining_development_audit_for_chatgpt.md` 与 U9 状态一致。
9. V4.x gap markdown / drawio XML valid。
10. 旧版 V4.6、U5A、U5B、U6 之前的审计包如仍存在，必须标记 historical 或明确不是当前控制文件。
11. UX-01 到 UX-12 的 PASS 不得抹平 `evidence_scope`。
12. `v4_target_architecture_after_u9.md`、`v4_target_spec_prd_after_u9.md`、`v4_target_acceptance_plan_after_u9.md` 和 `v4_document_review_for_chatgpt_after_u9.md` 均保持 closure-only，不提出新增 V4 feature。

验收命令：

```bash
./.venv/bin/python scripts/v4_unified_reality_check_audit.py
xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
./.venv/bin/python - <<'PY'
import json
json.load(open("docs/design/V4.x/evidence/final-human-acceptance/u9-final-acceptance-data.json", encoding="utf-8"))
print("u9 json parse PASS")
PY
```

通过声明：

```text
V4-R0 complete: V4 documentation boundary frozen for human audit.
```

## 4. V4-R1 人工验收复核

目标：

用户或外部审计者打开静态 HTML 和 JSON 证据，复核 UX-01 到 UX-12 的状态、证据范围和边界声明。

最小人工验收路径：

1. 打开最终人工验收报告。
2. 检查 UX-01 到 UX-12 是否全部 PASS。
3. 检查每个 UX 的 evidence_scope 是否准确。
4. 打开 reality-check 看板。
5. 打开 U8 人工验收报告。
6. 检查 UX-08 / UX-09 / UX-10 是否限定为 dev/local provider-backed。
7. 检查 UX-12 是否记录 real LLM provider、本地 Markdown 读取和 summary artifact。
8. 检查 Evidence Chain 是否只读。
9. 检查 no false green 和 forbidden claims。
10. 检查 V5 planning brief 是否只是 future planning。
11. 检查 `u9-final-acceptance-report.html` 可打开。
12. 检查 `u9-final-acceptance-data.json` 可解析。
13. 检查 UX-01 到 UX-12 都有 `status`、`evidence_scope`、`evidence_refs`。
14. 检查 evidence links 不缺失。
15. 检查 PRD main path 与 evidence mapping 一致。
16. 检查 false-green audit 为 PASS。
17. 检查 redaction 为 PASS。
18. 检查 forbidden claims 只出现在 forbidden/no false green 上下文。
19. 检查 provider-backed dev/local 不被写成 production-ready。
20. 检查 real_runtime dev/local 不被写成 distributed runtime。
21. 检查 Agent Workflow Builder 不被写成 Agent executor。
22. 检查 Evidence Chain / Review Console 不被写成 execution panel。

需要打开的文件：

```text
docs/design/V4.x/evidence/final-human-acceptance/u9-final-acceptance-report.html
docs/design/V4.x/evidence/final-human-acceptance/u9-final-acceptance-data.json
docs/design/V4.x/evidence/final-human-acceptance/u9-prd-spec-review.md
docs/design/V4.x/evidence/final-human-acceptance/u9-false-green-audit.md
docs/design/V4.x/v4_final_human_acceptance_confirmation.md
docs/design/V4.x/evidence/unified-experience/reality-check/index.html
docs/design/V4.x/evidence/unified-experience/reality-check/audit-data.json
docs/design/V4.x/evidence/manual-acceptance/u8-manual-acceptance-report.html
docs/design/V4.x/evidence/manual-acceptance/u8-manual-acceptance-data.json
docs/design/V5.x/v5_0_production_productization_planning_brief.md
```

通过条件：

1. 人工能打开 U9 HTML。
2. UX-01 到 UX-12 证据链接可追溯。
3. 无 FAIL / BLOCKED。
4. 无 redaction failure。
5. 无 forbidden claim violation。
6. 审计者接受 V4 dev/local 边界。
7. `evidence_scope` 保留且可逐 UX 复核。
8. provider-backed 和 real_runtime 均带 dev/local 边界。

通过声明：

```text
V4-R1 complete: V4 final human acceptance reviewed.
```

## 5. V4-R2 勘误修复

目标：

只修复人工验收或 ChatGPT 审计中发现的文档错误、链接错误、证据引用错误、claim 口径错误。

允许修复：

```text
错别字
错误路径
坏链接
文档状态不一致
outdated document status
wording inconsistency
claim wording
drawio XML formatting
evidence path typo
README indexing errors
deprecated/historical labels
drawio 文案不同步
completion note 与实际测试结果不一致
false-green wording
敏感词扫描误触发
```

禁止修复：

```text
新增 Agent executor
新增 controlled executor
新增 production auth
新增 production tenant control plane
新增 production external app support
新增 full Web Studio 功能
新增 runtime mutation path
new runtime behavior
new Agent executor behavior
new controlled executor behavior
new production auth
new production external app onboarding
new full Web Studio feature
```

R2 不得改变 UX case 的 `status` 或 `evidence_scope`，除非只是修正指向已存在证据的错误链接。

验收命令：

```bash
./.venv/bin/python scripts/v4_unified_reality_check_audit.py
./.venv/bin/python scripts/v4_u9_final_acceptance.py
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
./.venv/bin/python -m pytest tests/test_v4_*.py -q
xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
./.venv/bin/python - <<'PY'
import json
json.load(open("docs/design/V4.x/evidence/final-human-acceptance/u9-final-acceptance-data.json", encoding="utf-8"))
print("u9 json parse PASS")
PY
```

通过声明：

```text
V4-R2 complete: V4 acceptance errata resolved without scope expansion.
```

## 6. V4-R3 V5 进入前门禁

目标：

确认 V4 不再承载 production hardening，把 production auth、provider lifecycle、audit export、Agent executor safety gate、external app onboarding 等工作移交 V5。

V5 候选方向：

```text
V5-0 Production Productization Planning
V5-1 Production Auth / Tenant Boundary
V5-2 Production Provider / Credential Lifecycle
V5-3 Production Observability / Audit Export
V5-4 Real Agent Executor Design and Safety Gate
V5-5 Production External App Onboarding
```

V5 entry checklist:

V5 可继承：

```text
V4 Headless workflow core dev/local evidence
Mission Console / Blueprint / Runtime Report / Review Console / Evidence Chain experience baseline
UX-01 到 UX-12 evidence inventory
Runtime Capability Matrix
WorkflowSpec Registry
V4 false-green audit result
V4 redaction result
```

No False Green: V5 不得继承为已完成：

```text
production auth
production tenant isolation
production token lifecycle
production credential lifecycle
production observability / audit export
production external app onboarding
Agent executor ready
production controlled executor ready
complete Workflow Studio
distributed multi-Agent runtime
production-ready external app support
```

通过条件：

1. V4-U9 final acceptance remains PASS。
2. V5 brief 明确 planning only。
3. V5 不反向修改 V4 allowed claim。
4. V5 开始前形成单独 V5 PRD、gap、acceptance、No False Green guard。
5. V5 entry checklist 已完成并被外部审计接受。

通过声明：

```text
V4-R3 complete: V4 closed and V5 entry gate ready for planning.
```

## 7. R 阶段统一验收命令

R0-R3 任一阶段结束后都必须执行：

```bash
./.venv/bin/python scripts/v4_unified_reality_check_audit.py
xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
./.venv/bin/python -m pytest tests/test_v4_u9_final_acceptance.py -q
./.venv/bin/python -c 'import json; json.load(open("docs/design/V4.x/evidence/final-human-acceptance/u9-final-acceptance-data.json", encoding="utf-8")); print("u9 json parse PASS")'
```

No False Green / forbidden claim scan:

```bash
./.venv/bin/python scripts/v4_unified_reality_check_audit.py
jq ".claims_audit.violation_count" docs/design/V4.x/evidence/unified-experience/reality-check/audit-data.json
```

验收通过条件：

```text
reality-check: 12 PASS / 0 PARTIAL / 0 FAIL / 0 BLOCKED
claim violations: 0
redaction: PASS
drawio XML: valid
U9 final acceptance tests: PASS
U9 JSON parse: PASS
```

## 8. 全局停止条件

如果出现以下任一情况，停止并请求人工决策：

```text
Spec Drift Risk = HIGH
False Green Risk = HIGH
reality-check 出现 FAIL 或 BLOCKED
claim guard 出现 forbidden claim violation
redaction audit FAIL
需要新增 runtime mutation path
需要 Agent executor
需要 production auth
需要 production controlled executor
需要 production external app support
any forbidden completion claim outside forbidden/no-false-green context
U9 allowed claim missing or changed
V5 brief retroactively upgrades V4 to production-ready
u9-final-acceptance-data.json cannot parse
u9-final-acceptance-report.html missing
drawio XML invalid
evidence_scope removed from UX cases
V4 remaining plan proposes new runtime/Agent/production features
```

## 9. 需要 ChatGPT 审计的问题

```text
1. 是否同意 V4 功能开发应在 U9 后收口？
2. V4-R0 到 V4-R3 是否只是验收、勘误和 V5 交接，而非新功能开发？
3. 是否存在把 dev/local evidence 写成 production-ready 的风险？
4. 是否存在把 Agent Workflow Builder 写成 Agent executor 的风险？
5. 是否存在把 Review Console / Evidence Chain 写成执行面板的风险？
6. 是否存在把 V5 planning 反向写入 V4 completion claim 的风险？
7. 当前需要人工打开的 evidence 文件是否足以支撑 V4 final human acceptance？
8. 是否应该在 V5 单独建立 production auth、credential lifecycle、audit export 和 Agent executor safety gate？
9. V4 目标架构、目标规格 PRD、目标验收计划是否均保持 U9 后 closure-only？
```

## 10. 最终判断

V4 剩余开发大纲不是继续新增功能，而是：

```text
冻结口径
人工验收
勘误修复
V5 移交
```

如果人工验收通过，V4 应保持收口，不再新增 V4 功能阶段。

After V4-U9, V4 remains closed.

R0-R3 closure work may proceed.

V5 planning may proceed only after R0-R3 pass.

人工验收确认文件：

```text
docs/design/V4.x/v4_final_human_acceptance_confirmation.md
```

该文件记录最终人工复核接受结论：V4 人工验收通过，V4 feature development closed，V4-R0/R1/R2/R3 closure gates accepted，V5 planning may proceed。
