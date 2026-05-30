# ResearchNotebook V1.6-E Research 补源 / 冲突分析 Plan

日期：2026-05-28

## 阶段目标

实现 PRD 7.4 的受限 Research 闭环：

1. 当前 Notebook sources 无法覆盖问题时，明确拒答并给出补源建议。
2. 用户补充来源后，可生成结构化 Research 输出。
3. Research 输出必须区分：
   - supported_conclusions
   - inferences
   - conflicts
   - missing_evidence
4. 每条关键结论必须携带可解析 evidence_refs。

## 范围

- 新增 source-grounded Research 后端合同。
- 新增 Research 前端入口和局部展示。
- 新增真实数据 smoke。
- 使用已有 SourcePreview / DocumentUnit / EvidenceSpan 引用路径。
- 不自动联网搜索。
- 不使用 provider 常识替代 Notebook sources。

## 后端合同

Route:

```text
POST /api/workspaces/{workspace_id}/research
```

Request:

```ts
type ResearchRequest = {
  question: string;
  top_k?: number;
};
```

Response:

```ts
type ResearchReport = {
  research_available: boolean;
  question: string;
  coverage_status: "source_supported" | "insufficient_evidence" | "no_sources";
  answer_basis: "source_supported" | "source_based_inference" | "source_grounded_refusal";
  supported_conclusions: Array<{
    claim: string;
    evidence_refs: QueryEvidence[];
  }>;
  inferences: Array<{
    inference: string;
    evidence_refs: QueryEvidence[];
    inference_notice: string;
  }>;
  conflicts: Array<{
    topic: string;
    positions: Array<{
      claim: string;
      evidence_refs: QueryEvidence[];
    }>;
  }>;
  missing_evidence: string[];
  suggested_source_actions: string[];
  generation_metadata?: GenerationMetadata;
};
```

## 验收

- 无 sources 时 Research 返回 no_sources，不硬答。
- sources 存在但问题未覆盖时返回 insufficient_evidence，不硬答。
- 补源后返回 research_available=true。
- supported_conclusions 至少 1 条。
- supported_conclusions 每条至少 1 个 evidence_ref。
- evidence_ref 包含 source_id + unit_id + evidence_id。
- evidence_ref 可解析 DocumentUnit 和 EvidenceSpan。
- missing_evidence 可为空，但字段必须存在。
- conflicts 可为空，但字段必须存在。
- response 不含 raw path / cache path / artifact physical path。
- 前端 Research 失败只显示局部状态，不清空 answer / guide / studio。

## 禁止

- 不自动联网搜索。
- 不把 provider 常识当作来源。
- 不生成无 evidence 的 Research 结论。
- 不把 Research 写成互联网通用问答。
- 不声明 all-domain ready。
- 不声明 conflict analysis 全量准确 ready。

## 风险评估

开发计划漂移风险：MEDIUM。

虚假验收风险：MEDIUM。

收敛措施：

- 只声明 PASS_LIMITED_CONTRACT_SMOKE。
- 不声明 Research quality ready。
- 不把 empty conflicts 当作完整冲突分析能力。
- 最终人工质量检查放入 V1.6-RC。
