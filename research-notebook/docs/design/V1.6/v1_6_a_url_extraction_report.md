# ResearchNotebook V1.6-A URL Extraction Report

日期：2026-05-28

## 结论

V1.6-A URL 正文抽取已完成限定范围 smoke，状态为 PASS_LIMITED。

本阶段证明公开 HTML URL 可以作为 source 导入，并进入 Source Preview、DocumentUnit、EvidenceSpan、Guide、QA、Studio FAQ 的引用链。该结论只覆盖本轮 smoke 的公开 HTTP URL，不代表 all websites ready。

## 实现范围

- 后端扩展 `POST /api/workspaces/{workspace_id}/sources`，新增 `urls[]`。
- URL source 归一为 `source_type=url`。
- URL source 复用现有 source registry、preview、DocumentUnit、EvidenceSpan。
- 前端来源导入表单新增“公开网页 URL”输入。
- 前端 `dataServiceClient.sources.create` 只在 adapter 层映射 `urls[]`。
- 新增 `npm run smoke:v1.6-a-url`。

## 真实 smoke

命令：

`npm run smoke:v1.6-a-url`

结果：

PASS_LIMITED。

覆盖：

| 项目 | 状态 | 说明 |
| --- | --- | --- |
| workspace create | PASS | `rn-v16-url-1779938401240` |
| unsafe URL blocked | PASS | `http://127.0.0.1:8003/` 返回 `url_security_blocked` |
| URL import 1 | PASS | `http://example.com/` |
| URL import 2 | PASS | `http://example.org/` |
| workspace build | PASS | operation completed |
| source preview / DocumentUnit | PASS | 两个 URL source 均有 unit |
| query EvidenceSpan | PASS | query evidence 可解析到 EvidenceSpan |
| Guide URL evidence | PASS | Guide 返回 URL source evidence refs |
| Studio URL evidence | PASS | FAQ 返回 URL source evidence refs |
| cleanup | PASS | workspace archived |

## Focused Tests

后端：

`python3 -m pytest tests/test_target_http_url_sources.py tests/test_target_http_source_preview.py -q`

结果：

11 passed, 1 warning。

前端：

`npm run test -- dataServiceClient.test.ts WorkspacePage.test.tsx`

结果：

99 passed。

全量 ResearchNotebook check：

`npm run check`

结果：

PASS。Boundary checks、lint、126 个 Vitest tests、production build 均通过。

Drawio 验证：

`drawio ok 17`

边界检查：

- `/api/v1/knowledge` 仅出现在 guard / smoke 检查文本中。
- feature/components 无 direct HTTP `fetch`，仅有 `refetch()`。
- `/api/` 命中均为 import path 或集中 adapter，不是 feature route string。
- `fixtures/real/v1_6/url-extraction/` 未发现 raw path / cache path / artifact physical path。
- `.smoke-artifacts/` 未进入 git。

## Fixtures

保存路径：

`fixtures/real/v1_6/url-extraction/`

关键文件：

- `workspace-create.json`
- `url-security-blocked.json`
- `url-import-1.json`
- `url-import-2.json`
- `source-src_38c28c096b05c01f-preview.json`
- `source-src_38c28c096b05c01f-units.json`
- `url-query.json`
- `url-query-evidence-span.json`
- `url-guide.json`
- `url-studio-faq.json`
- `v1_6_a_url_extraction_smoke_result.json`

Fixtures 已经通过脚本脱敏逻辑过滤 raw path / cache path / artifact physical path / stack trace。

## PRD 规格检视

PRD 将 URL 正文抽取标为 P1 可选能力，并明确“不保证所有站点”。本阶段实现符合该边界：

- 支持公开 HTTP/HTML URL。
- 不支持登录页、私有页、付费墙。
- 不支持 JavaScript rendered page。
- 不支持批量网页采集。
- 不将 URL 抽取等同于自动联网 Research。

## 风险评估

开发计划漂移风险：LOW。

原因：实现只扩展 source import contract，没有引入新 Research 流程或 arbitrary web search。

虚假验收风险：MEDIUM。

原因：本轮真实 URL 数量少，且只覆盖 HTTP 示例站点。已用 PASS_LIMITED 限定声明范围。

安全风险：MEDIUM。

原因：已实现 blocked URL 和 SSRF 基础门禁，但 robots / permission / redirect 私网跳转仍需要在后续更广泛站点和测试中继续扩充。

是否存在 HIGH 风险：NO。

## 仍未完成

- all websites URL extraction ready。
- HTTPS 站点兼容性全量验证。
- 登录页 / 私有页 / 付费墙。
- JavaScript rendered page。
- batch web crawl。
- 自动联网 Research。

## 下一阶段审计建议

可以进入 V1.6-B 多数据集质量评分计划审计，但不得把 V1.6-A 的两个 URL smoke 扩大为 all websites ready。

V1.6-B 必须使用至少 3 个主题数据集，并加入人工质量评分。规格漂移风险预估 MEDIUM，虚假验收风险预估 MEDIUM。
