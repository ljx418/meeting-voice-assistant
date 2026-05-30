# ResearchNotebook V1.6-E Research 补源 / 冲突分析 Report

日期：2026-05-28

## 阶段结论

状态：PASS_LIMITED_CONTRACT_SMOKE

V1.6-E 已完成受限 source-grounded Research 合同、前端入口、真实数据 smoke 和自动化回归。

该结论只代表：

- 无 sources 时 Research 会拒答并建议补源。
- 补源后可生成结构化 Research report。
- Report 包含 supported_conclusions / inferences / conflicts / missing_evidence。
- supported_conclusions 带可解析 evidence_refs。

不代表：

- Research 质量最终通过。
- 冲突分析完整准确。
- 通用互联网问答 ready。
- all-domain research ready。

## 实现范围

- 后端新增：
  - `POST /api/workspaces/{workspace_id}/research`
  - source-grounded Research report contract
  - no_sources / insufficient_evidence 拒答
  - supported_conclusions / inferences / conflicts / missing_evidence 字段
- 前端新增：
  - Chat answer 区域的 “生成 Research 综合” 入口
  - Research report 局部展示
  - evidence citation 复用 SourcePreview / DocumentUnit / EvidenceSpan 路径
- Smoke 新增：
  - `npm run smoke:v1.6-e-research`
  - fixtures: `fixtures/real/v1_6/research-workflow/`

## 真实数据

使用本地真实数据：

```text
Desktop/技术分享/11-数字人/AI数字人资料包/01_industry_overview.md
```

Smoke 问题：

```text
数字人行业的市场趋势和商业应用有哪些？
```

## 验收结果

| 验收项 | 结果 | 说明 |
| --- | --- | --- |
| target route probe | PASS | data_service target route 可访问。 |
| workspace create | PASS | 创建 V1.6-E smoke workspace。 |
| no-source refusal | PASS | 无 sources 时返回 `no_sources`，不硬答。 |
| source import | PASS | 导入数字人 Markdown。 |
| research report | PASS | 返回 3 条 supported conclusions。 |
| evidence resolution | PASS | evidence_ref 可解析 DocumentUnit 和 EvidenceSpan。 |
| cleanup | PASS | workspace archive 成功。 |

最终 smoke 决策：

```text
FINAL PASS_LIMITED_CONTRACT_SMOKE
```

## 执行命令

后端：

```bash
python3 -m pytest tests/test_target_http_research.py tests/test_target_http_evidence_spans.py tests/test_target_http_studio_artifacts.py -q
```

结果：16 passed。

前端：

```bash
npm run smoke:v1.6-e-research
npm run check
```

结果：

- `smoke:v1.6-e-research`：PASS_LIMITED_CONTRACT_SMOKE。
- `npm run check`：boundary checks、lint、127 tests、build 全部通过。

## PRD 规格检视

| PRD 要求 | 结果 | 说明 |
| --- | --- | --- |
| 资料不足时明确拒答 | PASS | no_sources / insufficient_evidence 不硬答。 |
| 引导补源 | PASS | 返回 suggested_source_actions。 |
| 补充 sources 后综合输出 | PASS_LIMITED | 生成 source-grounded structured report。 |
| 结论区分来源支持 / 推断 | PASS_LIMITED | supported_conclusions 和 inferences 分离。 |
| 冲突标注 | CONTRACT_ONLY | conflicts 字段存在；未声明完整冲突识别 ready。 |
| 每个关键结论带引用 | PASS_LIMITED | supported_conclusions 绑定 evidence_refs。 |

## 风险评估

开发计划漂移风险：MEDIUM。

虚假验收风险：MEDIUM。

原因：

- Research 输出当前是受限合同 smoke，不是最终质量评审。
- conflicts 为空只能证明字段存在，不能证明冲突识别能力完整。

收敛措施：

- 只声明 PASS_LIMITED_CONTRACT_SMOKE。
- V1.6-RC 必须进行人工质量审阅。
- 不声明通用 Research ready。

是否存在 HIGH 风险：NO。

## 下一阶段审计结论

下一阶段：V1.6-F Phase 2/3 Output Contract Discovery。

准入意见：Go for disabled shell / contract discovery only。

禁止进入真实 Audio / PPT / Mindmap / Document Compare 生成。
