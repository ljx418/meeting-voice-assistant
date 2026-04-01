/**
 * 音频录制 Composable
 *
 * 设计要点:
 * - 使用 MediaRecorder API
 * - 支持暂停/恢复
 * - 实时流式传输到 WebSocket
 * - 采样率统一转换为 16kHz (ASR 要求)
 */

import { ref, readonly, onUnmounted } from 'vue'
import type { VoiceWSClient } from '../api/websocket'

export function useAudioRecorder(wsClient: VoiceWSClient) {
  const isRecording = ref(false)
  const isPaused = ref(false)
  const audioLevel = ref(0) // 用于音量可视化 (0-100)
  const audioWaveform = ref<number[]>([]) // 用于波形可视化
  const recordingDuration = ref(0) // 录音时长（秒）

  let mediaRecorder: MediaRecorder | null = null
  let audioContext: AudioContext | null = null
  let analyser: AnalyserNode | null = null
  let stream: MediaStream | null = null
  const audioChunks: Blob[] = []

  /**
   * 初始化麦克风访问
   */
  async function startRecording(): Promise<void> {
    console.log('[Recorder] startRecording called')
    try {
      console.log('[Recorder] Getting microphone permission...')
      // 获取麦克风权限
      stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
        },
      })
      console.log('[Recorder] Microphone permission granted')

      // 设置音频分析 (用于音量显示)
      audioContext = new AudioContext({ sampleRate: 16000 })
      console.log('[Recorder] AudioContext state after creation:', audioContext.state)
      const source = audioContext.createMediaStreamSource(stream)
      analyser = audioContext.createAnalyser()
      analyser.fftSize = 256
      source.connect(analyser)

      // 确保 AudioContext 处于运行状态（浏览器策略可能导致挂起）
      if (audioContext.state === 'suspended') {
        console.log('[Recorder] AudioContext is suspended, resuming...')
        await audioContext.resume()
        console.log('[Recorder] AudioContext state after resume:', audioContext.state)
      }

      // 开始音量监控
      monitorAudioLevel()

      // 创建 MediaRecorder
      mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      })

      mediaRecorder.ondataavailable = (event) => {
        console.log('[Recorder] ondataavailable, size:', event.data.size)
        if (event.data.size > 0) {
          audioChunks.push(event.data)
          // 转换为 ArrayBuffer 并发送
          event.data.arrayBuffer().then((buffer) => {
            console.log('[Recorder] Sending audio chunk:', buffer.byteLength, 'bytes')
            wsClient.sendAudio(buffer)
          }).catch((err) => {
            console.error('[Recorder] Failed to send audio chunk:', err)
          })
        }
      }

      mediaRecorder.start(100) // 每 100ms 发送一次
      console.log('[Recorder] MediaRecorder started')
      isRecording.value = true
      isPaused.value = false
      recordingDuration.value = 0
      startDurationTimer()

      // 通知后端开始
      console.log('[Recorder] Calling wsClient.start()')
      wsClient.start()
      console.log('[Recorder] wsClient.start() completed')

    } catch (error) {
      console.error('[Recorder] Failed to start recording:', error)
      throw error
    }
  }

  /**
   * 停止录音
   */
  function stopRecording(): void {
    console.log('[Recorder] stopRecording called, isRecording:', isRecording.value, 'mediaRecorder:', !!mediaRecorder)
    if (mediaRecorder && isRecording.value) {
      // 先发送 stop 控制消息到后端
      console.log('[Recorder] Calling wsClient.stop() first, ws connected:', wsClient.isConnected)
      wsClient.stop()

      // 请求并等待最后的音频数据
      console.log('[Recorder] Requesting final audio data...')
      mediaRecorder.requestData()  // 请求当前缓冲的数据

      // 等待 ondataavailable 完成后再停止
      // 使用 setTimeout 确保异步 ondataavailable 有时间执行
      setTimeout(() => {
        console.log('[Recorder] Stopping mediaRecorder after final data...')
        mediaRecorder?.stop()
        isRecording.value = false
        isPaused.value = false

        // 停止时长计时
        if (durationTimer) {
          clearInterval(durationTimer)
          durationTimer = null
        }

        // 清理资源
        cleanup()
      }, 200)
    }
  }

  /**
   * 暂停录音
   */
  function pauseRecording(): void {
    if (mediaRecorder && isRecording.value && !isPaused.value) {
      mediaRecorder.pause()
      isPaused.value = true
      wsClient.pause()
    }
  }

  /**
   * 恢复录音
   */
  function resumeRecording(): void {
    if (mediaRecorder && isRecording.value && isPaused.value) {
      mediaRecorder.resume()
      isPaused.value = false
      wsClient.resume()
    }
  }

  /**
   * 监控音频音量
   */
  function monitorAudioLevel(): void {
    if (!analyser) {
      console.log('[Recorder] monitorAudioLevel: analyser is null, returning')
      return
    }

    const dataArray = new Uint8Array(analyser.frequencyBinCount)
    console.log('[Recorder] monitorAudioLevel: starting, frequencyBinCount:', analyser.frequencyBinCount)

    let frameCount = 0
    let lastLogTime = 0

    const updateLevel = () => {
      // 继续运行动画循环，即使还没开始录音
      if (!analyser) return

      // 获取频率数据
      analyser.getByteFrequencyData(dataArray)

      // 计算音量级别
      const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length
      audioLevel.value = Math.min(100, Math.round((average / 128) * 100))

      // 更新波形数据
      const waveformData = Array.from(dataArray.slice(0, 32)).map(v => v / 255)
      audioWaveform.value = waveformData

      // 调试日志（每秒最多一次）
      const now = Date.now()
      frameCount++
      if (now - lastLogTime > 1000 && frameCount <= 10) {
        console.log(`[Recorder] monitorAudioLevel frame ${frameCount}: audioLevel=${audioLevel.value}, waveform[0]=${waveformData[0]?.toFixed(3) || 'N/A'}, isRecording=${isRecording.value}, avg=${average.toFixed(1)}`)
        lastLogTime = now
      }

      requestAnimationFrame(updateLevel)
    }

    updateLevel()
  }

  /**
   * 录音时长定时器
   */
  let durationTimer: number | null = null
  function startDurationTimer(): void {
    if (durationTimer) clearInterval(durationTimer)
    durationTimer = window.setInterval(() => {
      if (isRecording.value && !isPaused.value) {
        recordingDuration.value++
      }
    }, 1000)
  }

  /**
   * 清理资源
   */
  function cleanup(): void {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop())
      stream = null
    }

    if (audioContext) {
      audioContext.close()
      audioContext = null
    }

    analyser = null
    mediaRecorder = null
    audioChunks.length = 0
    audioLevel.value = 0
    audioWaveform.value = []
    recordingDuration.value = 0
  }

  // 组件卸载时清理
  onUnmounted(() => {
    cleanup()
  })

  return {
    isRecording: readonly(isRecording),
    isPaused: readonly(isPaused),
    audioLevel: readonly(audioLevel),
    audioWaveform: readonly(audioWaveform),
    recordingDuration: readonly(recordingDuration),
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
  }
}
