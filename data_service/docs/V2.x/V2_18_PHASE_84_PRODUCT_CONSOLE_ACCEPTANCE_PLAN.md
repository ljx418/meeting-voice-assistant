# V2.18 Phase 84 Acceptance Plan：Product Console & Report UX

## 1. 验收目标

验证 Platform Console 是否真正改善用户理解项目的体验，同时不引入虚假事实、不隐藏风险、不越过 V2.18 范围。

## 2. 必须验收项

| 验收项 | 标准 |
| --- | --- |
| Artifact 落盘 | `platform_console.json` 存在且可读。 |
| HTML 落盘 | `views/platform_console.html` 存在且 HTML parser 可解析。 |
| Schema | payload 包含 `schema_version=v2.18` 和 `artifact_type=platform_console`。 |
| 面板 | 至少包含 Overview、Evidence、Architecture、Agent、Runtime、Patch、Next Actions。 |
| Missing artifact | 缺失输入必须显示 `needs_build` / `missing` / `blocked`。 |
| No unpersisted fact | HTML 不得显示 payload 中不存在的 capability/finding/recommendation。 |
| Redaction | public 输出不得包含本机绝对路径、secret、raw traceback。 |
| Thin wrapper | HTTP/MCP/CLI 不实现核心逻辑，只调用 platform service。 |
| V1/V2 regression | 不破坏既有 public surface guard。 |

## 3. 真实数据验收

真实仓库：

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

验收流程：

```text
workspace create/import current repo
-> snapshot
-> build console
-> read console JSON
-> read console HTML
-> inspect artifact files
-> run tests
```

## 4. False-Green 拒绝规则

以下情况必须拒绝验收：

- 只生成 HTML，不落盘 JSON artifact。
- HTML 文本硬编码能力结论，payload 中没有对应来源。
- 缺失 artifact 时仍显示 ready。
- blocker / needs_review 被隐藏。
- absolute path / secret / traceback 泄露。
- 使用 mock-only repo。
- 跳过 HTTP/MCP/CLI contract 检查。
- 为通过测试改小 public surface 或删除已有工具。

## 5. 测试命令

最小测试：

```text
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_18_platform_console.py -q
PYTHONPATH=backend python3 -m pytest backend/tests/test_public_surface_guard.py -q
npm run build
git diff --check -- .
```

全量回归建议：

```text
PYTHONPATH=backend python3 -m pytest backend/tests -q
```

## 6. 审计输出

Phase 84 完成后必须产出：

```text
docs/V2.x/V2_18_PHASE_84_PRODUCT_CONSOLE_ACCEPTANCE_AUDIT_REPORT.md
```

报告必须包含：

- 测试命令和结果。
- 真实仓库 E2E 摘要。
- Artifact refs。
- PRD/spec review。
- False-green review。
- open findings。
