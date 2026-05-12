# PhaseG16 Packaging Console Scripts Report

日期：2026-05-11

## 背景

PhaseG16 继续沿 Interface Convergence 主线推进 CLI 目标入口。PhaseG15 已提供 `knowledge_main` entrypoint-ready alias，本阶段补齐最小 packaging 配置，让后续安装包可以暴露 `knowledge` console script。

## 变更范围

- `backend/pyproject.toml`
  - 新增 setuptools build metadata。
  - 声明 `data-service = data_service.__main__:main`。
  - 声明 `knowledge = data_service.__main__:knowledge_main`。
  - 声明 package discovery 覆盖 `app*` 与 `data_service*`。
- `backend/tests/test_data_service_api.py`
  - 新增 PhaseG16 packaging drift test，验证 console scripts 指向现有 entrypoint。
- `README.md` / `backend/README.md`
  - 补充 console script 入口说明。

## 对外能力检查

- MCP：未新增 tool。
- HTTP：未新增 route。
- CLI：新增 packaging metadata 中的 console script 声明；`data_service quality ...` 保持兼容。
- 运行时：未新增运行时依赖，依赖列表与 `backend/requirements.txt` 对齐。

## 出门验证

- PhaseG16 API 专项：通过，`22 passed`。
- MCP 专项回归：通过，`30 passed`。
- frontend `npm run build`：通过。
- Data Service/API/MCP 组合回归：通过，`123 passed`。
- drawio XML 校验：通过。
