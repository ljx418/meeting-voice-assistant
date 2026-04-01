<template>
  <div class="audio-recorder">
    <!-- 录音状态和时长 -->
    <div class="recorder-status-bar">
      <div class="status-indicator" :class="{ recording: isRecording, paused: isPaused }">
        <span class="status-dot"></span>
        <span class="status-text">{{ statusText }}</span>
      </div>
      <div v-if="isRecording" class="duration-display">
        {{ formattedDuration }}
      </div>
    </div>

    <!-- 波形可视化 -->
    <AudioWaveform
      :audio-level="audioLevel"
      :audio-waveform="audioWaveform"
      :is-recording="isRecording"
      :is-paused="isPaused"
    />

    <!-- 音量指示器 -->
    <div class="volume-indicator">
      <div class="volume-bar">
        <div
          class="volume-level"
          :style="{
            width: `${audioLevel}%`,
            backgroundColor: volumeColor
          }"
        ></div>
      </div>
      <span class="volume-label">{{ audioLevel }}%</span>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <!-- 控制按钮 -->
    <div class="recorder-controls">
      <button
        v-if="!isRecording"
        class="btn-record"
        @click="handleStart"
        :disabled="!isConnected || isConnecting"
      >
        {{ isConnecting ? '连接中...' : '开始录音' }}
      </button>

      <template v-else>
        <button
          v-if="!isPaused"
          class="btn-pause"
          @click="handlePause"
        >
          暂停
        </button>
        <button
          v-else
          class="btn-resume"
          @click="handleResume"
        >
          继续
        </button>

        <button
          class="btn-stop"
          @click="handleStop"
        >
          停止
        </button>
      </template>
    </div>

    <!-- 连接状态 -->
    <div v-if="!isConnected" class="connection-hint">
      请先点击「连接」按钮建立连接
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAudioRecorder } from '../composables/useAudioRecorder'
import { useMeetingStore } from '../stores/meeting'
import AudioWaveform from './AudioWaveform.vue'
import type { VoiceWSClient } from '../api/websocket'

const props = defineProps<{
  isConnected: boolean
  wsClient: VoiceWSClient
}>()

const emit = defineEmits<{
  (e: 'start'): void
  (e: 'pause'): void
  (e: 'resume'): void
  (e: 'stop'): void
}>()

const meetingStore = useMeetingStore()
const isConnecting = ref(false)

const {
  isRecording,
  isPaused,
  audioLevel,
  audioWaveform,
  recordingDuration,
  startRecording,
  stopRecording,
  pauseRecording,
  resumeRecording,
} = useAudioRecorder(props.wsClient)

const errorMessage = computed(() => meetingStore.errorMessage)

const statusText = computed(() => {
  if (!props.isConnected) return '未连接'
  if (isRecording.value) {
    return isPaused.value ? '已暂停' : '录音中'
  }
  return '就绪'
})

const volumeColor = computed(() => {
  if (isPaused.value) return '#ff9800'
  if (isRecording.value) return '#4caf50'
  return '#9e9e9e'
})

const formattedDuration = computed(() => {
  const minutes = Math.floor(recordingDuration.value / 60)
  const seconds = recordingDuration.value % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

async function handleStart() {
  try {
    if (!props.wsClient) {
      throw new Error('WebSocket client not available')
    }
    isConnecting.value = true
    console.log('[Recorder] Starting recording, wsClient:', props.wsClient)
    console.log('[Recorder] wsClient.start:', props.wsClient.start)
    await startRecording()
    meetingStore.setStatus('recording')
    meetingStore.clearError()
    emit('start')
  } catch (error) {
    console.error('Failed to start recording:', error)
    meetingStore.setError(`启动录音失败: ${(error as Error).message}`)
  } finally {
    isConnecting.value = false
  }
}

function handlePause() {
  pauseRecording()
  meetingStore.setStatus('paused')
  emit('pause')
}

function handleResume() {
  resumeRecording()
  meetingStore.setStatus('recording')
  emit('resume')
}

function handleStop() {
  stopRecording()
  meetingStore.setStatus('ended')
  emit('stop')
}
</script>

<style scoped>
.audio-recorder {
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

.recorder-status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #9e9e9e;
  transition: background-color 0.3s;
}

.status-indicator.recording .status-dot {
  background: #f44336;
  animation: pulse 1s infinite;
}

.status-indicator.paused .status-dot {
  background: #ff9800;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 0.9rem;
  color: #666;
}

.duration-display {
  font-size: 1.2rem;
  font-weight: 600;
  font-family: monospace;
  color: #333;
}

.volume-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.volume-bar {
  flex: 1;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.volume-level {
  height: 100%;
  transition: width 0.1s ease, background-color 0.3s;
}

.volume-label {
  font-size: 0.75rem;
  color: #999;
  min-width: 35px;
  text-align: right;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  margin-bottom: 0.75rem;
  border-left: 3px solid #c62828;
}

.recorder-controls {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

button {
  padding: 0.6rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s, opacity 0.2s;
}

.btn-record {
  background: #f44336;
  color: white;
}

.btn-record:hover:not(:disabled) {
  background: #d32f2f;
}

.btn-record:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-pause {
  background: #ff9800;
  color: white;
}

.btn-pause:hover {
  background: #f57c00;
}

.btn-resume {
  background: #4caf50;
  color: white;
}

.btn-resume:hover {
  background: #388e3c;
}

.btn-stop {
  background: #9e9e9e;
  color: white;
}

.btn-stop:hover {
  background: #757575;
}

.connection-hint {
  text-align: center;
  font-size: 0.8rem;
  color: #999;
  margin-top: 0.5rem;
}
</style>
