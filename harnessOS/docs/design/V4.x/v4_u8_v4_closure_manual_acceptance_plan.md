# V4-U8 V4 Closure Manual Acceptance Plan

文档状态：V4-U8 收口与人工验收阶段计划。

当前基线：

```text
V4-U7 complete: real provider-backed multi-agent scenario evidence ready for review.
Reality check: PASS 12 / PARTIAL 0 / FAIL 0 / BLOCKED 0
```

允许声明：

```text
V4-U8 complete: V4 dev/local closure package ready for human acceptance.
```

禁止声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

## 目标

V4-U8 不新增 runtime 能力。它只把 V4.1 到 V4-U7 的 dev/local 证据收口成可人工验收、可交给 ChatGPT 审计、可继续进入 V5 规划的 closure package。

## U8A Human Acceptance Package

交付：

```text
docs/design/V4.x/evidence/manual-acceptance/u8-manual-acceptance-report.html
docs/design/V4.x/evidence/manual-acceptance/u8-manual-acceptance-data.json
```

验收：

```text
UX-01 到 UX-12 均有状态、scope、证据链接。
UX-08 / UX-09 / UX-10 指向 provider-backed dev/local evidence。
UX-12 指向真实本地 Markdown 读取和 provider evidence。
HTML 静态可打开，不依赖外部 CDN。
```

## U8B Manual Acceptance Proxy

脚本：

```text
scripts/v4_u8_manual_acceptance_proxy.py
```

脚本只读取现有证据，不启动 workflow，不调用 provider，不执行 mutation。

检查项：

```text
Reality check 是否 PASS 12 / PARTIAL 0。
No False Green claim violation 是否为 0。
redaction 是否 PASS。
gap drawio XML 是否可解析。
UX-08 provider invocation count >= 7。
UX-09 provider invocation count >= 7。
UX-10 provider invocation count >= 12。
UX-12 scanner_actual_read_count > 0。
UX-12 provider invocation count > 0。
```

## U8C Closure Gate

通过条件：

```text
./.venv/bin/python scripts/v4_u8_manual_acceptance_proxy.py PASS
./.venv/bin/python scripts/v4_unified_reality_check_audit.py PASS
./.venv/bin/python -m pytest tests/test_v4_*.py -q PASS
./.venv/bin/python -m pytest -q PASS
xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio PASS
```

## 下一阶段建议

V4-U8 后不建议继续把 production hardening 塞入 V4。建议进入 V5 planning，单独处理：

```text
production auth / tenant isolation
production token lifecycle
production secret manager
production observability and audit export
production external app onboarding
real Agent executor
production controlled executor
full Web Studio productization
distributed multi-Agent runtime
```

## No False Green

V4-U8 只能证明 V4 dev/local closure package ready for human acceptance。它不证明生产级、完整 Studio、Agent executor、controlled executor 或 unrestricted multi-Agent orchestration。
