# V2.4 Audio Overview Plan Audit

日期：2026-06-02

## 审计结论

**当前状态**：待审计

## 审计检查表

### 规格漂移风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| 不声明 all languages ready | ✅ | 计划明确限制为"受限 MVP" |
| 不声明 full production ready | ✅ | 计划只做 limited path |
| TTS provider gate 决策正确 | ⏳ | 需要确认 TTS provider 可用性 |
| script evidence binding 覆盖 | ⏳ | 需要确认 AudioSegment.evidence_refs 结构 |
| Audio 不生成伪音频 | ⏳ | 需要确认 fallback 行为 |

### 虚假验收风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| TTS provider 可用性测试 | ⏳ | health probe 是否充分 |
| script evidence binding 测试 | ⏳ | 如何验证每个 segment 有 evidence_refs |
| 音频内容人工质量审查 | ⏳ | 审查标准是否明确 |
| provider 不可用时 fallback | ⏳ | 如何显示错误而不是生成伪音频 |

### 实现风险评估

| 检查项 | 状态 | 说明 |
| --- | --- | --- |
| TTS provider 可用性 | ⏳ | 需要确认是否有可用 TTS provider |
| Audio artifact schema 与后端对齐 | ⏳ | AudioArtifact 结构需要确认 |
| 前端 Audio player UI 实现 | ⏳ | 需要新增 AudioPlayer 组件 |
| Audio script 生成依赖 Guide/QA | ⏳ | 是否有现成的 script 生成逻辑 |

## 审计结论

**规格漂移风险**：MEDIUM
- TTS provider gate 是关键决策点

**虚假验收风险**：MEDIUM
- 音频内容质量审查标准需要明确
- evidence binding 验证方法需要确定

**实现风险**：HIGH
- 无 TTS provider 时不应进入实现
- Audio Overview 依赖 script generation 能力

**是否可以进入实现**：需要确认

### 关键决策点

V2.4 的核心是 TTS provider gate。若无 TTS provider：
- 保持 `AUDIO_OVERVIEW_DECISION_RECORDED`
- 不进入实现阶段

若有 TTS provider：
- 进入 Audio Overview 实现
- 需要与后端对齐 audio artifact schema

### 前置确认事项

- [ ] 确认是否有可用的 TTS provider
- [ ] 若有 provider，确认 Audio artifact schema（script、duration、voice_metadata）
- [ ] 若有 provider，确认 script generation 依赖关系
- [ ] 确认人工质量审查标准（无资料外硬答）

若没有 TTS provider，审计通过但停留在 DECISION_RECORDED。
若有 provider，需要进一步审计实现计划。