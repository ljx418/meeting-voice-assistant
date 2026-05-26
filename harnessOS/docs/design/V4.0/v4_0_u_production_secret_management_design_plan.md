# V4.0-U Production Secret Management Follow-up Design Plan

阶段定位：V4.0-U 只做 production secret management follow-up design，不实现 production secret manager、secret admin route、vault integration、token rotate/revoke 或 audit export。

允许完成声明：

```text
V4.0-U complete: production secret management follow-up design ready for review.
```

## PR Slices

1. 新增机器可读 secret boundary matrix，覆盖 capability token、subscription token、connector secret、external LLM key、upstream signed URL 和 raw prompt。
2. 固化 DTO、DOM、event payload、audit summary 均不得暴露 secret/raw 字段。
3. 固化 future executor sandbox 只能读取 redacted BFF DTO，不能访问 raw payload 或 secret store。
4. 新增 forbidden route scan，确保没有 `/secret`、`/secrets`、secret admin、token lifecycle 或 audit export route。
5. 同步 V4.0 核心文档并记录 No False Green。

## Test Plan

新增 `tests/test_v4_0_production_secret_management_design.py` 覆盖合同、secret matrix、sandbox boundary、forbidden route scan 和 production secret manager false claims。

## Risk Controls

U 阶段不实现任何 secret retrieval/write/admin path。secret management 仍是 production blocking gap。

## Completion Evidence Format

Completion note 必须记录 allowed claim、forbidden claims、secret boundary result、sandbox boundary result、route scan result、validation command results 和 No False Green statement。
