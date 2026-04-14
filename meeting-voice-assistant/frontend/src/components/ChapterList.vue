<template>
  <div class="chapter-list">
    <h3 class="list-title">段落列表</h3>
    <div class="list-items">
      <div
        v-for="(chapter, idx) in chapters"
        :key="chapter.id"
        class="chapter-item"
        :class="{ active: selectedChapterId === chapter.id }"
      >
        <div class="chapter-header">
          <div class="chapter-info" @click.stop="$emit('select-chapter', chapter.id)">
            <span class="chapter-icon">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <rect x="3" y="5" width="10" height="6" rx="1" stroke="currentColor" stroke-width="1.33"/>
                <path d="M5 8H7" stroke="currentColor" stroke-width="1.33" stroke-linecap="round"/>
              </svg>
            </span>
            <span class="chapter-name">{{ chapter.title }}</span>
          </div>
          <span class="chapter-arrow" :class="{ expanded: isExpanded(chapter.id) }" @click.stop="toggleChapter(chapter.id)">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </span>
        </div>
        <div v-show="isExpanded(chapter.id)" class="speaker-bars">
          <span class="bar-label">发言人</span>
          <div class="bars-row">
            <div
              v-for="spkSummary in getChapterSpeakers(chapter)"
              :key="spkSummary.speaker"
              class="speaker-bar"
              :class="{ active: activeSpeakerBar === chapter.id + '-' + spkSummary.speaker }"
              :style="{
                width: getSpeakerPercent(chapter, spkSummary.speaker) + '%',
                backgroundColor: getSpeakerColor(spkSummary.speaker)
              }"
              :title="spkSummary.speaker + ': ' + getSpeakerPercent(chapter, spkSummary.speaker) + '%'"
              @click.stop="handleSpeakerBarClick(chapter, spkSummary)"
            ></div>
          </div>
        </div>
        <div v-show="isExpanded(chapter.id)" class="speaker-details">
          <div
            v-for="spkSummary in getChapterSpeakers(chapter)"
            :key="spkSummary.speaker"
            class="speaker-detail"
          >
            <span class="speaker-dot" :style="{ backgroundColor: getSpeakerColor(spkSummary.speaker) }"></span>
            <span class="speaker-name">{{ spkSummary.speaker }}</span>
            <span class="speaker-time">{{ formatTimeRange(spkSummary.source_timestamps) }}</span>
            <p class="speaker-text">{{ spkSummary.summary }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Chapter, SpeakerSummary } from '../stores/meeting'

const props = defineProps<{
  chapters: Chapter[]
  selectedChapterId: string | null
  speakers: Array<{ id: string; name: string; color: string }>
}>()

const emit = defineEmits<{
  'select-chapter': [id: string]
  'jump-to-time': [time: number]
}>()

// Track expanded state for each chapter
const expandedChapters = ref<Record<string, boolean>>({})
const activeSpeakerBar = ref<string | null>(null)
const DEBUG = false

function toggleChapter(chapterId: string) {
  const wasExpanded = !!expandedChapters.value[chapterId]
  expandedChapters.value[chapterId] = !wasExpanded
  if (DEBUG) console.log('[ChapterList] toggleChapter', chapterId, 'wasExpanded:', wasExpanded, 'nowExpanded:', expandedChapters.value[chapterId])
}

function isExpanded(chapterId: string): boolean {
  const result = !!expandedChapters.value[chapterId]
  if (DEBUG) console.log('[ChapterList] isExpanded', chapterId, result)
  return result
}

const speakerColors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']

function getChapterSpeakers(chapter: Chapter): SpeakerSummary[] {
  return chapter.speaker_summaries || []
}

function getSpeakerDuration(summaries: SpeakerSummary[], speaker: string): number {
  const s = summaries.find(s => s.speaker === speaker)
  if (!s) return 0
  return s.source_timestamps.reduce((acc, ts) => acc + ((ts?.end ?? 0) - (ts?.start ?? 0)), 0)
}

function getSpeakerPercent(chapter: Chapter, speaker: string): number {
  const summaries = chapter.speaker_summaries || []
  const total = summaries.reduce((acc, s) => acc + getSpeakerDuration(summaries, s.speaker), 0)
  if (total === 0) return 0
  return Math.round((getSpeakerDuration(summaries, speaker) / total) * 100)
}

function getSpeakerColor(speaker: string): string {
  const index = props.speakers.findIndex(s => s.name === speaker)
  if (index >= 0) return props.speakers[index].color
  let hash = 0
  for (let i = 0; i < speaker.length; i++) {
    hash = speaker.charCodeAt(i) + ((hash << 5) - hash)
  }
  return speakerColors[Math.abs(hash) % speakerColors.length]
}

function formatTimeRange(timestamps: { start: number; end: number }[], chapterStart: number = 0): string {
  if (!timestamps?.length) return ''
  // Use the last timestamp block to show the speaker's full time range in the chapter
  const ts = timestamps[timestamps.length - 1]
  const formatTime = (s: number) => {
    const min = Math.floor(s / 60)
    const sec = Math.floor(s % 60)
    return `${min}:${String(sec).padStart(2, '0')}`
  }
  // source_timestamps from backend are ALREADY absolute time in seconds
  // (not relative to chapter), so we use them directly
  // chapterStart parameter kept for API compatibility but not used
  return `${formatTime(ts.start)} - ${formatTime(ts.end)}`
}

function handleSpeakerBarClick(chapter: Chapter, spkSummary: SpeakerSummary) {
  const timestamps = spkSummary.source_timestamps
  console.log('[ChapterList] handleSpeakerBarClick:', chapter.title, spkSummary.speaker,
    'chapter.start_time:', chapter.start_time, 'chapter.end_time:', chapter.end_time,
    'timestamps:', JSON.stringify(timestamps))

  if (!timestamps || timestamps.length === 0) {
    console.log('[ChapterList] speaker bar click - no timestamps', spkSummary)
    return
  }

  // Use the LAST timestamp block to get the speaker's final position in this chapter
  // (a speaker may have multiple speaking turns, we want the last one)
  const lastTimestamp = timestamps[timestamps.length - 1]
  console.log('[ChapterList] lastTimestamp:', JSON.stringify(lastTimestamp))

  if (lastTimestamp) {
    // source_timestamps values from backend are ALREADY absolute time in seconds from audio start
    // (not relative to chapter), so we use them directly without adding chapter.start_time
    const absoluteTime = lastTimestamp.start

    console.log('[ChapterList] speaker bar click', spkSummary.speaker,
      'ts.start:', lastTimestamp.start,
      'ts.end:', lastTimestamp.end,
      'absolute:', absoluteTime,
      'ALL timestamps:', timestamps.map(t => `(${t.start}-${t.end})`).join(', '))

    // Set active state for visual feedback
    activeSpeakerBar.value = chapter.id + '-' + spkSummary.speaker
    console.log('[ChapterList] activeSpeakerBar set to:', activeSpeakerBar.value)

    // Clear active state after 300ms
    setTimeout(() => {
      if (activeSpeakerBar.value === chapter.id + '-' + spkSummary.speaker) {
        activeSpeakerBar.value = null
      }
    }, 300)

    console.log('[ChapterList] EMIT jump-to-time:', absoluteTime)
    emit('jump-to-time', absoluteTime)
  } else {
    console.log('[ChapterList] speaker bar click - no timestamp', spkSummary)
  }
}
</script>

<style scoped>
.chapter-list {
  flex: 1;
  background: #1a1a24;
  border-radius: 8px;
  overflow-y: auto;
  height: 100%;
}

.list-title {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  margin: 0;
  padding: 12px 16px;
  border-bottom: 1px solid #262626;
}

.list-items {
  padding: 8px;
}

.chapter-item {
  padding: 12px;
  background: #0d0d15;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.chapter-item:hover {
  background: #1e1e2e;
}

.chapter-item.active {
  background: #6366f1;
}

.chapter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.chapter-icon {
  display: flex;
  align-items: center;
  color: rgba(255, 255, 255, 0.7);
}

.chapter-name {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
}

.chapter-arrow {
  display: flex;
  align-items: center;
  color: rgba(255, 255, 255, 0.5);
  transition: transform 0.2s;
}

.chapter-arrow.expanded {
  transform: rotate(180deg);
}

.speaker-bars {
  margin-bottom: 8px;
}

.bar-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  display: block;
  margin-bottom: 4px;
}

.bars-row {
  display: flex;
  height: 6px;
  border-radius: 3px;
  overflow: visible;
  gap: 2px;
}

.speaker-bar {
  height: 100%;
  border-radius: 3px;
  min-width: 2px;
  cursor: pointer;
  pointer-events: auto;
  position: relative;
  z-index: 1;
  transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
}

.speaker-bar:hover {
  transform: scaleY(1.3);
  box-shadow: 0 0 8px currentColor;
  filter: brightness(1.2);
}

.speaker-bar:active,
.speaker-bar.active {
  transform: scaleY(1.5);
  box-shadow: 0 0 12px currentColor;
  filter: brightness(1.3);
}

.speaker-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.speaker-detail {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.speaker-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.speaker-name {
  font-size: 12px;
  font-weight: 500;
  color: #ffffff;
}

.speaker-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

.speaker-text {
  width: 100%;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin: 4px 0 0 0;
  line-height: 1.4;
}
</style>
