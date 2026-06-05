# V9 Automation-Assisted Development Policy

文档状态：V9 P0 automation development policy / required before automated V9 implementation。

## 1. Purpose

本文件约束使用 AI / 自动化工具开发 V9 本身的边界，避免自动化开发过程绕过 V9 的安全原则。

## 2. Allowed Automation

AI / automation may:

```text
generate plan
generate diff proposal
generate test proposal
generate evidence draft
run read-only analysis
run approved tests
draft documentation
summarize audit findings
```

## 3. Forbidden Automation

AI / automation must not:

```text
auto commit
auto push
auto deploy
apply unreviewed patch
apply patch without explicit human review acceptance
bypass human review
commit, push, deploy, or mark review as approval
write production runtime truth
read secrets
count planning docs as runtime evidence
issue high-risk human decision
issue HumanAuthorizationRef as source=agent
```

## 4. Required Evidence

Automated development evidence must record:

```text
tool_name
actor_type
source
workspace_scope
diff_refs
test_refs
human_review_refs
redaction_status
claim_scan_status
audit_ref
```

## 5. Stop Conditions

```text
automation commits without human approval.
automation pushes or deploys.
automation reads secret.
automation applies patch without review.
automation marks planning docs as runtime evidence.
```
