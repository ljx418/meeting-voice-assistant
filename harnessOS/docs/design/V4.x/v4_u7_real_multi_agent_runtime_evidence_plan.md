# V4-U7 Real Multi-Agent Runtime Evidence Plan

文档状态：V4-U7 实施计划，目标是补齐 UX-08 / UX-09 / UX-10 的真实 provider-backed dev/local 运行证据。

允许声明：

```text
V4-U7 complete: real provider-backed multi-agent scenario evidence ready for review.
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

V4-U7 不新增 Agent executor，不新增 production runtime，不改变 source=agent 不能执行 mutation 的治理边界。它只把之前 UX-08 / UX-09 / UX-10 的 deterministic dev/local 证据升级为真实 provider-backed dev/local scenario evidence。

## PR Slices

1. U7A Serial Multi-Agent Runtime Evidence
   - 编剧、分镜、文案、剪辑计划、质量审查、发布准备工位均调用配置的 provider。
   - 记录 station output artifact、attempt history、storyboard rerun、downstream stale。

2. U7B Parallel Deliberation Runtime Evidence
   - Orchestrator、多个 persona、synthesis、contradiction review 均调用配置的 provider。
   - 记录 persona artifact、cross inspiration refs、synthesis attribution。

3. U7C Long-Running Engineering Runtime Evidence
   - 产品规划到人工确认的 11 个阶段均调用配置的 provider。
   - 记录 code_review rerun、attempt history、downstream stale、quality gate。

4. U7D Unified Reality Recheck
   - reality-check 优先读取 U7 evidence。
   - UX-08 / UX-09 / UX-10 若证据完整，则标记 PASS / real_runtime / runtime_backed=true / deterministic_only=false。
   - No False Green 和 sensitive literal scan 必须通过。

## 验收命令

```bash
./.venv/bin/python scripts/v4_u7_serial_multi_agent_runtime.py
./.venv/bin/python scripts/v4_u7_parallel_multi_agent_runtime.py
./.venv/bin/python scripts/v4_u7_engineering_workflow_runtime.py
./.venv/bin/python scripts/v4_unified_reality_check_audit.py
./.venv/bin/python -m pytest tests/test_v4_u7_*.py -q
./.venv/bin/python -m pytest tests/test_v4_*.py -q
xmllint --noout docs/design/V4.x/v4_x_headless_current_gap_analysis.drawio
```

## No False Green

V4-U7 证明的是 dev/local provider-backed scenario evidence。它不证明完整 Agent executor、production controlled executor、production external app support、autonomous workflow editing 或无限制多 Agent 编排。
