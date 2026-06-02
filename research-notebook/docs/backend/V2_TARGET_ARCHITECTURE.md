# ResearchNotebook V2.x 目标架构设计

日期：2026-06-02
版本：v1.0

---

## 1. 系统架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ResearchNotebook Frontend                         │
│                   (React + TypeScript + Vite + TanStack Query)            │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Workspace   │  │  Source     │  │   Studio    │  │   Query     │     │
│  │  Page      │  │  Library    │  │   Panel     │  │   Panel     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Notes     │  │  Source     │  │   Audio     │  │   Slide     │     │
│  │   Panel     │  │  Preview    │  │   Player    │  │   Preview   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    API Client Layer                              │   │
│  │  dataServiceClient.ts  │  workspaceM2Queries.ts  │  api.ts        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │ HTTP/REST
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         Data Service Backend                              │
│                   (/Users/Zhuanz/Desktop/workspace/data_service)           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                        API Layer (FastAPI / Flask)                    │ │
│  │  /api/workspaces/*  │  /api/sources/*  │  /api/artifacts/*           │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│  ┌──────────────────────────────────┴───────────────────────────────────┐ │
│  │                         Service Layer                                 │ │
│  │                                                                       │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │ │
│  │  │  Source Service  │  │ Artifact Service │  │   LLM Service   │        │ │
│  │  │  - URL Fetch     │  │ - Studio         │  │ - Guide Gen     │        │ │
│  │  │  - SSRF Guard    │  │ - Slides         │  │ - Research      │        │ │
│  │  │  - Content Parse │  │ - Audio          │  │ - Compare       │        │ │
│  │  │  - OCR (optional)│  │ - Mindmap        │  │ - Query         │        │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │ │
│  │                                                                       │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │ │
│  │  │  Graph Service   │  │  Index Service   │  │  Quality Service │        │ │
│  │  │  - GraphRAG      │  │  - Document Units │  │  - Citation      │        │ │
│  │  │  - Neighbors     │  │  - Evidence Spans │  │  - Feedback      │        │ │
│  │  │  - Communities   │  │  - Trace          │  │  - Fallback Det  │        │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘        │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│  ┌──────────────────────────────────┴───────────────────────────────────┐ │
│  │                       External Provider Layer                         │ │
│  │                                                                       │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │ │
│  │  │  OCR Provider │  │ TTS Provider │  │  LLM Provider │                │ │
│  │  │  (optional)   │  │ (optional)   │  │  (required)   │                │ │
│  │  │  - Tesseract  │  │ - Azure      │  │  - OpenAI     │                │ │
│  │  │  - Azure      │  │ - Google     │  │  - Anthropic  │                │ │
│  │  │  - Google     │  │ - ElevenLabs │  │               │                │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                    │                                       │
│  ┌──────────────────────────────────┴───────────────────────────────────┐ │
│  │                         Storage Layer                                  │ │
│  │                                                                       │ │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │ │
│  │  │  Workspace Store │  │  Source Store     │  │  Artifact Store  │     │ │
│  │  │  - Metadata       │  │  - Content        │  │  - Generated     │     │ │
│  │  │  - Settings       │  │  - Index          │  │  - Metadata      │     │ │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘     │ │
│  │                                                                       │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                          │ │
│  │  │  Graph Store      │  │  File Store       │                          │ │
│  │  │  - Nodes          │  │  - Original Files │                          │ │
│  │  │  - Edges          │  │  - Extracted Text │                          │ │
│  │  │  - Communities    │  │  - OCR Output     │                          │ │
│  │  └──────────────────┘  └──────────────────┘                          │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 组件职责

### 2.1 Frontend Components

| 组件 | 职责 | 依赖服务 |
| --- | --- | --- |
| `WorkspacePage` | 主工作空间页面，管理 sources 和 tools | Sources API, Studio API |
| `SourceLibrary` | 显示 source 列表，支持搜索 | Sources API, Search API |
| `SourceImportForm` | 导入文件/URL/文本 | Sources API |
| `SourcePreviewDrawer` | 显示 source 预览 | SourcePreview API |
| `StudioPanel` | 生成 artifacts（Guide, Research, Studio） | Studio API |
| `NotesPanel` | Notes CRUD（localStorage） | - |
| `QueryPanel` | 问答界面 | Query API |

### 2.2 Backend Services

| Service | 职责 | 关键依赖 |
| --- | --- | --- |
| `SourceService` | Source 生命周期，URL fetch，content parse | SSRF Guard, Content Parser |
| `ArtifactService` | Artifacts 统一管理（Studio, Audio, Slides, Mindmap, Compare） | LLM Service, External Providers |
| `LLMService` | LLM 调用（Guide, Research, Compare 生成） | LLM Provider |
| `GraphService` | GraphRAG 查询，neighbors, communities | Graph Store |
| `IndexService` | Document units, evidence spans 索引 | Source Store |
| `QualityService` | Citation 检查，feedback，fallback 检测 | - |
| `OCRService` | 扫描 PDF OCR 处理 | OCR Provider |
| `TTSService` | 文本转语音 | TTS Provider |
| `PPTService` | PPTX 生成 | - |

### 2.3 External Providers

| Provider | 用途 | 集成方式 |
| --- | --- | --- |
| `LLM Provider (OpenAI/Anthropic)` | Guide 生成, Research, Compare | API |
| `OCR Provider (Tesseract/Azure/Google)` | 扫描 PDF OCR | API / SDK |
| `TTS Provider (Azure/Google/ElevenLabs)` | Audio Overview | API |

---

## 3. 数据流

### 3.1 Source Import Flow

```
User Input (URL/File/Text)
        │
        ▼
Frontend: SourceImportForm
        │
        │ POST /api/workspaces/{id}/sources
        ▼
Backend: SourceService
        │
        ├─► SSRF Guard (check URL)
        │       │
        │       ├─► Blocked → return block_reason
        │       │
        │       └─► Allowed → continue
        │
        ├─► Content Fetch (for URL)
        │       │
        │       ├─► Fetch URL
        │       ├─► Follow Redirects (with security checks)
        │       └─► Validate Content-Type
        │
        ├─► Content Parser
        │       │
        │       ├─► Extract text (HTML, PDF, etc.)
        │       └─► OCR (if scanned PDF, optional)
        │
        └─► Index Service
                │
                ├─► Create Document Units
                ├─► Index Evidence Spans
                └─► Store Artifact Refs
```

### 3.2 Query Flow

```
User Question
        │
        ▼
Frontend: QueryPanel
        │
        │ POST /api/workspaces/{id}/query
        ▼
Backend: LLMService
        │
        ├─► Retrieve relevant Sources
        │       │
        │       └─► IndexService.search()
        │
        ├─► Check sources quality
        │       │
        │       └─► QualityService.checkFallbackMode()
        │               │
        │               └─► If low quality → set fallback_mode=true
        │
        ├─► Generate Answer with Citations
        │       │
        │       └─► LLM Provider
        │
        └─► Return Response
                │
                ├─► answer
                ├─► evidence (with source refs)
                ├─► coverage_status
                └─► generation_metadata.fallback_mode
```

### 3.3 Artifact Generation Flow

```
User Request (Audio/Slides/Mindmap/Compare)
        │
        ▼
Frontend: StudioPanel
        │
        │ POST /api/workspaces/{id}/artifacts/{type}
        ▼
Backend: ArtifactService
        │
        ├─► Validate Sources
        │       │
        │       └─► Check sufficient sources
        │
        ├─► Generate Content
        │       │
        │       ├─► Audio → TTSService → Audio File
        │       ├─► Slides → PPTService / Markdown → Slide File
        │       ├─► Mindmap → LLMService → Mindmap Tree
        │       └─► Compare → LLMService → Comparison Result
        │
        └─► Store & Return
                │
                ├─► Store Artifact
                ├─► Return Artifact ID & Status
```

---

## 4. API 分层

```
HTTP Request
        │
        ▼
┌───────────────────┐
│   API Router      │  /api/workspaces/*, /api/sources/*, /api/artifacts/*
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   Validators       │  Request validation, schema check
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   Services         │  Business logic
│  - SourceService   │
│  - ArtifactService │
│  - LLMService      │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   External         │  Provider calls (LLM, OCR, TTS)
│   Providers        │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   Storage          │  Workspace, Source, Graph, Artifact stores
└───────────────────┘
```

---

## 5. 关键数据模型关系

```
Workspace
   │
   ├── Sources[]
   │      │
   │      ├── DocumentUnits[]
   │      │      │
   │      │      └── EvidenceSpans[]
   │      │
   │      └── Artifacts[]
   │
   ├── Graph
   │      ├── Nodes[]
   │      ├── Edges[]
   │      └── Communities[]
   │
   └── Artifacts[]
          │
          ├── Studio Artifact
          ├── Audio Artifact
          ├── Slide Artifact
          ├── Mindmap Artifact
          └── Compare Artifact
```

---

## 6. Security Model

### 6.1 SSRF Protection

```
URL Input
    │
    ▼
Parse URL ──────────────────────────────────────┐
    │                                            │
    ▼                                            ▼
Check Hostname                           Check IP (after DNS resolve)
    │                                            │
    ├─► Is localhost? ─────► BLOCK (ssrf)         │
    │                                            │
    ├─► Is private IP? ───► BLOCK (private_ip)   │
    │                                            │
    ├─► Is metadata IP? ──► BLOCK (ssrf)         │
    │                                            │
    └─► Is public IP? ────► ALLOW                 │
                                                  │
Check IP ───────────────────────────────────────┘
    │
    ├─► 10.0.0.0/8 ─────────► BLOCK
    │
    ├─► 172.16.0.0/12 ─────► BLOCK
    │
    ├─► 192.168.0.0/16 ────► BLOCK
    │
    ├─► 127.0.0.0/8 ───────► BLOCK
    │
    ├─► 169.254.0.0/16 ────► BLOCK
    │
    └─► Public IP ─────────► ALLOW
```

### 6.2 Content Security

| Content-Type | Action |
| --- | --- |
| `text/*` | Allow |
| `application/pdf` | Allow |
| `*` (other) | Reject (unsupported_content_type) |

---

## 7. Capability Matrix

| Capability | Status | Description |
| --- | --- | --- |
| `source_preview` | ✅ Implemented | Source preview |
| `document_units` | ✅ Implemented | Document unit navigation |
| `evidence_spans` | ✅ Implemented | Evidence span navigation |
| `source_level_preview` | ✅ Implemented | Source-level preview |
| `unit_level_navigation` | ✅ Implemented | Unit navigation |
| `precise_span_highlight` | ✅ Implemented | Precise span highlight |
| `citation_backjump` | ✅ Implemented | Citation backjump |
| `ocr` | ⏳ Optional | OCR for scanned PDFs |
| `scanned_pdf_ocr` | ⏳ Optional | Scanned PDF OCR |

---

## 8. Deployment

### 8.1 Components

| Component | Technology | Location |
| --- | --- | --- |
| Frontend | Vite + React | `/Users/Zhuanz/Desktop/workspace/research-notebook` |
| Backend | Python/FastAPI | `/Users/Zhuanz/Desktop/workspace/data_service` |
| Database | SQLite / PostgreSQL | Data service storage |
| File Storage | Local FS / S3 | Original files, artifacts |

### 8.2 Environment Variables

```bash
# Backend
DATA_SERVICE_WORKSPACE_ROOT=/path/to/workspaces
DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS=/path/to/allowed
API_KEY=xxx
JWT_DEV_MODE=false

# Optional Providers
OCR_PROVIDER=azure|google|tesseract
OCR_API_KEY=xxx
TTS_PROVIDER=azure|google|elevenlabs
TTS_API_KEY=xxx
LLM_PROVIDER=openai|anthropic
LLM_API_KEY=xxx
```

---

## 9. Future Extensions

### 9.1 V3 规划

| Feature | Description |
| --- | --- |
| Real-time Collaboration | Multi-user workspace |
| Cloud Sync | Cross-device sync |
| Plugin System | Extensible providers |
| Advanced Graph | Entity extraction, knowledge graph |

### 9.2 Provider Integration

```
Provider Interface (Abstract)
    │
    ├── OCR Provider
    │      ├── TesseractProvider
    │      ├── AzureOCRProvider
    │      └── GoogleVisionProvider
    │
    ├── TTS Provider
    │      ├── AzureTTSProvider
    │      ├── GoogleTTSProvider
    │      └── ElevenLabsProvider
    │
    └── LLM Provider
           ├── OpenAIProvider
           └── AnthropicProvider
```

---

## 10. 参考文档

| 文档 | 位置 |
| --- | --- |
| 后端服务 PRD | `docs/backend/V2_BACKEND_SERVICE_PRD.md` |
| API 接口矩阵 | `docs/backend/V2_BACKEND_API_MATRIX.md` |
| 前端 API 客户端 | `src/shared/api/dataServiceClient.ts` |
| 前端类型定义 | `src/shared/types/api.ts` |
| V2.x 设计文档 | `docs/design/V2.x/` |
| Data Service README | `/Users/Zhuanz/Desktop/workspace/data_service/backend/README.md` |