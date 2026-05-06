# harnessOS 阶段验收标准与测试用例集

本文档是阶段验收的执行基线。每个阶段的验收必须同时满足：

- 自动化用例通过
- 用户态手工用例通过
- 文档与架构状态同步
- 未完成项明确记录到 `TASKS.md`

## Phase 0: 底座与骨架

### 验收标准

- 仓库结构存在并可导入核心模块。
- `POST /v1/runs` 能完成用户输入到模型回复的最小闭环。
- 基础 CLI 可输入“你好”并获得回复或 demo fallback。
- 基础工具 `workspace_ls`、`workspace_read_file`、`workspace_write_file`、`artifact_save` 可调用。
- FastAPI app 可创建并提供 `/health`。
- 本地 smoke/unit 测试通过。
- README、`.env.example`、架构文档存在。

### 自动化用例

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| P0-A01 | Python 编译检查 | `python3 -m compileall apps core tools cli` | 退出码 0 |
| P0-A02 | API app 导入 | `from apps.api import app` | 无异常 |
| P0-A03 | Health API | `GET /health` | 200，`status=healthy` |
| P0-A04 | Headless demo fallback | 清空 API key 后运行 `python3 -m cli.main run "你好"` | 输出包含“你好”或 demo mode |

### 用户态手工用例

1. 进入项目根目录：`cd <workspace>/harnessOS`
2. 启动普通 CLI：`python3 -m cli.main`
3. 输入：`你好`
4. 预期：终端输出模型回复或 demo fallback。
5. 输入：`quit`
6. 预期：CLI 正常退出。

## Phase 0.5-0.6: 协议优先控制面

### 验收标准

- `harness run` 或 `python3 -m cli.main run` 可直接在普通终端运行，不进入 TUI。
- Gateway 具备项目自有协议模型：`RpcRequest`、`RpcResponse`、`RpcError`、`GatewayEvent`、`TurnResult`。
- Gateway 支持 `initialize`、`health.ping`、`session.start`、`session.resume`、`session.events`、`session.close`、`turn.start`、`turn.continue`、`turn.interrupt`。
- Gateway 支持 `session.list`、`session.read`、`session.transcript`。
- Gateway 事件输出归一化为 `turn.started`、`item.delta`、`turn.completed`、`turn.failed` 等项目事件。
- session snapshot 和 `events.jsonl` 可持久化并读取。
- FastAPI 暴露 `/v1/runs`、`/v1/runs/stream`、`/v1/sessions/{session_id}/events`、`/v1/sessions`、`/v1/rpc`。
- stdio JSONL 暴露 `python3 -m apps.gateway.stdio_server`。
- 旧 `apps/gateway` 不再依赖 `ohmo.*` 或 channel bus。
- 自动化测试覆盖协议 happy path、unknown session、resume/interrupt、API run。

### 自动化用例

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| P05-A01 | Gateway 协议单测 | `pytest tests/test_gateway_protocol.py` | 全部通过 |
| P05-A02 | API runs/session/RPC 单测 | `pytest tests/test_api_runs.py` | 全部通过 |
| P05-A03 | Gateway 去 ohmo 化 | `rg "ohmo\|Ohmo\|ChannelManager\|openharness.channels" apps/gateway` | 无匹配 |
| P05-A04 | Draw.io XML 校验 | `xmllint --noout docs/architecture/current-vs-target-gap_v2.drawio` | 退出码 0 |
| P05-A05 | Headless CLI demo | 清空 API key 后运行 `python3 -m cli.main run "你好"` | 退出码 0，有文本输出 |
| P05-A06 | FastAPI `/v1/runs` | TestClient `POST /v1/runs` | 200，返回 `session_id/turn_id/final_text/events` |
| P05-A07 | FastAPI SSE | TestClient `POST /v1/runs/stream` | 200，返回 `text/event-stream` 事件 |
| P05-A08 | Session events | 运行 turn 后读取 `session.events` | 至少包含 started/delta/completed |
| P05-A09 | Session 查询 | `GET /v1/sessions`、`GET /v1/sessions/{id}`、`GET /v1/sessions/{id}/transcript` | 200，返回 snapshot/transcript |
| P05-A10 | RPC 入口 | `POST /v1/rpc` 调用 `health.ping` | 200，`error=null` |
| P05-A11 | stdio JSONL | `pytest tests/test_gateway_stdio.py` | stdout 每行是合法 RpcResponse JSON |
| P06-A01 | RuntimeBundle backend 路径 | `pytest tests/test_gateway_protocol.py::test_gateway_runtime_bundle_backend_paths` | turn.start/continue 走 bundle stream |
| P06-A02 | 统一错误码 | unknown session / unknown method | 返回 `SESSION_NOT_FOUND` / `METHOD_NOT_FOUND` |

### 用户态手工用例

1. Headless CLI：
   ```bash
   cd <workspace>/harnessOS
   python3 -m cli.main run "你好"
   ```
   预期：直接在当前终端输出回复，不进入 TUI。

2. Headless JSON：
   ```bash
   python3 -m cli.main run --json "你好"
   ```
   预期：输出 JSON，包含 `session_id`、`turn_id`、`final_text`、`events`。

3. API 同步 run：
   ```bash
   python3 main.py --port 8010 --no-reload
   curl -X POST http://localhost:8010/v1/runs \
     -H 'Content-Type: application/json' \
     -d '{"input":"你好","close_session":true}'
   ```
   预期：返回 JSON，包含 `final_text`。如果使用 8000 端口且提示端口占用，先用 `lsof -nP -iTCP:8000 -sTCP:LISTEN` 确认旧进程，或改用 `--port 8010`。

4. API SSE run：
   ```bash
   curl -N -X POST http://localhost:8010/v1/runs/stream \
     -H 'Content-Type: application/json' \
     -d '{"input":"你好","close_session":true}'
   ```
   预期：返回 SSE 格式事件，至少包含 `turn.started` 和 `turn.completed`。

5. TUI 兼容：
   ```bash
   python3 -m cli.main --oh
   ```
   输入 `你好`。预期：TUI 内显示回复。

6. JSON-RPC：
   ```bash
   curl -X POST http://localhost:8010/v1/rpc \
     -H 'Content-Type: application/json' \
     -d '{"id":"req_1","method":"health.ping","params":{}}'
   ```
   预期：返回 `id=req_1`，`error=null`。

7. stdio JSONL：
   ```bash
   python3 -m apps.gateway.stdio_server
   ```
   输入：
   ```json
   {"id":"req_1","method":"health.ping","params":{}}
   ```
   预期：stdout 返回一行合法 JSON，`error=null`。

## Phase 0.7: 控制面收口与进入业务编排前置

状态：已完成，真实模型 smoke 默认跳过，仅在显式设置 `HARNESSOS_RUN_MODEL_SMOKE=1` 时联网执行。

### 验收标准

- `turn.interrupt` 能取消正在进行的 turn，至少在 Gateway active task 层取消；如果底层 RuntimeBundle 暴露 cancel API，则优先调用底层 cancel。
- 中断后 session snapshot 状态为 `interrupted`，event log 包含 `turn.interrupted`。
- Headless CLI 有自动化回归，覆盖普通文本、`--json`、无 API key demo fallback。
- 真实模型 smoke 测试存在，但默认跳过，只有显式设置环境变量才联网执行。
- `/v1/rpc` 与 stdio JSONL 在同一组方法上输出兼容的 `RpcResponse`。
- 本地用户态验收步骤覆盖 CLI、HTTP、SSE、RPC、stdio 五类入口。

### 自动化用例

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| P07-A01 | Active turn interrupt | `pytest tests/test_gateway_interrupt.py` | running turn 被取消，事件为 `turn.interrupted` |
| P07-A02 | Interrupt 持久化 | 读取 `session.events` 与 `session.read` | event log 有 interrupted，snapshot 状态为 `interrupted` |
| P07-A03 | Headless CLI 文本 | `pytest tests/test_cli_headless.py::test_cli_run_text_demo` | 退出码 0，stdout 有文本 |
| P07-A04 | Headless CLI JSON | `pytest tests/test_cli_headless.py::test_cli_run_json_demo` | stdout 是 JSON，含 `final_text/events` |
| P07-A05 | Headless CLI fallback | 清空 API key 后运行 CLI | demo fallback 可用 |
| P07-A06 | 真实模型 smoke | `HARNESSOS_RUN_MODEL_SMOKE=1 pytest -m smoke_model` | 显式开启时请求真实模型并返回文本 |
| P07-A07 | RPC/stdio 同构 | 同一批 `RpcRequest` 分别走 `/v1/rpc` 与 stdio | `id/error/result` 结构一致 |

本阶段自动化验收命令：

```bash
PYTHONPYCACHEPREFIX=/tmp/harnessos-pycache python3 -m pytest \
  tests/test_gateway_interrupt.py \
  tests/test_cli_headless.py \
  tests/test_rpc_stdio_compat.py \
  tests/test_model_smoke.py
```

### 用户态手工用例

1. 启动 API：
   ```bash
   python3 main.py --port 8010 --no-reload
   ```

2. 启动一个长 turn 后中断：
   ```bash
   curl -X POST http://localhost:8010/v1/rpc \
     -H 'Content-Type: application/json' \
     -d '{"id":"s1","method":"session.start","params":{}}'
   ```
   使用返回的 `session_id` 发起长请求，再调用：
   ```bash
   curl -X POST http://localhost:8010/v1/rpc \
     -H 'Content-Type: application/json' \
     -d '{"id":"i1","method":"turn.interrupt","params":{"session_id":"<session_id>"}}'
   ```
   预期：返回 `interrupted=true`，随后读取 events 可见 `turn.interrupted`。

3. CLI 回归：
   ```bash
   python3 -m cli.main run "你好"
   python3 -m cli.main run --json "你好"
   ```
   预期：两者都退出码 0，后者输出合法 JSON。

## Phase 1: 会议 MCP MVP

### 验收标准

- harnessOS 通过 `meeting.*` RPC 接入相邻项目的 Meeting MCP server。
- `meeting.capabilities` 能发现 `meeting_process_file`、`meeting_analyze_text`、`meeting_build_minutes` 和 `meeting://agent-guide`。
- `meeting.analyze_text` 能完成文本会议分析并生成会议纪要。
- `meeting.process_recording` 必须使用团队标准样本目录 `fixtures/audio_samples/` 下真实音频完成验收；标准样本落地前，可使用本机真实音频作为 local validation evidence。
- `turn.start(domain=meeting)` 和普通聊天/headless 输入中的会议音频路径，必须能自动进入 Meeting workflow。
- 成功处理的真实音频必须产出非空 transcript、`segment_count > 0`、非空 `analysis.theme` 和 `minutes.md`。
- 较长真实音频的 MCP stdio 单行 JSON 响应可能超过 Python 默认 `readline()` 限制；harnessOS 必须提高 Meeting MCP stdio 读取上限。若下游分析器仍触发 `chunk/limit` 限制，必须降级为“先转写、再压缩转写分析、最后生成纪要”，不得向用户直接暴露 `Separator is found, but chunk is longer than limit`。
- 面试关键词的音频请求不得误触发 Meeting workflow。
- 面试 workflow 暂缓，不作为 Phase1 验收内容。

### 自动化用例

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| P1-A01 | Meeting Gateway 单测 | `pytest tests/test_meeting_gateway.py` | fake MCP 下 capabilities/analyze/process/audio_dir 全部通过 |
| P1-A02 | Gateway 回归 | `pytest tests/test_gateway_protocol.py tests/test_rpc_stdio_compat.py` | 既有 session/turn/RPC/stdio 行为不回归 |
| P1-A03 | 真实音频验收 | `pytest tests/test_meeting_audio_acceptance.py` | 使用标准样本或本机真实音频产出 transcript/analysis/minutes |
| P1-A04 | Meeting turn workflow | `pytest tests/test_meeting_turn_workflow.py` | `turn.start(domain=meeting)`、自然语言会议音频路径、真实音频和面试防误路由均通过 |
| P1-A05 | Draw.io XML 校验 | `xmllint --noout docs/architecture/current-vs-target-gap_v2.drawio docs/architecture/diagrams/01_current_architecture_v2.drawio docs/architecture/diagrams/02_target_architecture_v2.drawio` | 退出码 0 |
| P1-A06 | 长转写降级分析 | `pytest tests/test_meeting_gateway.py::test_meeting_process_recording_retries_long_transcript_analysis` | inline 分析遇到 chunk/limit 错误后，重试只转写并用压缩转写完成分析和纪要 |
| P1-A07 | MCP 大响应读取上限 | `pytest tests/test_meeting_gateway.py::test_meeting_mcp_stdio_limit_allows_large_json_responses` | Meeting MCP stdio 读取上限不低于 128MB |

本阶段已验收结果：

- 团队标准真实音频目录：`fixtures/audio_samples/`
- 当前标准 fixture 未落地时，可使用本机真实音频作为 local validation evidence。
- 已处理音频：`TED演讲对话_How to tune your inner voice  Rhonda Ross Daniel A.mp3`
- 显式 RPC Meeting session：`meeting_895b5d29`
- Chat/headless Meeting session：`meeting_8e8d3499`
- Minutes artifact：本机 meeting output 中的 `minutes.md`；团队基线只要求产物路径存在并可读取，不绑定个人机器绝对路径。
- 自动化结果：`tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_gateway_protocol.py` 为 19 passed。
- 用户态结果：使用本机真实音频样本执行 `python3 -m cli.main run --json '请分析 <audio_path>，生成会议纪要'` 返回 `会议分析已完成`，并产出 transcript/analysis/result/minutes artifacts。团队标准路径应迁移到 `./fixtures/audio_samples/sample_ted_talk.mp3`。

### 用户态手工用例

1. 确认 FunASR 服务可用：
   ```bash
   curl -sS --max-time 5 http://127.0.0.1:8001/health
   ```
   预期：返回 `{"status":"ok","service":"funasr"}`。

2. 通过 Gateway RPC 查看会议能力：
   ```bash
   python3 -m apps.gateway.stdio_server
   ```
   输入：
   ```json
   {"id":"m1","method":"meeting.capabilities","params":{}}
   ```
   预期：返回包含 `meeting_process_file`、`meeting_analyze_text`、`meeting_build_minutes`。

3. 处理真实音频：
   ```json
   {"id":"m2","method":"meeting.process_recording","params":{"path":"./fixtures/audio_samples/sample_ted_talk.mp3","engine":"funasr","language":"en"}}
   ```
   预期：返回 `transcript_chars > 0`、`segment_count > 0`、`analysis.theme` 非空、`minutes_path` 存在。

4. 处理音频目录：
   ```json
   {"id":"m3","method":"meeting.process_audio_dir","params":{"audio_dir":"./fixtures/audio_samples","engine":"funasr","language":"en"}}
   ```
   预期：返回 `file_count >= 1`，每个成功项包含 `minutes_path`。

5. 通过聊天/headless 自动编排会议分析：
   ```bash
   python3 -m cli.main run --json '请分析 ./fixtures/audio_samples/sample_ted_talk.mp3，生成会议纪要'
   ```
   预期：`final_text` 包含 `会议分析已完成`、`主题：`、`会议纪要：`，`events[-1].data.meeting` 包含 `transcript_chars > 0`、`segment_count > 0`、`analysis.theme` 和存在的 `minutes_path`。

6. 通过显式 domain 进入会议 workflow：
   ```json
   {"id":"m4","method":"turn.start","params":{"session_id":"<session_id>","domain":"meeting","input":"请分析 ./fixtures/audio_samples/sample_ted_talk.mp3，生成会议纪要"}}
   ```
   预期：返回与第 5 项相同的会议分析结果。

7. 验证较长音频的降级分析：
   ```bash
   python3 -m cli.main run --json '请分析 ./fixtures/audio_samples/sample_ted_talk.mp3，生成会议纪要'
   ```
   预期：命令不再输出 `Separator is found, but chunk is longer than limit`；返回 `会议分析已完成`、`主题：`、`会议纪要：`，并产出 transcript/result/minutes artifacts。若下游完整分析超限，允许使用压缩转写完成降级分析。

## Phase 1-C: Meeting Artifact Store

### 验收标准

- 会议分析完成后，harnessOS 自动登记 `transcript`、`analysis`、`result`、`minutes` 四类产物。
- `turn.completed.data.meeting.artifacts` 必须保留原始文件路径，并新增 harnessOS `artifact_id`。
- `artifact.list` 能按 `session_id` 查询本轮会议产物。
- `artifact.read` 能读取 `minutes.md` 文本和 `analysis.json` JSON。
- 真实音频验收继续使用 `fixtures/audio_samples/`；标准 fixture 未落地时，可使用本机真实音频作为 local validation evidence。
- Phase1-B 的聊天/headless 会议分析命令不回归。

### 自动化用例

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| P1C-A01 | Artifact Registry 单测 | `pytest tests/test_artifact_gateway.py::test_artifact_registry_register_list_get_read` | register/list/get/read 均通过 |
| P1C-A02 | Gateway artifact RPC | `pytest tests/test_artifact_gateway.py` | `artifact.register/list/get/read` 行为正确 |
| P1C-A03 | Meeting artifact integration | `pytest tests/test_meeting_turn_workflow.py` | meeting turn completed 包含 artifact ids |
| P1C-A04 | 真实音频 artifact 验收 | `pytest tests/test_meeting_audio_acceptance.py` | 真实音频产物可通过 artifact id 读取 |
| P1C-A05 | Draw.io XML 校验 | `xmllint --noout docs/architecture/current-vs-target-gap_v2.drawio` | 退出码 0 |

本阶段已验收结果：

- 团队标准真实音频目录：`fixtures/audio_samples/`
- 已处理音频：`TED演讲对话_How to tune your inner voice  Rhonda Ross Daniel A.mp3`
- Gateway session：`sess_a08b1f628ce2`
- Meeting session：`meeting_c4dc4073`
- Minutes artifact id：`art_c27fa88d8d93`
- Analysis artifact id：`art_9c1eb1071d60`
- 自动化结果：`tests/test_artifact_gateway.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_gateway_protocol.py` 为 22 passed。
- 用户态结果：headless 会议分析返回 `analysis/minutes/result/transcript` 四个 artifact id，`artifact.read(art_c27fa88d8d93)` 可读回 `minutes.md`。

### 用户态手工用例

1. 使用真实音频触发会议分析：
   ```bash
   python3 -m cli.main run --json '请分析 ./fixtures/audio_samples/sample_ted_talk.mp3，生成会议纪要'
   ```
   预期：`events[-1].data.meeting.artifacts` 中每个产物包含原始 path 和 `artifact_id`。

2. 查询本轮 session 的 artifacts：
   ```json
   {"id":"a1","method":"artifact.list","params":{"session_id":"<session_id>"}}
   ```
   预期：返回至少 4 个 artifact，kind 包含 `transcript`、`analysis`、`result`、`minutes`。

3. 读取会议纪要：
   ```json
   {"id":"a2","method":"artifact.read","params":{"artifact_id":"<minutes_artifact_id>"}}
   ```
   预期：返回 markdown 文本，包含会议主题或章节内容。

4. 读取分析 JSON：
   ```json
   {"id":"a3","method":"artifact.read","params":{"artifact_id":"<analysis_artifact_id>"}}
   ```
   预期：返回可解析 JSON，包含 `theme`、`chapters` 或等价结构。

## Phase 1-D: Lead Orchestrator 与 Domain Workflow Registry

### 验收标准

- MeetingWorkflow 不再作为 `GatewayRuntimePool` 中的硬编码特例，而是作为 `DomainWorkflow` 注册到 workflow registry。
- `turn.start(domain=meeting)` 和普通会议音频路径仍能路由到会议 workflow。
- 普通聊天，例如 `你好`，仍走普通 assistant。
- 知识类请求能路由到 knowledge workflow，并返回来源引用。
- 面试关键词不触发会议 workflow。
- 会议结果仍包含 artifact id。

### 自动化用例

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| P1D-A01 | DomainWorkflow contract | `pytest tests/test_lead_orchestrator.py::test_workflow_registry_selects_explicit_domain` | meeting/knowledge workflow 均满足接口 |
| P1D-A02 | Lead Orchestrator routing | `pytest tests/test_lead_orchestrator.py` | meeting、knowledge、generic chat 路由正确 |
| P1D-A03 | Meeting regression | `pytest tests/test_meeting_turn_workflow.py` | 真实音频、artifact id、防误路由均通过 |
| P1D-A04 | Knowledge workflow MVP | `pytest tests/test_lead_orchestrator.py::test_lead_orchestrator_runs_knowledge_workflow` | knowledge workflow 返回检索结果 |
| P1D-A05 | Draw.io XML 校验 | `xmllint --noout docs/architecture/current-vs-target-gap_v2.drawio` | 退出码 0 |

本阶段已验收结果：

- Gateway session：`sess_2858157d522e`
- Meeting session：`meeting_882541b5`
- Minutes artifact id：`art_3b24d8ee4fe2`
- Workflow：`meeting.workflow`
- 自动化结果：`tests/test_lead_orchestrator.py tests/test_artifact_gateway.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_meeting_audio_acceptance.py tests/test_gateway_protocol.py tests/test_rpc_stdio_compat.py tests/test_cli_headless.py` 为 30 passed。
- 用户态结果：`python3 -m cli.main run '你好'` 走普通 chat；`python3 -m cli.main run --domain knowledge '检索知识库 会议 MCP'` 进入 `knowledge.workflow`。

### 用户态手工用例

1. 会议路由回归：
   ```bash
   python3 -m cli.main run --json '请分析 ./fixtures/audio_samples/sample_ted_talk.mp3，生成会议纪要'
   ```
   预期：仍返回会议分析、会议纪要路径和 artifact id。

2. 普通聊天不误路由：
   ```bash
   python3 -m cli.main run '你好'
   ```
   预期：返回普通 assistant 回复，不出现 `会议分析已完成`。

3. 知识 workflow：
   ```bash
   python3 -m cli.main run --json '检索知识库中关于会议 MCP 的设计，并给出来源'
   ```
   预期：进入 knowledge workflow，返回答案和 source references。

## Phase 2: 生产化与治理

### 验收标准

- Phase 2-A：普通聊天、会议真实音频分析、artifact 读取都能生成并查询 trace。已完成 MVP。
- Phase 2-B：`approval.request/list/get/approve/reject` 可用，审批状态可持久化查询。已完成 MVP。
- Phase 2-C：写入、发送、发布类请求默认需要 approval；只读请求和会议分析不触发审批。已完成 MVP。
- Phase 2-D：policy-blocked turn 支持 approval 通过后 retry/resume，且同一 retry context 不会重复执行。已完成 MVP。
- Phase 2-E：secrets 不进入持久化日志、trace、approval、retry 和 artifact read/register metadata 明文。已完成 MVP。
- Phase 2-F：本地 JSON/JSONL 持久化写入加锁并原子化，缓解并发写丢记录和坏 JSON 风险。已完成 MVP。
- Phase 3-A：FastAPI route 不再持有模块级 `_gateway`，GatewayService 通过 app lifecycle 和 dependency injection 获取。已完成 MVP。
- Baseline v1.5 文档先行：项目目标升级为本地优先 Agent OS / App Server Core；文档、测试计划和架构图作为后续迁移基线，并随每次迁移同步更新。
- Baseline v1.5-A：`Session / Thread / Turn / Item / Artifact / Trace / Approval / Retry` 等协议模型与 SQLite Store 基础层已完成；新增 `CoreAppService` 作为 Core 服务门面；Gateway session start/close、turn/item 生命周期、会议产物和治理记录已通过 CoreAppService 写入 Core SQLite，并提供最小查询 RPC。`GatewayRuntimePool` 与 `GatewayService` 不再暴露 `CoreRuntimeRecorder`。
- Baseline v1.5-E：Runtime Adapter Boundary MVP 已完成；Gateway 通过 `RuntimeHandle`/`RuntimeAdapter` 管理 Simple/OpenHarness runtime，不再直接创建运行时内部对象。
- V2.0 目标架构采纳：`docs/design/V2.0/harnessos_architecture_master_spec_v2.md` 已作为正式目标架构主干；当前事实基线是 Baseline v1.5-E，当前主验收阶段是 Phase 4-B1 Meeting Artifact Lineage Acceptance，后续按 V2.0 方向渐进迁移，不立即做大规模目录搬迁。
- 会议验收继续使用标准样本或本机真实音频；会议、知识、普通聊天不回归。
- 下一代码阶段允许破坏旧 Gateway method 命名和响应结构，以 Core-native RPC 为准。

### 开发阶段拆分

| 子阶段 | 目标 | 自动化用例 | 手工验收 |
| --- | --- | --- | --- |
| Phase 2-A Trace/Audit MVP | 建立 trace_id 与 trace store | `tests/test_trace_gateway.py` | 已完成：普通聊天、会议分析、artifact 操作后可查询 trace |
| Phase 2-B Approval Coordinator MVP | 建立审批状态机与 RPC | `tests/test_approval_gateway.py` | 已完成：手工创建、拒绝、批准 approval，并可通过 trace 查询 |
| Phase 2-C Policy Rules MVP | 写/发/发布类操作默认审批 | `tests/test_policy_approval.py` | 已完成：写文件请求进入 pending approval，只读请求放行 |
| Phase 2-D Retry/Resume MVP | 失败 turn/workflow 可恢复，批准后续跑原动作 | `tests/test_retry_resume.py` | 已完成：pending 阻断、approved 后 retry 成功、防重复 retry |
| Phase 2-E Secret Hygiene | trace/log/artifact 脱敏 | `tests/test_secret_hygiene.py` | 已完成：输入 `sk-*` 后持久化日志、trace、approval、retry、artifact read 不出现明文 |
| Phase 2-F Architecture Hardening | 本地存储并发安全 | `tests/test_gateway_persistence.py` | 已完成：approval/retry/artifact 并发写不丢记录，snapshot 可原子读回 |
| Phase 3-A App Lifecycle | API service 生命周期与注入 | `tests/test_api_runs.py` | 已完成：`create_app(gateway_service=...)` 注入的 service 被 `/v1/runs` 和 `/v1/rpc` 共享 |
| Baseline v1.5 文档先行 | 同步 Core / Store / Pack / Job / Policy 目标设计 | `xmllint` + 文档审阅 | 已完成，并作为后续迁移阶段的持续更新基线 |
| Baseline v1.5-A Protocol + Store | Core 对象模型、CoreAppService 与 SQLite Store | `tests/test_core_v15_protocol_store.py`、`tests/test_gateway_protocol.py` | 已完成基础层：模型 round-trip、CoreAppService、SQLite CRUD/过滤、legacy session import、session/turn/item/artifact/trace/approval/retry 原生 mutation/conversion、移除 Gateway runtime recorder 依赖 |
| Baseline v1.5-E Runtime Adapter Boundary | Simple/OpenHarness 上层运行时边界收敛 | `tests/test_runtime_adapter.py`、`tests/test_gateway_protocol.py::test_gateway_runtime_bundle_backend_paths` | 已完成 MVP：RuntimeHandle/RuntimeAdapter、SimpleRuntimeAdapter、OpenHarnessRuntimeAdapter、Gateway adapter 启停/调用/stream/continue/close；治理注入已在 Roadmap Phase 3-D 完成 MVP |
| V2.0 Target Architecture | 正式目标架构升级为 Protocol-first Harness Core + OS-like App Server + Domain Pack Platform | 文档审阅 + `xmllint` | 已完成文档基线：目标架构、当前差距、设计缺陷、下一阶段优先级已同步 |
| Roadmap Phase 3-B Core-native Session/Event Store | Core Store 成为 session/event 主路径 | `pytest tests/test_core_v15_protocol_store.py tests/test_gateway_protocol.py tests/test_api_runs.py tests/test_gateway_persistence.py` | 已完成 MVP：可从 Core records 重建 session events/transcript，legacy JSON 兼容读取 |
| Roadmap Phase 3-C Background Job Worker | 同步 Job Record & Tracking MVP 升级为后台长任务服务 | `tests/test_core_v15_protocol_store.py`、`tests/test_gateway_protocol.py`、`tests/test_gateway_stdio.py` | 已完成 MVP：本地 in-process worker、job.events、cancel/failure_context 可查询；会议同步路径写完整 job events |
| Roadmap Phase 3-D Adapter-level Governance Injection | Runtime Adapter 默认注入治理上下文 | `pytest tests/test_runtime_adapter.py tests/test_tool_policy_middleware.py` | 已完成 MVP：Simple/OpenHarness 默认路径注入 policy/approval/trace/tool metadata，未审批高风险工具不得执行 |
| Roadmap Phase 3-E Pack Assembly MVP | pack manifest 驱动装配 | `python3 -m pytest tests/test_pack_registry.py tests/test_lead_orchestrator.py tests/test_gateway_protocol.py tests/test_meeting_turn_workflow.py`；`python3 -m pytest tests/test_meeting_audio_acceptance.py tests/test_meeting_turn_workflow.py::test_phase1b_real_audio_turn_start_acceptance` | meeting/knowledge 由 pack assembly 注册；`pack.list/get` 返回 assembly 状态；缺 connector 返回可解释错误；真实音频验收通过 |
| Roadmap Phase 3-F Connector Registry MVP | Meeting MCP 进入 connector registry | `python3 -m pytest tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_pack_registry.py tests/test_meeting_gateway.py tests/test_meeting_turn_workflow.py -k 'not phase1b_real_audio_turn_start_acceptance'` | connector list/get/health 可发现并验证 Meeting MCP；定向回归 40 passed |

### 自动化用例

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| P2-A01 | Trace store 单测 | `pytest tests/test_trace_gateway.py` | trace 可写入、查询，并关联 session/turn/workflow/artifact |
| P2-A02 | 普通聊天 trace | `pytest tests/test_gateway_protocol.py::test_turn_start_records_trace` | `turn.completed` 可通过 trace 查询 |
| P2-A03 | 会议 trace 回归 | `pytest tests/test_meeting_turn_workflow.py tests/test_meeting_audio_acceptance.py` | 真实音频会议分析产物和 trace 关联 |
| P2-B01 | Approval 状态机 | `pytest tests/test_approval_gateway.py` | pending -> approved/rejected 状态转换正确 |
| P2-B02 | Approval stdio/RPC 同构 | `pytest tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py` | stdio 与 service 返回结构一致 |
| P2-C01 | Policy 写操作拦截 | `pytest tests/test_policy_approval.py` | workspace write 生成 approval request |
| P2-C02 | Policy 只读放行 | `pytest tests/test_policy_approval.py` | read/list/search 不触发审批 |
| P2-C03 | Policy 会议放行 | `pytest tests/test_policy_approval.py` | `生成会议纪要` 不误触发写入审批 |
| P2-C04 | Policy RPC/工具分类 | `pytest tests/test_policy_approval.py` | `workspace_write_file` 需审批，`workspace_read_file` 不审批 |
| P2-D01 | Retry 失败 turn | `pytest tests/test_retry_resume.py` | 模拟失败后 retry 成功，events 连续 |
| P2-D02 | Retry 不破坏会议 | `pytest tests/test_meeting_gateway.py tests/test_meeting_turn_workflow.py` | 会议 workflow 与 artifact id 不回归 |
| P2-E01 | Secret 脱敏 | `pytest tests/test_secret_hygiene.py` | `sk-*`、Authorization、token 明文被 mask |
| P3-A01 | App lifecycle service 注入 | `pytest tests/test_api_runs.py::test_create_app_accepts_injected_gateway_service` | 注入的 GatewayService 被 API route 使用，session 状态可通过同一实例读取 |
| C15-D01 | Baseline v1.5 文档一致性 | 文档审阅 | `CURRENT-STATUS`、`current-vs-target-gap`、Phase 3 设计、测试计划、drawio 均指向同一目标 |
| C15-D02 | drawio XML 校验 | `xmllint --noout docs/architecture/current-vs-target-gap_v2.drawio` | 图文件 XML 合法 |
| C15-A01 | Core protocol models | `pytest tests/test_core_v15_protocol_store.py::test_core_protocol_objects_round_trip` | Core 对象 id、字段和 content 可序列化 |
| C15-A01b | CoreAppService facade | `pytest tests/test_core_v15_protocol_store.py::test_core_app_service_records_runtime_session_via_native_mutation` | CoreAppService 可用原生 mutation 记录并更新 Gateway runtime session |
| C15-A01c | Core turn/item native mutation | `pytest tests/test_core_v15_protocol_store.py::test_core_app_service_records_gateway_events_via_native_mutation` | CoreAppService 可用原生 mutation 记录 Gateway turn/item 事件 |
| C15-A01d | Core artifact/governance native mutation | `pytest tests/test_core_v15_protocol_store.py::test_core_app_service_records_governance_and_artifacts_via_native_mutation` | CoreAppService 可用原生转换路径记录 artifact/trace/approval/retry |
| C15-A02 | Core SQLite CRUD | `pytest tests/test_core_v15_protocol_store.py::test_core_sqlite_store_crud_and_filters` | session/thread/turn/item/job/artifact/trace/approval/retry 可保存、读取、过滤 |
| C15-A03 | Legacy session import | `pytest tests/test_core_v15_protocol_store.py::test_core_sqlite_store_imports_legacy_gateway_sessions` | legacy snapshot/events 可导入为 Core session/thread/turn/items |
| C15-A04 | Gateway Core write | `pytest tests/test_gateway_protocol.py::test_turn_start_mirrors_core_records` | 旧 `turn.start` 写入 Core session/thread/turn/items/trace，并可通过 Core 查询 RPC 读取 |
| C15-A05 | Gateway governance Core write | `pytest tests/test_gateway_protocol.py::test_policy_approval_and_retry_mirror_core_governance_records` | policy-blocked turn 写入 Core approval/retry/trace，并可通过 Core 查询 RPC 读取 |
| C15-A06 | Gateway artifact Core write | `pytest tests/test_gateway_protocol.py::test_turn_completed_artifacts_mirror_core_records` | workflow artifact records 写入 Core artifacts，并可通过 Core 查询 RPC 读取 |
| C15-E01 | Runtime Adapter 边界 | `pytest tests/test_runtime_adapter.py` | Simple/OpenHarness adapter 可启动 handle、invoke/stream/continue，Gateway session 保存 adapter handle |
| V20-D01 | V2.0 目标架构一致性 | 文档审阅 + `xmllint --noout docs/architecture/current-vs-target-gap_v2.drawio` | `CURRENT-STATUS`、V2 target doc、gap、drawio、验收文档均指向同一六大平面 V2.0 目标 |
| P2-R01 | 阶段回归 | `pytest tests/test_lead_orchestrator.py tests/test_artifact_gateway.py tests/test_cli_headless.py tests/test_gateway_protocol.py tests/test_rpc_stdio_compat.py` | Phase 0/1 核心链路不回归 |

Phase 2-A 已验收结果：

- 自动化：`tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_artifact_gateway.py` 为 13 passed。
- 回归：`tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 38 passed。
- 用户态：`python3 -m cli.main run --json '你好'` 返回顶层 `trace_id=trace_f124c372d3f3`。
- stdio 查询：`trace.get(trace_id=trace_f124c372d3f3)` 返回 turn、tool、delta、completed 等 trace records。

Phase 2-B 已验收结果：

- 自动化：`tests/test_approval_gateway.py tests/test_gateway_stdio.py tests/test_trace_gateway.py` 为 11 passed。
- 回归：`tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 42 passed。
- 用户态：通过 stdio JSONL 创建 `approval_id=appr_df10a7c3946c`，状态为 `pending`。
- 用户态：通过 `approval.approve` 批准后，`trace.get(trace_manual_phase2b)` 返回 `approval.request` 与 `approval.approve` 两条记录。

Phase 2-C 已验收结果：

- 自动化：`tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py` 为 10 passed。
- 回归：`tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 45 passed。
- 写入类 turn：`请在 workspace 下写入 phase2c.txt，内容为 hello` 会返回 `操作需要审批`，并创建 `approval.status=pending`。
- 用户态写入类 smoke：`phase2c_policy_manual.txt` 请求返回 `approval_id=appr_1532cf6d65fc`、`trace_id=trace_030c83793b25`，目标文件未创建。
- 只读类 turn：`请读取 README 并总结当前项目` 不创建 approval，继续进入普通 agent。
- 会议类输入：`请分析会议音频 /tmp/demo.mp3，生成会议纪要` 不因“生成会议纪要”误触发写入审批。
- `policy.evaluate` 可区分 `workspace_write_file` 和 `workspace_read_file`。

Phase 2-D 已验收结果：

- 自动化：`tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py` 为 12 passed。
- 回归：`tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 47 passed。
- pending approval 执行 `turn.retry` 会返回错误，不执行原动作。
- approval 通过后，`turn.retry` 能按 `approval_id` 或原 `turn_id` 找到 retry context 并继续执行原动作。
- retry turn 的 `turn.started.data` 包含 `retry_of_turn_id` 和 `approval_id`。
- 同一 retry context 重复执行会返回错误，避免重复写入/重复发布。

Phase 2-E 已验收结果：

- 自动化：`tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py` 为 15 passed。
- 回归：`tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 50 passed。
- `events.jsonl` 与 TraceStore 中不出现 `sk-test-1234567890` 和 bearer token 明文。
- ApprovalStore 与 RetryStore 中不出现被拦截写入请求里的 `sk-*` 明文。
- `artifact.read` 返回内容和 artifact metadata 不出现 `api_key/token/Authorization` 明文。

Phase 2-F 已验收结果：

- 自动化：`tests/test_gateway_persistence.py tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py` 为 19 passed。
- 回归：`tests/test_gateway_persistence.py tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 54 passed。
- ApprovalStore 40 个并发 request 不丢记录。
- RetryStore 40 个并发 context 创建不丢记录。
- ArtifactRegistry 40 个并发 register 不丢记录。
- Session snapshot 原子写入后可正常读回。

Phase 3-A 已验收结果：

- 自动化：`tests/test_api_runs.py tests/test_gateway_persistence.py tests/test_gateway_protocol.py` 为 15 passed。
- 回归：`tests/test_api_runs.py tests/test_gateway_persistence.py tests/test_secret_hygiene.py tests/test_retry_resume.py tests/test_policy_approval.py tests/test_approval_gateway.py tests/test_trace_gateway.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_rpc_stdio_compat.py tests/test_meeting_turn_workflow.py tests/test_meeting_gateway.py tests/test_cli_headless.py tests/test_lead_orchestrator.py` 为 57 passed。
- `create_app(gateway_service=...)` 注入的 GatewayService 可被 `/v1/runs` 创建 session，并被 `/v1/rpc health.ping` 看到同一 active session 状态。
- route 模块不再持有 `_gateway = GatewayService()`；API 层通过 app state 和 FastAPI dependency 获取 service。

Baseline v1.5 文档先行验收标准：

- `CURRENT-STATUS_v2.md` 明确下一阶段为本地优先 Agent OS / App Server Core。
- `current-vs-target-gap_v2.md` 明确当前 Gateway/Workflow/治理 primitives 与目标 Core/Pack/Job/SQLite 的差距。
- `04_PHASE3_DETAILED_ARCHITECTURE.md` 定义 `Session / Thread / Turn / Item / Job / Artifact / Approval / Connector`。
- `acceptance-test-cases_v2.md` 与 `test-acceptance-plan_v2.md` 已从文档先行基线更新为 Baseline v1.5-A 完成状态，并指向后续 Baseline v1.5-B Pack Visibility & Manifest MVP。
- `current-vs-target-gap_v2.drawio` 已更新为当前 Baseline v1.5-E / Roadmap Phase 3-D 架构 vs V2.0 目标架构。

Baseline v1.5 代码阶段验收标准：

- 普通 `你好` 能创建 session/thread/turn/items，并可通过 Core RPC 查询。
- SQLite 默认写入 `.harnessos/core.sqlite3`，legacy JSON/JSONL 可导入或读取。
- `pack.list` 返回 meeting、knowledge、investment、interview、video_studio。
- meeting/knowledge/video_studio 是真实 pack；investment/interview 是 manifest stub。
- 会议真实音频通过 Meeting Pack 创建 job，完成后关联 transcript/minutes/analysis/result artifacts。
- Tool Policy Middleware 在工具执行层阻断未审批的写/删/发/发布/交易类动作。

Baseline v1.5-A 已验收结果：

- 自动化：`tests/test_core_v15_protocol_store.py tests/test_gateway_protocol.py` 为 17 passed。
- 治理回归：`tests/test_approval_gateway.py tests/test_policy_approval.py tests/test_retry_resume.py tests/test_secret_hygiene.py tests/test_gateway_stdio.py` 为 15 passed。
- 编译：`PYTHONPYCACHEPREFIX=/tmp/harnessos-pycache python3 -m compileall core/protocol core/stores apps/gateway tests/test_core_v15_protocol_store.py tests/test_gateway_protocol.py` 通过。
- Service facade：`CoreAppService` 已接管 Gateway 对 Core Store 的查询，以及 session/turn/item/artifact/trace/approval/retry 原生 mutation/conversion 入口。
- Runtime dependency：`GatewayRuntimePool` 与 `GatewayService` 不再暴露 `CoreRuntimeRecorder`；该模块只作为 legacy compatibility code 保留。
- Gateway Core 写入：`tests/test_gateway_protocol.py::test_turn_start_mirrors_core_records` 通过，证明现有 `turn.start` 已写入 Core SQLite session/thread/turn/items/trace。
- Artifact Core 写入：`tests/test_gateway_protocol.py::test_turn_completed_artifacts_mirror_core_records` 通过，证明会议/workflow 产物已写入 Core artifacts。
- Governance Core 写入：`tests/test_gateway_protocol.py::test_policy_approval_and_retry_mirror_core_governance_records` 通过，证明 policy-blocked turn 已写入 Core approval/retry/trace。
- 查询 RPC：`session.get`、`thread.list`、`turn.get`、`turn.items`、`core.artifact.list`、`core.trace.list`、`core.approval.list`、`core.retry.list` 可读取 Core records。
- 用户态命令验收：使用本机 TED 音频样本成功生成会议纪要；Core SQLite 中 `turn_bb1be285fcef` 关联 `analysis=art_aa191af7547a`、`minutes=art_964dae1ba8ed`、`result=art_92c69a69b94e`、`transcript=art_e4c60cd13dc2`。团队标准路径应迁移到 `./fixtures/audio_samples/sample_ted_talk.mp3`。
- Baseline v1.5-A 状态：已完成。旧 Gateway snapshot/events/trace/approval/retry stores 仍作为 runtime 兼容源保留，后续在 Runtime Adapter 和 Core-native App Server 阶段继续收敛。

Baseline v1.5-B Pack Visibility & Manifest MVP 已验收结果：

- `core.packs.PackRegistry` 已加载 `packs/*/manifest.json`。
- `pack.list` 返回 meeting、knowledge、investment、interview、video_studio。
- `pack.get` 可按 `name` 或 `domain` 获取 pack manifest。
- meeting/knowledge 为 active pack；investment/interview/video_studio 为 manifest stub。
- `workflow.list` 返回 meeting/knowledge workflow，并带有 `pack_name`、`pack_version`、`pack_status`。
- 自动化：`tests/test_pack_registry.py tests/test_gateway_protocol.py tests/test_lead_orchestrator.py tests/test_gateway_stdio.py` 为 22 passed。
- 阶段相关完整回归：70 passed。
- Draw.io：`docs/architecture/current-vs-target-gap_v2.drawio` XML 校验通过。
- 用户态真实音频验收：使用本机 TED 音频样本成功生成会议纪要、转写、分析、result，并在验收后清理 `meeting_c5c47fc9` 外部产物和本地 `.harnessos` 验收记录。团队标准路径应迁移到 `./fixtures/audio_samples/sample_ted_talk.mp3`。

Baseline v1.5-C Job Record & Tracking MVP 已验收结果：

- `CoreAppService` 已提供 job lifecycle mutation/query。
- DomainWorkflow 执行时会创建 Core job，完成后写入 `status=completed`、`progress=1.0` 和 artifact ids。
- `turn.completed.data` 包含 `job_id` 和完整 `job` 记录。
- Gateway RPC 支持 `job.list`、`job.get`、`job.cancel`、`core.job.list`。
- 自动化：`tests/test_core_v15_protocol_store.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py tests/test_lead_orchestrator.py tests/test_meeting_turn_workflow.py` 为 36 passed。
- 阶段相关完整回归：72 passed。
- Draw.io：`docs/architecture/current-vs-target-gap_v2.drawio` XML 校验通过。
- 用户态真实音频验收：使用本机 TED 音频样本成功生成会议纪要，并创建 `job_c3f8541207ed`，状态为 `completed`，关联 transcript/minutes/analysis/result 四个 artifact；验收后已清理 `meeting_1400e111` 外部产物和本地 `.harnessos` 验收记录。团队标准路径应迁移到 `./fixtures/audio_samples/sample_ted_talk.mp3`。
- 当前阶段是同步 Job MVP，后台 worker、进度事件流和运行中取消留到后续阶段。

Baseline v1.5-D Tool Execution Guard MVP 已验收结果：

- builtin tools 经过 `tools.policy_guard` 包装后，未审批的 `workspace_write_file` 不会创建文件。
- `approved=True` 或 approved `approval_id` 可放行 mutating tool。
- read-only tool 不触发阻断。
- Core engine `_execute_tool_call` 在 `tool.execute(...)` 前阻断未审批 mutating tool。
- 自动化：`tests/test_tool_policy_middleware.py tests/test_policy_approval.py tests/test_gateway_protocol.py` 为 20 passed。
- 阶段相关完整回归：77 passed。
- Draw.io：`docs/architecture/current-vs-target-gap_v2.drawio` XML 校验通过。
- 用户态真实音频验收：使用本机 TED 音频样本成功生成会议纪要，并创建 `job_741a70df5a79`，状态为 `completed`；验收后已清理 `meeting_338e1a81` 外部产物和本地 `.harnessos` 验收记录。团队标准路径应迁移到 `./fixtures/audio_samples/sample_ted_talk.mp3`。
- 当前阶段是执行层阻断 MVP，工具层自动创建 approval request 和所有 runtime adapter 默认注入留到后续阶段。

Baseline v1.5-E Runtime Adapter Boundary MVP 已验收结果：

- `core.runtime_adapter` 新增 `RuntimeHandle`、`RuntimeAdapter`、`SimpleRuntimeAdapter`、`OpenHarnessRuntimeAdapter`。
- `GatewayRuntimePool.start_session` 通过 adapter 创建 runtime，`stream_turn` 通过 adapter invoke/stream，`continue_turn` 通过 adapter continue，`close_session` 通过 adapter close。
- fake agent 注入、Simple fallback 和 OpenHarness RuntimeBundle 测试路径均保持兼容。
- 自动化定向验收：`tests/test_runtime_adapter.py tests/test_gateway_protocol.py::test_gateway_runtime_bundle_backend_paths` 为 5 passed。
- 自动化阶段定向回归：`tests/test_runtime_adapter.py tests/test_gateway_protocol.py tests/test_rpc_stdio_compat.py tests/test_cli_headless.py` 为 20 passed。
- 阶段相关完整回归：81 passed。
- Draw.io：`docs/architecture/current-vs-target-gap_v2.drawio` XML 校验通过。
- 用户态真实音频验收：使用本机 TED 音频样本成功生成会议纪要，并创建 `job_e881abee5217`，状态为 `completed`，关联 transcript/minutes/analysis/result 四个 artifact；验收后已清理 `meeting_ebdc8357` 外部产物和本地 `.harnessos` 验收记录。团队标准路径应迁移到 `./fixtures/audio_samples/sample_ted_talk.mp3`。
- 当前阶段是运行时边界收敛和 adapter-level governance injection 均已完成 MVP；Core-native session/event store 已在 Roadmap Phase 3-B 完成 MVP，Background Job Worker 已在 Roadmap Phase 3-C 完成本地 in-process MVP。

V2.0 目标架构采纳验收结果：

- `harnessos_architecture_master_spec_v2.md` 已评估为高质量目标架构蓝图，但不是接口冻结规格。
- 新增 `docs/architecture/harnessos_target_architecture_v2.md`，明确 V2.0 目标、与 Baseline v1.5-E 的关系、设计缺陷和下一阶段落地顺序。
- V2.0 目标架构统一采用六大平面：Client/Gateway、Protocol App Server、Harness Core、Runtime Adapter、Domain Pack、Connector/Tool/Store。
- `CURRENT-STATUS_v2.md`、`current-vs-target-gap_v2.md`、`current-vs-target-gap_v2.drawio`、`test-acceptance-plan_v2.md` 和本文件已同步 V2.0 目标。
- 下一阶段验收仍要求真实会议音频闭环，并在验收后清理外部会议产物和 `.harnessos` 验收记录。

V2.0 Phase 3+ 开发计划验收口径：

- Phase 1 已完成 MVP：Meeting MCP、真实音频分析、会议产物登记、通用编排和 KnowledgeWorkflow MVP 已验收。
- Phase 2 已完成 MVP：Trace、Approval、Policy、Retry、Secret Hygiene 和 Persistence Hardening 已验收。
- Phase 3-A 已完成：API App Lifecycle 和 GatewayService DI 已验收。
- Roadmap Phase 3-E/3-F 已完成 MVP。
- Phase 4-A Video Studio Pack MVP 已完成，`video.workflow` 可生成 brief/script/storyboard/shot_list 四类规划 artifact。
- Phase 4-B0 Domain Pack Workflow Loader 已完成，meeting/knowledge/video workflow 实现已迁入对应 pack module，Meeting MCP client/service 已迁入 `packs/meeting/connector.py`，Gateway 只保留 workflow registry/orchestrator/factory 与旧导入兼容面。
- Phase 4-B1 Artifact Lineage Query MVP 已完成，`artifact.lineage` / `core.artifact.lineage` 可查询 Meeting workflow 用户态验收链路；Video Studio 规划链路保留自动化覆盖。
- Phase 4-B2 Remote ComfyUI / Render Manifest Scaffold 已延期保留，`remote_comfyui` connector 可查询但不执行远程渲染，不作为当前用户态验收线。
- Review Cleanup Gate 的 2026-04-30 P0/P1 清理批次已完成；Phase 5-A Pack DSL / Skill / Policy Bundle Assembly、Phase 5-B Memory & Session Intelligence、Phase 5-C Connector Execution Runtime 和 Phase 5-D Cross-domain MCP Workflow Stabilization 已完成当前 MVP；后续进入 Phase 5-D hardening 或 Phase 6 Productization。Remote ComfyUI Execution Adapter 延期到后续远程 Connector 阶段。

Phase 4-A / 4-B0 已验收结果：

- `video_studio` 为 active pack，`workflow.list` 可返回 `video.workflow` 及 pack metadata。
- `turn.start(domain=video_studio)` 可生成四类规划 artifact，并写入 Core job/trace/artifact 链路。
- `packs/meeting/workflow.py` 承载 `meeting.workflow` 的业务实现，默认 runtime/orchestrator 使用 pack 版本。
- `packs/meeting/connector.py` 承载 Meeting MCP stdio client 与 `MeetingGatewayService`。
- `packs/knowledge/workflow.py` 承载 `knowledge.workflow` 的业务实现。
- `packs/video_studio/workflow.py` 承载 `video.workflow` 的业务实现。
- `apps/gateway/workflows.py` 不再承载 meeting/knowledge/video 的具体业务流程。
- 定向回归：`tests/test_lead_orchestrator.py tests/test_pack_registry.py tests/test_gateway_protocol.py::test_video_studio_workflow_registers_planning_artifacts tests/test_gateway_stdio.py::test_stdio_server_workflow_list` 为 10 passed。
- `artifact.lineage(session_id, domain=meeting)` 可返回 `transcript -> analysis -> result -> minutes` 的 artifacts、edges、roots、leaves。
- `artifact.lineage(session_id, domain=video_studio)` 仍在自动化中覆盖 `brief -> script -> storyboard -> shot_list -> asset_plan -> render_output`。
- Phase 4-B1 定向回归：`tests/test_meeting_turn_workflow.py::test_turn_start_meeting_registers_artifacts tests/test_gateway_protocol.py::test_video_studio_workflow_registers_planning_artifacts tests/test_core_v15_protocol_store.py tests/test_artifact_gateway.py` 为 13 passed。
- Phase 4-B2 scaffold 定向回归仅用于防止预留边界回退，不属于当前用户态验收：`tests/test_gateway_protocol.py::test_gateway_connector_registry_lists_meeting_mcp tests/test_gateway_protocol.py::test_video_studio_workflow_registers_planning_artifacts tests/test_pack_registry.py tests/test_lead_orchestrator.py::test_lead_orchestrator_runs_video_studio_workflow`。

Roadmap Phase 3-B 已验收结果：

- `CoreAppService` 新增 Core-native session snapshot、session list、session events、transcript 重建能力。
- `session.list/read/events/transcript` 已优先从 Core records 查询或重建，legacy JSON/JSONL 保留为兼容回退。
- 定向回归：`tests/test_core_v15_protocol_store.py tests/test_gateway_protocol.py tests/test_api_runs.py tests/test_gateway_persistence.py` 为 26 passed。
- 阶段完整回归：包含 API、persistence、secret、retry、policy、approval、trace、artifact、gateway、stdio、meeting、CLI、orchestrator、Core Store、Pack、Tool Policy、Runtime Adapter 的 83 tests passed。
- 用户态真实音频验收：使用本机 TED 音频样本成功生成会议纪要，并创建 `job_5fbee48cc68c`，状态为 `completed`，关联 transcript/minutes/analysis/result 四个 artifact；验收后已清理 `meeting_df894f3d` 外部产物和本地 `.harnessos` 验收记录。团队标准路径应迁移到 `fixtures/audio_samples/sample_ted_talk.mp3`。
- Draw.io：`xmllint --noout docs/architecture/current-vs-target-gap_v2.drawio` 通过。
- Roadmap Phase 3-D Adapter-level Governance Injection MVP 已完成；Roadmap Phase 3-E/3-F、Phase 4-A、Phase 4-B0 和 Phase 4-B1 后续也已完成。Phase 4-B2 ComfyUI 相关代码延期保留，当前继续 Meeting artifact lineage 用户态验收闭环。
- 剩余开发计划按 Phase 5-D hardening、Phase 6 推进：Cross-domain MCP Workflow Stabilization 的超时/取消/retryable failure/可观测性补强，以及 Productization。Review Cleanup Gate 已完成本批次 P0/P1 清理，并将在每次大阶段完成后继续更新。Phase 4-C Core-native RPC Router、Phase 4-D Tool-level Approval Automation、Phase 5-A Pack DSL/Skill/Policy Bundle Assembly、Phase 5-B Memory & Session Intelligence、Phase 5-C Connector Execution Runtime 和 Phase 5-D Cross-domain MCP Workflow Stabilization 已完成当前 MVP。

### 后续阶段验收标准

| 阶段 | 用户态验收 | 自动化验收 |
| --- | --- | --- |
| Phase 4-C Core-native RPC Router | `scripts/e2e_meeting_validation.sh` 通过；RPC/stdio/headless 行为不变 | method registry、capability registry、unknown method、invalid params、handler failure 回归 |
| Phase 4-D Tool-level Approval Automation | 写文件类请求返回 approval id，批准后可 retry | tool policy、approval、retry、trace 串联测试 |
| Review Cleanup Gate | 2026-04-30 清理批次已完成；后续大阶段完成后持续更新 | 代码检视清单、drawio XML、二次检视、阶段并行验收；本批次 HarnessOS `tests/` 为 113 passed、1 skipped |
| Phase 5-A Pack DSL / Skill / Policy Bundle Assembly | 已完成 MVP：`pack.get(domain=knowledge)` 展示 Typed DAG、Pack-owned agents、data_service_mcp contract 和 blocked reason；Meeting 真实音频不回归 | 42 项 Phase 5-A 定向回归；HarnessOS `tests/` 主线 125 passed、1 skipped；真实音频依赖启动 FunASR 后 2 passed |
| Phase 5-B Memory & Session Intelligence | 已完成 MVP：Meeting 多轮追问可通过 memory refs 引用前序 transcript/minutes，普通 turn 可注入 session summary | Core memory、Gateway memory RPC、artifact-backed memory、secret masking、retry 原样重放回归；默认本地 128 passed、1 skipped、2 deselected；真实音频 2 passed |
| Phase 5-C Connector Execution Runtime | 已完成当前 MVP：轻量 connector 可 submit/poll/cancel/collect；data_service_mcp gated stdio 真实 E2E 通过；ComfyUI 未配置不影响主线 | connector job lifecycle、job.events、artifact collect、fake MCP、真实 data_service E2E |
| Phase 5-D Cross-domain MCP Workflow Stabilization | 已完成当前集成 MVP：一条命令跑通 audio -> transcription -> meeting minutes -> knowledge import/build/query；默认测试仍不依赖真实服务 | FunASR MCP smoke、Meeting workflow MCP 转写、cross-domain runner；真实验收 `status=ok`，artifact lineage count `33` |
| Phase 6 Productization / Open Source / Commercial Readiness | 新开发者按文档跑通 smoke + Meeting lineage acceptance | API versioning、extension examples、release docs 检查 |

Roadmap Phase 3-D Adapter-level Governance Injection MVP 已验收结果：

- 定向回归：`tests/test_runtime_adapter.py tests/test_tool_policy_middleware.py`，11 passed。
- 阶段相关回归：runtime adapter、tool policy、gateway、policy、approval、trace、meeting、Core Store 相关 58 tests passed。
- 用户态验收：真实 TED 音频通过 `python3 -m cli.main run --json` 成功生成会议纪要，会议链路未被 adapter-level governance 误拦截。
- 产物链路：生成 session `sess_4fe9d283c297`、turn `turn_4c38dbc1178f`、trace `trace_39830f4e47e3`、job `job_552cbf52c163`，并登记 analysis/minutes/result/transcript 四类 artifact。
- 清理结果：验收后已删除 `meeting_d1c6cc48` 外部会议产物和本地 `.harnessos` 验收记录。
- `docs/architecture/development_plan_v2.md` 是后续开发计划的主文档。

Roadmap Phase 3-C 已验收结果：

- 新增 `core.jobs.BackgroundJobWorker`，支持本地 in-process job submit/wait/cancel。
- 新增 `JobEventRecord`、SQLite `job_events` 表和 `job.events` RPC。
- `job.create` 可创建 queued job；worker 可推进 queued/running/completed/failed/cancelled。
- completed/failed/cancelled 终态 job 的 cancel 会保持终态并记录 `job.cancel_ignored`。
- 失败 job 会记录 `failure_context.error_type/message`。
- 定向回归：`tests/test_core_v15_protocol_store.py tests/test_gateway_protocol.py tests/test_gateway_stdio.py` 为 27 passed。
- 用户态真实音频验收：使用本机 TED 音频样本成功生成会议纪要，并创建 `job_703ecb999341`，状态为 `completed`，关联 transcript/minutes/analysis/result 四个 artifact；`job.events` 返回 `job.queued`、`job.started`、`job.completed`；验收后已清理 `meeting_aa91f008` 外部产物和本地 `.harnessos` 验收记录。
- 当前阶段是 Background Job Worker MVP，不包含分布式队列、多 worker 调度或图形化 job 管理台。

### 用户态手工用例

1. 普通聊天 trace：
   ```bash
   python3 -m cli.main run --json '你好'
   ```
   预期：返回结果中包含 trace_id，或可以通过 session/turn 查询到 trace。

   查询 trace：
   ```bash
   printf '%s\n' '{"id":"t1","method":"trace.get","params":{"trace_id":"<trace_id>"}}' | python3 -m apps.gateway.stdio_server
   ```
   预期：返回同一 trace 下的 `turn.started`、`item.delta`、`turn.completed` 或 `tool.*` 记录。

2. 会议真实音频 trace：
   ```bash
   python3 -m cli.main run --json '请分析 ./fixtures/audio_samples/sample_ted_talk.mp3，生成会议纪要'
   ```
   预期：会议分析完成，trace 关联 `meeting.workflow`、`analysis/minutes/result/transcript` artifacts。

3. 触发写文件审批：
   ```bash
   python3 -m cli.main run --json '请在 workspace 下写入 approval_test.txt，内容为 hello'
   ```
   预期：返回 pending approval，不直接写文件；`final_text` 包含 `操作需要审批` 和 `Approval ID`。

   也可以通过 stdio 直接验证策略分类：
   ```bash
   printf '%s\n' '{"id":"policy-1","method":"policy.evaluate","params":{"tool_name":"workspace_write_file","tool_input":{"file_path":"approval_test.txt"}}}' | python3 -m apps.gateway.stdio_server
   ```
   预期：`decision.requires_approval=true`，`decision.action=workspace.write`。

4. 拒绝审批：
   ```json
   {"id":"p2-reject","method":"approval.reject","params":{"approval_id":"<approval_id>","reason":"manual test"}}
   ```
   预期：文件不存在，trace 中记录 rejected。

5. 批准审批：
   ```json
   {"id":"p2-approve","method":"approval.approve","params":{"approval_id":"<approval_id>"}}
   ```
   预期：审批状态更新为 `approved`，trace 中记录 approved。

   Phase 2-D 当前验收范围：批准后可通过 `turn.retry` 继续原动作。

6. Retry/Resume：
   ```json
   {"id":"p2-retry","method":"turn.retry","params":{"session_id":"<session_id>","turn_id":"<failed_turn_id>"}}
   ```
   预期：已批准的 policy-blocked turn 被重试，新的 events 包含 `retry_of_turn_id` 与 `approval_id`，重复 retry 被拒绝。

7. Secret 脱敏：
   ```bash
   python3 -m cli.main run --json '请记录测试密钥 sk-test-1234567890 和 Authorization: Bearer abcdef'
   ```
   预期：持久化 session events、trace、approval、retry、artifact read/register metadata 中不出现完整密钥明文，出现 `[REDACTED]`。

## V2.0: Protocol-first Harness Core + OS-like App Server

### 验收标准

- `Session / Thread / Turn / Item` 成为协议一级对象。
- SQLite Store 成为默认写入路径。
- meeting/knowledge 已迁移为 manifest-backed Domain Pack。
- investment/interview/video_studio 已以 manifest stub 进入 Pack Registry。
- Job Service MVP 支持创建、查询、取消状态和失败/完成状态；事件流和后台执行留到后续阶段。
- Tool Policy Middleware 已覆盖 builtin tools 与 Core engine tool loop 的 MVP 执行层阻断，而不是只做 turn preflight。
- 会议真实音频仍是端到端验收主场景。

### 用户态手工用例

- 输入 `你好`，检查 session/thread/turn/items 是否可查询。
- 输入真实会议音频路径，检查是否创建 job 并产出 meeting artifacts。
- 查询 `pack.list`，检查五个 pack 是否可见；查询 `pack.get(domain=meeting)`，检查 `meeting.workflow` 是否在 manifest 内。
- 触发写文件请求，检查 Tool Policy Middleware 是否在审批前阻断执行。

## Phase 4: Pack 工作流与 Artifact Lineage

### 验收标准

- 输入短剧 brief，输出脚本、分镜、镜头清单。已完成 Phase 4-A MVP。
- 当前用户态主验收不启动本地视频工作流，不轮询 ComfyUI，不要求远程工作站可用。
- Meeting workflow 的 transcript -> analysis -> result -> minutes artifact lineage 可查询，已完成 Phase 4-B1 用户态验收 MVP。
- Video Studio 的 brief -> script -> storyboard -> shot_list 规划 lineage 保留为自动化回归覆盖。
- Video Studio 的 shot_list -> asset_plan -> render_output manifest lineage 只作为延期 scaffold 保留。
- 真实远程 render output 采集延期到后续远程 Connector 阶段。
- 单镜头或单 render step 失败支持局部重跑。
- 至少连续完成 3 个短剧任务批处理。
- 发布或最终 render 前有人审确认点。

### Phase 4-A MVP 已实现

### Phase 4-B1 Lineage Query MVP 已实现

- `artifact.lineage` / `core.artifact.lineage` 可查询 Meeting 产物链路。
- 当前验收范围不包含 assets/render output、不包含 ComfyUI render、不包含局部重跑。

### Phase 4-B2 Remote ComfyUI / Render Manifest Scaffold 已延期保留

- `remote_comfyui` connector 可通过 `connector.list/get/health` 查询。
- 未配置 `HARNESS_COMFYUI_BASE_URL` 时，`remote_comfyui` health 为 `not_configured`。
- `video.workflow` 生成 `asset_plan` 与 `render_output` manifest artifact。
- 当前验收范围不包含真实远程 ComfyUI 调用、轮询、取消和输出采集；不要求启动 ComfyUI。

- `video_studio` pack 已从 stub 提升为 active。
- `video.workflow` 可由 pack assembly 注册并通过 `turn.start(domain=video_studio)` 触发。
- 默认 workflow 生成 `brief`、`script`、`storyboard`、`shot_list` artifacts。
- 该阶段不调用 ComfyUI、不采集真实 render output、不做批处理和发布审批。

### 用户态手工用例

- 执行 `scripts/e2e_meeting_validation.sh ./fixtures/audio_samples/sample_ted_talk.mp3`，完成 Meeting workflow。
- 检查脚本输出 `status=passed`，并确认 `artifact.lineage(session_id, domain=meeting)` 为 `transcript -> analysis -> result -> minutes`。
- 不执行 ComfyUI render job；ComfyUI 相关测试只保留为 scaffold 自动化回归。

## Phase 5: 开源与商用就绪

### 验收标准

- 外部 API 版本化，核心 schema 冻结到 `v1alpha` 或 `v1beta`。
- tools/skills/plugins 各有 2+ 第三方扩展示例。
- 新开发者 30 分钟内能跑通 smoke test。
- LICENSE、贡献协议、隐私与遥测说明齐全。
- tag、changelog、release note、CI release pipeline 可用。
- 架构文档、扩展开发文档、部署文档齐全。
- 多租户、审计、计费/限流接口预留完成。

### 用户态手工用例

- 按新开发者文档从零安装并跑通 smoke test。
- 安装一个示例 tool/skill/plugin 并运行。
- 执行一次 release dry-run，检查 changelog 和 release note。

## Phase 5-C: FunASR MCP Connector

### 自动化用例

- `funasr_service.mcp_stdio` 的 `tools/list` 返回 `funasr_health` 和 `funasr_recognize_file`。
- `resources/read(funasr://capabilities)` 返回 endpoint、allowed roots、支持格式与文件大小限制。
- `funasr_recognize_file` 在 mock HTTP proxy 下可把本地音频文件转成 `/recognize` multipart 请求，并规范化返回 `status/data.text/data.sentences`。
- 越权路径、symlink、非法后缀、超大文件必须被拒绝。
- harnessOS `connector.list/get/health` 返回 `funasr_mcp`，并隐藏具体敏感配置，仅暴露 `config_ref=HARNESS_FUNASR_MCP_*`。
- `connector.submit(funasr_mcp, funasr_recognize_file)` 当前阶段生成 connector job 与 connector_result artifact。
- 显式设置 `HARNESS_FUNASR_MCP_EXECUTION=stdio` 后，`connector.submit(funasr_mcp, funasr_recognize_file)` 必须走真实 MCP stdio `tools/call` 并写入 governed connector result artifact。

### 手工验收用例

- 启动 FunASR HTTP 服务后，通过 MCP stdio 调用 `funasr_health`，预期返回 `{"status":"ok","service":"funasr"}`。
- 使用 `HARNESS_FUNASR_AUDIO_ROOTS` 指向测试音频目录，调用 `funasr_recognize_file(path=...)`，预期返回非空 transcript 和 sentence 列表。
- 不启动 FunASR HTTP 服务时，默认 harnessOS 测试仍应通过；真实服务调用只作为显式集成验收。

## Phase 5-C: Data Service MCP External Harness E2E

### 自动化用例

- 默认模式：`data_service_mcp` 保持 contract stub，`connector.submit(data_service_mcp, knowledge_query_v2)` 可生成 Core job/events/artifact，不启动外部 MCP server。
- 显式模式：设置 `HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio` 后，connector registry 校验 `python3 -m data_service.mcp_stdio` 的 cwd、command 和 module path。
- stdio MCP client：`connector.submit(data_service_mcp, knowledge_query_v2)` 必须发送 `initialize` 和 `tools/call`，解析 MCP `content[].text` JSON，并写入 `connector_result` artifact。
- 持久 MCP session：真实 Knowledge lifecycle runner 在 stdio 模式下必须复用同一 MCP server 进程，避免 `knowledge_build_start` 后后台 build queue 状态丢失。
- envelope 映射：artifact 中必须保留 MCP 返回的统一 envelope，包含 `workspace_id`、`operation_id`、`status`、`warnings`、`artifact_refs`、`next_actions`、`data`。
- 失败映射：MCP 协议错误或 tool error 必须将 connector job 标记为 `failed`，并写入 retryable `failure_context`。

### 外部真实验收用例

- 启动相邻项目 data_service MCP：

```bash
cd /Users/Zhuanz/Desktop/workspace/meeting-voice-assistant/backend
python3 -m data_service.mcp_stdio
```

- 配置 Harness 侧环境：

```bash
export HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio
export HARNESS_DATA_SERVICE_MCP_COMMAND=venv312/bin/python
export HARNESS_DATA_SERVICE_MCP_WORKSPACE_ROOT=/path/to/managed/workspaces
export HARNESS_DATA_SERVICE_MCP_ALLOWED_WORKSPACE_ROOTS=/path/to/managed
export HARNESS_DATA_SERVICE_MCP_ALLOWED_SOURCE_ROOTS=/path/to/source/files
```

- 通过 harnessOS connector execution 跑通：

```text
knowledge_workspace_create
-> knowledge_source_import
-> knowledge_build_start
-> knowledge_build_status until terminal
-> knowledge_query_v2
-> knowledge_quality_feedback_v2
-> knowledge_correction_rules_v2
-> knowledge_review_correction_rule_v2
-> knowledge_correction_plan_v2
-> knowledge_workspace_archive
```

- 验收结论口径：若上述链路全程只依赖 opaque `workspace_id`，且所有 lifecycle/v2 tools 返回统一 envelope，旧 tools 兼容、安全边界和 build queue 语义符合 data_service Phase 4 标准，则外部 Harness MCP 验收通过。
- 已通过验收证据：`HarnessOSRealDataServiceAcceptance4` 返回 `status=ok`、`workspace_id=harnessosrealdataserviceacceptance4`、`operation_id=op_fb639a7aee3c`、`warnings=[]`。
- 环境前置：相邻项目 data_service venv 必须完整安装 `backend/requirements.txt`；缺少 `numpy`、`pandas` 等依赖会在 build 阶段失败。

## Phase 5-D: Meeting -> Knowledge MCP Cross-domain E2E

### 自动化用例

- Knowledge smoke：检查 `mcp/numpy/pandas/graphrag` 依赖，再执行 lifecycle runner。
- FunASR smoke：默认 contract stub 不依赖模型；显式设置 `HARNESS_FUNASR_MCP_EXECUTION=stdio` 时调用真实 `funasr_health` 和 `funasr_recognize_file`。
- Meeting workflow：转写步骤支持配置为 `funasr_mcp.funasr_recognize_file`，失败时返回可解释 connector failure，不静默吞错。
- Cross-domain runner：把 meeting transcript/minutes artifacts 作为 data_service source 的上游 lineage，随后 build/query。
- Transcript artifact：真实 FunASR MCP 路径必须登记 transcript artifact，即使外部 Meeting MCP text analysis/minutes 响应没有 transcript 文件。

### 外部真实验收用例

```text
audio file
-> funasr_mcp.funasr_recognize_file
-> meeting minutes artifact
-> data_service_mcp.knowledge_source_import
-> data_service_mcp.knowledge_build_start/status
-> data_service_mcp.knowledge_query_v2
```

验收要求：

- 所有跨项目能力调用均通过 MCP connector。
- Harness 侧只依赖 opaque `workspace_id`、`operation_id`、artifact id 和 connector job id。
- 不直接写相邻项目内部 workspace、GraphRAG、LLMWiki、quality 或 FunASR 模型产物目录。
- 端到端 artifact lineage 能追踪 audio、transcript、minutes、knowledge source、build operation、query result。

已通过真实验收：

- FunASR MCP smoke：`status=ok`、connector job `job_db4b4114eab3`、artifact `art_5f24f94bfbdc`。
- Data Service MCP smoke：`status=ok`、workspace `harnessos-real-data-service-phase5d`、operation `op_7df6de70eb14`。
- Meeting -> Knowledge smoke：`status=ok`、session `sess_333527af725f`、meeting session `meeting_cceef461`、workspace `harnessos-meeting-knowledge-phase5d-retry`、artifact lineage count `33`。
- 回归：2 项 Phase 5-D 定向测试通过；默认本地测试线为 133 passed、1 skipped、2 deselected。

剩余验收项：

- connector 超时、取消、retryable failure 和 server interrupted recovery。
- 产品化 BFF/UI 入口、operation dashboard 和更完整的故障排查手册。
