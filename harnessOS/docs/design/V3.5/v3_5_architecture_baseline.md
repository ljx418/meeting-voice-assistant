# V3.5 Architecture Baseline

文档状态：V3.5 architecture baseline。  
配套图：`diagrams/01_v3_5_application_adaptation_layer_baseline.drawio`。

## 1. Architecture Position

V3.5 的架构位置是 **Application Adaptation Layer**：

```text
Product UI / External Business App
  -> V3.5 Application Adaptation Layer
      SDK
      BFF template
      TypeScript SDK core client
      React hooks
      Event bridge
      Pack / Connector templates
      Embed contract
  -> harnessOS Protocol App Server
  -> harnessOS Core
```

V3.5 不改变 Core 主合同，而是把业务 App 接入所需的客户端、BFF、安全、事件和模板层补齐。

## 2. Frontend Access Modes

V3.5 支持两种前端接入模式：

```text
Production recommended:
  Business UI -> BFF -> harnessOS

Dev/direct:
  Business UI -> TypeScript SDK -> harnessOS
```

生产默认路径应通过 BFF 绑定业务身份、scope 和 capability token。浏览器不应长期持有广权限 capability token。Dev/direct 只用于本地开发、受限 capability token 或显式 dev mode。

## 3. Adaptation Layer Responsibilities

| 组件 | 职责 | 不负责 |
| --- | --- | --- |
| Protocol Schema Registry | 为 SDK/BFF/Event bridge 提供 method/event/error schema。 | 不改变业务 handler 语义。 |
| Capability Token | 为外部 App 提供 local token、scope、origin、capability 约束。 | 不实现云端 IAM。 |
| Event Bridge | 提供浏览器友好的 native EventSource、fetch stream 和 replay cursor。 | 不替代 Core event/job/trace storage。 |
| Python SDK | 为 backend/BFF 提供 typed JSON-RPC client、scope helper、error handling。 | 不直接访问 Core store。 |
| TypeScript SDK | 为 browser/Node 提供 typed client 和 EventSource helper。 | 不暴露 legacy/debug API 作为默认模板。 |
| React Hooks | 为 Product UI 提供 session、turn、events、artifacts、jobs、approvals hooks。 | 不实现业务 UI 终局。 |
| BFF Template | 绑定 app scope、token、CORS、RPC proxy、EventSource proxy，示范业务 identity 到 harnessOS scope/capability token 的映射。 | 不实现完整用户系统，不绕过 GatewayService。 |
| Pack / Connector Template | 生成 app pack 和 connector descriptor skeleton。 | 不改变 PackRegistry/ConnectorRegistry 主合同。 |
| Embed Contract | 定义未来嵌入式 Agent 面板所需 bootstrap 和 event union。 | 不实现完整 AgentTalkWindow。 |

## 4. Boundary Rules

- 所有外部 App 请求必须显式绑定 scope。
- SDK/BFF 必须通过 JSON-RPC、HTTP 或 stdio 入口调用 harnessOS。
- 生产推荐路径是 Business UI -> BFF -> harnessOS。
- 浏览器直连 harnessOS 仅限 dev/direct 或严格受限 token 场景。
- Event bridge 必须保留原始 event id / cursor，不能生成无法追踪的新孤儿事件。
- Native EventSource 不能依赖 Authorization header，必须使用 same-origin BFF cookie 或 short-lived signed subscription URL。
- Fetch stream 可以使用 `Authorization: Bearer`，但必须校验 scope 和 capability。
- Capability token 必须绑定 scope、origin 和 capabilities。
- SDK/BFF 默认面必须排除 legacy/debug API。
- SDK default export 必须保持 thin client，不得包含业务 workflow wrapper。
- Pack / Connector template 必须证明不改 Core 即可被 registry 发现。

## 5. Exit Architecture

V3.5 完成后，一个外部业务 App 的标准接入路径应是：

```text
Business UI
  -> React hooks / TypeScript SDK
  -> BFF template
  -> capability token + scope binding
  -> harnessOS JSON-RPC / native EventSource / fetch stream
  -> Core job / artifact / approval / trace
```

该路径不要求修改 Core，也不依赖任何业务专用 legacy RPC。
