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

        <!-- Processing Status Card (shown while uploading/processing) -->
        <div v-if="hasProcessingFile" class="processing-section">
          <div class="processing-header">
            <div class="processing-info">
              <span class="processing-file">{{ processingFileName }}</span>
              <span class="processing-stage" :class="debugStore.stage">
                {{ getStageLabel(debugStore.stage) }}
              </span>
            </div>
            <div class="processing-progress">
              <span>{{ debugStore.progress }}%</span>
            </div>
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
              <span class="stat-label">剩余时间</span>
              <span class="stat-value">{{ formatTime(debugStore.remainingTime) }}</span>
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
                      {{ file.status === 'completed' ? '已完成' : '处理中' }}
                    </span>
                    <span class="duration">{{ file.duration || '--:--' }}</span>
                  </div>
                </div>
                <button class="btn-delete" @click="removeFile(file.id)">
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.33" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <div class="add-more">
            <button class="btn-add-more" @click="triggerFileInput">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 3V13M3 8H13" stroke="currentColor" stroke-width="1.33" stroke-linecap="round"/>
              </svg>
              继续添加音频
            </button>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMeetingStore, type Chapter } from '../stores/meeting'
import { useDebugStore } from '../stores/debug'
import { API_CONFIG } from '../api/config'

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

// File input ref
const fileInputRef = ref<HTMLInputElement | null>(null)

// State
const meetingTitleInput = ref('')
const meetingTitle = computed(() => meetingTitleInput.value)
const isDragOver = ref(false)
const activeDetailTab = ref('transcript')

const uploadedFiles = computed(() => store.uploadedFiles)

const completedCount = computed(() =>
  uploadedFiles.value.filter(f => f.status === 'completed').length
)

// Check if any file is processing
const hasProcessingFile = computed(() =>
  store.uploadedFiles.some(f => f.status === 'processing')
)

const processingFileName = computed(() => {
  const file = store.uploadedFiles.find(f => f.status === 'processing')
  return file?.name || '处理中'
})

const detailTabs = computed(() => [
  { id: 'transcript', label: '转写', count: debugStore.transcriptResult?.segments?.length },
  { id: 'analysis', label: '分析', count: debugStore.analysisResult?.chapters?.length }
])

function getStageLabel(stage: string): string {
  const labels: Record<string, string> = {
    idle: '等待',
    uploading: '上传中',
    transcribing: '转写中',
    analyzing: '分析中',
    completed: '完成',
    error: '错误'
  }
  return labels[stage] || stage
}

function formatTime(seconds: number | null): string {
  if (seconds === null || seconds === undefined) return '-'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

// SSE Polling
let pollInterval: number | null = null

function startPolling(sessionId: string) {
  stopPolling()

  async function poll() {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/upload/${sessionId}/status`)
      if (response.ok) {
        const data = await response.json()
        debugStore.updateFromSSE(data)

        if (data.stage === 'completed') {
          stopPolling()
          // Data already populated from upload response, no need to fetch again
        }
      }
    } catch (e) {
      console.error('[MeetingPage] Poll error:', e)
    }
  }

  pollInterval = window.setInterval(poll, 1000)
  poll()
}

function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}

async function fetchFullResult(sessionId: string) {
  console.log('[MeetingPage] fetchFullResult called with sessionId:', sessionId)
  try {
    const response = await fetch(`http://localhost:8000/api/v1/upload/${sessionId}`)
    console.log('[MeetingPage] fetchFullResult response status:', response.status)
    if (response.ok) {
      const data = await response.json()
      console.log('[MeetingPage] fetchFullResult data keys:', Object.keys(data))
      populateStoresFromResponse(data)
    } else {
      console.error('[MeetingPage] fetchFullResult failed with status:', response.status)
    }
  } catch (e) {
    console.error('[MeetingPage] Fetch result error:', e)
  }
}

function populateStoresFromResponse(data: UploadResponse) {
  console.log('[MeetingPage] populateStoresFromResponse called')
  console.log('[MeetingPage] data.segments count:', data.segments?.length)
  console.log('[MeetingPage] data.chapters count:', data.chapters?.length)
  console.log('[MeetingPage] data.theme:', data.theme)

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
      name: `发言人 ${String.fromCharCode(65 + idx)}`
    }))
    console.log('[MeetingPage] Setting meetingStore speakers:', speakers.length)
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
    console.log('[MeetingPage] Setting meetingStore chapters:', chapters.length)
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
    console.log('[MeetingPage] Setting meetingStore decisions:', allDecisions.length, 'actionItems:', allActionItems.length)
    store.setDecisions(allDecisions)
    store.setActionItems(allActionItems)

    // Set topic from analysis
    if (data.theme) {
      console.log('[MeetingPage] Setting meetingStore topic:', data.theme)
      store.setTopic(data.theme)
    }

    // Set audio URL for playback
    if (data.audio_url) {
      console.log('[MeetingPage] Setting meetingStore audioUrl:', data.audio_url)
      store.setAudioUrl(data.audio_url)
    }
  }

  console.log('[MeetingPage] Final meetingStore state:')
  console.log('  topic:', store.topic)
  console.log('  speakers:', store.speakers.length)
  console.log('  chapters:', store.chapters.length)
  console.log('  decisions:', store.decisions.length)
  console.log('  actionItems:', store.actionItems.length)
}

onUnmounted(() => {
  stopPolling()
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

  const file = files[0]
  const sizeMB = (file.size / (1024 * 1024)).toFixed(1)
  const fileId = `file_${Date.now()}`
  const tempSessionId = `upload_${Date.now()}`

  // Set session in store
  store.setMeetingId(tempSessionId)
  debugStore.sessionId = tempSessionId
  debugStore.stage = 'uploading'
  debugStore.progress = 0
  debugStore.message = '正在上传音频文件...'

  // Add file to list
  store.addUploadedFile({
    id: fileId,
    name: file.name,
    size: `${sizeMB} MB`,
    topic: meetingTitleInput.value || '会议记录',
    status: 'processing',
    duration: '--:--'
  })

  store.updateUploadProgress({
    stage: 'uploading',
    progress: 0,
    message: '正在上传音频文件...'
  })

  // Start polling immediately
  startPolling(tempSessionId)

  try {
    const formData = new FormData()
    formData.append('file', file)

    await new Promise<void>((resolve, reject) => {
      const xhr = new XMLHttpRequest()

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const uploadPercent = Math.round((e.loaded / e.total) * 50)
          debugStore.progress = uploadPercent
          debugStore.message = `正在上传... ${uploadPercent}%`
          store.updateUploadProgress({
            stage: 'uploading',
            progress: uploadPercent,
            message: `正在上传... ${uploadPercent}%`
          })
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText)
            console.log('[MeetingPage] Upload response:', response)

            const finalSessionId = response.session_id || fileId
            store.setMeetingId(finalSessionId)
            debugStore.sessionId = finalSessionId

            // CRITICAL: Populate stores from response data immediately!
            populateStoresFromResponse(response)

            // Update file status
            store.updateUploadedFile(fileId, { status: 'completed' })

            // Update store
            debugStore.stage = 'completed'
            debugStore.progress = 100
            debugStore.message = '处理完成'

            resolve()
          } catch (e) {
            console.error('[MeetingPage] Failed to parse response:', e)
            reject(e)
          }
        } else {
          console.error('[MeetingPage] Upload failed:', xhr.status)
          debugStore.stage = 'error'
          debugStore.message = `上传失败: ${xhr.status}`
          store.updateUploadProgress({
            stage: 'error',
            progress: 0,
            message: `上传失败: ${xhr.status}`
          })
          reject(new Error(`Upload failed: ${xhr.status}`))
        }
      })

      xhr.addEventListener('error', () => {
        console.error('[MeetingPage] Upload error')
        debugStore.stage = 'error'
        debugStore.message = '上传失败'
        store.updateUploadProgress({
          stage: 'error',
          progress: 0,
          message: '上传失败'
        })
        reject(new Error('Upload error'))
      })

      xhr.open('POST', API_CONFIG.uploadUrl)
      xhr.send(formData)
    })
  } catch (e) {
    console.error('[MeetingPage] Upload failed:', e)
    store.updateUploadedFile(fileId, { status: 'pending' })
  }
}

function removeFile(id: string) {
  store.removeUploadedFile(id)
}

function useDemoAudio() {
  store.updateUploadProgress({
    stage: 'uploading',
    progress: 0,
    message: '正在准备示例音频...'
  })

  const demoFiles = [
    { name: '用户反馈分析.mp3', size: '12.3 MB', topic: '用户反馈与问题分析', duration: '4:00' },
    { name: '时间规划讨论.mp3', size: '8.7 MB', topic: '时间规划与资源评估', duration: '2:20' },
    { name: '实施方案制定.mp3', size: '9.5 MB', topic: '实施方案与行动计划', duration: '2:00' }
  ]

  for (const demo of demoFiles) {
    store.addUploadedFile({
      id: `demo_${Date.now()}_${Math.random().toString(36).slice(2)}`,
      name: demo.name,
      size: demo.size,
      topic: demo.topic,
      status: 'completed',
      duration: demo.duration
    })
  }

  store.setMeetingId(`meeting_${Date.now()}`)
  store.setTopic(meetingTitleInput.value || 'Q2产品路线图讨论会')

  store.setSpeakers([
    { id: 'spk1', name: '产品经理', color: '#6366f1' },
    { id: 'spk2', name: '技术负责人', color: '#10b981' },
    { id: 'spk3', name: '设计师', color: '#f59e0b' }
  ])

  store.setDecisions([
    { decision: '决定采用两阶段实施方案', source_timestamps: [{ start: 0, end: 380 }] },
    { decision: '资源分配已确定', source_timestamps: [{ start: 380, end: 500 }] }
  ])

  store.setActionItems([
    { todo: '王磊：下周三前提交技术方案和工作量评估报告', source_timestamps: [{ start: 450, end: 480 }] },
    { todo: '李娜：协调用户研究团队，补充功能优先级分析', source_timestamps: [{ start: 480, end: 510 }] },
    { todo: '张伟：准备技术方案评审会议', source_timestamps: [{ start: 510, end: 540 }] }
  ])

  router.push('/console')
}

function enterConsole() {
  router.push('/console')
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
</style>
