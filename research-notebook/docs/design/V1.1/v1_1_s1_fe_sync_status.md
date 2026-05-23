# ResearchNotebook V1.1-S1-FE Sync Status

文档状态：S1-FE session browser smoke 已重新验证；准备进入 V1.1-S2 All-Source-Type Contract Discovery。
日期：2026-05-23。

## Summary

S1-FE 已把 session answer citation 接入现有 Source Preview Drawer / DocumentUnit / EvidenceSpan 高亮路径，并通过真实浏览器 smoke。

当前可声明：

```text
ResearchNotebook session precise evidence navigation is browser-smoke-ready for data_service-supported text-source session query citations carrying source_id + unit_id + evidence_id.
```

不得扩大为：

- all-session precise navigation ready
- all-source-type precise backjump ready
- all-source-type source trace ready
- multi-format ingestion ready

## Verified Commands

```text
npm run check
npm run smoke:v1.1-s1-session
npm run smoke:v1.1-s1-fe-browser
```

结果：

| Command | Result |
| --- | --- |
| `npm run check` | PASS |
| `npm run smoke:v1.1-s1-session` | PASS, `API_SMOKE_READY` |
| `npm run smoke:v1.1-s1-fe-browser` | PASS, `BROWSER_SMOKE_READY` |

## Latest Smoke Evidence

S1 API smoke:

```text
workspace_id: rn-v11-s1-session-1779552117955-workspace
source_id: src_103b26d7f9363bae
session_id: ksess_a92bf2adc1fe348a
session build: succeeded
session query evidence shape: HAS_EVIDENCE_SPAN_IDS
unit detail resolution: PASS
EvidenceSpan resolution: PASS
```

S1-FE browser smoke:

```text
workspace_id: rn-v11-s1-fe-session-1779552117975-workspace
source_id: src_730f2fb42bc6a574
session_id: ksess_369913602193cc25
unit_id: unit_5b52cd7d1a9a762b
evidence_id: ev_f4b88ee55adf37a5
session citation render: PASS
EvidenceSpan highlight visible: PASS
cleanup: PASS
```

## Fixture / Artifact Hygiene

S1 fixtures:

```text
fixtures/real/v1_1/session-precise-navigation/
fixtures/real/v1_1/session-precise-navigation-browser/
```

Browser screenshot artifact:

```text
.smoke-artifacts/v1_1_s1_fe_session_browser/1779552117975/session-evidence-highlight.png
```

The screenshot stays under `.smoke-artifacts/` and must not be committed.

## Next Phase Audit

Next phase:

```text
V1.1-S2 All-Source-Type Contract Discovery
```

S2 must start from contract discovery only. It must not implement multi-format UI, frontend parser logic, or all-source-type ready claims.

S2 should classify each candidate source type as:

- PASS
- LIMITED_PASS
- UNSUPPORTED
- NOT_READY
- BLOCKED_BY_BACKEND_CONTRACT

Recommended S2 audit documents:

- `docs/design/V1.1/v1_1_s2_all_source_type_contract_discovery.md`
- `docs/design/V1.1/v1_1_current_gap_analysis.md`
- `docs/design/V1.1/v1_1_current_gap_analysis.drawio`
- `docs/design/V1.1/feature-route-matrix.md`
- `docs/design/V1.1/capability-manifest-contract.md`
- `docs/design/V1.1/source-preview-contract.md`
- `docs/design/V1.1/document-unit-navigation-contract.md`
- `docs/design/V1.1/evidence-navigation-contract.md`
- `docs/design/V1.1/00_README.md`
