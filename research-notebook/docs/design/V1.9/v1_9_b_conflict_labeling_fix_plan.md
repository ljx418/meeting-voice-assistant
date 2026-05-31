# V1.9-B Conflict Labeling Fix Plan

日期：2026-05-31

## 目标

修复 V1.9-B 的唯一阻塞：真实冲突样本已经进入 `supported_conclusions`，但 `conflicts` 为空。

目标不是实现通用自然语言冲突推理，而是把 PRD 要求的“同一问题存在不同来源结论时，显式列出分歧与各自证据”在 approved dataset 上闭环。

## 修复策略

1. 优先修复 data_service Research contract。
2. 保持 source-grounded，不使用外部互联网或 provider 常识。
3. 从 supported conclusions 中识别同主题相反立场。
4. 将分歧写入 structured `conflicts`。
5. 每个 position 保留原 evidence refs。
6. ResearchNotebook 前端只消费后端返回的 `conflicts`，不伪造冲突。

## 最低合同

```ts
type ResearchConflict = {
  topic: string;
  positions: Array<{
    claim: string;
    evidence_refs: AnswerEvidence[];
  }>;
};
```

当前 V1.9-B approved sample 必须生成：

- topic：`数字人项目 Alpha 2026 年规模化商业化状态`
- position 1：Alpha 已经实现规模化商业化
- position 2：Alpha 尚未实现规模化商业化

## 验收标准

执行：

```bash
npm run smoke:v1.9-conflict-labeling
```

必须满足：

- target route probe PASS
- workspace create PASS
- conflict source import PASS
- Research report returned PASS
- `conflicts.length >= 1`
- `conflicts[0].positions.length >= 2`
- 每个 position 至少有一个 evidence ref
- 至少一个 evidence ref 可解析到 DocumentUnit / EvidenceSpan
- cleanup PASS
- final decision 为 `PASS_LIMITED`

后端 focused tests：

```bash
python3 -m pytest tests/test_target_http_research.py -q
```

必须覆盖：

- Alpha 乐观与保守口径生成 structured conflict。
- 非冲突资料不误报 conflict。
- conflict evidence refs 可解析。
- response 不暴露 raw path / cache path / artifact physical path。

## 执行结果

状态：`PASS_LIMITED`

已执行：

```bash
python3 -m pytest tests/test_target_http_research.py -q
npm run smoke:v1.9-conflict-labeling
```

结果：

- 后端 focused tests：4 passed
- V1.9-B smoke：PASS_LIMITED
- conflict positions：2
- evidence resolution：PASS

## 风险评估

| 风险项 | 评级 | 收敛措施 |
| --- | --- | --- |
| 规格漂移 | MEDIUM | 仅声明 approved dataset PASS_LIMITED |
| 虚假验收 | MEDIUM | 保留人工语义审查要求 |
| 误报冲突 | LOW | 增加 non-conflicting backend test |

## 后续

进入 V1.9-RC aggregation re-smoke。
