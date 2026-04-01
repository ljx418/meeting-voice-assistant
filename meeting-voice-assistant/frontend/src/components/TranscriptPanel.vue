<template>
  <div class="transcript-panel">
    <h3>实时转写</h3>

    <div class="transcript-list" ref="listRef">
      <div
        v-for="segment in transcripts"
        :key="segment.id"
        class="transcript-segment"
        :class="{ 'is-final': segment.is_final, [`speaker-${getSpeakerColorIndex(segment.speaker)}`]: true }"
      >
        <span class="speaker-badge" v-if="segment.speaker" :style="{ backgroundColor: getSpeakerColor(segment.speaker) }">
          {{ formatSpeakerLabel(segment.speaker) }}
        </span>
        <span class="text">{{ segment.text }}</span>
        <span class="time">
          {{ formatTime(segment.start_time) }}
        </span>
      </div>

      <div v-if="currentText" class="transcript-segment is-current">
        <span class="speaker-badge" style="background-color: #9e9e9e;">识别中</span>
        <span class="text">{{ currentText }}</span>
        <span class="typing-indicator">...</span>
      </div>

      <div v-if="transcripts.length === 0 && !currentText" class="empty-state">
        <template v-if="isRealtimeMode">
          点击"开始录音"启动语音识别
        </template>
        <template v-else>
          上传音频文件开始识别
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import type { TranscriptSegment } from '../api/types'

const props = defineProps<{
  transcripts: TranscriptSegment[]
  currentText?: string
  mode?: 'realtime' | 'file'
}>()

const listRef = ref<HTMLElement | null>(null)

// Speaker color palette
const speakerColors = [
  '#4CAF50', // Green
  '#2196F3', // Blue
  '#FF9800', // Orange
  '#E91E63', // Pink
  '#9C27B0', // Purple
  '#00BCD4', // Cyan
  '#795548', // Brown
  '#607D8B', // Blue Grey
]

// Track assigned colors for speakers
const speakerColorMap = ref<Map<string, string>>(new Map())
const colorIndexMap = ref<Map<string, number>>(new Map())

function getSpeakerColorIndex(speaker: string | undefined): number {
  if (!speaker) return 0
  if (!colorIndexMap.value.has(speaker)) {
    colorIndexMap.value.set(speaker, colorIndexMap.value.size % speakerColors.length)
  }
  return colorIndexMap.value.get(speaker) || 0
}

function getSpeakerColor(speaker: string | undefined): string {
  if (!speaker) return speakerColors[0]
  if (!speakerColorMap.value.has(speaker)) {
    speakerColorMap.value.set(speaker, speakerColors[speakerColorMap.value.size % speakerColors.length])
  }
  return speakerColorMap.value.get(speaker) || speakerColors[0]
}

function formatSpeakerLabel(speaker: string | undefined): string {
  if (!speaker) return '未知'
  if (speaker === 'file') return '文件'
  // speaker_0 -> A, speaker_1 -> B, etc.
  if (speaker.startsWith('speaker_')) {
    const index = parseInt(speaker.split('_')[1])
    return String.fromCharCode(65 + index) // A, B, C, ...
  }
  return speaker
}

const isRealtimeMode = computed(() => props.mode !== 'file')

// 自动滚动到底部
watch(
  () => props.transcripts.length,
  async () => {
    await nextTick()
    if (listRef.value) {
      listRef.value.scrollTop = listRef.value.scrollHeight
    }
  }
)

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.transcript-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  overflow: hidden;
  min-height: 0;
}

h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: #333;
}

.transcript-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.transcript-segment {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f5f5f5;
  border-radius: 8px;
  animation: fadeIn 0.2s ease;
}

.transcript-segment.is-current {
  background: #e3f2fd;
}

.transcript-segment.is-final {
  background: #fafafa;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.speaker-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 24px;
  padding: 0 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}

.text {
  flex: 1;
  color: #333;
  line-height: 1.5;
}

.time {
  font-size: 0.75rem;
  color: #999;
  flex-shrink: 0;
}

.typing-indicator {
  color: #1976d2;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%,
  50% {
    opacity: 1;
  }
  51%,
  100% {
    opacity: 0;
  }
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 2rem;
}
</style>
