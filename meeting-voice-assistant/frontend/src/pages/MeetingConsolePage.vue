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
      <h1 class="console-title">{{ activeTopic }}</h1>
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
            <button class="btn-play" @click="togglePlay" :disabled="isAudioLoading">
              <span class="play-icon">
                <!-- Loading spinner -->
                <svg v-if="isAudioLoading" width="16" height="16" viewBox="0 0 16 16" fill="none" class="loading-spinner">
                  <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2" stroke-dasharray="30" stroke-dashoffset="10"/>
                </svg>
                <!-- Play icon -->
                <svg v-else-if="!isPlaying" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M6 4L12 8L6 12V4Z" fill="currentColor"/>
                </svg>
                <!-- Pause icon -->
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
            :speakers="activeSpeakers"
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
          <button class="tab-item" :class="{ active: activeTab === 'decisions' }" @click="activeTab = 'decisions'">
            待办决策
          </button>
        </div>

        <!-- Notes Panel Component -->
        <NotesPanel
          v-if="activeTab === 'notes'"
          :chapter-data="currentChapterData"
          @jump-to-time="jumpToTime"
        />

        <!-- Transcript Display -->
        <div v-else-if="activeTab === 'transcript'" class="transcript-panel">
          <div class="transcript-list">
            <div v-for="(seg, idx) in allTranscripts" :key="idx" class="transcript-item">
              <span class="seg-time" @click="jumpToTime(seg.start_time)">{{ formatTime(seg.start_time) }}</span>
              <span class="seg-speaker" :style="{ color: getSpeakerColor(seg.speaker) }">{{ seg.speaker }}</span>
              <span class="seg-text">{{ seg.text }}</span>
            </div>
            <div v-if="allTranscripts.length === 0" class="empty-hint">
              暂无转写数据
            </div>
          </div>
        </div>

        <!-- Decisions and Action Items -->
        <div v-else-if="activeTab === 'decisions'" class="decisions-panel">
          <!-- Decisions Section -->
          <div class="decisions-section">
            <h3 class="section-title">决策点</h3>
            <div class="decisions-list">
              <div v-for="(dec, idx) in allDecisions" :key="'dec-' + idx" class="decision-item">
                <div class="decision-icon">✓</div>
                <div class="decision-content">
                  <span class="decision-text">{{ dec.decision }}</span>
                  <span class="decision-time" v-if="dec.source_timestamps?.length">
                    {{ formatTime(dec.source_timestamps[0]?.start) }}
                  </span>
                </div>
              </div>
              <div v-if="allDecisions.length === 0" class="empty-hint">
                暂无决策点
              </div>
            </div>
          </div>

          <!-- Action Items Section -->
          <div class="actions-section">
            <h3 class="section-title">待办事项</h3>
            <div class="actions-list">
              <div v-for="(item, idx) in allActionItems" :key="'action-' + idx" class="action-item">
                <div class="action-checkbox">
                  <input type="checkbox" disabled />
                </div>
                <div class="action-content">
                  <span class="action-text">{{ item.todo }}</span>
                  <span class="action-time" v-if="item.source_timestamps?.length">
                    {{ formatTime(item.source_timestamps[0]?.start) }}
                  </span>
                </div>
              </div>
              <div v-if="allActionItems.length === 0" class="empty-hint">
                暂无待办事项
              </div>
            </div>
          </div>
        </div>
      </section>

<!-- Right Sidebar (C) - external knowledge service boundary -->
      <aside class="sidebar-right">
        <div class="knowledge-service-card">
          <h3>Knowledge Service</h3>
          <p>会议应用只负责转写和分析；知识固化、GraphRAG、Wiki 和 trace 由独立 data_service 提供。</p>
          <button class="btn-knowledge-service" @click="router.push('/knowledge')">打开服务控制台</button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMeetingStore, type Chapter } from '../stores/meeting'
import ChapterList from '../components/ChapterList.vue'
import AudioTimeline from '../components/AudioTimeline.vue'
import NotesPanel from '../components/NotesPanel.vue'

const router = useRouter()
const route = useRoute()
const store = useMeetingStore()

// Load session data from route param if present
const routeSessionId = computed(() => route.params.sessionId as string | undefined)
const sessionData = computed(() => {
  if (routeSessionId.value) {
    const data = store.getSessionData(routeSessionId.value) ?? null
    console.log(`[MeetingConsole] sessionData:`, { routeSessionId: routeSessionId.value, hasData: !!data, chaptersCount: data?.chapters?.length })
    return data
  }
  console.log(`[MeetingConsole] sessionData: no routeSessionId`)
  return null
})

// Audio element ref
const audioElement = ref<HTMLAudioElement | null>(null)
const audioSrc = ref('')

// Audio player state
const isPlaying = ref(false)
const isAudioLoading = ref(false)
const currentTime = ref('0:00')
const progressPercent = ref(0)
const totalSeconds = ref(0)
const audioError = ref('')

// Demo audio URL (使用一个短音频用于测试)
const DEMO_AUDIO_URL = 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'

// Tab state
const activeTab = ref<'notes' | 'transcript' | 'decisions'>('notes')

// Speaker colors
const speakerColors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']

// All transcripts from all chapters
const allTranscripts = computed(() => {
  const transcripts: Array<{ start_time: number; end_time: number; speaker: string; text: string }> = []
  chapters.value.forEach((ch: Chapter) => {
    if (ch.speaker_summaries) {
      ch.speaker_summaries.forEach((spk) => {
        if (spk.source_timestamps) {
          spk.source_timestamps.forEach((ts) => {
            transcripts.push({
              start_time: ts.start,
              end_time: ts.end,
              speaker: spk.speaker,
              text: spk.summary
            })
          })
        }
      })
    }
  })
  return transcripts.sort((a, b) => a.start_time - b.start_time)
})

// All decisions: from sessionData if available, else from chapters
const allDecisions = computed(() => {
  if (activeDecisions.value.length) return activeDecisions.value
  const decisions: Array<{ decision: string; source_timestamps: Array<{ start: number; end: number }> }> = []
  chapters.value.forEach((ch: Chapter) => {
    if (ch.decisions) ch.decisions.forEach(d => decisions.push(d))
  })
  return decisions
})

// All action items: from sessionData if available, else from chapters
const allActionItems = computed(() => {
  if (activeActionItems.value.length) return activeActionItems.value
  const items: Array<{ todo: string; source_timestamps: Array<{ start: number; end: number }> }> = []
  chapters.value.forEach((ch: Chapter) => {
    if (ch.action_items) ch.action_items.forEach(a => items.push(a))
  })
  return items
})

function getSpeakerColor(speaker: string): string {
  const index = activeSpeakers.value.findIndex(s => s.name === speaker)
  if (index >= 0) return activeSpeakers.value[index].color
  let hash = 0
  for (let i = 0; i < speaker.length; i++) {
    hash = speaker.charCodeAt(i) + ((hash << 5) - hash)
  }
  return speakerColors[Math.abs(hash) % speakerColors.length]
}

function formatTime(seconds: number): string {
  if (!seconds && seconds !== 0) return '-'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${String(secs).padStart(2, '0')}`
}

// Search
// Computed
const meetingDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
})

const audioDuration = computed(() => audioElement.value?.duration || 0)

const chapters = computed(() => {
  // Only use real data - never fallback to mock
  const src = sessionData.value?.chapters ?? store.chapters
  return src.length ? src : []
})

const activeSpeakers = computed(() => sessionData.value?.speakers ?? store.speakers)
const activeTopic = computed(() => sessionData.value?.theme || store.topic || '会议记录')
const activeDecisions = computed(() => sessionData.value?.decisions ?? store.decisions)
const activeActionItems = computed(() => sessionData.value?.actionItems ?? store.actionItems)
const activeAudioUrl = computed(() => sessionData.value?.audioUrl || store.audioUrl || '')

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
  router.push('/meeting')
}

function initAudio() {
  if (!audioElement.value) {
    audioElement.value = new Audio()
    audioElement.value.addEventListener('loadedmetadata', () => {
      if (audioElement.value) {
        const dur = audioElement.value.duration
        console.log('[MeetingConsole] Metadata loaded, duration:', dur)
        isAudioLoading.value = false
        totalSeconds.value = dur
        // If there's a pending seek request, execute it now
        if (pendingSeekTime.value !== null && dur > 0 && dur !== Infinity) {
          const seekTime = pendingSeekTime.value
          pendingSeekTime.value = null
          console.log('[MeetingConsole] Executing pending seek to:', seekTime)
          audioElement.value.currentTime = seekTime
        }
      }
    })
    // Also listen for canplay as fallback - it fires when audio is ready to play
    audioElement.value.addEventListener('canplay', () => {
      if (audioElement.value) {
        const dur = audioElement.value.duration
        console.log('[MeetingConsole] Canplay, duration:', dur)
        isAudioLoading.value = false
        // Only update totalSeconds if not already set
        if (!totalSeconds.value || totalSeconds.value === Infinity) {
          totalSeconds.value = dur
        }
        if (pendingSeekTime.value !== null && dur > 0 && dur !== Infinity) {
          const seekTime = pendingSeekTime.value
          pendingSeekTime.value = null
          console.log('[MeetingConsole] Canplay: executing pending seek to:', seekTime)
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
  // Use session or store audioUrl or demo URL
  const src = activeAudioUrl.value || DEMO_AUDIO_URL
  if (audioSrc.value !== src) {
    audioSrc.value = src
    audioElement.value.src = src
    audioElement.value.load()
  }
}

// Watch for audioUrl changes from session or store
let savedPlaybackPosition = 0
watch(activeAudioUrl, (newUrl) => {
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
    // Check if audio is ready to play
    if (audioElement.value.readyState >= 3) {
      // HAVE_CURRENT_DATA or more - audio is ready
      audioElement.value.play().then(() => {
        isPlaying.value = true
      }).catch(err => {
        console.error('[MeetingConsole] Play failed:', err)
        isPlaying.value = false
      })
    } else {
      // Audio not ready, wait for canplay
      console.log('[MeetingConsole] Audio not ready for play, waiting...')
      isAudioLoading.value = true
      const handleCanPlay = () => {
        if (audioElement.value) {
          audioElement.value.play().then(() => {
            isPlaying.value = true
          }).catch(err => {
            console.error('[MeetingConsole] Play failed:', err)
            isPlaying.value = false
          })
        }
        audioElement.value?.removeEventListener('canplay', handleCanPlay)
      }
      audioElement.value.addEventListener('canplay', handleCanPlay)
      // Trigger loading if not already
      if (!audioElement.value.src) {
        audioElement.value.src = activeAudioUrl.value || DEMO_AUDIO_URL
        audioElement.value.load()
      }
    }
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

  console.log('[MeetingConsole] jumpToTime called:', {
    time: time,
    audioDuration: audioDuration,
    audioSrc: audioSrc.value,
    hasAudioElement: !!audioElement.value,
    pendingSeekTime: pendingSeekTime.value,
  })

  // If audio loaded, use audio duration. Otherwise use chapter total but VALIDATE it.
  let total: number
  if (audioDuration > 0) {
    total = audioDuration
  } else {
    // Fallback: use chapter end_time but cap it to a reasonable max
    const lastChapterEnd = chapters.value[chapters.value.length - 1]?.end_time || 500
    total = lastChapterEnd < 1800 ? lastChapterEnd : 500
  }
  // Only clamp when audio duration is known. When using fallback, allow >100%
  // since actual audio might be longer than chapter-based total.
  if (audioDuration > 0) {
    progressPercent.value = Math.min((time / total) * 100, 100)
  } else {
    progressPercent.value = (time / total) * 100
  }
  totalSeconds.value = total
  const min = Math.floor(time / 60)
  const sec = Math.floor(time % 60)
  currentTime.value = `${min}:${String(sec).padStart(2, '0')}`

  // If audio element exists, seek to the time
  if (audioElement.value) {
    // Re-check duration at seek time (audio might have loaded since this function was called)
    const currentDuration = audioElement.value.duration || 0

    // Always try to seek directly first - this works even if duration is not yet known
    // The browser will queue the seek and execute when metadata is loaded
    console.log('[MeetingConsole] Seeking to:', time, 'currentDuration:', currentDuration)
    audioElement.value.currentTime = time

    // If audio not loaded (duration is 0, NaN, or Infinity), ensure it starts loading
    if (!currentDuration || currentDuration === Infinity || isNaN(currentDuration)) {
      console.log('[MeetingConsole] Duration unknown, ensuring audio is loading')
      isAudioLoading.value = true
      const src = activeAudioUrl.value || DEMO_AUDIO_URL
      if (audioSrc.value !== src) {
        // Different src, load it
        audioSrc.value = src
        audioElement.value.src = src
        audioElement.value.load()
      } else if (!audioElement.value.src || audioElement.value.src === window.location.href) {
        // No src set or src is page URL (invalid), set it
        audioElement.value.src = src
        audioElement.value.load()
      }
      // If src is already set to DEMO_AUDIO_URL, the seek we just set will apply when loaded
    }
  }
}

// Initialize
onMounted(() => {
  // Sync session data to global store if navigated via sessionId route
  if (routeSessionId.value) {
    store.setActiveSession(routeSessionId.value)
  }
  // Ensure we have chapters - fallback to store.chapters if sessionData is null
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

.btn-play:disabled {
  background: #6366f1;
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
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

.knowledge-service-card {
  padding: 16px;
  background: #141420;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}

.knowledge-service-card h3 {
  margin: 0 0 8px;
  font-size: 15px;
}

.knowledge-service-card p {
  margin: 0 0 14px;
  color: rgba(255, 255, 255, 0.65);
  font-size: 13px;
  line-height: 1.5;
}

.btn-knowledge-service {
  width: 100%;
  padding: 9px 12px;
  border: 0;
  border-radius: 6px;
  color: #fff;
  background: #6366f1;
  cursor: pointer;
}

/* Transcript Panel */
.transcript-panel {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.transcript-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.transcript-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #141420;
  border-radius: 6px;
  font-size: 13px;
}

.transcript-item .seg-time {
  color: #6366f1;
  cursor: pointer;
  flex-shrink: 0;
  min-width: 50px;
}

.transcript-item .seg-time:hover {
  text-decoration: underline;
}

.transcript-item .seg-speaker {
  flex-shrink: 0;
  min-width: 80px;
  font-weight: 500;
}

.transcript-item .seg-text {
  color: rgba(255, 255, 255, 0.8);
  flex: 1;
}

/* Decisions Panel */
.decisions-panel {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.decisions-section,
.actions-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 12px;
}

.decisions-list,
.actions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.decision-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #141420;
  border-radius: 6px;
  border-left: 3px solid #22c55e;
}

.decision-icon {
  color: #22c55e;
  font-size: 14px;
  flex-shrink: 0;
}

.decision-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.decision-text {
  font-size: 13px;
  color: #fff;
}

.decision-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.action-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #141420;
  border-radius: 6px;
  border-left: 3px solid #f59e0b;
}

.action-checkbox {
  flex-shrink: 0;
}

.action-checkbox input {
  width: 16px;
  height: 16px;
  accent-color: #f59e0b;
}

.action-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.action-text {
  font-size: 13px;
  color: #fff;
}

.action-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
}

.empty-hint {
  padding: 24px;
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
}
</style>
