# V2.5 PPT Generation

日期：2026-06-02

## 阶段目标

实现 PRD Phase 2 PPT 生成的受限 MVP。

**约束**：不伪装 Markdown/JSON 为 PPT，不声明 all presentation styles ready。

## 阶段 Entry Gate

- [ ] V2.4 Audio Overview 通过验收
- [ ] 当前分支无未合并的 V2.4 功能变更
- [ ] Slide generator 能力确认

## 决策路径

```
无法生成真实 .pptx？
  → 使用 SLIDE_OUTLINE_ONLY 方案
  → 提供 Markdown outline download
  → 不伪装成 PPT

可以生成真实 .pptx？
  → 进入 V2.5-A ~ V2.5-D 实现
  → V2.5-RC 人工质量审查
```

## 子阶段

### V2.5-A Slide Artifact Schema

**目标**：定义 slide artifact 数据结构。

**API Contract**：
```typescript
// 创建 Slide artifact
POST /api/workspaces/{workspace_id}/artifacts/slides
Request: {
  source_ids: string[]
  topic?: string
  slide_count?: number  // 默认 10，最大 30
}
Response: {
  artifact: SlideArtifact
}

// 获取 artifact
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}
Response: {
  artifact: SlideArtifact
}

// SlideArtifact 结构
interface SlideArtifact {
  artifact_id: string
  workspace_id: string
  type: "slides"
  status: "generating" | "ready" | "error"
  title: string
  slides: Slide[]
  created_at: string
  error?: {
    code: string
    message: string
  }
}

interface Slide {
  slide_num: number
  title: string
  bullets: string[]
  speaker_notes?: string
  layout_hint?: "title_only" | "bullets" | "two_column" | "image_left" | "image_right"
  evidence_refs: EvidenceRef[]
}
```

### V2.5-B Slide Outline Generation

**目标**：基于 sources 生成 slide outline。

**Generation Contract**：
```typescript
// 生成 slides
POST /api/workspaces/{workspace_id}/artifacts/slides/generate
Request: {
  source_ids: string[]
  topic?: string
  slide_count?: number
}
Response: {
  artifact_id: string
  status: "generating"
}

// 获取生成状态
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}/status
Response: {
  artifact_id: string
  status: "generating" | "ready" | "error"
  progress?: number
}
```

**约束**：
- 每页关键结论带 citation metadata
- 若 sources 不足，拒绝生成：
```typescript
{
  error: {
    code: "INSUFFICIENT_SOURCES",
    message: "资料不足，无法生成 Slides。请先添加更多 sources。"
  }
}
```

### V2.5-C PPTX Generator / Export Contract

**目标**：生成真实 .pptx 文件或明确 outline only。

**方案 A - 真实 PPTX**：
```typescript
// 导出 PPTX
POST /api/workspaces/{workspace_id}/artifacts/slides/export
Request: {
  artifact_id: string
}
Response: {
  download_url: string  // 临时 signed URL
  file_size: number
  slide_count: number
  format: "pptx"
}

// 下载文件
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}/download
Response: {
  url: string
  format: "pptx" | "md"
  size_bytes: number
}
```

**方案 B - Slide Outline Only**：
```typescript
// Markdown export
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}/download?format=md
Response: {
  url: string
  format: "md"
  size_bytes: number
}

// Markdown 格式
# {title}

## Slide 1: {slide_title}
- {bullet 1}
- {bullet 2}
- **Evidence**: [{source_title}]

## Slide 2: {slide_title}
...
```

**决策点**：
- 若 `/export` 返回 501 或 `SLIDE_OUTLINE_ONLY` 标志 → 使用方案 B
- 若 `/export` 返回有效 download_url → 使用方案 A
- 前端需要处理两种情况

### V2.5-D Slide Preview / Download UI

**目标**：Slide 可预览和下载。

**UI 组件**：
```typescript
// SlidePreview 组件
interface SlidePreviewProps {
  artifact: SlideArtifact
  onSlideChange?: (slide_num: number) => void
}

// 功能
- 每页预览（缩略图或详情）
- 上一页/下一页导航
- 页码指示器

// SlideDownload 组件
interface SlideDownloadProps {
  artifact: SlideArtifact
}

// 功能
- 下载 .pptx（如果支持）
- 下载 .md（始终支持）
- 显示文件大小
```

**PPTX vs Markdown UI 逻辑**：
```typescript
function SlideDownload({ artifact }: SlideDownloadProps) {
  const [exportFormat, setExportFormat] = useState<'pptx' | 'md'>('md');

  // 如果不支持 PPTX，显示提示
  if (!artifact.pptx_available && exportFormat === 'pptx') {
    return (
      <div className="warning">
        PPT export 不可用，请使用 Markdown 格式下载
      </div>
    );
  }

  return (
    <Select value={exportFormat} onChange={setExportFormat}>
      <Option value="md">Markdown</Option>
      <Option value="pptx">PowerPoint</Option>
    </Select>
  );
}
```

**验收**：
- [ ] 真实 .pptx 可打开（若方案 A）
- [ ] Markdown outline 可下载（始终支持）
- [ ] 每页关键结论带 citation metadata
- [ ] PPTX 不可用时正确降级

### V2.5-RC PPT Manual Review

**目标**：人工确认 slide 内容和结构。

**人工审查检查项**：
- [ ] 真实 .pptx 可打开（若方案 A）
- [ ] Markdown / JSON export 不伪装成 PPT
- [ ] 每页关键结论带 citation metadata
- [ ] 人工确认内容和结构可用
- [ ] 导出文件格式正确（.pptx 或 .md）

**质量标准**：
- 每页有明确标题
- 每个 bullet 有 evidence_refs（除非是过渡性文字）
- Markdown export 格式正确，可直接使用

## 风险评估

| 风险 | 等级 | 缓解策略 |
| --- | --- | --- |
| PPTX generator 不可用 | HIGH | Phase 1 先确认 export 能力 |
| Slide 生成质量不达标 | MEDIUM | 设置 evidence_refs 覆盖率阈值 |
| Export 格式错误 | MEDIUM | 添加文件格式验证 |

## 实现顺序

### Phase 1: Export 能力确认（1天）
1. 调用 slide export API
2. 确认 PPTX 可用性
3. 若不可用，确定 SLIDE_OUTLINE_ONLY 方案

### Phase 2: Slide Schema 对齐（1-2天）
1. 与后端对齐 SlideArtifact schema
2. 确认 Slide 结构（title、bullets、evidence_refs）
3. 确认 export format

### Phase 3: 前端 Slide UI（1-2天）
1. SlidePreview 组件
2. SlideDownload 组件
3. PPTX/Markdown 降级处理

### Phase 4: Smoke + Manual Review（1天）
1. 运行 Slide smoke 测试
2. 人工质量审查
3. 更新报告

## 出门状态

- `PPT_GENERATION_PASS_LIMITED`（真实 PPTX）
- `SLIDE_OUTLINE_ONLY`（仅 outline）

## 仍不声明

- all presentation styles ready
- full production ready

## 下一步

V2.5 通过后进入 V2.6 Mindmap Generation。