<template>
  <div class="summary-panel">
    <h3>会议总结</h3>

    <!-- 文件上传分析区域 -->
    <div class="analyze-section">
      <div class="analyze-header">
        <span class="analyze-title">📊 智能分析</span>
        <button
          class="btn-upload-file"
          :disabled="isAnalyzing"
          @click="openFilePicker"
        >
          {{ isAnalyzing ? '分析中...' : '上传文本文件' }}
        </button>
      </div>
      <input
        ref="fileInput"
        type="file"
        accept=".txt,.text,.log"
        @change="handleFileSelect"
        hidden
      />
      <div class="analyze-hint">
        支持 .txt, .text, .log 格式的转写文本文件
      </div>
      <div v-if="uploadProgress > 0" class="upload-progress">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${uploadProgress}%` }"></div>
        </div>
        <span class="progress-text">{{ uploadProgress }}%</span>
      </div>
    </div>

    <!-- 分析结果区域 -->
    <div v-if="hasAnalysisResult" class="summary-content">

      <!-- 会议主题（一句话概括） -->
      <div v-if="analysisResult?.theme" class="summary-section">
        <h4 class="section-title">
          <span class="icon">📌</span>
          会议主题
        </h4>
        <p class="theme-text">{{ analysisResult.theme }}</p>
      </div>

      <!-- 会议主题标签 -->
      <div v-if="analysisResult?.topics?.length" class="summary-section">
        <h4 class="section-title">
          <span class="icon">🏷️</span>
          主题标签
        </h4>
        <div class="topic-tags">
          <span
            v-for="(topic, index) in analysisResult.topics"
            :key="index"
            class="topic-tag"
          >
            {{ topic }}
          </span>
        </div>
      </div>

      <!-- 会议章节 -->
      <div v-if="chapterList.length" class="summary-section">
        <h4 class="section-title">
          <span class="icon">📚</span>
          会议章节
        </h4>
        <div class="chapters-list">
          <div
            v-for="(chapter, index) in chapterList"
            :key="chapter.id || index"
            class="chapter-item"
          >
            <span class="chapter-time">{{ chapter.start_time || '' }}</span>
            <span class="chapter-title">{{ chapter.title || chapter.章节名称 }}</span>
          </div>
        </div>
      </div>

      <!-- 发言人员角色识别 -->
      <div v-if="speakerRoles.length" class="summary-section">
        <h4 class="section-title">
          <span class="icon">👥</span>
          发言人员角色
        </h4>
        <div class="speakers-list">
          <div
            v-for="sr in speakerRoles"
            :key="sr.speaker"
            class="speaker-item"
          >
            <span class="speaker-badge" :style="{ backgroundColor: getSpeakerColor(sr.speaker) }">
              {{ getSpeakerLabel(sr.speaker) }}
            </span>
            <div class="speaker-info">
              <span class="speaker-role">{{ sr.role }}</span>
              <span v-if="sr.reasoning" class="speaker-reasoning">{{ sr.reasoning }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 会议摘要 -->
      <div v-if="analysisResult?.summary" class="summary-section">
        <h4 class="section-title">
          <span class="icon">📝</span>
          会议摘要
        </h4>
        <p class="summary-text">{{ analysisResult.summary }}</p>
      </div>

      <!-- 关键要点 -->
      <div v-if="analysisResult?.key_points?.length" class="summary-section">
        <h4 class="section-title">
          <span class="icon">⭐</span>
          关键要点
        </h4>
        <ul class="key-points-list">
          <li v-for="(point, index) in analysisResult.key_points" :key="index">
            {{ point }}
          </li>
        </ul>
      </div>

      <!-- 行动项 -->
      <div v-if="analysisResult?.action_items?.length" class="summary-section">
        <h4 class="section-title">
          <span class="icon">✅</span>
          行动项
        </h4>
        <ul class="action-items-list">
          <li v-for="(item, index) in analysisResult.action_items" :key="index">
            <span class="checkbox"></span>
            {{ item }}
          </li>
        </ul>
      </div>

    </div>

    <!-- 无分析结果时的基础信息 -->
    <div v-else-if="speakers.length" class="basic-info">
      <p class="basic-hint">暂无深度分析结果</p>
      <p class="basic-hint-sub">在上方文本框粘贴转写文本，点击「开始分析」</p>
      <div class="summary-section">
        <h4 class="section-title">
          <span class="icon">👥</span>
          发言人员
        </h4>
        <div class="speakers-list">
          <div
            v-for="speaker in speakers"
            :key="speaker.id"
            class="speaker-item"
          >
            <span class="speaker-badge" :style="{ backgroundColor: speaker.color }">
              {{ speaker.label }}
            </span>
            <span class="speaker-count">{{ speaker.count }} 次发言</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 初始状态 -->
    <div v-else class="empty-state">
      <p>暂无数据</p>
      <p class="hint">上传音频文件或粘贴转写文本进行深度分析</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { AnalysisResult, Chapter, TranscriptSegment, SpeakerRole } from '../api/types'
import { API_CONFIG } from '../api/config'

const props = defineProps<{
  analysisResult?: AnalysisResult
  chapters?: Chapter[]
  transcripts?: TranscriptSegment[]
}>()

const emit = defineEmits<{
  (e: 'analysis-result', result: AnalysisResult): void
}>()

// Speaker colors
const speakerColors = [
  '#4CAF50', // Green
  '#2196F3', // Blue
  '#FF9800', // Orange
  '#E91E63', // Pink
  '#9C27B0', // Purple
  '#00BCD4', // Cyan
  '#795548', // Brown
  '#607D8B', // Blue Grey
]

// 分析相关状态
const fileInput = ref<HTMLInputElement | null>(null)
const isAnalyzing = ref(false)
const uploadProgress = ref(0)

// 是否有分析结果
const hasAnalysisResult = computed(() => {
  return props.analysisResult?.theme ||
    props.analysisResult?.summary ||
    props.analysisResult?.topics?.length ||
    props.analysisResult?.key_points?.length ||
    props.analysisResult?.action_items?.length ||
    props.analysisResult?.speaker_roles?.length ||
    props.analysisResult?.chapters?.length
})

// Extract unique speakers from transcripts
const speakers = computed(() => {
  if (!props.transcripts) return []

  const speakerMap = new Map<string, { id: string; count: number; color: string; label: string }>()

  for (const seg of props.transcripts) {
    if (seg.speaker && seg.speaker !== 'file') {
      if (!speakerMap.has(seg.speaker)) {
        const index = speakerMap.size
        let label = seg.speaker
        if (seg.speaker.startsWith('speaker_')) {
          const idx = parseInt(seg.speaker.split('_')[1])
          label = String.fromCharCode(65 + idx) // A, B, C, ...
        }
        speakerMap.set(seg.speaker, {
          id: seg.speaker,
          count: 1,
          color: speakerColors[index % speakerColors.length],
          label
        })
      } else {
        speakerMap.get(seg.speaker)!.count++
      }
    }
  }

  return Array.from(speakerMap.values())
})

// 发言人员角色（来自 LLM 分析）
const speakerRoles = computed((): SpeakerRole[] => {
  return props.analysisResult?.speaker_roles || []
})

// 获取章节列表（优先使用 analysis 中的，备用 store 的）
const chapterList = computed(() => {
  if (props.analysisResult?.chapters?.length) {
    return props.analysisResult.chapters
  }
  return props.chapters || []
})

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 获取说话人标签
function getSpeakerLabel(speakerId: string): string {
  if (speakerId.startsWith('speaker_')) {
    const idx = parseInt(speakerId.split('_')[1])
    return String.fromCharCode(65 + idx)
  }
  return speakerId
}

// 获取说话人颜色
function getSpeakerColor(speakerId: string): string {
  if (speakerId.startsWith('speaker_')) {
    const idx = parseInt(speakerId.split('_')[1])
    return speakerColors[idx % speakerColors.length]
  }
  return speakerColors[0]
}

// 打开文件选择器
function openFilePicker() {
  fileInput.value?.click()
}

// 处理文件选择
async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    await uploadTextFile(file)
  }
}

// 上传文本文件
async function uploadTextFile(file: File) {
  isAnalyzing.value = true
  uploadProgress.value = 0

  try {
    const text = await file.text()
    console.log('[SummaryPanel] File loaded, text length:', text.length)

    // 调用分析接口，添加 AbortController 超时
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 120000) // 2分钟超时

    const response = await fetch(API_CONFIG.analyzeUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        session_id: `file_${Date.now()}`,
      }),
      signal: controller.signal,
    })

    clearTimeout(timeoutId)
    console.log('[SummaryPanel] Response status:', response.status)
    uploadProgress.value = 50

    if (response.ok) {
      const result = await response.json()
      console.log('[SummaryPanel] Analysis result:', result)

      if (result.success) {
        const analysisResult: AnalysisResult = {
          summary: result.summary || '',
          key_points: result.key_points || [],
          action_items: result.action_items || [],
          topics: result.topics || [],
          theme: result.theme,
          chapters: result.chapters || [],
          speaker_roles: result.speaker_roles || [],
        }
        console.log('[SummaryPanel] Emitting analysis-result:', analysisResult)
        uploadProgress.value = 100
        emit('analysis-result', analysisResult)
      }
    } else {
      const errorText = await response.text()
      console.error('Analysis failed:', response.status, errorText)
    }
  } catch (error) {
    console.error('Analysis error:', error)
  } finally {
    isAnalyzing.value = false
    // 延迟清空进度，让用户看到完成状态
    setTimeout(() => {
      uploadProgress.value = 0
    }, 2000)
    // 清空文件输入
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}
</script>

<style scoped>
.summary-panel {
  display: flex;
  flex-direction: column;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  overflow: hidden;
  height: 100%;
}

h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: #333;
  border-bottom: 2px solid #1976d2;
  padding-bottom: 0.5rem;
}

/* 分析输入区域 */
.analyze-section {
  margin-bottom: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 0.75rem;
  background: #fafafa;
}

.analyze-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.analyze-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #333;
}

.btn-upload-file {
  padding: 0.4rem 0.85rem;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
}

.btn-upload-file:hover:not(:disabled) {
  background: #1565c0;
}

.btn-upload-file:disabled {
  background: #999;
  cursor: not-allowed;
}

.analyze-hint {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #999;
}

.upload-progress {
  margin-top: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4caf50;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: #666;
  min-width: 35px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  text-align: center;
}

.empty-state .hint {
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.basic-info {
  padding: 1rem 0;
}

.basic-hint {
  color: #999;
  font-size: 0.9rem;
  margin: 0 0 0.25rem 0;
}

.basic-hint-sub {
  color: #bbb;
  font-size: 0.8rem;
  margin: 0 0 1rem 0;
}

.summary-content {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.summary-section {
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.summary-section:last-child {
  border-bottom: none;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
  color: #333;
  font-weight: 600;
}

.icon {
  font-size: 1rem;
}

.summary-text {
  margin: 0;
  color: #666;
  line-height: 1.6;
  white-space: pre-wrap;
}

.theme-text {
  margin: 0;
  color: #333;
  line-height: 1.6;
  font-size: 0.95rem;
  font-weight: 500;
}

.speaker-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
}

.speaker-role {
  font-size: 0.85rem;
  color: #333;
  font-weight: 500;
}

.speaker-reasoning {
  font-size: 0.75rem;
  color: #999;
  line-height: 1.4;
}

.topic-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.topic-tag {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 500;
}

.chapters-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.chapter-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: #f5f5f5;
  border-radius: 4px;
}

.chapter-time {
  font-size: 0.75rem;
  color: #999;
  flex-shrink: 0;
}

.chapter-title {
  font-size: 0.85rem;
  color: #333;
}

.speakers-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.speaker-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: #f5f5f5;
  border-radius: 4px;
}

.speaker-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 24px;
  padding: 0 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.speaker-count {
  font-size: 0.8rem;
  color: #666;
}

.key-points-list {
  margin: 0;
  padding-left: 1.25rem;
  color: #666;
  line-height: 1.8;
}

.key-points-list li {
  margin-bottom: 0.5rem;
}

.action-items-list {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.action-items-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  color: #666;
  line-height: 1.5;
}

.checkbox {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #4caf50;
  border-radius: 3px;
  flex-shrink: 0;
  margin-top: 2px;
}
</style>
