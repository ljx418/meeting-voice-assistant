# ResearchNotebook V2.x 后端服务 PRD

日期：2026-06-02
版本：v1.0
状态：向后端开发团队提交

---

## 1. 概述

本文档定义 ResearchNotebook V2.x 后端服务需求，涵盖 V2.1-V2.8 各阶段所需的后端 API 能力。

**后端服务位置**：`/Users/Zhuanz/Desktop/workspace/data_service`

**前端位置**：`/Users/Zhuanz/Desktop/workspace/research-notebook`

### 1.1 已完成（前端实现）

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| V2.1 PRD MVP Gap Closure | ✅ 前端完成 | Sources 搜索、Notes (localStorage)、Archive 确认、AI 质量标识 |
| V2.2 URL P1 | ⚠️ 前端完成 | URL validation 前端实现，block_reason 后端待实现 |

### 1.2 待实现（后端）

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| V2.2 URL P1 Hardening | 后端需实现 | `block_reason` 返回、SSRF 防护服务端实现 |
| V2.3 OCR Provider Gate | 后端需实现 | OCR provider 集成（可选，若无 provider 则保持 `ocr: false`） |
| V2.4 Audio Overview | 后端需实现 | TTS provider 集成（可选，若无 provider 则保持 AUDIO_NOT_READY） |
| V2.5 PPT Generation | 后端需实现 | PPTX generation（可选，若无则 SLIDE_OUTLINE_ONLY） |
| V2.6 Mindmap Generation | 后端需实现 | Mindmap generator（可选，若无则 MINDMAP_NOT_READY） |
| V2.7 Document Comparison | 后端需实现 | Comparison generator（可选，若无则 NOT_READY） |

---

## 2. 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    ResearchNotebook Frontend                      │
│  (React + TypeScript + TanStack Query)                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Service Backend                          │
│  (/Users/Zhuanz/Desktop/workspace/data_service)                 │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Sources API  │  │ Artifacts API│  │ OCR Provider │ (optional)│
│  │ - URL fetch  │  │ - Studio     │  │ - Tesseract  │          │
│  │ - SSRF check │  │ - Slides     │  │ - Azure      │          │
│  │ - Content    │  │ - Mindmap    │  │ - Google     │          │
│  └──────────────┘  │ - Compare    │  └──────────────┘          │
│                    │ - Audio      │                             │
│  ┌──────────────┐  └──────────────┘  ┌──────────────┐          │
│  │ GraphRAG     │  ┌──────────────┐  │ TTS Provider │ (optional)│
│  │ Service      │  │ LLM Wiki     │  │ - Azure      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 已有的 API 端点

### 3.1 Capability Manifest

**当前状态**：已实现

```yaml
GET /api/workspaces/{workspace_id}/capabilities
Response:
  capabilities:
    source_preview: true
    document_units: true
    evidence_spans: true
    source_level_preview: true
    unit_level_navigation: true
    precise_span_highlight: true
    citation_backjump: true
    ocr: false              # 待实现 - 需后端确认 provider
    scanned_pdf_ocr: false  # 待实现 - 需后端确认 provider
```

### 3.2 Sources API

**当前状态**：部分实现

```yaml
# 已有端点
GET    /api/workspaces/{workspace_id}/sources
POST   /api/workspaces/{workspace_id}/sources
GET    /api/workspaces/{workspace_id}/sources/{source_id}
DELETE /api/workspaces/{workspace_id}/sources/{source_id}/remove
POST   /api/workspaces/{workspace_id}/sources/{source_id}/rename
GET    /api/workspaces/{workspace_id}/sources/{source_id}/preview
GET    /api/workspaces/{workspace_id}/sources/{source_id}/trace
GET    /api/workspaces/{workspace_id}/sources/{source_id}/units
GET    /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}
GET    /api/workspaces/{workspace_id}/sources/{source_id}/units/{unit_id}/evidence/{evidence_id}

# 已有搜索端点（V2.1 前端实现）
GET    /api/workspaces/{workspace_id}/sources/search?q={query}&type_filter={type}&limit={limit}
```

**待补充**：URL source 需返回 `block_reason` 字段（见 V2.2）

---

## 4. V2.2 URL P1 Hardening - 后端需求

### 4.1 需求描述

前端 URL validation 可被绕过，必须有后端 SSRF 防护。

### 4.2 需后端实现

#### 4.2.1 POST /api/workspaces/{workspace_id}/sources

**变更**：URL source 创建失败时需返回 `block_reason`

```yaml
POST /api/workspaces/{workspace_id}/sources
Request:
  urls:
    - url: "https://example.com/article"
      title: "Article Title"
      metadata: {}

Response (成功):
  source: SourceDetail

Response (安全阻断):
  source: SourceDetail
  block_reason: "ssrf" | "private_ip" | "timeout" | "unsupported_content_type" | "robots_blocked" | "permission_denied" | "paywall"
  warnings: ["此 URL 指向内部网络，不允许抓取"]
```

#### 4.2.2 安全检查层

| 检查项 | 实现要求 |
| --- | --- |
| SSRF 防护 | 拒绝 private IP (10.x, 172.16.x, 192.168.x) |
| Localhost 防护 | 拒绝 127.x, ::1 |
| Metadata service | 拒绝 169.254.x |
| Redirect 校验 | follow redirect 后二次安全检查 |
| Content-Type allowlist | 仅允许 text/*, application/pdf |
| Size limit | max_response_size: 10MB, timeout: 30s, redirect_limit: 5 |

#### 4.2.3 block_reason 映射

| block_reason | HTTP status | 用户消息 |
| --- | --- | --- |
| ssrf | 400 | "此 URL 指向内部网络，不允许抓取" |
| private_ip | 400 | "此 URL 指向私有网络地址，不允许抓取" |
| timeout | 408 | "此页面加载超时，请稍后重试" |
| unsupported_content_type | 415 | "此页面内容类型不支持，仅支持文本和 PDF" |
| robots_blocked | 403 | "此页面不允许被抓取（robots.txt 限制）" |
| permission_denied | 403 | "此页面需要登录或无权限访问" |
| paywall | 402 | "此页面需要付费订阅，无法抓取" |

#### 4.2.4 SourceDetail 需增加字段

```typescript
interface URLSourceDetail extends SourceDetail {
  url: string
  final_url?: string  // redirect 后的 URL
  content_type?: string
  block_reason?: string
  import_state: 'ready' | 'blocked' | 'failed_import'
}
```

### 4.3 验收标准

- [ ] private IP URL 返回 block_reason
- [ ] localhost URL 返回 block_reason
- [ ] metadata service URL 返回 block_reason
- [ ] redirect 后仍执行安全校验
- [ ] 正常 URL 成功创建 source

---

## 5. V2.3 OCR Provider Gate - 后端需求

### 5.1 需求描述

扫描 PDF 需 OCR 处理，验证 OCR provider 可用性。

### 5.2 Capability Manifest 变更

```yaml
# 若有 OCR provider
capabilities:
  ocr: true
  scanned_pdf_ocr: true

# 若无 OCR provider，保持现状
capabilities:
  ocr: false
  scanned_pdf_ocr: false
```

### 5.3 需后端实现（可选）

#### 5.3.1 OCR Provider Health Check

```yaml
POST /api/ocr/provider/health
Response:
  available: boolean
  provider: string  # "tesseract" | "azure" | "google"
  latency_ms?: number
  supported_languages?: string[]
  unsupported_reason?: string
```

#### 5.3.2 OCR API

```yaml
POST /api/workspaces/{workspace_id}/sources/{source_id}/ocr
Response:
  source_id: string
  status: "processing" | "completed" | "error"
  pages?: OCRPage[]
  error?: { code: string, message: string }

GET /api/workspaces/{workspace_id}/sources/{source_id}/ocr/status
Response:
  source_id: string
  status: "processing" | "completed" | "error"
  progress?: number  # 0-100
```

#### 5.3.3 OCRPage Schema

```typescript
interface OCRPage {
  page_num: number
  text: string          // 提取的文本
  bbox: BBox[]          // 文本块位置数组
  confidence: number    // 0-1
  language?: string     // 检测到的语言
}

interface BBox {
  x: number
  y: number
  width: number
  height: number
  text: string
  confidence: number
}
```

#### 5.3.4 DocumentUnit 映射

```typescript
interface OCRDocumentUnit extends DocumentUnit {
  // OCR 特有字段
  text_basis: string  // OCRPage.text
  bbox: BBox[]
  confidence: number
  language?: string
}
```

### 5.4 决策路径

```
有 OCR provider？
  → 实现 OCR API
  → capabilities.ocr = true
  → 支持扫描 PDF OCR

无 OCR provider？
  → 保持 ocr: false
  → 扫描 PDF 返回 unsupported_reason: "ocr_required"
```

---

## 6. V2.4 Audio Overview - 后端需求

### 6.1 需求描述

基于 sources 生成音频概述，需要 TTS provider。

### 6.2 需后端实现（可选）

#### 6.2.1 TTS Provider Health Check

```yaml
POST /api/tts/provider/health
Response:
  available: boolean
  provider: string  # "azure" | "google" | "elevenlabs"
  voices: string[]  # 可用 voice ID 列表
  default_voice: string
  supported_languages?: string[]
```

#### 6.2.2 Audio Artifact API

```yaml
# 创建 Audio artifact
POST /api/workspaces/{workspace_id}/artifacts/audio
Request:
  source_ids: string[]
  language?: string
  voice_id?: string  # 可选，默认使用 provider 默认 voice
Response:
  artifact: AudioArtifact

# 获取 Audio artifact
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}
Response:
  artifact: AudioArtifact

# 获取生成状态
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}/status
Response:
  artifact_id: string
  status: "generating" | "ready" | "error"
  progress?: number  # 0-100

# 下载 Audio
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}/download
Response:
  url: string  # 临时 signed URL
  format: "mp3" | "wav"
  size_bytes: number
```

#### 6.2.3 AudioArtifact Schema

```typescript
interface AudioArtifact {
  artifact_id: string
  workspace_id: string
  type: "audio_overview"
  status: "generating" | "ready" | "error"
  script: AudioSegment[]
  citations: EvidenceRef[]
  duration_seconds: number
  voice_metadata: {
    provider: string
    voice_id: string
    language: string
  }
  created_at: string
  error?: {
    code: string
    message: string
  }
}

interface AudioSegment {
  text: string
  start_time: number   // 秒
  end_time: number
  evidence_refs?: EvidenceRef[]
}
```

#### 6.2.4 约束

- script 每个关键段落带 evidence_refs
- 不基于外部知识硬答
- 若 sources 不足，拒绝生成：
  ```json
  {
    "error": {
      "code": "INSUFFICIENT_SOURCES",
      "message": "资料不足，无法生成 Audio Overview。请先添加更多 sources。"
    }
  }
  ```

### 6.3 决策路径

```
有 TTS provider？
  → 实现 Audio Artifact API
  → 支持音频生成

无 TTS provider？
  → 保持 AUDIO_OVERVIEW_NOT_READY
  → 前端不显示 Audio 功能
```

---

## 7. V2.5 PPT Generation - 后端需求

### 7.1 需求描述

生成幻灯片，可选 PPTX 导出或仅 Markdown outline。

### 7.2 需后端实现（可选）

#### 7.2.1 Slide Artifact API

```yaml
# 创建 Slide artifact
POST /api/workspaces/{workspace_id}/artifacts/slides
Request:
  source_ids: string[]
  topic?: string
  slide_count?: number  # 默认 10，最大 30
Response:
  artifact: SlideArtifact

# 获取 Slide artifact
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}
Response:
  artifact: SlideArtifact

# 导出 PPTX（可选）
POST /api/workspaces/{workspace_id}/artifacts/slides/export
Request:
  artifact_id: string
Response:
  download_url: string  # 临时 signed URL
  file_size: number
  slide_count: number
  format: "pptx"

# 下载
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}/download?format=md|pptx
Response:
  url: string
  format: "md" | "pptx"
  size_bytes: number
```

#### 7.2.2 SlideArtifact Schema

```typescript
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

#### 7.2.3 约束

- 每页关键结论带 citation metadata
- 若 sources 不足：
  ```json
  {
    "error": {
      "code": "INSUFFICIENT_SOURCES",
      "message": "资料不足，无法生成 Slides。请先添加更多 sources。"
    }
  }
  ```

### 7.3 决策路径

```
有 PPTX generation 能力？
  → 实现 SLIDE_OUTLINE + PPTX export
  → 支持 .pptx 下载

无 PPTX generation？
  → 仅支持 Markdown outline download
  → 返回 SLIDE_OUTLINE_ONLY
```

---

## 8. V2.6 Mindmap Generation - 后端需求

### 8.1 需求描述

基于 sources 生成思维导图，区别于现有的 Graph（实体关系图）。

### 8.2 需后端实现（可选）

#### 8.2.1 Mindmap Artifact API

```yaml
# 创建 Mindmap artifact
POST /api/workspaces/{workspace_id}/artifacts/mindmap
Request:
  source_ids: string[]
  topic?: string
  max_depth?: number  # 默认 3，最大 5
Response:
  artifact: MindmapArtifact

# 获取 Mindmap artifact
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}
Response:
  artifact: MindmapArtifact

# 获取生成状态
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}/status
Response:
  artifact_id: string
  status: "generating" | "ready" | "error"
  progress?: number
```

#### 8.2.2 MindmapArtifact Schema

```typescript
interface MindmapArtifact {
  artifact_id: string
  workspace_id: string
  type: "mindmap"
  status: "generating" | "ready" | "error"
  root_node: MindmapNode
  created_at: string
  error?: {
    code: string
    message: string
  }
}

interface MindmapNode {
  node_id: string
  label: string
  summary?: string        // 节点摘要，用于 hover
  parent_id?: string      // null for root
  children?: MindmapNode[] // 递归结构
  evidence_refs?: EvidenceRef[]
  position?: {             // 可选，用于固定布局
    x: number
    y: number
  }
}
```

#### 8.2.3 与 Graph 的区别

| 属性 | Mindmap | Graph |
| --- | --- | --- |
| 生成方式 | 用户触发，基于 sources | 自动构建，基于 workspace |
| 结构 | 树形（parent-child） | 网状（任意连接） |
| 内容 | 用户可读的主题 | 实体关系 |
| 用途 | 梳理思路 | 探索关联 |

### 8.3 决策路径

```
有 Mindmap generation 能力？
  → 实现 Mindmap Artifact API

无？
  → 保持 MINDMAP_NOT_READY
  → 前端不显示 Mindmap 功能
```

---

## 9. V2.7 Document Comparison - 后端需求

### 9.1 需求描述

多文档对比分析，区别于 Research Report（单问题多源回答）。

### 9.2 需后端实现（可选）

#### 9.2.1 Compare Artifact API

```yaml
# 创建 Compare artifact
POST /api/workspaces/{workspace_id}/artifacts/compare
Request:
  source_ids: string[]  // 至少 2 个
Response:
  artifact: CompareArtifact

# 获取 Compare artifact
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}
Response:
  artifact: CompareArtifact
```

#### 9.2.2 CompareArtifact Schema

```typescript
interface CompareArtifact {
  artifact_id: string
  workspace_id: string
  type: "compare"
  status: "generating" | "ready" | "error"
  compare_set: string[]  // source_ids
  result: ComparisonResult
  created_at: string
  error?: {
    code: string
    message: string
  }
}

interface ComparisonResult {
  summary: string  // 总体概述
  source_pairs: SourcePair[]  // 两两对比结果
  all_similarities?: Similarity[]  // 多文档共同点
  all_differences?: Difference[]  // 多文档分歧
}

interface SourcePair {
  source_a: string  // source_id
  source_b: string  // source_id
  source_a_title?: string
  source_b_title?: string
  similarities: Similarity[]
  differences: Difference[]
  conflicts: Conflict[]
}

interface Similarity {
  topic: string
  description: string
  evidence_refs: EvidenceRef[]
}

interface Difference {
  topic: string
  source_a_position: string  // A 的观点
  source_b_position: string  // B 的观点
  evidence_a: EvidenceRef[]
  evidence_b: EvidenceRef[]
}

interface Conflict {
  topic: string
  claim_a: string
  claim_b: string
  evidence_a: EvidenceRef[]
  evidence_b: EvidenceRef[]
  resolution?: string  // 如果有的话
}
```

#### 9.2.3 与 Research 的区别

| 属性 | Compare | Research |
| --- | --- | --- |
| 输入 | 多个文档 | 问题 + sources |
| 输出 | 文档间异同 | 基于 source 回答 |
| 目的 | 对比分析 | 信息提取 |
| evidence | 两侧证据 | 单侧证据 |

### 9.3 决策路径

```
有 Comparison generation 能力？
  → 实现 Compare Artifact API

无？
  → 保持 DOCUMENT_COMPARISON_NOT_READY
  → 前端不显示 Compare 功能
```

---

## 10. Artifacts 统一管理

### 10.1 Artifacts API 前缀

所有 artifact 类型统一使用 `/api/workspaces/{workspace_id}/artifacts/` 前缀：

```yaml
# 获取所有 artifacts
GET /api/workspaces/{workspace_id}/artifacts

# 获取特定 artifact
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}

# 删除 artifact
DELETE /api/workspaces/{workspace_id}/artifacts/{artifact_id}

# artifact 类型
type: "studio" | "slides" | "audio_overview" | "mindmap" | "compare"
```

### 10.2 Artifact 通用 Schema

```typescript
interface BaseArtifact {
  artifact_id: string
  workspace_id: string
  type: string
  title: string
  status: "generating" | "ready" | "error"
  artifact_available: boolean
  summary: string
  sections?: ArtifactSection[]
  evidence_refs: EvidenceRef[]
  unsupported_reason?: string
  generation_metadata?: GenerationMetadata
  created_at: string
  updated_at?: string
}

interface ArtifactSection {
  title: string
  content: string
  evidence_refs?: EvidenceRef[]
}

interface GenerationMetadata {
  provider?: string
  provider_name?: string
  model?: string
  prompt_version?: string
  evidence_ref_count?: number
  fallback_mode?: boolean
  latency_ms?: number
  response_schema?: string
  error_code?: string
}
```

---

## 11. 接口定义矩阵

| 功能 | 方法 | 端点 | 优先级 | 依赖 |
| --- | --- | --- | --- | --- |
| URL SSRF 防护 | POST | `/api/workspaces/{workspace_id}/sources` | P0 | 无 |
| URL block_reason | GET | `/api/workspaces/{workspace_id}/sources/{source_id}` | P0 | URL SSRF |
| OCR Provider Health | POST | `/api/ocr/provider/health` | P1 | 无（可选） |
| OCR Processing | POST | `/api/workspaces/{workspace_id}/sources/{source_id}/ocr` | P1 | OCR Provider |
| TTS Provider Health | POST | `/api/tts/provider/health` | P1 | 无（可选） |
| Audio Artifact Create | POST | `/api/workspaces/{workspace_id}/artifacts/audio` | P1 | TTS Provider |
| Audio Artifact Download | GET | `/api/workspaces/{workspace_id}/artifacts/{artifact_id}/download` | P1 | Audio Artifact |
| Slide Artifact Create | POST | `/api/workspaces/{workspace_id}/artifacts/slides` | P2 | 无（可选） |
| Slide Export | POST | `/api/workspaces/{workspace_id}/artifacts/slides/export` | P2 | Slide Artifact |
| Slide Download | GET | `/api/workspaces/{workspace_id}/artifacts/{artifact_id}/download` | P2 | Slide Artifact |
| Mindmap Artifact Create | POST | `/api/workspaces/{workspace_id}/artifacts/mindmap` | P2 | 无（可选） |
| Compare Artifact Create | POST | `/api/workspaces/{workspace_id}/artifacts/compare` | P2 | 无（可选） |
| Artifacts List | GET | `/api/workspaces/{workspace_id}/artifacts` | P2 | 无 |

---

## 12. 错误码定义

### 12.1 通用错误码

```typescript
type ErrorCode =
  | "validation_error"      // 400
  | "not_found"             // 404
  | "conflict"              // 409
  | "version_or_schema_mismatch"  // 412/426
  | "capability_missing"   // 422
  | "backend_unavailable"   // 503
  | "unknown_service_error" // 500
  | "request_timeout"       // timeout
  | "missing_graph_artifact"
  | "ocr_required"          // 扫描 PDF 需要 OCR
  | "insufficient_sources"  // 资料不足
  | "ssrf_blocked"          // SSRF 攻击
  | "private_ip_blocked"    // 私有 IP
  | "timeout"               // 请求超时
  | "unsupported_content_type"
  | "robots_blocked"
  | "permission_denied"
  | "paywall"
```

### 12.2 业务错误码

| error.code | 说明 | 处理建议 |
| --- | --- | --- |
| INSUFFICIENT_SOURCES | 资料不足 | 提示用户添加更多 sources |
| OCR_REQUIRED | 扫描 PDF 需要 OCR | 提示用户使用原生文本 PDF |
| SSRF_BLOCKED | SSRF 攻击被拦截 | 提示用户更换 URL |
| PRIVATE_IP_BLOCKED | 私有 IP 被拦截 | 提示用户更换 URL |

---

## 13. Capability Manifest 完整 Schema

```typescript
interface CapabilityManifest {
  workspace_id: string
  service_version?: string
  schema_version?: string
  generated_at?: string
  capabilities: {
    source_preview: boolean
    document_units: boolean
    evidence_spans: boolean
    source_level_preview: boolean
    unit_level_navigation: boolean
    precise_span_highlight: boolean
    citation_backjump: boolean
    ocr?: boolean              // 可选，V2.3
    scanned_pdf_ocr?: boolean  // 可选，V2.3
  }
  supported_source_types: Array<{
    source_type: string
    preview: "none" | "source" | "unit" | "span"
    locators: Array<"page_no" | "slide_no" | "timestamp" | "json_path" | "offset">
  }>
}
```

---

## 14. 前端当前实现（供参考）

### 14.1 前端已有 API 客户端

**位置**：`src/shared/api/dataServiceClient.ts`

前端已实现：
- `sources.search()` - 搜索 sources
- `sources.preview()` - 获取 source preview
- `sources.listUnits()` - 获取 document units
- `sources.getUnit()` - 获取单个 unit
- `sources.getEvidenceSpan()` - 获取 evidence span
- `studio.createArtifact()` - 创建 studio artifact

### 14.2 前端已有 Query Hooks

**位置**：`src/shared/api/workspaceM2Queries.ts`

前端已实现：
- `useSourceSearchQuery()` - Sources 搜索
- `useSourcePreviewQuery()` - Source preview
- `useSourceUnitsQuery()` - Document units（分页）
- `useSourceUnitQuery()` - 单个 unit
- `useSourceEvidenceSpanQuery()` - Evidence span

### 14.3 前端待后端实现的 UI

| 功能 | 前端组件 | 状态 |
| --- | --- | --- |
| URL SSRF 错误显示 | `ApiErrorState` | 前端已备好，需后端返回 block_reason |
| OCR 状态显示 | SourcePreview | 前端已备好，需后端返回 ocr_status |
| Audio Player | AudioPlayer | 前端已规划，待后端实现 |
| Slide Preview | SlidePreview | 前端已规划，待后端实现 |
| Mindmap Canvas | MindmapCanvas | 前端已规划，待后端实现 |
| Compare Panel | ComparePanel | 前端已规划，待后端实现 |

---

## 15. 测试要求

### 15.1 V2.2 URL P1 测试用例

```python
test_cases = [
    # SSRF 攻击
    ("http://10.0.0.1/internal", "ssrf"),
    ("http://172.16.0.1/internal", "private_ip"),
    ("http://192.168.1.1/internal", "private_ip"),
    ("http://127.0.0.1/localhost", "ssrf"),
    ("http://169.254.169.254/metadata", "ssrf"),

    # 正常 URL
    ("https://example.com/public", "success"),
    ("https://httpbin.org/html", "success"),
]

for url, expected in test_cases:
    response = create_url_source(url)
    if expected == "success":
        assert response.status == 200
        assert "block_reason" not in response
    else:
        assert response.block_reason == expected
```

### 15.2 V2.3 OCR 测试用例

```python
test_cases = [
    # 扫描 PDF（需要 OCR）
    ("scanned.pdf", "ocr_required"),

    # 原生文本 PDF
    ("text.pdf", "success"),
]
```

---

## 16. 部署注意事项

### 16.1 环境变量

```bash
# OCR Provider（可选）
OCR_PROVIDER=azure|google|tesseract
OCR_API_KEY=xxx
OCR_ENDPOINT=xxx

# TTS Provider（可选）
TTS_PROVIDER=azure|google|elevenlabs
TTS_API_KEY=xxx
TTS_ENDPOINT=xxx

# SSRF 防护配置
ALLOWED_IP_RANGES=10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
BLOCKED_IP_RANGES=127.0.0.0/8,169.254.0.0/16
```

### 16.2 性能要求

- URL fetch timeout: 30s
- Max response size: 10MB
- Redirect limit: 5
- OCR processing: 60s per page
- TTS generation: 120s per artifact

---

## 17. 后续步骤

1. **V2.2 必须实现**：URL SSRF 防护和 block_reason
2. **V2.3-V2.7 可选**：根据 provider 可用性决定实现
3. **Artifacts 统一管理**：建议统一 artifact 管理接口

---

## 18. 联系方式

- 前端项目：`/Users/Zhuanz/Desktop/workspace/research-notebook`
- 后端项目：`/Users/Zhuanz/Desktop/workspace/data_service`
- API 类型定义：`research-notebook/src/shared/types/api.ts`
- API 客户端：`research-notebook/src/shared/api/dataServiceClient.ts`