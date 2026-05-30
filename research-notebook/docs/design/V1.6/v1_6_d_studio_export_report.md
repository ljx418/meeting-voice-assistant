# ResearchNotebook V1.6-D Studio Export / Download Report

日期：2026-05-28

## 阶段结论

V1.6-D 已完成 Studio 轻量输出的 Markdown / JSON 导出实现，并通过自动化测试与 `npm run check`。

状态：PASS_LIMITED_UI_TESTED

说明：本阶段验证的是 Studio artifact 已生成后的复制 / 下载能力。最终浏览器下载文件人工体验、文件内容抽查和质量修整仍放入 V1.6-RC 集中验收。

## 实现范围

- Studio artifact 生成后显示：
  - 复制 Markdown
  - 下载 Markdown
  - 下载 JSON
- Markdown 导出包含：
  - artifact 标题
  - summary
  - sections
  - citation metadata
- JSON 导出包含：
  - artifact_id
  - artifact_type
  - title
  - summary
  - sections
  - evidence_refs
  - generation_metadata
  - schema_version
  - exported_at
- 导出文件名使用 safe slug。
- 复制 / 下载状态只显示在 Studio 局部区域。

## PRD 对齐

| PRD 项 | 结果 | 说明 |
| --- | --- | --- |
| Studio 轻量输出可沉淀 | PASS_LIMITED | 已生成 artifact 可复制和下载。 |
| Notes / Study Guide / Briefing Doc / FAQ 均需引用 | PASS_LIMITED | 导出保留后端返回的 evidence_refs，不补造引用。 |
| 输出可下载或内置预览 | PASS_LIMITED | 支持 Markdown / JSON 下载；最终人工下载体验在 RC 检查。 |
| 重输出 Audio / PPT / Mindmap / Compare | NOT_READY | 本阶段未实现，也不声明 ready。 |

## 验收命令

```bash
npm run test -- WorkspacePage.test.tsx
npm run check
```

结果：

- `WorkspacePage.test.tsx`：25 tests passed。
- `npm run check`：boundary checks、lint、126 tests、build 全部通过。

备注：jsdom 对模拟下载链接会输出 `navigation not implemented` 非阻塞警告；断言已覆盖复制、Markdown 下载、JSON 下载、citation metadata 和 EvidenceSpan 回跳。

## 风险评估

开发计划漂移风险：LOW。

虚假验收风险：MEDIUM。

原因：自动化测试证明 UI 控件和导出内容结构可用，但没有在真实浏览器中人工打开下载文件进行审阅。

收敛措施：

- 本阶段只声明 PASS_LIMITED_UI_TESTED。
- V1.6-RC 必须人工检查下载的 Markdown / JSON 文件。
- 不把本阶段写成 Studio 全量 ready 或 Phase 2/3 输出 ready。

是否存在 HIGH 风险：NO。

## 仍未完成

- 真实浏览器下载文件人工检查。
- 多数据集人工质量评分。
- Research 补源 / 冲突分析。
- Phase 2/3 输出合同发现。
- V1.6-RC 集中验收。

## 下一阶段审计结论

下一阶段：V1.6-E Research 补源 / 冲突分析。

准入意见：Conditional Go。

注意：V1.6-E 存在 HIGH 规格漂移风险，因为 Research 很容易变成无来源互联网问答。进入实质开发前必须先写独立计划、验收标准和计划审计，并明确只基于当前 Notebook sources，不自动联网搜索。
