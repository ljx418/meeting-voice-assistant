# V2.25 Phase 91 开发计划：Architecture Source Model

## 1. 阶段目标

Phase 91 是 V2.25-V2.30 的入口阶段，目标是建立统一的 Architecture Source Model，把后续意图推断和架构图反推需要的输入源全部登记成可追踪 artifact。

本阶段只做 source model，不做架构意图推断，不做 diagram-to-code accepted 判断。

## 2. 实现范围

新增 focused module：

```text
backend/data_service/code_assets/architecture_intent/
  __init__.py
  paths.py
  source_model.py
```

新增测试：

```text
backend/tests/test_v2_25_architecture_source_model.py
```

暂不新增 HTTP/MCP/CLI public endpoints。Phase 91 验收通过后，Phase 96 统一收敛 public contract；本阶段通过 service/module 和 artifact inspection 验收。

## 3. 输入

- 已注册 codebase asset。
- Repo snapshot。
- 既有 V2 architecture artifacts，如果存在则登记为 source artifact ref。
- 项目真实文件树：
  - Markdown / README / PRD / architecture / gap / audit / acceptance。
  - drawio。
  - Mermaid / PlantUML 文本块。
  - 代码文件。
  - config / manifest / workflow descriptor。
  - test / fixture / contract 文件。

## 4. 输出 Artifact

```text
workspace/assets/codebase/{codebase_id}/architecture/intent/sources/
  architecture_sources.jsonl
  diagram_cells.jsonl
  source_blocks.jsonl
  architecture_source_summary.json
```

## 5. Source 分类规则

| source_type | 识别规则 |
| --- | --- |
| markdown | `.md`, `.mdx`, README/PRD/architecture/gap/audit/acceptance 文档。 |
| drawio | `.drawio`, `.dio`。 |
| mermaid | Markdown fenced block: `mermaid`。 |
| plantuml | `.puml`, `.plantuml` 或 Markdown fenced block。 |
| code | `.py`, `.ts`, `.tsx`, `.js`, `.jsx`, `.vue`, `.rs`, `.go` 等。 |
| config | `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, package/pyproject/tsconfig 等。 |
| test | path/name 包含 `test`, `tests`, `spec`, `fixture`, `fixtures`。 |
| runtime_descriptor | path/name 包含 `runtime`, `run`, `trace`, `execution`, `evidence` 的 JSON/YAML/MD，只作为 descriptor，不作为 runtime_observed。 |

## 6. Authority 规则

| authority_role | 识别规则 |
| --- | --- |
| target | 文件名/路径包含 target architecture、target state、目标架构。 |
| plan | development plan、implementation package、milestones。 |
| acceptance | acceptance plan、e2e matrix、coverage matrix。 |
| audit | audit report、review report。 |
| implementation | backend/frontend/src/tests 代码和测试。 |
| historical | history、archive、legacy、superseded、旧版本目录。 |
| unknown | 无法分类。 |

## 7. 安全与边界

- public payload 只输出 repo-relative path。
- 不读取二进制正文。
- drawio 只解析 XML cell 元数据和 label，不执行外部链接。
- Markdown HTML 原文不渲染执行。
- 本阶段不修改 source registry、V2.0-V2.24 artifacts 或原始项目文档。

## 8. 开发任务

1. 新增 paths helper，生成 intent source artifact 路径。
2. 实现 source_model builder：
   - 文件扫描遵循 snapshot files 优先。
   - fallback 到 repo walk，但必须尊重常见 ignore。
   - 生成 source rows。
   - 对 Markdown 生成 source block rows。
   - 对 drawio 生成 diagram cell rows。
   - 对 Mermaid / PlantUML fenced blocks 生成 diagram/source blocks。
   - 生成 summary。
3. 增加 redaction/path safety。
4. 增加 focused tests。
5. 用 data_service 与 HarnessOS 做真实 E2E。

## 9. 不做内容

- 不做 accepted diagram-to-code match。
- 不做 intent inference。
- 不做 runtime 执行采集。
- 不暴露新 public endpoint。
