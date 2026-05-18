# V2.2 MCP Adapter Research

文档状态：research-only；V2.1 不实现 MCP。

## Question

`pet-mcp` 是否应该进入后续版本？

建议：可以进入 V2.2 或更后版本，但前提是 V2.1 先完成真实 Codex / Claude Code / third-party agent smoke。MCP 不能绕过当前 HTTP bridge 的 token、schema、白名单、rate limit 和 diagnostics 边界。

## Candidate Tools

| Tool | Purpose | Notes |
| --- | --- | --- |
| `pet_notify` | 写入 PetEvent intent。 | 必须复用 `pet-protocol`，并通过本地 HTTP API 入站。 |
| `pet_get_capabilities` | 读取 levels/actions/sounds/hardware capabilities。 | 不需要返回 token 或敏感路径。 |
| `pet_get_state` | 读取只读 runtime/diagnostics summary。 | 不返回原始 payload、metadata 全量、message 全文或声音路径。 |

## Smoke Criteria For Future MCP Ready

- `packages/pet-mcp` 已实现并有自动测试。
- Codex MCP smoke 通过。
- Claude Code MCP smoke 通过。
- diagnostics 能区分 MCP 来源，且不能由外部 payload 自由伪造 transport。
- MCP 工具失败时有明确错误，不无限重试。

## Forbidden For V2.1

- 不创建 `packages/pet-mcp`。
- 不声明 `MCP ready`。
- 不把 MCP 写成当前已实现能力。
- 不引入 USB、Windows ready、3D 或照片自定义。

