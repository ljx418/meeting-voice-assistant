# V2.16 测试与审计计划

## 1. 文件定位

本文件定义 V2.16 Phase 76-82 的统一测试、真实仓 E2E、审计和假验收拒绝策略。

它是以下文件的执行补充：

- `V2_16_TARGET_PRD.md`
- `V2_16_TARGET_ARCHITECTURE.md`
- `V2_16_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `V2_16_PHASE_76_82_DETAILED_IMPLEMENTATION_PACKAGE.md`
- `V2_16_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md`
- `V2_16_FULL_COVERAGE_MATRIX.md`

## 2. 测试分层

V2.16 测试分为 7 层：

| 层级 | 目标 | 示例 |
| --- | --- | --- |
| Unit tests | 验证 model、builder、merge、redaction 等单元逻辑。 | provider status classification。 |
| Artifact tests | 验证 artifact 落盘、schema、readback、一致性。 | `capability_registry.json` schema。 |
| Contract tests | 验证 HTTP/MCP/CLI stable fields 一致。 | schema_version、counts、error code。 |
| Real repo E2E | 使用真实 `data_service` 和 HarnessOS / 替代大项目。 | provider matrix、workbench、patch preview。 |
| Safety tests | 验证 default-deny、redaction、no source mutation。 | non-profile command blocked。 |
| False-green tests | 验证不能把 skipped/unavailable/weak evidence 写成 accepted。 | provider health-only not accepted。 |
| Closure tests | 验证 coverage matrix 和 audit report 可追溯。 | accepted row has evidence。 |

## 3. 真实仓输入

主仓：

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

大项目泛化仓：

```text
/Users/Zhuanz/Desktop/workspace/harnessOS
```

如果 HarnessOS 不可用，必须记录：

- 替代项目路径。
- 替代原因。
- 项目规模。
- 是否覆盖多语言 / 多入口 / 多文档。
- 为什么可以作为大项目泛化验收输入。

## 4. 每个 Phase 的测试要求

### Phase 76：Provider Capability Registry

必须覆盖：

- provider registry schema。
- provider decision schema。
- health / configured / execution_supported / available 分离。
- provider missing credential。
- provider unsupported。
- redaction。
- HTTP/MCP/CLI parity。

拒绝通过：

- health-known 被标记为 execution accepted。
- missing credential 泄露 key 名或 key 值。
- unsupported provider fallback 到其他 provider。

### Phase 77：Semantic Provider Orchestrator

必须覆盖：

- AST baseline。
- optional provider unavailable。
- provider fact schema。
- provider fact line range truth sampling。
- merge policy。
- conflict policy。
- forbidden claim scan。

拒绝通过：

- import/reference 输出为 runtime call。
- full call graph / data flow / control flow / type inference 出现在 artifact 或 public payload。
- fact 没 evidence 却 accepted。

### Phase 78：Runtime Profile Manager

必须覆盖：

- profile schema。
- command template rendering。
- argument validation。
- default-deny。
- approved profile run。
- timeout / failed / blocked classification。
- redacted logs。

拒绝通过：

- 任意命令绕过 profile。
- failed / timeout 变成 passed。
- log 泄露绝对路径、secret、raw traceback。
- runtime evidence 覆盖 static evidence。

### Phase 79：Workbench v2

必须覆盖：

- payload schema。
- HTML render。
- Mermaid render。
- node integrity。
- blocker visibility。
- `needs_review` visibility。
- report redaction。
- JSON / HTML / Mermaid 一致性。

拒绝通过：

- HTML/Mermaid 生成 payload 中不存在的新事实。
- major/fatal/blocker 被隐藏。
- 页面只堆 raw JSON，不满足人类可读目标。

### Phase 80：Large-Project Abstraction Advisor

必须覆盖：

- generic adapter catalog。
- taxonomy mapping。
- document claim / code fact / pattern evidence 分离。
- blocker normalization。
- HarnessOS 或替代大项目 E2E。
- anti-hardcoding scan。

拒绝通过：

- HarnessOS-only hardcoding。
- document claim 被当作 code fact。
- accepted claim 缺 code evidence。
- blocker 只有“无法识别”，没有原因和下一步。

### Phase 81：Human-Gated Patch Sandbox

必须覆盖：

- preview artifact schema。
- diff artifact。
- rollback artifact。
- validation profile linkage。
- approval state machine。
- source hash before/after。
- apply without approval blocked。

拒绝通过：

- dry-run preview 修改源码。
- 未审批 apply。
- 默认 git commit / push / reset / restore。
- rollback 未覆盖 previewed files。

### Phase 82：最终闭环验收

必须覆盖：

- Phase 76-81 focused tests。
- 真实 `data_service` E2E。
- HarnessOS 或替代大项目 E2E。
- HTTP/MCP/CLI parity。
- artifact disk inspection。
- public redaction。
- false-green audit。
- coverage matrix 无 pending。
- no fatal / major finding。

拒绝通过：

- accepted row 缺测试命令。
- accepted row 缺 artifact path。
- accepted row 缺真实仓证据。
- planning docs 被当作 closure evidence。

## 5. HTTP/MCP/CLI Parity 验收

每个 public read/build 接口必须比较：

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- stable IDs
- counts
- artifact_refs
- warnings
- unresolved
- error code
- redaction state

错误路径也必须比较：

- provider unavailable。
- provider unsupported。
- semantic artifact not built。
- runtime profile not approved。
- runtime profile arg invalid。
- workbench not built。
- patch preview not found。
- patch apply not approved。

## 6. Artifact Integrity 验收

每个 artifact 必须验证：

- 文件存在。
- JSON 可解析。
- `schema_version` 正确。
- required fields 存在。
- artifact refs 可解析。
- evidence refs 可解析，或 `needs_review` 明确。
- public payload 不包含本机绝对路径。

Phase 81 额外验证：

- diff 文件可读。
- rollback 文件覆盖 previewed files。
- source hash before == source hash after dry-run preview。

## 7. Redaction 验收

public payload、HTML、Mermaid、runtime logs、provider errors 不得包含：

- `/Users/`
- `/private/`
- API key。
- token。
- secret。
- Authorization header。
- raw traceback。
- raw provider response body。

如果原始用户文档中包含路径，必须在 public payload 中标记为 redacted 或以 repo-relative 形式展示。

## 8. False-Green 审计

每个 Phase acceptance audit 必须回答：

1. 是否使用真实 repo，而不是 mock-only。
2. 是否检查 artifact 落盘和 readback。
3. 是否检查 HTTP/MCP/CLI parity。
4. 是否有 skipped test 被当作 accepted。
5. 是否有 unavailable provider 被当作 accepted。
6. 是否有 weak inference 被当作 accepted。
7. 是否有 blocker 被隐藏。
8. 是否有 source mutation 未被审批。
9. 是否有 public payload 泄露敏感信息。
10. 是否有非目标能力被过度声明。

任何答案为“是”的高风险项，都必须判定为 major 或 fatal。

## 9. 文档审计要求

每个 Phase 完成后必须更新：

- phase acceptance audit report。
- `V2_16_FULL_COVERAGE_MATRIX.md`。
- `V2_16_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md`。
- 如有偏差，更新 `V2_16_GAP_ANALYSIS.md`。

Phase 82 完成后必须生成：

```text
V2_16_PHASE_82_CLOSURE_AUDIT_REPORT.md
```

## 10. 当前结论

本测试与审计计划足以支撑 V2.16 Phase 76-82 的实现和验收设计。

但它不代表实现完成。进入每个 Phase 代码实现前，仍必须生成该 Phase 的 pre-implementation audit，并确认：

- 真实输入可用。
- 高风险动作被审批或 blocked。
- 无 fatal / major 规格偏差。
