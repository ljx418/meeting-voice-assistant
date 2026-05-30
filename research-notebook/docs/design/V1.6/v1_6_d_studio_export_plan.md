# ResearchNotebook V1.6-D Studio Export / Download Plan

日期：2026-05-28

## 阶段目标

为 Studio 轻量输出增加复制 / 下载能力，优先支持 Markdown 和 JSON。导出必须保留 citation metadata，不能泄漏 raw path / cache path / artifact physical path。

## 范围

- Notes / Study Guide / Briefing Doc / FAQ 的已生成 artifact 可导出。
- 前端生成 Markdown / JSON 文件。
- JSON 包含 artifact id、type、sections、evidence_refs、schema_version、exported_at。
- Markdown 保留 section 标题、内容和 citation id。

## 禁止

- 不生成 Audio / PPT / Mindmap / Compare。
- 不把导出能力写成 Studio Phase 2 ready。
- 不导出本地绝对路径。
- 不导出 cache path 或 artifact physical path。

## 验收

- Studio artifact 生成后出现复制 Markdown、下载 Markdown、下载 JSON。
- 导出文件名为 safe slug。
- 导出 JSON 有 `evidence_refs`。
- 导出 Markdown 有 citation 标记。
- 复制 / 下载失败为局部状态。
- `npm run check` PASS。

## 风险评估

开发计划漂移风险：LOW。

虚假验收风险：LOW。

原因：导出是已生成 artifact 的呈现能力，不涉及新 AI 质量声明。
