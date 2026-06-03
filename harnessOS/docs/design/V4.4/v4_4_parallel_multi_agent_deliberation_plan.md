# V4.4 Parallel Multi-Agent Deliberation Workflow MVP Plan

阶段目标：

验证一个 dev/local deterministic 罗马广场式并行讨论工作流。多个 persona 从不同角度讨论同一项目问题，允许 cross-inspiration edge，最后由 synthesis 节点输出带归因的汇总，并由 contradiction review 记录矛盾和未决风险。

允许声明：

```text
V4.4 complete: parallel multi-Agent deliberation workflow MVP ready for dev/local validation.
```

禁止声明：

```text
forbidden Agent executor ready
forbidden controlled executor ready
forbidden full multi-Agent orchestration ready
forbidden production-ready external app support
forbidden complete Workflow Studio ready
```

## PR Slices

1. Parallel deliberation spec and persona descriptors.
2. Deterministic persona artifact runner.
3. BFF user-confirmed start, persona rerun, and downstream continuation.
4. TUI transcript, Drawio, HTML reports, and evidence package.
5. Focused tests and no false-green scan.

## Real Data Fixture

```text
tests/fixtures/v4_4/deliberation/project_question.md
```

