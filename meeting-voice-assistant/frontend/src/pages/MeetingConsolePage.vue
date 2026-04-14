<template>
  <div class="console-page">
    <!-- Header -->
    <header class="console-header">
      <button class="btn-back" @click="goBack">
        <span class="back-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>
        <span>返回上传</span>
      </button>
      <h1 class="console-title">{{ store.topic || '会议记录' }}</h1>
      <div class="console-meta">
        <span class="meta-date">{{ meetingDate }}</span>
        <span class="meta-dot">•</span>
        <span class="meta-topics">{{ chapters.length }} 个议题</span>
      </div>
    </header>

    <!-- Main Content - Three Column Layout -->
    <div class="console-body">
      <!-- Left Sidebar (A) - 320px -->
      <aside class="sidebar-left">
        <!-- Audio Player (inline - controls playback state) -->
        <div class="audio-player">
          <div class="player-info">
            <h3 class="player-title">整场会议</h3>
            <p class="player-subtitle">{{ chapters.length }} 个分段 · {{ totalDuration }}</p>
          </div>
          <div class="player-controls">
            <button class="btn-play" @click="togglePlay">
              <span class="play-icon">
                <svg v-if="!isPlaying" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M6 4L12 8L6 12V4Z" fill="currentColor"/>
                </svg>
                <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <rect x="4" y="3" width="3" height="10" rx="0.5" fill="currentColor"/>
                  <rect x="9" y="3" width="3" height="10" rx="0.5" fill="currentColor"/>
                </svg>
              </span>
            </button>
            <span class="time-display">{{ currentTime }} / {{ totalDuration }}</span>
          </div>
          <div class="player-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
            </div>
          </div>
          <div v-if="audioError" class="audio-error">
            {{ audioError }}
          </div>
        </div>

        <!-- Chapter List Component -->
        <div class="chapter-list-wrapper">
          <ChapterList
            :chapters="chapters"
            :selected-chapter-id="store.selectedChapterId"
            :speakers="store.speakers"
            @select-chapter="selectChapter"
            @jump-to-time="jumpToTime"
          />
        </div>
      </aside>

      <!-- Main Content (B) - flex: 1 -->
      <section class="main-content">
        <!-- Audio Timeline Component -->
        <AudioTimeline
          :chapters="chapters"
          :selected-chapter-id="store.selectedChapterId"
          :current-time="currentTime"
          :progress-percent="progressPercent"
          :audio-duration="audioDuration"
          @seek="seekTimeline"
          @select-chapter="selectChapter"
        />

        <!-- Tab List -->
        <div class="tab-list">
          <button class="tab-item" :class="{ active: activeTab === 'notes' }" @click="activeTab = 'notes'">
            AI 纪要
          </button>
          <button class="tab-item" :class="{ active: activeTab === 'transcript' }" @click="activeTab = 'transcript'">
            语音转文字
          </button>
        </div>

        <!-- Notes Panel Component -->
        <NotesPanel
          v-if="activeTab === 'notes'"
          :chapter-data="currentChapterData"
          @jump-to-time="jumpToTime"
        />

        <!-- Transcript Display (placeholder for now) -->
        <div v-else class="transcript-panel">
          <p class="transcript-placeholder">转写内容展示区域</p>
        </div>
      </section>

      <!-- Right Sidebar (C) - 320px -->
      <aside class="sidebar-right">
        <!-- GraphRAG Panel Component -->
        <GraphRAGPanel
          :search-query="searchQuery"
          :search-results="searchResults"
          :auto-tags="autoTags"
          :is-searching="isSearching"
          :search-error="searchError"
          @search="triggerSearch"
          @update:search-query="searchQuery = $event"
        />
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMeetingStore, type Chapter } from '../stores/meeting'
import ChapterList from '../components/ChapterList.vue'
import AudioTimeline from '../components/AudioTimeline.vue'
import NotesPanel from '../components/NotesPanel.vue'
import GraphRAGPanel from '../components/GraphRAGPanel.vue'
import { API_CONFIG } from '../api/config'

const router = useRouter()
const store = useMeetingStore()

// Audio element ref
const audioElement = ref<HTMLAudioElement | null>(null)
const audioSrc = ref('')

// Audio player state
const isPlaying = ref(false)
const currentTime = ref('0:00')
const progressPercent = ref(0)
const totalSeconds = ref(0)
const audioError = ref('')

// Demo audio URL (使用一个短音频用于测试)
const DEMO_AUDIO_URL = 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'

// Tab state
const activeTab = ref<'notes' | 'transcript'>('notes')

// Search
const searchQuery = ref('')
const searchResults = ref<Array<{ id: string; name: string; relevance: number }>>([])
const isSearching = ref(false)
const searchError = ref('')

// Computed
const meetingDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
})

const audioDuration = computed(() => audioElement.value?.duration || 0)

const chapters = computed(() => {
  return store.chapters.length ? store.chapters : mockChapters
})

const currentChapterData = computed(() => {
  if (!store.selectedChapterId && chapters.value.length) {
    return chapters.value[0]
  }
  return chapters.value.find(c => c.id === store.selectedChapterId) || null
})

const totalDuration = computed(() => {
  // Use actual audio duration when available (set by loadedmetadata event)
  const audioDur = audioElement.value?.duration || 0
  if (audioDur > 0) {
    const min = Math.floor(audioDur / 60)
    const sec = Math.floor(audioDur % 60)
    return `${min}:${String(sec).padStart(2, '0')}`
  }
  // Fallback: use chapter end_time but cap at 30 minutes to avoid hallucinated values
  if (!chapters.value.length) return '0:00'
  const lastChapter = chapters.value[chapters.value.length - 1]
  const rawEnd = lastChapter.end_time || 0
  // If chapter end_time is hallucinated (e.g., 372s for 18:48 audio), cap at 30min
  const total = rawEnd < 1800 ? rawEnd : 500
  const min = Math.floor(total / 60)
  const sec = Math.floor(total % 60)
  return `${min}:${String(sec).padStart(2, '0')}`
})

const autoTags = computed(() => {
  const tags: string[] = []
  if (store.topic) tags.push(store.topic)
  if (currentChapterData.value?.summary) {
    // 简单提取关键词
    const words = currentChapterData.value.summary.split(/[,，。.]/)
    tags.push(...words.slice(0, 3))
  }
  store.decisions.forEach(d => {
    if (d.decision.length < 20) tags.push(d.decision)
  })
  return tags.slice(0, 5)
})

// Mock data for demo
const mockChapters: Chapter[] = [
  {
    id: 'ch1',
    title: '用户反馈与问题分析',
    start_time: 0,
    end_time: 240,
    speaker_summaries: [
      { speaker: '产品经理', summary: '提出本季度产品路线图规划的核心目标，强调用户体验优化的重要性', source_timestamps: [{ start: 0, end: 96 }] },
      { speaker: '技术负责人', summary: '讨论技术实现方案的可行性，提出性能优化和架构调整建议', source_timestamps: [{ start: 96, end: 168 }] },
      { speaker: '设计师', summary: '分享最新的UI设计稿，说明设计思路和用户研究发现', source_timestamps: [{ start: 168, end: 240 }] }
    ],
    summary: '讨论Q2产品路线图，确定两阶段实施方案',
    decisions: [
      { decision: '决定采用两阶段实施方案：第一阶段处理性能优化和移动端适配（4月15日前），第二阶段上线搜索功能增强', source_timestamps: [{ start: 0, end: 240 }] }
    ],
    action_items: [
      { todo: '王磊：下周三前提交技术方案和工作量评估报告', source_timestamps: [{ start: 100, end: 120 }] },
      { todo: '李娜：协调用户研究团队，补充功能优先级分析', source_timestamps: [{ start: 120, end: 140 }] },
      { todo: '张伟：准备技术方案评审会议', source_timestamps: [{ start: 140, end: 160 }] }
    ]
  },
  {
    id: 'ch2',
    title: '时间规划与资源评估',
    start_time: 240,
    end_time: 380,
    speaker_summaries: [
      { speaker: '产品经理', summary: '介绍项目时间线规划', source_timestamps: [{ start: 240, end: 300 }] },
      { speaker: '技术负责人', summary: '评估技术资源和人力分配', source_timestamps: [{ start: 300, end: 380 }] }
    ],
    summary: '确定项目时间线和资源分配方案',
    decisions: [
      { decision: '资源分配已确定', source_timestamps: [{ start: 240, end: 380 }] }
    ],
    action_items: [
      { todo: '准备资源调配计划', source_timestamps: [{ start: 320, end: 350 }] }
    ]
  },
  {
    id: 'ch3',
    title: '实施方案与行动计划',
    start_time: 380,
    end_time: 500,
    speaker_summaries: [
      { speaker: '技术负责人', summary: '阐述技术实施方案', source_timestamps: [{ start: 380, end: 440 }] },
      { speaker: '设计师', summary: '说明设计实施计划', source_timestamps: [{ start: 440, end: 500 }] }
    ],
    summary: '制定具体实施方案',
    decisions: [
      { decision: '实施方案已确定', source_timestamps: [{ start: 380, end: 500 }] }
    ],
    action_items: [
      { todo: '各自负责部分的具体行动计划', source_timestamps: [{ start: 450, end: 480 }] }
    ]
  }
]

// Methods
function goBack() {
  router.push('/')
}

function initAudio() {
  if (!audioElement.value) {
    audioElement.value = new Audio()
    audioElement.value.addEventListener('loadedmetadata', () => {
      if (audioElement.value) {
        totalSeconds.value = audioElement.value.duration
        // If there's a pending seek request, execute it now
        if (pendingSeekTime.value !== null && audioElement.value.duration > 0) {
          const seekTime = pendingSeekTime.value
          pendingSeekTime.value = null
          audioElement.value.currentTime = seekTime
        }
      }
    })
    audioElement.value.addEventListener('timeupdate', () => {
      if (audioElement.value) {
        const current = audioElement.value.currentTime
        const total = totalSeconds.value || audioElement.value.duration || 500
        progressPercent.value = (current / total) * 100
        const min = Math.floor(current / 60)
        const sec = Math.floor(current % 60)
        currentTime.value = `${min}:${String(sec).padStart(2, '0')}`
      }
    })
    audioElement.value.addEventListener('ended', () => {
      isPlaying.value = false
      progressPercent.value = 0
      currentTime.value = '0:00'
    })
    audioElement.value.addEventListener('error', (e) => {
      console.error('[MeetingConsole] Audio error:', e)
      isPlaying.value = false
      audioError.value = '音频加载失败，请检查网络或音频文件'
      setTimeout(() => { audioError.value = '' }, 5000)
    })
  }
  // Use store audioUrl or demo URL
  const src = store.audioUrl || DEMO_AUDIO_URL
  if (audioSrc.value !== src) {
    audioSrc.value = src
    audioElement.value.src = src
    audioElement.value.load()
  }
}

// Watch for store.audioUrl changes - update audio when real audio URL is set
// P0-2: Save current playback position before load, restore after
let savedPlaybackPosition = 0

watch(() => store.audioUrl, (newUrl) => {
  if (newUrl && audioElement.value) {
    const src = newUrl || DEMO_AUDIO_URL
    if (audioSrc.value !== src) {
      // Save current playback position if playing
      savedPlaybackPosition = audioElement.value.currentTime || 0
      audioSrc.value = src
      audioElement.value.src = src
      audioElement.value.load()
      // Restore position after metadata loads
      const restoredPosition = savedPlaybackPosition
      audioElement.value.addEventListener('loadedmetadata', function restorePosition() {
        if (audioElement.value) {
          audioElement.value.currentTime = restoredPosition
          audioElement.value.removeEventListener('loadedmetadata', restorePosition)
        }
      }, { once: true })
    }
  }
})

function togglePlay() {
  if (!audioElement.value) {
    initAudio()
  }
  if (!audioElement.value) return

  if (isPlaying.value) {
    audioElement.value.pause()
    isPlaying.value = false
  } else {
    audioElement.value.play().then(() => {
      isPlaying.value = true
    }).catch(err => {
      console.error('[MeetingConsole] Play failed:', err)
    })
  }
}

function selectChapter(id: string) {
  store.setSelectedChapterId(id)
  // 停止当前播放
  isPlaying.value = false
  if (audioElement.value) {
    audioElement.value.pause()
  }
  // 更新播放位置到章节开始时间
  const chapter = chapters.value.find(c => c.id === id)
  if (chapter) {
    const audioDuration = audioElement.value?.duration || 0
    // Use ACTUAL audio duration when available, not chapter-based total
    let total: number
    if (audioDuration > 0) {
      total = audioDuration
    } else {
      const lastChapterEnd = chapters.value[chapters.value.length - 1]?.end_time || 500
      total = lastChapterEnd < 1800 ? lastChapterEnd : 500
    }
    const chapterStart = chapter.start_time || 0
    progressPercent.value = Math.min((chapterStart / total) * 100, 100)
    totalSeconds.value = total
    const min = Math.floor(chapterStart / 60)
    const sec = Math.floor(chapterStart % 60)
    currentTime.value = `${min}:${String(sec).padStart(2, '0')}`
    // 如果有真实音频，跳转到对应时间
    if (audioElement.value && audioDuration > 0) {
      audioElement.value.currentTime = chapterStart
    }
  }
}

function seekTimeline(e: MouseEvent) {
  const track = e.currentTarget as HTMLElement
  const rect = track.getBoundingClientRect()
  const percent = ((e.clientX - rect.left) / rect.width) * 100
  progressPercent.value = Math.max(0, Math.min(100, percent))
  // Use ACTUAL audio duration, with validation fallback
  const audioDuration = audioElement.value?.duration || 0
  let total: number
  if (audioDuration > 0) {
    total = audioDuration
  } else {
    const lastChapterEnd = chapters.value[chapters.value.length - 1]?.end_time || 500
    total = lastChapterEnd < 1800 ? lastChapterEnd : 500
  }
  const current = Math.floor((percent / 100) * total)
  const min = Math.floor(current / 60)
  const sec = Math.floor(current % 60)
  currentTime.value = `${min}:${String(sec).padStart(2, '0')}`
  // 如果有真实音频，跳转到对应时间
  if (audioElement.value && audioDuration > 0) {
    const audioTime = (percent / 100) * audioDuration
    audioElement.value.currentTime = audioTime
  }
}

// Pending seek request (used when audio not loaded yet)
const pendingSeekTime = ref<number | null>(null)

function jumpToTime(time: number | undefined) {
  if (time === undefined) return
  // Use ACTUAL audio duration for ALL calculations
  const audioDuration = audioElement.value?.duration || 0

  // If audio loaded, use audio duration. Otherwise use chapter total but VALIDATE it.
  let total: number
  if (audioDuration > 0) {
    total = audioDuration
  } else {
    // Fallback: use chapter end_time but cap it to a reasonable max
    const lastChapterEnd = chapters.value[chapters.value.length - 1]?.end_time || 500
    total = lastChapterEnd < 1800 ? lastChapterEnd : 500
  }
  progressPercent.value = Math.min((time / total) * 100, 100)
  totalSeconds.value = total
  const min = Math.floor(time / 60)
  const sec = Math.floor(time % 60)
  currentTime.value = `${min}:${String(sec).padStart(2, '0')}`

  // If audio element exists, seek to the time
  if (audioElement.value) {
    if (audioDuration > 0) {
      // Audio already loaded, seek directly
      audioElement.value.currentTime = time
    } else {
      // Audio not loaded yet, save pending seek and trigger loading
      pendingSeekTime.value = time
      // Trigger audio load by setting src and loading
      const src = store.audioUrl || DEMO_AUDIO_URL
      if (audioSrc.value !== src) {
        audioSrc.value = src
        audioElement.value.src = src
        audioElement.value.load()
      } else {
        // Already has correct src, just trigger metadata load
        audioElement.value.load()
      }
    }
  }
}

async function triggerSearch() {
  // 构建查询上下文
  const queryParts: string[] = []
  const contextParts: string[] = []

  // 添加主题
  if (store.topic) {
    queryParts.push(`会议主题: ${store.topic}`)
    contextParts.push(`会议主题是"${store.topic}"`)
  }

  // 添加当前章节的决策和待办
  const chapterData = currentChapterData.value
  if (chapterData) {
    if (chapterData.decisions?.length) {
      const decisionTexts = chapterData.decisions.map(d => d.decision).join('；')
      contextParts.push(`关键决策: ${decisionTexts}`)
    }
    if (chapterData.action_items?.length) {
      const actionTexts = chapterData.action_items.map(a => a.todo).join('；')
      contextParts.push(`待办事项: ${actionTexts}`)
    }
    if (chapterData.summary) {
      contextParts.push(`段落摘要: ${chapterData.summary}`)
    }
  }

  // 使用搜索框输入或自动生成的标签
  const query = searchQuery.value || autoTags.value.slice(0, 3).join(' ')
  if (!query && contextParts.length === 0) {
    searchResults.value = []
    return
  }

  // 如果没有搜索词但有上下文，使用上下文作为查询
  const finalQuery = query || contextParts.join('，')
  const context = contextParts.join('。')

  isSearching.value = true
  searchError.value = ''

  try {
    const response = await fetch(`${API_CONFIG.graphragUrl}/api/v1/query/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: finalQuery,
        top_k: 10,
        context: context || undefined,
      }),
    })

    if (!response.ok) {
      throw new Error(`查询失败: ${response.status}`)
    }

    const data = await response.json()

    // 转换响应为展示格式
    searchResults.value = data.sources?.map((source: any, index: number) => ({
      id: source.doc_id || `result-${index}`,
      name: source.chunk?.substring(0, 50) + (source.chunk?.length > 50 ? '...' : '') || '未知文档',
      relevance: Math.round((source.similarity || 0.8 - index * 0.05) * 100),
      fullChunk: source.chunk,
      answer: data.answer,
    })) || []
  } catch (error) {
    console.error('GraphRAG query failed:', error)
    searchError.value = error instanceof Error ? error.message : '查询失败'
    searchResults.value = []
  } finally {
    isSearching.value = false
  }
}

// Initialize
onMounted(() => {
  // Do NOT set totalSeconds from chapter data here - let loadedmetadata event set it from actual audio duration
  if (chapters.value.length && !store.selectedChapterId) {
    store.setSelectedChapterId(chapters.value[0].id)
  }
  initAudio()
})

onUnmounted(() => {
  if (audioElement.value) {
    audioElement.value.pause()
    audioElement.value = null
  }
})
</script>

<style scoped>
.console-page {
  min-height: 100vh;
  background: #0d0d15;
  color: #ffffff;
}

/* Header */
.console-header {
  display: flex;
  align-items: center;
  height: 56px;
  padding: 0 24px;
  background: #1a1a24;
  border-bottom: 1px solid #2d2d3d;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: transparent;
  color: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.1);
}

.back-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.console-title {
  margin-left: 16px;
  font-size: 18px;
  font-weight: 500;
  color: #ffffff;
}

.console-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.meta-dot {
  opacity: 0.5;
}

/* Body Layout */
.console-body {
  display: flex;
  height: calc(100vh - 56px);
}

/* Left Sidebar */
.sidebar-left {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 56px);
  overflow: hidden;
  background: #0d0d15;
}

.audio-player {
  flex-shrink: 0;
  background: #1a1a24;
  border-radius: 8px;
  margin: 16px;
  padding: 16px;
}

.chapter-list-wrapper {
  flex: 1;
  min-height: 0;
  margin: 0 16px 16px 16px;
  border-radius: 8px;
  overflow: hidden;
}

.player-info {
  margin-bottom: 12px;
}

.player-title {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  margin: 0 0 4px 0;
}

.player-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.player-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.btn-play {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #6366f1;
  border: none;
  border-radius: 50%;
  color: #ffffff;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-play:hover {
  background: #5558e3;
}

.time-display {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  flex: 1;
}

.player-progress {
  margin-bottom: 12px;
}

.progress-bar {
  height: 4px;
  background: #262626;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #6366f1;
  transition: width 0.3s;
}

.audio-error {
  margin-top: 8px;
  padding: 6px 10px;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid #ef4444;
  border-radius: 4px;
  color: #ef4444;
  font-size: 12px;
  text-align: center;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #1a1a24;
  margin: 16px;
  border-radius: 8px;
  overflow: hidden;
}

/* Tab List */
.tab-list {
  display: flex;
  border-bottom: 1px solid #262626;
}

.tab-item {
  flex: 1;
  padding: 14px;
  font-size: 14px;
  background: transparent;
  color: #a1a1a1;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-item.active {
  color: #fafafa;
  background: #262626;
}

.tab-item:hover:not(.active) {
  color: #ffffff;
}

/* Right Sidebar */
.sidebar-right {
  width: 320px;
  flex-shrink: 0;
  padding: 16px 16px 16px 0;
}
</style>
