/**
 * WebSocket 客户端 - 负责与后端建立连接并传输语音流
 */

import type {
  AudioConfig,
  ControlMessage,
  TranscriptData,
  StatusMessage,
  ProcessingMessage,
  AnalysisResult,
} from './types'

type StatusHandler = (data: StatusMessage) => void
type ProcessingHandler = (data: ProcessingMessage) => void
type AnalysisResultHandler = (data: AnalysisResult) => void

type MessageHandler = (data: TranscriptData) => void
type ErrorHandler = (error: Error) => void
type WelcomeHandler = (sessionId: string, config: AudioConfig) => void

export class VoiceWSClient {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private heartbeatTimer: number | null = null
  private sessionId: string | null = null
  private config: AudioConfig | null = null

  private onWelcomeHandlers: WelcomeHandler[] = []
  private onResultCallback: MessageHandler | null = null
  private onErrorCallback: ErrorHandler | null = null
  private onStatusCallback: StatusHandler | null = null
  private onProcessingCallback: ProcessingHandler | null = null
  private onAnalysisResultCallback: AnalysisResultHandler | null = null

  constructor(url: string = 'ws://localhost:8000/api/v1/ws/voice') {
    this.url = url
    console.log('[WS] WebSocket URL:', this.url)
  }

  /**
   * 连接到 WebSocket 服务器
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      console.log(`[WS] Connecting to ${this.url}`)

      // 如果已有连接，先关闭
      if (this.ws) {
        console.log('[WS] Closing existing connection')
        this.ws.close()
        this.ws = null
      }

      this.ws = new WebSocket(this.url)
      this.ws.binaryType = 'arraybuffer'

      this.ws.onopen = () => {
        console.log('[WS] Connection opened')
        this.reconnectAttempts = 0
        this.startHeartbeat()
      }

      this.ws.onmessage = (event) => {
        this.handleMessage(event)
      }

      this.ws.onerror = (error) => {
        console.error('[WS] WebSocket error:', error)
        this.onErrorCallback?.(new Error('WebSocket connection failed'))
      }

      this.ws.onclose = (event) => {
        console.log('[WS] Connection closed', event.code, event.reason)
        this.stopHeartbeat()
        // 非正常关闭时自动重连（1000 为正常关闭）
        if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.handleReconnect()
        }
      }

      // 注册 welcome 回调，同时解决 Promise
      this.onWelcomeHandlers.push((sessionId, config) => {
        console.log(`[WS] Welcome received: session_id=${sessionId}`)
        resolve()
      })

      // 设置超时
      setTimeout(() => {
        if (!this.sessionId) {
          console.error('[WS] Connection timeout')
          reject(new Error('Connection timeout'))
          this.disconnect()
        }
      }, 10000)
    })
  }

  /**
   * 处理接收到的消息
   */
  private handleMessage(event: MessageEvent) {
    if (typeof event.data === 'string') {
      try {
        const msg = JSON.parse(event.data)
        console.log('[WS] Received message type:', msg.type)

        switch (msg.type) {
          case 'welcome':
            this.sessionId = msg.session_id
            this.config = msg.config
            // 调用所有 welcome 处理器
            this.onWelcomeHandlers.forEach(handler => handler(this.sessionId!, this.config!))
            break

          case 'transcript':
            this.onResultCallback?.(msg.data as TranscriptData)
            break

          case 'meeting_info':
            // TODO: 触发 meeting_info 回调
            console.log('[WS] Meeting info:', msg.data)
            break

          case 'ack':
            console.log(`[WS] ACK: ${msg.action} - ${msg.message}`)
            break

          case 'error':
            console.error(`[WS] Server error: ${msg.code} - ${msg.message}`)
            this.onErrorCallback?.(new Error(`${msg.code}: ${msg.message}`))
            break

          case 'status':
            console.log(`[WS] Status: ${msg.status} - ${msg.message}`)
            this.onStatusCallback?.(msg as StatusMessage)
            break

          case 'processing':
            console.log(`[WS] Processing: ${msg.stage} - ${msg.message}`)
            this.onProcessingCallback?.(msg as ProcessingMessage)
            break

          case 'analysis_result':
            console.log('[WS] Analysis result received')
            this.onAnalysisResultCallback?.(msg.data as AnalysisResult)
            break
        }
      } catch (e) {
        console.error('[WS] Failed to parse message:', e)
      }
    } else if (event.data instanceof ArrayBuffer) {
      console.log(`[WS] Received audio data: ${event.data.byteLength} bytes`)
    }
  }

  /**
   * 发送控制消息
   */
  sendControl(action: ControlMessage['action'], metadata?: ControlMessage['metadata']): void {
    console.log('[WS] sendControl called, action:', action, 'ws.readyState:', this.ws?.readyState)
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('[WS] Cannot send control: not connected, readyState:', this.ws?.readyState)
      return
    }

    const msg: ControlMessage = {
      type: 'control',
      action,
      metadata,
    }

    this.ws.send(JSON.stringify(msg))
    console.log(`[WS] Sent control: ${action}, message:`, JSON.stringify(msg))
  }

  /**
   * 发送音频数据
   */
  sendAudio(frame: ArrayBuffer): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('[WS] Cannot send audio: not connected')
      return
    }

    this.ws.send(frame)
  }

  /**
   * 注册结果回调
   */
  onResult(callback: MessageHandler): void {
    this.onResultCallback = callback
  }

  /**
   * 注册错误回调
   */
  onError(callback: ErrorHandler): void {
    this.onErrorCallback = callback
  }

  /**
   * 注册状态回调
   */
  onStatus(callback: StatusHandler): void {
    this.onStatusCallback = callback
  }

  /**
   * 注册处理中回调
   */
  onProcessing(callback: ProcessingHandler): void {
    this.onProcessingCallback = callback
  }

  /**
   * 注册分析结果回调
   */
  onAnalysisResult(callback: AnalysisResultHandler): void {
    this.onAnalysisResultCallback = callback
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.sessionId = null
    this.config = null
    this.onWelcomeHandlers = []
  }

  /**
   * 开始录音
   */
  start(metadata?: ControlMessage['metadata']): void {
    this.sendControl('start', metadata)
  }

  /**
   * 停止录音
   */
  stop(): void {
    this.sendControl('stop')
  }

  /**
   * 暂停录音
   */
  pause(): void {
    this.sendControl('pause')
  }

  /**
   * 恢复录音
   */
  resume(): void {
    this.sendControl('resume')
  }

  /**
   * 启动心跳
   */
  private startHeartbeat(): void {
    // WebSocket 不需要手动心跳
  }

  /**
   * 停止心跳
   */
  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * 处理重连
   */
  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WS] Max reconnection attempts reached')
      this.onErrorCallback?.(new Error('Max reconnection attempts reached'))
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)

    setTimeout(() => {
      this.connect().catch((err) => {
        console.error('[WS] Reconnection failed:', err)
      })
    }, delay)
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  get currentSessionId(): string | null {
    return this.sessionId
  }

  get currentConfig(): AudioConfig | null {
    return this.config
  }
}
