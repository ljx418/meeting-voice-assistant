# PhaseF2 Console Ops Drilldown Report

日期：2026-05-09

## 目标

继续 PhaseF 控制台产品化，把分散在 Source 台账、目录扫描、低信号审计和格式诊断里的异常统一到 Overview 可见的治理队列。

## 已完成

- Overview 新增 `Ops Drilldown / 异常队列` 面板。
- 异常队列展示四类治理对象：
  - failed sources
  - unreadable files
  - low-signal samples
  - format issues
- failed source 支持跳转到 Source Trace 或 Quality。
- low-signal sample 支持定位 source 或生成质量反馈。
- unreadable file 与 format issue 在 Overview 直接可见。
- 复用既有 `/summary`、`/distill`、`/sources/list`、`/directories/scan`、`/quality/low-signal-audit` 数据，不新增后端接口。
- 重新构建静态控制台产物。

## 出门验证

```bash
npm run build
```

结果：通过；生成：

- `backend/app/static/knowledge_console/index.html`
- `backend/app/static/knowledge_console/assets/index-C617ideI.css`
- `backend/app/static/knowledge_console/assets/index-Rj2_7vtB.js`

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：`103 passed`。

```bash
backend/.venv/bin/python -m pytest backend/tests -q
```

结果：`138 passed`。仍有既有 `datetime.utcnow()` deprecation warnings，未在本阶段扩大处理范围。

```bash
backend/.venv/bin/python -c "import xml.etree.ElementTree as ET; [ET.parse(p) for p in ['docs/V1.5/current-vs-target-gap.drawio','docs/V1.5/data-service-v1.5-roadmap.drawio']]; print('drawio xml ok')"
```

结果：`drawio xml ok`。

## 对外能力检查

- 未新增 MCP tool。
- 未新增 HTTP route。
- 未新增 CLI 参数。
- 只在控制台组合展示既有响应数据。
- 静态控制台产物更新，不改变 API contract。
- 入口扫描覆盖 `backend/app/api` 与 `backend/data_service`，本阶段未发现隐藏的对外能力变更。

## 下一步

进入 PhaseF3：准备 MCP Debugger 入口和 tool/resource contract 可视化，同时继续保持 MCP 为主入口、HTTP/CLI 为兼容入口。
