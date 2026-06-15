# V2.37 Real Repo E2E Acceptance Matrix

## 1. 真实项目

| 项目 | 角色 | 最低验收 |
| --- | --- | --- |
| data_service | 本项目自举 | target/current/diff/report/brief 全链路 |
| HarnessOS | workflow/runtime/agent 大项目样例 | docs 目标架构重塑 + 代码事实核查 |
| codexPat | desktop/app/package 项目样例 | 非 HTTP/MCP 项目不硬失败，输出 current model 与 blocker |
| research-notebook | 可选样例 | 若路径存在，验证非代码资产文档与后端 artifacts |

## 2. data_service E2E

验收：

- V2.37 docs 被识别为 current target。
- 旧 V2.x docs 被识别为 historical/supporting。
- target model 包含 Project Intelligence / code assets / MCP/HTTP/CLI / governance。
- current model 消费已有 code facts。
- 至少 20 条 verification row。
- HTML 原位渲染图。

## 3. HarnessOS E2E

验收：

- 从 docs/design 中抽取 workflow/runtime/agent/adapter/artifact/governance claims。
- 生成 target architecture model。
- 从代码 facts 中生成 current implementation model。
- 至少 10 条 claim 完成 supported / weakly_supported / unsupported 分类。
- 若 public surface 仍缺失，必须保留 blocker，不伪造 HTTP/MCP/CLI。
- 不允许 HarnessOS-only hardcode。

## 4. codexPat E2E

验收：

- 能处理 desktop/app/package 结构。
- docs-heavy 项目不会被误判为 code-supported。
- current model 至少包含 apps/packages/config/tests/docs 层事实。
- unsupported / code_not_documented 可见。

## 5. False-Green Rejection

以下情况不得通过：

- 只跑 mock repo。
- 只生成目录枚举图。
- drawio 节点被当成 code fact。
- supported claim 缺 document evidence 或 code evidence。
- token overlap only 被标 supported。
- HarnessOS 专用规则通过测试。
- HTML 展示 Mermaid 源码而不是渲染图。
- 目标项目被静默修改。
