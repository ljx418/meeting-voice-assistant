# V2.4 Audio Overview

日期：2026-06-02

## 阶段目标

实现 PRD Phase 2 Audio Overview 的受限 MVP。

**约束**：不声明 all languages ready，不声明 full production ready。

## 阶段 Entry Gate

- [ ] V2.3 OCR 通过验收（Audio 可能需要 OCR 处理扫描 PDF）
- [ ] 当前分支无未合并的 V2.3 功能变更
- [ ] TTS provider 可用性确认

## 子阶段

### V2.4-A Audio Artifact Contract

**目标**：定义 Audio artifact 数据结构。

**API Contract**：
```typescript
// 创建 Audio artifact
POST /api/workspaces/{workspace_id}/artifacts/audio
Request: {
  source_ids: string[]
  language?: string
  voice_id?: string  // 可选，默认使用 provider 默认 voice
}
Response: {
  artifact: AudioArtifact
}

// Audio artifact 结构
interface AudioArtifact {
  artifact_id: string
  workspace_id: string
  type: "audio_overview"
  status: "generating" | "ready" | "error"
  script: AudioSegment[]
  citations: EvidenceRef[]
  duration_seconds: number
  voice_metadata: {
    provider: string
    voice_id: string
    language: string
  }
  created_at: string
  error?: {
    code: string
    message: string
  }
}

interface AudioSegment {
  text: string
  start_time: number   // 秒
  end_time: number
  evidence_refs?: EvidenceRef[]
}
```

### V2.4-B Source-grounded Script Generation

**目标**：Audio script 基于 sources 生成。

**Script Generation Contract**：
```
POST /api/workspaces/{workspace_id}/artifacts/audio/generate
Request: {
  source_ids: string[]
  topic?: string  // 可选，指定生成主题
}
Response: {
  artifact_id: string,
  status: "generating"
}

// 获取生成状态
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}/status
Response: {
  artifact_id: string,
  status: "generating" | "ready" | "error",
  progress?: number  // 0-100
}
```

**约束**：
- script 每个关键段落带 evidence_refs
- 不基于外部知识硬答
- 若 sources 不足，拒绝生成并返回：
```typescript
{
  error: {
    code: "INSUFFICIENT_SOURCES",
    message: "资料不足，无法生成 Audio Overview。请先添加更多 sources。"
  }
}
```

### V2.4-C TTS Provider Gate

**目标**：验证 TTS provider 可用。

**Health Check**：
```typescript
POST /api/tts/provider/health
Response: {
  available: boolean,
  provider: string,  // "azure" | "google" | "elevenlabs" | etc
  voices: string[],    // 可用 voice ID 列表
  default_voice: string
}
```

**约束**：
- provider 不可用时不生成伪音频
- 显示明确错误："语音生成暂时不可用，请稍后重试"
- 不使用 provider 外部默认音频

### V2.4-D Audio Preview / Download UI

**目标**：Audio 可播放和下载。

**UI 组件**：
```typescript
// AudioPlayer 组件
interface AudioPlayerProps {
  artifact: AudioArtifact
  onPlay?: () => void
  onPause?: () => void
  onSeek?: (time: number) => void
}

// 显示内容
- 播放/暂停按钮
- 进度条（可拖拽）
- 当前时间 / 总时长
- 播放速度选择（0.75x, 1x, 1.25x, 1.5x）
- 音量控制
```

**Download 功能**：
```typescript
// 下载 Audio
GET /api/workspaces/{workspace_id}/artifacts/{artifact_id}/download
Response: {
  url: string,  // 临时 signed URL
  format: "mp3" | "wav",
  size_bytes: number
}
```

**CitationMetadata 组件**：
- 显示当前播放段的 evidence_refs
- 点击跳转到 SourcePreview

**验收**：
- [ ] 音频可播放（播放/暂停/进度条）
- [ ] 音频可下载（mp3/wav）
- [ ] citation metadata 可查看
- [ ] evidence_refs 绑定正确

### V2.4-RC Audio Manual Review

**目标**：人工确认音频内容质量。

**人工审查检查项**：
- [ ] script 每个关键段落带 evidence_refs
- [ ] provider 不可用时不生成伪音频（显示错误消息）
- [ ] 音频可播放和下载
- [ ] citation metadata 可查看
- [ ] 人工确认内容没有资料外硬答

**质量标准**：
- 音频内容与 script 一致
- 无明显拼接痕迹
- evidence_refs 对应的 source 确实包含相关内容

## 风险评估

| 风险 | 等级 | 缓解策略 |
| --- | --- | --- |
| TTS provider 不可用 | HIGH | Phase 1 先验证 provider |
| script 生成质量不达标 | MEDIUM | 设置 evidence_refs 覆盖率阈值 |
| 音频文件生成失败 | MEDIUM | 添加 error handling 和重试 |

## 实现顺序

### Phase 1: TTS Provider Gate（1天）
1. 调用 TTS provider health API
2. 确认 provider 可用性
3. 若不可用，记录 DECISION_RECORDED，结束

### Phase 2: Audio Artifact Schema 对齐（1-2天）
1. 与后端对齐 AudioArtifact schema
2. 确认 script/segment 结构
3. 确认 voice_metadata

### Phase 3: 前端 Audio UI（1-2天）
1. AudioPlayer 组件
2. Download 功能
3. CitationMetadata 组件

### Phase 4: Smoke + Manual Review（1天）
1. 运行 Audio smoke 测试
2. 人工质量审查
3. 更新报告

## 出门状态

- `AUDIO_OVERVIEW_PASS_LIMITED`

## 仍不声明

- all languages ready
- all voices ready
- full production ready

## 下一步

V2.4 通过后进入 V2.5 PPT Generation。