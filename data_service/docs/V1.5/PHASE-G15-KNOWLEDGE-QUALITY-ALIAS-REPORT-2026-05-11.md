# PhaseG15 Knowledge Quality Alias Report

日期：2026-05-11

## 背景

PhaseG15 继续沿 Interface Convergence 主线推进 quality CLI 目标语义。PhaseG13/G14 已开放 `data_service quality ...` 只读和写入型治理命令，本阶段提供目标 `knowledge quality ...` 的 entrypoint-ready alias，但不假设当前环境已经安装独立 `knowledge` 可执行文件。

## 变更范围

- `backend/data_service/__main__.py`
  - `_build_parser` 支持传入 `prog`，用于 `data_service` 与 `knowledge` 两种命令名。
  - `main` 支持传入 argv，便于别名入口和测试复用同一 parser。
  - 新增 `knowledge_main`，供后续 console script `knowledge = data_service.__main__:knowledge_main` 绑定。
- `backend/tests/test_data_service_api.py`
  - 新增 PhaseG15 alias 端到端测试，验证 `knowledge_main(["quality", ...])` 复用 quality shared helper。
- `backend/tests/test_data_service_mcp.py`
  - 更新 CLI drift test，验证 `knowledge_main` 存在、`prog=knowledge` 可用、文档和矩阵同步。

## 对外能力检查

- MCP：未新增 tool。
- HTTP：未新增 route。
- CLI：新增 entrypoint-ready alias 函数 `knowledge_main`；当前仓库未新增打包配置，也未假设系统已安装 `knowledge` 命令。
- 兼容性：`data_service quality ...` 保持可用。

## 出门验证

- PhaseG15 API 专项：通过，`21 passed`。
- MCP 专项回归：通过，`30 passed`。
- frontend `npm run build`：通过。
- Data Service/API/MCP 组合回归：通过，`122 passed`。
- drawio XML 校验：通过。
