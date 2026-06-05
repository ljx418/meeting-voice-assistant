# V9 No False Green Claim Guard

文档状态：V9 No False Green guard / planning baseline。

## 1. Allowed Claim Pattern

V9 阶段完成声明必须使用：

```text
ready for review
slice ready for review
pilot ready for review
gate ready for review
```

不得把 `ready for review` 摘要成 `ready`。

## 2. Forbidden English Claims

```text
production ready
full production GA
Agent executor ready
controlled executor ready
production controlled executor ready
full multi-Agent orchestration ready
distributed multi-Agent runtime ready
autonomous coding workflow ready
autonomous workflow editing ready
complete Workflow Studio ready
unrestricted terminal worker ready
production terminal automation ready
production browser automation ready
GA ready
production automation ready
```

## 3. Forbidden Chinese Claims

```text
生产可用
全面生产可用
Agent执行器已完成
受控执行器已完成
生产级受控执行器已完成
完整多Agent编排已完成
自主代码工作流已完成
自主工作流编辑已完成
完整工作流工作台已完成
无限制终端worker已完成
生产终端自动化已完成
生产浏览器自动化已完成
生产就绪
可投产
正式发布
生产级可用
多智能体编排已完成
Agent Executor 已完成
生产自动化已完成
```

## 4. Allowed Contexts

Forbidden terms may appear only in:

```text
Forbidden Claims
No False Green
Stop Conditions
Out Of Scope
Audit Questions
Drawio warning boxes
Boundary explanations
```

They must not appear as positive completion claims, status summaries, allowed claims or release notes.

## 5. Redaction Terms

V9 evidence must not contain:

```text
raw_prompt
raw prompt
raw_file_content
raw file content
raw_provider_payload
raw_connector_payload
raw_artifact_content
API key
Bearer
signed URL
credential raw secret
```

## 6. Suggested Scan

```text
rg -in "production[- ]?ready|full production GA|GA ready|Agent executor ready|controlled executor ready|production controlled executor ready|full multi-Agent orchestration ready|distributed multi-Agent runtime ready|autonomous coding workflow ready|autonomous workflow editing ready|complete Workflow Studio ready|unrestricted terminal worker ready|production terminal automation ready|production browser automation ready|production automation ready|生产可用|全面生产可用|生产就绪|可投产|正式发布|生产级可用|Agent执行器已完成|Agent Executor 已完成|受控执行器已完成|生产级受控执行器已完成|完整多Agent编排已完成|多智能体编排已完成|自主代码工作流已完成|自主工作流编辑已完成|完整工作流工作台已完成|无限制终端worker已完成|生产终端自动化已完成|生产浏览器自动化已完成|生产自动化已完成" docs/design/V9.x
```

Expected result: hits only in forbidden/no-false-green/audit contexts.
