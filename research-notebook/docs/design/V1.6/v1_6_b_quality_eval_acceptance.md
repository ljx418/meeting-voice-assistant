# ResearchNotebook V1.6-B Quality Evaluation Acceptance

日期：2026-05-28

## 验收状态

- PASS：自动 smoke 和人工质量评分均通过。
- CANDIDATE_READY_FOR_MANUAL_REVIEW：自动 smoke 通过，但人工评分未完成。
- NOT_READY：自动 smoke 不通过或质量评分不达标。
- BLOCKED：provider、真实数据或 source import 阻塞。

## 自动 smoke 验收

每个数据集：

1. workspace create PASS。
2. source import PASS。
3. build PASS。
4. Guide schema PASS。
5. Guide evidence_refs PASS。
6. 覆盖型 QA evidence_refs PASS。
7. 资料外拒答 PASS。
8. Studio artifact evidence_refs PASS。
9. citation route resolution PASS。
10. cleanup PASS。

## 人工评分验收

每个数据集必须填写评分表：

- 资料相关性：1 到 5。
- 覆盖完整性：1 到 5。
- citation 正确性：百分比。
- 拒答正确性：百分比。
- 中文表达：1 到 5。
- 高危幻觉数量。
- 审核人。
- 审核时间。
- 结论：PASS / FAIL。

## 阈值

- Guide 可用性 >= 4/5。
- 每个数据集 QA citation 正确率 >= 80%。
- 每个数据集拒答正确率 >= 80%。
- 每个数据集 citation 可定位率 >= 90%。
- 高危幻觉 = 0。

## 停止规则

以下任一情况必须停止：

- 缺少人工评分却声明 PASS。
- 自动 smoke 失败。
- 出现高危幻觉。
- citation route 可解析但语义不支持结论。
- 把 3 个数据集结论扩大为 all-domain ready。
