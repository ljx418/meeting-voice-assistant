/**
 * useWebSocket Composable 单元测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Create mock client instance
const createMockClient = () => ({
  connect: vi.fn().mockResolvedValue(undefined),
  disconnect: vi.fn(),
  start: vi.fn(),
  stop: vi.fn(),
  pause: vi.fn(),
  resume: vi.fn(),
  sendAudio: vi.fn(),
  isConnected: true,
  currentSessionId: 'test-session-123',
  onError: vi.fn(),
  onResult: vi.fn(),
  onStatus: vi.fn(),
  onAnalysisResult: vi.fn(),
})

// Mock the websocket module before importing useWebSocket
vi.mock('../api/websocket', () => {
  const MockVoiceWSClient = function(this: any) {
    return createMockClient.call(this)
  }
  return {
    VoiceWSClient: MockVoiceWSClient,
  }
})

import { useWebSocket } from './useWebSocket'
import { VoiceWSClient } from '../api/websocket'

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      const ws = useWebSocket()
      expect(ws.isConnected.value).toBe(false)
      expect(ws.sessionId.value).toBeNull()
      expect(ws.lastTranscript.value).toBeNull()
      expect(ws.error.value).toBeNull()
      expect(ws.processingStatus.value).toBeNull()
      expect(ws.processingMessage.value).toBe('')
      expect(ws.analysisResult.value).toBeNull()
    })
  })

  describe('connect', () => {
    it('应该建立连接并更新状态', async () => {
      const ws = useWebSocket()
      await ws.connect()
      expect(ws.isConnected.value).toBe(true)
      expect(ws.sessionId.value).toBe('test-session-123')
    })
  })

  describe('disconnect', () => {
    it('应该断开连接并重置状态', async () => {
      const ws = useWebSocket()
      await ws.connect()
      ws.disconnect()
      expect(ws.isConnected.value).toBe(false)
      expect(ws.sessionId.value).toBeNull()
    })
  })

  describe('client', () => {
    it('应该返回 VoiceWSClient 实例', () => {
      const ws = useWebSocket()
      expect(ws.client).toBeDefined()
    })
  })

  describe('setAnalysisResult', () => {
    it('应该设置分析结果', () => {
      const ws = useWebSocket()
      const result = {
        summary: '测试总结',
        key_points: ['要点1'],
        action_items: ['行动项1'],
        topics: ['主题1'],
      }
      ws.setAnalysisResult(result)
      expect(ws.analysisResult.value).toEqual(result)
    })
  })
})
