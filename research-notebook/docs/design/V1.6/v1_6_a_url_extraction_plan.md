# ResearchNotebook V1.6-A URL Extraction Plan

日期：2026-05-28

## 阶段目标

V1.6-A 只补齐 PRD 中 P1 可选能力：公开网页 URL 正文抽取。目标是让 URL 作为 source 进入现有 Sources / Preview / DocumentUnit / EvidenceSpan / Guide / QA / Studio 证据链。

本阶段不声明 all websites ready，不做登录页、付费墙、私有网页、JavaScript 渲染页面或批量网页采集。

## Entry Gate

- V1.5 revalidation 已 PASS_LIMITED。
- P0 Markdown / TXT / 可抽取文本 PDF 主路径仍可用。
- AI provider smoke 已 PASS。
- data_service 可启动。
- ResearchNotebook `npm run check` 当前可运行。
- V1.6-0 已记录 URL 安全门禁和云同步 / 协作 OUT_OF_SCOPE。

## 后端合同

扩展现有 route：

`POST /api/workspaces/{workspace_id}/sources`

新增请求字段：

```ts
type UrlSourceInput = {
  title?: string;
  url: string;
  metadata?: Record<string, unknown>;
};

type TargetSourceImportRequest = {
  paths?: string[];
  texts?: TextSourceInput[];
  files?: FileSourceInput[];
  urls?: UrlSourceInput[];
  metadata?: Record<string, unknown>;
};
```

导入成功后必须返回 registry `source_id`，并将 `source_type` 归一为 `url`。URL source 必须支持：

- source list / get。
- source preview。
- DocumentUnit。
- EvidenceSpan。
- Guide / QA / Studio citation。

## 安全门禁

后端必须执行：

- 只允许 `http` 和 `https`。
- 禁止 `localhost`、`127.0.0.1`、`0.0.0.0`、private IP ranges、link-local、metadata service。
- 禁止 `file://`、`ftp://`、`data:`、`javascript:`。
- redirect 后必须重新校验目标 URL。
- 不携带 cookies。
- 不访问登录页、私有页、付费墙。
- 不绕过 robots / permission block。
- HTML 只抽正文和 sanitize，不执行 script。
- 设置 `max_response_size`、`timeout`、`redirect_limit`、`content_type allowlist`。

稳定错误：

- `url_security_blocked`
- `unsupported_site`
- `extraction_failed`
- `robots_or_permission_blocked`
- `fetch_timeout`

## 前端实现

- `CreateSourceRequest` 增加 `url`。
- `dataServiceClient.sources.create` 将 URL 输入映射为 backend `urls[]`。
- Workspace 来源导入表单增加公开 URL 输入。
- feature 层不拼 route string。
- 不使用 `dangerouslySetInnerHTML`。
- URL 导入失败为局部状态，不清空已有来源、Guide、QA 或 Studio。

## 测试计划

后端：

- URL source 导入成功。
- URL source preview 成功。
- URL source DocumentUnit 成功。
- URL source EvidenceSpan 成功。
- `file://` / localhost / private IP / metadata service 被拒绝。
- redirect 到私有地址被拒绝。
- unsupported content type 返回稳定错误。
- timeout 返回稳定错误。
- 401 / 403 / 451 返回 `robots_or_permission_blocked`。
- response 不含 raw path / cache path / artifact physical path / stack trace。

前端：

- URL request body 映射为 `urls[]`。
- URL 导入表单可提交。
- URL source 显示为来源。
- 不新增 feature direct fetch。
- route string 仍只在 `src/shared/api/dataServiceClient.ts`。

真实 smoke：

- 至少 2 个公开 URL 成功。
- 至少 1 个失败 URL 返回稳定失败。
- 成功 URL 可 preview / unit / evidence。
- 成功 URL 进入 Guide / QA / Studio 引用链。

## 风险评估

规格漂移风险：MEDIUM。

原因：URL 抽取容易被误读为全网站支持或 Research 自动联网搜索。

收敛措施：文档、UI 和报告均限定为公开 HTML / plain text URL，失败站点必须稳定降级。

虚假验收风险：MEDIUM。

原因：只验证导入成功不足以证明 citation 可定位。

收敛措施：验收必须覆盖 preview、DocumentUnit、EvidenceSpan、Guide / QA / Studio citation，不允许只用 HTTP 200 作为 PASS。

## 阶段退出

PASS_LIMITED：

公开 URL 导入、正文抽取、preview、DocumentUnit、EvidenceSpan、Guide / QA / Studio citation 在限定真实 URL 上通过。

NOT_READY：

URL 导入或 citation 定位不稳定。

BLOCKED：

网络或站点策略导致无法稳定执行真实 URL smoke，或安全门禁无法实现。
