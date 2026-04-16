/**
 * 会议状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Participant,
  TranscriptSegment,
  Chapter,
  MeetingStatus,
  StatusMessage,
  AnalysisResult,
} from '../api/types'

// 时间范围
export interface TimeRange {
  start: number
  end: number
}

// 说话人总结
export interface SpeakerSummary {
  speaker: string
  summary: string
  source_timestamps: TimeRange[]
}

// 决策
export interface Decision {
  decision: string
  source_timestamps: TimeRange[]
}

// 行动项
export interface ActionItem {
  todo: string
  source_timestamps: TimeRange[]
}

// 说话人
export interface Speaker {
  id: string
  name: string
  color: string
}

// 上传进度
export interface UploadProgress {
  stage: 'idle' | 'uploading' | 'transcribing' | 'analyzing' | 'completed' | 'error'
  progress: number  // 0-100
  remaining_time?: number  // 秒
  speaker_count?: number
  segment_count?: number
  message?: string
}

// 段落（章节）
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

// 段落计算属性接口
export interface ChapterComputed {
  id: string
  title: string
  start_time: number
  end_time: number
  speaker_summaries: SpeakerSummary[]
  summary: string
  decisions: Decision[]
  action_items: ActionItem[]
  duration: number
}

export const useMeetingStore = defineStore('meeting', () => {
  // 状态
  const meetingId = ref('')
  const topic = ref('')
  const participants = ref<Participant[]>([])
  const transcripts = ref<TranscriptSegment[]>([])
  const chapters = ref<Chapter[]>([])
  const currentSpeaker = ref<string | null>(null)
  const status = ref<MeetingStatus>('idle')
  const startTime = ref<Date | null>(null)
  const endTime = ref<Date | null>(null)
  const processingStatus = ref<StatusMessage['status'] | null>(null)
  const processingMessage = ref<string>('')
  const analysisResult = ref<AnalysisResult | null>(null)
  const errorMessage = ref<string | null>(null)

  // 新增状态
  const selectedChapterId = ref<string | null>(null)
  const decisions = ref<Decision[]>([])
  const actionItems = ref<ActionItem[]>([])
  const speakers = ref<Speaker[]>([])
  const audioUrl = ref<string>('')
  const uploadProgress = ref<UploadProgress>({
    stage: 'idle',
    progress: 0,
  })

  // 上传文件列表（持久化）
  interface UploadedFileItem {
    id: string
    name: string
    size: string
    topic: string
    status: 'pending' | 'processing' | 'completed'
    duration: string
  }
  const uploadedFiles = ref<UploadedFileItem[]>([])

  function addUploadedFile(file: UploadedFileItem) {
    uploadedFiles.value.push(file)
  }

  function updateUploadedFile(id: string, updates: Partial<UploadedFileItem>) {
    const file = uploadedFiles.value.find(f => f.id === id)
    if (file) Object.assign(file, updates)
  }

  function removeUploadedFile(id: string) {
    const idx = uploadedFiles.value.findIndex(f => f.id === id)
    if (idx !== -1) uploadedFiles.value.splice(idx, 1)
  }

  // 计算属性
  const duration = computed(() => {
    if (!startTime.value) return 0
    const end = endTime.value || new Date()
    return Math.floor((end.getTime() - startTime.value.getTime()) / 1000)
  })

  const participantCount = computed(() => participants.value.length)

  const transcriptCount = computed(() => transcripts.value.length)

  // 当前段落
  const currentChapter = computed(() => {
    if (!selectedChapterId.value) return null
    return chapters.value.find(c => c.id === selectedChapterId.value) || null
  })

  // 当前片段（基于 selectedChapterId 查找对应的转写片段）
  const currentSegment = computed(() => {
    if (!selectedChapterId.value) return null
    const chapter = chapters.value.find(c => c.id === selectedChapterId.value)
    if (!chapter) return null
    // 找到在当前章节时间范围内的转写片段
    return transcripts.value.filter(
      t => t.start_time >= chapter.start_time && t.start_time < chapter.end_time
    )
  })

  // Actions
  function setTopic(newTopic: string) {
    topic.value = newTopic
  }

  function setMeetingId(id: string) {
    meetingId.value = id
  }

  function addParticipant(participant: Participant) {
    if (!participants.value.find((p) => p.id === participant.id)) {
      participants.value.push(participant)
    }
  }

  function updateParticipant(id: string, updates: Partial<Participant>) {
    const participant = participants.value.find((p) => p.id === id)
    if (participant) {
      Object.assign(participant, updates)
    }
  }

  function addTranscript(segment: TranscriptSegment) {
    transcripts.value.push(segment)
  }

  function clearTranscripts() {
    transcripts.value = []
  }

  function setCurrentSpeaker(speaker: string | null) {
    currentSpeaker.value = speaker
  }

  function addChapter(chapter: Chapter) {
    // 结束上一个章节
    if (chapters.value.length > 0) {
      const lastChapter = chapters.value[chapters.value.length - 1]
      lastChapter.end_time = chapter.start_time
    }
    chapters.value.push(chapter)
  }

  function setChapters(newChapters: Chapter[]) {
    chapters.value = newChapters
  }

  function setStatus(newStatus: MeetingStatus) {
    status.value = newStatus

    if (newStatus === 'recording' && !startTime.value) {
      startTime.value = new Date()
    } else if (newStatus === 'ended') {
      endTime.value = new Date()
    }
  }

  function reset() {
    meetingId.value = ''
    topic.value = ''
    participants.value = []
    transcripts.value = []
    chapters.value = []
    currentSpeaker.value = null
    status.value = 'idle'
    startTime.value = null
    endTime.value = null
    processingStatus.value = null
    processingMessage.value = ''
    analysisResult.value = null
    errorMessage.value = null
    selectedChapterId.value = null
    decisions.value = []
    actionItems.value = []
    speakers.value = []
    uploadProgress.value = { stage: 'idle', progress: 0 }
  }

  function setProcessingStatus(status: StatusMessage['status'], message: string) {
    processingStatus.value = status
    processingMessage.value = message
    if (status === 'error') {
      errorMessage.value = message
    }
  }

  function setAnalysisResult(result: AnalysisResult) {
    analysisResult.value = result
  }

  function setError(message: string) {
    errorMessage.value = message
    processingStatus.value = 'error'
    processingMessage.value = message
  }

  function clearError() {
    errorMessage.value = null
  }

  // 新增 Actions
  function setSelectedChapterId(id: string | null) {
    selectedChapterId.value = id
  }

  function setDecisions(newDecisions: Decision[]) {
    decisions.value = newDecisions
  }

  function setActionItems(newActionItems: ActionItem[]) {
    actionItems.value = newActionItems
  }

  function setSpeakers(newSpeakers: Speaker[]) {
    speakers.value = newSpeakers
  }

  function setAudioUrl(url: string) {
    audioUrl.value = url
  }

  function setUploadProgress(progress: UploadProgress) {
    uploadProgress.value = progress
  }

  function updateUploadProgress(updates: Partial<UploadProgress>) {
    Object.assign(uploadProgress.value, updates)
  }

  return {
    // 状态
    meetingId,
    topic,
    participants,
    transcripts,
    chapters,
    currentSpeaker,
    status,
    startTime,
    endTime,
    processingStatus,
    processingMessage,
    analysisResult,
    errorMessage,
    selectedChapterId,
    decisions,
    actionItems,
    speakers,
    audioUrl,
    uploadProgress,
    uploadedFiles,

    // 计算属性
    duration,
    participantCount,
    transcriptCount,
    currentChapter,
    currentSegment,

    // Actions
    setTopic,
    setMeetingId,
    addParticipant,
    updateParticipant,
    addTranscript,
    clearTranscripts,
    setCurrentSpeaker,
    addChapter,
    setChapters,
    setStatus,
    reset,
    setProcessingStatus,
    setAnalysisResult,
    setError,
    clearError,
    setSelectedChapterId,
    setDecisions,
    setActionItems,
    setSpeakers,
    setAudioUrl,
    setUploadProgress,
    updateUploadProgress,
    addUploadedFile,
    updateUploadedFile,
    removeUploadedFile,
  }
})
