import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Segment {
  text: string
  speaker: string
  start_time: number
  end_time: number
}

export interface SourceTimestamp {
  start: number
  end: number
}

export interface SpeakerSummary {
  speaker: string
  summary: string
  source_timestamps: SourceTimestamp[]
}

export interface Decision {
  decision: string
  source_timestamps: SourceTimestamp[]
}

export interface ActionItem {
  todo: string
  source_timestamps: SourceTimestamp[]
}

export interface Chapter {
  id: string
  title: string
  start_time: number
  end_time: number
  speaker_summaries: SpeakerSummary[]
  summary: string
  decisions: Decision[]
  action_items: ActionItem[]
}

export interface AnalysisResult {
  session_id: string
  theme: string
  topics: string[]
  chapters: Chapter[]
  speaker_roles: Array<{ speaker: string; role: string; reasoning: string }>
  summary: string
}

export interface GraphRAGResult {
  query: string
  answer: string
  sources: Array<{
    doc_id: string
    chunk: string
    similarity: number
  }>
}

// SSE 状态消息类型
interface SSEStatusData {
  session_id?: string
  stage?: string
  progress?: number
  message?: string
  remaining_time_seconds?: number
  speaker_count?: number
  segment_count?: number
  type?: string
}

// Transcript 数据类型
interface TranscriptData {
  segments: Segment[]
  speaker_count: number
}

// SSE 消息历史项类型
interface SSEMessageItem {
  time: string
  type: string
  data: SSEStatusData | TranscriptData | AnalysisResult | GraphRAGResult
}

export const useDebugStore = defineStore('debug', () => {
  // Session state
  const sessionId = ref<string | null>(null)
  const stage = ref<string>('idle')
  const progress = ref<number>(0)
  const message = ref<string>('')
  const remainingTime = ref<number | null>(null)
  const speakerCount = ref<number>(0)
  const segmentCount = ref<number>(0)

  // Results
  const transcriptResult = ref<TranscriptData | null>(null)
  const analysisResult = ref<AnalysisResult | null>(null)
  const graphragResult = ref<GraphRAGResult | null>(null)

  // SSE history
  const sseMessages = ref<SSEMessageItem[]>([])

  // Computed
  const isProcessing = computed(() => ['transcribing', 'analyzing'].includes(stage.value))
  const isComplete = computed(() => stage.value === 'completed')
  const isError = computed(() => stage.value === 'error')

  // Actions
  function updateFromSSE(data: SSEStatusData) {
    if (data.session_id) sessionId.value = data.session_id
    if (data.stage) stage.value = data.stage
    if (data.progress !== undefined) progress.value = data.progress
    if (data.message) message.value = data.message
    if (data.remaining_time_seconds !== undefined) remainingTime.value = data.remaining_time_seconds
    if (data.speaker_count !== undefined) speakerCount.value = data.speaker_count
    if (data.segment_count !== undefined) segmentCount.value = data.segment_count

    // Log SSE message
    sseMessages.value.push({
      time: new Date().toLocaleTimeString(),
      type: data.type || 'status',
      data: data
    })
  }

  function setTranscript(data: TranscriptData) {
    transcriptResult.value = data
    sseMessages.value.push({
      time: new Date().toLocaleTimeString(),
      type: 'transcript',
      data: data
    })
  }

  function setAnalysis(data: AnalysisResult) {
    analysisResult.value = data
    sseMessages.value.push({
      time: new Date().toLocaleTimeString(),
      type: 'analysis',
      data: data
    })
  }

  function setGraphRAG(data: GraphRAGResult) {
    graphragResult.value = data
  }

  function reset() {
    sessionId.value = null
    stage.value = 'idle'
    progress.value = 0
    message.value = ''
    remainingTime.value = null
    speakerCount.value = 0
    segmentCount.value = 0
    transcriptResult.value = null
    analysisResult.value = null
    graphragResult.value = null
    sseMessages.value = []
  }

  return {
    // State
    sessionId,
    stage,
    progress,
    message,
    remainingTime,
    speakerCount,
    segmentCount,
    transcriptResult,
    analysisResult,
    graphragResult,
    sseMessages,
    // Computed
    isProcessing,
    isComplete,
    isError,
    // Actions
    updateFromSSE,
    setTranscript,
    setAnalysis,
    setGraphRAG,
    reset
  }
})
