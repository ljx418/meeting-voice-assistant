# ResearchNotebook V1.6-A URL Extraction Acceptance

日期：2026-05-28

## 验收状态词

- PASS_LIMITED：限定公开 URL smoke 通过。
- DEGRADED_ACCEPTED：失败 URL 稳定返回可解释错误，不影响已有来源。
- NOT_READY：URL source 不能进入证据链。
- BLOCKED：网络、站点策略或安全合同阻塞。

## 必须执行

1. 后端 focused tests。
2. 前端 adapter / UI tests。
3. `npm run check`。
4. `npm run smoke:v1.6-a-url`。
5. 文档和 fixtures 脱敏检查。

## 真实 URL 验收

建议 URL 集：

- `http://example.com/`
- `http://example.org/`
- `http://127.0.0.1:8003/`，作为安全失败样本，必须返回 `url_security_blocked`。

若公开站点临时不可用，报告中记录 `BLOCKED_BY_NETWORK_OR_SITE`，不得写 PASS。

## 功能验收

- 创建 workspace。
- 导入 URL source。
- source list/get 返回 registry `source_id`。
- source_type 为 `url`。
- source preview 可见。
- DocumentUnit 可见。
- EvidenceSpan 可解析。
- Guide 能引用 URL source。
- QA 回答能引用 URL source。
- Studio 输出能引用 URL source。
- citation 可打开 source preview / unit / EvidenceSpan。

## 安全验收

- `file://` 被拒绝。
- localhost 被拒绝。
- private IP 被拒绝。
- metadata service 被拒绝。
- redirect 到 private IP 被拒绝。
- unsupported content type 稳定失败。
- timeout 稳定失败。
- 401 / 403 / 451 稳定返回 permission blocked。
- response / fixtures / docs 不含 raw path、cache path、artifact physical path、stack trace。

## PRD 规格检视

PRD P1 写明 URL 正文抽取可选，且不保证所有站点。本阶段只能声明：

ResearchNotebook V1.6-A URL extraction is PASS_LIMITED for tested public HTML / plain text URLs.

不得声明：

- all websites ready。
- 登录页 / 私有页 / 付费墙 ready。
- JavaScript rendered page ready。
- 批量网页 ready。
- 自动联网 Research ready。

## 阶段风险门禁

若出现任一情况，停止并打回计划：

- URL 安全门禁缺失。
- citation 无法定位但报告写 PASS。
- 仅导入成功却声明 Guide / QA / Studio 引用闭环。
- response 泄漏本地路径或 backend stack trace。
- feature 层直接拼 backend route。
