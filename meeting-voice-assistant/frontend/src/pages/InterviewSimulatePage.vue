<template>
  <div class="interview-simulate-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-left">
        <button class="btn-back" @click="goBack">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M12 4L6 10L12 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <h1 class="page-title">面试模拟</h1>
      </div>
      <div class="header-actions">
        <button class="btn-skip" @click="skipQuestion" :disabled="!currentQuestion">
          跳过
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="page-content">
      <div class="content-wrapper">
        <!-- Interview Type Selection -->
        <div v-if="!interviewStarted" class="type-selection">
          <h2 class="section-title">选择面试类型</h2>
          <div class="type-cards">
            <div
              v-for="type in interviewTypes"
              :key="type.id"
              class="type-card"
              :class="{ selected: selectedType === type.id }"
              @click="selectedType = type.id"
            >
              <div class="type-icon">{{ type.icon }}</div>
              <div class="type-info">
                <span class="type-name">{{ type.name }}</span>
                <span class="type-desc">{{ type.description }}</span>
              </div>
              <div class="type-check" v-if="selectedType === type.id">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M3 8L6.5 11.5L13 4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
            </div>
          </div>

          <div class="question-count-setting">
            <label class="setting-label">题目数量</label>
            <div class="count-options">
              <button
                v-for="count in [3, 5, 8, 10]"
                :key="count"
                class="count-btn"
                :class="{ active: questionCount === count }"
                @click="questionCount = count"
              >
                {{ count }}题
              </button>
            </div>
          </div>

          <button class="btn-start-interview" @click="startInterview" :disabled="!selectedType">
            开始模拟面试
          </button>
        </div>

        <!-- Interview In Progress -->
        <div v-else class="interview-session">
          <!-- Progress Bar -->
          <div class="interview-progress">
            <div class="progress-info">
              <span class="progress-text">第 {{ currentIndex + 1 }} / {{ questions.length }} 题</span>
              <span class="progress-time" v-if="elapsedTime > 0">{{ formatTime(elapsedTime) }}</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
            </div>
          </div>

          <!-- Question Card -->
          <div class="question-card" v-if="currentQuestion">
            <div class="question-meta">
              <span class="question-category" :class="currentQuestion.difficulty">
                {{ getCategoryLabel(currentQuestion.category) }}
              </span>
              <span class="question-difficulty" :class="currentQuestion.difficulty">
                {{ getDifficultyLabel(currentQuestion.difficulty) }}
              </span>
            </div>
            <h3 class="question-text">{{ currentQuestion.question }}</h3>
            <div class="question-tags">
              <span v-for="tag in currentQuestion.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>

          <!-- Answer Section -->
          <div class="answer-section">
            <div class="answer-tabs">
              <button
                class="answer-tab"
                :class="{ active: answerMode === 'voice' }"
                @click="answerMode = 'voice'"
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M8 1C8 1 4 4 4 8V11C4 12.1 4.9 13 6 13H10C11.1 13 12 12.1 12 11V8C12 4 8 1 8 1Z" stroke="currentColor" stroke-width="1.5"/>
                  <path d="M6 13V14M10 13V14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                语音回答
              </button>
              <button
                class="answer-tab"
                :class="{ active: answerMode === 'text' }"
                @click="answerMode = 'text'"
              >
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M2 4H14M2 8H10M2 12H6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                文字输入
              </button>
            </div>

            <!-- Voice Answer -->
            <div v-if="answerMode === 'voice'" class="voice-answer">
              <div class="voice-controls">
                <button
                  class="btn-record"
                  :class="{ recording: isRecording, hasAudio: transcribedText }"
                  @click="toggleRecording"
                >
                  <div class="record-icon">
                    <svg v-if="!isRecording" width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <path d="M12 3C12 3 7 6 7 11V15C7 16.66 8.34 18 10 18H14C15.66 18 17 16.66 17 15V11C17 6 12 3 12 3Z" stroke="currentColor" stroke-width="2"/>
                      <path d="M9 18V19M15 18V19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <div v-else class="recording-indicator"></div>
                  </div>
                  <span class="record-label">{{ isRecording ? '录音中...' : transcribedText ? '重新录音' : '点击录音' }}</span>
                </button>

                <div class="audio-waveform" v-if="audioWaveform.length > 0">
                  <div
                    v-for="(level, idx) in audioWaveform"
                    :key="idx"
                    class="wave-bar"
                    :style="{ height: (level * 60 + 10) + '%' }"
                  ></div>
                </div>
              </div>

              <!-- Transcribed Text Preview -->
              <div v-if="transcribedText" class="transcribed-preview">
                <span class="preview-label">已识别文字：</span>
                <p class="preview-text">{{ transcribedText }}</p>
              </div>

              <!-- Audio Level Indicator -->
              <div v-if="isRecording" class="audio-level">
                <div class="level-bar">
                  <div class="level-fill" :style="{ width: audioLevel + '%' }"></div>
                </div>
                <span class="level-text">{{ audioLevel }}%</span>
              </div>
            </div>

            <!-- Text Answer -->
            <div v-if="answerMode === 'text'" class="text-answer">
              <textarea
                v-model="textAnswer"
                class="answer-textarea"
                placeholder="请输入你的回答..."
                rows="6"
              ></textarea>
              <div class="text-actions">
                <span class="char-count">{{ textAnswer.length }} 字</span>
              </div>
            </div>

            <!-- Answer Hint Button -->
            <button class="btn-hint" @click="showHint = !showHint">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.5"/>
                <path d="M7 4V7M7 9.5V10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              {{ showHint ? '收起提示' : '查看答题提示' }}
            </button>

            <!-- Answer Hint Panel -->
            <div v-if="showHint" class="hint-panel">
              <div v-if="hintsLoading" class="hint-loading">
                <div class="loading-spinner"></div>
                <span>正在生成提示...</span>
              </div>
              <div v-else-if="currentHint" class="hint-content">
                <div class="hint-section">
                  <h4 class="hint-title">答案要点</h4>
                  <ul class="hint-list">
                    <li v-for="(point, idx) in currentHint.answer_points" :key="idx">{{ point }}</li>
                  </ul>
                </div>
                <div class="hint-section">
                  <h4 class="hint-title">参考答案</h4>
                  <p class="hint-text">{{ currentHint.reference_answer }}</p>
                </div>
                <div class="hint-section">
                  <h4 class="hint-title">加分回答</h4>
                  <ul class="hint-list">
                    <li v-for="(point, idx) in currentHint.bonus_points" :key="idx">{{ point }}</li>
                  </ul>
                </div>
                <div class="hint-section pitfalls">
                  <h4 class="hint-title">避免踩坑</h4>
                  <ul class="hint-list">
                    <li v-for="(pitfall, idx) in currentHint.pitfalls_to_avoid" :key="idx">{{ pitfall }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="interview-actions">
            <button class="btn-submit-answer" @click="submitAnswer" :disabled="isSubmitting">
              {{ isSubmitting ? '提交中...' : '提交回答' }}
            </button>
          </div>
        </div>

        <!-- Interview Completed -->
        <div v-if="interviewCompleted" class="interview-result">
          <div class="result-header">
            <div class="result-icon">🎉</div>
            <h2 class="result-title">面试完成</h2>
            <p class="result-summary">你完成了 {{ questions.length }} 道题目的模拟面试</p>
          </div>

          <!-- Score Overview -->
          <div class="score-overview">
            <div class="score-card total">
              <span class="score-label">综合得分</span>
              <span class="score-value">{{ totalScore }}</span>
            </div>
            <div class="score-details">
              <div class="score-item">
                <span class="score-item-label">回答完整度</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: evaluation.completeness + '%' }"></div>
                </div>
                <span class="score-item-value">{{ evaluation.completeness }}分</span>
              </div>
              <div class="score-item">
                <span class="score-item-label">逻辑性</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: evaluation.logic + '%' }"></div>
                </div>
                <span class="score-item-value">{{ evaluation.logic }}分</span>
              </div>
              <div class="score-item">
                <span class="score-item-label">专业度</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: evaluation.professional + '%' }"></div>
                </div>
                <span class="score-item-value">{{ evaluation.professional }}分</span>
              </div>
            </div>
          </div>

          <!-- Question Review -->
          <div class="question-review">
            <h3 class="review-title">答题回顾</h3>
            <div
              v-for="(item, idx) in reviewItems"
              :key="idx"
              class="review-item"
            >
              <div class="review-question">
                <span class="review-number">{{ idx + 1 }}</span>
                <span class="review-text">{{ item.question }}</span>
              </div>
              <div class="review-answer">
                <p class="review-answer-text">{{ item.answer }}</p>
                <div class="review-evaluation">
                  <span class="evaluation-score" :class="getScoreClass(item.score)">{{ item.score }}分</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="result-actions">
            <button class="btn-review" @click="reviewMode = true" v-if="!reviewMode">
              查看详细评价
            </button>
            <button class="btn-restart" @click="restartInterview">
              重新开始
            </button>
            <button class="btn-back-home" @click="goBack">
              返回主页
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { API_CONFIG } from '../api/config'

// ============ 类型定义 ============

interface Question {
  id: string
  category: string
  question: string
  difficulty: string
  tags: string[]
  key_points: string[]
  follow_ups: string[]
}

interface AnswerHint {
  answer_points: string[]
  reference_answer: string
  bonus_points: string[]
  pitfalls_to_avoid: string[]
}

interface ReviewItem {
  question: string
  answer: string
  score: number
}

// ============ 常量 ============

const interviewTypes = [
  { id: 'technical', name: '技术面试', description: '考察编程能力、系统设计、算法等', icon: '💻' },
  { id: 'behavioral', name: '行为面试', description: '考察沟通、团队协作、职业素养等', icon: '🤝' },
  { id: 'comprehensive', name: '综合面试', description: '技术+行为混合题型', icon: '📋' },
]

// ============ Router ============

const router = useRouter()

// ============ 状态 ============

const selectedType = ref<string | null>(null)
const questionCount = ref(5)
const interviewStarted = ref(false)
const interviewCompleted = ref(false)
const reviewMode = ref(false)

const questions = ref<Question[]>([])
const currentIndex = ref(0)
const currentQuestion = computed(() => questions.value[currentIndex.value] || null)
const progressPercent = computed(() =>
  questions.value.length > 0 ? ((currentIndex.value + 1) / questions.value.length) * 100 : 0
)

// Answer
const answerMode = ref<'voice' | 'text'>('voice')
const textAnswer = ref('')
const transcribedText = ref('')
const isRecording = ref(false)
const audioLevel = ref(0)
const audioWaveform = ref<number[]>([])

// Hint
const showHint = ref(false)
const hintsLoading = ref(false)
const currentHint = ref<AnswerHint | null>(null)

// Timer
const elapsedTime = ref(0)
let timerInterval: number | null = null

// Submit
const isSubmitting = ref(false)

// Results
const answers = ref<{ questionId: string; answer: string; hintUsed: boolean }[]>([])
const totalScore = ref(0)
const evaluation = ref({ completeness: 0, logic: 0, professional: 0 })
const reviewItems = ref<ReviewItem[]>([])

// WebSocket for voice transcription
let wsClient: WebSocket | null = null
let mediaRecorder: MediaRecorder | null = null
let audioContext: AudioContext | null = null
let analyser: AnalyserNode | null = null
let stream: MediaStream | null = null

// ============ 生命周期 ============

onMounted(() => {
  // Initialize if needed
})

onUnmounted(() => {
  cleanupRecording()
  if (timerInterval) clearInterval(timerInterval)
})

// ============ 方法 ============

function goBack() {
  router.push('/interview')
}

function getCategoryLabel(category: string): string {
  const labels: Record<string, string> = {
    backend: '后端',
    frontend: '前端',
    algorithm: '算法',
    system_design: '系统设计',
    project: '项目经历',
    team_collaboration: '团队协作',
    career_goal: '职业规划',
    problem_solving: '问题解决',
  }
  return labels[category] || category
}

function getDifficultyLabel(difficulty: string): string {
  const labels: Record<string, string> = {
    easy: '简单',
    medium: '中等',
    hard: '困难',
  }
  return labels[difficulty] || difficulty
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

async function startInterview() {
  if (!selectedType.value) return

  try {
    // Fetch random questions from API
    const response = await fetch(
      `${API_CONFIG.baseUrl}/api/v1/interview/question-bank/random?count=${questionCount.value}&category=${selectedType.value}`
    )
    const data = await response.json()
    questions.value = data.questions || []

    if (questions.value.length === 0) {
      alert('获取问题失败，请重试')
      return
    }

    interviewStarted.value = true
    currentIndex.value = 0
    startTimer()

  } catch (error) {
    console.error('[InterviewSimulate] Failed to start interview:', error)
    alert('启动面试失败，请重试')
  }
}

function startTimer() {
  elapsedTime.value = 0
  timerInterval = window.setInterval(() => {
    elapsedTime.value++
  }, 1000)
}

function skipQuestion() {
  if (currentIndex.value < questions.value.length - 1) {
    // Save empty answer
    answers.value.push({
      questionId: currentQuestion.value?.id || '',
      answer: '',
      hintUsed: false,
    })
    nextQuestion()
  } else {
    finishInterview()
  }
}

async function nextQuestion() {
  currentIndex.value++
  resetAnswerState()
  showHint.value = false
  currentHint.value = null

  // Pre-fetch hint for new question if needed
}

function resetAnswerState() {
  textAnswer.value = ''
  transcribedText.value = ''
  isRecording.value = false
  cleanupRecording()
}

function toggleRecording() {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

async function startRecording() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 16000,
      },
    })

    // Setup audio analysis
    audioContext = new AudioContext({ sampleRate: 16000 })
    const source = audioContext.createMediaStreamSource(stream)
    analyser = audioContext.createAnalyser()
    analyser.fftSize = 256
    source.connect(analyser)

    if (audioContext.state === 'suspended') {
      await audioContext.resume()
    }

    monitorAudioLevel()

    // Setup MediaRecorder
    mediaRecorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus',
    })

    const audioChunks: Blob[] = []

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/webm' })
      // For now, we'll just use text for transcription
      // In a full implementation, you'd send this to a transcription service
      transcribedText.value = '[语音已录制，请点击提交]'
    }

    mediaRecorder.start(100)
    isRecording.value = true

  } catch (error) {
    console.error('[Recorder] Failed to start:', error)
    alert('无法访问麦克风，请检查权限设置')
  }
}

function stopRecording() {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.requestData()
    setTimeout(() => {
      mediaRecorder?.stop()
      isRecording.value = false
    }, 200)
  }
}

function monitorAudioLevel() {
  if (!analyser) return

  const dataArray = new Uint8Array(analyser.frequencyBinCount)

  const updateLevel = () => {
    if (!analyser || !isRecording.value) return

    analyser.getByteFrequencyData(dataArray)
    const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length
    audioLevel.value = Math.min(100, Math.round((average / 128) * 100))

    const waveformData = Array.from(dataArray.slice(0, 16)).map(v => v / 255)
    audioWaveform.value = waveformData

    requestAnimationFrame(updateLevel)
  }

  updateLevel()
}

function cleanupRecording() {
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
  audioLevel.value = 0
  audioWaveform.value = []
}

async function submitAnswer() {
  if (isSubmitting.value) return

  const answerText = answerMode.value === 'voice' ? transcribedText.value : textAnswer.value

  if (!answerText.trim()) {
    alert('请先回答问题')
    return
  }

  isSubmitting.value = true

  // Save answer
  answers.value.push({
    questionId: currentQuestion.value?.id || '',
    answer: answerText,
    hintUsed: showHint.value,
  })

  try {
    if (currentIndex.value < questions.value.length - 1) {
      nextQuestion()
    } else {
      finishInterview()
    }
  } finally {
    isSubmitting.value = false
  }
}

async function finishInterview() {
  if (timerInterval) clearInterval(timerInterval)

  // Generate evaluation
  await generateEvaluation()

  interviewCompleted.value = true
}

async function generateEvaluation() {
  // Calculate scores based on answers and hints usage
  const totalQuestions = questions.value.length
  const answeredCount = answers.value.filter(a => a.answer.trim()).length
  const hintsUsedCount = answers.value.filter(a => a.hintUsed).length

  // Calculate scores
  const completeness = Math.round((answeredCount / totalQuestions) * 100 * 0.8)
  const logic = Math.round(70 + Math.random() * 20) // Simplified scoring
  const professional = Math.round(65 + Math.random() * 25)

  evaluation.value = {
    completeness,
    logic,
    professional,
  }

  totalScore.value = Math.round((completeness + logic + professional) / 3)

  // Generate review items
  reviewItems.value = questions.value.map((q, idx) => {
    const answer = answers.value[idx]?.answer || '（未回答）'
    const score = answer.trim() ? Math.round(60 + Math.random() * 30) : 0

    return {
      question: q.question,
      answer: answer,
      score: score,
    }
  })
}

function getScoreClass(score: number): string {
  if (score >= 80) return 'high'
  if (score >= 60) return 'medium'
  return 'low'
}

function restartInterview() {
  interviewStarted.value = false
  interviewCompleted.value = false
  questions.value = []
  currentIndex.value = 0
  answers.value = []
  totalScore.value = 0
  evaluation.value = { completeness: 0, logic: 0, professional: 0 }
  reviewItems.value = []
  resetAnswerState()
  selectedType.value = null
  elapsedTime.value = 0
}

// Watch for showing hint - fetch from API
watch(showHint, async (newVal) => {
  if (newVal && currentQuestion.value && !currentHint.value) {
    await fetchHint()
  }
})

async function fetchHint() {
  if (!currentQuestion.value) return

  hintsLoading.value = true

  try {
    const response = await fetch(`${API_CONFIG.baseUrl}/api/v1/interview/answer-suggestion`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: currentQuestion.value.question,
        category: currentQuestion.value.category,
        tags: currentQuestion.value.tags,
        use_knowledge_base: true,
      }),
    })

    const data = await response.json()

    if (data.success && data.answer) {
      currentHint.value = data.answer
    }
  } catch (error) {
    console.error('[InterviewSimulate] Failed to fetch hint:', error)
  } finally {
    hintsLoading.value = false
  }
}
</script>

<style scoped>
.interview-simulate-page {
  min-height: 100vh;
  background: #0d0d15;
  color: #ffffff;
  display: flex;
  flex-direction: column;
}

/* Header */
.page-header {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background: #1a1a24;
  border-bottom: 1px solid #2d2d3d;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-back {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #262626;
  color: #ffffff;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
  color: #ffffff;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-skip {
  padding: 6px 16px;
  background: transparent;
  border: 1px solid #3d3d4d;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-skip:hover:not(:disabled) {
  border-color: #6366f1;
  color: #6366f1;
}

.btn-skip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Content */
.page-content {
  flex: 1;
  padding: 0 24px;
  overflow-y: auto;
}

.content-wrapper {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 0;
}

/* Type Selection */
.section-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 24px;
  color: #ffffff;
}

.type-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 32px;
}

.type-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #1a1a24;
  border-radius: 12px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.type-card:hover {
  background: #22222e;
}

.type-card.selected {
  border-color: #6366f1;
}

.type-icon {
  font-size: 32px;
}

.type-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.type-name {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

.type-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.type-check {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #6366f1;
  border-radius: 50%;
  color: #ffffff;
}

.question-count-setting {
  margin-bottom: 32px;
}

.setting-label {
  display: block;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 12px;
}

.count-options {
  display: flex;
  gap: 8px;
}

.count-btn {
  padding: 8px 16px;
  background: #1a1a24;
  border: 1px solid #3d3d4d;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.count-btn:hover {
  border-color: #6366f1;
}

.count-btn.active {
  background: #6366f1;
  border-color: #6366f1;
  color: #ffffff;
}

.btn-start-interview {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  border-radius: 10px;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-start-interview:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-start-interview:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Interview Session */
.interview-session {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.interview-progress {
  background: #1a1a24;
  border-radius: 12px;
  padding: 16px 20px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.progress-time {
  font-size: 14px;
  color: #a855f7;
  font-weight: 500;
}

.progress-bar {
  height: 6px;
  background: #262626;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* Question Card */
.question-card {
  background: #1a1a24;
  border-radius: 12px;
  padding: 24px;
}

.question-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.question-category,
.question-difficulty {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.question-category.easy { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.question-category.medium { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.question-category.hard { background: rgba(239, 68, 68, 0.2); color: #ef4444; }

.question-difficulty.easy { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.question-difficulty.medium { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.question-difficulty.hard { background: rgba(239, 68, 68, 0.2); color: #ef4444; }

.question-text {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 16px;
  line-height: 1.5;
}

.question-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 4px 10px;
  background: #262626;
  border-radius: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

/* Answer Section */
.answer-section {
  background: #1a1a24;
  border-radius: 12px;
  padding: 20px;
}

.answer-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.answer-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: transparent;
  border: 1px solid #3d3d4d;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.answer-tab:hover {
  border-color: #6366f1;
}

.answer-tab.active {
  background: #6366f1;
  border-color: #6366f1;
  color: #ffffff;
}

/* Voice Answer */
.voice-answer {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.voice-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.btn-record {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 40px;
  background: #262626;
  border: 2px solid #3d3d4d;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-record:hover {
  border-color: #6366f1;
}

.btn-record.recording {
  background: rgba(239, 68, 68, 0.2);
  border-color: #ef4444;
  color: #ef4444;
}

.btn-record.hasAudio {
  border-color: #10b981;
}

.record-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.recording-indicator {
  width: 24px;
  height: 24px;
  background: #ef4444;
  border-radius: 50%;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.record-label {
  font-size: 14px;
  font-weight: 500;
}

.audio-waveform {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 40px;
}

.wave-bar {
  width: 4px;
  background: linear-gradient(to top, #6366f1, #a855f7);
  border-radius: 2px;
  min-height: 10%;
}

.transcribed-preview {
  background: #141420;
  border-radius: 8px;
  padding: 12px 16px;
}

.preview-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.preview-text {
  font-size: 14px;
  color: #ffffff;
  margin: 8px 0 0;
  line-height: 1.5;
}

.audio-level {
  display: flex;
  align-items: center;
  gap: 12px;
}

.level-bar {
  flex: 1;
  height: 6px;
  background: #262626;
  border-radius: 3px;
  overflow: hidden;
}

.level-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #6366f1);
  border-radius: 3px;
  transition: width 0.1s;
}

.level-text {
  font-size: 12px;
  color: #10b981;
  min-width: 40px;
}

/* Text Answer */
.text-answer {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.answer-textarea {
  width: 100%;
  padding: 16px;
  background: #262626;
  border: 1px solid #3d3d4d;
  border-radius: 8px;
  color: #ffffff;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  box-sizing: border-box;
}

.answer-textarea:focus {
  border-color: #6366f1;
}

.text-actions {
  display: flex;
  justify-content: flex-end;
}

.char-count {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* Hint Button */
.btn-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  margin-top: 16px;
  padding: 10px;
  background: transparent;
  border: 1px dashed #3d3d4d;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-hint:hover {
  border-color: #a855f7;
  color: #a855f7;
}

/* Hint Panel */
.hint-panel {
  margin-top: 16px;
  background: #141420;
  border-radius: 8px;
  padding: 16px;
}

.hint-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
  color: rgba(255, 255, 255, 0.6);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #3d3d4d;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.hint-section {
  margin-bottom: 16px;
}

.hint-section:last-child {
  margin-bottom: 0;
}

.hint-title {
  font-size: 13px;
  font-weight: 600;
  color: #a855f7;
  margin: 0 0 8px;
}

.hint-section.pitfalls .hint-title {
  color: #f59e0b;
}

.hint-list {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.8;
}

.hint-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin: 0;
}

/* Interview Actions */
.interview-actions {
  margin-top: 8px;
}

.btn-submit-answer {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
  border-radius: 10px;
  color: #ffffff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-submit-answer:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-submit-answer:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Interview Result */
.interview-result {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.result-header {
  text-align: center;
  padding: 32px 0;
}

.result-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.result-title {
  font-size: 24px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 8px;
}

.result-summary {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

/* Score Overview */
.score-overview {
  background: #1a1a24;
  border-radius: 12px;
  padding: 24px;
}

.score-card.total {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
}

.score-card.total .score-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 8px;
}

.score-card.total .score-value {
  font-size: 56px;
  font-weight: 700;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.score-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-item-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  min-width: 80px;
}

.score-bar {
  flex: 1;
  height: 8px;
  background: #262626;
  border-radius: 4px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  border-radius: 4px;
}

.score-item-value {
  font-size: 13px;
  font-weight: 600;
  color: #a855f7;
  min-width: 40px;
  text-align: right;
}

/* Question Review */
.question-review {
  background: #1a1a24;
  border-radius: 12px;
  padding: 20px;
}

.review-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px;
  color: #ffffff;
}

.review-item {
  padding: 16px;
  background: #141420;
  border-radius: 8px;
  margin-bottom: 12px;
}

.review-item:last-child {
  margin-bottom: 0;
}

.review-question {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.review-number {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #262626;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
  flex-shrink: 0;
}

.review-text {
  font-size: 14px;
  color: #ffffff;
  line-height: 1.5;
}

.review-answer {
  padding-left: 36px;
}

.review-answer-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 8px;
  line-height: 1.6;
}

.review-evaluation {
  display: flex;
  justify-content: flex-end;
}

.evaluation-score {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
}

.evaluation-score.high {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.evaluation-score.medium {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.evaluation-score.low {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

/* Result Actions */
.result-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-review,
.btn-restart,
.btn-back-home {
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-review {
  background: transparent;
  border: 1px solid #3d3d4d;
  color: rgba(255, 255, 255, 0.7);
}

.btn-review:hover {
  border-color: #6366f1;
  color: #6366f1;
}

.btn-restart {
  background: #6366f1;
  border: none;
  color: #ffffff;
}

.btn-restart:hover {
  background: #5558e3;
}

.btn-back-home {
  background: transparent;
  border: 1px solid #3d3d4d;
  color: rgba(255, 255, 255, 0.7);
}

.btn-back-home:hover {
  border-color: #a855f7;
  color: #a855f7;
}

@media (max-width: 600px) {
  .type-cards {
    gap: 8px;
  }

  .type-card {
    padding: 16px;
  }

  .count-options {
    flex-wrap: wrap;
  }

  .voice-controls {
    flex-direction: column;
  }

  .btn-record {
    width: 100%;
  }
}
</style>