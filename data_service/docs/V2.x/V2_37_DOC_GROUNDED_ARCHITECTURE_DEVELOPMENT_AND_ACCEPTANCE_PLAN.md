# V2.37 开发及验收计划

## 1. 阶段划分

| Phase | 名称 | 目标 |
| --- | --- | --- |
| 103 | Document Authority Registry v2 | 建立 docs 权威索引 |
| 104 | Architecture Claim Graph v2 | 抽取架构声明与关系 |
| 105 | Current Implementation Model | 汇总代码当前实现模型 |
| 106 | Claim-to-Code Verification | 双边证据核查 |
| 107 | Reconstruction Report + Agent Brief | 可读报告与 Agent 架构 brief |
| 108 | Closure Acceptance | 真实项目 E2E 与收口审计 |

## 2. 共享开发规则

- 每个 Phase 开始前必须有 pre-implementation audit。
- 每个 Phase 完成后必须有 acceptance audit、PRD/spec review、false-green review。
- 使用真实仓库验收：data_service、HarnessOS、codexPat；若 research-notebook 可用则作为第四样例。
- 不允许 mock-only acceptance。
- 不允许 HarnessOS-only hardcode。
- 所有 accepted verification 必须有 document evidence + code evidence。
- HTML/Mermaid 不得展示源码块，不得引入未持久化事实。

## 3. Phase 103：Document Authority Registry v2

开发内容：

- 文档发现与分类。
- authority_role / authority_level / phase_hint / version_hint。
- stale、historical、superseded、current 判断。
- 文档来源 evidence。

验收：

- data_service/HarnessOS/codexPat 均生成非空 registry。
- V2.37 docs 识别为 current target。
- 历史 V2.x docs 不得误判为当前 authority。
- HarnessOS design docs 能被登记并区分 target/gap/audit/evidence。

## 4. Phase 104：Architecture Claim Graph v2

开发内容：

- Markdown heading/bullet/table/acceptance/non-goal 抽取。
- drawio node/edge 抽取。
- claim relation 构建。
- term taxonomy 初始生成。

验收：

- 每个 claim 有 doc_id、source block、line range 或 drawio cell id。
- non-goal / forbidden claim 一等抽取。
- drawio claim 默认不高置信，除非有文本证据补强。
- HarnessOS workflow/runtime/agent/adaptor 类 claim 可被抽出，但不得直接标 code-supported。

## 5. Phase 105：Current Implementation Model

开发内容：

- 消费 V2.0-V2.36 artifacts。
- 汇总 surfaces、symbols、relationships、tests、configs、task navigation、blockers。
- 建立 current architecture node/edge。

验收：

- 不重写上游 artifacts。
- current model 中 accepted code fact 有 repo-relative evidence。
- 无 public surface 项目仍可生成 current model，并保留 blocker。
- data_service/HarnessOS/codexPat 均生成 current model。

## 6. Phase 106：Claim-to-Code Verification

开发内容：

- claim-to-code match。
- code-to-doc coverage。
- contradiction / unsupported / weak support 检测。
- verification matrix 和 drift findings。

验收：

- supported 必须有 document evidence + code evidence。
- token overlap only 只能 weakly_supported 或 needs_review。
- HarnessOS 至少 10 条架构 claim 被分类。
- code_not_documented 不得缺席。
- contradicted 结论必须有双边证据，否则降级 needs_review。

## 7. Phase 107：Reconstruction Report + Agent Brief

开发内容：

- target/current/diff/needs_review HTML。
- Mermaid/SVG 原位渲染。
- Agent architecture brief。
- token budget 与 evidence floor。

验收：

- HTML 不展示 Mermaid 源码。
- 图中每个节点可回溯 persisted artifact。
- 每条 recommendation 有 evidence 或 needs_review。
- 小 token budget 下不得保留无证据建议。
- 人类可在页面看到目标架构、当前实现、差异、阻塞原因。

## 8. Phase 108：Closure Acceptance

开发内容：

- 全量 coverage matrix。
- real repo E2E matrix。
- final audit report。
- 文档审计和规格检视。

验收：

- data_service、HarnessOS、codexPat E2E 通过。
- 全量 backend tests 通过。
- 无 open fatal/major。
- 无 HarnessOS-only rule。
- 不声称 full design intent recovery。

## 9. Stop Conditions

出现以下情况必须停止并回到计划/审计：

- 需要把 document-only claim 写成 code fact。
- 需要把 token overlap 写成 accepted proof。
- 需要写 HarnessOS 专用路径或类名规则。
- accepted row 缺 document evidence 或 code evidence。
- HTML 图与 persisted model 不一致。
- 目标项目代码或 docs 被静默改写。
