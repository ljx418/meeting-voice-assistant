# ResearchNotebook V1.3 当前差距分析

文档状态：V1.3-A/B 计划阶段。当前项目仍不是 Agent 产品。

## 一句话结论

ResearchNotebook 已有知识来源、预览、DocumentUnit 和 EvidenceSpan 证据回跳基础，但还缺少 Agent Workflow 产品层：

```text
Agent 入口 -> workflow draft -> 用户授权 -> 本地文件夹扫描 -> 子文件夹总结 -> summary citation 回跳
```

当前不能声明 Agent ready、Workflow ready、Folder Summary ready。

## 当前基线

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| Source Preview | PASS | 继承 V1.1/V1.2。 |
| DocumentUnit Navigation | PASS | 继承 V1.1/V1.2。 |
| EvidenceSpan Highlight | PASS_LIMITED | text/markdown/json 受限路径已通过 smoke。 |
| V1.2 Manual Acceptance | SKIPPED_BY_PRODUCT_DECISION | 传统 UI 手工验收不再作为最终入口。 |
| Agent Workflow | NOT_READY | 当前没有 AgentTask、workflow draft、run 或 step logs。 |
| Local Folder Connector | NOT_READY | 当前 Chrome CLI 脚本是探索，不是后端授权 connector。 |
| Folder Summary Artifact | NOT_READY | 当前没有结构化 summary artifact。 |

## 阶段拆分

| 阶段 | 状态 | 目标 |
| --- | --- | --- |
| V1.3-A Agent Workflow Contract Discovery | NEXT | 定义 AgentTask / Workflow / WorkflowRun / WorkflowStep / Tool / FolderCollection / SummaryArtifact。 |
| V1.3-B Local Folder Connector Backend | NEXT | 后端支持显式授权目录扫描，第一版只支持 md/txt 正文抽取。 |
| V1.3-C Deterministic Folder Summary Workflow Runtime | NOT_STARTED | 固定模板 workflow：scan、extract、group、summarize、write artifacts。 |
| V1.3-D Folder Summary Generator | NOT_STARTED | 每个子文件夹生成结构化 summary artifact。 |
| V1.3-E Workflow UI | NOT_STARTED | workflow draft、run、step timeline、logs、artifact、retry、dry run。 |
| V1.3-F Agent Planner | NOT_STARTED | 用户自然语言生成已注册 workflow template draft。 |
| V1.3-G Evidence-backed Summary | NOT_STARTED | summary citation 回跳 SourcePreview / DocumentUnit / EvidenceSpan。 |
| V1.3-RC Agent Entry Acceptance | NOT_STARTED | Chrome CLI / manual 走完整 Agent 入口验收。 |

## 仍不能声明

- Agent ready。
- Workflow ready。
- Local folder connector ready。
- Folder summary ready。
- PDF/PPTX/DOCX/video/audio 原生正文摄入 ready。
- Assessment / Governance / Cloud collaboration ready。

## No False Green

- Chrome CLI 手工导入脚本不等于 Local Folder Connector。
- workflow draft 不等于 workflow run。
- Agent draft 不得未确认就读取本地目录。
- summary 普通文本不等于 evidence-backed summary。
- relative_path 是唯一可展示路径；不得展示 `/Users` 绝对路径。
