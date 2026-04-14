<template>
  <div class="audio-timeline">
    <div class="timeline-header">
      <span class="timeline-title">时间线</span>
      <span class="timeline-current">{{ currentTime }}</span>
    </div>
    <div class="timeline-track" @click="$emit('seek', $event)">
      <div
        v-for="chapter in chapters"
        :key="chapter.id"
        class="timeline-chapter"
        :class="{ active: selectedChapterId === chapter.id }"
        :style="{
          left: getChapterPosition(chapter.start_time) + '%',
          width: getChapterWidth(chapter) + '%'
        }"
        @click.stop="$emit('select-chapter', chapter.id)"
      >
        <span class="chapter-label">{{ chapter.title }}</span>
      </div>
      <div class="timeline-playhead" :style="{ left: progressPercent + '%' }"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Chapter } from '../stores/meeting'

const props = defineProps<{
  chapters: Chapter[]
  selectedChapterId: string | null
  currentTime: string
  progressPercent: number
  audioDuration?: number  // actual audio duration in seconds
}>()

defineEmits<{
  'seek': [event: MouseEvent]
  'select-chapter': [id: string]
}>()

function getChapterPosition(startTime: number): number {
  // Use actual audio duration when available, fallback to chapter-based total
  const total = props.audioDuration || props.chapters[props.chapters.length - 1]?.end_time || 500
  return (startTime / total) * 100
}

function getChapterWidth(chapter: Chapter): number {
  // Use actual audio duration when available, fallback to chapter-based total
  const total = props.audioDuration || props.chapters[props.chapters.length - 1]?.end_time || 500
  const duration = (chapter.end_time || 0) - chapter.start_time
  return (duration / total) * 100
}
</script>

<style scoped>
.audio-timeline {
  padding: 16px;
  background: #1a1a24;
  border-bottom: 1px solid #262626;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.timeline-title {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.timeline-current {
  font-size: 12px;
  color: #6366f1;
}

.timeline-track {
  position: relative;
  height: 32px;
  background: #262626;
  border-radius: 4px;
  cursor: pointer;
  overflow: hidden;
}

.timeline-chapter {
  position: absolute;
  top: 0;
  height: 100%;
  background: #3d3d4d;
  border-right: 1px solid #0d0d15;
  display: flex;
  align-items: center;
  padding: 0 8px;
  transition: background 0.2s;
  min-width: 40px;
}

.timeline-chapter:hover,
.timeline-chapter.active {
  background: #6366f1;
}

.chapter-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.8);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.timeline-playhead {
  position: absolute;
  top: 0;
  width: 2px;
  height: 100%;
  background: #ff6b6b;
  transition: left 0.1s;
}
</style>
