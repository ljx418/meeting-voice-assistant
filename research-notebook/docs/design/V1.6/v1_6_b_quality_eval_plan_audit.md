# ResearchNotebook V1.6-B Quality Evaluation Plan Audit

日期：2026-05-28

## 审计结论

Conditional Go for automatic candidate evaluation。

用户已确认采用“先实现自动评估 harness，最终阶段再人工修整”的路径。因此允许继续实现 V1.6-B 自动候选评估和人工评分模板，但不得独立声明 V1.6-B PASS。原因是 V1.6-B 的核心是输出质量评估，自动化无法替代人工语义审查。

## 审计意见

| 编号 | 意见 | 风险 | 处理 |
| --- | --- | --- | --- |
| B1 | 多数据集自动 smoke 不能证明 citation 语义正确。 | HIGH | 必须加入人工评分表；无人工评分只能 CANDIDATE_READY_FOR_MANUAL_REVIEW。 |
| B2 | 3 个主题数据集不能证明 all-domain ready。 | MEDIUM | 所有声明使用 PASS_LIMITED。 |
| B3 | 资料外拒答需要人工判断是否真的没有资料覆盖。 | HIGH | 人工评分必须包含拒答正确性。 |
| B4 | provider 输出可能看似合理但引入资料外硬结论。 | HIGH | 人工评分必须记录高危幻觉数量，阈值为 0。 |

## 风险评估

开发计划漂移风险：MEDIUM。

虚假验收风险：MEDIUM，前提是结果只标记为 `CANDIDATE_READY_FOR_MANUAL_REVIEW`。

是否允许继续自动开发：YES，限定为候选评估 harness。

## 执行决定

根据用户确认，继续执行 V1.6-B 自动候选评估。

阶段边界：

- 可以生成候选输出、fixtures、自动结构评分和人工评分模板。
- 只能声明 `CANDIDATE_READY_FOR_MANUAL_REVIEW`。
- 不得声明 PASS / quality ready / all-domain ready。
- 人工评分放到 V1.6-RC 或用户指定的最后阶段闭环。
