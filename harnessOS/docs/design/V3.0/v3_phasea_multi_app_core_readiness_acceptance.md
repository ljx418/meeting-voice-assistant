# harnessOS V3.0-PhaseA Multi-App Core Readiness Acceptance Appendix

文档状态：FROZEN PHASEA ACCEPTANCE BASELINE（COMPLETED 2026-05-06）。

本文是 V3.0-PhaseA 的辅助验收文件。2026-05-06 完成重新验收后，本文转为冻结验收基线。后续只能追加证据、记录缺陷修复和补充环境基线说明，不得把后续阶段的新验收目标回写成 PhaseA 的验收要求。

## 1. 验收原则

- 默认回归与显式集成验收分开记录。
- PhaseA 主要验收对象是 multi-app 隔离、scope 传递、默认查询过滤与 legacy backfill 口径。
- 真实音频验收保留，但属于显式外部服务验收，不计入默认 stub/contract 基线。
- 本附录中的 AC01-AC08 已作为 PhaseA 冻结验收项保留；后续阶段不得删改其通过标准，只能在兼容前提下增加新的后续阶段验收项。
- 验收记录必须区分：
  - 代码行为缺陷
  - 外部服务未启动
  - 环境缺依赖
  - 文档口径不一致

## 2. 默认回归范围

默认回归覆盖以下能力：

- AppProfile / AppRegistry / ScopeContext
- Core records scope 字段与 scope filtering
- Gateway/Core service 的默认安全查询路径
- artifact external registration / metadata-only read
- runtime adapter / governance 相关基础回归
- session/job/artifact/trace/approval/retry 查询面

默认回归命令：

```bash
.venv/bin/python -m pytest tests -q -k 'not phase1_meeting_acceptance_uses_workspace_audio_dir and not phase1b_real_audio_turn_start_acceptance'
```

期望结果：

- 默认主线回归通过。
- 失败项若出现，优先视为 PhaseA 代码或合同问题，而不是“测试不稳定”。
- 2026-05-06 本地验证结果：`145 passed, 1 skipped, 2 deselected`。

## 3. 显式集成验收范围

显式集成验收覆盖以下能力：

- `meeting.process_recording` 真实音频路径
- `turn.start` 会议路径真实音频分析
- transcript / analysis / result / minutes artifact 产出
- job / trace / turn / artifact lineage 记录

显式集成验收命令：

```bash
.venv/bin/python -m pytest -q \
  tests/test_meeting_audio_acceptance.py \
  tests/test_meeting_turn_workflow.py::test_phase1b_real_audio_turn_start_acceptance
```

说明：以上命令是 PhaseA 2026-05-06 历史冻结基线。2026-05-08 之后，当前真实音频平台验收以 `voice_service` FunASR HTTP + MCP stdio 和 `scripts/e2e_meeting_validation.sh` 为准，详见 `docs/design/V3.0/test-acceptance-plan_v3.md`。

前置条件：

- 2026-05-06 历史基线要求相邻 `meeting-voice-assistant` 项目可访问，Meeting MCP / FunASR 服务已显式启动，或相关环境变量已启用真实执行路径。
- 当前基线要求相邻 `voice_service` FunASR HTTP 服务可访问，并通过 `voice_service/.venv/bin/python` 提供 FunASR MCP stdio connector。
- 当前样本目录按本地实现事实仍是 `/Users/Zhuanz/Desktop/workspace/音频资料`。
- harnessOS 侧命令使用 `.venv/bin/python`。
- 相邻 backend 侧历史真实 MCP 优先使用 `/Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/backend/venv312/bin/python`；当前 FunASR MCP 优先使用 `/Users/Zhuanz/Desktop/workspace/voice_service/.venv/bin/python`。
- 若 `venv312` 缺依赖或未建成，失败应优先记为 `environment_missing_dependency`，而不是直接记为业务代码通过。
- 建议先运行 `.venv/bin/python scripts/check_real_mcp_env.py`；仅当返回 `status=ok` 时再执行真实音频验收。

## 4. 验收项

### PhaseA-AC01 AppProfile 加载

- 目的：验证五个默认 profiles 可被统一加载与查询。
- 前置条件：无。
- 入口：`app.list`、`app.get` 或 `tests/test_v3_multi_app_core.py`
- 期望结果：meeting、knowledge、interview、investment、video_studio 全部可见。
- 失败判定：缺 profile、字段缺失、默认合同不一致。

### PhaseA-AC02 Scope Resolver 一致性

- 目的：验证 `resolve_scope_context()` 与 RPC/service 层使用同一套解析语义。
- 前置条件：无。
- 入口：`session.start`、`turn.start`、artifact/job/trace/approval/retry 查询相关测试。
- 期望结果：显式 scope、params scope、default fallback 行为一致。
- 失败判定：不同入口对同一 scope 输入产生不一致解析结果。

### PhaseA-AC03 Core Records 写入带 Scope

- 目的：验证普通写入路径不仅有字段定义，而且实际写入 scope。
- 前置条件：无。
- 入口：session/turn/job/artifact/trace/approval/retry/connector 相关测试。
- 期望结果：关键 record 可查询到 `app_id/project_id/workspace_id`。
- 失败判定：桥接/适配路径产生缺 scope records。

### PhaseA-AC04 默认查询隔离

- 目的：验证 Gateway/Core service 的普通 list/query 默认安全。
- 前置条件：准备 meeting 与 knowledge 同名 records fixture。
- 入口：`tests/test_v3_multi_app_core.py` 与相关 Gateway protocol tests。
- 期望结果：meeting 查询看不到 knowledge 同名 records，反之亦然。
- 失败判定：普通调用链中出现跨 app 泄漏。

### PhaseA-AC05 Legacy Backfill 口径一致

- 目的：验证 legacy records 的默认归属规则与文档一致。
- 前置条件：存在无 scope 输入的兼容 fixture 或导入路径。
- 入口：migration/import fixture。
- 期望结果：
  - 默认 `app_id=default`
  - 可明确识别的 meeting 记录映射为 `meeting`
  - 其余不做业务归属猜测
- 失败判定：不同路径使用不同 backfill 规则。
- 当前代码证据：legacy schema 补列 fixture、legacy gateway import fixture、meeting legacy backfill fixture 已存在。

### PhaseA-AC06 Namespace Isolation Fixture

- 目的：验证 session/thread/job/artifact 至少四类对象不串数据。
- 前置条件：构造 meeting / knowledge 同名 fixture。
- 入口：Core store 与 Gateway service 组合测试。
- 期望结果：至少四类对象完成跨 app 隔离断言。
- 失败判定：任何一类普通查询穿透到其他 app 数据。
- 当前代码证据：session/thread/job/artifact 四类对象已有 namespace fixtures；Gateway `session.list/read` 默认隔离已回归。

### PhaseA-AC07 默认 Stub/Contract 回归通过

- 目的：确认 PhaseA 改动未破坏当前主回归线。
- 前置条件：Python 依赖齐备。
- 入口：默认回归命令。
- 期望结果：默认主线通过。
- 失败判定：出现非真实音频类失败。

### PhaseA-AC08 真实音频显式验收记录完整

- 目的：确认团队在验收时不会把外部依赖问题误判为 PhaseA 默认回归失败。
- 前置条件：Meeting MCP / FunASR 服务状态明确。
- 入口：显式真实音频验收命令。
- 期望结果：
  - 若服务已启动，则产出 transcript、analysis、result、minutes。
  - 若服务未启动，则失败原因被记录为外部服务未就绪。
- 失败判定：把外部依赖失败错误记为默认回归失败，或无证据记录。
- 当前证据：2026-05-06 在 `.venv/bin/python` + `meeting-voice-assistant/backend/venv312/bin/python` 基线下，先通过 `scripts/check_real_mcp_env.py`，再执行显式真实音频验收命令，结果为 `2 passed`。

## 5. 证据记录模板

每次 PhaseA 验收至少记录以下字段：

```text
Date:
Executor:
Command:
Scope:
Result: pass | fail
Failure Class: code_defect | external_service_unavailable | environment_missing_dependency | doc_mismatch
Key Evidence:
Notes:
```

## 6. 当前已知风险说明

- 默认回归与真实音频验收是两条不同基线，验收记录必须显式区分。
- 2026-05-08 PhaseD 已将 `meeting.process_recording` 降级为 runtime-backed compatibility facade；该路径现在复用 `meeting.workflow` 的 job/trace/turn/artifact 绑定。
- 若真实 Meeting/FunASR/MCP 链路仍落回系统 `python3`，验收结果可能受解释器权限或依赖差异影响；验收记录必须说明实际使用的解释器路径。
- 若未来把真实音频样本目录从本地路径迁回可移植 fixture，本附录也需要同步更新。
