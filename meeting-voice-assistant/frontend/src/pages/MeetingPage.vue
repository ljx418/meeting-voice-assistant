<template>
  <div class="upload-page">
    <!-- Header -->
    <header class="page-header">
      <h1 class="page-title">会议音频上传</h1>
    </header>

    <!-- Main Content -->
    <main class="page-content">
      <div class="content-wrapper">
        <!-- Meeting Title Section -->
        <div class="title-section">
          <label class="section-label">会议总标题</label>
          <div class="title-input-wrapper">
            <input
              v-if="!meetingTitle"
              type="text"
              class="title-input"
              placeholder="请输入会议总标题"
              v-model="meetingTitleInput"
            />
            <div v-else class="title-display">
              {{ meetingTitle }}
            </div>
          </div>
        </div>

        <!-- Processing Status Card (shown when any file exists) -->
        <div v-if="hasAnyFile" class="processing-section">
          <div class="processing-header">
            <div class="processing-info">
              <span class="processing-file">{{ processingFileName }}</span>
              <span class="processing-stage" :class="debugStore.stage">
                {{ getStageLabel(debugStore.stage) }}
              </span>
            </div>
            <div class="processing-progress">
              <span>{{ debugStore.progress }}%</span>
              <button
                v-if="debugStore.stage !== 'completed'"
                class="btn-cancel-processing"
                @click="cancelProcessing"
                title="取消并删除"
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M11 3L3 11M3 3L11 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                取消
              </button>
              <button
                v-else
                class="btn-cancel-processing btn-reset"
                @click="cancelProcessing"
                title="重新上传"
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M11 3L3 11M3 3L11 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                删除
              </button>
            </div>
          </div>

          <!-- Process Flow Chart -->
          <div class="flow-chart-wrapper">
            <!-- 计时器显示 -->
            <div v-if="totalStartedAt && debugStore.stage !== 'completed'" class="upload-timer">
              <span class="timer-icon">⏱</span>
              <span class="timer-value">{{ formatDuration(totalElapsedSeconds) }}</span>
              <span class="timer-label">已耗时</span>
            </div>
            <ProcessFlowChart
              :steps="steps"
              :current-step-id="currentStepId"
              title="处理流程"
            />
          </div>

          <!-- Progress Bar -->
          <div class="progress-bar-container">
            <div class="progress-bar" :style="{ width: debugStore.progress + '%' }"></div>
          </div>

          <!-- Stats Row -->
          <div class="stats-row">
            <div class="stat-item">
              <span class="stat-label">说话人</span>
              <span class="stat-value">{{ debugStore.speakerCount || '-' }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">片段数</span>
              <span class="stat-value">{{ debugStore.segmentCount || '-' }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">预计剩余</span>
              <span class="stat-value">{{ estimatedRemainingTime !== null ? formatTime(estimatedRemainingTime) : '-' }}</span>
            </div>
            <div class="stat-item flex-1">
              <span class="stat-label">状态</span>
              <span class="stat-value">{{ debugStore.message || '等待中...' }}</span>
            </div>
          </div>

          <!-- Quick Results (shown when completed) -->
          <div v-if="debugStore.stage === 'completed' && debugStore.analysisResult" class="quick-results">
            <div class="result-theme">
              <span class="result-label">主题</span>
              <span class="result-value">{{ debugStore.analysisResult.theme || '-' }}</span>
            </div>
            <div class="result-chapters">
              <span class="result-label">章节</span>
              <span class="result-value">{{ debugStore.analysisResult.chapters?.length || 0 }} 个</span>
            </div>
          </div>

          <!-- Tabs for Details -->
          <div v-if="debugStore.stage === 'completed'" class="detail-tabs">
            <button
              v-for="tab in detailTabs"
              :key="tab.id"
              class="tab-btn"
              :class="{ active: activeDetailTab === tab.id }"
              @click="activeDetailTab = tab.id"
            >
              {{ tab.label }}
              <span class="tab-count" v-if="tab.count !== undefined">{{ tab.count }}</span>
            </button>
          </div>

          <!-- Transcript Preview -->
          <div v-if="debugStore.stage === 'completed' && activeDetailTab === 'transcript'" class="detail-content">
            <div v-if="debugStore.transcriptResult" class="segment-list">
              <div v-for="(seg, idx) in debugStore.transcriptResult.segments?.slice(0, 20)" :key="idx" class="segment-item">
                <span class="seg-time">[{{ formatTime(seg.start_time) }}]</span>
                <span class="seg-speaker">{{ seg.speaker }}</span>
                <span class="seg-text">{{ seg.text }}</span>
              </div>
              <div v-if="(debugStore.transcriptResult.segments?.length || 0) > 20" class="more-hint">
                还有 {{ debugStore.transcriptResult.segments.length - 20 }} 个片段...
              </div>
            </div>
            <div v-else class="empty-hint">暂无转写数据</div>
          </div>

          <!-- Analysis Preview -->
          <div v-if="debugStore.stage === 'completed' && activeDetailTab === 'analysis'" class="detail-content">
            <div v-if="debugStore.analysisResult" class="chapter-list">
              <div v-for="chapter in (debugStore.analysisResult.chapters || []).slice(0, 5)" :key="chapter.id" class="chapter-item">
                <div class="chapter-header">
                  <span class="chapter-title">{{ chapter.title }}</span>
                  <span class="chapter-time">[{{ formatTime(chapter.start_time) }} - {{ formatTime(chapter.end_time) }}]</span>
                </div>
                <div class="chapter-summary">{{ chapter.summary }}</div>
              </div>
            </div>
            <div v-else class="empty-hint">暂无分析数据</div>
          </div>
        </div>

        <!-- Upload Area (shown when no files) -->
        <div v-else-if="uploadedFiles.length === 0" class="upload-section">
          <div
            class="upload-area"
            :class="{ 'drag-over': isDragOver }"
            @dragover.prevent="isDragOver = true"
            @dragleave="isDragOver = false"
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <div class="upload-icon">
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                <path d="M20 10V25M20 10L13 17M20 10L27 17" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M8 30V34C8 35.1046 8.89543 36 10 36H30C31.1046 36 32 35.1046 32 34V30" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <h3 class="upload-title">上传会议音频</h3>
            <p class="upload-hint">拖拽文件到此处，或点击选择文件</p>
            <p class="upload-formats">支持 MP3、WAV、M4A 格式，最大 500MB</p>
            <button class="btn-select" type="button">选择文件</button>
          </div>

          <div class="demo-section">
            <p class="demo-hint">想快速体验功能？</p>
            <button class="btn-demo" @click="useDemoAudio">
              使用示例音频体验
            </button>
          </div>
        </div>

        <!-- Uploaded Files List (shown when files exist and not processing) -->
        <div v-else class="files-section">
          <h3 class="files-heading">已添加音频 ({{ uploadedFiles.length }})</h3>

          <div class="files-list">
            <div
              v-for="file in uploadedFiles"
              :key="file.id"
              class="audio-card"
              :class="{ selected: selectedFileId === file.id }"
              @click="selectFile(file.id)"
            >
              <div class="card-content">
                <div class="file-icon">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M4 4V16H16V7L11 2H4Z" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M11 2V5H14" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
                <div class="file-info">
                  <div class="file-row">
                    <span class="file-name">{{ file.name }}</span>
                    <span class="file-size">{{ file.size }}</span>
                  </div>
                  <div class="topic-row">
                    <span class="topic-name">{{ file.topic || '未分类' }}</span>
                  </div>
                  <div class="status-row">
                    <span class="status-text" :class="file.status">
                      {{ file.status === 'completed' ? '已完成' : file.status === 'error' ? '失败' : getStageLabelShort(file.stage || 'uploading') }}
                    </span>
                    <span class="duration">{{ file.duration || '--:--' }}</span>
                    <span v-if="file.status === 'processing' && file.progress !== undefined" class="progress-pct">{{ file.progress }}%</span>
                  </div>
                  <!-- Per-file progress bar (shown when processing) -->
                  <div v-if="file.status === 'processing'" class="file-progress-bar">
                    <div class="file-progress-fill" :style="{ width: (file.progress || 0) + '%' }"></div>
                  </div>
                  <!-- Stage message (shown when processing) -->
                  <div v-if="file.status === 'processing' && file.message" class="stage-message">
                    {{ file.message }}
                  </div>
                </div>
                <!-- Enter console button for completed files -->
                <button
                  v-if="file.status === 'completed' && file.sessionId && selectedFileId === file.id"
                  class="btn-enter-file-console"
                  @click="enterFileConsole(file)"
                  title="进入此文件的控制台"
                >
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M5 2L10 7L5 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  进入控制台
                </button>
                <button class="btn-delete" @click="removeFile(file.id)">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.33" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div class="add-more">
            <button
              v-if="uploadedFiles.length < 5"
              class="btn-add-more"
              @click="triggerFileInput"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 3V13M3 8H13" stroke="currentColor" stroke-width="1.33" stroke-linecap="round"/>
              </svg>
              继续添加音频
            </button>
            <div v-else class="add-more-limit">
              最多支持 5 个文件
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Bar (shown when files exist) -->
      <div v-if="uploadedFiles.length > 0" class="bottom-bar">
        <div class="bottom-status">
          <span class="status-text">{{ completedCount }} / {{ uploadedFiles.length }} 个音频已完成</span>
        </div>
        <button class="btn-enter-console" @click="enterConsole">
          进入会议控制台
        </button>
      </div>
    </main>

    <!-- Hidden file input -->
    <input
      ref="fileInputRef"
      type="file"
      accept=".mp3,.wav,.m4a,audio/*"
      multiple
      hidden
      @change="handleFileSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMeetingStore, type Chapter } from '../stores/meeting'
import { useDebugStore } from '../stores/debug'
import { API_CONFIG } from '../api/config'
import ProcessFlowChart from '../components/ProcessFlowChart.vue'
import { useProcessFlow } from '../composables/useProcessFlow'

// 上传响应类型
interface UploadResponse {
  session_id?: string
  segments?: Array<{ text: string; speaker: string; start_time: number; end_time: number }>
  chapters?: Chapter[]
  theme?: string
  topics?: string[]
  speaker_roles?: Array<{ speaker: string; role: string; reasoning: string }>
  summary?: string
  key_points?: string[]
  action_items?: string[]
  audio_url?: string
}

const router = useRouter()
const store = useMeetingStore()
const debugStore = useDebugStore()

// Process flow tracking
const { steps, currentStepId, updateFromStage, reset: resetFlow } = useProcessFlow({ flowId: 'main' })

// Track stage start time for ETA estimation
const stageStartedAt = ref<number | null>(null)
const totalStartedAt = ref<number | null>(null)
const totalTick = ref(0)  // 用于触发计时器更新
const typicalStageDurations: Record<string, number> = {
  uploading: 30,
  transcribing: 120,
  analyzing: 60,
}

// 计时器更新 (每秒触发)
let totalTimer: number | null = null
onMounted(() => {
  totalTimer = window.setInterval(() => {
    if (totalStartedAt.value) {
      totalTick.value++
    }
  }, 1000)
})
onUnmounted(() => {
  if (totalTimer) clearInterval(totalTimer)
})

// 计算总耗时
const totalElapsedSeconds = computed(() => {
  totalTick.value // 依赖 tick 以触发更新
  if (!totalStartedAt.value) return 0
  return Math.floor((Date.now() - totalStartedAt.value) / 1000)
})

// 格式化时间 (MM:SS)
function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// Watch debugStore.stage to update flow and track stage timing
watch(() => debugStore.stage, (newStage, oldStage) => {
  console.log(`[MeetingPage] debugStore.stage watch: ${oldStage} -> ${newStage}`)
  if (newStage !== oldStage) {
    stageStartedAt.value = Date.now()
  }
  if (newStage && newStage !== 'idle') {
    console.log(`[MeetingPage] calling updateFromStage(${newStage})`)
    updateFromStage(newStage)
    console.log(`[MeetingPage] after updateFromStage, steps:`, steps.value.map(s => `${s.id}:${s.status}`))
  }
}, { immediate: true })

// Computed estimated remaining time (uses backend value or estimates locally)
const estimatedRemainingTime = computed(() => {
  if (debugStore.remainingTime !== null && debugStore.remainingTime > 0) {
    return debugStore.remainingTime
  }
  const stage = debugStore.stage
  if (!stageStartedAt.value || stage === 'idle' || stage === 'completed' || stage === 'error') {
    return null
  }
  const typical = typicalStageDurations[stage]
  if (!typical) return null
  const progress = debugStore.progress / 100
  if (progress <= 0) return typical
  const elapsed = (Date.now() - stageStartedAt.value) / 1000
  return Math.max(0, Math.round(elapsed / progress - elapsed))
})

// GraphRAG API URL
const GRAPHRAG_API_URL = import.meta.env.VITE_GRAPHRAG_API_URL || 'http://localhost:8002'

// File input ref
const fileInputRef = ref<HTMLInputElement | null>(null)

// State
const meetingTitleInput = ref('')
const meetingTitle = computed(() => meetingTitleInput.value)
const isDragOver = ref(false)
const activeDetailTab = ref('transcript')

const uploadedFiles = computed(() => store.uploadedFiles)
const selectedFileId = ref<string | null>(null)

const completedCount = computed(() =>
  uploadedFiles.value.filter(f => f.status === 'completed').length
)

// Check if any file is processing
const hasProcessingFile = computed(() =>
  store.uploadedFiles.some(f => f.status === 'processing')
)

// Check if any file exists (for showing flow chart persistently)
const hasAnyFile = computed(() =>
  store.uploadedFiles.length > 0
)

const processingFileName = computed(() => {
  // Show the first processing file, or the first completed file
  const processingFile = store.uploadedFiles.find(f => f.status === 'processing')
  const completedFile = store.uploadedFiles.find(f => f.status === 'completed')
  const file = processingFile || completedFile
  return file?.name || '处理中'
})

const detailTabs = computed(() => [
  { id: 'transcript', label: '转写', count: debugStore.transcriptResult?.segments?.length },
  { id: 'analysis', label: '分析', count: debugStore.analysisResult?.chapters?.length }
])

function getStageLabel(stage: string): string {
  const labels: Record<string, string> = {
    idle: '等待',
    uploading: '正在上传音频...',
    transcribing: '正在识别语音...',
    analyzing: '正在深度分析...',
    completed: '处理完成',
    error: '处理失败'
  }
  return labels[stage] || stage
}

function getStageLabelShort(stage: string): string {
  const labels: Record<string, string> = {
    idle: '等待',
    uploading: '上传中',
    transcribing: '识别中',
    analyzing: '分析中',
    completed: '已完成',
    error: '失败'
  }
  return labels[stage] || stage
}

function formatTime(seconds: number | null): string {
  if (seconds === null || seconds === undefined) return '-'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// Active XHR map: fileId → XHR (for cancellation)
const activeXHRs = new Map<string, XMLHttpRequest>()

// SSE Polling map: fileId → abort controller
const pollControllers = new Map<string, AbortController>()

async function startFilePolling(fileId: string, sessionId: string) {
  stopFilePolling(fileId)

  const controller = new AbortController()
  pollControllers.set(fileId, controller)
  const pollStartTime = Date.now()

  console.log(`[MeetingPage] SSE polling started`, { fileId, sessionId, url: API_CONFIG.uploadSSEUrl(sessionId) })

  try {
    const response = await fetch(API_CONFIG.uploadSSEUrl(sessionId), {
      headers: {
        'Accept': 'text/event-stream',
      },
      signal: controller.signal,
    })

    if (!response.ok) {
      console.warn(`[MeetingPage] SSE poll HTTP failed: ${response.status} ${response.statusText}`, { fileId, sessionId })
      return
    }

    if (!response.body) {
      console.error('[MeetingPage] SSE response body is null', { fileId, sessionId })
      return
    }

    console.log(`[MeetingPage] SSE stream connected, reading...`, { fileId, sessionId })

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()

        if (done || controller.signal.aborted) {
          break
        }

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // Keep incomplete line in buffer

        for (const line of lines) {
          const trimmed = line.trim()
          if (!trimmed) continue

          // Parse SSE format: "data: {...}"
          if (trimmed.startsWith('data: ')) {
            const jsonStr = trimmed.slice(6)
            try {
              const data = JSON.parse(jsonStr)

              console.log(`[MeetingPage] SSE stage: ${data.stage} | progress: ${data.progress}% | message: ${data.message}`, {
                sessionId,
                remainingTime: data.remaining_time_seconds,
                speakerCount: data.speaker_count,
                segmentCount: data.segment_count
              })

              // Update per-file progress in store
              store.updateUploadedFile(fileId, {
                progress: data.progress,
                stage: data.stage,
                message: data.message,
              })
              store.setSessionData(sessionId, {
                progress: data.progress ?? 0,
                stage: data.stage ?? '',
                message: data.message ?? '',
              })
              // Also sync to debugStore for flow chart (last active file)
              console.log(`[MeetingPage] SSE received, calling debugStore.updateFromSSE: stage=${data.stage}`, { sessionId, fileId })
              debugStore.updateFromSSE(data)
              console.log(`[MeetingPage] debugStore.stage is now: ${debugStore.stage}`)

              // Stop on terminal states
              if (data.stage === 'completed' || data.stage === 'error') {
                console.log(`[MeetingPage] SSE stream ended: ${data.stage}`, { sessionId, fileId })
                // 异步模式下，completed 时获取完整结果
                if (data.stage === 'completed') {
                  fetchFullResultAndIndex(sessionId, fileId)
                }
                return
              }
            } catch (e) {
              console.warn('[MeetingPage] Failed to parse SSE data:', jsonStr, e)
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  } catch (e) {
    if ((e as Error).name === 'AbortError') {
      // Expected abort, ignore
    } else {
      console.error('[MeetingPage] Poll error:', e)
    }
  }
}

function stopFilePolling(fileId: string) {
  const controller = pollControllers.get(fileId)
  if (controller) {
    controller.abort()
    pollControllers.delete(fileId)
  }
}

function stopAllPolling() {
  pollControllers.forEach((controller) => controller.abort())
  pollControllers.clear()
}

// Kept for backward compat reference — no longer used directly
let currentXHR: XMLHttpRequest | null = null

// Legacy poll — kept for backward compat reference
let pollInterval: number | null = null
function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}


async function fetchFullResult(sessionId: string) {
  try {
    const response = await fetch(API_CONFIG.uploadSessionUrl(sessionId))
    if (response.ok) {
      const data = await response.json()
      //后端返回 { session_id, segments, chapters, analysis }
      //需要转换为 populateStoresFromResponse 期望的格式
      const transformed = {
        session_id: data.session_id,
        segments: data.segments,
        chapters: data.chapters,
        theme: data.analysis?.theme,
        topics: data.analysis?.topics,
        speaker_roles: data.analysis?.speaker_roles,
        summary: data.analysis?.summary,
        audio_url: `/api/v1/upload/${sessionId}/audio`,
      }
      populateStoresFromResponse(transformed)
      // Also save to session
      saveSessionFromResponse(sessionId, data.session_id || sessionId, '', transformed)
    }
  } catch (e) {
    console.error('[MeetingPage] Fetch result error:', e)
  }
}

// SSE completed 时调用：获取完整结果并索引到 GraphRAG
async function fetchFullResultAndIndex(sessionId: string, fileId: string) {
  try {
    const response = await fetch(API_CONFIG.uploadSessionUrl(sessionId))
    if (response.ok) {
      const data = await response.json()
      const transformed = {
        session_id: data.session_id,
        segments: data.segments,
        chapters: data.chapters,
        theme: data.analysis?.theme,
        topics: data.analysis?.topics,
        speaker_roles: data.analysis?.speaker_roles,
        summary: data.analysis?.summary,
        audio_url: `/api/v1/upload/${sessionId}/audio`,
      }
      populateStoresFromResponse(transformed)
      saveSessionFromResponse(sessionId, fileId, '', transformed)
      // Index to GraphRAG
      indexToGraphRAG(transformed)
      // Mark as completed
      store.updateUploadedFile(fileId, { status: 'completed', progress: 100, stage: 'completed' })
    } else {
      console.error('[MeetingPage] Failed to fetch full result:', response.status)
      store.updateUploadedFile(fileId, { status: 'error', stage: 'error' })
    }
  } catch (e) {
    console.error('[MeetingPage] Fetch result error:', e)
    store.updateUploadedFile(fileId, { status: 'error', stage: 'error' })
  }
}

function populateStoresFromResponse(data: UploadResponse) {
  // Store in debug store (for inline display)
  if (data.segments) {
    const speakerCount = new Set(data.segments.map((s) => s.speaker)).size
    debugStore.setTranscript({
      segments: data.segments,
      speaker_count: speakerCount
    })

    // Also populate meeting store with speakers
    const speakers = Array.from(new Set(data.segments.map((s) => s.speaker))).map((spk: string, idx: number) => ({
      id: spk,
      name: `发言人 ${String.fromCharCode(65 + idx)}`,
      color: ''
    }))
    store.setSpeakers(speakers)
  }

  if (data.chapters) {
    // Store in debug store - construct analysis result
    debugStore.setAnalysis({
      session_id: data.session_id || '',
      theme: data.theme || '',
      topics: data.topics || [],
      chapters: data.chapters,
      speaker_roles: data.speaker_roles || [],
      summary: data.summary || ''
    })

    // Also populate meeting store with chapters
    const chapters: Chapter[] = data.chapters.map((ch, idx: number) => ({
      id: `chapter_${idx}`,
      title: ch.title,
      start_time: ch.start_time,
      end_time: ch.end_time,
      speaker_summaries: ch.speaker_summaries || [],
      summary: ch.summary || '',
      decisions: ch.decisions || [],
      action_items: ch.action_items || []
    }))
    store.setChapters(chapters)

    // Extract decisions and action_items from chapters
    const allDecisions = chapters.flatMap((ch) =>
      (ch.decisions || []).map((d) => ({
        decision: d.decision,
        source_timestamps: d.source_timestamps || []
      }))
    )
    const allActionItems = chapters.flatMap((ch) =>
      (ch.action_items || []).map((a) => ({
        todo: a.todo,
        source_timestamps: a.source_timestamps || []
      }))
    )
    store.setDecisions(allDecisions)
    store.setActionItems(allActionItems)

    // Set topic from analysis
    if (data.theme) {
      store.setTopic(data.theme)
    }

    // Set audio URL for playback
    if (data.audio_url) {
      store.setAudioUrl(data.audio_url)
    }
  }
}

// Convert meeting data to markdown for GraphRAG indexing
function convertMeetingToMarkdown(data: UploadResponse): string {
  const lines: string[] = []

  // Title
  const title = data.theme || store.topic || '会议记录'
  lines.push(`# ${title}`)
  lines.push('')

  // Summary
  if (data.summary) {
    lines.push('## 会议摘要')
    lines.push(data.summary)
    lines.push('')
  }

  // Topics
  if (data.topics && data.topics.length > 0) {
    lines.push('## 主题')
    data.topics.forEach(topic => lines.push(`- ${topic}`))
    lines.push('')
  }

  // Key Points
  if (data.key_points && data.key_points.length > 0) {
    lines.push('## 关键要点')
    data.key_points.forEach(point => lines.push(`- ${point}`))
    lines.push('')
  }

  // Chapters
  if (data.chapters && data.chapters.length > 0) {
    lines.push('## 章节')
    data.chapters.forEach((chapter, idx) => {
      lines.push(`### ${idx + 1}. ${chapter.title}`)
      if (chapter.summary) {
        lines.push(chapter.summary)
      }
      if (chapter.speaker_summaries && chapter.speaker_summaries.length > 0) {
        lines.push('**发言摘要:**')
        chapter.speaker_summaries.forEach((ss: any) => {
          lines.push(`- ${ss.speaker}: ${ss.summary}`)
        })
      }
      if (chapter.decisions && chapter.decisions.length > 0) {
        lines.push('**决策:**')
        chapter.decisions.forEach((d: any) => lines.push(`- ${d.decision}`))
      }
      if (chapter.action_items && chapter.action_items.length > 0) {
        lines.push('**行动项:**')
        chapter.action_items.forEach((a: any) => lines.push(`- ${a.todo}`))
      }
      lines.push('')
    })
  }

  // Action Items (top level)
  if (data.action_items && data.action_items.length > 0) {
    lines.push('## 行动项')
    data.action_items.forEach((item: string) => lines.push(`- ${item}`))
    lines.push('')
  }

  // Transcript
  if (data.segments && data.segments.length > 0) {
    lines.push('## 完整转写')
    data.segments.forEach((seg) => {
      const start = formatTime(seg.start_time)
      const end = formatTime(seg.end_time)
      lines.push(`[${start}-${end}] **${seg.speaker}**: ${seg.text}`)
    })
    lines.push('')
  }

  // Speaker Roles
  if (data.speaker_roles && data.speaker_roles.length > 0) {
    lines.push('## 说话人角色')
    data.speaker_roles.forEach((role: any) => {
      lines.push(`- **${role.speaker}**: ${role.role} - ${role.reasoning}`)
    })
    lines.push('')
  }

  return lines.join('\n')
}

// Index meeting data to GraphRAG
async function indexToGraphRAG(data: UploadResponse) {
  try {
    const markdown = convertMeetingToMarkdown(data)
    const title = data.theme || store.topic || `会议_${Date.now()}`
    const filename = `${title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}.md`

    const formData = new FormData()
    const blob = new Blob([markdown], { type: 'text/markdown' })
    formData.append('doc', blob, filename)

    const response = await fetch(`${GRAPHRAG_API_URL}/api/v1/index/stream`, {
      method: 'POST',
      body: formData,
    })

    if (response.ok) {
      console.log('[MeetingPage] GraphRAG indexing started:', filename)
    } else {
      console.error('[MeetingPage] GraphRAG indexing failed:', response.status)
    }
  } catch (e) {
    console.error('[MeetingPage] GraphRAG indexing error:', e)
  }
}

onUnmounted(() => {
  activeXHRs.forEach(xhr => xhr.abort())
  activeXHRs.clear()
  stopAllPolling()
})

// Methods
function triggerFileInput() {
  fileInputRef.value?.click()
}

function handleDrop(e: DragEvent) {
  isDragOver.value = false
  const files = Array.from(e.dataTransfer?.files || [])
  processFiles(files)
}

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const files = Array.from(input.files || [])
  processFiles(files)
  input.value = ''
}

async function processFiles(files: File[]) {
  if (files.length === 0) return
  // Launch all files in parallel
  await Promise.all(files.map(file => uploadSingleFile(file)))
}

async function uploadSingleFile(file: File) {
  const sizeMB = (file.size / (1024 * 1024)).toFixed(1)
  const fileId = `file_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`
  const tempSessionId = `upload_pending_${fileId}`
  const uploadStartTime = Date.now()

  // 启动总计时器
  if (!totalStartedAt.value) {
    totalStartedAt.value = Date.now()
  }

  console.log(`[MeetingPage] uploadSingleFile started: ${file.name}`, { fileId, sessionId: tempSessionId, fileSize: `${sizeMB}MB` })

  // Initialize session data
  store.setSessionData(tempSessionId, {
    sessionId: tempSessionId,
    fileId,
    fileName: file.name,
    stage: 'uploading',
    progress: 0,
    message: '正在上传音频文件...',
  })

  // Add file to list
  store.addUploadedFile({
    id: fileId,
    name: file.name,
    size: `${sizeMB} MB`,
    topic: meetingTitleInput.value || '会议记录',
    status: 'processing',
    duration: '--:--',
    sessionId: tempSessionId,
    progress: 0,
    stage: 'uploading',
  })

  // Track most recent upload in debugStore (for flow chart)
  debugStore.sessionId = tempSessionId
  debugStore.stage = 'uploading'
  debugStore.progress = 0
  debugStore.message = '正在上传音频文件...'

  const formData = new FormData()
  formData.append('file', file)

  try {
    await new Promise<void>((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      activeXHRs.set(fileId, xhr)
      const xhrStartTime = Date.now()

      console.log(`[MeetingPage] XHR upload started: ${file.name}`, { fileId, sessionId: tempSessionId, fileSize: `${sizeMB}MB` })

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const pct = Math.round((e.loaded / e.total) * 40)
          const elapsed = Date.now() - xhrStartTime
          const msg = `正在上传... ${pct}%`
          console.log(`[MeetingPage] XHR progress: ${pct}%`, { stage: 'uploading', elapsed, loaded: e.loaded, total: e.total })
          store.updateUploadedFile(fileId, { progress: pct, stage: 'uploading', message: msg })
          store.setSessionData(tempSessionId, { progress: pct, stage: 'uploading', message: msg })
          // Sync to debugStore if this is the latest active file
          if (debugStore.sessionId === tempSessionId) {
            debugStore.progress = pct
            debugStore.message = msg
          }
        }
      })

      xhr.timeout = 0 // No timeout for large files

      xhr.addEventListener('load', () => {
        activeXHRs.delete(fileId)
        stopFilePolling(fileId)
        const xhrTotalTime = Date.now() - xhrStartTime
        console.log(`[MeetingPage] XHR load event: status=${xhr.status}, duration=${xhrTotalTime}ms`, { fileId, sessionId: tempSessionId })

        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText)
            const finalSessionId = response.session_id || fileId
            console.log(`[MeetingPage] XHR success (async mode), session_id=${finalSessionId}`, { fileId, response })

            // 异步模式：后端立即返回 session_id，实际处理在后台进行
            // 不再有 immediate result，需要通过 SSE 获取进度和最终结果
            store.updateUploadedFile(fileId, {
              sessionId: finalSessionId,
              progress: 0,
              stage: 'transcribing',
              message: response.message || '正在处理中...',
            })

            // Update debugStore to reflect transcribing state
            debugStore.sessionId = finalSessionId
            debugStore.stage = 'transcribing'
            debugStore.progress = 0
            debugStore.message = response.message || '正在处理中...'

            // Start SSE polling to receive progress updates and final results
            startFilePolling(fileId, finalSessionId)
            resolve()
          } catch (e) {
            console.error('[MeetingPage] XHR response parse error:', e)
            store.updateUploadedFile(fileId, { status: 'error', stage: 'error' })
            store.setSessionData(tempSessionId, { stage: 'error', message: '处理响应失败' })
            reject(e)
          }
        } else {
          console.warn(`[MeetingPage] XHR failed: status=${xhr.status}`, { fileId })
          store.updateUploadedFile(fileId, { status: 'error', stage: 'error', progress: 0 })
          store.setSessionData(tempSessionId, { stage: 'error', message: `上传失败: ${xhr.status}` })
          reject(new Error(`Upload failed: ${xhr.status}`))
        }
      })

      xhr.addEventListener('error', () => {
        activeXHRs.delete(fileId)
        stopFilePolling(fileId)
        store.updateUploadedFile(fileId, { status: 'error', stage: 'error' })
        store.setSessionData(tempSessionId, { stage: 'error', message: '上传失败' })
        reject(new Error('Upload error'))
      })

      xhr.open('POST', API_CONFIG.uploadUrl)
      xhr.send(formData)
    })
  } catch (e) {
    console.error('[MeetingPage] Upload failed:', e)
    store.updateUploadedFile(fileId, { status: 'error' })
  }
}

function saveSessionFromResponse(
  sessionId: string,
  fileId: string,
  fileName: string,
  data: UploadResponse
) {
  console.log(`[MeetingPage] saveSessionFromResponse:`, { sessionId, fileId, dataChapters: data.chapters?.length, hasChapters: !!(data.chapters?.length), data })
  const chapters = (data.chapters || []).map((ch, idx) => ({
    id: `chapter_${idx}`,
    title: ch.title,
    start_time: ch.start_time,
    end_time: ch.end_time,
    speaker_summaries: ch.speaker_summaries || [],
    summary: ch.summary || '',
    decisions: ch.decisions || [],
    action_items: ch.action_items || [],
  }))

  const speakers = Array.from(new Set((data.segments || []).map(s => s.speaker)))
    .map((spk, idx) => ({
      id: spk,
      name: `发言人 ${String.fromCharCode(65 + idx)}`,
      color: ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'][idx % 5],
    }))

  const decisions = chapters.flatMap(ch =>
    (ch.decisions || []).map(d => ({ decision: d.decision, source_timestamps: d.source_timestamps || [] }))
  )
  const actionItems = chapters.flatMap(ch =>
    (ch.action_items || []).map(a => ({ todo: a.todo, source_timestamps: a.source_timestamps || [] }))
  )

  store.setSessionData(sessionId, {
    sessionId,
    fileId,
    fileName,
    progress: 100,
    stage: 'completed',
    message: '处理完成',
    chapters,
    segments: data.segments || [],
    audioUrl: data.audio_url || '',
    theme: data.theme || '',
    topics: data.topics || [],
    speakerRoles: data.speaker_roles || [],
    speakers,
    decisions,
    actionItems,
  })
}

function cancelProcessing() {
  activeXHRs.forEach(xhr => xhr.abort())
  activeXHRs.clear()
  stopAllPolling()
  store.uploadedFiles.slice().forEach(f => store.removeUploadedFile(f.id))
  debugStore.reset()
  resetFlow()
}

function removeFile(id: string) {
  const file = store.uploadedFiles.find(f => f.id === id)
  if (file) {
    // Cancel any active upload
    const xhr = activeXHRs.get(id)
    if (xhr) { xhr.abort(); activeXHRs.delete(id) }
    stopFilePolling(id)
  }
  store.removeUploadedFile(id)
}

function enterFileConsole(file: { id: string; sessionId?: string }) {
  if (file.sessionId) {
    const sessionId = file.sessionId
    const sessionData = store.getSessionData(sessionId)
    if (!sessionData || !sessionData.chapters?.length) {
      // Fetch session data from backend if not available or incomplete
      fetchFullResult(sessionId).then(() => {
        store.setActiveSession(sessionId)
        router.push(`/console/${sessionId}`)
      }).catch(() => {
        store.setActiveSession(sessionId)
        router.push(`/console/${sessionId}`)
      })
    } else {
      store.setActiveSession(sessionId)
      router.push(`/console/${sessionId}`)
    }
  }
}

function selectFile(id: string) {
  selectedFileId.value = id
}

function useDemoAudio() {
  const demoSessionId = `demo_${Date.now()}`
  const demoChapters = [
    { id: 'ch0', title: '用户反馈分析', start_time: 0, end_time: 240, speaker_summaries: [], summary: '分析了用户主要痛点', decisions: [], action_items: [] },
    { id: 'ch1', title: '时间规划讨论', start_time: 240, end_time: 380, speaker_summaries: [], summary: '讨论了项目时间线', decisions: [], action_items: [] },
    { id: 'ch2', title: '实施方案制定', start_time: 380, end_time: 500, speaker_summaries: [], summary: '制定了两阶段方案', decisions: [], action_items: [] },
  ]
  const demoSpeakers = [
    { id: 'spk1', name: '产品经理', color: '#6366f1' },
    { id: 'spk2', name: '技术负责人', color: '#10b981' },
    { id: 'spk3', name: '设计师', color: '#f59e0b' },
  ]
  const demoDecisions = [
    { decision: '决定采用两阶段实施方案', source_timestamps: [{ start: 0, end: 380 }] },
    { decision: '资源分配已确定', source_timestamps: [{ start: 380, end: 500 }] },
  ]
  const demoActionItems = [
    { todo: '王磊：下周三前提交技术方案和工作量评估报告', source_timestamps: [{ start: 450, end: 480 }] },
    { todo: '李娜：协调用户研究团队，补充功能优先级分析', source_timestamps: [{ start: 480, end: 510 }] },
    { todo: '张伟：准备技术方案评审会议', source_timestamps: [{ start: 510, end: 540 }] },
  ]

  store.setSessionData(demoSessionId, {
    sessionId: demoSessionId,
    fileId: 'demo',
    fileName: 'Q2产品路线图讨论会.mp3',
    progress: 100,
    stage: 'completed',
    message: '示例数据加载完成',
    chapters: demoChapters,
    segments: [],
    audioUrl: '',
    theme: meetingTitleInput.value || 'Q2产品路线图讨论会',
    topics: ['产品规划', '资源分配', '用户反馈'],
    speakerRoles: [],
    speakers: demoSpeakers,
    decisions: demoDecisions,
    actionItems: demoActionItems,
  })

  const demoFiles = [
    { name: '用户反馈分析.mp3', size: '12.3 MB', topic: '用户反馈与问题分析', duration: '4:00' },
    { name: '时间规划讨论.mp3', size: '8.7 MB', topic: '时间规划与资源评估', duration: '2:20' },
    { name: '实施方案制定.mp3', size: '9.5 MB', topic: '实施方案与行动计划', duration: '2:00' },
  ]

  for (const demo of demoFiles) {
    store.addUploadedFile({
      id: `demo_${Date.now()}_${Math.random().toString(36).slice(2)}`,
      name: demo.name,
      size: demo.size,
      topic: demo.topic,
      status: 'completed',
      duration: demo.duration,
      sessionId: demoSessionId,
      progress: 100,
      stage: 'completed',
    })
  }

  store.setMeetingId(demoSessionId)
  store.setActiveSession(demoSessionId)

  router.push(`/console/${demoSessionId}`)
}

function enterConsole() {
  // Navigate to the first completed file's console, or generic console
  const completed = store.uploadedFiles.find(f => f.status === 'completed' && f.sessionId)
  console.log(`[MeetingPage] enterConsole:`, { completedSessionId: completed?.sessionId, allCompletedFiles: store.uploadedFiles.filter(f => f.status === 'completed') })
  if (completed?.sessionId) {
    const sessionData = store.getSessionData(completed.sessionId)
    console.log(`[MeetingPage] enterConsole sessionData:`, { sessionId: completed.sessionId, hasData: !!sessionData, chaptersCount: sessionData?.chapters?.length })
    store.setActiveSession(completed.sessionId)
    router.push(`/console/${completed.sessionId}`)
  } else {
    router.push('/console')
  }
}
</script>

<style scoped>
.upload-page {
  min-height: 100vh;
  background: #0d0d15;
  color: #ffffff;
  display: flex;
  flex-direction: column;
}

/* Header */
.page-header {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  background: #1a1a24;
  border-bottom: 1px solid #2d2d3d;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
  color: #ffffff;
  margin: 0;
}

/* Content */
.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 92px;
}

.content-wrapper {
  flex: 1;
  max-width: 896px;
  width: 100%;
  margin: 0 auto;
  padding-top: 16px;
}

/* Title Section */
.title-section {
  background: #1a1a24;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.section-label {
  display: block;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 8px;
}

.title-input-wrapper {
  width: 100%;
}

.title-input {
  width: 100%;
  height: 36px;
  padding: 0 12px;
  background: #262626;
  border: 1px solid #3d3d4d;
  border-radius: 4px;
  color: #ffffff;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.title-input::placeholder {
  color: #a1a1a1;
}

.title-input:focus {
  border-color: #6366f1;
}

.title-display {
  font-size: 16px;
  color: #ffffff;
  padding: 6px 0;
}

/* Processing Section */
.processing-section {
  background: #1a1a24;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}

/* Flow Chart Wrapper */
.flow-chart-wrapper {
  margin-bottom: 16px;
}

/* Upload Timer */
.upload-timer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  color: white;
  font-size: 14px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.upload-timer .timer-icon {
  font-size: 16px;
}

.upload-timer .timer-value {
  font-weight: 600;
  font-size: 18px;
  font-family: 'SF Mono', Monaco, 'Courier New', monospace;
  min-width: 50px;
  text-align: center;
}

.upload-timer .timer-label {
  font-size: 12px;
  opacity: 0.9;
}

.processing-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.processing-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.processing-file {
  font-size: 14px;
  color: #ffffff;
  font-weight: 500;
}

.processing-stage {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.processing-stage.uploading { background: #3b82f6; color: #fff; }
.processing-stage.transcribing { background: #f59e0b; color: #000; }
.processing-stage.analyzing { background: #8b5cf6; color: #fff; }
.processing-stage.completed { background: #22c55e; color: #fff; }
.processing-stage.error { background: #ef4444; color: #fff; }

.processing-progress {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #a1a1a1;
}

/* Progress Bar */
.progress-bar-container {
  height: 4px;
  background: #262626;
  border-radius: 2px;
  margin-bottom: 16px;
}

.progress-bar {
  height: 100%;
  background: #6366f1;
  border-radius: 2px;
  transition: width 0.3s;
}

/* Stats Row */
.stats-row {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-item.flex-1 {
  flex: 1;
}

.stat-label {
  font-size: 11px;
  color: #666;
  text-transform: uppercase;
}

.stat-value {
  font-size: 14px;
  color: #ffffff;
}

/* Quick Results */
.quick-results {
  display: flex;
  gap: 24px;
  padding: 12px;
  background: #141420;
  border-radius: 6px;
  margin-bottom: 16px;
}

.result-theme, .result-chapters {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.result-label {
  font-size: 11px;
  color: #666;
}

.result-value {
  font-size: 13px;
  color: #ffffff;
}

/* Detail Tabs */
.detail-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
}

.tab-btn {
  padding: 6px 12px;
  background: transparent;
  color: #a1a1a1;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  gap: 6px;
  align-items: center;
}

.tab-btn:hover {
  background: #262626;
  color: #ffffff;
}

.tab-btn.active {
  background: #262626;
  color: #6366f1;
}

.tab-count {
  background: #3d3d4d;
  padding: 1px 5px;
  border-radius: 8px;
  font-size: 11px;
}

/* Detail Content */
.detail-content {
  max-height: 300px;
  overflow-y: auto;
}

.segment-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.segment-item {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: #141420;
  border-radius: 4px;
  font-size: 12px;
}

.seg-time {
  color: #6366f1;
  font-family: monospace;
  flex-shrink: 0;
}

.seg-speaker {
  color: #22c55e;
  flex-shrink: 0;
}

.seg-text {
  color: #ffffff;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.more-hint {
  text-align: center;
  padding: 8px;
  color: #666;
  font-size: 12px;
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chapter-item {
  padding: 12px;
  background: #141420;
  border-radius: 6px;
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.chapter-title {
  font-size: 13px;
  font-weight: 500;
  color: #ffffff;
}

.chapter-time {
  font-size: 11px;
  color: #6366f1;
  font-family: monospace;
}

.chapter-summary {
  font-size: 12px;
  color: #a1a1a1;
  line-height: 1.5;
}

.empty-hint {
  text-align: center;
  padding: 24px;
  color: #666;
  font-size: 13px;
}

/* Upload Section */
.upload-section {
  background: #1a1a24;
  border-radius: 8px;
  padding: 40px 16px 24px;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px;
  border: 2px dashed #3d3d4d;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: #6366f1;
  background: rgba(99, 102, 241, 0.05);
}

.upload-icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #6366f1;
  border-radius: 50%;
  margin-bottom: 16px;
}

.upload-title {
  font-size: 18px;
  font-weight: 500;
  color: #ffffff;
  margin: 0 0 12px 0;
}

.upload-hint {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 8px 0;
}

.upload-formats {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0 0 24px 0;
}

.btn-select {
  padding: 8px 24px;
  background: #6366f1;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-select:hover {
  background: #5558e3;
}

/* Demo Section */
.demo-section {
  margin-top: 24px;
  text-align: center;
}

.demo-hint {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 12px 0;
}

.btn-demo {
  width: 100%;
  padding: 10px 24px;
  background: #262626;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-demo:hover {
  background: #3d3d4d;
}

/* Files Section */
.files-section {
  background: #1a1a24;
  border-radius: 8px;
  padding: 16px;
}

.files-heading {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  margin: 0 0 16px 0;
}

.files-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.audio-card {
  background: #1a1a24;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.audio-card:hover {
  background: #22222e;
}

.audio-card.selected {
  border-color: #6366f1;
  background: rgba(99, 102, 241, 0.1);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
}

.file-icon {
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.6);
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.file-name {
  font-size: 14px;
  color: #ffffff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  flex-shrink: 0;
}

.topic-row {
  margin-bottom: 4px;
}

.topic-name {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-text {
  font-size: 12px;
  color: #00c950;
}

.status-text.processing {
  color: #f59e0b;
}

.duration {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-left: auto;
}

.btn-delete {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-delete:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

/* Per-file progress bar */
.file-progress-bar {
  height: 3px;
  background: #262626;
  border-radius: 2px;
  margin-top: 6px;
  overflow: hidden;
}

.file-progress-fill {
  height: 100%;
  background: #6366f1;
  border-radius: 2px;
  transition: width 0.3s;
}

.progress-pct {
  font-size: 11px;
  color: #888;
  margin-left: 4px;
}

.stage-message {
  font-size: 11px;
  color: #888;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Enter console button for completed files */
.btn-enter-file-console {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #6366f1;
  border: none;
  border-radius: 4px;
  color: #ffffff;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  margin-right: 4px;
}

.btn-enter-file-console:hover {
  background: #5558e3;
}

/* Add More Button */
.add-more {
  margin-top: 8px;
}

.btn-add-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px;
  background: #262626;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-add-more:hover {
  background: #3d3d4d;
}

.add-more-limit {
  text-align: center;
  padding: 10px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
}

/* Bottom Bar */
.bottom-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 92px;
  background: #1a1a24;
  border-top: 1px solid #2d2d3d;
}

.bottom-status {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.btn-enter-console {
  padding: 10px 24px;
  background: #6366f1;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-enter-console:hover {
  background: #5558e3;
}

.btn-cancel-processing {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  margin-left: 8px;
}

.btn-cancel-processing:hover {
  background: rgba(239, 68, 68, 0.25);
  border-color: #ef4444;
}

.btn-cancel-processing.btn-reset {
  background: rgba(161, 161, 161, 0.1);
  color: #a1a1a1;
  border-color: rgba(161, 161, 161, 0.3);
}

.btn-cancel-processing.btn-reset:hover {
  background: rgba(161, 161, 161, 0.2);
  color: #ffffff;
}
</style>
