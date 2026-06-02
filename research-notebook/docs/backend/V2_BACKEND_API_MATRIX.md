# V2.x Backend API 接口定义矩阵

## 目录

- [1. 必实现 API（P0）](#1-必实现-apip0）
- [2. 可选 API（P1-P2）](#2-可选-apip1-p2)
- [3. 数据模型](#3-数据模型)
- [4. 错误码](#4-错误码)

---

## 1. 必实现 API（P0）

### 1.1 URL Source SSRF 防护

**当前状态**：前端已有 validation，后端必须实现服务端校验。

#### POST /api/workspaces/{workspace_id}/sources

**Request**：
```json
{
  "urls": [
    {
      "url": "https://example.com",
      "title": "Optional Title",
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

**Response (成功)**：
```json
{
  "source": {
    "source_id": "src_xxx",
    "workspace_id": "ws_xxx",
    "title": "Example",
    "source_type": "url",
    "import_state": "ready",
    "url": "https://example.com"
  }
}
```

**Response (安全阻断)**：
```json
{
  "source": {
    "source_id": "src_xxx",
    "workspace_id": "ws_xxx",
    "title": "Example",
    "source_type": "url",
    "import_state": "blocked",
    "url": "https://example.com",
    "block_reason": "ssrf"
  },
  "warnings": ["此 URL 指向内部网络，不允许抓取"]
}
```

**block_reason 值**：
| 值 | HTTP Status | 用户消息 |
| --- | --- | --- |
| `ssrf` | 400 | "此 URL 指向内部网络，不允许抓取" |
| `private_ip` | 400 | "此 URL 指向私有网络地址，不允许抓取" |
| `timeout` | 408 | "此页面加载超时，请稍后重试" |
| `unsupported_content_type` | 415 | "此页面内容类型不支持，仅支持文本和 PDF" |
| `robots_blocked` | 403 | "此页面不允许被抓取（robots.txt 限制）" |
| `permission_denied` | 403 | "此页面需要登录或无权限访问" |
| `paywall` | 402 | "此页面需要付费订阅，无法抓取" |

#### GET /api/workspaces/{workspace_id}/sources/{source_id}

**Response**：
```json
{
  "source": {
    "source_id": "src_xxx",
    "workspace_id": "ws_xxx",
    "title": "Example",
    "source_type": "url",
    "import_state": "ready",
    "url": "https://example.com",
    "final_url": "https://example.com",  // redirect 后的 URL
    "content_type": "text/html",
    "block_reason": null
  }
}
```

---

## 2. 可选 API（P1-P2）

> 以下 API 根据 provider 可用性实现。若 provider 不可用，保持 capability 为 false。

### 2.1 OCR Provider (P1)

#### POST /api/ocr/provider/health

**Response**：
```json
{
  "available": true,
  "provider": "tesseract",
  "latency_ms": 100,
  "supported_languages": ["eng", "chi_sim", "chi_tra", "jpn", "kor"]
}
```

**or (not available)**：
```json
{
  "available": false,
  "provider": null,
  "unsupported_reason": "no_provider_configured"
}
```

#### POST /api/workspaces/{workspace_id}/sources/{source_id}/ocr

**Response**：
```json
{
  "source_id": "src_xxx",
  "status": "completed",
  "pages": [
    {
      "page_num": 1,
      "text": "Hello world",
      "bbox": [
        {"x": 10, "y": 20, "width": 100, "height": 20, "text": "Hello", "confidence": 0.95}
      ],
      "confidence": 0.92,
      "language": "eng"
    }
  ]
}
```

### 2.2 TTS Provider (P1)

#### POST /api/tts/provider/health

**Response**：
```json
{
  "available": true,
  "provider": "azure",
  "voices": ["en-US-JennyNeural", "zh-CN-XiaoxiaoNeural"],
  "default_voice": "en-US-JennyNeural"
}
```

### 2.3 Audio Artifact (P1)

#### POST /api/workspaces/{workspace_id}/artifacts/audio

**Request**：
```json
{
  "source_ids": ["src_xxx", "src_yyy"],
  "language": "en-US",
  "voice_id": "en-US-JennyNeural"
}
```

**Response**：
```json
{
  "artifact": {
    "artifact_id": "art_xxx",
    "workspace_id": "ws_xxx",
    "type": "audio_overview",
    "title": "Audio Overview",
    "status": "generating",
    "artifact_available": false,
    "created_at": "2026-06-02T10:00:00Z"
  }
}
```

#### GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}

**Response**：
```json
{
  "artifact": {
    "artifact_id": "art_xxx",
    "workspace_id": "ws_xxx",
    "type": "audio_overview",
    "title": "Audio Overview",
    "status": "ready",
    "artifact_available": true,
    "duration_seconds": 120,
    "script": [
      {
        "text": "This is the first segment.",
        "start_time": 0.0,
        "end_time": 3.5,
        "evidence_refs": [
          {"source_id": "src_xxx", "source_title": "Document A"}
        ]
      }
    ],
    "voice_metadata": {
      "provider": "azure",
      "voice_id": "en-US-JennyNeural",
      "language": "en-US"
    },
    "created_at": "2026-06-02T10:00:00Z"
  }
}
```

#### GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}/download

**Response**：
```json
{
  "url": "https://signed-url.example.com/audio.mp3?expires=xxx",
  "format": "mp3",
  "size_bytes": 2400000
}
```

### 2.4 Slide Artifact (P2)

#### POST /api/workspaces/{workspace_id}/artifacts/slides

**Request**：
```json
{
  "source_ids": ["src_xxx"],
  "topic": "Overview",
  "slide_count": 10
}
```

**Response**：
```json
{
  "artifact": {
    "artifact_id": "art_xxx",
    "workspace_id": "ws_xxx",
    "type": "slides",
    "title": "Presentation Overview",
    "status": "ready",
    "artifact_available": true,
    "slides": [
      {
        "slide_num": 1,
        "title": "Introduction",
        "bullets": ["Point 1", "Point 2"],
        "evidence_refs": [
          {"source_id": "src_xxx", "source_title": "Document A"}
        ]
      }
    ],
    "created_at": "2026-06-02T10:00:00Z"
  }
}
```

#### POST /api/workspaces/{workspace_id}/artifacts/slides/export

**Request**：
```json
{
  "artifact_id": "art_xxx"
}
```

**Response (有 PPTX 能力)**：
```json
{
  "download_url": "https://signed-url.example.com/slides.pptx?expires=xxx",
  "file_size": 50000,
  "slide_count": 10,
  "format": "pptx"
}
```

**Response (无 PPTX 能力)**：
```json
{
  "error": {
    "code": "SLIDE_OUTLINE_ONLY",
    "message": "PPTX export not available, use Markdown download instead."
  }
}
```

### 2.5 Mindmap Artifact (P2)

#### POST /api/workspaces/{workspace_id}/artifacts/mindmap

**Request**：
```json
{
  "source_ids": ["src_xxx"],
  "topic": "Topic Overview",
  "max_depth": 3
}
```

**Response**：
```json
{
  "artifact": {
    "artifact_id": "art_xxx",
    "workspace_id": "ws_xxx",
    "type": "mindmap",
    "title": "Mindmap: Topic Overview",
    "status": "ready",
    "artifact_available": true,
    "root_node": {
      "node_id": "node_root",
      "label": "Topic Overview",
      "summary": "Main topic summary",
      "children": [
        {
          "node_id": "node_1",
          "label": "Subtopic 1",
          "evidence_refs": [
            {"source_id": "src_xxx", "source_title": "Document A"}
          ],
          "children": []
        }
      ]
    },
    "created_at": "2026-06-02T10:00:00Z"
  }
}
```

### 2.6 Compare Artifact (P2)

#### POST /api/workspaces/{workspace_id}/artifacts/compare

**Request**：
```json
{
  "source_ids": ["src_xxx", "src_yyy"]
}
```

**Response**：
```json
{
  "artifact": {
    "artifact_id": "art_xxx",
    "workspace_id": "ws_xxx",
    "type": "compare",
    "title": "Document Comparison",
    "status": "ready",
    "artifact_available": true,
    "compare_set": ["src_xxx", "src_yyy"],
    "result": {
      "summary": "Two documents compared",
      "source_pairs": [
        {
          "source_a": "src_xxx",
          "source_b": "src_yyy",
          "source_a_title": "Document A",
          "source_b_title": "Document B",
          "similarities": [
            {
              "topic": "Shared Topic",
              "description": "Both discuss...",
              "evidence_refs": [
                {"source_id": "src_xxx"},
                {"source_id": "src_yyy"}
              ]
            }
          ],
          "differences": [
            {
              "topic": "Different Views",
              "source_a_position": "Document A says...",
              "source_b_position": "Document B says...",
              "evidence_a": [{"source_id": "src_xxx"}],
              "evidence_b": [{"source_id": "src_yyy"}]
            }
          ],
          "conflicts": []
        }
      ]
    },
    "created_at": "2026-06-02T10:00:00Z"
  }
}
```

---

## 3. 数据模型

### 3.1 SourceDetail (URL 扩展)

```typescript
interface URLSourceDetail {
  source_id: string
  workspace_id: string
  title: string
  source_type: "url" | "text" | "markdown" | "pdf"
  import_state: "ready" | "blocked" | "failed_import"
  url: string
  final_url?: string  // redirect 后的 URL
  content_type?: string
  block_reason?: string
  updated_at?: string
  trace_available?: boolean
  artifact_refs?: string[]
}
```

### 3.2 DocumentUnit (OCR 扩展)

```typescript
interface OCRDocumentUnit {
  unit_id: string
  source_id: string
  unit_type: "page" | "text" | "section"
  title?: string
  text_preview?: string
  content_type?: "text/plain" | "text/markdown" | "text/html"
  // OCR 特有字段
  text_basis?: string  // OCRPage.text
  bbox?: BBox[]
  confidence?: number
  language?: string
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

### 3.3 EvidenceRef

```typescript
interface EvidenceRef {
  source_id?: string
  source_title?: string
  unit_id?: string
  evidence_id?: string
  snippet?: string
  confidence?: number
}
```

### 3.4 GenerationMetadata

```typescript
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

## 4. 错误码

### 4.1 HTTP 错误码

| HTTP Status | code | 说明 |
| --- | --- | --- |
| 400 | `validation_error` | 请求参数错误 |
| 400 | `ssrf_blocked` | SSRF 攻击 |
| 400 | `private_ip_blocked` | 私有 IP |
| 402 | `paywall` | 付费内容 |
| 403 | `robots_blocked` | robots.txt 禁止 |
| 403 | `permission_denied` | 权限不足 |
| 404 | `not_found` | 资源不存在 |
| 408 | `timeout` | 请求超时 |
| 415 | `unsupported_content_type` | 不支持的 content-type |
| 422 | `capability_missing` | capability 不支持 |
| 422 | `ocr_required` | 需要 OCR 处理 |
| 500 | `unknown_service_error` | 未知错误 |
| 503 | `backend_unavailable` | 服务不可用 |

### 4.2 业务错误码

| error.code | 说明 | 处理建议 |
| --- | --- | --- |
| `INSUFFICIENT_SOURCES` | 资料不足 | 提示用户添加更多 sources |
| `OCR_REQUIRED` | 需要 OCR | 使用原生文本 PDF |
| `SLIDE_OUTLINE_ONLY` | 仅支持 outline | 使用 Markdown 下载 |
| `SSRF_BLOCKED` | SSRF 攻击 | 更换 URL |
| `PRIVATE_IP_BLOCKED` | 私有 IP | 更换 URL |

---

## 5. Capability Manifest 更新

### 5.1 当前状态

```json
{
  "capabilities": {
    "source_preview": true,
    "document_units": true,
    "evidence_spans": true,
    "source_level_preview": true,
    "unit_level_navigation": true,
    "precise_span_highlight": true,
    "citation_backjump": true,
    "ocr": false,
    "scanned_pdf_ocr": false
  }
}
```

### 5.2 目标状态（实现后）

```json
{
  "capabilities": {
    "source_preview": true,
    "document_units": true,
    "evidence_spans": true,
    "source_level_preview": true,
    "unit_level_navigation": true,
    "precise_span_highlight": true,
    "citation_backjump": true,
    "ocr": true,
    "scanned_pdf_ocr": true
  }
}
```

---

## 6. 快速参考

### 6.1 P0 必实现端点

| 方法 | 端点 | 说明 |
| --- | --- | --- |
| POST | `/api/workspaces/{workspace_id}/sources` | URL source 创建（返回 block_reason） |
| GET | `/api/workspaces/{workspace_id}/sources/{source_id}` | 获取 source（含 block_reason） |

### 6.2 P1 可选端点

| 方法 | 端点 | 说明 |
| --- | --- | --- |
| POST | `/api/ocr/provider/health` | OCR provider 健康检查 |
| POST | `/api/workspaces/{workspace_id}/sources/{source_id}/ocr` | OCR 处理 |
| POST | `/api/tts/provider/health` | TTS provider 健康检查 |
| POST | `/api/workspaces/{workspace_id}/artifacts/audio` | 创建 audio artifact |
| GET | `/api/workspaces/{workspace_id}/artifacts/{artifact_id}/download` | 下载 audio |

### 6.3 P2 可选端点

| 方法 | 端点 | 说明 |
| --- | --- | --- |
| POST | `/api/workspaces/{workspace_id}/artifacts/slides` | 创建 slide artifact |
| POST | `/api/workspaces/{workspace_id}/artifacts/slides/export` | 导出 PPTX |
| POST | `/api/workspaces/{workspace_id}/artifacts/mindmap` | 创建 mindmap artifact |
| POST | `/api/workspaces/{workspace_id}/artifacts/compare` | 创建 compare artifact |