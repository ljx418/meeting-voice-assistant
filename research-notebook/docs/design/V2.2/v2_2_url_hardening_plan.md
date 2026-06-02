# V2.2 Sources P1 URL Hardening 开发计划

日期：2026-06-02

## 1. 背景

V2.1 已完成 PRD MVP Gap Closure。V2.2 目标把 limited URL 抽取推进到更稳定的 P1 能力。

**约束**：不声明 all websites ready。

## 2. 阶段 Entry Gate

- [ ] V2.1 通过验收
- [ ] 当前分支无未合并的 V2.1 功能变更
- [ ] 后端 URL gateway 安全实现已确认

## 3. 开发任务

### 3.1 服务端 URL Gateway 安全合同

**目标**：建立 URL 抽取的安全边界。

**API Contract**：
```
POST /api/workspaces/{workspace_id}/sources
Body: {
  url: "https://...",
  title?: "Page Title"
}
Response: {
  source: SourceDetail,
  block_reason?: "ssrf" | "private_ip" | "timeout" | "unsupported_content_type" | "robots_blocked" | "permission_denied" | "paywall"
}

GET /api/workspaces/{workspace_id}/sources/{source_id}/preview
Response: {
  preview: SourcePreview,
  // 包含 URL source 的 preview
}
```

**安全检查层**：
1. **SSRF 防护**：拒绝 private IP、localhost、metadata service
   - Private IP 范围：10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
   - Localhost：127.0.0.0/8, ::1
   - Metadata service：169.254.0.0/16

2. **Redirect 校验**：follow redirect 后二次安全检查
   - 记录 redirect chain
   - 每个 URL 都必须通过安全检查

3. **Content-Type allowlist**：
   - text/* (text/html, text/plain, text/markdown)
   - application/pdf
   - 拒绝其他类型

4. **Size limit**：
   - max_response_size: 10MB
   - timeout: 30s
   - redirect_limit: 5

### 3.2 安全阻断实现

**目标**：unsafe_url / private IP / metadata service 全部拒绝。

**前端行为**：
```typescript
// 创建 URL source 时的错误处理
if (response.block_reason) {
  // 显示用户可理解的错误消息
  showError(getUserFriendlyMessage(response.block_reason))
}
```

**用户可理解错误消息映射**：
| block_reason | 用户消息 |
|---|---|
| ssrf | "此 URL 指向内部网络，不允许抓取" |
| private_ip | "此 URL 指向私有网络地址，不允许抓取" |
| timeout | "此页面加载超时，请稍后重试" |
| unsupported_content_type | "此页面内容类型不支持，仅支持文本和 PDF" |
| robots_blocked | "此页面不允许被抓取（robots.txt 限制）" |
| permission_denied | "此页面需要登录或无权限访问" |
| paywall | "此页面需要付费订阅，无法抓取" |

**验收**：
- [ ] private IP (10.x, 172.16.x, 192.168.x) 返回 blocked
- [ ] localhost 返回 blocked
- [ ] metadata service (169.254.x) 返回 blocked
- [ ] redirect 后仍执行安全校验

### 3.3 稳定错误处理

**目标**：robots / permission / paywall 返回用户可理解的错误。

**Error State 设计**：
```typescript
interface SourceImportError {
  source_id: string
  error_type: 'ssrf' | 'private_ip' | 'timeout' | 'unsupported_content_type' | 'robots_blocked' | 'permission_denied' | 'paywall'
  user_message: string
  retryable: boolean
}
```

**UI 展示**：
- SourceLibrary 中显示错误状态
- 错误图标 + 用户消息
- 重试按钮（如果是 retryable）

### 3.4 URL Source UI 集成

**目标**：URL source 进入 SourcePreview / DocumentUnit / EvidenceSpan。

**URL Source 特有字段**：
```typescript
interface URLSourceDetail extends SourceDetail {
  url: string
  final_url?: string  // redirect 后的 URL
  content_type?: string
  block_reason?: string
  import_state: 'ready' | 'blocked' | 'failed_import'
}
```

**验收**：
- [ ] URL source 可在 SourceLibrary 中显示
- [ ] 点击可打开 SourcePreview
- [ ] citation 可定位

## 4. 实现顺序

### Phase 1: 安全合同对齐（1-2天）
- 与后端对齐 block_reason 字段
- 确认 SSRF/redirect/content-type 安全检查实现
- 测试安全阻断行为

### Phase 2: 前端错误处理（1-2天）
- 错误消息映射
- SourceLibrary 错误状态显示
- SourcePreview 支持 URL source

### Phase 3: 验收测试（1天）
- 10+ 公开 URL 测试
- 3+ 稳定失败测试
- SSRF 样本测试

## 5. 风险评估

| 风险 | 等级 | 缓解策略 |
| --- | --- | --- |
| 后端安全实现不完整 | MEDIUM | Phase 1 先验证安全行为 |
| 前端错误消息不匹配 | LOW | 与后端对齐错误码 |
| URL source preview 性能 | LOW | 添加 loading state |
| 安全测试样本覆盖 | MEDIUM | 准备标准测试样本 |

## 6. 下一步

V2.2 通过后进入 V2.3 OCR / Scanned PDF Provider Gate。