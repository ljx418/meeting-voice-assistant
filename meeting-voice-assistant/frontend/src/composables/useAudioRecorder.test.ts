/**
 * useAudioRecorder Composable 单元测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock audio objects
const mockAnalyser = {
  fftSize: 256,
  frequencyBinCount: 128,
  getByteFrequencyData: vi.fn(),
}

const mockAudioContextInstance = {
  state: 'running',
  createMediaStreamSource: vi.fn().mockReturnValue({
    connect: vi.fn(),
  }),
  createAnalyser: vi.fn().mockReturnValue(mockAnalyser),
  close: vi.fn(),
  resume: vi.fn().mockResolvedValue(undefined),
  sampleRate: 16000,
}

const mockStreamTrack = { stop: vi.fn() }
const mockMediaStream = {
  getTracks: vi.fn().mockReturnValue([mockStreamTrack]),
}

const mockMediaRecorderInstance = {
  start: vi.fn(),
  stop: vi.fn(),
  pause: vi.fn(),
  resume: vi.fn(),
  requestData: vi.fn(),
  state: 'inactive',
  ondataavailable: null as ((event: { data: { size: number; arrayBuffer: () => Promise<ArrayBuffer> } }) => void) | null,
}

// Mock WebSocket client
const mockWsClient = {
  start: vi.fn(),
  stop: vi.fn(),
  pause: vi.fn(),
  resume: vi.fn(),
  sendAudio: vi.fn(),
  isConnected: true,
}

describe('useAudioRecorder', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    // Setup global mocks with proper constructor behavior
    vi.stubGlobal('navigator', {
      mediaDevices: {
        getUserMedia: vi.fn().mockResolvedValue(mockMediaStream),
      },
    })

    // AudioContext constructor mock
    const MockAudioContext = function(this: any) {
      return mockAudioContextInstance
    }
    vi.stubGlobal('AudioContext', MockAudioContext)

    // MediaRecorder constructor mock
    const MockMediaRecorder = function(this: any, _stream: any, _options?: any) {
      return mockMediaRecorderInstance
    }
    vi.stubGlobal('MediaRecorder', MockMediaRecorder)

    vi.stubGlobal('requestAnimationFrame', vi.fn((cb: () => void) => {
      // Don't immediately call to avoid infinite loop
      return 1
    }))
    vi.stubGlobal('setTimeout', vi.fn((fn: () => void) => fn() as unknown as number))
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('初始状态', () => {
    it('应该有正确的初始状态', async () => {
      const { useAudioRecorder } = await import('./useAudioRecorder')
      const recorder = useAudioRecorder(mockWsClient as any)
      expect(recorder.isRecording.value).toBe(false)
      expect(recorder.isPaused.value).toBe(false)
      expect(recorder.audioLevel.value).toBe(0)
      expect(recorder.audioWaveform.value).toEqual([])
      expect(recorder.recordingDuration.value).toBe(0)
    })
  })

  describe('startRecording', () => {
    it('应该请求麦克风权限', async () => {
      const { useAudioRecorder } = await import('./useAudioRecorder')
      const recorder = useAudioRecorder(mockWsClient as any)
      await recorder.startRecording()
      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
        },
      })
    })

    it('麦克风权限被拒绝时应该抛出错误', async () => {
      const { useAudioRecorder } = await import('./useAudioRecorder')
      ;(navigator.mediaDevices.getUserMedia as any).mockRejectedValue(new Error('Permission denied'))
      const recorder = useAudioRecorder(mockWsClient as any)
      await expect(recorder.startRecording()).rejects.toThrow('Permission denied')
    })
  })
})

describe('useAudioRecorder - Audio Level Monitoring', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    vi.stubGlobal('navigator', {
      mediaDevices: {
        getUserMedia: vi.fn().mockResolvedValue(mockMediaStream),
      },
    })

    const MockAudioContext = function(this: any) {
      return mockAudioContextInstance
    }
    vi.stubGlobal('AudioContext', MockAudioContext)

    const MockMediaRecorder = function(this: any, _stream: any, _options?: any) {
      return mockMediaRecorderInstance
    }
    vi.stubGlobal('MediaRecorder', MockMediaRecorder)

    vi.stubGlobal('requestAnimationFrame', vi.fn((cb: () => void) => {
      // Don't immediately call to avoid infinite loop
      return 1
    }))
    vi.stubGlobal('setTimeout', vi.fn((fn: () => void) => fn() as unknown as number))
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('audioLevel 应该在录音时更新', async () => {
    const { useAudioRecorder } = await import('./useAudioRecorder')
    const recorder = useAudioRecorder(mockWsClient as any)
    mockMediaRecorderInstance.ondataavailable = vi.fn()
    await recorder.startRecording()
    expect(typeof recorder.audioLevel.value).toBe('number')
    expect(recorder.audioLevel.value).toBeGreaterThanOrEqual(0)
  })
})
