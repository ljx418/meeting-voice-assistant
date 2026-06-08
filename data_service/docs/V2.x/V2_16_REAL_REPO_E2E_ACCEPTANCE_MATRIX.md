# V2.16 真实仓 E2E 验收矩阵

## 1. 验收仓库

主仓：

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

大项目泛化仓：

```text
/Users/Zhuanz/Desktop/workspace/harnessOS
```

如果 HarnessOS 不可用，必须记录替代大项目路径和原因。

## 2. 用户场景验收

| 场景 | 输入 | 期望输出 | 通过标准 |
| --- | --- | --- | --- |
| 陌生项目接手 | repo path | provider matrix、项目摘要、workbench | 用户能看到项目能力、风险和 evidence。 |
| Coding Agent 改动准备 | task text | impact、patch plan、runtime profiles | 每条建议有 evidence 或 needs_review。 |
| 代码审查 | patch plan id | risk lanes、runtime result、rollback | blocker 不隐藏，runtime 失败不伪装通过。 |
| 大项目架构审计 | HarnessOS repo | abstraction report、pattern evidence、blockers | 无 HarnessOS-only hardcoding；blocker 精确。 |
| Patch preview | patch plan id | preview、diff、rollback、approval state | preview 不修改源码；apply 未审批 blocked。 |

## 3. Phase E2E 验收

| Phase | data_service 验收 | HarnessOS / 大项目验收 |
| ---: | --- | --- |
| 76 | provider matrix 非空，missing/unsupported provider 结构化 | 同样输出 provider matrix，不泄露路径/secret |
| 77 | AST baseline + optional provider unavailable 路径通过 | 大项目输出 semantic facts 或 structured blocker |
| 78 | approved runtime profile 可运行 | profile 返回 pass/fail/blocker，不伪装成功 |
| 79 | workbench v2 可读，HTML/Mermaid/JSON 一致 | 大项目 workbench 可解释 blocker |
| 80 | abstraction report accepted items 有 evidence | HarnessOS blocker 比 V2.15 更精确 |
| 81 | patch preview 不改源，diff/rollback 可读 | 大项目 patch preview 低置信度进入 needs_review |
| 82 | 全链路 closure | 全链路 closure 或 structured blocker accepted |

## 4. 磁盘 Artifact 检查

必须检查：

```text
coding_agent/v2_16/providers/capability_registry.json
coding_agent/v2_16/semantic/merged_semantic_index.json
coding_agent/v2_16/runtime_profiles/profiles.json
coding_agent/v2_16/workbench_v2/payload.json
coding_agent/v2_16/large_project/abstraction_report.json
coding_agent/v2_16/patch_sandbox/previews/{preview_id}.json
```

## 5. 假验收拒绝

拒绝通过：

- 只用 mock repo。
- HarnessOS hardcoding。
- provider unavailable 写 accepted。
- skipped optional provider 写 accepted。
- runtime command 绕过 profile。
- patch preview 修改源码。
- public payload 泄露绝对路径或 secret。
