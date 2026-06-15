# V2.25-V2.30 Architecture Intent Closure Audit Report

审计日期：2026-06-10
范围：Phase 91-96B
结论：核心 artifact 链路 accepted；公共 HTTP/MCP/CLI 合同 accepted

## 1. 已完成能力

| Phase | 能力 | 状态 |
| --- | --- | --- |
| 91 | Architecture Source Model | accepted |
| 92 | Diagram-to-Claim Parser | accepted |
| 93 | Code Proof Graph | accepted |
| 94 | Intent Inference Engine | accepted |
| 95 | Diagram-to-Code Verification | accepted |
| 96 | Report / Context / Governance artifact closure | accepted |
| 96B | HTTP/MCP/CLI public contract | accepted |

## 2. 真实仓库验收

已使用真实仓库：

- `/Users/Zhuanz/Desktop/workspace/data_service`
- `/Users/Zhuanz/Desktop/workspace/harnessOS`

最终 Phase 96 E2E 结果：

| 仓库 | verification | accepted | report nodes | context recommendations | hash gate | path leak |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| data_service | 11362 | 9040 | 69 | 8 | pass | false |
| HarnessOS | 6766 | 5337 | 69 | 8 | pass | false |

Phase 96B 公共合同 E2E 结果：

| 仓库 | verification | intent candidates | report nodes | HTTP/MCP parity | HTTP/CLI parity | path leak |
| --- | ---: | ---: | ---: | --- | --- | --- |
| data_service | 11442 | 9 | 69 | pass | pass | false |
| HarnessOS | 6766 | 9 | 69 | pass | pass | false |

## 3. 测试结果

回归子集：

```text
22 passed
```

全量后端测试：

```text
PYTHONPATH=backend python3 -m pytest -q backend/tests
```

结果：

```text
479 passed, 617 warnings in 229.24s
```

覆盖：

- V2.18-V2.24 platform productization regression。
- Phase 91-96 focused tests。
- Phase 96B public contract focused test。
- Public surface guard、MCP console contract、CLI inventory baseline。

## 4. PRD 偏差审计

无 fatal 偏差。

明确偏差/限制项：

- 当前 HTTP/MCP/CLI public contracts 已补齐并验收通过。
- 当前 accepted diagram-code verification 仍是静态证据对齐，不是 runtime call graph 或完整设计意图恢复。
- HarnessOS 大仓库 E2E 用时约 171 秒，后续产品化应继续优化索引与增量构建。

## 5. False-Green 审计

| 场景 | 结果 |
| --- | --- |
| token-only accepted | 未发现 |
| drawio 节点直接变 code fact | 未发现 |
| runtime descriptor 写成 runtime observed | 未发现 |
| inferred intent 写成 confirmed | 未发现 |
| HTML/Mermaid 引入新事实 | 未发现 |
| public path leak | 未发现 |
| 未实现 public contract 却 accepted | 未发生；Phase 96B 实现后才改为 accepted |

## 6. 后续建议

建议下一阶段优先补齐：

1. Verification 索引缓存与增量构建。
2. 报告可读性增强和多图可视化。
3. 更细粒度的跨语言证据适配器。

## 7. 关闭结论

V2.25-V2.30 的核心 artifact 能力和 Architecture Intent 公共 Agent-callable surface 均可以关闭为 accepted。

该结论仍限定在证据分层、静态事实对齐、文档/diagram/code verification 与 read-time governance overlay；不代表 full call graph、runtime tracing、data flow、type inference 或完整人类设计意图恢复。
