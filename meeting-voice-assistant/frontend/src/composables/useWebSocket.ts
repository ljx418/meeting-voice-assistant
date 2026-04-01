/**
 * WebSocket Composable
 */

import { ref, readonly, onUnmounted } from 'vue'
import { VoiceWSClient } from '../api/websocket'
import type { TranscriptData, MeetingInfoMessage, StatusMessage, AnalysisResult } from '../api/types'

export function useWebSocket() {
  const isConnected = ref(false)
  const sessionId = ref<string | null>(null)
  const lastTranscript = ref<TranscriptData | null>(null)
  const meetingInfo = ref<MeetingInfoMessage['data'] | null>(null)
  const error = ref<Error | null>(null)
  const processingStatus = ref<StatusMessage['status'] | null>(null)
  const processingMessage = ref<string>('')
  const analysisResult = ref<AnalysisResult | null>(null)

  const client = new VoiceWSClient()

  // 注册错误回调
  client.onError((err) => {
    error.value = err
    isConnected.value = false
  })

  // 注册结果回调
  client.onResult((data) => {
    lastTranscript.value = data
  })

  // 注册状态回调
  client.onStatus((data) => {
    processingStatus.value = data.status
    processingMessage.value = data.message
    if (data.status === 'completed' || data.status === 'error') {
      // 处理完成后延迟清除状态
      setTimeout(() => {
        if (processingStatus.value === data.status) {
          processingStatus.value = null
          processingMessage.value = ''
        }
      }, 5000)
    }
  })

  // 注册分析结果回调
  client.onAnalysisResult((data) => {
    analysisResult.value = data
  })

  /**
   * 设置分析结果（用于文件上传等外部来源）
   */
  function setAnalysisResult(result: AnalysisResult) {
    analysisResult.value = result
  }

  /**
   * 连接服务器
   */
  async function connect(): Promise<void> {
    try {
      error.value = null
      // 直接调用 connect，它内部会处理 welcome 回调
      await client.connect()
      // 连接成功后更新状态
      isConnected.value = true
      sessionId.value = client.currentSessionId
    } catch (err) {
      error.value = err as Error
      isConnected.value = false
      throw err
    }
  }

  /**
   * 断开连接
   */
  function disconnect(): void {
    client.disconnect()
    isConnected.value = false
    sessionId.value = null
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected: readonly(isConnected),
    sessionId: readonly(sessionId),
    lastTranscript: readonly(lastTranscript),
    meetingInfo: readonly(meetingInfo),
    error: readonly(error),
    processingStatus: readonly(processingStatus),
    processingMessage: readonly(processingMessage),
    analysisResult: readonly(analysisResult),
    setAnalysisResult,
    client,
    connect,
    disconnect,
  }
}
