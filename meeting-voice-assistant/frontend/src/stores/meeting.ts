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

  // 计算属性
  const duration = computed(() => {
    if (!startTime.value) return 0
    const end = endTime.value || new Date()
    return Math.floor((end.getTime() - startTime.value.getTime()) / 1000)
  })

  const participantCount = computed(() => participants.value.length)

  const transcriptCount = computed(() => transcripts.value.length)

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

    // 计算属性
    duration,
    participantCount,
    transcriptCount,

    // Actions
    setTopic,
    setMeetingId,
    addParticipant,
    updateParticipant,
    addTranscript,
    clearTranscripts,
    setCurrentSpeaker,
    addChapter,
    setStatus,
    reset,
    setProcessingStatus,
    setAnalysisResult,
    setError,
    clearError,
  }
})
