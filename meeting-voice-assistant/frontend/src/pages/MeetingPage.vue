<template>
  <div id="app">
    <header class="app-header">
      <h1>会议语音助手</h1>
      <p class="subtitle">实时语音识别会议助手</p>
      <button class="btn-nav" @click="goToGraphRAG">
        知识图谱 →
      </button>
    </header>

    <main class="app-main">
      <!-- 三栏布局 -->
      <div class="three-panel-layout" ref="layoutRef">

        <!-- 左侧面板：录音控制 + 文件上传 -->
        <aside class="panel panel-left" :style="{ width: `${leftWidth}px` }">
          <div class="panel-section">
            <h3>录音控制</h3>
            <ControlBar
              :is-connected="isConnected"
              :connecting="connecting"
              :session-id="sessionId"
              :is-recording="isRecording"
              @connect="handleConnect"
              @disconnect="handleDisconnect"
            />
            <AudioRecorder
              :is-connected="isConnected"
              :ws-client="client"
              @start="handleRecordingStart"
              @pause="handleRecordingPause"
              @resume="handleRecordingResume"
              @stop="handleRecordingStop"
            />
          </div>

          <div class="panel-section">
            <h3>文件上传</h3>
            <FileUploader
              @transcript="handleFileTranscript"
              @processing-log="handleProcessingLog"
              @processing-reset="handleProcessingReset"
            />
          </div>
        </aside>

        <!-- 控制柄1 -->
        <div
          class="resize-handle"
          @mousedown="startResize($event, 1)"
        ></div>

        <!-- 中间面板：控制台 + 识别结果 -->
        <section class="panel panel-center" :style="{ width: `${centerWidth}px` }">
          <!-- 处理状态 Console - 常驻显示 -->
          <div class="processing-console">
            <div class="console-header">
              <span class="console-title">处理日志</span>
              <button class="console-clear" @click="clearProcessingLogs">清除</button>
            </div>
            <div class="console-log">
              <div v-if="processingLogs.length === 0" class="console-line">
                <span class="console-time">--:--:--</span>
                <span class="console-indicator">▸</span>
                <span class="console-message">等待处理...</span>
              </div>
              <div
                v-for="(log, index) in processingLogs"
                :key="index"
                class="console-line"
                :class="{ 'in-progress': log.status === 'progress', completed: log.status === 'completed' }"
              >
                <span class="console-time">{{ log.timestamp }}</span>
                <span class="console-indicator">{{ log.status === 'progress' ? '▸' : '✓' }}</span>
                <span class="console-message">{{ log.message }}</span>
              </div>
            </div>
          </div>

          <!-- 识别结果区域 -->
          <div class="result-section">
            <div class="result-header">
              <span class="result-count">{{ transcripts.length }} 条</span>
              <button class="btn-clear" @click="clearTranscripts">清空</button>
            </div>
            <TranscriptPanel
              :transcripts="transcripts"
              :current-text="currentText"
              mode="realtime"
            />
          </div>
        </section>

        <!-- 控制柄2 -->
        <div
          class="resize-handle"
          @mousedown="startResize($event, 2)"
        ></div>

        <!-- 右侧面板：会议总结 -->
        <aside class="panel panel-right" :style="{ width: `${rightWidth}px` }">
          <SummaryPanel
            :analysis-result="analysisResult"
            :chapters="chapters"
            :transcripts="transcripts"
            @analysis-result="handleAnalysisResult"
          />
        </aside>

      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-toast">
        {{ error.message }}
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMeetingStore } from '../stores/meeting'
import { useWebSocket } from '../composables/useWebSocket'
import ControlBar from '../components/ControlBar.vue'
import AudioRecorder from '../components/AudioRecorder.vue'
import TranscriptPanel from '../components/TranscriptPanel.vue'
import FileUploader from '../components/FileUploader.vue'
import SummaryPanel from '../components/SummaryPanel.vue'

const router = useRouter()
const meetingStore = useMeetingStore()
const {
  isConnected,
  sessionId,
  lastTranscript,
  error,
  processingStatus,
  processingMessage,
  analysisResult,
  setAnalysisResult,
  client,
  connect,
  disconnect,
} = useWebSocket()

const connecting = ref(false)
const isRecording = ref(false)
const currentText = ref('')

// 面板宽度控制
const leftWidth = ref(250)
const centerWidth = ref(500)
const rightWidth = ref(500)
const layoutRef = ref<HTMLElement | null>(null)
let isResizing = false
let currentHandle = 0

function startResize(e: MouseEvent, handle: number) {
  isResizing = true
  currentHandle = handle
  document.addEventListener('mousemove', doResize)
  document.addEventListener('mouseup', stopResize)
  e.preventDefault()
}

function doResize(e: MouseEvent) {
  if (!isResizing || !layoutRef.value) return

  const layout = layoutRef.value
  const rect = layout.getBoundingClientRect()
  const x = e.clientX - rect.left
  const handleWidth = 12

  if (currentHandle === 1) {
    const maxLeft = rect.width - rightWidth.value - handleWidth * 2 - 200
    const newLeft = Math.max(150, Math.min(x - handleWidth / 2, maxLeft))
    leftWidth.value = newLeft
    centerWidth.value = rect.width - leftWidth.value - rightWidth.value - handleWidth * 2
  } else if (currentHandle === 2) {
    const minRight = 150
    const maxRight = rect.width - leftWidth.value - handleWidth * 2 - 200
    const newRight = Math.max(minRight, Math.min(rect.width - x - handleWidth / 2, maxRight))
    rightWidth.value = newRight
    centerWidth.value = rect.width - leftWidth.value - rightWidth.value - handleWidth * 2
  }
}

function stopResize() {
  isResizing = false
  document.removeEventListener('mousemove', doResize)
  document.removeEventListener('mouseup', stopResize)
}

// 处理日志状态
interface ProcessingLog {
  timestamp: string
  message: string
  status: 'progress' | 'completed'
}

const processingLogs = ref<ProcessingLog[]>([])

function handleProcessingLog(log: ProcessingLog) {
  const existingIndex = processingLogs.value.findIndex(
    (l) => l.timestamp === log.timestamp && l.message.includes(log.message.substring(0, 10))
  )

  if (existingIndex >= 0) {
    processingLogs.value[existingIndex] = log
  } else {
    processingLogs.value.push(log)
  }
}

function handleProcessingReset() {
  processingLogs.value = []
}

// 从 store 获取数据
const transcripts = computed(() => meetingStore.transcripts)
const chapters = computed(() => meetingStore.chapters)

// 监听 store 的处理状态变化
watch(processingStatus, (newStatus) => {
  if (newStatus) {
    meetingStore.setProcessingStatus(newStatus, processingMessage.value)
  }
})

watch(analysisResult, (newResult) => {
  if (newResult) {
    meetingStore.setAnalysisResult(newResult)
  }
})

// 监听 store 的错误状态
watch(() => meetingStore.errorMessage, (newError) => {
  if (newError) {
    console.error('Meeting error:', newError)
  }
})

async function handleConnect() {
  connecting.value = true
  try {
    await connect()
  } catch (e) {
    console.error('Connection failed:', e)
  } finally {
    connecting.value = false
  }
}

function handleDisconnect() {
  disconnect()
}

client.onResult((data) => {
  if (data.is_final) {
    meetingStore.addTranscript({
      id: `seg_${Date.now()}`,
      text: data.text,
      start_time: data.start_time,
      end_time: data.end_time,
      speaker: data.speaker,
      confidence: data.confidence,
    })
    currentText.value = ''
  } else {
    currentText.value = data.text
  }
})

function handleRecordingStart() {
  isRecording.value = true
}

function handleRecordingPause() {}

function handleRecordingResume() {}

function handleRecordingStop() {
  isRecording.value = false
  currentText.value = ''
}

function handleAnalysisResult(result: any) {
  meetingStore.setAnalysisResult(result)
  setAnalysisResult(result)
}

function handleFileTranscript(data: { transcript: string; segments?: any[]; analysis?: any }) {
  if (data.segments && data.segments.length > 0) {
    for (const seg of data.segments) {
      meetingStore.addTranscript({
        id: `file_${Date.now()}_${Math.random()}`,
        text: seg.text,
        start_time: seg.start_time,
        end_time: seg.end_time,
        speaker: seg.speaker || 'file',
        confidence: 1.0,
      })
    }
  } else if (data.transcript) {
    meetingStore.addTranscript({
      id: `file_${Date.now()}`,
      text: data.transcript,
      start_time: 0,
      end_time: 0,
      speaker: 'file',
      confidence: 1.0,
    })
  }
  if (data.analysis) {
    meetingStore.setAnalysisResult(data.analysis)
    setAnalysisResult(data.analysis)
  }
}

function clearTranscripts() {
  meetingStore.clearTranscripts()
}

function goToGraphRAG() {
  router.push('/graphrag')
}

onUnmounted(() => {
  document.removeEventListener('mousemove', doResize)
  document.removeEventListener('mouseup', stopResize)
})
</script>

<style scoped>
#app {
  min-height: 100vh;
  width: 100%;
  background: #fafafa;
}

.app-header {
  background: #1976d2;
  color: white;
  padding: 1rem 2rem;
  text-align: center;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.app-header h1 {
  margin: 0;
  font-size: 1.3rem;
}

.subtitle {
  margin: 0;
  font-size: 0.85rem;
  opacity: 0.9;
}

.btn-nav {
  margin-left: auto;
  padding: 0.5rem 1rem;
  background: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid rgba(255,255,255,0.4);
  border-radius: 4px;
  cursor: pointer;
}

.btn-nav:hover {
  background: rgba(255,255,255,0.3);
}

.app-main {
  padding: 1rem;
  height: calc(100vh - 80px);
  box-sizing: border-box;
}

.three-panel-layout {
  display: flex;
  flex-direction: row;
  gap: 0;
  height: 100%;
}

.panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow: hidden;
  flex-shrink: 0;
}

.panel-left {
  flex: none;
  width: 300px;
  background: white;
  border-radius: 8px;
  padding: 1rem;
  overflow-y: auto;
  max-height: 100%;
}

.panel-center {
  flex: none;
  display: flex;
  flex-direction: column;
  gap: 0;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  margin: 0 0.5rem;
  min-width: 300px;
}

.panel-right {
  flex: none;
  width: 300px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.resize-handle {
  width: 12px;
  background: #f0f0f0;
  cursor: col-resize;
  flex-shrink: 0;
  position: relative;
  transition: background 0.2s ease;
  border-radius: 4px;
}

.resize-handle:hover {
  background: #e0e0e0;
}

.resize-handle:active {
  background: #d0d0d0;
}

.panel-section {
  margin-bottom: 1rem;
}

.panel-section h3 {
  margin: 0 0 0.75rem 0;
  font-size: 0.9rem;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.result-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 0 0.5rem 0.5rem 0.5rem;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
  margin-bottom: 0.5rem;
}

.result-count {
  font-size: 0.8rem;
  color: #666;
}

.btn-clear {
  padding: 0.25rem 0.75rem;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear:hover {
  background: #e0e0e0;
  color: #333;
}

.error-toast {
  position: fixed;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  background: #f44336;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease;
  z-index: 1000;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(1rem);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.processing-console {
  background: #1e1e1e;
  border-radius: 8px;
  margin: 0.5rem;
  flex-shrink: 0;
  overflow: hidden;
}

.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background: #2d2d2d;
  border-bottom: 1px solid #333;
}

.console-title {
  font-size: 0.8rem;
  color: #888;
  font-weight: 500;
}

.console-clear {
  padding: 0.2rem 0.5rem;
  background: #444;
  color: #aaa;
  border: none;
  border-radius: 3px;
  font-size: 0.7rem;
  cursor: pointer;
}

.console-clear:hover {
  background: #555;
  color: #ccc;
}

.processing-console .console-log {
  max-height: 225px;
  overflow-y: auto;
}

.console-log {
  background: #1e1e1e;
  border-radius: 0;
  padding: 0.5rem 1rem;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 0.8rem;
}

.console-log::-webkit-scrollbar {
  width: 6px;
}

.console-log::-webkit-scrollbar-track {
  background: #2d2d2d;
}

.console-log::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 3px;
}

.console-line {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.2rem 0;
  color: #fff;
  line-height: 1.4;
}

.console-time {
  color: #666;
  flex-shrink: 0;
}

.console-indicator {
  flex-shrink: 0;
}

.console-message {
  flex: 1;
  word-break: break-all;
}

.console-line.in-progress .console-indicator {
  color: #ffc107;
}

.console-line.in-progress .console-message {
  color: #ffc107;
}

.console-line.completed .console-indicator {
  color: #888;
}

.console-line.completed .console-message {
  color: #888;
}

@media (max-width: 1024px) {
  .three-panel-layout {
    flex-direction: column;
    overflow-y: auto;
  }

  .panel-left,
  .panel-center,
  .panel-right {
    width: 100% !important;
    margin: 0 0 0.5rem 0;
  }

  .resize-handle {
    display: none;
  }

  .panel-left {
    flex-direction: row;
    gap: 1rem;
  }

  .panel-section {
    flex: 1;
    margin-bottom: 0;
  }

  .app-main {
    height: auto;
  }
}
</style>
