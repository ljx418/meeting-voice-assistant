# V1.8-B Agent-Led Source Import Report

日期：2026-05-30

## 当前状态

`PASS_LIMITED`

本阶段新增并通过 Agent-led source import smoke，用于验证 Agent 在授权后编排 PDF / TXT / Markdown / limited URL 导入。

## 实现内容

| 项 | 状态 |
| --- | --- |
| Agent draft | IMPLEMENTED |
| permission_grant_id 记录 | IMPLEMENTED |
| 未授权前不得 scan / import / source read 断言 | IMPLEMENTED |
| Markdown import | IMPLEMENTED |
| TXT import | IMPLEMENTED |
| PDF import | IMPLEMENTED |
| limited URL import | IMPLEMENTED |
| stable failing URL | IMPLEMENTED |
| build/index polling | IMPLEMENTED |
| source list registry source_id 验证 | IMPLEMENTED |
| skipped files with reason | IMPLEMENTED |
| WorkflowRun / ValidationReport fixture | IMPLEMENTED |
| fixture path hygiene | PASS |

## 新增命令

```bash
npm run smoke:v1.8-agent-source-import
```

## 真实数据

- `Desktop/技术分享/11-数字人`
- 数字人 Markdown 资料包
- 数字人 PDF 报告
- TXT 样本由 Markdown 派生，仅作为 V1.8-B smoke 输入，不声明任意 TXT 语义质量 ready
- 默认 URL 样本：
  - `http://example.com/`
  - `http://example.org/`
  - `http://127.0.0.1:8003/` 作为稳定安全失败样本

## 输出 fixtures

目标目录：

`fixtures/real/v1_8/agent-source-import/`

关键文件：

- `workspace-create.json`
- `markdown-import.json`
- `txt-import.json`
- `pdf-import.json`
- `url-import-1.json`
- `url-import-2.json`
- `url-stable-failure.json`
- `workspace-build.json`
- `source-list.json`
- `workspace-cleanup.json`
- `v1_8_b_agent_source_import_result.json`

## 当前仍不可声明

- Agent ready
- Workflow ready
- 普通用户 UX ready
- Guide / QA / Studio quality ready
- citation ready for V1.8-B
- all-source-type ready
- all websites URL ready
- OCR ready

## 已执行命令

```bash
npm run check
npm run smoke:v1.4-sources-p0
npm run smoke:v1.6-a-url
npm run smoke:v1.8-agent-source-import
```

结果：

| 命令 | 状态 |
| --- | --- |
| `npm run check` | PASS |
| `npm run smoke:v1.4-sources-p0` | PASS |
| `npm run smoke:v1.6-a-url` | PASS |
| `npm run smoke:v1.8-agent-source-import` | PASS_LIMITED |

## V1.8-B 决策

ResearchNotebook V1.8-B Agent-led source import is PASS_LIMITED for validated Markdown / TXT / PDF and limited URL sources on the approved digital human dataset.

该声明只覆盖 Agent-led source import，不覆盖 Guide / QA / Studio / citation quality。

## 下一步

下一阶段只能审计 V1.8-C Agent-Led Guide / QA / Citation Validation，不能直接进入 D/E/RC。
