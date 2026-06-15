# V2.43 Phase 120 drawio / Document Semantics Acceptance Plan

## 1. 验收定义

Phase 120 通过条件：Markdown/drawio semantic claims 和 relations 落盘、可读回、三端一致，且不把 document claims 混入 code facts。

## 2. 自动化测试

Focused:

```text
backend/tests/test_v2_43_document_semantics.py
```

必须验证：

- Markdown acceptance / non-goal / stop condition 可抽取。
- drawio page / lane / group / edge / gate 可抽取。
- drawio cell id 或 markdown line range 可追踪。
- HTML/Mermaid escaping 通过。
- document claim 不进入 code fact artifact。
- HTTP/MCP/CLI parity。

## 3. 真实项目 E2E

- data_service：V2.x docs semantic claims 非空。
- HarnessOS：docs/design 中 drawio/Markdown semantic claims 非空或 structured blocker。
- codexPat：文档少时输出 attempt + blocker，不伪造完成。

## 4. False-Green Rejection

拒绝：

- drawio claim 变成 code fact。
- Mermaid/HTML 中出现未落盘 claim。
- raw label 注入图表语法。
- 没有文档仍标 accepted。
