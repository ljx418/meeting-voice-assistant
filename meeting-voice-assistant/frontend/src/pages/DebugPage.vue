<template>
  <div class="debug-page">
    <!-- Header -->
    <header class="debug-header">
      <div class="header-left">
        <h1 class="debug-title">Debug Console</h1>
        <span class="session-badge" v-if="store.sessionId">
          Session: {{ store.sessionId }}
        </span>
      </div>
      <div class="header-right">
        <button class="btn-link" @click="goToConsole">三栏布局 →</button>
        <button class="btn-refresh" @click="refreshResults">刷新结果</button>
      </div>
    </header>

    <!-- Status Bar -->
    <div class="status-bar">
      <div class="status-item">
        <span class="status-label">Stage:</span>
        <span class="status-value" :class="stageClass">{{ store.stage.toUpperCase() }}</span>
      </div>
      <div class="status-item">
        <span class="status-label">Progress:</span>
        <span class="status-value">{{ store.progress }}%</span>
      </div>
      <div class="status-item" v-if="store.remainingTime">
        <span class="status-label">剩余时间:</span>
        <span class="status-value">{{ formatTime(store.remainingTime) }}</span>
      </div>
      <div class="status-item" v-if="store.speakerCount">
        <span class="status-label">说话人:</span>
        <span class="status-value">{{ store.speakerCount }}</span>
      </div>
      <div class="status-item" v-if="store.segmentCount">
        <span class="status-label">片段数:</span>
        <span class="status-value">{{ store.segmentCount }}</span>
      </div>
      <div class="status-item flex-1">
        <span class="status-label">Message:</span>
        <span class="status-value">{{ store.message || '-' }}</span>
      </div>
    </div>

    <!-- Progress Bar -->
    <div class="progress-bar-container">
      <div class="progress-bar" :style="{ width: store.progress + '%' }"></div>
    </div>

    <!-- Tabs -->
    <div class="tab-bar">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-btn"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
        <span class="tab-count" v-if="tab.count !== undefined">{{ tab.count }}</span>
      </button>
    </div>

    <!-- Content -->
    <div class="debug-content">
      <!-- Transcript Tab -->
      <div v-if="activeTab === 'transcript'" class="json-viewer">
        <div v-if="store.transcriptResult" class="json-section">
          <h3>Segments ({{ store.transcriptResult.segments?.length || 0 }})</h3>
          <div class="segment-list">
            <div v-for="(seg, idx) in store.transcriptResult.segments" :key="idx" class="segment-item">
              <span class="seg-time">[{{ formatTime(seg.start_time) }} - {{ formatTime(seg.end_time) }}]</span>
              <span class="seg-speaker">{{ seg.speaker }}:</span>
              <span class="seg-text">{{ seg.text }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无转写结果</p>
          <p class="hint">请先上传音频文件</p>
        </div>
      </div>

      <!-- Analysis Tab -->
      <div v-if="activeTab === 'analysis'" class="json-viewer">
        <div v-if="store.analysisResult" class="analysis-content">
          <div class="analysis-section">
            <h3>Theme</h3>
            <p>{{ store.analysisResult.theme || '-' }}</p>
          </div>
          <div class="analysis-section">
            <h3>Topics</h3>
            <div class="tag-list">
              <span v-for="topic in store.analysisResult.topics" :key="topic" class="tag">{{ topic }}</span>
            </div>
          </div>
          <div class="analysis-section">
            <h3>Summary</h3>
            <p>{{ store.analysisResult.summary || '-' }}</p>
          </div>
          <div class="analysis-section">
            <h3>Chapters ({{ store.analysisResult.chapters?.length || 0 }})</h3>
            <div class="chapter-list">
              <details v-for="chapter in store.analysisResult.chapters" :key="chapter.id" class="chapter-item">
                <summary class="chapter-summary">
                  <span class="chapter-title">{{ chapter.title }}</span>
                  <span class="chapter-time">[{{ formatTime(chapter.start_time) }} - {{ formatTime(chapter.end_time) }}]</span>
                </summary>
                <div class="chapter-content">
                  <div class="chapter-subsection">
                    <h4>Summary</h4>
                    <p>{{ chapter.summary }}</p>
                  </div>
                  <div class="chapter-subsection" v-if="chapter.speaker_summaries?.length">
                    <h4>Speaker Summaries</h4>
                    <div v-for="ss in chapter.speaker_summaries" :key="ss.speaker" class="speaker-summary">
                      <span class="speaker-name">{{ ss.speaker }}:</span>
                      <span>{{ ss.summary }}</span>
                      <div class="timestamps">
                        <span v-for="ts in ss.source_timestamps" :key="ts.start" class="timestamp">
                          [{{ formatTime(ts.start) }} - {{ formatTime(ts.end) }}]
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="chapter-subsection" v-if="chapter.decisions?.length">
                    <h4>Decisions</h4>
                    <div v-for="d in chapter.decisions" :key="d.decision" class="decision-item">
                      <span>{{ d.decision }}</span>
                      <div class="timestamps">
                        <span v-for="ts in d.source_timestamps" :key="ts.start" class="timestamp">
                          [{{ formatTime(ts.start) }} - {{ formatTime(ts.end) }}]
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="chapter-subsection" v-if="chapter.action_items?.length">
                    <h4>Action Items</h4>
                    <div v-for="a in chapter.action_items" :key="a.todo" class="action-item">
                      <span>{{ a.todo }}</span>
                      <div class="timestamps">
                        <span v-for="ts in a.source_timestamps" :key="ts.start" class="timestamp">
                          [{{ formatTime(ts.start) }} - {{ formatTime(ts.end) }}]
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </details>
            </div>
          </div>
          <div class="analysis-section" v-if="store.analysisResult.speaker_roles?.length">
            <h3>Speaker Roles</h3>
            <div v-for="role in store.analysisResult.speaker_roles" :key="role.speaker" class="role-item">
              <span class="role-speaker">{{ role.speaker }}:</span>
              <span class="role-name">{{ role.role }}</span>
              <span class="role-reasoning">({{ role.reasoning }})</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无分析结果</p>
          <p class="hint">请先完成音频转写和分析</p>
        </div>
      </div>

      <!-- GraphRAG Tab -->
      <div v-if="activeTab === 'graphrag'" class="json-viewer">
        <div class="graphrag-search">
          <input
            v-model="searchQuery"
            class="search-input"
            placeholder="输入查询内容..."
            @keyup.enter="triggerSearch"
          />
          <button class="btn-search" @click="triggerSearch">搜索</button>
          <button class="btn-auto" @click="autoSearch">自动检索</button>
        </div>
        <div v-if="store.graphragResult" class="graphrag-result">
          <div class="answer-section">
            <h3>Answer</h3>
            <p>{{ store.graphragResult.answer || '-' }}</p>
          </div>
          <div class="sources-section">
            <h3>Sources ({{ store.graphragResult.sources?.length || 0 }})</h3>
            <div v-for="(src, idx) in store.graphragResult.sources" :key="idx" class="source-item">
              <div class="source-header">
                <span class="source-id">{{ src.doc_id }}</span>
                <span class="source-score">{{ (src.similarity * 100).toFixed(1) }}%</span>
              </div>
              <p class="source-chunk">{{ src.chunk }}</p>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无GraphRAG检索结果</p>
          <p class="hint">点击"自动检索"使用会议内容查询</p>
        </div>
      </div>

      <!-- Raw SSE Tab -->
      <div v-if="activeTab === 'raw'" class="json-viewer">
        <div class="sse-log">
          <div v-for="(msg, idx) in store.sseMessages" :key="idx" class="sse-item">
            <span class="sse-time">{{ msg.time }}</span>
            <span class="sse-type">[{{ msg.type }}]</span>
            <pre class="sse-data">{{ JSON.stringify(msg.data, null, 2) }}</pre>
          </div>
          <div v-if="store.sseMessages.length === 0" class="empty-state">
            <p>暂无SSE消息</p>
            <p class="hint">等待服务器推送...</p>
          </div>
        </div>
      </div>

      <!-- Raw JSON Tab -->
      <div v-if="activeTab === 'raw-json'" class="json-viewer">
        <div class="json-section">
          <h3>Transcript (Raw)</h3>
          <pre class="json-pre">{{ JSON.stringify(store.transcriptResult, null, 2) || 'null' }}</pre>
        </div>
        <div class="json-section">
          <h3>Analysis (Raw)</h3>
          <pre class="json-pre">{{ JSON.stringify(store.analysisResult, null, 2) || 'null' }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDebugStore } from '../stores/debug'
import { useMeetingStore } from '../stores/meeting'
import { API_CONFIG } from '../api/config'

const router = useRouter()
const route = useRoute()
const store = useDebugStore()
const meetingStore = useMeetingStore()

const activeTab = ref('transcript')
const searchQuery = ref('')

const tabs = computed(() => [
  { id: 'transcript', label: 'Transcripts', count: store.transcriptResult?.segments?.length },
  { id: 'analysis', label: 'Analysis', count: store.analysisResult?.chapters?.length },
  { id: 'graphrag', label: 'GraphRAG' },
  { id: 'raw', label: 'Raw SSE' },
  { id: 'raw-json', label: 'Raw JSON' }
])

const stageClass = computed(() => ({
  'status-processing': store.isProcessing,
  'status-complete': store.isComplete,
  'status-error': store.isError
}))

// Reactive session_id: use URL param first, then fall back to meetingStore
const currentSessionId = computed(() => {
  return (route.query.session_id as string) || meetingStore.sessionId
})

// Watch for session_id changes and start/stop polling accordingly
watch(currentSessionId, (newSessionId, oldSessionId) => {
  if (newSessionId && newSessionId !== oldSessionId) {
    store.sessionId = newSessionId
    startPolling(newSessionId)
  }
}, { immediate: false })

function formatTime(seconds: number): string {
  if (seconds === undefined || seconds === null) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function goToConsole() {
  router.push('/console')
}

async function refreshResults() {
  if (!store.sessionId) return

  // Fetch latest results from backend
  try {
    // TODO: Implement fetch from backend
  } catch (e) {
    console.error('Failed to refresh:', e)
  }
}

async function triggerSearch() {
  if (!searchQuery.value) return

  try {
    const response = await fetch(`${API_CONFIG.graphragUrl}/api/v1/query/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: searchQuery.value,
        top_k: 10
      })
    })
    const data = await response.json()
    store.setGraphRAG(data)
  } catch (e) {
    console.error('GraphRAG search failed:', e)
  }
}

async function autoSearch() {
  if (!store.analysisResult) return

  const queryParts: string[] = []
  if (store.analysisResult.theme) queryParts.push(store.analysisResult.theme)
  queryParts.push(...store.analysisResult.topics)
  store.analysisResult.chapters?.forEach(ch => {
    ch.decisions?.forEach(d => queryParts.push(d.decision))
    ch.action_items?.forEach(a => queryParts.push(a.todo))
  })

  searchQuery.value = queryParts.slice(0, 5).join(' ')
  await triggerSearch()
}

// Connect to SSE for live updates
let statusPollInterval: number | null = null

function startPolling(sessionId: string) {
  // Stop any existing polling
  if (statusPollInterval) {
    clearInterval(statusPollInterval)
    statusPollInterval = null
  }

  async function pollStatus() {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/upload/${sessionId}/status`)
      if (response.ok) {
        const data = await response.json()
        store.updateFromSSE(data)

        // If completed, fetch full result
        if (data.stage === 'completed') {
          stopPolling()
          await fetchFullResult(sessionId)
        }
      }
    } catch (e) {
      console.error('[DebugPage] Failed to poll status:', e)
    }
  }

  function stopPolling() {
    if (statusPollInterval) {
      clearInterval(statusPollInterval)
      statusPollInterval = null
    }
  }

  statusPollInterval = window.setInterval(pollStatus, 1000)
  pollStatus() // Immediate first poll
}

onMounted(() => {
  // Use URL session_id if available, otherwise fall back to meetingStore
  const initialSessionId = currentSessionId.value

  if (initialSessionId) {
    store.sessionId = initialSessionId
    startPolling(initialSessionId)
  }

  // Sync with meeting store if available
  if (meetingStore.chapters.length > 0) {
    store.setAnalysis({
      session_id: store.sessionId,
      theme: meetingStore.topic,
      topics: [],
      chapters: meetingStore.chapters,
      speaker_roles: [],
      summary: ''
    })
  }
})

async function fetchFullResult(sessionId: string) {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/upload/${sessionId}`)
    if (response.ok) {
      const data = await response.json()
      if (data.segments) {
        store.setTranscript({
          segments: data.segments,
          speaker_count: new Set(data.segments.map((s: any) => s.speaker)).size
        })
      }
      if (data.chapters) {
        store.setAnalysis(data)
      }
    }
  } catch (e) {
    console.error('[DebugPage] Failed to fetch full result:', e)
  }
}
</script>

<style scoped>
.debug-page {
  min-height: 100vh;
  background: #0d0d15;
  color: #ffffff;
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #1a1a24;
  border-bottom: 1px solid #2d2d3d;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.debug-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.session-badge {
  background: #262626;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-family: monospace;
}

.header-right {
  display: flex;
  gap: 12px;
}

.btn-link, .btn-refresh {
  padding: 8px 16px;
  background: transparent;
  color: #a1a1a1;
  border: 1px solid #3d3d4d;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-link:hover, .btn-refresh:hover {
  background: #262626;
  color: #ffffff;
}

.status-bar {
  display: flex;
  gap: 24px;
  padding: 12px 24px;
  background: #141420;
  border-bottom: 1px solid #2d2d3d;
  font-size: 14px;
}

.status-item {
  display: flex;
  gap: 8px;
}

.status-item.flex-1 {
  flex: 1;
}

.status-label {
  color: #a1a1a1;
}

.status-value {
  color: #ffffff;
  font-weight: 500;
}

.status-processing { color: #f59e0b; }
.status-complete { color: #22c55e; }
.status-error { color: #ef4444; }

.progress-bar-container {
  height: 3px;
  background: #262626;
}

.progress-bar {
  height: 100%;
  background: #6366f1;
  transition: width 0.3s;
}

.tab-bar {
  display: flex;
  gap: 4px;
  padding: 8px 24px;
  background: #1a1a24;
  border-bottom: 1px solid #2d2d3d;
}

.tab-btn {
  padding: 8px 16px;
  background: transparent;
  color: #a1a1a1;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  gap: 8px;
  align-items: center;
  transition: all 0.2s;
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
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 12px;
}

.debug-content {
  padding: 24px;
  overflow-y: auto;
  height: calc(100vh - 180px);
}

.json-viewer {
  font-size: 14px;
}

.json-section {
  margin-bottom: 24px;
}

.json-section h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #a1a1a1;
}

.json-pre {
  background: #141420;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 12px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.segment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.segment-item {
  background: #141420;
  padding: 12px;
  border-radius: 8px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.seg-time {
  color: #6366f1;
  font-family: monospace;
  font-size: 12px;
}

.seg-speaker {
  color: #22c55e;
  font-weight: 500;
}

.seg-text {
  color: #ffffff;
  flex: 1;
}

.analysis-section {
  margin-bottom: 24px;
}

.analysis-section h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #a1a1a1;
}

.analysis-section p {
  margin: 0;
  color: #ffffff;
  line-height: 1.6;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: #262626;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
}

.chapter-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chapter-item {
  background: #141420;
  border-radius: 8px;
  overflow: hidden;
}

.chapter-summary {
  padding: 12px 16px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #1a1a24;
}

.chapter-title {
  font-weight: 500;
}

.chapter-time {
  color: #6366f1;
  font-size: 12px;
  font-family: monospace;
}

.chapter-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chapter-subsection h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #a1a1a1;
}

.chapter-subsection p {
  margin: 0;
  color: #ffffff;
}

.speaker-summary, .decision-item, .action-item {
  background: #1a1a24;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 8px;
}

.speaker-name, .role-speaker {
  color: #22c55e;
  font-weight: 500;
}

.role-name {
  color: #ffffff;
}

.role-reasoning {
  color: #a1a1a1;
  font-size: 12px;
}

.timestamps {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.timestamp {
  background: #262626;
  padding: 2px 6px;
  border-radius: 2px;
  font-size: 11px;
  color: #6366f1;
  font-family: monospace;
}

.role-item {
  background: #141420;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 8px;
}

.graphrag-search {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}

.search-input {
  flex: 1;
  padding: 10px 16px;
  background: #141420;
  border: 1px solid #3d3d4d;
  border-radius: 4px;
  color: #ffffff;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #6366f1;
}

.btn-search, .btn-auto {
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-search {
  background: #6366f1;
  color: #ffffff;
  border: none;
}

.btn-search:hover {
  background: #5558e3;
}

.btn-auto {
  background: transparent;
  color: #a1a1a1;
  border: 1px solid #3d3d4d;
}

.btn-auto:hover {
  background: #262626;
  color: #ffffff;
}

.graphrag-result {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.answer-section h3, .sources-section h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #a1a1a1;
}

.answer-section p {
  margin: 0;
  background: #141420;
  padding: 16px;
  border-radius: 8px;
  line-height: 1.6;
}

.source-item {
  background: #141420;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
}

.source-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.source-id {
  color: #a1a1a1;
  font-size: 12px;
}

.source-score {
  color: #6366f1;
  font-size: 12px;
}

.source-chunk {
  margin: 0;
  color: #ffffff;
  font-size: 13px;
  line-height: 1.5;
}

.sse-log {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sse-item {
  background: #141420;
  padding: 12px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sse-time {
  color: #6366f1;
  font-size: 11px;
  font-family: monospace;
}

.sse-type {
  color: #22c55e;
  font-size: 12px;
  font-weight: 500;
}

.sse-data {
  margin: 0;
  font-size: 12px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
  color: #a1a1a1;
}

.empty-state {
  text-align: center;
  padding: 48px;
  color: #a1a1a1;
}

.empty-state p {
  margin: 0 0 8px 0;
}

.hint {
  font-size: 13px;
  color: #666;
}
</style>
