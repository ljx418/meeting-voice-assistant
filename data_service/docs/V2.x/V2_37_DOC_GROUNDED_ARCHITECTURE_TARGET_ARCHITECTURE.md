# V2.37 目标架构：文档驱动架构重塑与事实核查

## 1. 目标状态

V2.37 在既有 V2 项目智能 artifacts 上增加一层“文档驱动架构理解层”：

```text
项目 docs
  PRD / target architecture / gap / drawio / audit / acceptance
        |
        v
Document Authority Registry v2
        |
        v
Architecture Claim Graph v2
        |
        +-------------------------------+
        |                               |
        v                               v
Target Architecture Model          Project Term Taxonomy
        |
        v
Claim-to-Code Verification <--- Current Implementation Model
        |                                ^
        |                                |
        v                                |
Architecture Reconstruction Report v2    V2.0-V2.36 code facts
        |
        v
HTML / Mermaid / Agent Architecture Brief / HTTP-MCP-CLI
```

## 2. 架构原则

- 文档声明与代码事实分离：document claim 不是 code fact。
- 双边证据：supported claim 必须有 document evidence + code evidence。
- 低置信显式化：weakly_supported、unsupported、contradicted 必须可见。
- 项目无关：HarnessOS 只作为样例，不作为硬编码逻辑来源。
- 词表可配置：项目词汇通过 taxonomy/alias 映射到通用架构类型。
- 不过度承诺：不声称完整设计意图恢复、full call graph、runtime topology。
- 报告可读：HTML 原位渲染图，不展示 Mermaid 源码。

## 3. 当前架构与目标架构差异

| 维度 | 当前状态 | V2.37 目标 |
| --- | --- | --- |
| 架构图 | 偏目录/数量枚举 | target/current/diff/needs_review 四视图 |
| 文档理解 | 有 V2.7 claim extraction 基线 | authority ranking + claim graph + term taxonomy |
| 代码事实 | V2.0-V2.36 facts 可用 | 汇总成 current implementation model |
| 核查 | 部分 doc-code alignment | claim-to-code verification matrix |
| HarnessOS | 可以扫描但 public surface 缺失 | 从 docs 重塑 workflow/runtime/agent target model，再核查代码事实 |
| Agent 上下文 | task reading pack | architecture brief with constraints and evidence |
| 风险呈现 | blocker 可见 | blocker + drift + unsupported/contradicted claim 可见 |

## 4. 模块设计

### 4.1 Document Authority Registry v2

职责：

- 扫描 docs 文件。
- 识别文档类型、阶段、版本、权威角色。
- 判断 stale/superseded/historical/current。

建议模块：

```text
backend/data_service/code_assets/architecture_docs/
  authority_registry.py
  document_classifier.py
  version_resolver.py
```

### 4.2 Architecture Claim Graph v2

职责：

- 从 Markdown/drawio/table/list/non-goal/acceptance gate 抽 claim。
- 生成 claim node 和 relation edge。
- 保留 source block、line range、drawio cell id。

建议模块：

```text
architecture_docs/
  claim_extractor.py
  drawio_parser.py
  relation_builder.py
```

### 4.3 Project Term Taxonomy

职责：

- 把项目术语映射到通用架构类型。
- 支持配置和自动建议，但自动建议只能 needs_review。

示例：

```json
{
  "station": "agent_role",
  "mission": "workflow",
  "runtime_adapter": "adapter",
  "orchestration": "runtime"
}
```

### 4.4 Current Implementation Model

职责：

- 消费 V2.0-V2.36 artifacts。
- 汇总 code facts 为 module/entrypoint/surface/relationship/test/config/artifact 模型。
- 不重写上游 artifacts。

### 4.5 Claim-to-Code Verification

职责：

- 将 claim graph 与 current model 对齐。
- 输出 verification row。
- 保留 match_strategy、confidence、document_evidence、code_evidence。

状态：

```text
supported
weakly_supported
unsupported
contradicted
code_not_documented
needs_review
```

### 4.6 Reconstruction Report v2

职责：

- 生成 JSON model。
- 生成 HTML。
- 生成 Mermaid/SVG。
- 图必须来自 persisted model，不得 renderer 自造事实。

视图：

```text
Target from Docs
Current from Code
Diff / Drift
Needs Review
```

### 4.7 Agent Architecture Brief

职责：

- 生成面向 coding_agent / architecture_reviewer / maintainer 的架构上下文。
- 支持 token budget。
- 保留 constraints、risk、recommended next steps。

## 5. Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/architecture/doc_grounded/
  authority_registry.json
  documents.jsonl
  claims.jsonl
  claim_relations.jsonl
  term_taxonomy.json
  target_architecture_model.json
  current_implementation_model.json
  verification_matrix.jsonl
  drift_findings.jsonl
  architecture_reconstruction_report.json
  views/
    architecture_reconstruction_report.html
    target_current_diff.mmd
    target_current_diff.svg
  agent_briefs/
    {brief_id}.json
    {brief_id}.md
```

## 6. Public Contracts

HTTP：

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/report
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/verification
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/doc-grounded/brief
```

MCP：

```text
knowledge_code_doc_grounded_architecture_build
knowledge_code_doc_grounded_architecture_report
knowledge_code_doc_grounded_verification
knowledge_code_doc_grounded_architecture_brief
```

CLI：

```text
knowledge code architecture doc-grounded build
knowledge code architecture doc-grounded report
knowledge code architecture doc-grounded verification
knowledge code architecture doc-grounded brief
```

## 7. 架构门禁

- 不修改 `backend/app/api/v1/data_service.py`。
- 不修改 `backend/data_service/service.py`。
- 不把 V2.37 逻辑塞进已有巨型模块。
- 不改写 V2.0-V2.36 artifacts。
- 不改写目标项目 docs/code。
- 不输出绝对路径。
- 不把 document-only claim 作为 code-supported fact。
- 不把 token overlap 作为 accepted proof。
