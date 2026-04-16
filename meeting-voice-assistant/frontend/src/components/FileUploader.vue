<template>
  <div class="file-uploader">
    <!-- 上传区域 -->
    <div
      class="drop-zone"
      :class="{ 'drag-over': isDragOver, 'uploading': isUploading, 'has-result': uploadResult }"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
      @click="openFilePicker"
    >
      <input
        ref="fileInput"
        type="file"
        accept="audio/*,video/*,.mp3,.mp4,.wav,.m4a,.ogg,.flac,.webm"
        @change="handleFileSelect"
        hidden
      />

      <div v-if="isUploading" class="upload-progress">
        <div class="progress-header">
          <span class="file-name">{{ currentFileName }}</span>
          <button class="btn-cancel" @click.stop="cancelUpload" title="取消上传">✕</button>
        </div>
        <p class="upload-status">正在上传和处理文件...</p>
        <p class="upload-percent">{{ uploadProgress }}%</p>
      </div>

      <div v-else-if="uploadResult" class="drop-content has-result">
        <div class="result-actions">
          <button class="btn-cancel result-cancel" @click.stop="resetUpload" title="清除结果">
            <span>✕</span>
            <span>清除</span>
          </button>
        </div>
        <div class="upload-icon">📁</div>
        <p class="drop-text">{{ currentFileName || '文件已上传' }}</p>
        <p class="drop-hint">点击选择新文件替换</p>
      </div>

      <div v-else class="drop-content">
        <div class="upload-icon">📁</div>
        <p class="drop-text">
          {{ isDragOver ? '松开以上传文件' : '拖拽音频/视频文件到此处' }}
        </p>
        <p class="drop-hint">支持 MP3, MP4, WAV, M4A, OGG, FLAC, WebM 格式</p>
        <button class="btn-browse" @click.stop="openFilePicker">
          选择文件
        </button>
      </div>
    </div>

    <!-- 转写结果区域 -->
    <div v-if="uploadResult?.segments?.length" class="transcript-result">
      <div class="result-header">
        <h4>转写结果</h4>
        <span class="segment-count">{{ uploadResult.segments.length }} 段</span>
      </div>
      <div class="transcript-list">
        <div
          v-for="(seg, idx) in uploadResult.segments"
          :key="idx"
          class="transcript-segment"
          :style="{ borderLeftColor: getSpeakerColor(seg.speaker) }"
        >
          <span class="speaker-badge" :style="{ backgroundColor: getSpeakerColor(seg.speaker) }">
            {{ formatSpeakerLabel(seg.speaker) }}
          </span>
          <span class="segment-text">{{ seg.text }}</span>
          <span class="segment-time">
            {{ formatTime(seg.start_time) }} - {{ formatTime(seg.end_time) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 上传进度 -->
    <div v-else-if="uploadResult && uploadResult.progress < 100" class="upload-progress-inline">
      <p>正在处理...</p>
    </div>

    <!-- 上传完成提示（无结构化结果时） -->
    <div v-else-if="uploadResult && uploadResult.progress >= 100 && !uploadResult.segments?.length" class="upload-complete">
      <p>识别完成，结果已添加到转写面板</p>
    </div>

    <!-- 错误消息 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { API_CONFIG } from '../api/config'

interface Segment {
  text: string
  speaker: string
  start_time: number
  end_time: number
}

interface ProcessingStatus {
  session_id: string
  stage: string
  progress: number
  message: string
  started_at: string | null
  stage_started_at: string | null
  elapsed_seconds: number
  stage_elapsed_seconds: number
  error: string | null
}

const emit = defineEmits<{
  (e: 'transcript', data: { transcript: string; segments?: Segment[]; analysis?: any }): void
  (e: 'processing-log', log: { timestamp: string; message: string; status: 'progress' | 'completed' }): void
  (e: 'processing-reset'): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragOver = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadResult = ref<{ transcript: string; segments?: Segment[]; analysis?: any; progress: number } | null>(null)
const errorMessage = ref('')
const currentFileName = ref('')
const currentXhr = ref<XMLHttpRequest | null>(null)

// 处理日志
interface ProcessingLog {
  timestamp: string
  message: string
  status: 'progress' | 'completed'
}
const processingLogs = ref<ProcessingLog[]>([])

// 添加日志
function addLog(message: string, status: 'progress' | 'completed' = 'progress') {
  const now = new Date()
  const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  const log = { timestamp, message, status }
  processingLogs.value.push(log)
  emit('processing-log', log)
}

// 更新最后一条日志为完成状态
function completeLastLog(message?: string) {
  const lastLog = processingLogs.value[processingLogs.value.length - 1]
  if (lastLog) {
    lastLog.status = 'completed'
    if (message) {
      lastLog.message = message
    }
    emit('processing-log', { ...lastLog })
  }
}

// 替换最后一条日志
function replaceLastLog(message: string) {
  const lastLog = processingLogs.value[processingLogs.value.length - 1]
  if (lastLog) {
    lastLog.message = message
    emit('processing-log', { ...lastLog })
  }
}

// SSE 状态
const processingStage = ref('idle')
const processingMessage = ref('')
const stageStartedAt = ref<number | null>(null)
const totalStartedAt = ref<number | null>(null)
const currentSessionId = ref<string | null>(null)
let statusEventSource: EventSource | null = null
let localTimer: number | null = null
const tick = ref(0)

// 计算属性
const stageElapsedSeconds = computed(() => {
  tick.value // 依赖 tick 以触发更新
  if (!stageStartedAt.value) return 0
  return Math.floor((Date.now() - stageStartedAt.value) / 1000)
})

const totalElapsedSeconds = computed(() => {
  tick.value // 依赖 tick 以触发更新
  if (!totalStartedAt.value) return 0
  return Math.floor((Date.now() - totalStartedAt.value) / 1000)
})

const stageDisplayName = computed(() => {
  const stageNames: Record<string, string> = {
    idle: '等待中',
    uploading: '上传中',
    transcribing: '语音识别',
    analyzing: '深度分析',
    completed: '已完成',
    error: '出错'
  }
  return stageNames[processingStage.value] || processingStage.value
})

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

const speakerColorMap = new Map<string, string>()

function getSpeakerColor(speaker: string): string {
  if (!speakerColorMap.has(speaker)) {
    speakerColorMap.set(speaker, speakerColors[speakerColorMap.size % speakerColors.length])
  }
  return speakerColorMap.get(speaker) || speakerColors[0]
}

function formatSpeakerLabel(speaker: string): string {
  if (!speaker) return '未知'
  if (speaker === 'file') return '文件'
  if (speaker === 'unknown') return '未知'
  if (speaker.startsWith('speaker_')) {
    const index = parseInt(speaker.split('_')[1])
    return String.fromCharCode(65 + index) // A, B, C, ...
  }
  return speaker
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}秒`
  }
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}分${secs}秒`
}

let statusPollInterval: number | null = null

async function fetchStatus(sessionId: string) {
  try {
    const response = await fetch(API_CONFIG.uploadStatusUrl(sessionId))
    if (response.ok) {
      const status: ProcessingStatus = await response.json()
      console.log('[FileUploader] Status update:', status)

      processingStage.value = status.stage
      processingMessage.value = status.message
      uploadProgress.value = status.progress

      // 更新阶段开始时间
      if (status.stage_started_at) {
        stageStartedAt.value = new Date(status.stage_started_at).getTime()
      }

      // 检查是否完成或出错
      if (status.stage === 'completed' || status.stage === 'error') {
        console.log('[FileUploader] Processing ended:', status.stage)
        stopPolling()
      }
    }
  } catch (e) {
    console.error('[FileUploader] Failed to fetch status:', e)
  }
}

function startPolling(sessionId: string) {
  stopPolling()
  currentSessionId.value = sessionId
  // 立即获取一次状态
  fetchStatus(sessionId)
  // 每秒轮询一次
  statusPollInterval = window.setInterval(() => {
    fetchStatus(sessionId)
  }, 1000)
}

function stopPolling() {
  if (statusPollInterval) {
    clearInterval(statusPollInterval)
    statusPollInterval = null
  }
}

function disconnectStatusStream() {
  stopPolling()
  if (statusEventSource) {
    statusEventSource.close()
    statusEventSource = null
  }
  if (localTimer) {
    clearInterval(localTimer)
    localTimer = null
  }
}

function resetProcessingStatus() {
  processingStage.value = 'idle'
  processingMessage.value = ''
  uploadProgress.value = 0
  stageStartedAt.value = null
  totalStartedAt.value = null
  currentSessionId.value = null
  disconnectStatusStream()
}

function openFilePicker() {
  if (isUploading.value) return
  fileInput.value?.click()
}

function cancelUpload() {
  if (currentXhr.value) {
    currentXhr.value.abort()
    currentXhr.value = null
  }
  resetUpload()
}

function resetUpload() {
  isUploading.value = false
  uploadProgress.value = 0
  uploadResult.value = null
  errorMessage.value = ''
  currentFileName.value = ''
  currentXhr.value = null
  processingLogs.value = []
  resetProcessingStatus()
  emit('processing-reset')
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function handleDragOver(event: DragEvent) {
  isDragOver.value = true
}

function handleDragLeave(event: DragEvent) {
  isDragOver.value = false
}

async function handleDrop(event: DragEvent) {
  isDragOver.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    await uploadFile(files[0])
  }
}

async function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    await uploadFile(files[0])
  }
}

async function uploadFile(file: File) {
  errorMessage.value = ''
  uploadResult.value = null
  isUploading.value = true
  uploadProgress.value = 0
  currentFileName.value = file.name
  currentXhr.value = null
  processingLogs.value = []

  // 添加第一条日志
  addLog(`正在上传文件: ${file.name}`)

  // 初始化处理状态
  processingStage.value = 'uploading'
  stageStartedAt.value = Date.now()
  totalStartedAt.value = Date.now()
  tick.value = 0

  // 启动本地计时器，每秒更新以触发 computed 重新计算
  if (localTimer) clearInterval(localTimer)
  localTimer = window.setInterval(() => {
    tick.value++
  }, 1000)

  let uploadedSessionId: string | null = null

  try {
    const formData = new FormData()
    formData.append('file', file)

    // 使用 XMLHttpRequest 来追踪上传进度
    const xhr = new XMLHttpRequest()
    currentXhr.value = xhr

    await new Promise<void>((resolve, reject) => {
      let uploadComplete = false

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const uploadPercent = Math.round((e.loaded / e.total) * 100)
          uploadProgress.value = uploadPercent
          replaceLastLog(`正在上传中... ${Math.round(e.loaded / 1024)}KB / ${Math.round(e.total / 1024)}KB (${uploadPercent}%)`)
        }
      })

      // 上传完成，准备接收服务器处理结果
      xhr.upload.addEventListener('loadend', () => {
        if (!uploadComplete) {
          uploadComplete = true
          // 上传完成但服务器还在处理中
          addLog('已完成上传')
          addLog('正在识别音频内容...')
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText)
            uploadProgress.value = 100
            uploadedSessionId = response.session_id
            console.log('[FileUploader] Upload completed, session_id:', uploadedSessionId)

            if (response.success) {
              // 更新日志
              completeLastLog('已完成音频识别')
              addLog(`已完成音频识别，共 ${response.segments?.length || 0} 段`)

              uploadResult.value = {
                transcript: response.transcript || '（无转写文本）',
                segments: response.segments || [],
                analysis: response.analysis,
                progress: 100
              }
              processingStage.value = 'completed'
              emit('transcript', uploadResult.value)

              // 如果有分析结果，也添加日志
              if (response.analysis) {
                addLog('正在识别语音内容...')
                setTimeout(() => {
                  completeLastLog('已完成语音内容识别')
                  addLog('处理完成')
                }, 500)
              } else {
                addLog('处理完成')
              }
            } else {
              completeLastLog(`上传失败: ${response.message || '未知错误'}`)
              errorMessage.value = response.message || '上传失败'
              processingStage.value = 'error'
            }
          } catch (e) {
            completeLastLog('解析响应失败')
            errorMessage.value = '解析响应失败'
            processingStage.value = 'error'
          }
          resolve()
        } else {
          try {
            const error = JSON.parse(xhr.responseText)
            completeLastLog(`上传失败: ${error.detail || xhr.status}`)
            errorMessage.value = error.detail || `上传失败: ${xhr.status}`
            processingStage.value = 'error'
          } catch {
            completeLastLog(`上传失败: ${xhr.status}`)
            errorMessage.value = `上传失败: ${xhr.status}`
            processingStage.value = 'error'
          }
          reject(new Error(errorMessage.value))
        }
      })

      xhr.addEventListener('error', () => {
        errorMessage.value = '网络错误，请检查后端服务'
        processingStage.value = 'error'
        processingMessage.value = '网络错误'
        reject(new Error(errorMessage.value))
      })

      xhr.addEventListener('abort', () => {
        errorMessage.value = '上传已取消'
        processingStage.value = 'error'
        processingMessage.value = '已取消'
        reject(new Error('Upload cancelled'))
      })

      xhr.open('POST', API_CONFIG.uploadUrl)
      xhr.send(formData)
    })

    // 如果有 session_id，轮询状态
    if (uploadedSessionId) {
      // 轮询状态
      startPolling(uploadedSessionId)
    }
  } catch (error) {
    console.error('Upload error:', error)
    processingStage.value = 'error'
    processingMessage.value = '上传出错'
  } finally {
    isUploading.value = false
    currentXhr.value = null
    // 清理本地计时器
    if (localTimer) {
      clearInterval(localTimer)
      localTimer = null
    }
    // 延迟清理轮询
    setTimeout(() => {
      stopPolling()
    }, 3000)
  }
}
</script>

<style scoped>
.file-uploader {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  min-height: 0;
  flex: 1;
  box-sizing: border-box;
}

.drop-zone {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100px;
}

.drop-zone:hover {
  border-color: #4caf50;
  background: #f1f8f1;
}

.drop-zone.drag-over {
  border-color: #4caf50;
  background: #e8f5e9;
  border-style: solid;
}

.drop-zone.uploading {
  cursor: wait;
  opacity: 0.8;
}

.drop-zone.has-result {
  padding: 1rem;
}

.drop-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.drop-content.has-result {
  position: relative;
}

.result-actions {
  position: absolute;
  top: 0;
  right: 0;
}

.btn-cancel {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: #f44336;
  color: white;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn-cancel:hover {
  background: #d32f2f;
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-bottom: 0.5rem;
}

.file-name {
  font-size: 0.9rem;
  color: #333;
  max-width: 80%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-cancel {
  width: auto;
  height: auto;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  gap: 0.25rem;
  font-size: 0.8rem;
}

.upload-icon {
  font-size: 3rem;
}

.drop-text {
  font-size: 1.1rem;
  color: #333;
  margin: 0;
}

.drop-hint {
  font-size: 0.85rem;
  color: #888;
  margin: 0;
}

.btn-browse {
  margin-top: 0.5rem;
  padding: 0.5rem 1.5rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-browse:hover {
  background: #388e3c;
}

/* 转写结果区域 */
.transcript-result {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fafafa;
  border-radius: 8px;
  min-height: 0;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}

.result-header h4 {
  margin: 0;
  font-size: 0.9rem;
  color: #333;
}

.segment-count {
  font-size: 0.8rem;
  color: #666;
}

.transcript-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-height: 0;
}

.transcript-segment {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  background: white;
  border-radius: 8px;
  border-left: 3px solid #4caf50;
}

.speaker-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 24px;
  padding: 0 6px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.segment-text {
  flex: 1;
  color: #333;
  line-height: 1.5;
  font-size: 0.9rem;
}

.segment-time {
  font-size: 0.7rem;
  color: #999;
  flex-shrink: 0;
}

/* 上传进度 */
.upload-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
}

.upload-status {
  font-size: 0.85rem;
  color: #666;
  margin: 0;
}

.upload-percent {
  font-size: 0.9rem;
  color: #333;
  font-weight: 500;
  margin: 0;
}

.upload-progress-inline {
  padding: 1rem;
  background: #e3f2fd;
  border-radius: 8px;
  text-align: center;
}

.upload-progress-inline p {
  margin: 0;
  color: #1976d2;
  font-size: 0.9rem;
}

.upload-complete {
  padding: 1rem;
  background: #e8f5e9;
  border-radius: 8px;
  text-align: center;
}

.upload-complete p {
  margin: 0;
  color: #4caf50;
  font-size: 0.9rem;
}

.error-message {
  padding: 0.75rem;
  background: #ffebee;
  color: #c62828;
  border-radius: 4px;
  border-left: 3px solid #c62828;
  font-size: 0.9rem;
}
</style>
