# V1.0 Roadmap Boundary

V1.0 之后的工作必须保持 V1.0 安全边界和低打扰体验。

## 推荐下一阶段

Phase 9：Agent Integration Adapters

目标：

- 降低真实 Agent 接入成本。
- 增加 Codex / Claude Code / custom script 的 instruction layer 和示例。
- 所有接入仍通过 `petctl` 或 localhost HTTP 写入 PetEvent。

范围：

- `skills/codex-agent-pet/SKILL.md`
- `skills/claude-agent-pet/SKILL.md`
- `docs/agent-integration-guide.md`
- `docs/petctl-recipes.md`
- shell / Node 示例

明确不做：

- MCP server。
- USB。
- Windows。
- 自动更新。
- 正式签名发布。

## 后续跨平台阶段

Phase 8 / 8A / 8B：Windows readiness and smoke

当前 macOS 环境不支持直接验收 Windows 透明窗口、托盘、置顶、WebView2 和 Defender 行为。因此 Windows 必须在真实 Windows 环境中完成。

完成前不得声明：

```text
Windows ready
cross-platform ready
```

## 后续能力池

- MCP server adapter。
- Codex / Claude Code Skill 完整包。
- USB serial ambient light。
- Rive / Live2D / 3D cat renderer。
- Cat pack manifest。
- 照片辅助自定义外观。
- 自动更新。
- 正式签名发布。

这些能力均不能绕过 V1.0 的协议和安全边界。
