# harnessOS V3.0 Manual Acceptance Notes

文档状态：ACTIVE V3.0 MANUAL ACCEPTANCE。V2 手工验收文档已归档到 `docs/history/v2-phase-docs/phase3-manual-acceptance_v2.md`。

## 1. 使用范围

本文只记录 V3.0 手工验收入口。Phase 3 旧命名不再代表当前活动开发阶段；当前活动阶段以 V3.0-A 到 V3.0-E 为准。

## 2. Core Smoke

```bash
python3 -m cli.main run "你好"
python3 -m cli.main run --json "你好"
```

预期：

- 普通 CLI 与 JSON 输出可用。
- 输出中不会出现跨 app scope 数据。

## 3. RPC Smoke

```bash
python3 main.py --port 8010 --no-reload
curl -X POST http://localhost:8010/v1/rpc \
  -H 'Content-Type: application/json' \
  -d '{"id":"req_1","method":"health.ping","params":{}}'
```

预期：

- 返回 JSON-RPC 响应。
- `result` 与 `error` 不同时存在。

## 4. Meeting Manual Acceptance

V3.0-D 前后均需验证：

- meeting pack 可 assembly。
- Meeting MCP / FunASR MCP 通过 ConnectorRegistry。
- 真实音频产出 transcript、analysis、result、minutes。
- artifacts、job、trace、turn 关联完整。

## 5. Knowledge Manual Acceptance

V3.0-E 验证：

- knowledge pack 可 assembly。
- Knowledge MCP connector 健康检查通过。
- ingest/search/summarize/citation 链路输出 note、brief、citation_bundle。
- 替换 knowledge connector 不需要修改 Core。
