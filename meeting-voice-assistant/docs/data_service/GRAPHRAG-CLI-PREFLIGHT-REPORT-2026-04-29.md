# GraphRAG CLI Preflight 阶段报告

日期：2026-04-29

## 背景

Phase 3 已完成 GraphRAG 职责收口：`data_service` 默认把 graph execution 委托给 `app.graphrag`，并在 native GraphRAG CLI 不可用时使用 `app.graphrag` compat materializer 完成本地图谱 state。

本次补充的目标是避免把“compat fallback 成功”误读成“native Microsoft GraphRAG CLI 健康”。

## 已完成

- `app.graphrag.service.data_service_runner` 新增 native CLI preflight
- 不再只检查 `which graphrag`
- 现在会执行 `graphrag --version` 作为最小健康检查
- CLI 不存在时返回 `graphrag_cli_not_found`
- CLI 存在但不可执行或返回非 0 时返回 `graphrag_cli_broken`
- 返回中包含 `cli_health.available / healthy / path / returncode / stdout / stderr`
- CLI preflight 失败时仍由 `app.graphrag` compat materializer 完成可用图谱 state

## 当前机器诊断结果

当前本机 `graphrag` 命令存在：

```text
/usr/local/bin/graphrag
```

但它是一个指向临时补丁脚本的 shim：

```bash
exec /usr/local/opt/python@3.12/bin/python3.12 /tmp/graphrag_patched.py "$@"
```

实际 `/tmp/graphrag_patched.py` 已不存在，因此 native CLI healthcheck 失败。

## 验收结果

自动化测试：

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py -q
```

结果：

- 55 passed

真实知识库端到端验证：

```bash
python3 -m data_service ingest \
  --workspace /tmp/data-service-graphrag-preflight-20260429 \
  /Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split
```

结果：

- 86 sources
- 248 distilled units
- `llmwiki: success`
- `graphrag: indexed`
- graph execution owner: `app.graphrag`
- execution result reason: `graphrag_cli_broken`
- compat graph state: 85 entities / 76 themes / 131 relationships

## 验收分层

- 可用基线：`app.graphrag` compat materializer 能稳定产出本地图谱 state
- 增强验收：native Microsoft GraphRAG CLI 通过 preflight，并能完成原生 index

当前项目满足可用基线；native CLI 增强验收需要修复本机 `/usr/local/bin/graphrag` shim 或重新安装 GraphRAG CLI。
