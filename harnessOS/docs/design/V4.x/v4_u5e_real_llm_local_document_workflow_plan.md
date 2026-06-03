# V4-U5E Real LLM Local Document Workflow Plan

文档状态：待实现阶段计划。

允许完成声明：

```text
V4-U5E complete: real LLM-backed local technical document workflow ready for dev/local validation.
```

禁止完成声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
production filesystem permission ready
```

## 1. 目标

V4 完成后，本地知识工作流必须可以真实启动，并能解析用户授权的本地技术文档目录。

最低目标场景：

```text
用户输入：
帮我创建并运行一个工作流，读取 Desktop/技术分享，递归解析 Markdown 技术文档，为每个子文件夹生成总结，最后生成总览总结。
```

系统必须：

```text
显式请求本地文件夹读取授权。
递归扫描真实或等价 fixture 目录。
解析 .md / .markdown 文件。
优先调用 MiniMax provider 生成总结；也允许明确配置的 OpenAI-compatible provider。
输出每个子文件夹总结、总览总结、质量报告和证据链。
```

## 1.1 LLM Provider And Dotenv

V4-U5E 的默认真实 LLM provider 为 MiniMax。密钥只允许通过 dotenv 加载的本地环境变量提供，用户在本地 `.env` 或 `.env.local` 中填写，仓库只提交 `.env.example` 占位。

建议本地配置：

```text
LLM_PROVIDER=minimax
MINIMAX_API_KEY=<user-filled-local-key>
MINIMAX_BASE_URL=https://api.minimax.chat/v1
V4_U5E_LLM_PROVIDER=minimax
V4_U5E_LLM_MODEL=MiniMax-M2.1
V4_U5E_REAL_LLM_REQUIRED=true
```

规则：

```text
不得提交真实 MINIMAX_API_KEY。
测试和 Evidence 只能记录 provider/model/ref，不能记录 API key。
没有 MINIMAX_API_KEY 或等价 provider key 时，UX-12 必须 BLOCKED 或 fallback_demo_only。
fallback_demo_only 不得作为 real_llm PASS。
```

## 2. 实现范围

```text
LocalFolderReadAuthorization DTO。
Markdown scanner / parser。
Real LLM Station Runtime adapter。
MiniMax-first LLM provider profile resolution。
dotenv / .env.local provider configuration loading。
Per-folder summary station。
Overview summary station。
Quality check station。
Artifact publishing to dev/local artifact store。
Runtime Report / Evidence Chain 更新。
```

LLM 调用必须记录：

```text
provider
model_ref
provider_config_source
prompt_template_ref
input_artifact_refs
output_artifact_refs
redaction_status
token/raw payload redaction result
runtime_result_ref
correlation_id
```

## 3. 边界

```text
这是 dev/local 真实 LLM 文档工作流，不是 Agent executor。
Agent 仍不能 auto apply / publish / run / rerun。
本地文件读取必须 user_confirmed。
不支持 production filesystem permission model。
不支持 PDF / DOCX / PPTX，除非后续阶段单独扩展。
不把 raw file content 暴露到 DOM、network log、error response 或 Evidence Chain。
```

## 4. 验收

```text
用户确认后工作流真实启动。
实际读取 Desktop/技术分享 或等价 fixture。
Markdown 文件被递归解析。
每个子文件夹生成一份 LLM-backed 总结。
生成总览总结。
quality_report.json 记录 unsupported 文件和空文件夹。
Evidence Chain 记录 provider/model/ref，而不泄露 raw prompt 或 raw content。
MiniMax provider 调用证据存在，或明确记录使用的 OpenAI-compatible provider。
如果没有 MINIMAX_API_KEY 或等价 LLM key，测试必须标记 BLOCKED 或 fallback_demo_only，不能写成 real_llm PASS。
```

## 5. 停止条件

```text
需要 production auth。
需要 production filesystem permission。
需要 Agent executor。
LLM raw prompt 或 raw document content 泄露。
没有真实 LLM key 却把结果标成 real_llm。
Spec Drift Risk = HIGH。
False Green Risk = HIGH。
```
