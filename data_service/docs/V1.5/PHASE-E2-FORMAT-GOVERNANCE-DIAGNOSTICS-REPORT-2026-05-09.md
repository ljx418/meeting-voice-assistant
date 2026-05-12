# PhaseE2 Format Governance Diagnostics Report

日期：2026-05-09

## 目标

在 PhaseE1 支持 `docx/yaml/yml` 后，补齐治理侧可观察性：控制台和质量层能看到 source 格式分布、extractor 分布和潜在格式问题，而不新增外部入口或改变既有 contract。

## 已完成

- distill source record 增加：
  - `source_format`
  - `extractor_name`
  - `extractor_available`
- manifest source summary 增加同样的格式治理字段。
- `manifest.quality` 增加：
  - `format_counts`
  - `extractor_counts`
  - `format_issue_sources`
- `read_distill_bundle().source_profiles` 增加格式治理字段。
- `read_summary_bundle().quality.distill` 增加格式分布、extractor 分布和格式问题列表。
- PhaseE docx/yaml E2E 测试扩展到检查 manifest、source profile 和 summary quality。

## 出门验证

```bash
backend/.venv/bin/python -m py_compile backend/data_service/service.py backend/tests/test_data_service.py
```

结果：通过。

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py::test_data_service_phasee_docx_yaml_run_default_pipeline -q
```

结果：`1 passed`。

```bash
backend/.venv/bin/python -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

结果：`103 passed`。

```bash
backend/.venv/bin/python -c "import xml.etree.ElementTree as ET; [ET.parse(p) for p in ['docs/V1.5/current-vs-target-gap.drawio','docs/V1.5/data-service-v1.5-roadmap.drawio']]; print('drawio xml ok')"
```

结果：`drawio xml ok`。

## 对外能力检查

- 未新增 MCP tool。
- 未新增 HTTP route。
- 未新增 CLI 参数。
- 既有 source ingest / scan 的新增格式支持保持不变。
- 新增字段为治理诊断字段，属于已有 distill/summary payload 的附加信息。

## 下一步

进入 PhaseF 前的控制台产品化准备：将 format diagnostics 显示到 `/knowledge` Overview / Sources / Quality 区域。
