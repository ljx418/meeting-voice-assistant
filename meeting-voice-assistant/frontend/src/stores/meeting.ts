/**
 * 会议状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Participant,
  TranscriptSegment,
  MeetingStatus,
  StatusMessage,
  AnalysisResult,
  Chapter,
  TimeRange,
  SpeakerSummary,
  Decision,
  ActionItem,
} from '../api/types'

export type { Chapter, TimeRange, SpeakerSummary, Decision, ActionItem }

export interface Speaker {
  id: string
  name: string
  color: string
}

export interface UploadProgress {
  stage: 'idle' | 'uploading' | 'transcribing' | 'analyzing' | 'completed' | 'error'
  progress: number
  remaining_time?: number
  speaker_count?: number
  segment_count?: number
  message?: string
}

export interface UploadedFileItem {
  id: string
  name: string
  size: string
  topic: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  duration: string
  sessionId?: string
  progress?: number
  stage?: string
  message?: string
}

export interface SessionData {
  sessionId: string
  fileId: string
  fileName: string
  progress: number
  stage: string
  message: string
  chapters: Chapter[]
  segments: Array<{ text: string; speaker: string; start_time: number; end_time: number }>
  audioUrl: string
  theme: string
  topics: string[]
  speakerRoles: Array<{ speaker: string; role: string; reasoning: string }>
  speakers: Speaker[]
  decisions: Decision[]
  actionItems: ActionItem[]
}

export const useMeetingStore = defineStore('meeting', () => {
  // ============ 会议核心状态 ============
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

  const decisions = ref<Decision[]>([])
  const actionItems = ref<ActionItem[]>([])
  const speakers = ref<Speaker[]>([])

  // ============ 上传状态 ============
  const audioUrl = ref<string>('')
  const uploadProgress = ref<UploadProgress>({ stage: 'idle', progress: 0 })
  const uploadedFiles = ref<UploadedFileItem[]>([])

  // ============ Session 状态 (多文件支持) ============
  const sessionMap = ref<Map<string, SessionData>>(new Map())
  const activeSessionId = ref<string | null>(null)

  // ============ UI 状态 ============
  const selectedChapterId = ref<string | null>(null)

  // ============ 计算属性 ============
  const duration = computed(() => {
    if (!startTime.value) return 0
    const end = endTime.value || new Date()
    return Math.floor((end.getTime() - startTime.value.getTime()) / 1000)
  })

  const participantCount = computed(() => participants.value.length)
  const transcriptCount = computed(() => transcripts.value.length)

  const currentChapter = computed(() => {
    if (!selectedChapterId.value) return null
    return chapters.value.find(c => c.id === selectedChapterId.value) || null
  })

  const currentSegment = computed(() => {
    if (!selectedChapterId.value) return null
    const chapter = chapters.value.find(c => c.id === selectedChapterId.value)
    if (!chapter) return null
    return transcripts.value.filter(
      t => t.start_time >= chapter.start_time && t.start_time < chapter.end_time
    )
  })

  // ============ 会议核心 Actions ============
  function setTopic(newTopic: string) { topic.value = newTopic }
  function setMeetingId(id: string) { meetingId.value = id }

  function addParticipant(participant: Participant) {
    if (!participants.value.find((p) => p.id === participant.id)) {
      participants.value.push(participant)
    }
  }

  function updateParticipant(id: string, updates: Partial<Participant>) {
    const participant = participants.value.find((p) => p.id === id)
    if (participant) Object.assign(participant, updates)
  }

  function addTranscript(segment: TranscriptSegment) { transcripts.value.push(segment) }
  function clearTranscripts() { transcripts.value = [] }
  function setCurrentSpeaker(speaker: string | null) { currentSpeaker.value = speaker }

  function addChapter(chapter: Chapter) {
    if (chapters.value.length > 0) {
      chapters.value[chapters.value.length - 1].end_time = chapter.start_time
    }
    chapters.value.push(chapter)
  }

  function setChapters(newChapters: Chapter[]) { chapters.value = newChapters }

  function setStatus(newStatus: MeetingStatus) {
    status.value = newStatus
    if (newStatus === 'recording' && !startTime.value) startTime.value = new Date()
    else if (newStatus === 'ended') endTime.value = new Date()
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
    decisions.value = []
    actionItems.value = []
    speakers.value = []
    selectedChapterId.value = null
    uploadProgress.value = { stage: 'idle', progress: 0 }
    audioUrl.value = ''
  }

  function setProcessingStatus(s: StatusMessage['status'], message: string) {
    processingStatus.value = s
    processingMessage.value = message
    if (s === 'error') errorMessage.value = message
  }

  function setAnalysisResult(result: AnalysisResult) { analysisResult.value = result }
  function setError(message: string) {
    errorMessage.value = message
    processingStatus.value = 'error'
    processingMessage.value = message
  }
  function clearError() { errorMessage.value = null }
  function setDecisions(newDecisions: Decision[]) { decisions.value = newDecisions }
  function setActionItems(newActionItems: ActionItem[]) { actionItems.value = newActionItems }
  function setSpeakers(newSpeakers: Speaker[]) { speakers.value = newSpeakers }

  // ============ 上传 Actions ============
  function addUploadedFile(file: UploadedFileItem) { uploadedFiles.value.push(file) }

  function updateUploadedFile(id: string, updates: Partial<UploadedFileItem>) {
    const file = uploadedFiles.value.find(f => f.id === id)
    if (file) Object.assign(file, updates)
  }

  function removeUploadedFile(id: string) {
    const idx = uploadedFiles.value.findIndex(f => f.id === id)
    if (idx !== -1) uploadedFiles.value.splice(idx, 1)
  }

  function setAudioUrl(url: string) { audioUrl.value = url }
  function setUploadProgress(progress: UploadProgress) { uploadProgress.value = progress }
  function updateUploadProgress(updates: Partial<UploadProgress>) {
    Object.assign(uploadProgress.value, updates)
  }

  // ============ Session Actions (多文件支持) ============
  function setSessionData(sessionId: string, data: Partial<SessionData>) {
    const existing = sessionMap.value.get(sessionId)
    const merged: SessionData = {
      sessionId,
      fileId: '',
      fileName: '',
      progress: 0,
      stage: 'uploading',
      message: '',
      chapters: [],
      segments: [],
      audioUrl: '',
      theme: '',
      topics: [],
      speakerRoles: [],
      speakers: [],
      decisions: [],
      actionItems: [],
      ...(existing || {}),
      ...data,
    }
    const newMap = new Map(sessionMap.value)
    newMap.set(sessionId, merged)
    sessionMap.value = newMap
  }

  function getSessionData(sessionId: string): SessionData | undefined {
    return sessionMap.value.get(sessionId)
  }

  // 激活某个 session 并同步到全局状态（供 MeetingConsolePage 使用）
  function setActiveSession(sessionId: string | null) {
    activeSessionId.value = sessionId
    if (sessionId) {
      const data = sessionMap.value.get(sessionId)
      if (data) {
        chapters.value = data.chapters
        decisions.value = data.decisions
        actionItems.value = data.actionItems
        speakers.value = data.speakers
        audioUrl.value = data.audioUrl
        topic.value = data.theme
      }
    }
  }

  // ============ UI Actions ============
  function setSelectedChapterId(id: string | null) { selectedChapterId.value = id }

  return {
    meetingId, topic, participants, transcripts, chapters, currentSpeaker,
    status, startTime, endTime, processingStatus, processingMessage,
    analysisResult, errorMessage, decisions, actionItems, speakers,
    audioUrl, uploadProgress, uploadedFiles,
    sessionMap, activeSessionId,
    selectedChapterId,
    duration, participantCount, transcriptCount, currentChapter, currentSegment,
    setTopic, setMeetingId, addParticipant, updateParticipant, addTranscript,
    clearTranscripts, setCurrentSpeaker, addChapter, setChapters, setStatus,
    reset, setProcessingStatus, setAnalysisResult, setError, clearError,
    setDecisions, setActionItems, setSpeakers,
    addUploadedFile, updateUploadedFile, removeUploadedFile, setAudioUrl,
    setUploadProgress, updateUploadProgress,
    setSessionData, getSessionData, setActiveSession,
    setSelectedChapterId,
  }
})
