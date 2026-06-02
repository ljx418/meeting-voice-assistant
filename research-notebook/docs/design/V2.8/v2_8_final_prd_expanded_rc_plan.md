# V2.8 Final PRD Expanded RC

日期：2026-06-02

## 阶段目标

汇总 V2.1-V2.7，形成 PRD 扩展版最终验收。

**约束**：不扩大声明范围，不跳过任何验收步骤。

## 前置条件

- [ ] V2.1 PRD MVP Gap Closure 通过
- [ ] V2.2 URL P1 受限通过
- [ ] V2.3 OCR 若实现则通过，否则保持 NOT_READY
- [ ] V2.4 ~ V2.7 若实现则单项 PASS_LIMITED

## 阶段 Entry Gate

- [ ] 所有 V2.1~V2.7 阶段已完成
- [ ] 所有 smoke 测试通过
- [ ] 所有人工质量审查完成
- [ ] PRD coverage matrix 已更新

## 验收流程

### 1. 阶段完成确认

| 阶段 | 出门状态 | 完成日期 | 验证方法 |
| --- | --- | --- | --- |
| V2.1 PRD MVP Gap Closure | `PRD_MVP_GAP_CLOSURE_PASS_LIMITED` | ⏳ | smoke + 人工 |
| V2.2 URL P1 | `URL_P1_PASS_LIMITED` | ⏳ | smoke + 样本测试 |
| V2.3 OCR | `OCR_DECISION_RECORDED` 或 `OCR_PASS_LIMITED` | ⏳ | provider gate |
| V2.4 Audio | `AUDIO_OVERVIEW_PASS_LIMITED` | ⏳ | smoke + 人工 |
| V2.5 PPT | `PPT_PASS_LIMITED` 或 `SLIDE_OUTLINE_ONLY` | ⏳ | smoke + 人工 |
| V2.6 Mindmap | `MINDMAP_PASS_LIMITED` | ⏳ | smoke + 人工 |
| V2.7 Document Comparison | `DOCUMENT_COMPARISON_PASS_LIMITED` | ⏳ | smoke + 人工 |

### 2. PRD Coverage Matrix 更新

**更新文件**：`v2_prd_coverage_matrix.md`

**更新内容**：
- V2.1 Features：Sources 搜索、Notes 管理、Studio artifact、AI 质量
- V2.2：URL P1
- V2.3~V2.7：OCR/Audio/PPT/Mindmap/Compare 状态

**Coverage Matrix 格式**：
```markdown
| 能力 | V1 状态 | V2 目标 | V2.x 完成 | 声明 |
| --- | --- | --- | --- | --- |
| Sources 搜索 | NOT_READY | PASS_LIMITED | ⏳ | ⏳ |
| Notes 管理 | NOT_READY | PASS_LIMITED | ⏳ | ⏳ |
```

### 3. 自动化 smoke

```bash
# 全量检查
npm run check

# V2.x 汇总 smoke
npm run smoke:v2-x-all

# 逐阶段验证
npm run smoke:v2.1-full
npm run smoke:v2.2-url
npm run smoke:v2.3-ocr  # 如果实现了
npm run smoke:v2.4-audio  # 如果实现了
npm run smoke:v2.5-ppt  # 如果实现了
npm run smoke:v2.6-mindmap  # 如果实现了
npm run smoke:v2.7-compare  # 如果实现了
```

### 4. Browser / Chrome E2E

**用户旅程覆盖**：
| 旅程 | 覆盖 | 测试方法 |
| --- | --- | --- |
| A: 导入与导读 | ⏳ | Playwright E2E |
| B: 可信引用问答 | ⏳ | Playwright E2E |
| C: 轻量 Studio 输出 | ⏳ | Playwright E2E |
| D: Research 补源与冲突分析 | ⏳ | Playwright E2E |
| E: 高风险后置能力 | ⏳ | 验证 disabled 状态 |

**disabled 工具验证**：
- [ ] OCR 工具（若未实现）正确显示 disabled
- [ ] Audio 工具（若未实现）正确显示 disabled
- [ ] PPT 工具（若未实现）正确显示 disabled
- [ ] Mindmap 工具（若未实现）正确显示 disabled
- [ ] Compare 工具（若未实现）正确显示 disabled
- [ ] disabled 工具不得触发 API 请求

### 5. 人工质量评分

**评分标准**：
| 能力 | 质量标准 | 评分方法 |
| --- | --- | --- |
| Sources 搜索 | 可用性 >= 4/5 | 人工测试 10 个查询 |
| Notes 管理 | citation 保留率 = 100% | 抽查 5 个 notes |
| Studio artifact | artifact 可管理 | 手动测试 CRUD |
| AI Guide | Guide 可用性 >= 4/5 | 人工评分 20 个样本 |
| AI QA | citation 可定位率 >= 90% | 抽样测试 |
| AI QA | 拒答正确率 >= 80% | 抽样测试 |
| AI QA | 高危幻觉 = 0 | 人工审查 |
| Audio (若实现) | 内容无资料外硬答 | 人工审查 |
| PPT (若实现) | 内容和结构可用 | 人工审查 |
| Mindmap (若实现) | 结构正确 | 人工审查 |
| Compare (若实现) | 证据正确 | 人工审查 |

### 6. 声明边界确认

**可以声明**：
- V2.1 features smoke-ready
- URL P1 limited pass
- OCR decision recorded or pass-limited
- Audio decision recorded or pass-limited
- PPT decision recorded or pass-limited
- Mindmap decision recorded or pass-limited
- Compare decision recorded or pass-limited

**仍不能声明**：
- all websites URL ready
- all-source-type ready
- OCR all-language/all-layout ready
- Audio all-languages ready
- PPT all-presentation-styles ready
- Mindmap all-styles ready
- Compare all-document-types ready
- full AI quality ready
- cloud sync / collaboration ready

## 出门状态

- `V2_X_PRD_EXPANDED_RC_READY_WITH_LIMITATIONS`

## 最终声明模板

```
ResearchNotebook V2.x is PRD expanded RC ready with accepted limitations for:
- Validated PDF / TXT / Markdown sources
- Approved public URL (P1)
- V2.1 features: Sources search, Notes management, Studio artifact management, AI quality
- [OCR: DECISION_RECORDED | PASS_LIMITED]
- [Audio: DECISION_RECORDED | PASS_LIMITED]
- [PPT: SLIDE_OUTLINE_ONLY | PPT_GENERATION_PASS_LIMITED]
- [Mindmap: NOT_READY | MINDMAP_PASS_LIMITED]
- [Compare: NOT_READY | DOCUMENT_COMPARISON_PASS_LIMITED]
```

## 下一步

V2.8 通过后，V2 文档体系完整关闭。后续如继续推进，应新开 V3 或 V2.1.x 子计划。