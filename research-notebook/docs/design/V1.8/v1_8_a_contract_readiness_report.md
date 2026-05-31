# V1.8-A Agent Task Contract Readiness Report

日期：2026-05-30

## 结论

V1.8-A 合同补强已完成到文档层，状态为 `CONTRACT_READY_FOR_REVIEW`。

本阶段没有实现业务代码，没有读取本地目录，没有执行 workflow，也没有声明 Agent ready。

## 已补强内容

| 项 | 状态 |
| --- | --- |
| AgentTask 使用 target_path_labels / target_path_refs | PASS |
| 禁止最终 report / fixtures 写 raw target paths | PASS |
| WorkflowRun DTO | PASS |
| WorkflowStep 错误与 retry 字段 | PASS |
| ValidationAssertion DTO | PASS |
| ValidationReport 增加 step_results / assertions / raw_fixture_refs | PASS |
| draft 成功不等于 workflow 可运行 | PASS |
| 未确认前不得 scan / import / source read | PASS |
| 不调用 `/api/v1/knowledge/*` | PASS |
| 后续 B/C/D/E 需逐阶段审计 | PASS |

## 仍不可声明

- Agent ready。
- Workflow ready。
- 普通用户 UX ready。
- Local folder connector ready。
- Source import workflow ready。
- Guide / QA / Studio quality ready。
- all-source-type ready。
- all websites URL ready。

## 风险评估

| 风险 | 等级 | 说明 |
| --- | --- | --- |
| 规格漂移 | LOW-MEDIUM | 已限制 V1.8-A 只做合同。 |
| 虚假验收 | MEDIUM | draft / contract 成功仍可能被误读为 workflow 可运行。 |
| 路径泄露 | MEDIUM | 已通过 target_path_refs 和 fixture/report 禁止项收敛。 |
| 后续阶段过度批准 | MEDIUM | 已明确 B/C/D/E 必须逐阶段审计。 |

## 下一阶段入口

下一阶段只能审计 V1.8-B Agent-Led Source Import，不得直接进入 C/D/E/RC。

V1.8-B 审计必须重点确认：

- permission_grant_id。
- 用户确认前不得 scan / import / source read。
- symlink 默认不跟随。
- logs / fixtures / reports 不含 raw path、API key、raw content dump。
- Agent import 必须基于真实 data_service，不得 mock。
- URL 仍为 limited URL，不是 all websites。

