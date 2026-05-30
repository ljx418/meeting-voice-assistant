# ResearchNotebook V1.6-A URL Extraction Plan Audit

日期：2026-05-28

## 审计结论

Conditional Go。

V1.6-A 可以进入实质开发，前提是实现严格限定在公开 URL source 导入和引用闭环，不扩大为全网站抓取、自动 Research 或私有页面访问。

## 审计意见闭环

| 编号 | 意见 | 处理 |
| --- | --- | --- |
| A1 | URL 抽取必须有 SSRF 防护。 | 已列为后端硬门禁。 |
| A2 | redirect 后必须重新校验。 | 已列为测试和合同要求。 |
| A3 | 不能声明 all websites ready。 | 计划和验收均限定 PASS_LIMITED。 |
| A4 | 不能只验收导入成功。 | 验收覆盖 preview / unit / EvidenceSpan / Guide / QA / Studio citation。 |
| A5 | 不得新增 feature direct fetch。 | route 仍限定在 `dataServiceClient.ts`。 |
| A6 | 失败 URL 必须稳定降级。 | 验收要求安全失败和 unsupported / permission / timeout 错误。 |

## 风险评估

开发计划漂移风险：MEDIUM。

收敛措施：代码只扩展 source import contract 和 URL source mapper，不引入新 Research 工作流。

虚假验收风险：MEDIUM。

收敛措施：smoke 必须验证 citation 可定位，不接受单纯 HTTP 200。

安全风险：MEDIUM。

收敛措施：SSRF、redirect、content type、timeout、size limit、permission block 都要有 focused tests。

## Go / No-Go

当前无 HIGH 风险。

允许进入 V1.6-A 实质开发。

下一阶段完成后必须输出：

- `v1_6_a_url_extraction_report.md`
- fixtures under `fixtures/real/v1_6/url-extraction/`
- updated gap / drawio / README
- command results and risk reassessment
