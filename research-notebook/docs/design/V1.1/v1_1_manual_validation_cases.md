# ResearchNotebook V1.1 手工验证用例

文档状态：待人工执行。
日期：2026-05-24。

## 当前结论

V1.1 功能开发剩余为 0 个阶段。当前还需要人工确认的是受限 ready 范围是否在真实使用中可接受。

可以人工验收：

- text workspace query evidence navigation
- text session query evidence navigation
- markdown workspace query evidence navigation
- json workspace query evidence navigation
- RC4 scoped source trace

仍不可声明 ready：

- all-session precise navigation
- all-source-type precise backjump
- all-source-type source trace
- native PDF/PPTX/HTML/video/audio ingestion
- Assessment / Mastery
- Quality/Governance console
- Graph editing/governance
- Cloud sync/collaboration

## 手工验收环境

| 检查项 | 期望 | 人工结果 |
| --- | --- | --- |
| 前端服务 | `http://127.0.0.1:5173/` 可访问 | 待填写 |
| 后端服务 | `http://127.0.0.1:8003` 可访问 | 待填写 |
| 页面加载 | 非空白，无 crash overlay | 待填写 |
| 控制台 | 无阻塞 console error / pageerror | 待填写 |
| 网络边界 | 未出现 `/api/v1/knowledge/*` 功能请求 | 待填写 |

## 用例 1：Text Workspace EvidenceSpan

建议 source content：

```text
Manual acceptance should keep the answer, source preview, document unit, and highlighted evidence span visible during evidence navigation.
```

建议问题：

```text
What should manual acceptance keep visible during evidence navigation?
```

| 步骤 | 验收点 | 人工结果 |
| --- | --- | --- |
| 创建 workspace | workspace 出现在列表并可进入 | 待填写 |
| 创建 text source | source 出现在 Source Library | 待填写 |
| 点击 Preview | Source Preview Drawer 打开 | 待填写 |
| 查看 source preview | 文本预览可见，按 escaped text 渲染 | 待填写 |
| 查看 Document Units | unit list 可见 | 待填写 |
| 点击第一个 unit | selected unit 有 active state | 待填写 |
| 提交 workspace query | answer 可见 | 待填写 |
| 查看 citation | citation 是 jumpable 状态 | 待填写 |
| 点击 citation | Drawer 打开或聚焦 | 待填写 |
| 检查高亮 | EvidenceSpan 高亮可见且非空 | 待填写 |
| 检查局部状态 | answer / source preview / unit detail 均未被清空 | 待填写 |

## 用例 2：Text Session EvidenceSpan

建议 session content：

```text
Session precise navigation should preserve source id, unit id, and evidence id so the notebook can highlight the same source span from a session answer.
```

建议问题：

```text
What identifiers should session precise navigation preserve?
```

| 步骤 | 验收点 | 人工结果 |
| --- | --- | --- |
| 创建 session | session 出现在 Workbench session list | 待填写 |
| ingest session text | ingest 成功，build 可完成或 session 可 query | 待填写 |
| 提交 session query | session answer 可见 | 待填写 |
| 查看 citation | citation 携带可跳转 affordance | 待填写 |
| 点击 citation | Source Preview Drawer 打开或聚焦 | 待填写 |
| 检查 selected unit | 正确 unit 被选中 | 待填写 |
| 检查高亮 | EvidenceSpan 高亮可见且非空 | 待填写 |
| 检查局部状态 | session answer / source preview / unit detail 均未被清空 | 待填写 |

## 用例 3：Markdown Workspace EvidenceSpan

建议 source type：

```text
markdown
```

建议 source content：

```markdown
# Markdown Manual Evidence

manualmarkdownanchor evidence should be highlighted from markdown source.
```

建议问题：

```text
What should manualmarkdownanchor evidence do?
```

| 步骤 | 验收点 | 人工结果 |
| --- | --- | --- |
| 创建 markdown source | source_type 显示为 markdown 或 service-defined fallback | 待填写 |
| 点击 Preview | Preview button 可用，Drawer 打开 | 待填写 |
| 查看 markdown preview | markdown 按 escaped text 渲染，不转 HTML | 待填写 |
| 查看 Document Units | markdown section unit 可见 | 待填写 |
| 点击 unit | unit detail 可见 | 待填写 |
| 提交 workspace query | answer 与 jumpable citation 可见 | 待填写 |
| 点击 citation | Drawer 打开并选择正确 unit | 待填写 |
| 检查高亮 | 高亮文本与 markdown evidence 相关 | 待填写 |

## 用例 4：JSON Workspace EvidenceSpan

建议 source type：

```text
json
```

建议 source content：

```json
{"summary":"manualjsonanchor evidence should be highlighted from json source","status":"supported"}
```

建议问题：

```text
What should manualjsonanchor evidence do?
```

| 步骤 | 验收点 | 人工结果 |
| --- | --- | --- |
| 创建 json source | source_type 显示为 json 或 service-defined fallback | 待填写 |
| 点击 Preview | Preview button 可用，Drawer 打开 | 待填写 |
| 查看 JSON preview | JSON 按 escaped text 渲染，不执行 parser UI | 待填写 |
| 查看 Document Units | `json_node` unit 可见 | 待填写 |
| 查看 locator | `json_path` 元数据可见 | 待填写 |
| 提交 workspace query | answer 与 jumpable citation 可见 | 待填写 |
| 点击 citation | Drawer 打开并选择正确 json unit | 待填写 |
| 检查高亮 | 高亮文本与 JSON evidence 相关 | 待填写 |

## 用例 5：Source Trace Scoped Path

| 步骤 | 验收点 | 人工结果 |
| --- | --- | --- |
| 选择已创建 source | source_id 是 registry `src_...` | 待填写 |
| 点击 Trace 入口 | Source Trace Drawer 打开 | 待填写 |
| 查看 trace/provenance | trace summary 或 provenance 可见 | 待填写 |
| 检查 id 语义 | 未使用 sourceRef / slug / artifact_ref 伪装 source_id | 待填写 |
| 检查隐私边界 | 不显示 raw path / cache path / physical artifact path | 待填写 |

## 用例 6：Unsupported Source Type Fallback

候选 source types：

```text
pdf
pptx
html
video
audio
```

| 步骤 | 验收点 | 人工结果 |
| --- | --- | --- |
| 创建 unsupported source | source 可作为 metadata source 出现 | 待填写 |
| 查看 Preview button | 不应显示为完整 ready 能力 | 待填写 |
| 打开或查看 fallback | 显示 unsupported / unavailable 状态 | 待填写 |
| 提交 query | 不伪造 precise backjump ready | 待填写 |
| 检查局部状态 | fallback 不清空 answer 或已加载内容 | 待填写 |

## 用例 7：Cleanup

| 步骤 | 验收点 | 人工结果 |
| --- | --- | --- |
| 归档测试 workspace | workspace 不再作为 active workspace 留存 | 待填写 |
| 记录失败项 | 如 cleanup 失败，记录 workspace id/name | 待填写 |
| 检查声明边界 | 没有把 unsupported 能力写成 ready | 待填写 |

## 人工验收签字

| 项目 | 填写 |
| --- | --- |
| 验收人 | 待填写 |
| 验收时间 | 待填写 |
| 前端 commit | 待填写 |
| 后端 commit | 待填写 |
| 最终结论 | PASS / PASS_WITH_DEGRADED_ACCEPTED / FAIL |
| 备注 | 待填写 |
