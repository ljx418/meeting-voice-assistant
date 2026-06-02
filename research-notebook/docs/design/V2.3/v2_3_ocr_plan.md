# V2.3 OCR / Scanned PDF Provider Gate and MVP

日期：2026-06-02

## 阶段目标

决定是否实现 OCR；若实现，只做扫描 PDF 受限 MVP。

**约束**：不声明 all PDF ready，不声明 all-language/all-layout OCR ready。

## 决策路径

```
无 provider？
  → 保持 OCR_NOT_READY，记录 DECISION_RECORDED
  → 结束

有 provider？
  → 进入 V2.3-A ~ V2.3-D 实现
  → V2.3-RC 人工质量审查
```

## 阶段 Entry Gate

- [ ] V2.2 URL P1 通过验收（OCR 依赖 URL source）
- [ ] 当前分支无未合并的 V2.2 功能变更
- [ ] OCR provider 可用性确认

## 子阶段

### V2.3-A OCR Provider Contract

**目标**：定义 OCR provider 接口。

**API Contract**：
```
POST /api/ocr/provider/health
Response: { "available": true, "provider": "xxx", "latency_ms": 100 }

POST /api/workspaces/{workspace_id}/sources/{source_id}/ocr
Response: {
  source_id: string,
  status: "processing" | "completed" | "error",
  pages?: OCRPage[],
  error?: { code: string, message: string }
}

GET /api/workspaces/{workspace_id}/sources/{source_id}/ocr/status
Response: {
  source_id: string,
  status: "processing" | "completed" | "error",
  progress?: number  // 0-100
}
```

**OCR Provider Health Response**：
```typescript
interface OCRProviderHealth {
  available: boolean
  provider: string  // "tesseract" | "azure" | "google" | etc
  latency_ms?: number
  supported_languages?: string[]
  unsupported_reason?: string
}
```

### V2.3-B OCR Page Text Schema

**目标**：定义 OCR 输出结构。

**OCRPage Schema**：
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

**与 DocumentUnit 的映射**：
```typescript
interface OCRDocumentUnit extends DocumentUnit {
  // DocumentUnit 基础字段
  unit_id: string
  source_id: string
  unit_type: 'page'

  // OCR 特有字段
  text_basis: string  // OCRPage.text
  bbox: BBox[]
  confidence: number
  language?: string
}
```

### V2.3-C OCR DocumentUnit / EvidenceSpan Contract

**目标**：OCR 结果可进入 SourcePreview / DocumentUnit / EvidenceSpan。

**SourcePreview 对 OCR 的支持**：
```typescript
interface OCRSourcePreview extends SourcePreview {
  source_type: "pdf" | "image"  // 原始文件类型
  ocr_status: "processing" | "completed" | "unavailable"
  pages?: OCRPage[]
}
```

**EvidenceSpan 对 OCR 的支持**：
```typescript
interface OCREvidenceSpan extends EvidenceSpan {
  locator: {
    page_no: number
    bbox?: BBox
  }
  confidence: number
  text_basis: "ocr" | "native"
}
```

**验收**：
- [ ] OCR source 可进入 SourcePreview
- [ ] DocumentUnit 包含 OCR 特有字段（bbox、confidence）
- [ ] EvidenceSpan 支持 page_no + bbox locator

### V2.3-D Scanned PDF Smoke

**目标**：用真实扫描 PDF 测试。

**测试样本要求**：
- 至少 3 个不同类型的扫描 PDF
- 至少 1 个中文扫描 PDF（如果支持中文）
- 至少 1 个英文扫描 PDF

**Smoke 测试脚本**：
```javascript
// V2.3 OCR smoke 测试场景
const testCases = [
  {
    name: "英文扫描 PDF",
    file: "fixtures/ocr/english_scanned.pdf",
    expected: { page_count: 3, ocr_completed: true }
  },
  {
    name: "中文扫描 PDF",
    file: "fixtures/ocr/chinese_scanned.pdf",
    expected: { page_count: 5, ocr_completed: true }
  }
]
```

### V2.3-RC OCR Manual Quality Review

**目标**：人工确认 OCR 质量。

**人工审查检查项**：
- [ ] 无 provider 时保持 OCR_NOT_READY
- [ ] 有 provider 时 health probe PASS
- [ ] 扫描 PDF 生成 page text
- [ ] OCR unit 可进入 SourcePreview
- [ ] citation 可定位到 page / text span 或 bbox
- [ ] OCR confidence 可见（用于判断是否可信）

**质量标准**：
- OCR text 与原始 PDF 文字匹配度 >= 85%
- bbox 位置误差 <= 5px
- confidence >= 0.7 的 text 可直接使用

## 风险评估

| 风险 | 等级 | 缓解策略 |
| --- | --- | --- |
| OCR provider 不可用 | HIGH | Phase 1 先验证 provider |
| 多语言支持不足 | MEDIUM | 限制为单语言 MVP |
| OCR 质量不达标 | MEDIUM | 设置 confidence 阈值 |

## 实现顺序

### Phase 1: Provider Gate（1天）
1. 调用 OCR provider health API
2. 确认 provider 可用性
3. 若不可用，记录 DECISION_RECORDED，结束

### Phase 2: OCR Schema 对齐（1-2天）
1. 与后端对齐 OCRPage schema
2. 确认 bbox/confidence 字段
3. 确认 DocumentUnit 映射

### Phase 3: 前端 OCR UI（1-2天）
1. OCR processing 状态显示
2. SourcePreview OCR 支持
3. confidence 可见性

### Phase 4: Smoke + Manual Review（1天）
1. 运行 OCR smoke 测试
2. 人工质量审查
3. 更新报告

## 出门状态

- 无 provider：`OCR_DECISION_RECORDED`
- 有 provider 且通过：`OCR_PASS_LIMITED`

## 仍不声明

- all PDF ready
- all-language OCR ready
- all-layout OCR ready

## 下一步

V2.3 通过后进入 V2.4 Audio Overview。