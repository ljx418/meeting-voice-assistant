# ResearchNotebook V1.4 Feature Route Matrix

日期：2026-05-26

| Feature | Route / Dependency | Status | Notes |
| --- | --- | --- | --- |
| Notebook 三列布局 | Frontend only | PASS_LIMITED | Sources / Chat / Studio 骨架已落地；不代表 Guide / Studio 输出 ready。 |
| Notebook lifecycle | `/api/workspaces`, `/api/workspaces/{workspace_id}/rename`, `/api/workspaces/{workspace_id}/archive`, local recent storage | PASS_LIMITED | 创建、列表、重命名、归档、最近打开可用；不声明物理删除或跨设备最近打开。 |
| Sources P0 | `/api/workspaces/{workspace_id}/sources` with text and base64 file payloads plus PDF extraction / preview / citation contract | PASS_LIMITED | Markdown/TXT/可抽取文本 PDF 已通过数字人资料包浏览器式上传 smoke；扫描版 PDF/OCR 不声明 ready。 |
| Source Preview | `/sources/{source_id}/preview` | PASS | 继承 V1.1。 |
| DocumentUnit | `/sources/{source_id}/units` | PASS | 继承 V1.1。 |
| EvidenceSpan / citation navigation | `/sources/{source_id}/units/{unit_id}/evidence/{evidence_id}` | PASS_LIMITED | Chat / Studio citation 可复用 SourcePreviewDrawer / DocumentUnit / EvidenceSpan；不声明 all-source-type precise backjump ready。 |
| Notebook Guide | `/api/workspaces/{workspace_id}/guide` | PASS_LIMITED | 返回 Overview / Key Topics / Suggested Questions 和 evidence_refs；当前是确定性 source-grounded 导读，不声明完整 AI Guide 质量 ready。 |
| Source-grounded Chat | `/api/workspaces/{workspace_id}/query` | PASS_LIMITED | 返回 evidence、coverage_status、answer_basis、suggested_source_actions；workspace query 支持资料不足拒答和补源建议。 |
| Studio Notes | `/api/workspaces/{workspace_id}/studio/artifacts` with `artifact_type=notes` | PASS_LIMITED | 确定性轻量输出，必须带 evidence_refs。 |
| Study Guide | `/api/workspaces/{workspace_id}/studio/artifacts` with `artifact_type=study_guide` | PASS_LIMITED | 确定性轻量输出，必须带 evidence_refs。 |
| Briefing Doc | `/api/workspaces/{workspace_id}/studio/artifacts` with `artifact_type=briefing_doc` | PASS_LIMITED | 确定性轻量输出，必须带 evidence_refs。 |
| FAQ | `/api/workspaces/{workspace_id}/studio/artifacts` with `artifact_type=faq` | PASS_LIMITED | 确定性轻量输出，必须带 evidence_refs。 |
| Agent folder summary | V1.3 routes | PASS_LIMITED | 保留为 Studio 扩展入口，最终验收并入 V1.4-RC。 |
