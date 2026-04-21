/**
 * Meeting Store 单元测试
 */

import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMeetingStore } from './meeting'
import type { TranscriptSegment, Chapter, Participant } from '../api/types'

describe('Meeting Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('状态初始化', () => {
    it('应该有正确的初始状态', () => {
      const store = useMeetingStore()
      expect(store.meetingId).toBe('')
      expect(store.topic).toBe('')
      expect(store.participants).toEqual([])
      expect(store.transcripts).toEqual([])
      expect(store.chapters).toEqual([])
      expect(store.status).toBe('idle')
      expect(store.startTime).toBeNull()
      expect(store.endTime).toBeNull()
      expect(store.processingStatus).toBeNull()
      expect(store.analysisResult).toBeNull()
      expect(store.errorMessage).toBeNull()
    })
  })

  describe('setTopic', () => {
    it('应该设置会议主题', () => {
      const store = useMeetingStore()
      store.setTopic('产品需求评审')
      expect(store.topic).toBe('产品需求评审')
    })
  })

  describe('setMeetingId', () => {
    it('应该设置会议ID', () => {
      const store = useMeetingStore()
      store.setMeetingId('meeting-123')
      expect(store.meetingId).toBe('meeting-123')
    })
  })

  describe('addParticipant', () => {
    it('应该添加参会者', () => {
      const store = useMeetingStore()
      const participant: Participant = {
        id: 'p1',
        name: '张三',
        role: 'host',
      }
      store.addParticipant(participant)
      expect(store.participants).toHaveLength(1)
      expect(store.participants[0].name).toBe('张三')
    })

    it('不应该添加重复ID的参会者', () => {
      const store = useMeetingStore()
      const participant1: Participant = { id: 'p1', name: '张三' }
      const participant2: Participant = { id: 'p1', name: '李四' }
      store.addParticipant(participant1)
      store.addParticipant(participant2)
      expect(store.participants).toHaveLength(1)
      expect(store.participants[0].name).toBe('张三')
    })
  })

  describe('updateParticipant', () => {
    it('应该更新参会者信息', () => {
      const store = useMeetingStore()
      const participant: Participant = { id: 'p1', name: '张三' }
      store.addParticipant(participant)
      store.updateParticipant('p1', { name: '张三（主持人）', role: 'host' })
      expect(store.participants[0].name).toBe('张三（主持人）')
      expect(store.participants[0].role).toBe('host')
    })
  })

  describe('transcripts', () => {
    it('应该添加转写片段', () => {
      const store = useMeetingStore()
      const segment: TranscriptSegment = {
        id: 't1',
        text: '大家好',
        start_time: 0,
        end_time: 2,
        confidence: 0.95,
      }
      store.addTranscript(segment)
      expect(store.transcripts).toHaveLength(1)
      expect(store.transcripts[0].text).toBe('大家好')
    })

    it('clearTranscripts 应该清空所有转写', () => {
      const store = useMeetingStore()
      const segment: TranscriptSegment = {
        id: 't1',
        text: '测试',
        start_time: 0,
        end_time: 1,
        confidence: 0.9,
      }
      store.addTranscript(segment)
      store.clearTranscripts()
      expect(store.transcripts).toHaveLength(0)
    })
  })

  describe('chapters', () => {
    it('addChapter 应该添加章节并结束上一个章节', () => {
      const store = useMeetingStore()
      const chapter1: Chapter = {
        id: 'c1',
        title: '开场',
        start_time: 0,
        end_time: 0,
        speaker_summaries: [],
        summary: '',
        decisions: [],
        action_items: [],
      }
      const chapter2: Chapter = {
        id: 'c2',
        title: '讨论',
        start_time: 300,
        end_time: 0,
        speaker_summaries: [],
        summary: '',
        decisions: [],
        action_items: [],
      }
      store.addChapter(chapter1)
      store.addChapter(chapter2)
      expect(store.chapters).toHaveLength(2)
      expect(store.chapters[0].end_time).toBe(300)
      expect(store.chapters[1].end_time).toBe(0)
    })
  })

  describe('status 状态管理', () => {
    it('setStatus 应该更新状态', () => {
      const store = useMeetingStore()
      store.setStatus('recording')
      expect(store.status).toBe('recording')
      expect(store.startTime).toBeInstanceOf(Date)
    })

    it('设置为 ended 时应该设置 endTime', () => {
      const store = useMeetingStore()
      store.setStatus('recording')
      store.setStatus('ended')
      expect(store.status).toBe('ended')
      expect(store.endTime).toBeInstanceOf(Date)
    })
  })

  describe('processingStatus', () => {
    it('setProcessingStatus 应该更新处理状态', () => {
      const store = useMeetingStore()
      store.setProcessingStatus('processing', '正在处理音频...')
      expect(store.processingStatus).toBe('processing')
      expect(store.processingMessage).toBe('正在处理音频...')
    })

    it('状态为 error 时应该设置 errorMessage', () => {
      const store = useMeetingStore()
      store.setProcessingStatus('error', '处理失败')
      expect(store.processingStatus).toBe('error')
      expect(store.errorMessage).toBe('处理失败')
    })
  })

  describe('analysisResult', () => {
    it('setAnalysisResult 应该设置分析结果', () => {
      const store = useMeetingStore()
      const result = {
        summary: '会议讨论了产品需求',
        key_points: ['需求明确', '分工清晰'],
        action_items: ['周三前完成设计稿'],
        topics: ['产品需求'],
      }
      store.setAnalysisResult(result)
      expect(store.analysisResult).toEqual(result)
      expect(store.analysisResult?.summary).toBe('会议讨论了产品需求')
    })
  })

  describe('reset', () => {
    it('应该重置所有状态', () => {
      const store = useMeetingStore()
      store.setTopic('测试主题')
      store.setMeetingId('meeting-1')
      store.setStatus('recording')
      store.reset()
      expect(store.topic).toBe('')
      expect(store.meetingId).toBe('')
      expect(store.status).toBe('idle')
      expect(store.startTime).toBeNull()
    })
  })

  describe('uploadedFiles', () => {
    it('addUploadedFile 应该添加文件', () => {
      const store = useMeetingStore()
      store.addUploadedFile({
        id: 'f1',
        name: 'meeting.mp3',
        size: '10MB',
        topic: '测试',
        status: 'pending',
        duration: '10:00',
      })
      expect(store.uploadedFiles).toHaveLength(1)
    })

    it('updateUploadedFile 应该更新文件', () => {
      const store = useMeetingStore()
      store.addUploadedFile({
        id: 'f1',
        name: 'meeting.mp3',
        size: '10MB',
        topic: '测试',
        status: 'pending',
        duration: '10:00',
      })
      store.updateUploadedFile('f1', { status: 'completed' })
      expect(store.uploadedFiles[0].status).toBe('completed')
    })

    it('removeUploadedFile 应该删除文件', () => {
      const store = useMeetingStore()
      store.addUploadedFile({
        id: 'f1',
        name: 'meeting.mp3',
        size: '10MB',
        topic: '测试',
        status: 'pending',
        duration: '10:00',
      })
      store.removeUploadedFile('f1')
      expect(store.uploadedFiles).toHaveLength(0)
    })
  })

  describe('计算属性', () => {
    it('participantCount 应该返回参会者数量', () => {
      const store = useMeetingStore()
      store.addParticipant({ id: 'p1', name: '张三' })
      store.addParticipant({ id: 'p2', name: '李四' })
      expect(store.participantCount).toBe(2)
    })

    it('transcriptCount 应该返回转写片段数量', () => {
      const store = useMeetingStore()
      store.addTranscript({ id: 't1', text: '测试1', start_time: 0, end_time: 1, confidence: 0.9 })
      store.addTranscript({ id: 't2', text: '测试2', start_time: 1, end_time: 2, confidence: 0.9 })
      expect(store.transcriptCount).toBe(2)
    })

    it('duration 应该计算会议时长', () => {
      const store = useMeetingStore()
      store.setStatus('recording')
      // startTime 已设置，duration 应该是正数
      expect(typeof store.duration).toBe('number')
      expect(store.duration).toBeGreaterThanOrEqual(0)
    })
  })
})
