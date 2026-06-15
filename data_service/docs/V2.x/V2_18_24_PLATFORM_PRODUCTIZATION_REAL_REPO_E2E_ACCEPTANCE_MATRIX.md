# V2.18-V2.24 真实仓库 E2E 验收矩阵

## 1. 文档目标

本矩阵定义 V2.18-V2.24 每个阶段必须用真实仓库验证的内容，防止只用 mock 或单元测试通过而误判为产品能力完成。

## 2. 验收仓库

| 仓库 | 用途 | 要求 |
| --- | --- | --- |
| `/Users/Zhuanz/Desktop/workspace/data_service` | 主验收仓库 | 每阶段必须跑。 |
| `/Users/Zhuanz/Desktop/workspace/harnessOS` | 大项目/复杂文档/多 Agent 场景 | 涉及大项目、工具发现、增量构建、治理时应跑。 |

## 3. V2.18 Console E2E

| 检查项 | data_service | HarnessOS | 通过标准 |
| --- | --- | --- | --- |
| Console build | required | optional | 生成 console JSON/HTML。 |
| Artifact readback | required | optional | read API 能读回。 |
| Blocker visible | required | required if generated | blocker 不隐藏。 |
| No unpersisted facts | required | required | HTML 中无 artifact 外事实。 |
| XSS/link safety | required | required | HTML escape / link sanitize。 |

## 4. V2.19 Contract E2E

| 检查项 | data_service | HarnessOS | 通过标准 |
| --- | --- | --- | --- |
| Artifact discovery | required | required | 发现主要 V2 artifact families。 |
| Validator run | required | required | 输出 pass/fail/warning。 |
| Schema version | required | required | 新 artifact 必须有 schema_version。 |
| Ref integrity | required | required | artifact_refs 可解析或有 unresolved reason。 |
| Public parity | required | optional | HTTP/MCP/CLI stable fields 一致。 |

## 5. V2.20 MCP Tool Catalog E2E

| 检查项 | data_service | HarnessOS | 通过标准 |
| --- | --- | --- | --- |
| Registry count | required | n/a | catalog count == 当前 registry count。 |
| Tool grouping | required | n/a | 每个 tool 有 group。 |
| Goal guide | required | required | project_overview / coding_task_preparation / review 至少三条链。 |
| Missing tool guard | required | n/a | 不推荐不存在 tool。 |
| Agent readable | required | required | 输出包含 preconditions、outputs、failure_modes。 |

## 6. V2.21 Incremental Build E2E

| 检查项 | data_service | HarnessOS | 通过标准 |
| --- | --- | --- | --- |
| Snapshot A/B | required | required | 修改 fixture 后 snapshot_id 变化。 |
| Diff detection | required | required | changed file 被识别。 |
| Build impact plan | required | required | reused/refreshed/invalidated 非空或有 full rebuild reason。 |
| Cache safety | required | required | unsafe reuse 被拒绝。 |
| Scan budget | required | required | warnings repo-relative。 |

## 7. V2.22 Provider Plugin E2E

| 检查项 | data_service | HarnessOS | 通过标准 |
| --- | --- | --- | --- |
| AST baseline | required | required | mandatory provider ready。 |
| Optional unavailable | required | required | tree-sitter/Jedi/LSP 未配置时 structured unavailable。 |
| Provider output | required | optional | 有 confidence/extractor/evidence。 |
| Health vs execution | required | required | health-known 不等于 execution-ready。 |
| No fake accepted | required | required | unavailable 不得 accepted。 |

## 8. V2.23 Governance E2E

| 检查项 | data_service | HarnessOS | 通过标准 |
| --- | --- | --- | --- |
| Feedback create | required | required | target resolver 通过。 |
| Missing target | required | required | 被拒绝。 |
| Rule approve | required | required | read output 有 applied_rules。 |
| Rule revoke | required | required | applied_rules 消失。 |
| Hash unchanged | required | required | source artifact hash 不变。 |

## 9. V2.24 Production CI E2E

| 检查项 | data_service | HarnessOS | 通过标准 |
| --- | --- | --- | --- |
| Unit layer | required | optional | 命令记录。 |
| Contract layer | required | required | public contract guard。 |
| Artifact layer | required | required | validator gate。 |
| Frontend build | required | n/a | build pass。 |
| Real repo E2E | required | required | 真实仓库结果引用。 |
| Redaction gate | required | required | 无 absolute path / secret / traceback 泄露。 |

## 10. False-Green 拒绝规则

以下情况不能接受：

- mock-only 结果被标为 E2E。
- skipped provider 被标为 accepted。
- Console HTML 生成了 artifact 中没有的事实。
- Tool Catalog 用手写静态清单替代 registry。
- Incremental build 没有 diff 证据却声称复用安全。
- Governance rule 直接改写 source artifact。
- CI skipped 被写成 passed。
