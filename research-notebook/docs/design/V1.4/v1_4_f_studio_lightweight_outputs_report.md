# ResearchNotebook V1.4-F Studio Lightweight Outputs Report

日期：2026-05-26

## 阶段结论

V1.4-F Studio 轻量输出达到 PASS_LIMITED。

已完成：

- data_service 新增 `POST /api/workspaces/{workspace_id}/studio/artifacts`。
- 支持 `notes`、`study_guide`、`briefing_doc`、`faq`。
- 每个可用输出都返回 `evidence_refs`。
- 无可引用证据时返回 `artifact_available=false`，不生成无来源输出。
- ResearchNotebook Studio 列提供生成按钮和输出预览。
- Studio evidence citation 可复用 SourcePreviewDrawer / DocumentUnit / EvidenceSpan 路径。

## 限定范围

- 当前是确定性轻量输出，不声明 Claude / LLM 高质量写作 ready。
- 当前不支持下载、外发、Figma / Stitch 流转。
- 当前不声明 Audio Overview、PPT、思维导图、文档对比 ready。

## 验证结果

后端 focused tests：

```text
python3 -m pytest backend/tests/test_target_http_studio_artifacts.py backend/tests/test_target_http_notebook_guide.py backend/tests/test_target_http_evidence_spans.py -q
13 passed
```

前端 focused tests：

```text
npm run test -- src/shared/api/dataServiceClient.test.ts src/features/workspaces/WorkspacePage.test.tsx
97 passed
```

## 风险评估

规格漂移风险：MEDIUM

原因：PRD 的 Studio 输出是 AI 驱动轻量输出，当前实现是确定性模板化输出。

收敛措施：只声明 PASS_LIMITED，不声明高质量 AI Studio 输出 ready。

虚假验收风险：MEDIUM

原因：用户可能把 “生成” 按钮误解为完整 AI 文档生成。

收敛措施：输出必须带 evidence_refs；无证据时拒绝生成；文档保留 Phase 2+ 输出能力为 NOT_READY。

结论：无 HIGH 风险，可以进入 V1.4-G 来源定位与引用高亮产品化确认。
