# Phase 0.5 阶段性验收报告

验收日期：2026-04-25  
验收阶段：Phase 0.5 协议优先控制面  
验收基线：`docs/acceptance-test-cases_v2.md`

## 结论

**通过，带剩余风险。**

Phase 0.5 的核心验收项已经满足：

- headless CLI 可用
- Gateway 协议模型可用
- session/turn 最小生命周期可用
- resume/events/continue/interrupt 方法面可用
- `/v1/runs` 与 `/v1/runs/stream` FastAPI 入口可用
- snapshot 与 events.jsonl 持久化可用
- 自动化测试通过

剩余风险：

- `turn.continue` 当前在 SimpleRuntime 下是协议占位，尚未接 OpenHarness `continue_pending`。
- `turn.interrupt` 当前是状态标记，尚未实现真实运行中取消。
- `GatewayRuntimePool` 仍是 `session_id -> agent`，尚未升级为 OpenHarness `RuntimeBundle` 池。
- 真实模型 smoke 依赖外网和 API key，不纳入默认自动验收。

## 自动化验收结果

| ID | 用例 | 执行结果 | 备注 |
| --- | --- | --- | --- |
| P05-A01 | Gateway 协议单测 | PASS | `tests/test_gateway_protocol.py` |
| P05-A02 | API runs 单测 | PASS | `tests/test_api_runs.py` |
| P05-A03 | Gateway 去 ohmo 化 | PASS | `apps/gateway` 无 `ohmo` / channel bus 残留 |
| P05-A04 | Draw.io XML 校验 | PASS | `xmllint --noout` |
| P05-A05 | Headless CLI demo | PASS | 清空 API key 后可输出 demo fallback |
| P05-A06 | FastAPI `/v1/runs` | PASS | TestClient 返回 200 |
| P05-A07 | FastAPI SSE | PASS | TestClient 返回 SSE 事件 |
| P05-A08 | Session events | PASS | turn 后可读取 persisted events |

## 执行命令

```bash
PYTHONPYCACHEPREFIX=/tmp/harnessos-pycache \
python3 -m pytest tests/test_gateway_protocol.py tests/test_api_runs.py
```

```bash
xmllint --noout docs/architecture/current-vs-target-gap_v2.drawio
```

```bash
DEEPSEEK_API_KEY= MINIMAX_API_KEY= OPENAI_API_KEY= OPENHARNESS_API_KEY= ANTHROPIC_API_KEY= \
PYTHONPYCACHEPREFIX=/tmp/harnessos-pycache \
python3 -m cli.main run '你好'
```

```bash
PYTHONPYCACHEPREFIX=/tmp/harnessos-pycache python3 - <<'PY'
from fastapi.testclient import TestClient
from apps.api import app

client = TestClient(app)
resp = client.post('/v1/runs', json={'input': '你好', 'close_session': True})
print(resp.status_code)
print(resp.json().keys())
PY
```

## 用户态手工验收步骤

### 用例 M-P05-01：普通终端直接调用

步骤：

```bash
cd /Users/Zhuanz/Desktop/workspace/harnessOS
python3 -m cli.main run "你好"
```

预期：

- 不进入 TUI
- 当前终端直接输出回复文本
- 退出码为 0

结果：PASS

### 用例 M-P05-02：JSON 输出

步骤：

```bash
python3 -m cli.main run --json "你好"
```

预期：

- 输出 JSON
- 包含 `session_id`、`turn_id`、`final_text`、`events`
- `events` 至少包含 `turn.started`、`item.delta`、`turn.completed`

结果：PASS

### 用例 M-P05-03：HTTP 同步 run

步骤：

```bash
python3 main.py --port 8010 --no-reload
curl -X POST http://localhost:8010/v1/runs \
  -H 'Content-Type: application/json' \
  -d '{"input":"你好","close_session":true}'
```

预期：

- HTTP 200
- 返回 `session_id`、`turn_id`、`final_text`、`events`

结果：PASS（通过 TestClient 验证）

### 用例 M-P05-04：HTTP SSE run

步骤：

```bash
curl -N -X POST http://localhost:8010/v1/runs/stream \
  -H 'Content-Type: application/json' \
  -d '{"input":"你好","close_session":true}'
```

预期：

- 返回 `text/event-stream`
- 至少包含 `event: turn.started` 和 `event: turn.completed`

结果：PASS（通过 TestClient 验证）

### 用例 M-P05-05：读取 session event log

步骤：

1. 发起一个不关闭 session 的 `/v1/runs`
2. 记录返回的 `session_id`
3. 请求 `/v1/sessions/{session_id}/events`

预期：

- 返回该 session 的事件列表
- 至少包含 `turn.started`、`item.delta`、`turn.completed`

结果：PASS

## 下一阶段准入建议

Phase 0.5 可以进入下一轮协议面开发。建议下一轮只做一条主线：

1. 把 `GatewayRuntimePool` 升级为 OpenHarness `RuntimeBundle` 池。
2. 将 `turn.continue` 接到 `continue_pending`。
3. 将 `turn.interrupt` 接到真实运行中取消。
4. 增加 `session.list` / `session.read` / transcript replay。
