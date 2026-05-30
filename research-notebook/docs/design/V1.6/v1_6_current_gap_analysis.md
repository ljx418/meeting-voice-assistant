# ResearchNotebook V1.6 Current Gap Analysis

日期：2026-05-29

## 一句话结论

V1.6 将 V1.5 的数字人 P0 质量 smoke 扩展为 PRD 剩余闭环计划：URL 抽取、多数据集评分、OCR 合同、Studio 导出、Research 补源 / 冲突分析、Phase 2/3 输出合同发现。云同步 / 协作已剔除为 OUT_OF_SCOPE。V1.6-A 已完成限定公开 URL smoke，V1.6-D 已完成 Studio Markdown / JSON 导出自动化验证，V1.6-E 已完成 Research 受限合同 smoke，V1.6-F 已完成 Phase 2/3 disabled shell。V1.6-RC 已通过 ChromeCLI 路径回归和用户人工截图 / UX 验收，最终状态为 scoped acceptance pass。

## 当前状态

| 能力 | 状态 | V1.6 处理方式 |
| --- | --- | --- |
| V1.6-0 Scope Rebase | PASS | V1.5 revalidation 已确认；云同步 / 协作仍 OUT_OF_SCOPE；V1.6-A 安全门禁已补齐。 |
| V1.5 AI Guide / QA / Studio 主路径 | PASS_LIMITED | 回归保留。 |
| URL 正文抽取 | PASS_LIMITED | V1.6-A 限定公开 HTTP URL smoke 通过；不代表 all websites ready。 |
| 多数据集质量评分 | PASS_LIMITED_ACCEPTED | V1.6-B 自动候选评估已完成；三组真实数据集结构化 smoke 通过，并经用户截图 / 关键文本验收接受。 |
| OCR / 扫描 PDF | CONTRACT_DISCOVERY_READY | V1.6-C 已明确 `ocr=false` / `scanned_pdf_ocr=false`，扫描 PDF 返回 `ocr_required`，不声明 OCR ready。 |
| Studio 导出 | PASS_LIMITED_UI_TESTED | V1.6-D 已实现 Markdown/JSON 导出，保留 citation metadata；真实浏览器下载文件人工检查后移到 V1.6-RC。 |
| Research 补源 / 冲突分析 | PASS_LIMITED_CONTRACT_SMOKE | V1.6-E 已实现 no-source 拒答、补源后 structured Research report 和 resolvable evidence_refs；冲突分析仍只是合同字段，不声明完整 ready。 |
| Audio / PPT / Mindmap / Compare | DISABLED_READY | V1.6-F 已完成合同发现壳；不生成真实输出，不声明 ready。 |
| V1.6-RC 人工验收 | V1.6_FINAL_ACCEPTANCE_PASS_SCOPED | ChromeCLI 最新截图报告和关键文本已由用户验收通过；完成声明仍限 PRD MVP scoped path。 |
| 云同步 / 协作 | OUT_OF_SCOPE | 从 V1.x 剩余范围剔除。 |

## 主要风险

| 风险 | 等级 | 收敛措施 |
| --- | --- | --- |
| URL 抽取被误认为全网站支持 | MEDIUM | 只声明限定站点；失败站点必须稳定返回 unsupported。 |
| URL 抽取产生 SSRF 或权限越界 | MEDIUM | V1.6-A 已阻断 localhost / unsafe URL；后续扩展站点仍需持续测试 redirect / permission / robots。 |
| 多数据集评分被误写成全域质量 ready | MEDIUM | 用户已验收截图报告，但只声明 approved datasets / scoped quality smoke。 |
| OCR provider 缺失却声明 OCR ready | LOW | V1.6-C 已完成 disabled contract，manifest 明确 OCR false。 |
| Studio 导出被误写成全格式输出 ready | MEDIUM | 仅 Markdown / JSON scoped export pass；Audio / PPT / Mindmap / Compare 仍 disabled。 |
| Phase 2/3 disabled shell 被误读为 ready | LOW | UI 已显示合同未就绪 / 暂不可用，不发起后端请求。 |
| Research 输出变成无来源互联网问答 | MEDIUM | V1.6-E route 只使用 Notebook evidence，无 evidence 时拒答；RC 仍需人工审查。 |
| Research 冲突分析被误认为完整 ready | MEDIUM | conflicts 字段存在但不声明完整冲突识别能力，最终人工质量检查后移到 RC。 |

## 停止规则

任一阶段出现 HIGH 规格漂移或 HIGH 虚假验收风险，停止自动推进，重新进入计划审计。

## V1.6 完成口径

当前最多声明：

```text
ResearchNotebook V1.6 PRD MVP browser path and manual UX / quality screenshot review are accepted for validated PDF / TXT / Markdown and limited URL sources, with source-grounded Guide, QA, Studio exports, and Research contract smoke on approved datasets.
```

仍不能声明：

- all websites URL extraction ready。
- OCR ready。
- Audio Overview ready。
- PPT generation ready。
- Mindmap ready。
- Document comparison ready。
- all-domain Research ready。
- cloud sync / collaboration ready。

## 下一阶段

V1.6-FINAL Release Handoff / Scoped Sync。目标是整理最终文档、复跑最终验证、执行 scoped commit / push。不得新增功能，不进入 V1.7。
