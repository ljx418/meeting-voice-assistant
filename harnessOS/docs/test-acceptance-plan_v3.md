# Test & Acceptance Plan - harnessOS V3.0

文档状态：ACTIVE V3.0 TEST PLAN。V2 测试计划已归档到 `docs/history/v2-phase-docs/test-acceptance-plan_v2.md`。

已完成阶段冻结规则：

- 已完成并重新验收通过的阶段，必须把对应测试入口固化为回归基线。
- 后续阶段不得删除或弱化这些测试来适配新实现；若测试需要修改，必须说明是缺陷修复、环境基线调整，还是后续阶段兼容扩展。

## 1. 当前测试目标

V3.0 的测试重点不是新增业务，而是验证同一份 harnessOS Core 能被多个 app 复用，并通过 AppProfile + Pack + Connector + RuntimeAdapter + Job + Artifact + Governance 实现多态运行。

## 2. 默认自动化测试

```bash
.venv/bin/python -m pytest tests -q -k 'not phase1_meeting_acceptance_uses_workspace_audio_dir and not phase1b_real_audio_turn_start_acceptance'
```

预期：

- 既有 Gateway、Core Store、RuntimeAdapter、Policy、Approval、Retry、Artifact 回归不失败。
- 默认测试不依赖真实 FunASR、Meeting MCP、Knowledge MCP 或外部网络。
- 2026-05-06 本地验证结果：`161 passed, 1 skipped, 2 deselected`（在显式排除两个真实音频验收用例后）。

## 3. V3.0 Targeted Tests

```bash
python3 -m pytest tests/test_v3_multi_app_core.py -q
```

覆盖：

- AppProfile / AppRegistry / ScopeContext。
- Core records scope 字段。
- Gateway/Core service 普通调用链的默认 scope filtering；底层 Store 不传 scope 的全量查询必须作为受控 bypass 单独测试或显式标记。
- Artifact external registration 和 metadata-only read。
- 大文件、视频、external-only artifact read 阻断。音频、图片、binary 和统一错误码仍属于 V3.0-PhaseC 待冻结验收。

PhaseA 详细实施与辅助验收文件：

- `docs/design/V3.0/v3_phasea_multi_app_core_readiness.md`
- `docs/design/V3.0/v3_phasea_multi_app_core_readiness_acceptance.md`

PhaseA 冻结测试基线：

- `tests/test_v3_multi_app_core.py`
- `tests/test_gateway_protocol.py`
- `tests/test_meeting_audio_acceptance.py`
- `tests/test_meeting_turn_workflow.py::test_phase1b_real_audio_turn_start_acceptance`

其中：

- `tests/test_v3_multi_app_core.py` 与 `tests/test_gateway_protocol.py` 是仓库默认自动化基线。
- `tests/test_meeting_audio_acceptance.py` 与 `tests/test_meeting_turn_workflow.py::test_phase1b_real_audio_turn_start_acceptance` 是显式真实 MCP / 真实音频集成线，不属于可移植默认主线。

上述用例现在同时承担三类角色：

- 已完成阶段的行为合同
- 后续 Phase 的回归门
- 文档验收口径的代码证据

## 3.1 V3.0-PhaseB 目标测试入口

PhaseB 当前重点不是业务 E2E，而是 Pack / Connector 合同冻结。建议优先覆盖：

- `tests/test_pack_registry.py`
  - pack manifest schema
  - PackAssemblyResult 字段完整性
  - conflicts / missing dependency / degraded / blocked 语义
  - AppProfile `pack_paths` 驱动的 external pack 加载
  - AppProfile 未启用 connector 时返回 `app_profile_connector:*` blocked dependency
  - external pack `metadata.target_version`：缺失时 degraded，不兼容时 blocked
- `tests/test_gateway_protocol.py`
  - `pack.list/get`
  - `connector.list/get/health`
  - connector descriptor 字段稳定性
  - `app_registry + connector_registry` 推导的 assembly 输入
- connector security fixture
  - 未 allowlist 的 stdio command/path/network 被 blocked
  - 合法 connector 不被误拦截

PhaseB 验收重点：

- 默认 contract/registry/security 回归必须通过。
- 不依赖真实音频或真实 MCP 外部服务作为主验收门。
- Meeting / Knowledge 的 pack/registry 装配入口可以通过 assembly/health 测试验证，不必等到 PhaseD/PhaseE 的真实 E2E 才确认入口合同。

## 4. Meeting Real Audio Acceptance

真实音频验收必须在 V3.0-PhaseD 前后保持不回归。

前置：

- 显式真实音频验收现在通过 `HARNESS_MEETING_MCP_AUDIO_DIR` 启用；未设置时，真实音频用例应 skip，而不是把仓库默认回归判为失败。
- `/Users/Zhuanz/Desktop/workspace/音频资料` 仍是当前开发机上的有效样本目录，但它只是本地实现事实，不再是仓库测试合同。
- FunASR / Meeting MCP 真实服务需要显式启动或显式环境变量开启。
- harnessOS 自身测试应使用 `.venv/bin/python`。
- FunASR MCP 默认优先使用 `/Users/Zhuanz/Desktop/workspace/voice_service/.venv/bin/python`；Meeting / Data Service MCP 仍使用各自配置的 backend 解释器。

建议环境基线：

```text
harnessOS:
  .venv/bin/python

meeting-voice-assistant backend:
  /Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/backend/venv312/bin/python

voice_service FunASR MCP:
  /Users/Zhuanz/Desktop/workspace/voice_service/.venv/bin/python
```

建议在显式真实验收前先执行：

```bash
.venv/bin/python scripts/check_real_mcp_env.py
```

2026-05-06 本地显式前检查结果：

- 未设置 `HARNESS_MEETING_MCP_AUDIO_DIR` 时，`scripts/check_real_mcp_env.py` 返回 `status=integration_disabled`，用于表示“默认仓库主线可运行，但显式真实音频验收未启用”。
- 在显式设置样本目录、相邻 `meeting-voice-assistant` 的 Meeting / FunASR 服务已启动，且默认 MCP 命令解析到 `backend/venv312/bin/python` 的前提下，`scripts/check_real_mcp_env.py` 返回 `status=ok`。

建议命令：

```bash
.venv/bin/python -m pytest -q \
  tests/test_meeting_audio_acceptance.py \
  tests/test_meeting_turn_workflow.py::test_phase1b_real_audio_turn_start_acceptance
```

预期：

- 产出 transcript、analysis、result、minutes。
- 产物注册为 artifacts。
- job、trace、turn、artifact lineage 可查询。
- 2026-05-06 在显式启动本地 Meeting / FunASR 服务并使用默认 `backend/venv312/bin/python` MCP 解释器后，上述命令本地结果为 `2 passed`。

## 5. Knowledge MCP Acceptance

V3.0-PhaseE 必须验证 Knowledge Pack 通过 Knowledge MCP connector 接入本地知识库服务。

验收链路：

```text
workspace create
  -> source import
  -> build start/status
  -> search/query
  -> summarize
  -> citation bundle
```

安全边界：

- 不直接读写 data_service 内部 artifact dirs。
- source path 必须经过 allowlist、大小上限、sha256 去重、symlink 防绕过。

## 6. Documentation Gate

每个 V3.0 阶段完成后必须同步：

- `docs/design/V3.0/v3_development_plan_multi_app_core.md`
- `docs/design/V3.0/v3_current_gap_analysis.md`
- `docs/acceptance-test-cases_v3.md`
- `docs/test-acceptance-plan_v3.md`
- `docs/architecture/CURRENT-STATUS_v3.md`
- `docs/architecture/current-vs-target-gap_v3.md`
- `docs/architecture/current-vs-target-gap_v3.drawio`

验收命令：

```bash
git diff --check -- docs
xmllint --noout docs/architecture/current-vs-target-gap_v3.drawio
```
