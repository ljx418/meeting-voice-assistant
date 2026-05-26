# V4.0-W External App Production Onboarding Follow-up Design Plan

阶段定位：V4.0-W 只做 external app production onboarding follow-up design，不实现 production onboarding、tenant provisioning、app registration runtime、quota route、customer offboarding 或 data export/delete。

允许完成声明：

```text
V4.0-W complete: external app production onboarding follow-up design ready for review.
```

## PR Slices

1. 新增机器可读 onboarding gap matrix，覆盖 app registration、domain verification、origin allowlist、tenant provisioning、service account lifecycle、token rotation/revocation、SDK/API policy、quota/rate limit、abuse detection、offboarding、data export/deletion 和 support runbook。
2. 明确 V3.5 SDK/BFF/Embed 仍是 dev/local baseline。
3. 新增 forbidden route scan，确保没有 `/production/onboarding`、tenant provision、quota、customer offboarding 或 data export/delete route。
4. 同步 V4.0 core docs 和 No False Green。

## Test Plan

新增 `tests/test_v4_0_production_external_app_onboarding_design.py` 覆盖合同、required gaps、dev/local boundary 和 forbidden route scan。

## Risk Controls

W 阶段不支持生产客户接入，不做 production app onboarding runtime。

## Completion Evidence Format

Completion note 必须记录 allowed claim、external app gap result、route scan result、validation command results 和 No False Green statement。
