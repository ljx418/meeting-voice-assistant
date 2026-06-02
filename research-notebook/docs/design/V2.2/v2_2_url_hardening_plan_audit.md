# V2.2 URL Hardening Plan Audit

日期：2026-06-02

## 审计结论

**当前状态**：待审计

## 审计检查表

### 规格漂移风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| 不声明 all websites ready | ✅ | 计划明确限制为 "limited URL P1" |
| SSRF/Private IP 防护范围明确 | ⏳ | 需要确认具体 IP 范围 |
| redirect 安全校验范围明确 | ⏳ | 需要确认 follow redirects 行为 |
| content-type allowlist 明确 | ⏳ | 需要确认具体允许的 content-type |
| URL citation 可定位 | ⏳ | 需要确认 SourcePreview 支持 URL source |

### 虚假验收风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| 样本量足够（10+ 公开 URL，3+ 失败） | ⏳ | 测试样本选择标准 |
| SSRF 攻击样本覆盖 | ⏳ | 需要测试 private IP、localhost、metadata service |
| 安全测试用例覆盖 | ⏳ | 需要覆盖 redirect、content-type 等场景 |
| 失败场景有明确错误消息 | ⏳ | robots_blocked / permission_denied / paywall 等 |

### 实现风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| 后端 URL gateway 安全实现确认 | ⏳ | 需要确认 data_service 是否有安全层 |
| 前端 URL source UI 实现 | ⏳ | 需要确认 SourcePreview 是否支持 URL source |
| SSRF 防护前端能检测 | ⏳ | 后端返回 block_reason 时前端如何处理 |

### 规格漂移风险量化

| 功能 | 风险 | 理由 |
| --- | --- | --- |
| URL Gateway 安全合同 | MEDIUM | 需要与后端对齐具体的安全检查项 |
| SSRF 防护 | MEDIUM | 前端无法完全防护，需要后端配合 |
| redirect 校验 | MEDIUM | 需要确认 follow redirect 后是否仍校验 |
| URL source UI | LOW | 已有 SourcePreview 可复用 |

## 审计结论

**规格漂移风险**：MEDIUM
- URL gateway 安全合同需要后端确认

**虚假验收风险**：MEDIUM
- 测试样本选择标准需要明确
- 安全测试用例需要具体化

**实现风险**：MEDIUM
- 主要依赖后端安全实现
- 前端只能做显示层

**是否可以进入实现**：待确认以下事项

### 前置确认事项

- [ ] 确认 data_service URL gateway 安全检查项
- [ ] 确认 SSRF 防护的具体实现（还是仅依赖前端）
- [ ] 确认 URL source 是否进入 SourcePreview
- [ ] 确认测试样本选择标准

若上述事项全部确认可行，审计通过。
若有任何一项不可行，需要先解决再进入实现。